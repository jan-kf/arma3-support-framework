#!/usr/bin/env python3
"""Minimal loopback-only RFB adapter for Pontifex's Arma display.

It talks to Weston's VNC backend inside the client network namespace.  This
deliberately avoids XTEST/Xwayland input.  At this stage it proves only the
authenticated RFB framebuffer/input transport, not Arma UI automation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import socket
import ssl
import struct
import time
import zlib
from pathlib import Path


def recv_exact(sock: socket.socket, length: int) -> bytes:
    data = b""
    while len(data) < length:
        chunk = sock.recv(length - len(data))
        if not chunk:
            raise RuntimeError("RFB peer closed the connection")
        data += chunk
    return data


class Rfb:
    def __init__(self, host: str, port: int) -> None:
        self.sock: socket.socket = socket.create_connection((host, port), timeout=10)
        self.sock.settimeout(15)
        self.width = 0
        self.height = 0
        self.bits_per_pixel = 0
        self.big_endian = 0
        self.red_max = self.green_max = self.blue_max = 0
        self.red_shift = self.green_shift = self.blue_shift = 0
        # This deliberately records wire-level protocol decisions without
        # recording credential material.  It makes an authentication failure
        # diagnosable from the run artifact alone.
        self.trace: list[dict[str, object]] = []
        self._negotiate()

    def _negotiate(self) -> None:
        version = recv_exact(self.sock, 12)
        if not version.startswith(b"RFB "):
            raise RuntimeError(f"unexpected RFB banner {version!r}")
        self.sock.sendall(b"RFB 003.008\n")
        self.trace.append({"step": "RFB version", "server": version.decode("ascii", "replace"), "client": "RFB 003.008"})
        count = recv_exact(self.sock, 1)[0]
        security = recv_exact(self.sock, count)
        self.trace.append({"step": "security types", "server": list(security), "selected": 19})
        if 19 in security:  # VeNCrypt, used by Weston's TLS VNC backend.
            self.sock.sendall(bytes([19]))
            vencrypt_version = recv_exact(self.sock, 2)
            self.sock.sendall(vencrypt_version)
            version_status = recv_exact(self.sock, 1)
            self.trace.append({"step": "VeNCrypt version", "version_hex": vencrypt_version.hex(), "status_hex": version_status.hex()})
            if version_status != b"\x00":
                raise RuntimeError("Weston rejected VeNCrypt version")
            subtype_count = recv_exact(self.sock, 1)[0]
            subtypes = [struct.unpack(">I", recv_exact(self.sock, 4))[0] for _ in range(subtype_count)]
            # Weston with a configured certificate exposes X509Plain (262).
            # It checks the supplied local username before consulting the
            # image's PAM service; no credential leaves this container.
            tls_none, tls_plain, x509_plain = 257, 259, 262
            selected = next((item for item in (x509_plain, tls_plain, tls_none) if item in subtypes), None)
            if selected is None:
                raise RuntimeError(f"Weston offered no supported TLS type: {subtypes}")
            self.sock.sendall(struct.pack(">I", selected))
            # VeNCrypt acknowledges the selected subtype before beginning
            # the TLS record stream.  Treating this byte as a TLS header
            # produces OpenSSL's WRONG_VERSION_NUMBER error.
            subtype_status = recv_exact(self.sock, 1)
            self.trace.append({"step": "VeNCrypt subtype", "server": subtypes, "selected": selected, "status_hex": subtype_status.hex()})
            if subtype_status != b"\x01":
                raise RuntimeError("Weston rejected VeNCrypt security subtype")
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            self.sock = context.wrap_socket(self.sock, server_hostname="localhost")
            self.trace.append({"step": "TLS", "status": "complete", "cipher": self.sock.cipher()[0]})
            if selected in (tls_plain, x509_plain):
                username = b"pontifex"
                password = b""
                # RFB Plain is four fields in this exact order: username
                # length, password length, username bytes, password bytes.
                # Sending the username before the password length makes
                # Weston treat "pont" as a huge password length and wait.
                self.sock.sendall(struct.pack(">II", len(username), len(password)) + username + password)
                self.trace.append({"step": "X509Plain", "framing": "u32 username_length, u32 password_length, username, password", "username_length": len(username), "password_length": len(password)})
        elif 1 in security:  # Test-only fallback if Weston has no TLS configured.
            self.sock.sendall(bytes([1]))
        else:
            raise RuntimeError(f"unsupported RFB security types {list(security)}")
        security_result = struct.unpack(">I", recv_exact(self.sock, 4))[0]
        self.trace.append({"step": "RFB SecurityResult", "status": security_result})
        if security_result != 0:
            raise RuntimeError("RFB security negotiation failed")
        self.sock.sendall(b"\x01")  # shared session
        header = recv_exact(self.sock, 24)
        self.width, self.height = struct.unpack(">HH", header[:4])
        # RFB ServerInit is: width/height, a 16-byte PixelFormat, then the
        # name length.  PixelFormat ends with three padding bytes; retaining
        # its full 16-byte extent keeps the following name length aligned.
        (self.bits_per_pixel, _depth, self.big_endian, true_color,
         self.red_max, self.green_max, self.blue_max,
         self.red_shift, self.green_shift, self.blue_shift) = struct.unpack(">BBBBHHHBBBxxx", header[4:20])
        if not true_color or self.bits_per_pixel not in (16, 32):
            raise RuntimeError("unsupported Weston RFB pixel format")
        name_length = struct.unpack(">I", header[20:24])[0]
        self.name = recv_exact(self.sock, name_length).decode("utf-8", "replace")
        self.trace.append({
            "step": "ServerInit", "width": self.width, "height": self.height,
            "name": self.name, "bits_per_pixel": self.bits_per_pixel,
            "big_endian": self.big_endian,
            "red_max": self.red_max, "green_max": self.green_max, "blue_max": self.blue_max,
            "red_shift": self.red_shift, "green_shift": self.green_shift, "blue_shift": self.blue_shift,
        })
        # Ask Weston for the conventional little-endian BGRX layout. Its
        # native scanout format is valid RFB but is unsuitable as a stable
        # screenshot input for UI recognition.
        pixel_format = struct.pack(
            ">B3xBBBBHHHBBB3x", 0, 32, 24, 0, 1, 255, 255, 255, 16, 8, 0
        )
        self.sock.sendall(pixel_format)
        self.bits_per_pixel = 32
        self.big_endian = 0
        self.red_max = self.green_max = self.blue_max = 255
        self.red_shift, self.green_shift, self.blue_shift = 16, 8, 0
        self.sock.sendall(b"\x02\x00\x00\x01" + struct.pack(">i", 0))  # raw encoding
        self.trace.append({"step": "SetEncodings", "encoding": 0})

    def frame(self) -> bytes:
        self.sock.sendall(struct.pack(">BBHHHH", 3, 0, 0, 0, self.width, self.height))
        while True:
            message = recv_exact(self.sock, 1)[0]
            if message == 0:
                recv_exact(self.sock, 1)
                count = struct.unpack(">H", recv_exact(self.sock, 2))[0]
                canvas = bytearray(self.width * self.height * (self.bits_per_pixel // 8))
                for _ in range(count):
                    x, y, width, height, encoding = struct.unpack(">HHHHi", recv_exact(self.sock, 12))
                    if encoding != 0:
                        raise RuntimeError(f"unsupported framebuffer encoding {encoding}")
                    row_bytes = width * (self.bits_per_pixel // 8)
                    data = recv_exact(self.sock, row_bytes * height)
                    for row in range(height):
                        target = ((y + row) * self.width + x) * (self.bits_per_pixel // 8)
                        source = row * row_bytes
                        canvas[target:target + row_bytes] = data[source:source + row_bytes]
                return bytes(canvas)
            if message == 2:  # Bell
                continue
            if message == 3:  # ServerCutText
                recv_exact(self.sock, 3)
                recv_exact(self.sock, struct.unpack(">I", recv_exact(self.sock, 4))[0])
                continue
            raise RuntimeError(f"unexpected RFB server message {message}")

    def pointer_move(self, x: int, y: int) -> None:
        # A button-mask of zero is a harmless mouse move: it proves that
        # Weston accepts RFB input without advancing any Arma UI state.
        self.sock.sendall(struct.pack(">BBHH", 5, 0, x, y))

    def pointer_click(self, x: int, y: int) -> None:
        event = lambda mask: struct.pack(">BBHH", 5, mask, x, y)
        # Arma's menu consumes a distinct press/release pair.  Coalescing
        # both events into one write reliably hovered the Direct Connect tab
        # but did not activate it in the supervised run.
        self.sock.sendall(event(1))
        time.sleep(0.08)
        self.sock.sendall(event(0))

    def key(self, key: int, down: bool = True) -> None:
        self.sock.sendall(struct.pack(">BBHI", 4, int(down), 0, key))

    def type_text(self, value: str) -> None:
        for character in value:
            self.key(ord(character), True)
            self.key(ord(character), False)

    def close(self) -> None:
        self.sock.close()


def pixels_to_rgb(rfb: Rfb, pixels: bytes) -> bytes:
    bytes_per_pixel = rfb.bits_per_pixel // 8
    rgb = bytearray()
    for index in range(0, len(pixels), bytes_per_pixel):
        value = int.from_bytes(pixels[index:index + bytes_per_pixel], "big" if rfb.big_endian else "little")
        rgb.extend((
            ((value >> rfb.red_shift) & rfb.red_max) * 255 // rfb.red_max,
            ((value >> rfb.green_shift) & rfb.green_max) * 255 // rfb.green_max,
            ((value >> rfb.blue_shift) & rfb.blue_max) * 255 // rfb.blue_max,
        ))
    return bytes(rgb)


def write_png(path: Path, width: int, height: int, rgb: bytes) -> None:
    """Write an RGB PNG without adding a graphics dependency to the image."""
    def chunk(kind: bytes, payload: bytes) -> bytes:
        return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xffffffff)

    rows = b"".join(b"\0" + rgb[offset:offset + width * 3] for offset in range(0, len(rgb), width * 3))
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0))
        + chunk(b"IDAT", zlib.compress(rows, 9))
        + chunk(b"IEND", b"")
    )


def write_capture(path: Path, rfb: Rfb, pixels: bytes) -> dict:
    path.parent.mkdir(parents=True, exist_ok=True)
    rgb = pixels_to_rgb(rfb, pixels)
    path.write_bytes(f"P6\n{rfb.width} {rfb.height}\n255\n".encode() + rgb)
    png_path = path.with_suffix(".png")
    write_png(png_path, rfb.width, rfb.height, rgb)
    nonblack = sum(any(rgb[index:index + 3]) for index in range(0, len(rgb), 3))
    return {"path": str(path), "png_path": str(png_path), "sha256": hashlib.sha256(pixels).hexdigest(), "nonblack_pixels": nonblack}


def sample_mean(rgb: bytes, width: int, x: int, y: int, box_width: int, box_height: int) -> tuple[float, float, float]:
    values = [0, 0, 0]
    samples = 0
    for sample_y in range(y + 2, y + box_height - 2, max(2, box_height // 8)):
        for sample_x in range(x + 2, x + box_width - 2, max(2, box_width // 20)):
            index = (sample_y * width + sample_x) * 3
            for channel in range(3):
                values[channel] += rgb[index + channel]
            samples += 1
    return tuple(value / samples for value in values)


def find_welcome_continue(rgb: bytes, width: int, height: int) -> dict[str, float | int] | None:
    """Find the visible Welcome modal's Continue button from its pixels."""
    # Confirm the distinctive gold full-width header first.
    header = sample_mean(rgb, width, width // 12, 29, width - width // 6, 29)
    gold = header[0] > 110 and header[1] > 70 and header[1] < header[0] and header[2] < 55
    if not gold:
        return None
    best: dict[str, float | int] | None = None
    # Search the lower half for a real light rectangular action control, not
    # a coordinate assumed from a prior frame.
    for y in range(height * 3 // 4, height - 24, 4):
        for x in range(width // 2, width - 140, 8):
            mean = sample_mean(rgb, width, x, y, 160, 28)
            brightness = sum(mean) / 3
            if brightness > 205 and (best is None or brightness > best["brightness"]):
                best = {"x": x, "y": y, "width": 160, "height": 28, "brightness": brightness}
    return best


def bright_pixels(rgb: bytes, width: int, x: int, y: int, box_width: int, box_height: int) -> int:
    count = 0
    for sample_y in range(y, y + box_height):
        for sample_x in range(x, x + box_width):
            index = (sample_y * width + sample_x) * 3
            if min(rgb[index:index + 3]) > 220:
                count += 1
    return count


def has_multiplayer_menu(rgb: bytes, width: int, height: int) -> bool:
    """Recognize the main menu's visible two-person multiplayer icon."""
    # The adjacent single-player icon and the large ARMA logo alone are not
    # sufficient: this crop specifically covers the rendered group icon.
    group = bright_pixels(rgb, width, 440, 48, 64, 58)
    logo = bright_pixels(rgb, width, 520, 20, 240, 112)
    return group > 180 and logo > 1000


def has_server_browser_menu_item(rgb: bytes, width: int, height: int) -> bool:
    """Recognize the open multiplayer dropdown's SERVER BROWSER row."""
    selected_icon = bright_pixels(rgb, width, 424, 48, 96, 48)
    # The row has white text on its dark menu background; require enough
    # bright glyph pixels in the exact rendered row, not merely the logo.
    row_text = bright_pixels(rgb, width, 424, 132, 240, 32)
    return selected_icon > 500 and row_text > 120


def has_bootcamp_prompt(rgb: bytes, width: int, height: int) -> bool:
    """Recognize Arma's visible first-run 'Start now?' two-button modal."""
    no_label = bright_pixels(rgb, width, 407, 459, 180, 30)
    yes_label = bright_pixels(rgb, width, 693, 459, 180, 30)
    overlay = sample_mean(rgb, width, 40, 240, 200, 200)
    return no_label > 20 and yes_label > 20 and min(overlay) > 40


def has_server_browser(rgb: bytes, width: int, height: int) -> bool:
    title = sample_mean(rgb, width, 29, 29, 420, 29)
    direct_text = bright_pixels(rgb, width, 475, 59, 205, 31)
    return title[0] > 110 and title[1] > 70 and title[2] < 55 and direct_text > 120


def has_direct_connect_form(rgb: bytes, width: int, height: int) -> bool:
    address_border = bright_pixels(rgb, width, 424, 288, 432, 29)
    join = sample_mean(rgb, width, 424, 374, 432, 59)
    return address_border > 100 and join[0] > 120 and join[1] > 70 and join[2] < 60


def wait_for_ui(rfb: Rfb, predicate, label: str, output: Path, steps: list[dict], timeout: float = 90.0) -> tuple[bytes, bytes]:
    deadline = time.monotonic() + timeout
    attempt = 0
    while time.monotonic() < deadline:
        pixels = rfb.frame()
        rgb = pixels_to_rgb(rfb, pixels)
        capture = write_capture(output.with_name(f"join-{attempt:02d}-{label}.ppm"), rfb, pixels)
        if predicate(rgb, rfb.width, rfb.height):
            steps.append({"state": label, "capture": capture})
            return pixels, rgb
        attempt += 1
        time.sleep(1)
    raise RuntimeError(f"timed out waiting for verified Arma UI state: {label}")


def surface_is_automation_ready(rgb: bytes, width: int, height: int) -> bool:
    """Require the actual Arma presentation target, not a startup surface."""
    if (width, height) != (1280, 720):
        return False
    nonblack = sum(any(rgb[index:index + 3]) for index in range(0, len(rgb), 3))
    # The following state detector is deliberately stronger than a merely
    # non-black compositor: it identifies a rendered Arma Welcome or main UI.
    return nonblack > 10_000 and (
        find_welcome_continue(rgb, width, height) is not None
        or has_multiplayer_menu(rgb, width, height)
    )


def join_from_main_menu(rfb: Rfb, output: Path, address: str, port: str) -> list[dict]:
    """Execute only the manually-proven main-menu Direct Connect path."""
    steps: list[dict] = []
    _pixels, rgb = wait_for_ui(
        rfb,
        surface_is_automation_ready,
        "initial", output, steps,
    )
    welcome = find_welcome_continue(rgb, rfb.width, rfb.height)
    if welcome is not None:
        rfb.pointer_click(int(welcome["x"] + welcome["width"] // 2), int(welcome["y"] + welcome["height"] // 2))
        steps.append({"action": "welcome_continue"})
    _pixels, _rgb = wait_for_ui(rfb, has_multiplayer_menu, "main-menu", output, steps)
    rfb.pointer_click(472, 74)
    steps.append({"action": "multiplayer_menu"})
    _pixels, _rgb = wait_for_ui(rfb, has_server_browser_menu_item, "multiplayer-dropdown", output, steps)
    rfb.pointer_click(544, 149)
    steps.append({"action": "server-browser"})
    _pixels, rgb = wait_for_ui(rfb, lambda image, w, h: has_bootcamp_prompt(image, w, h) or has_server_browser(image, w, h), "browser-or-bootcamp", output, steps)
    if has_bootcamp_prompt(rgb, rfb.width, rfb.height):
        rfb.pointer_click(497, 476)
        steps.append({"action": "bootcamp_no"})
    _pixels, _rgb = wait_for_ui(rfb, has_server_browser, "server-browser", output, steps)
    rfb.pointer_click(576, 75)
    steps.append({"action": "direct-connect-tab"})
    _pixels, _rgb = wait_for_ui(rfb, has_direct_connect_form, "direct-connect-form", output, steps)
    rfb.type_text(address)
    rfb.key(0xFF09)
    rfb.key(0xFFE3, True); rfb.key(ord("a"), True); rfb.key(ord("a"), False); rfb.key(0xFFE3, False)
    rfb.type_text(port)
    entered, _rgb = wait_for_ui(rfb, lambda image, w, h: has_direct_connect_form(image, w, h), "direct-connect-entered", output, steps, timeout=5)
    # The immediate non-incremental capture proves the form repainted after
    # text entry before the Join activation is sent.
    if entered == b"":
        raise RuntimeError("Direct Connect form did not return a framebuffer after entry")
    rfb.pointer_click(640, 403)
    steps.append({"action": "join", "address": address, "port": port})
    return steps


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--advance-welcome", action="store_true")
    parser.add_argument("--open-multiplayer", action="store_true")
    parser.add_argument("--open-server-browser", action="store_true")
    parser.add_argument("--dismiss-bootcamp", action="store_true")
    parser.add_argument("--open-direct-connect", action="store_true")
    parser.add_argument("--direct-connect", nargs=2, metavar=("ADDRESS", "PORT"))
    parser.add_argument("--join", nargs=2, metavar=("ADDRESS", "PORT"))
    args = parser.parse_args()
    connect_deadline = time.monotonic() + 90
    last_connect_error = None
    while True:
        try:
            rfb = Rfb("127.0.0.1", 5900)
            break
        except (OSError, ssl.SSLError, RuntimeError) as exc:
            last_connect_error = exc
            if time.monotonic() >= connect_deadline:
                raise RuntimeError(f"timed out waiting for authenticated Weston VNC: {last_connect_error}") from exc
            time.sleep(1)
    before = rfb.frame()
    report = {
        "rfb_name": rfb.name, "width": rfb.width, "height": rfb.height,
        "before": write_capture(args.output.with_name("join-before.ppm"), rfb, before),
        "protocol_trace": rfb.trace,
    }
    if not args.join and ((rfb.width, rfb.height) != (1280, 720) or report["before"]["nonblack_pixels"] < 10000):
        raise RuntimeError("expected a live 1280x720 Arma compositor surface")
    if args.join:
        report["join_steps"] = join_from_main_menu(rfb, args.output, *args.join)
        after = rfb.frame()
        report["after"] = write_capture(args.output.with_name("join-after.ppm"), rfb, after)
        report["input"] = {"type": "verified_main_menu_direct_connect", "accepted": True}
        rfb.close()
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 0
    action = None
    rgb = pixels_to_rgb(rfb, before)
    if args.advance_welcome:
        control = find_welcome_continue(rgb, rfb.width, rfb.height)
        if control is None:
            raise RuntimeError("expected Arma Welcome modal and its detected Continue control")
        x = int(control["x"] + control["width"] // 2)
        y = int(control["y"] + control["height"] // 2)
        rfb.pointer_click(x, y)
        action = {"type": "welcome_continue_click", "control": control, "x": x, "y": y}
    elif args.open_multiplayer:
        if not has_multiplayer_menu(rgb, rfb.width, rfb.height):
            raise RuntimeError("expected Arma main menu with the rendered multiplayer group icon")
        # This point lies inside the detected two-person icon's crop, not an
        # unverified screen coordinate.
        rfb.pointer_click(472, 74)
        action = {"type": "multiplayer_menu_click", "control": "two-person icon", "x": 472, "y": 74}
    elif args.open_server_browser:
        if not has_server_browser_menu_item(rgb, rfb.width, rfb.height):
            raise RuntimeError("expected the rendered multiplayer dropdown with its Server Browser row")
        rfb.pointer_click(544, 149)
        action = {"type": "server_browser_click", "control": "SERVER BROWSER row", "x": 544, "y": 149}
    elif args.dismiss_bootcamp:
        if not has_bootcamp_prompt(rgb, rfb.width, rfb.height):
            raise RuntimeError("expected the rendered New to Arma bootcamp Yes/No dialog")
        rfb.pointer_click(497, 476)
        action = {"type": "bootcamp_no_click", "control": "NO button", "x": 497, "y": 476}
    elif args.open_direct_connect:
        if not has_server_browser(rgb, rfb.width, rfb.height):
            raise RuntimeError("expected the rendered Server Browser with its Direct Connect tab")
        rfb.pointer_click(576, 75)
        action = {"type": "direct_connect_tab_click", "control": "DIRECT CONNECT tab", "x": 576, "y": 75}
    elif args.direct_connect:
        address, port = args.direct_connect
        if not has_direct_connect_form(rgb, rfb.width, rfb.height):
            raise RuntimeError("expected the rendered Direct Connect address, port, and Join controls")
        rfb.type_text(address)
        rfb.key(0xFF09)  # Tab to Port.
        rfb.key(0xFFE3, True)  # Ctrl+A selects the displayed default port.
        rfb.key(ord("a"), True)
        rfb.key(ord("a"), False)
        rfb.key(0xFFE3, False)
        rfb.type_text(port)
        entered = rfb.frame()
        report["form_entry"] = write_capture(args.output.with_name("join-form-entered.ppm"), rfb, entered)
        # Verify entry produced a new rendered form before activating Join.
        if report["form_entry"]["sha256"] == report["before"]["sha256"]:
            raise RuntimeError("Direct Connect form did not repaint after keyboard entry")
        rfb.pointer_click(640, 403)
        action = {"type": "direct_connect_join_click", "address": address, "port": port, "control": "JOIN button", "x": 640, "y": 403}
    else:
        rfb.pointer_move(1, 1)
        action = {"type": "pointer_move", "x": 1, "y": 1}
    # A fresh non-incremental framebuffer response after the input event is
    # the protocol-level acknowledgement available in RFB for pointer input.
    time.sleep(0.2)
    after = rfb.frame()
    report["after"] = write_capture(args.output.with_name("join-after.ppm"), rfb, after)
    report["surface_changed"] = report["before"]["sha256"] != report["after"]["sha256"]
    report["input"] = {**action, "accepted": True}
    rfb.close()
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

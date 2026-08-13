#!/usr/bin/env python3
"""Drive and evidence a generic rendered tab-control lifecycle over RFB."""

from __future__ import annotations

import argparse
import ctypes
import ctypes.util
import importlib.util
import json
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tribunal.observability.ui import Region, changed_pixel_fraction, selected_region_index  # noqa: E402


class X11KeyInput:
    """Deliver real X11 keycodes so Proton exposes the expected DIK events."""

    def __init__(self) -> None:
        x11_name = ctypes.util.find_library("X11")
        xtst_name = ctypes.util.find_library("Xtst")
        if not x11_name or not xtst_name:
            raise RuntimeError("X11 XTest input libraries are unavailable")
        self.x11 = ctypes.CDLL(x11_name)
        self.xtst = ctypes.CDLL(xtst_name)
        self.x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
        self.x11.XOpenDisplay.restype = ctypes.c_void_p
        self.x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
        self.x11.XKeysymToKeycode.restype = ctypes.c_uint
        self.x11.XFlush.argtypes = [ctypes.c_void_p]
        self.x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
        self.xtst.XTestFakeKeyEvent.argtypes = [
            ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong
        ]
        self.xtst.XTestFakeKeyEvent.restype = ctypes.c_int
        self.display = self.x11.XOpenDisplay(None)
        if not self.display:
            raise RuntimeError("unable to open the private Xwayland display for input")

    def key(self, keysym: int, down: bool) -> None:
        keycode = self.x11.XKeysymToKeycode(self.display, keysym)
        if not keycode or not self.xtst.XTestFakeKeyEvent(self.display, keycode, int(down), 0):
            raise RuntimeError(f"XTest rejected keysym {keysym:#x}")
        self.x11.XFlush(self.display)

    def chord(self, *keysyms: int) -> None:
        for keysym in keysyms:
            self.key(keysym, True)
            time.sleep(0.05)
        for keysym in reversed(keysyms):
            self.key(keysym, False)
            time.sleep(0.05)

    def close(self) -> None:
        if self.display:
            self.x11.XCloseDisplay(self.display)
            self.display = None


def load_rfb_module():
    path = ROOT / "client" / "container" / "vnc-join-adapter.py"
    spec = importlib.util.spec_from_file_location("tribunal_rfb_transport", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load authenticated RFB transport")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--regions", required=True, help="JSON list of x/y/width/height objects")
    parser.add_argument("--initial-index", type=int, required=True)
    parser.add_argument("--target-index", type=int, required=True)
    parser.add_argument("--timeout", type=float, default=45)
    args = parser.parse_args()
    regions = tuple(Region(**item) for item in json.loads(args.regions))
    if args.initial_index == args.target_index or not (0 <= args.initial_index < len(regions)) or not (0 <= args.target_index < len(regions)):
        raise SystemExit("initial and target indexes must be distinct valid regions")

    transport = load_rfb_module()
    rfb = transport.Rfb("127.0.0.1", 5900)
    keyboard = None
    report: dict[str, object] = {
        "schema": 1,
        "backend": "authenticated-rfb-tabbed-control",
        "status": "FAIL",
        "width": rfb.width,
        "height": rfb.height,
        "protocol_trace": rfb.trace,
        "regions": [item.__dict__ for item in regions],
    }

    def capture(label: str, pixels: bytes) -> tuple[bytes, dict]:
        rgb = transport.pixels_to_rgb(rfb, pixels)
        artifact = transport.write_capture(args.output.with_name(f"{args.output.stem}-{label}.ppm"), rfb, pixels)
        return rgb, artifact

    def wait_selected(
        expected: int,
        label: str,
        deadline: float,
        *,
        reference_rgb: bytes | None = None,
        minimum_changed_fraction: float = 0.0,
    ) -> tuple[bytes, bytes, list]:
        last_metrics = []
        last_changed_fraction = 0.0
        while time.monotonic() < deadline:
            pixels = rfb.frame()
            rgb = transport.pixels_to_rgb(rfb, pixels)
            selected, metrics = selected_region_index(rgb, rfb.width, rfb.height, regions)
            last_metrics = [item.as_dict() for item in metrics]
            last_changed_fraction = (
                changed_pixel_fraction(reference_rgb, rgb)
                if reference_rgb is not None
                else 1.0
            )
            if selected == expected and last_changed_fraction >= minimum_changed_fraction:
                return pixels, rgb, last_metrics
            time.sleep(0.1)
        raise RuntimeError(
            f"timed out waiting for selected region {expected}; "
            f"changed_fraction={last_changed_fraction}; metrics={last_metrics}"
        )

    try:
        keyboard = X11KeyInput()
        if (rfb.width, rfb.height) != (1280, 720):
            raise RuntimeError(f"unexpected framebuffer size {rfb.width}x{rfb.height}")
        deadline = time.monotonic() + args.timeout
        baseline_pixels = rfb.frame()
        baseline_rgb, report["baseline_capture"] = capture("baseline", baseline_pixels)
        report["baseline_nonblack"] = sum(any(baseline_rgb[index:index + 3]) for index in range(0, len(baseline_rgb), 3))
        if report["baseline_nonblack"] < 10_000:
            raise RuntimeError("baseline is not a live Arma surface")

        # Use the product's actual CBA Ctrl+Home keybind to open its UI. A cold
        # Xwayland game window can drop an instantaneous first chord while
        # focus settles, so retry the complete key lifecycle only while the
        # expected rendered state remains absent.
        open_pixels = open_rgb = open_metrics = None
        open_attempts = 0
        while time.monotonic() < deadline and open_pixels is None:
            open_attempts += 1
            keyboard.chord(0xFFE3, 0xFF50)
            attempt_deadline = min(deadline, time.monotonic() + 5.0)
            try:
                open_pixels, open_rgb, open_metrics = wait_selected(
                    args.initial_index, "initial", attempt_deadline
                )
            except RuntimeError:
                pass
        if open_pixels is None or open_rgb is None or open_metrics is None:
            raise RuntimeError(f"timed out opening UI after {open_attempts} verified key attempts")
        _, report["open_capture"] = capture("open", open_pixels)
        report["open_metrics"] = open_metrics
        report["open_input"] = {
            "type": "key_chord", "backend": "x11-xtest",
            "keys": ["Control_L", "Home"],
            "attempts": open_attempts, "state_driven": True,
        }
        report["baseline_to_open_changed_fraction"] = changed_pixel_fraction(baseline_rgb, open_rgb)
        if report["baseline_to_open_changed_fraction"] < 0.20:
            raise RuntimeError("UI open did not materially change the rendered surface")

        click_x, click_y = regions[args.target_index].center()
        target_pixels = target_rgb = target_metrics = None
        target_selected = None
        attempts = 0
        while attempts < 2 and target_pixels is None:
            attempts += 1
            rfb.pointer_move(click_x, click_y)
            time.sleep(0.1)
            rfb.pointer_click(click_x, click_y)
            # A hovered toolbox cell uses the same highlight as selection.
            # Move away and require the highlight to persist so focus-only
            # clicks cannot falsely count as control activation.
            rfb.pointer_move(1, 1)
            persistence_deadline = min(deadline, time.monotonic() + 2.0)
            while time.monotonic() < persistence_deadline:
                candidate_pixels = rfb.frame()
                candidate_rgb = transport.pixels_to_rgb(rfb, candidate_pixels)
                # RscToolbox highlights hover like selection. After moving
                # away, prove activation through the larger rendered page
                # transition rather than the transient tab paint alone.
                if changed_pixel_fraction(open_rgb, candidate_rgb) >= 0.015:
                    target_pixels, target_rgb = candidate_pixels, candidate_rgb
                    target_selected, metrics = selected_region_index(
                        candidate_rgb, rfb.width, rfb.height, regions
                    )
                    target_metrics = [item.as_dict() for item in metrics]
                    break
                time.sleep(0.1)
            if attempts >= 2 and target_pixels is None:
                raise RuntimeError("control activation did not produce a persistent page transition")
        _, report["target_capture"] = capture("target", target_pixels)
        report["target_metrics"] = target_metrics
        report["input"] = {
            "type": "pointer_click", "x": click_x, "y": click_y,
            "verified_region": args.target_index, "attempts": attempts,
            "hover_excluded": True,
        }
        report["selected_region_after_pointer_away"] = target_selected
        report["open_to_target_changed_fraction"] = changed_pixel_fraction(open_rgb, target_rgb)
        if report["open_to_target_changed_fraction"] < 0.01:
            raise RuntimeError("control activation did not visibly change the UI")

        # Exercise the normal user-facing Escape close path. Product-side
        # display-null evidence independently excludes another UI page being
        # mistaken for closure.
        closed_pixels = closed_rgb = None
        closed_selected = None
        close_attempts = 0
        while close_attempts < 2 and closed_pixels is None:
            close_attempts += 1
            rfb.key(0xFF1B, True)
            rfb.key(0xFF1B, False)
            attempt_deadline = min(deadline, time.monotonic() + 6.0)
            while time.monotonic() < attempt_deadline:
                candidate_pixels = rfb.frame()
                candidate_rgb = transport.pixels_to_rgb(rfb, candidate_pixels)
                selected, _metrics = selected_region_index(candidate_rgb, rfb.width, rfb.height, regions)
                if changed_pixel_fraction(target_rgb, candidate_rgb) >= 0.50:
                    closed_pixels, closed_rgb = candidate_pixels, candidate_rgb
                    closed_selected = selected
                    break
                time.sleep(0.1)
        if closed_pixels is None or closed_rgb is None:
            raise RuntimeError("UI did not visibly disappear")
        _, report["closed_capture"] = capture("closed", closed_pixels)
        report["target_to_closed_changed_fraction"] = changed_pixel_fraction(target_rgb, closed_rgb)
        report["closed_region_diagnostic"] = closed_selected
        report["close_input"] = {"type": "escape", "attempts": close_attempts}

        reopened_pixels, reopened_rgb, reopened_metrics = wait_selected(
            args.initial_index,
            "reopened",
            deadline,
            reference_rgb=closed_rgb,
            minimum_changed_fraction=0.50,
        )
        _, report["reopened_capture"] = capture("reopened", reopened_pixels)
        report["reopened_metrics"] = reopened_metrics
        report["closed_to_reopened_changed_fraction"] = changed_pixel_fraction(closed_rgb, reopened_rgb)
        if report["closed_to_reopened_changed_fraction"] < 0.20:
            raise RuntimeError("UI reopen did not materially change the rendered surface")
        report["status"] = "PASS"
    except BaseException as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if keyboard is not None:
            keyboard.close()
        rfb.close()
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

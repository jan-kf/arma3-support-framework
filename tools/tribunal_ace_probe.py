#!/usr/bin/env python3
"""Drive one verified external ACE interaction and its resulting dialog.

The feature scenario owns action names and success semantics. This adapter is
product-neutral: it captures the live surface, holds ACE's normal external-
interaction key, selects a caller-provided screen point, and activates one
caller-provided dialog region only after each rendered transition is seen.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tribunal.observability.ui import changed_pixel_fraction
from tools.tribunal_ui_probe import X11KeyInput, load_rfb_module


SUPER_L = 0xFFEB


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--interaction-point", required=True)
    parser.add_argument("--activation-region", required=True)
    parser.add_argument("--minimum-mean-luma", type=float, default=0)
    parser.add_argument("--maximum-frame-delta", type=float, default=0.12)
    parser.add_argument("--observation-hold", type=float, default=2.0)
    parser.add_argument("--timeout", type=float, default=60)
    args = parser.parse_args()
    point = json.loads(args.interaction_point)
    region = json.loads(args.activation_region)
    if len(point) != 2 or len(region) != 4:
        raise SystemExit("interaction point needs x/y; activation region needs x/y/width/height")
    if not 0 <= args.observation_hold <= 5:
        raise SystemExit("observation hold must be between 0 and 5 seconds")

    transport = load_rfb_module()
    rfb = transport.Rfb("127.0.0.1", 5900)
    keyboard = None
    report: dict[str, object] = {
        "schema": 1,
        "backend": "authenticated-rfb-ace-interaction",
        "status": "FAIL",
        "width": rfb.width,
        "height": rfb.height,
        "protocol_trace": rfb.trace,
    }

    def capture(label: str, pixels: bytes) -> tuple[bytes, dict]:
        rgb = transport.pixels_to_rgb(rfb, pixels)
        artifact = transport.write_capture(
            args.output.with_name(f"{args.output.stem}-{label}.ppm"), rfb, pixels
        )
        return rgb, artifact

    def wait_changed(
        reference: bytes, minimum: float, deadline: float, label: str
    ) -> tuple[bytes, bytes, float]:
        last = 0.0
        while time.monotonic() < deadline:
            pixels = rfb.frame()
            rgb = transport.pixels_to_rgb(rfb, pixels)
            last = changed_pixel_fraction(reference, rgb)
            if last >= minimum:
                return pixels, rgb, last
            time.sleep(0.1)
        raise RuntimeError(f"timed out waiting for {label}; changed_fraction={last}")

    def wait_stable_live_surface(deadline: float) -> tuple[bytes, bytes, list[float]]:
        previous_pixels = rfb.frame()
        previous = transport.pixels_to_rgb(rfb, previous_pixels)
        deltas: list[float] = []
        stable = 0
        while time.monotonic() < deadline:
            time.sleep(0.25)
            pixels = rfb.frame()
            rgb = transport.pixels_to_rgb(rfb, pixels)
            delta = changed_pixel_fraction(previous, rgb)
            deltas.append(delta)
            nonblack = sum(any(rgb[index:index + 3]) for index in range(0, len(rgb), 3))
            mean_luma = sum(rgb) / len(rgb)
            if (
                nonblack >= 10_000
                and mean_luma >= args.minimum_mean_luma
                and delta <= args.maximum_frame_delta
            ):
                stable += 1
                if stable >= 3:
                    return pixels, rgb, deltas
            else:
                stable = 0
            previous_pixels, previous = pixels, rgb
        raise RuntimeError(f"timed out waiting for stable live surface; deltas={deltas[-8:]}")

    def wait_overlay_closed(
        baseline: bytes, dialog: bytes, dialog_baseline_delta: float, deadline: float
    ) -> tuple[bytes, bytes, float, float]:
        last_dialog = last_baseline = 0.0
        while time.monotonic() < deadline:
            pixels = rfb.frame()
            rgb = transport.pixels_to_rgb(rfb, pixels)
            last_dialog = changed_pixel_fraction(dialog, rgb)
            last_baseline = changed_pixel_fraction(baseline, rgb)
            if last_dialog >= 0.04 and last_baseline <= (dialog_baseline_delta - 0.04):
                return pixels, rgb, last_dialog, last_baseline
            time.sleep(0.1)
        raise RuntimeError(
            "timed out waiting for verified dialog closure; "
            f"dialog_delta={last_dialog}|baseline_delta={last_baseline}"
        )

    try:
        keyboard = X11KeyInput()
        if (rfb.width, rfb.height) != (1280, 720):
            raise RuntimeError(f"unexpected framebuffer size {rfb.width}x{rfb.height}")
        deadline = time.monotonic() + args.timeout
        baseline_pixels, baseline_rgb, stabilization_deltas = wait_stable_live_surface(deadline)
        _, report["baseline_capture"] = capture("baseline", baseline_pixels)
        report["stabilization_deltas"] = stabilization_deltas
        nonblack = sum(
            any(baseline_rgb[index:index + 3])
            for index in range(0, len(baseline_rgb), 3)
        )
        report["baseline_nonblack"] = nonblack
        report["baseline_mean_luma"] = sum(baseline_rgb) / len(baseline_rgb)
        if nonblack < 10_000:
            raise RuntimeError("baseline is not a live Arma surface")

        keyboard.key(SUPER_L, True)
        rfb.pointer_move(int(point[0]), int(point[1]))
        time.sleep(0.35)
        rfb.pointer_click(int(point[0]), int(point[1]))
        keyboard.key(SUPER_L, False)

        dialog_pixels, dialog_rgb, dialog_delta = wait_changed(
            baseline_rgb, 0.15, deadline, "resulting dialog"
        )
        _, report["dialog_capture"] = capture("dialog", dialog_pixels)
        report["baseline_to_dialog_changed_fraction"] = dialog_delta
        report["interaction"] = {
            "type": "ace-external",
            "key": "Super_L",
            "point": point,
            "state_driven": True,
        }

        # A live Arma world and Draw3D preview can legitimately change behind
        # the dialog. Require the verified dialog-sized transition to persist
        # across multiple fresh frames instead of requiring pixel stasis.
        persistent_count = 0
        persistent_deltas: list[float] = []
        while time.monotonic() < deadline and persistent_count < 4:
            time.sleep(0.15)
            candidate = transport.pixels_to_rgb(rfb, rfb.frame())
            candidate_delta = changed_pixel_fraction(baseline_rgb, candidate)
            persistent_deltas.append(candidate_delta)
            if candidate_delta >= 0.15:
                persistent_count += 1
            else:
                persistent_count = 0
        report["dialog_persistence_deltas"] = persistent_deltas
        if persistent_count < 4:
            raise RuntimeError("resulting dialog transition did not persist")

        # Give the in-mission observer a bounded opportunity to record the
        # already-verified dialog before this external actor activates it.
        # This is observer synchronization, not a substitute for detecting a
        # UI transition.
        time.sleep(args.observation_hold)
        report["observation_hold_seconds"] = args.observation_hold

        x, y, width, height = (int(value) for value in region)
        click_x, click_y = x + width // 2, y + height // 2
        rfb.pointer_move(click_x, click_y)
        time.sleep(0.1)
        rfb.pointer_click(click_x, click_y)
        closed_pixels, _closed_rgb, closed_delta, closed_baseline_delta = wait_overlay_closed(
            baseline_rgb, dialog_rgb, dialog_delta, deadline
        )
        _, report["activated_capture"] = capture("activated", closed_pixels)
        report["dialog_to_activated_changed_fraction"] = closed_delta
        report["baseline_to_activated_changed_fraction"] = closed_baseline_delta
        report["activation"] = {
            "type": "pointer-click",
            "region": region,
            "point": [click_x, click_y],
            "state_driven": True,
        }
        report["status"] = "PASS"
    except Exception as exc:
        report["error"] = str(exc)
    finally:
        try:
            if keyboard is not None:
                keyboard.key(SUPER_L, False)
                keyboard.close()
        finally:
            rfb.close()
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

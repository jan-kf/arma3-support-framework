#!/usr/bin/env python3
"""Drive a tabbed map and evidence a staged marker lifecycle over RFB."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tribunal.observability.ui import (  # noqa: E402
    Region,
    changed_pixel_fraction,
    region_difference,
    selected_region_index,
)
from tribunal_ui_probe import X11KeyInput, load_rfb_module  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--regions", required=True)
    parser.add_argument("--initial-index", type=int, required=True)
    parser.add_argument("--target-index", type=int, required=True)
    parser.add_argument("--map-region", required=True)
    parser.add_argument("--expected-anchor", required=True)
    parser.add_argument("--timeout", type=float, default=55)
    args = parser.parse_args()

    regions = tuple(Region(**item) for item in json.loads(args.regions))
    map_region = Region(**json.loads(args.map_region))
    expected_anchor = json.loads(args.expected_anchor)
    anchor_pixels = (
        map_region.x + map_region.width * float(expected_anchor["x"]),
        map_region.y + map_region.height * float(expected_anchor["y"]),
    )
    transport = load_rfb_module()
    rfb = transport.Rfb("127.0.0.1", 5900)
    keyboard = None
    report: dict[str, object] = {
        "schema": 1,
        "backend": "authenticated-rfb-map-markers",
        "status": "FAIL",
        "width": rfb.width,
        "height": rfb.height,
        "protocol_trace": rfb.trace,
        "regions": [item.__dict__ for item in regions],
        "map_region": map_region.__dict__,
        "expected_anchor_pixels": anchor_pixels,
    }

    def capture(label: str, pixels: bytes) -> tuple[bytes, dict]:
        rgb = transport.pixels_to_rgb(rfb, pixels)
        artifact = transport.write_capture(
            args.output.with_name(f"{args.output.stem}-{label}.ppm"), rfb, pixels
        )
        return rgb, artifact

    def wait_selected(expected: int, deadline: float) -> tuple[bytes, bytes, list]:
        last_metrics = []
        while time.monotonic() < deadline:
            pixels = rfb.frame()
            rgb = transport.pixels_to_rgb(rfb, pixels)
            selected, metrics = selected_region_index(
                rgb, rfb.width, rfb.height, regions
            )
            last_metrics = [item.as_dict() for item in metrics]
            if selected == expected:
                return pixels, rgb, last_metrics
            time.sleep(0.1)
        raise RuntimeError(
            f"timed out waiting for selected region {expected}; metrics={last_metrics}"
        )

    def near_anchor(centroid: tuple[float, float] | None, tolerance: float = 110) -> bool:
        if centroid is None:
            return False
        return (
            abs(centroid[0] - anchor_pixels[0]) <= tolerance
            and abs(centroid[1] - anchor_pixels[1]) <= tolerance
        )

    def wait_marker_change(
        reference: bytes,
        *,
        minimum_fraction: float,
        minimum_width: int,
        minimum_height: int,
        deadline: float,
    ) -> tuple[bytes, bytes, dict]:
        last = None
        while time.monotonic() < deadline:
            pixels = rfb.frame()
            rgb = transport.pixels_to_rgb(rfb, pixels)
            difference = region_difference(
                reference, rgb, rfb.width, rfb.height, map_region
            )
            last = difference.as_dict()
            box = difference.bounding_box
            if (
                difference.changed_fraction >= minimum_fraction
                and near_anchor(difference.centroid)
                and box is not None
                and box[2] - box[0] + 1 >= minimum_width
                and box[3] - box[1] + 1 >= minimum_height
            ):
                return pixels, rgb, last
            time.sleep(0.1)
        raise RuntimeError(f"timed out waiting for localized marker change; last={last}")

    try:
        keyboard = X11KeyInput()
        if (rfb.width, rfb.height) != (1280, 720):
            raise RuntimeError(f"unexpected framebuffer size {rfb.width}x{rfb.height}")
        deadline = time.monotonic() + args.timeout
        game_pixels = rfb.frame()
        game_rgb, report["game_capture"] = capture("game", game_pixels)
        if sum(any(game_rgb[index:index + 3]) for index in range(0, len(game_rgb), 3)) < 10_000:
            raise RuntimeError("initial frame is not a live Arma surface")

        open_pixels = open_rgb = open_metrics = None
        open_attempts = 0
        while time.monotonic() < deadline and open_pixels is None:
            open_attempts += 1
            keyboard.chord(0xFFE3, 0xFF50)
            try:
                open_pixels, open_rgb, open_metrics = wait_selected(
                    args.initial_index, min(deadline, time.monotonic() + 5)
                )
            except RuntimeError:
                pass
        if open_pixels is None or open_rgb is None:
            raise RuntimeError(f"timed out opening map UI after {open_attempts} attempts")
        _, report["open_capture"] = capture("open", open_pixels)
        report["open_metrics"] = open_metrics

        click_x, click_y = regions[args.target_index].center()
        target_rgb = None
        for attempt in range(1, 3):
            rfb.pointer_move(click_x, click_y)
            time.sleep(0.1)
            rfb.pointer_click(click_x, click_y)
            rfb.pointer_move(1, 1)
            transition_deadline = min(deadline, time.monotonic() + 3)
            while time.monotonic() < transition_deadline:
                target_pixels = rfb.frame()
                target_rgb = transport.pixels_to_rgb(rfb, target_pixels)
                _selected, metrics = selected_region_index(
                    target_rgb, rfb.width, rfb.height, regions
                )
                target_metrics = [item.as_dict() for item in metrics]
                if changed_pixel_fraction(open_rgb, target_rgb) >= 0.01:
                    report["target_capture"] = capture("target", target_pixels)[1]
                    report["target_metrics"] = target_metrics
                    report["tab_input"] = {
                        "type": "pointer_click",
                        "x": click_x,
                        "y": click_y,
                        "attempts": attempt,
                        "pointer_moved_away": True,
                    }
                    break
                target_rgb = None
                time.sleep(0.1)
            if target_rgb is not None:
                break
            else:
                target_rgb = None
        if target_rgb is None:
            raise RuntimeError("artillery map page did not become visibly selected")

        # Product-side code commits a deterministic map center/scale after the
        # tab transition.  Wait for that zero-marker viewport to settle before
        # taking the reference frame.
        time.sleep(2.0)
        baseline_pixels = rfb.frame()
        baseline_rgb, report["baseline_capture"] = capture("baseline", baseline_pixels)

        one_pixels, one_rgb, one_difference = wait_marker_change(
            baseline_rgb,
            minimum_fraction=0.001,
            minimum_width=60,
            minimum_height=60,
            deadline=deadline,
        )
        report["one_capture"] = capture("one", one_pixels)[1]
        report["baseline_to_one"] = one_difference

        three_pixels, three_rgb, three_difference = wait_marker_change(
            one_rgb,
            minimum_fraction=0.004,
            minimum_width=120,
            minimum_height=120,
            deadline=deadline,
        )
        report["three_capture"] = capture("three", three_pixels)[1]
        report["one_to_three"] = three_difference

        # Exact marker/state census in the scenario proves clear and tab-owned
        # cleanup. Give those bounded transitions time to finish before the
        # independent Escape stimulus; a tab rebuild need not be pixel-identical
        # to the earlier baseline because live asset overlays may refresh.
        time.sleep(6.0)
        cleared_pixels = rfb.frame()
        cleared_rgb, report["cleared_capture"] = capture("cleared", cleared_pixels)
        report["baseline_to_cleared"] = region_difference(
            baseline_rgb, cleared_rgb, rfb.width, rfb.height, map_region
        ).as_dict()
        rfb.key(0xFF1B, True)
        rfb.key(0xFF1B, False)
        close_deadline = min(deadline, time.monotonic() + 6)
        closed = False
        while time.monotonic() < close_deadline:
            closed_pixels = rfb.frame()
            closed_rgb = transport.pixels_to_rgb(rfb, closed_pixels)
            if changed_pixel_fraction(cleared_rgb, closed_rgb) >= 0.20:
                report["closed_capture"] = capture("closed", closed_pixels)[1]
                closed = True
                break
            time.sleep(0.1)
        if not closed:
            raise RuntimeError("Escape did not visibly close the map UI")

        report["status"] = "PASS"
    except BaseException as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if keyboard is not None:
            keyboard.close()
        rfb.close()
        args.output.write_text(
            json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

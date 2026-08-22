#!/usr/bin/env python3
"""Drive authentic Arma curator-module placement through the live Zeus UI.

Feature semantics stay in the mission scenario. This adapter opens the native
curator display with real input and clicks scenario-provided screen positions
only after the mission has selected an exact configured module in the real tree.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.tribunal_ui_probe import X11KeyInput, load_rfb_module  # noqa: E402


def rpt_text() -> str:
    profile = Path("/run/pontifex/profile")
    reports = list(profile.glob("*.rpt"))
    if not reports:
        return ""
    # Steam's persistent profile intentionally retains earlier RPTs. Reading
    # all of them lets a prior run's DISPLAY_OPEN/PLACEMENT_READY markers drive
    # the current run. The actively written RPT is the newest profile artifact.
    current = max(reports, key=lambda path: path.stat().st_mtime_ns)
    return current.read_text(encoding="utf-8", errors="replace")


def wait_marker(pattern: re.Pattern[str], deadline: float) -> re.Match[str]:
    while time.monotonic() < deadline:
        match = pattern.search(rpt_text())
        if match:
            return match
        time.sleep(0.1)
    raise RuntimeError(f"timed out waiting for client marker {pattern.pattern}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--placements", type=int, default=2)
    parser.add_argument("--marker-prefix", default="TRIBUNAL_APS_ZEUS")
    parser.add_argument("--timeout", type=float, default=180)
    args = parser.parse_args()
    if not 1 <= args.placements <= 8:
        raise SystemExit("placements must be between 1 and 8")

    transport = load_rfb_module()
    rfb = transport.Rfb("127.0.0.1", 5900)
    keyboard = None
    report: dict[str, object] = {
        "schema": 1,
        "backend": "authenticated-rfb-x11-curator-placement",
        "status": "FAIL",
        "width": rfb.width,
        "height": rfb.height,
        "protocol_trace": rfb.trace,
        "inputs": [],
    }

    def capture(label: str) -> None:
        pixels = rfb.frame()
        report[f"{label}_capture"] = transport.write_capture(
            args.output.with_name(f"{args.output.stem}-{label}.ppm"), rfb, pixels
        )

    deadline = time.monotonic() + args.timeout
    try:
        if (rfb.width, rfb.height) != (1280, 720):
            raise RuntimeError(f"unexpected framebuffer size {rfb.width}x{rfb.height}")
        keyboard = X11KeyInput()
        capture("baseline")
        open_attempts = 0
        while time.monotonic() < deadline:
            open_attempts += 1
            keyboard.chord(ord("y"))
            try:
                wait_marker(re.compile(re.escape(args.marker_prefix) + r"\|DISPLAY_OPEN"), min(deadline, time.monotonic() + 4))
                break
            except RuntimeError:
                continue
        else:
            raise RuntimeError("curator display did not open")
        report["open_input"] = {"key": "Y", "attempts": open_attempts, "state_driven": True}
        capture("curator-open")

        for index in range(1, args.placements + 1):
            match = wait_marker(
                re.compile(re.escape(args.marker_prefix) + rf"\|PLACEMENT_READY\|{index}\|(\[[^\r\n]+\])"),
                deadline,
            )
            payload = json.loads(match.group(1))
            points = [payload] if len(payload) == 2 and all(isinstance(value, (int, float)) for value in payload) else payload
            if not 1 <= len(points) <= 16 or any(len(point) != 2 or not all(0 <= float(value) <= 1 for value in point) for point in points):
                raise RuntimeError(f"invalid normalized placement candidates: {payload}")
            hover_pattern = re.compile(re.escape(args.marker_prefix) + rf"\|HOVER_READY\|{index}\|")
            selected = None
            while selected is None and time.monotonic() < deadline:
                for point in points:
                    x = round(float(point[0]) * (rfb.width - 1))
                    y = round(float(point[1]) * (rfb.height - 1))
                    # Camera movement does not necessarily refresh
                    # curatorMouseOver when the requested point is already
                    # under the pointer. Force a real transition before each
                    # independently derived candidate.
                    rfb.pointer_move(1, 1)
                    time.sleep(0.1)
                    rfb.pointer_move(x, y)
                    try:
                        wait_marker(hover_pattern, min(deadline, time.monotonic() + 0.5))
                        selected = [point, x, y]
                        break
                    except RuntimeError:
                        continue
            if selected is None:
                raise RuntimeError(f"none of the placement candidates resolved the asserted hover target: {points}")
            point, x, y = selected
            rfb.pointer_click(x, y)
            wait_marker(re.compile(re.escape(args.marker_prefix) + rf"\|PLACED\|{index}\|"), deadline)
            # Curator hover state can remain latched to the object used by the
            # completed placement. Clear it before a repeated module operation
            # so the next pointer move produces a fresh engine hover transition.
            rfb.pointer_move(1, 1)
            report["inputs"].append({
                "phase": index,
                "type": "pointer-click",
                "normalized_point": point,
                "normalized_candidates": points,
                "pixel_point": [x, y],
                "pointer_moved_in": True,
                "pointer_moved_away": True,
                "state_driven": True,
            })
            capture(f"placed-{index}")

        report["status"] = "PASS"
    except Exception as exc:
        report["error"] = str(exc)
    finally:
        if keyboard is not None:
            keyboard.close()
        rfb.close()
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

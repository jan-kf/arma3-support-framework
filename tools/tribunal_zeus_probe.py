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
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(profile.glob("*.rpt"))
    )


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
                wait_marker(re.compile(r"TRIBUNAL_APS_ZEUS\|DISPLAY_OPEN"), min(deadline, time.monotonic() + 4))
                break
            except RuntimeError:
                continue
        else:
            raise RuntimeError("curator display did not open")
        report["open_input"] = {"key": "Y", "attempts": open_attempts, "state_driven": True}
        capture("curator-open")

        for index in range(1, args.placements + 1):
            match = wait_marker(
                re.compile(rf"TRIBUNAL_APS_ZEUS\|PLACEMENT_READY\|{index}\|(\[[^\r\n]+\])"),
                deadline,
            )
            point = json.loads(match.group(1))
            if len(point) != 2 or not all(0 <= float(value) <= 1 for value in point):
                raise RuntimeError(f"invalid normalized placement point: {point}")
            x = round(float(point[0]) * (rfb.width - 1))
            y = round(float(point[1]) * (rfb.height - 1))
            rfb.pointer_move(x, y)
            time.sleep(0.2)
            wait_marker(re.compile(rf"TRIBUNAL_APS_ZEUS\|HOVER_READY\|{index}\|"), deadline)
            rfb.pointer_click(x, y)
            wait_marker(re.compile(rf"TRIBUNAL_APS_ZEUS\|PLACED\|{index}\|"), deadline)
            report["inputs"].append({
                "phase": index,
                "type": "pointer-click",
                "normalized_point": point,
                "pixel_point": [x, y],
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

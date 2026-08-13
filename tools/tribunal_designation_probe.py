#!/usr/bin/env python3
"""Drive real Arma handheld/IR designation input and retain framebuffer evidence."""

from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import sys
import time


ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from tools.tribunal_ui_probe import X11KeyInput  # noqa: E402
from tribunal.observability.ui import changed_pixel_fraction  # noqa: E402


def load_rfb_module():
    path = ROOT / "client" / "container" / "vnc-join-adapter.py"
    spec = importlib.util.spec_from_file_location("tribunal_designation_rfb", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load authenticated RFB transport")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def rpt_text() -> str:
    profile = Path("/run/pontifex/profile")
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in sorted(profile.glob("*.rpt"))
    )


def wait_marker(marker: str, deadline: float) -> None:
    while time.monotonic() < deadline:
        if marker in rpt_text():
            return
        time.sleep(0.2)
    raise RuntimeError(f"timed out waiting for client marker: {marker}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout", type=float, default=240)
    args = parser.parse_args()

    transport = load_rfb_module()
    rfb = transport.Rfb("127.0.0.1", 5900)
    keyboard = None
    report: dict[str, object] = {
        "schema": 1,
        "backend": "authenticated-rfb-x11-designation-input",
        "status": "FAIL",
        "width": rfb.width,
        "height": rfb.height,
        "protocol_trace": rfb.trace,
        "inputs": [],
    }

    def capture(label: str) -> bytes:
        pixels = rfb.frame()
        rgb = transport.pixels_to_rgb(rfb, pixels)
        report[f"{label}_capture"] = transport.write_capture(
            args.output.with_name(f"{args.output.stem}-{label}.ppm"), rfb, pixels
        )
        return rgb

    deadline = time.monotonic() + args.timeout
    try:
        if (rfb.width, rfb.height) != (1280, 720):
            raise RuntimeError(f"unexpected framebuffer size {rfb.width}x{rfb.height}")
        keyboard = X11KeyInput()
        baseline = capture("baseline")
        if sum(any(baseline[index:index + 3]) for index in range(0, len(baseline), 3)) < 10_000:
            raise RuntimeError("baseline is not a live Arma surface")

        # Select the binocular-slot designator with the player's real keybind,
        # retrying only until the mission confirms the resulting weapon state.
        select_attempts = 0
        while time.monotonic() < deadline and "TRIBUNAL_FIXED_WING|HANDHELD_ARMED" not in rpt_text():
            select_attempts += 1
            keyboard.chord(ord("b"))
            time.sleep(1)
        wait_marker("TRIBUNAL_FIXED_WING|HANDHELD_ARMED", deadline)
        raised = capture("handheld-raised")
        handheld_attempts = 0
        while time.monotonic() < deadline and "TRIBUNAL_FIXED_WING|HANDHELD_ACTIVE" not in rpt_text():
            handheld_attempts += 1
            keyboard.button(1)
            time.sleep(1)
        wait_marker("TRIBUNAL_FIXED_WING|HANDHELD_ACTIVE", deadline)
        report["inputs"].append({
            "phase": "handheld", "keys": ["B", "Button1"],
            "selection_attempts": select_attempts,
            "activation_attempts": handheld_attempts, "state_driven": True,
        })
        active = capture("handheld-active")
        wait_marker("TRIBUNAL_FIXED_WING|HANDHELD_DONE", deadline)
        keyboard.button(1)
        time.sleep(0.5)

        wait_marker("TRIBUNAL_FIXED_WING|IR_ARMED", deadline)
        ir_baseline = capture("ir-baseline")
        keyboard.chord(ord("l"))
        aim_attempts = 0
        while time.monotonic() < deadline and "TRIBUNAL_FIXED_WING|IR_ACTIVE" not in rpt_text():
            aim_attempts += 1
            keyboard.relative_motion(0, 80)
            time.sleep(0.25)
        report["inputs"].append({
            "phase": "ir", "keys": ["L"], "aim": "state-driven-downward",
            "aim_attempts": aim_attempts,
        })
        wait_marker("TRIBUNAL_FIXED_WING|IR_ACTIVE", deadline)
        ir_active = capture("ir-active")
        wait_marker("TRIBUNAL_FIXED_WING|IR_DONE", deadline)
        keyboard.chord(ord("l"))
        wait_marker("TRIBUNAL_FIXED_WING|DESIGNATIONS_CLEAN", deadline)
        cleaned = capture("cleaned")

        report["frame_changes"] = {
            "handheld_raise": changed_pixel_fraction(baseline, raised),
            "handheld_active": changed_pixel_fraction(raised, active),
            "ir_active": changed_pixel_fraction(ir_baseline, ir_active),
            "cleanup": changed_pixel_fraction(ir_active, cleaned),
        }
        report["status"] = "PASS"
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        return 0
    except Exception as exc:
        report["error"] = str(exc)
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
        return 1
    finally:
        if keyboard is not None:
            keyboard.close()
        rfb.close()


if __name__ == "__main__":
    raise SystemExit(main())

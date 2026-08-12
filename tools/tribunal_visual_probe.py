#!/usr/bin/env python3
"""Capture and verify a Tribunal-owned rendered presence/removal transition."""

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

from tribunal.observability.visual import frame_metrics, visual_transition  # noqa: E402


def load_rfb_module():
    path = ROOT / "client" / "container" / "vnc-join-adapter.py"
    spec = importlib.util.spec_from_file_location("tribunal_rfb_transport", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("unable to load the authenticated RFB transport")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--timeout", type=float, default=30)
    args = parser.parse_args()
    transport = load_rfb_module()
    deadline = time.monotonic() + args.timeout
    rfb = transport.Rfb("127.0.0.1", 5900)
    report: dict[str, object] = {
        "schema": 1,
        "backend": "weston-vnc-rfb",
        "width": rfb.width,
        "height": rfb.height,
        "protocol_trace": rfb.trace,
        "status": "FAIL",
    }
    try:
        if (rfb.width, rfb.height) != (1280, 720):
            raise RuntimeError(f"unexpected framebuffer size {rfb.width}x{rfb.height}")
        baseline_pixels = rfb.frame()
        baseline_rgb = transport.pixels_to_rgb(rfb, baseline_pixels)
        baseline = frame_metrics(baseline_rgb)
        report["baseline_capture"] = transport.write_capture(args.output.with_name("visual-baseline.ppm"), rfb, baseline_pixels)
        report["baseline"] = baseline.as_dict()
        if baseline.nonblack_fraction < 0.10:
            raise RuntimeError("baseline is not a live rendered Arma surface")

        present_pixels = None
        present = None
        while time.monotonic() < deadline:
            candidate_pixels = rfb.frame()
            candidate_rgb = transport.pixels_to_rgb(rfb, candidate_pixels)
            candidate = frame_metrics(candidate_rgb)
            if candidate.dark_fraction >= 0.70 and candidate.mean_luma <= baseline.mean_luma * 0.45:
                present_pixels, present = candidate_pixels, candidate
                break
            time.sleep(0.1)
        if present is None or present_pixels is None:
            raise RuntimeError("known visual element did not become present before deadline")
        report["present_capture"] = transport.write_capture(args.output.with_name("visual-present.ppm"), rfb, present_pixels)
        report["present"] = present.as_dict()

        while time.monotonic() < deadline:
            absent_pixels = rfb.frame()
            absent_rgb = transport.pixels_to_rgb(rfb, absent_pixels)
            absent = frame_metrics(absent_rgb)
            passed, comparison = visual_transition(baseline, present, absent)
            if passed:
                report["absent_capture"] = transport.write_capture(args.output.with_name("visual-absent.ppm"), rfb, absent_pixels)
                report["comparison"] = comparison
                report["status"] = "PASS"
                break
            time.sleep(0.1)
        if report["status"] != "PASS":
            raise RuntimeError("known visual element did not become absent before deadline")
    except BaseException as exc:
        report["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        rfb.close()
        args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

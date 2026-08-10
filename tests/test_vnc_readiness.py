"""Regression coverage for bounded Arma-surface readiness classification."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("vnc_join_adapter", ROOT / "client" / "container" / "vnc-join-adapter.py")
adapter = importlib.util.module_from_spec(SPEC)
assert SPEC and SPEC.loader
SPEC.loader.exec_module(adapter)


class VncReadinessTests(unittest.TestCase):
    def test_non_arma_or_wrong_size_surfaces_are_not_ready(self) -> None:
        self.assertFalse(adapter.surface_is_automation_ready(b"\0" * (1280 * 720 * 3), 1280, 720))
        self.assertFalse(adapter.surface_is_automation_ready(b"\xff" * (1024 * 768 * 3), 1024, 768))

    def test_recognized_arma_welcome_surface_is_ready(self) -> None:
        rgb = bytearray(1280 * 720 * 3)
        # Gold header and bright lower control satisfy the same visual
        # predicate used against the real Welcome frame.
        for y in range(29, 58):
            for x in range(106, 1174):
                offset = (y * 1280 + x) * 3
                rgb[offset:offset + 3] = bytes((160, 100, 20))
        for y in range(664, 692):
            for x in range(1032, 1192):
                offset = (y * 1280 + x) * 3
                rgb[offset:offset + 3] = b"\xff\xff\xff"
        self.assertTrue(adapter.surface_is_automation_ready(bytes(rgb), 1280, 720))

    def test_direct_connect_form_requires_both_fields_and_join_anchor(self) -> None:
        rgb = bytearray(1280 * 720 * 3)
        # Address border: a real bright rectangular frame in the expected
        # form region, plus the gold Join button.
        for x in range(424, 856):
            for y in (288, 316):
                rgb[(y * 1280 + x) * 3:(y * 1280 + x) * 3 + 3] = b"\xff\xff\xff"
        for y in range(288, 317):
            for x in (424, 855):
                rgb[(y * 1280 + x) * 3:(y * 1280 + x) * 3 + 3] = b"\xff\xff\xff"
        for y in range(374, 433):
            for x in range(424, 856):
                rgb[(y * 1280 + x) * 3:(y * 1280 + x) * 3 + 3] = bytes((170, 110, 15))
        self.assertTrue(adapter.has_direct_connect_form(bytes(rgb), 1280, 720))
        self.assertFalse(adapter.has_direct_connect_form(b"\0" * len(rgb), 1280, 720))


if __name__ == "__main__":
    unittest.main()

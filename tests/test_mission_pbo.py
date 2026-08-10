"""Regression coverage for banked multiplayer-mission staging."""

from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_server as dedicated  # noqa: E402


class MissionPboTests(unittest.TestCase):
    def test_directory_is_packed_deterministically_with_valid_footer_hash(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            mission = root / "Example.Stratis"
            (mission / "nested").mkdir(parents=True)
            (mission / "mission.sqm").write_text("version=54;\n", encoding="ascii")
            (mission / "nested" / "init.sqf").write_text('diag_log "ok";\n', encoding="ascii")

            first = dedicated.build_mission_pbo(mission, root / "first.pbo")
            second = dedicated.build_mission_pbo(mission, root / "second.pbo")

            self.assertEqual(first["files"], ["mission.sqm", "nested/init.sqf"])
            self.assertEqual(first["sha256"], second["sha256"])
            payload = (root / "first.pbo").read_bytes()
            self.assertEqual(payload[-21], 0)
            self.assertEqual(payload[-20:], hashlib.sha1(payload[:-21]).digest())


if __name__ == "__main__":
    unittest.main()

"""Regression coverage for the SteamCMD official-content classifier."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_server as dedicated  # noqa: E402


class OfficialComponentPolicyTests(unittest.TestCase):
    def test_creatordlc_branch_keeps_creator_banks_explicit_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            install = Path(temporary)
            (install / "steamapps").mkdir()
            (install / "steamapps" / "appmanifest_233780.acf").write_text("manifest", encoding="utf-8")
            core = install / "addons"
            core.mkdir()
            (core / "core.pbo").write_text("", encoding="utf-8")
            for bank in ("mark", "gm", "csla", "vn", "spe", "ws", "ef", "rf"):
                addons = install / bank / "addons"
                addons.mkdir(parents=True)
                (addons / f"{bank}.pbo").write_text("", encoding="utf-8")
            previous = dedicated.LEGACY_INSTALL
            try:
                dedicated.LEGACY_INSTALL = install
                policy = dedicated.official_component_policy()
            finally:
                dedicated.LEGACY_INSTALL = previous

        self.assertEqual([item["id"] for item in policy["official_components"]], ["mark"])
        self.assertEqual(
            [item["id"] for item in policy["excluded"]["creator_or_community_dlc"]],
            ["csla", "ef", "gm", "rf", "spe", "vn", "ws"],
        )


if __name__ == "__main__":
    unittest.main()

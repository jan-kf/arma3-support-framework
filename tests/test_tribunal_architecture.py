"""Boundary contracts for the generic Tribunal framework migration."""

from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from tribunal.discovery import discover  # noqa: E402
from tribunal.runner.model import Scenario  # noqa: E402
import pontifex_multiplayer as multiplayer  # noqa: E402
import pontifex_server as dedicated  # noqa: E402


class TribunalArchitectureTests(unittest.TestCase):
    def test_pontifex_adapters_use_generic_pbo_and_protocol_boundaries(self) -> None:
        self.assertEqual(dedicated.build_mission_pbo.__module__, "tribunal.mission.pbo")
        self.assertEqual(multiplayer.TestPlan.__module__, "tribunal.runner.model")

    def test_feature_scenarios_are_discovered_outside_tribunal(self) -> None:
        scenarios = discover([
            ROOT / "source" / "advanced-systems" / "tests" / "tribunal",
            ROOT / "source" / "visual-support-tablet" / "tests" / "tribunal",
        ])
        aps = scenarios["aps-intercept"]
        self.assertIsInstance(aps, Scenario)
        self.assertEqual(aps.tier, "gameplay")
        self.assertIn("aps.positive.engaged", aps.server_expected)
        self.assertIn("aps.replication", aps.client_expected)
        self.assertEqual(multiplayer.APS_SCENARIO, aps)
        vigil = scenarios["vigil-ui"]
        self.assertEqual(vigil.metadata["visual_driver"], "tabbed-control")
        self.assertIn("vigil.input.artilleryTab", vigil.client_expected)
        self.assertIn("vigil.fixture.inputReady", vigil.client_expected)
        self.assertNotIn("ctrlShown _page", vigil.client_sqf)
        self.assertIn("ctrlEnabled _tabs", vigil.client_sqf)
        self.assertIn("lbCurSel _tabs", vigil.client_sqf)
        self.assertLess(vigil.client_sqf.index("private _inputReadyAt"), vigil.client_sqf.index('player linkItem "YSF_VigilTerminal_B"'))
        self.assertLess(vigil.client_sqf.index("vigil.fixture.inputReady"), vigil.client_sqf.index('diag_log "TRIBUNAL_VIGIL|ARMED"'))
        self.assertIn("private _reopenWorker = [] spawn", vigil.client_sqf)
        self.assertIn("[] call YSF_UI_OpenTablet", vigil.client_sqf)
        self.assertIn('"exec", "-e", "DISPLAY=:0", client_name', inspect.getsource(multiplayer))
        self.assertEqual(multiplayer.FEATURE_SCENARIOS["vigil-ui"], vigil)

    def test_generic_tribunal_sources_do_not_encode_pontifex_features(self) -> None:
        prohibited = ("aps", "iron dome", "vigil", "field utilities", "pontifex")
        for path in (ROOT / "tribunal").rglob("*.py"):
            text = path.read_text(encoding="utf-8").casefold()
            self.assertFalse(any(token in text for token in prohibited), path)


if __name__ == "__main__":
    unittest.main()

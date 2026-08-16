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
            ROOT / "source" / "field-utilities" / "tests" / "tribunal",
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
        markers = scenarios["vigil-markers"]
        self.assertEqual(markers.metadata["visual_driver"], "map-markers")
        self.assertEqual(markers.metadata["map_expected_anchor"], {"x": 0.5, "y": 0.5})
        self.assertIn("vigil.marker.firstBacking", markers.client_expected)
        self.assertIn("vigil.marker.dynamicReplacement", markers.client_expected)
        self.assertIn('["pattern", "circle"] call YOSHI_taskArty_Set', markers.client_sqf)
        self.assertIn('["spread", 50] call YOSHI_taskArty_Set', markers.client_sqf)
        self.assertIn('["dir", 0] call YOSHI_taskArty_Set', markers.client_sqf)
        self.assertIn('["count", _countControl] call YOSHI_setCount', markers.client_sqf)
        self.assertIn("_x in allMapMarkers", markers.client_sqf)
        self.assertNotIn("YOSHI_taskArty_submit", markers.client_sqf)
        self.assertEqual(multiplayer.FEATURE_SCENARIOS["vigil-markers"], markers)
        runner_source = inspect.getsource(multiplayer)
        self.assertIn('visual_driver == "map-markers"', runner_source)
        self.assertIn("/pontifex/tools/tribunal_map_probe.py", runner_source)
        self.assertIn("ui_probes_attempted: set[str]", runner_source)
        self.assertNotIn("only one interactive visual scenario", runner_source)
        gameplay = multiplayer.select_plan("gameplay")
        self.assertTrue({"vigil-ui", "vigil-markers", "vigil-artillery"}.issubset(gameplay.selected))

        artillery = scenarios["vigil-artillery"]
        self.assertEqual(artillery.metadata["targeting_modes"], "grid-only")
        self.assertEqual(artillery.metadata["patterns"], "circle,line")
        self.assertIn("vigil.artillery.vls.arrival", artillery.server_expected)
        self.assertIn("vigil.artillery.grid.invalid", artillery.client_expected)
        self.assertIn("TRIBUNAL_fnc_artilleryObserverStart", artillery.server_sqf)
        self.assertIn("call YOSHI_taskArty_submit", artillery.client_sqf)
        self.assertIn('["done", "ready_for_next"]', artillery.server_sqf)
        self.assertNotIn("laserTarget", artillery.client_sqf)

        transport = scenarios["vigil-transport"]
        self.assertEqual(transport.metadata["ui_path"], "YOSHI_taskTRN_submit/YOSHI_taskTRN_rtb")
        self.assertIn("vigil.transport.dispatch.flight", transport.server_expected)
        self.assertIn("vigil.transport.home", transport.server_expected)
        self.assertIn("vigil.transport.client.eligible", transport.client_expected)
        self.assertIn("TRIBUNAL_fnc_observeFlight", transport.server_sqf)
        self.assertIn("call YOSHI_taskTRN_submit", transport.client_sqf)
        self.assertIn("call YOSHI_taskTRN_rtb", transport.client_sqf)
        self.assertEqual(multiplayer.FEATURE_SCENARIOS["vigil-transport"], transport)
        self.assertIn("vigil-transport", gameplay.selected)

        radar = scenarios["advsys-counter-battery-radar"]
        self.assertNotIn("visual_driver", radar.metadata)
        self.assertIn("cbr.prediction.impactAccuracy", radar.server_expected)
        self.assertIn("cbr.control.disabledNoDetection", radar.server_expected)
        self.assertIn("cbr.client.warningDelivered", radar.client_expected)
        self.assertIn("TRIBUNAL_fnc_markerCensus", radar.server_sqf)
        self.assertEqual(multiplayer.FEATURE_SCENARIOS["advsys-counter-battery-radar"], radar)
        self.assertIn("advsys-counter-battery-radar", gameplay.selected)

        bridge = scenarios["fieldutils-bridge-builder"]
        self.assertNotIn("visual_driver", bridge.metadata)
        self.assertIn("bridge.traversal.authoritative", bridge.server_expected)
        self.assertIn("bridge.interaction.registration", bridge.client_expected)
        self.assertIn("bridge.interaction.conditions", bridge.client_expected)
        self.assertEqual(multiplayer.FEATURE_SCENARIOS["fieldutils-bridge-builder"], bridge)
        self.assertIn("fieldutils-bridge-builder", gameplay.selected)

    def test_generic_tribunal_sources_do_not_encode_pontifex_features(self) -> None:
        prohibited = ("aps", "iron dome", "vigil", "field utilities", "pontifex")
        for path in (ROOT / "tribunal").rglob("*.py"):
            text = path.read_text(encoding="utf-8").casefold()
            self.assertFalse(any(token in text for token in prohibited), path)


if __name__ == "__main__":
    unittest.main()

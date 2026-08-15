"""Focused regression contracts for the reviewed Bridge Builder boundary."""

from __future__ import annotations

import inspect
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from tribunal.discovery import discover  # noqa: E402
import pontifex_multiplayer as multiplayer  # noqa: E402
import tribunal_ace_probe  # noqa: E402


class BridgeBuilderContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = discover([
            ROOT / "source" / "field-utilities" / "tests" / "tribunal"
        ])["fieldutils-bridge-builder"]
        self.source = (
            ROOT / "source" / "field-utilities" / "addons" / "FieldUtils"
            / "functions" / "bridge" / "fn_bridgeUtils.sqf"
        ).read_text(encoding="utf-8")

    def test_supported_component_replaces_absent_legacy_class(self) -> None:
        self.assertNotIn("FootBridge_0_ACR", self.source)
        self.assertIn('case "Land_Plank_01_4m_F"', self.source)
        config = (
            ROOT / "source" / "field-utilities" / "addons" / "FieldUtils" / "config.cpp"
        ).read_text(encoding="utf-8")
        self.assertIn("A3_Structures_F_Exp_Civilian_Accessories", config)

    def test_mutation_is_server_authoritative_and_box_scoped(self) -> None:
        build = self.source.index("YFU_bridge_startBuildFromPlan =")
        remove = self.source.index("YFU_bridge_startRemoveFromBox =")
        self.assertIn('remoteExecCall ["YFU_bridge_startBuildFromPlan", 2]', self.source[build:remove])
        self.assertIn("YFU_bridge_validateServerRequest", self.source[build:remove])
        self.assertIn("YFU_bridge_builder_box", self.source)
        self.assertIn("YFU_bridge_segmentBelongsToBox", self.source)
        self.assertIn('_candidates = _candidates select {[_x, _sourceObject] call YFU_bridge_segmentBelongsToBox}', self.source)
        self.assertIn('remoteExecCall ["YFU_bridge_startRemoveFromBox", 2]', self.source[remove:])
        self.assertIn("private _deleteDeadline = diag_tickTime + 2;", self.source[remove:])
        self.assertIn("diag_tickTime >= _deleteDeadline", self.source[remove:])
        self.assertNotIn("YFU_bridge_getActivePlanBox", self.source)
        self.assertIn('missionNamespace getVariable ["YFU_bridge_active_plan_box", objNull]', self.source)
        self.assertIn('["YFU_Bridge_Box", 0, [], _openUiAction]', self.source)
        self.assertIn("\n\t\t8\n\t] call ace_interact_menu_fnc_createAction", self.source)

    def test_permanent_scenario_is_fail_closed_and_causal(self) -> None:
        self.assertEqual(self.scenario.review.outcome, "REWRITE BEFORE PERMANENT COVERAGE")
        self.assertIn("physical-traversal", self.scenario.review.evidence_types)
        self.assertIn("bridge.build.authority", self.scenario.server_expected)
        self.assertIn("bridge.remove.scope", self.scenario.server_expected)
        self.assertIn("lineIntersectsSurfaces", self.scenario.client_sqf)
        self.assertIn("_contactSamples >= 3", self.scenario.client_sqf)
        self.assertIn("private _originASL = [10, 10, 0];", self.scenario.server_sqf)
        self.assertIn("_boxForward vectorMultiply -5", self.scenario.client_sqf)
        self.assertIn("_boxForward vectorMultiply -3", self.scenario.client_sqf)
        self.assertIn("ace_interact_menu_fnc_collectActiveActionTree", self.scenario.client_sqf)
        self.assertIn("call (_action # 3)", self.scenario.client_sqf)
        self.assertIn("call YFU_bridge_dialogSubmit", self.scenario.client_sqf)
        self.assertIn("uiSleep 1;", self.scenario.client_sqf)
        self.assertNotIn("visual_driver", self.scenario.metadata)
        self.assertIn("TRIBUNAL_BRIDGE_REMOVE_OBSERVED", self.scenario.server_sqf)
        self.assertIn("TRIBUNAL_BRIDGE_REMOVE_OBSERVED", self.scenario.client_sqf)
        self.assertIn("private _cleanupDeadline = diag_tickTime + 2", self.scenario.server_sqf)
        self.assertNotIn("setVariable [\"YFU_bridge_last_result\"", self.scenario.client_sqf)
        self.assertIn("diag_tickTime > _buildDeadline", self.scenario.server_sqf)
        self.assertIn("_dialogDeadline = diag_tickTime + 5", self.scenario.client_sqf)
        self.assertNotIn("_heights selectMax", self.scenario.server_sqf)
        self.assertNotIn("_heights selectMin", self.scenario.server_sqf)
        self.assertIn("selectMax _heights", self.scenario.server_sqf)
        self.assertIn("selectMin _heights", self.scenario.server_sqf)

    def test_ace_driver_is_generic_and_runner_dispatches_it(self) -> None:
        driver = inspect.getsource(tribunal_ace_probe).casefold()
        self.assertNotIn("bridge", driver)
        self.assertNotIn("field utilities", driver)
        self.assertIn("--interaction-point", driver)
        self.assertIn("--activation-region", driver)
        self.assertIn("--observation-hold", driver)
        self.assertIn("dialog_persistence_deltas", driver)
        self.assertIn("wait_stable_live_surface", driver)
        self.assertIn("wait_overlay_closed", driver)
        self.assertIn("--minimum-mean-luma", driver)
        self.assertIn("--maximum-frame-delta", driver)
        runner = inspect.getsource(multiplayer)
        self.assertIn('visual_driver == "ace-interaction"', runner)
        self.assertIn('interaction_point_marker', runner)
        self.assertIn('ui_scenario.metadata.get("minimum_mean_luma", 0)', runner)
        self.assertIn('ui_scenario.metadata.get("maximum_frame_delta", 0.12)', runner)
        self.assertIn("/pontifex/tools/tribunal_ace_probe.py", runner)


if __name__ == "__main__":
    unittest.main()

"""Contracts for authentic APS curator-module activation."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_multiplayer as multiplayer  # noqa: E402


class ApsZeusModuleContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = multiplayer.FEATURE_SCENARIOS["advsys-aps-zeus-module"]
        self.addon = ROOT / "source/advanced-systems/addons/AdvSys"

    def test_scenario_uses_authentic_curator_input_and_narrow_causal_pair(self) -> None:
        self.assertEqual(self.scenario.metadata["visual_driver"], "zeus-placement")
        self.assertEqual(self.scenario.metadata["zeus_placements"], 1)
        self.assertEqual(self.scenario.metadata["visual_armed_marker"], "TRIBUNAL_APS_ZEUS|ARMED")
        self.assertTrue({
            "aps.zeus.offImpact",
            "aps.zeus.onTransition", "aps.zeus.onIntercept",
            "aps.zeus.authority", "aps.zeus.idempotence",
            "aps.zeus.logicCleanup", "aps.zeus.cleanup",
        }.issubset(self.scenario.server_expected))
        self.assertTrue({
            "aps.zeus.nativePlacement", "aps.zeus.feedback",
            "aps.zeus.clientNegativeReceipts", "aps.zeus.clientReplication",
        }.issubset(self.scenario.client_expected))
        self.assertIn("assignCurator", self.scenario.server_sqf)
        self.assertIn("addCuratorEditableObjects", self.scenario.server_sqf)
        self.assertIn("TRIBUNAL_fnc_directProjectileLaunch", self.scenario.server_sqf)
        self.assertIn("YOSHI_fnc_apsTrackProjectileLocal", self.scenario.server_sqf)
        self.assertIn("private _physicalImpact", self.scenario.server_sqf)
        self.assertIn("private _protected", self.scenario.server_sqf)
        self.assertEqual(self.scenario.server_sqf.count("call _fire;"), 2)
        self.assertIn("deleteVehicle _targetControl", self.scenario.server_sqf)
        self.assertIn("ctrlActivate (_display displayCtrl 152)", self.scenario.client_sqf)
        self.assertIn("Toggle Active Protection System (APS)", self.scenario.client_sqf)
        self.assertIn("worldToScreen", self.scenario.client_sqf)
        self.assertIn("curatorMouseOver", self.scenario.client_sqf)
        self.assertIn("HOVER_READY", self.scenario.client_sqf)
        self.assertNotIn("tvCount _tree", self.scenario.client_sqf)
        self.assertIn("_tree tvCount []", self.scenario.client_sqf)
        self.assertIn("_tree tvSetCurSel [_path # 0]", self.scenario.client_sqf)
        self.assertNotIn("call YAS_fnc_apsModuleToggle", self.scenario.server_sqf)
        self.assertNotIn("createVehicle ['YAS_APS_Zeus_Toggle_Module'", self.scenario.server_sqf)

    def test_product_boundary_binds_assigned_curator_exact_logic_target_and_operation(self) -> None:
        claim = (self.addon / "functions/aps/fn_apsZeusClaimServer.sqf").read_text(encoding="utf-8")
        toggle = (self.addon / "functions/aps/fn_apsModuleToggle.sqf").read_text(encoding="utf-8")
        result = (self.addon / "functions/aps/fn_apsZeusToggleResult.sqf").read_text(encoding="utf-8")
        client = (self.addon / "functions/client/fn_initPlayerLocal.sqf").read_text(encoding="utf-8")
        config = (self.addon / "config.cpp").read_text(encoding="utf-8")
        self.assertIn('addEventHandler ["CuratorObjectPlaced"', client)
        self.assertIn('typeOf _logic isNotEqualTo "YAS_APS_Zeus_Toggle_Module"', client)
        self.assertIn('remoteExecCall ["YAS_fnc_apsZeusClaimServer", 2]', client)
        for evidence in (
            "remoteExecutedOwner", "getAssignedCuratorLogic", "curatorEditableObjects",
            'typeOf _logic isEqualTo "YAS_APS_Zeus_Toggle_Module"',
            'YAS_APS_ZEUS_OPERATIONS', '"duplicate"',
        ):
            self.assertIn(evidence, claim)
        self.assertIn("while {(count _operations) > 127}", claim)
        self.assertIn("_operations deleteAt _oldestKey", claim)
        self.assertIn('typeOf _logic isNotEqualTo "YAS_APS_Zeus_Toggle_Module"', toggle)
        self.assertIn('(count _candidates) isEqualTo 1', toggle)
        self.assertIn("_claims deleteAt _logicId", toggle)
        self.assertIn('remoteExecCall ["YAS_fnc_apsZeusToggleResult", _requesterOwner]', toggle)
        self.assertIn('if (_accepted) then', result)
        self.assertIn('BIS_fnc_showCuratorFeedbackMessage', result)
        self.assertNotIn("YAS_fnc_notifyCurator", toggle + result)
        self.assertIn("class apsZeusClaimServer {};", config)
        self.assertIn("class apsZeusToggleResult {};", config)

    def test_generated_sqf_and_external_driver_are_registered(self) -> None:
        plan = multiplayer.select_plan("gameplay", "advsys-aps-zeus-module")
        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "Tier.Stratis"
            multiplayer.write_tier_mission(mission, "zeus-test-deadbeef", plan)
            server = (mission / "initServer.sqf").read_text(encoding="ascii")
            client = (mission / "initPlayerLocal.sqf").read_text(encoding="ascii")
        self.assertIn("aps.zeus.offImpact", server)
        self.assertIn("TRIBUNAL_APS_ZEUS|PLACEMENT_READY", client)
        self.assertNotIn("{direct_fixture_sqf()}", server)
        runner = (ROOT / "tools/pontifex_multiplayer.py").read_text(encoding="utf-8")
        driver = (ROOT / "tools/tribunal_zeus_probe.py").read_text(encoding="utf-8")
        self.assertIn('visual_driver == "zeus-placement"', runner)
        self.assertIn("tribunal_zeus_probe.py", runner)
        self.assertIn('keyboard.chord(ord("y"))', driver)
        self.assertIn("pointer_click", driver)
        self.assertIn("PLACEMENT_READY", driver)


if __name__ == "__main__":
    unittest.main()

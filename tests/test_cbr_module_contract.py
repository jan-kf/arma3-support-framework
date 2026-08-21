"""Contracts for authentic CBR Eden and curator activation."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_multiplayer as multiplayer  # noqa: E402


class CbrModuleContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = multiplayer.FEATURE_SCENARIOS["advsys-cbr-modules"]
        self.addon = ROOT / "source/advanced-systems/addons/AdvSys"

    def test_scenario_uses_authentic_entries_and_narrow_artillery_pair(self) -> None:
        self.assertEqual(self.scenario.metadata["visual_driver"], "zeus-placement")
        self.assertEqual(self.scenario.metadata["zeus_marker_prefix"], "TRIBUNAL_CBR_ZEUS")
        self.assertEqual(self.scenario.metadata["zeus_placements"], 1)
        self.assertEqual(len(self.scenario.mission_entities), 1)
        entity = self.scenario.mission_entities[0]
        self.assertEqual((entity.class_name, entity.data_type), ("YAS_CBR_Module", "Logic"))
        self.assertIn("TRIBUNAL_fnc_artilleryObserveSource", self.scenario.server_sqf)
        self.assertEqual(self.scenario.server_sqf.count("call _fire;"), 2)
        self.assertIn("cbr.module.edenCausalDetection", self.scenario.server_expected)
        self.assertIn("cbr.module.zeusOffPhysicalControl", self.scenario.server_expected)
        self.assertIn("Toggle Counter Batter Radar (CBR)", self.scenario.client_sqf)
        self.assertNotIn("call YAS_fnc_cbrModuleEnable", self.scenario.server_sqf)
        self.assertNotIn("call YAS_fnc_cbrModuleToggle", self.scenario.server_sqf)

    def test_product_boundary_is_exact_scoped_and_idempotent(self) -> None:
        eden = (self.addon / "functions/cbr/fn_cbrModuleEnable.sqf").read_text(encoding="utf-8")
        claim = (self.addon / "functions/cbr/fn_cbrZeusClaimServer.sqf").read_text(encoding="utf-8")
        toggle = (self.addon / "functions/cbr/fn_cbrModuleToggle.sqf").read_text(encoding="utf-8")
        result = (self.addon / "functions/cbr/fn_cbrZeusToggleResult.sqf").read_text(encoding="utf-8")
        client = (self.addon / "functions/client/fn_initPlayerLocal.sqf").read_text(encoding="utf-8")
        self.assertIn('_className isEqualTo "YAS_CBR_Module"', eden)
        self.assertIn("remoteExecutedOwner", eden)
        self.assertNotIn("deleteVehicle _logic", eden)
        for evidence in (
            "remoteExecutedOwner", "getAssignedCuratorLogic",
            'typeOf _logic isEqualTo "YAS_CBR_Zeus_Toggle_Module"',
            'YAS_CBR_ZEUS_OPERATIONS', '"duplicate"',
        ):
            self.assertIn(evidence, claim)
        self.assertIn('remoteExecCall ["YAS_fnc_cbrZeusToggleResult", _requesterOwner]', toggle)
        self.assertIn("deleteVehicle _logic", toggle)
        missing_claim = toggle.split('if (_claim isEqualTo []) exitWith {', 1)[1].split("};", 1)[0]
        self.assertNotIn("deleteVehicle", missing_claim)
        self.assertIn("_now - (_row param [4, _now]) > 300", claim)
        self.assertIn("_oldestAt", claim)
        self.assertIn("BIS_fnc_showCuratorFeedbackMessage", result)
        self.assertNotIn("YAS_fnc_notifyCurator", toggle + result)
        self.assertIn('typeOf _logic isEqualTo "YAS_CBR_Zeus_Toggle_Module"', client)
        self.assertIn('remoteExecCall ["YAS_fnc_cbrZeusClaimServer", 2]', client)

    def test_generated_sqf_and_generic_driver_prefix_are_registered(self) -> None:
        plan = multiplayer.select_plan("gameplay", "advsys-cbr-modules")
        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "Tier.Stratis"
            multiplayer.write_tier_mission(mission, "cbr-module-deadbeef", plan)
            server = (mission / "initServer.sqf").read_text(encoding="ascii")
            client = (mission / "initPlayerLocal.sqf").read_text(encoding="ascii")
        self.assertIn("cbr.module.edenDispatch", server)
        self.assertIn("TRIBUNAL_CBR_ZEUS|PLACEMENT_READY", client)
        runner = (ROOT / "tools/pontifex_multiplayer.py").read_text(encoding="utf-8")
        driver = (ROOT / "tools/tribunal_zeus_probe.py").read_text(encoding="utf-8")
        self.assertIn("zeus_marker_prefix", runner)
        self.assertIn("--marker-prefix", driver)
        self.assertIn("re.escape(args.marker_prefix)", driver)
        self.assertIn("max(reports, key=lambda path: path.stat().st_mtime_ns)", driver)
        self.assertIn('rfb.pointer_move(1, 1)', driver)
        self.assertIn('"pointer_moved_away": True', driver)
        self.assertNotIn('for path in sorted(profile.glob("*.rpt"))', driver)


if __name__ == "__main__":
    unittest.main()

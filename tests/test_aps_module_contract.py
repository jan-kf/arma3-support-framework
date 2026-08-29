"""Contracts for authentic typed APS Eden module activation."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_multiplayer as multiplayer  # noqa: E402


class ApsModuleContractTests(unittest.TestCase):
    def test_generated_mission_uses_real_typed_modules_and_sync_links(self) -> None:
        plan = multiplayer.select_plan("gameplay", "advsys-aps-eden-module")
        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "Tier.Stratis"
            multiplayer.write_tier_mission(mission, "module-test-deadbeef", plan)
            sqm = (mission / "mission.sqm").read_text(encoding="ascii")
            server = (mission / "initServer.sqf").read_text(encoding="ascii")
        self.assertEqual(sqm.count("type=\"YAS_APS_Module\""), 2)
        self.assertIn("dataType=\"Logic\"", sqm)
        self.assertEqual(sqm.count("type=\"Sync\""), 2)
        self.assertIn("item0=100; item1=102", sqm)
        self.assertIn("item0=101; item1=103", sqm)
        self.assertIn("\"YAS_AdvSys\"", sqm)
        self.assertNotIn("synchronizeObjectsAdd", server)
        self.assertNotIn("call YAS_fnc_apsModuleEnable", server)

    def test_scenario_requires_dispatch_physical_ab_replication_and_cleanup(self) -> None:
        scenario = multiplayer.FEATURE_SCENARIOS["advsys-aps-eden-module"]
        self.assertTrue({
            "aps.module.dispatch", "aps.module.authority", "aps.module.retained",
            "aps.module.targets", "aps.module.multiple",
            "aps.module.intercepts", "aps.module.unsyncedImpact", "aps.module.locality",
            "aps.module.cleanup",
        }.issubset(scenario.server_expected))
        self.assertIn("aps.module.clientAuthorityStimulus", scenario.client_expected)
        self.assertIn("aps.module.clientReplication", scenario.client_expected)
        self.assertEqual([entity.position[1] for entity in scenario.mission_entities if entity.data_type == "Object"], [16, 16, 16])
        self.assertIn("YAS_APS_MODULE_DISPATCH_AUDIT", scenario.server_sqf)
        self.assertIn("TRIBUNAL_fnc_directProjectileLaunch", scenario.server_sqf)
        self.assertIn("YOSHI_fnc_apsTrackProjectileLocal", scenario.server_sqf)
        self.assertIn("setVehiclePosition [[3000, 4200, 0], [], 0, \"NONE\"]", scenario.server_sqf)
        self.assertIn("private _grounded = isTouchingGround _target", scenario.server_sqf)
        self.assertIn("getCenterOfMass _target", scenario.server_sqf)
        self.assertIn("lineIntersectsSurfaces", scenario.server_sqf)
        self.assertIn("{_pathValid}", scenario.server_sqf)
        self.assertIn("private _closest = 1e9", scenario.server_sqf)
        self.assertIn("private _damageEvents", scenario.server_sqf)
        self.assertIn("private _collisionBounds = boundingBoxReal _target", scenario.server_sqf)
        self.assertIn("private _physicalImpact", scenario.server_sqf)
        self.assertIn("R_PG32V_F", scenario.server_sqf)
        self.assertIn("ammo_Penetrator_RPG32V", scenario.server_sqf)
        self.assertIn("private _protected", scenario.server_sqf)
        self.assertIn("TRIBUNAL_APS_EDEN_CLIENT_STIMULUS", scenario.server_sqf)
        self.assertIn("_target setAngularVelocity [0, 0, 0]", scenario.server_sqf)
        self.assertIn("{_stable}", scenario.server_sqf)
        self.assertIn("missionNamespace getVariable [_impactKey, false]", scenario.server_sqf)
        self.assertIn("objectFromNetId", scenario.client_sqf)


    def test_module_handler_accepts_only_native_typed_server_dispatch(self) -> None:
        source = (ROOT / "mods/advanced-systems/addons/AdvSys/functions/aps/fn_apsModuleEnable.sqf").read_text(encoding="utf-8")
        self.assertIn("_className isEqualTo \"YAS_APS_Module\"", source)
        self.assertIn("_owner isEqualTo 2", source)
        self.assertIn("_remoteOwner <= 2", source)
        self.assertIn("if (!isServer) exitWith {false}", source)
        self.assertIn("deleteRange [0, (count _audit) - 64]", source)
        self.assertNotIn("remoteExecCall [\"YAS_fnc_apsModuleEnable\", 2]", source)
        self.assertNotIn("deleteVehicle _logic", source)


if __name__ == "__main__":
    unittest.main()

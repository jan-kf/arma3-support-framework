"""Contracts for authentic Field Utilities Eden module registration."""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_multiplayer as multiplayer  # noqa: E402


class FieldUtilitiesEdenModuleContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = multiplayer.FEATURE_SCENARIOS["fieldutils-eden-modules"]
        self.addon = ROOT / "source/field-utilities/addons/FieldUtils"

    def test_scenario_uses_four_authentic_modules_and_native_syncs(self) -> None:
        modules = [entity for entity in self.scenario.mission_entities if entity.data_type == "Logic"]
        self.assertEqual(len(modules), 4)
        self.assertEqual(len(self.scenario.mission_syncs), 4)
        self.assertEqual({entity.class_name for entity in modules}, {
            "FieldUtils_Virtual_Storage_Module", "FieldUtils_Fabricator_Module",
        })
        self.assertNotIn("call YOSHI_setVirtualStorageLogic", self.scenario.server_sqf)
        self.assertNotIn("call YOSHI_setFabricatorLogic", self.scenario.server_sqf)
        self.assertIn("fabricator.module.authority", self.scenario.server_expected)
        self.assertIn("fabricator.module.inventoryToggle", self.scenario.server_expected)
        self.assertIn("fabricator.module.inventoryActionDisabled", self.scenario.client_expected)
        self.assertIn("fabricator.module.inventoryActionEnabled", self.scenario.client_expected)
        self.assertIn("ace_interact_menu_fnc_collectActiveActionTree", self.scenario.client_sqf)
        self.assertIn('"zenInventoryActions"', self.scenario.client_sqf)

    def test_server_authority_is_private_and_remote_setters_fail_closed(self) -> None:
        setters = (self.addon / "functions/global/fn_initModuleLogicSetters.sqf").read_text(encoding="utf-8")
        server = (self.addon / "functions/server/fn_fabricatorServer.sqf").read_text(encoding="utf-8")
        config = (self.addon / "config.cpp").read_text(encoding="utf-8")
        self.assertIn("remoteExecutedOwner", setters)
        self.assertIn('"remote_request"', setters)
        self.assertIn('localNamespace setVariable ["YFU_MODULE_CATALOGUE"', setters)
        self.assertIn('localNamespace setVariable ["YFU_MODULE_STATIONS"', setters)
        self.assertIn('localNamespace getVariable ["YFU_MODULE_CATALOGUE"', server)
        self.assertIn('localNamespace getVariable ["YFU_MODULE_STATIONS"', server)
        self.assertIn("FieldUtils_Virtual_Storage_Module", config.split("units[]", 1)[1].split("};", 1)[0])
        self.assertIn("FieldUtils_Fabricator_Module", config.split("units[]", 1)[1].split("};", 1)[0])

    def test_generated_mission_contains_typed_modules_and_syncs(self) -> None:
        plan = multiplayer.select_plan("gameplay", "fieldutils-eden-modules")
        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "Tier.Stratis"
            multiplayer.write_tier_mission(mission, "fieldutils-module-deadbeef", plan)
            sqm = (mission / "mission.sqm").read_text(encoding="ascii")
            server = (mission / "initServer.sqf").read_text(encoding="ascii")
        self.assertIn('type="FieldUtils_Virtual_Storage_Module";', sqm)
        self.assertIn('type="FieldUtils_Fabricator_Module";', sqm)
        self.assertEqual(sqm.count('type="Sync";'), 4)
        self.assertIn("fabricator.module.dispatch", server)


if __name__ == "__main__":
    unittest.main()

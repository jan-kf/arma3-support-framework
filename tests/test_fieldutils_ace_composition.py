"""Static contract for the Field Utilities cold-client ACE composition scenario."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tribunal.discovery import discover  # noqa: E402


class FieldUtilitiesAceCompositionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = discover([ROOT / "source" / "field-utilities" / "tests" / "tribunal"])["fieldutils-ace-composition"]

    def test_contract_is_exact_and_data_only(self) -> None:
        self.assertEqual(self.scenario.review.outcome, "KEEP AS-IS AND SPEC-TEST")
        self.assertNotIn("visual_driver", self.scenario.metadata)
        self.assertTrue({"fieldAce.registry", "fieldAce.coexistence", "fieldAce.relevance", "fieldAce.noMutation"}.issubset(self.scenario.client_expected))
        self.assertIn("ace_interact_menu_fnc_collectActiveActionTree", self.scenario.client_sqf)
        self.assertIn("ace_interact_menu_fnc_compileMenu", self.scenario.client_sqf)
        self.assertIn("canVehicleCargo", self.scenario.client_sqf)
        self.assertIn("isVehicleCargo", self.scenario.client_sqf)
        self.assertNotIn("call (_action # 3)", self.scenario.client_sqf)
        self.assertNotIn("remoteExec", self.scenario.client_sqf)

    def test_overlap_and_negative_controls_are_permanent(self) -> None:
        for action_id in (
            "YFU_BoxBridgeOpenUI_Class", "logiActions", "zenInventoryActions",
            "TowActions", "YOSHI_StowRopes", "UAV_field_task",
        ):
            self.assertIn(action_id, self.scenario.client_sqf)
        self.assertIn("_inventoryAbsent", self.scenario.client_sqf)
        self.assertIn("_stowAbsent", self.scenario.client_sqf)
        self.assertIn("_fpvAbsent", self.scenario.client_sqf)
        self.assertIn("fieldAce.cleanup", self.scenario.server_expected)


if __name__ == "__main__":
    unittest.main()

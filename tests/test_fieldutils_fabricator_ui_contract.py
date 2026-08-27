from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tribunal.discovery import discover


class FabricatorUiContractTests(unittest.TestCase):
    def setUp(self):
        self.scenario = discover([
            ROOT / "source" / "field-utilities" / "tests" / "tribunal"
        ])["fieldutils-fabricator-ui"]

    def test_evidence_contract_covers_every_permanent_assertion(self):
        contract = self.scenario.evidence_contract
        declared = {
            assertion
            for arm in contract["arms"]
            for assertion in arm["assertions"]
        }
        expected = set(self.scenario.server_expected) | set(self.scenario.client_expected)
        self.assertEqual(expected, declared)
        self.assertEqual(contract["scenario"]["version"], 2)
        self.assertEqual(len(contract["causal_relationships"]), 1)
        self.assertEqual(len(contract["propositions"]), 2)

    def test_real_dialog_controls_drive_both_arms(self):
        client = self.scenario.client_sqf
        server = self.scenario.server_sqf
        for token in (
            "call YFU_UI_OpenFabricator",
            "lbData _i",
            "lbText _i",
            "lbPicture _i",
            "lbSetCurSel",
            "ctrlActivate true",
            "call YFU_assetsQueueEntries",
            "12XX-5678",
        ):
            self.assertIn(token, client)
        self.assertIn("fabricator.ui.normalAccepted", server)
        self.assertIn("fabricator.ui.client.mixedAccepted", client)
        self.assertIn("fabricator.ui.mixedPacked", server)
        self.assertIn('[[netId _heavy, 1], [netId _light, 1]]', server)
        self.assertIn("attachedObjects _x", server)
        self.assertIn("getWeaponCargo _mixedHeavy", server)
        self.assertIn("getItemCargo _mixedLight", server)
        self.assertIn("fabricator.ui.invalidGridNoRequest", server)
        self.assertIn("YFU_fabricatorAudit", server)
        self.assertIn("TRIBUNAL_FAB_UI_fnc_census", server)

    def test_scope_excludes_unrelated_physics_and_cosmetic_progress(self):
        combined = self.scenario.client_sqf + self.scenario.server_sqf
        self.assertNotIn("surfaceIsWater", combined)
        self.assertNotIn("surfaceNormal", combined)
        self.assertNotIn("progressPosition", combined)
        self.assertNotIn("ace_dragging_isCarrying", combined)


if __name__ == "__main__":
    unittest.main()

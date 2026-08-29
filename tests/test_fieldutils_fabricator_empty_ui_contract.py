from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tribunal.discovery import discover


class FabricatorEmptyUiContractTests(unittest.TestCase):
    def setUp(self):
        self.scenario = discover([
            ROOT / "mods" / "field-utilities" / "tests" / "tribunal"
        ])["fieldutils-fabricator-empty-ui"]

    def test_evidence_contract_covers_every_permanent_assertion(self):
        contract = self.scenario.evidence_contract
        declared = {
            assertion
            for arm in contract["arms"]
            for assertion in arm["assertions"]
        }
        expected = set(self.scenario.server_expected) | set(self.scenario.client_expected)
        self.assertEqual(expected, declared)
        self.assertEqual(contract["scenario"]["version"], 1)
        self.assertEqual(len(contract["propositions"]), 1)

    def test_real_empty_module_and_dialog_actions_are_observed(self):
        client = self.scenario.client_sqf
        server = self.scenario.server_sqf
        for token in (
            "call YFU_UI_OpenFabricator",
            "lbSize _catalog",
            "_catalog lbText 0",
            "_catalog lbData 0",
            "_catalog lbPicture 0",
            "_add ctrlActivate true",
            "_submit ctrlActivate true",
            "call YFU_assetsQueueEntries",
            "tribunal-empty-queue-sentinel",
        ):
            self.assertIn(token, client)
        for token in (
            "call YOSHI_setVirtualStorageLogic",
            "fabricator.empty.noRequest",
            "YFU_fabricatorAudit",
            "YFU_fnc_fabricatorTransactions",
            'allMissionObjects "Land_CargoBox_V1_F"',
        ):
            self.assertIn(token, server)

    def test_page_initialization_clears_stale_selection(self):
        assets = (ROOT / "mods/field-utilities/addons/FieldUtils/functions/fabricator/fn_assets.sqf").read_text(encoding="utf-8")
        init = assets[assets.index("YFU_assetsInitPage = {"):assets.index("YFU_assetsQueueKeyForObject = {")]
        self.assertIn('uiNamespace setVariable ["YFU_selected_fabricator_item", objNull];', init)

    def test_scope_excludes_unrelated_physics_and_hint_rendering(self):
        combined = self.scenario.client_sqf + self.scenario.server_sqf
        self.assertNotIn("surfaceIsWater", combined)
        self.assertNotIn("surfaceNormal", combined)
        self.assertNotIn("progressPosition", combined)
        self.assertNotIn("hintSilent", combined)


if __name__ == "__main__":
    unittest.main()

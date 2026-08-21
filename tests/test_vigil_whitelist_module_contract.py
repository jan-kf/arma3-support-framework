"""Contracts for authentic Vigil whitelist Eden/Zeus activation."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_multiplayer as multiplayer  # noqa: E402


class VigilWhitelistModuleContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = multiplayer.FEATURE_SCENARIOS["vigil-whitelist-modules"]
        self.addon = ROOT / "source/visual-support-tablet/addons/VIGIL"

    def test_authentic_entries_and_one_placement_are_permanent(self) -> None:
        self.assertEqual(self.scenario.metadata["zeus_placements"], 1)
        self.assertEqual(self.scenario.metadata["zeus_marker_prefix"], "TRIBUNAL_VIGIL_WHITELIST_ZEUS")
        self.assertEqual(len([e for e in self.scenario.mission_entities if e.data_type == "Logic"]), 2)
        self.assertEqual(len(self.scenario.mission_syncs), 2)
        self.assertNotIn("call YSF_fnc_assetWhitelist", self.scenario.server_sqf)
        self.assertNotIn("call YSF_fnc_toggleObjectInWhitelist", self.scenario.server_sqf)
        self.assertIn("Add/Remove from Whitelist", self.scenario.client_sqf)

    def test_authority_and_discovery_use_server_snapshot(self) -> None:
        registry = (self.addon / "functions/global/fn_whitelistRegistry.sqf").read_text()
        claim = (self.addon / "functions/global/fn_whitelistZeusClaimServer.sqf").read_text()
        result = (self.addon / "functions/global/fn_whitelistZeusResult.sqf").read_text()
        browser = (self.addon / "functions/tablet/fn_assets.sqf").read_text()
        self.assertIn('localNamespace getVariable ["YSF_WHITELIST_MEMBERS"', registry)
        self.assertIn('missionNamespace setVariable ["YSF_WHITELISTED_ASSETS"', registry)
        self.assertNotIn("accepted_legacy", registry)
        for value in ("remoteExecutedOwner", "getAssignedCuratorLogic", "YSF_WHITELIST_ZEUS_OPERATIONS", '"duplicate"'):
            self.assertIn(value, claim)
        self.assertIn("BIS_fnc_showCuratorFeedbackMessage", result)
        self.assertIn('missionNamespace getVariable ["YSF_WHITELISTED_ASSETS"', browser)
        self.assertNotIn("synchronizedObjects YSF_WHITELISTED_ASSETS_MODULE", browser)

    def test_curator_placement_uses_the_assigned_curator_object_event(self) -> None:
        client_init = (self.addon / "functions/client/fn_initPlayerLocal.sqf").read_text()
        self.assertIn('addEventHandler ["CuratorObjectPlaced"', client_init)
        self.assertIn("getAssignedCuratorLogic player", client_init)
        self.assertIn('removeEventHandler ["CuratorObjectPlaced"', client_init)
        self.assertNotIn("call CBA_fnc_addEventHandler", client_init)


if __name__ == "__main__":
    unittest.main()

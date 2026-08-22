"""Static false-PASS boundaries for Vigil fixed-wing module coverage."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_multiplayer as multiplayer  # noqa: E402


class VigilFixedWingModuleContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = multiplayer.FEATURE_SCENARIOS["vigil-fixed-wing-modules"]
        self.server = self.scenario.server_sqf
        self.client = self.scenario.client_sqf

    def test_fixture_uses_exact_typed_modules_and_native_syncs(self) -> None:
        classes = [entity.class_name for entity in self.scenario.mission_entities]
        self.assertEqual(classes.count("YSF_FixedWing_Asset_Module"), 2)
        self.assertEqual(classes.count("YSF_FixedWing_Infil_Module"), 2)
        self.assertEqual(classes.count("YSF_FixedWing_Exfil_Module"), 2)
        self.assertEqual(len(self.scenario.mission_syncs), 2)
        self.assertNotIn("call YSF_fnc_fwModuleRegisterAssets", self.server)
        self.assertNotIn("call YSF_fnc_fwModuleRegisterPoint", self.server)

    def test_causal_oracles_and_delivered_negatives_are_fail_closed(self) -> None:
        for token in (
            "YSF_FW_MODULE_DISPATCH_AUDIT", "YSF_fwEnsureRegistry", "objectFromNetId",
            "YSF_fnc_fwSelectMissionPoint", "lastInfilPosASL", "lastExfilPosASL",
            'remoteExecCall ["YSF_fnc_fwModuleZeusClaimServer", 2]',
            '"duplicate"', '"predicate_logic_class"', "YSF_FW_ZEUS_ADD_AUDIT",
        ):
            self.assertIn(token, self.server + self.client)
        self.assertIn("TRIBUNAL_FW_CONTROL", self.server)
        self.assertIn("count _reg) isEqualTo 3", self.server)
        self.assertIn('PONTIFEX_LIVE_clientOwner', self.server)
        self.assertIn('allPlayers select {owner _x isEqualTo _requesterOwner}', self.server)
        self.assertNotIn("TRIBUNAL_FW_fnc_clientFixtureReady", self.server + self.client)
        self.assertIn("_cleanupDeadline = diag_tickTime + 5", self.server)
        self.assertIn("(call YSF_fwGetPublicRegistry) isEqualTo []", self.server)
        self.assertIn("(_logics findIf {!isNull _x}) < 0", self.server)

    def test_one_real_curator_placement_and_private_result_are_required(self) -> None:
        self.assertEqual(self.scenario.metadata["visual_driver"], "zeus-placement")
        self.assertEqual(self.scenario.metadata["zeus_placements"], 1)
        self.assertIn("Add Fixed Wing Asset", self.client)
        self.assertIn("curatorMouseOver", self.client)
        self.assertIn("addCuratorEditableObjects", self.client)
        self.assertIn("createVehicleCrew _zeusTarget", self.server)
        self.assertIn("doStop _x", self.server)
        self.assertIn("deleteVehicleCrew _control", self.server)
        self.assertIn("_projectionDeadline", self.client)
        self.assertIn("modelToWorldVisual (getCenterOfMass _target)", self.client)
        self.assertIn("lineIntersectsSurfaces", self.client)
        self.assertIn("(_x # 2) isEqualTo _target", self.client)
        self.assertIn("ASLToAGL _aimASL", self.client)
        self.assertIn("[0.075,0.075]", self.client)
        self.assertIn("_points arrayIntersect _points", self.client)
        self.assertIn("getAssignedCuratorLogic", self.server + self.client)
        self.assertIn("(_results findIf {(_x # 5) isNotEqualTo clientOwner}) < 0", self.client)

    def test_evidence_contract_covers_every_permanent_assertion(self) -> None:
        contract = self.scenario.evidence_contract
        declared = {name for arm in contract["arms"] for name in arm["assertions"]}
        expected = set(self.scenario.server_expected) | set(self.scenario.client_expected)
        self.assertEqual(declared, expected)
        self.assertTrue(contract["causal_relationships"])
        self.assertTrue(contract["propositions"])
        self.assertEqual(contract["knowledge_subject"]["key"], "pontifex:vigil:fixed-wing-module-activation")
        self.assertEqual(
            contract["knowledge_subject"]["biki_context"],
            [
                "biki-page:8458", "biki-page:14844", "biki-page:14896",
                "biki-page:14822", "biki-page:17356", "biki-page:14941",
            ],
        )
        self.assertEqual(
            {proposition["intended_use"] for proposition in contract["propositions"]},
            {"primary_result"},
        )

    def test_existing_explicit_position_lifecycle_contract_remains_available(self) -> None:
        fixed_wing = multiplayer.FEATURE_SCENARIOS["vigil-fixed-wing"]
        self.assertIn("YSF_fwRegisterAsset", fixed_wing.server_sqf)
        self.assertIn("_infil", fixed_wing.server_sqf)
        self.assertIn("_exfil", fixed_wing.server_sqf)


if __name__ == "__main__":
    unittest.main()

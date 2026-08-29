"""Contracts for Vigil whitelist Eden and product-entrypoint activation."""

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

    def test_configured_entrypoint_and_repeated_reversal_are_permanent(self) -> None:
        self.assertNotIn("visual_driver", self.scenario.metadata)
        self.assertEqual(len([e for e in self.scenario.mission_entities if e.data_type == "Logic"]), 2)
        self.assertEqual(len(self.scenario.mission_syncs), 2)
        self.assertNotIn("call YSF_fnc_assetWhitelist", self.scenario.server_sqf)
        self.assertIn("[_entrypointLogic] call YSF_fnc_toggleObjectInWhitelist", self.scenario.server_sqf)
        self.assertIn('createUnit ["YSF_Toggle_To_Whitelist_Module"', self.scenario.client_sqf)
        self.assertIn("_logic attachTo [_assetC, [0,0,0]]", self.scenario.client_sqf)
        self.assertIn('remoteExecCall ["YSF_fnc_whitelistZeusClaimServer", 2]', self.scenario.client_sqf)
        self.assertIn('remoteExecCall ["TRIBUNAL_VIGIL_WHITELIST_fnc_requestEntrypoint", 2]', self.scenario.client_sqf)
        self.assertIn('for "_phase" from 1 to 3 do', self.scenario.server_sqf)
        self.assertIn('for "_phase" from 1 to 3 do', self.scenario.client_sqf)
        self.assertIn('[netId _assetC, netId _assetC, netId _assetC]', self.scenario.server_sqf)
        self.assertIn('[true, false, true]', self.scenario.server_sqf)
        self.assertIn('[true, false, true]', self.scenario.client_sqf)
        self.assertIn("(_acceptedClaims apply {_x # 0}) isEqualTo (_acceptedToggles apply {_x # 0})", self.scenario.server_sqf)
        self.assertIn("(_acceptedClaims apply {_x # 1}) isEqualTo (_acceptedToggles apply {_x # 1})", self.scenario.server_sqf)
        self.assertIn("(_row # 0) isNotEqualTo (_activation # 1)", self.scenario.client_sqf)
        self.assertIn("(_row # 1) isNotEqualTo (_activation # 2)", self.scenario.client_sqf)
        self.assertIn("count (_activationLogicIds arrayIntersect _activationLogicIds) isEqualTo 3", self.scenario.client_sqf)
        self.assertIn("vigil.whitelist.zeusTransition2", self.scenario.server_expected)
        self.assertIn("vigil.whitelist.zeusTransition3", self.scenario.server_expected)
        self.assertIn("vigil.whitelist.edenDeletionRetires", self.scenario.server_expected)
        self.assertIn("vigil.whitelist.clientEdenRetirement", self.scenario.client_expected)
        self.assertIn("deleteVehicle _moduleA", self.scenario.server_sqf)
        self.assertIn("vigil.whitelist.fixtureStable", self.scenario.server_expected)
        self.assertIn("setVehiclePosition", self.scenario.server_sqf)
        self.assertIn("isTouchingGround", self.scenario.server_sqf)
        self.assertIn("diag_tickTime - _stableSince >= 1", self.scenario.server_sqf)
        self.assertIn("vigil.whitelist.clientFixtureStable", self.scenario.client_expected)
        self.assertIn("diag_tickTime - _replicaStableSince >= 1", self.scenario.client_sqf)
        self.assertIn("_x distance (_replicaAnchor # _forEachIndex)", self.scenario.client_sqf)
        self.assertIn("[netId _x, getPosASL _x, velocity _x, angularVelocity _x, isTouchingGround _x]", self.scenario.client_sqf)
        self.assertNotIn("findDisplay 312", self.scenario.client_sqf)
        self.assertNotIn("curatorMouseOver", self.scenario.client_sqf)
        self.assertNotIn("lineIntersectsSurfaces", self.scenario.client_sqf)
        self.assertNotIn("enableSimulation false", self.scenario.server_sqf + self.scenario.client_sqf)

    def test_authority_and_discovery_use_server_snapshot(self) -> None:
        registry = (self.addon / "functions/global/fn_whitelistRegistry.sqf").read_text()
        claim = (self.addon / "functions/global/fn_whitelistZeusClaimServer.sqf").read_text()
        result = (self.addon / "functions/global/fn_whitelistZeusResult.sqf").read_text()
        browser = (self.addon / "functions/tablet/fn_assets.sqf").read_text()
        self.assertIn('localNamespace getVariable ["YSF_WHITELIST_MEMBERS"', registry)
        self.assertIn('missionNamespace setVariable ["YSF_WHITELISTED_ASSETS"', registry)
        self.assertIn("YSF_fnc_whitelistReconcileEden", registry)
        self.assertIn('localNamespace getVariable ["YSF_WHITELIST_OVERRIDES"', registry)
        self.assertIn('localNamespace getVariable ["YSF_WHITELIST_EDEN_MONITOR"', registry)
        self.assertNotIn("accepted_legacy", registry)
        for value in ("remoteExecutedOwner", "getAssignedCuratorLogic", "target", "YSF_WHITELIST_ZEUS_OPERATIONS", '"duplicate"'):
            self.assertIn(value, claim)
        self.assertIn("BIS_fnc_showCuratorFeedbackMessage", result)
        for state_name in (
            "YSF_WHITELIST_ZEUS_CLAIMS",
            "YSF_WHITELIST_ZEUS_OPERATIONS",
            "YSF_WHITELIST_ZEUS_CLAIM_AUDIT",
            "YSF_WHITELIST_ZEUS_TOGGLE_AUDIT",
        ):
            self.assertIn(state_name, self.scenario.server_sqf)
        self.assertIn('uiNamespace setVariable ["YSF_WHITELIST_ZEUS_RESULTS", []]', self.scenario.client_sqf)
        self.assertIn('"TRIBUNAL_VIGIL_WHITELIST_ENTRYPOINT_REQUESTS"', self.scenario.server_sqf)
        self.assertIn('missionNamespace getVariable ["YSF_WHITELISTED_ASSETS"', browser)
        self.assertNotIn("synchronizedObjects YSF_WHITELISTED_ASSETS_MODULE", browser)

    def test_evidence_contract_covers_every_permanent_assertion(self) -> None:
        contract = self.scenario.evidence_contract
        declared = {name for arm in contract["arms"] for name in arm["assertions"]}
        expected = set(self.scenario.server_expected) | set(self.scenario.client_expected)
        self.assertEqual(declared, expected)
        self.assertEqual(
            contract["knowledge_subject"]["key"],
            "pontifex:vigil:asset-whitelist-modules",
        )
        self.assertEqual(
            {proposition["intended_use"] for proposition in contract["propositions"]},
            {"primary_result"},
        )
        self.assertTrue(contract["causal_relationships"])

    def test_curator_placement_uses_the_assigned_curator_object_event(self) -> None:
        client_init = (self.addon / "functions/client/fn_initPlayerLocal.sqf").read_text()
        self.assertIn('addEventHandler ["CuratorObjectPlaced"', client_init)
        self.assertIn("curatorMouseOver", client_init)
        self.assertIn("[_logic, _curator, _operationId, _target] remoteExecCall", client_init)
        self.assertIn("getAssignedCuratorLogic player", client_init)
        self.assertIn('removeEventHandler ["CuratorObjectPlaced"', client_init)
        self.assertNotIn("call CBA_fnc_addEventHandler", client_init)


if __name__ == "__main__":
    unittest.main()

"""Contracts for CORDIS routing, deduplication, results, and fan-out."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_multiplayer as multiplayer  # noqa: E402


class CordisRoutingContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.core = (ROOT / "source/core/addons/CORDIS/functions/global/fn_core.sqf").read_text(encoding="utf-8")
        self.scenario = multiplayer.FEATURE_SCENARIOS["cordis-routing"]

    def test_unknown_operations_fail_closed_before_dispatch(self) -> None:
        self.assertIn('missionNamespace getVariable [_fnName, objNull]', self.core)
        self.assertIn('["rejected", "unknown_operation"]', self.core)
        self.assertNotIn('missionNamespace getVariable [_fnName, {}]', self.core)

    def test_once_wrappers_namespace_keys_after_validation(self) -> None:
        self.assertIn("YCD_fnc_validateOnceRequest", self.core)
        self.assertIn("YCD_fnc_onceCacheKey", self.core)
        self.assertIn('["server", _fnName, _onceKey]', self.core)
        self.assertIn('["object", _fnName, _onceKey]', self.core)
        self.assertIn('["group", _fnName, _onceKey]', self.core)
        self.assertIn('["emit", _command, _onceKey]', self.core)
        self.assertIn('if (_onceKey isEqualTo "") then {""}', self.core)
        self.assertIn("private _expired = []", self.core)
        self.assertIn("{_cache deleteAt _x;} forEach _expired", self.core)

    def test_owner_resolution_is_server_brokered(self) -> None:
        object_route = self.core.split("YCD_fnc_runOnObjectOwner = {", 1)[1].split("YCD_fnc_runOnGroupOwner = {", 1)[0]
        group_route = self.core.split("YCD_fnc_runOnGroupOwner = {", 1)[1].split("YCD_fnc_onceCacheKey = {", 1)[0]
        self.assertIn('remoteExecCall ["YCD_fnc_runOnObjectOwner", 2]', object_route)
        self.assertIn('remoteExecCall ["YCD_fnc_runOnGroupOwner", 2]', group_route)
        self.assertIn("if (local _group)", group_route)
        self.assertNotIn("if (local _unit)", group_route)

    def test_explicit_empty_recipient_scope_never_broadens(self) -> None:
        notify = self.core.split("YCD_fnc_notifyCurator = {", 1)[1]
        self.assertIn('["rejected", "no_recipients"]', notify)
        self.assertNotIn("_resolvedTargets = allPlayers", notify)
        self.assertIn("_units arrayIntersect allPlayers", self.core)
        self.assertIn('isKindOf "Man"', self.core)
        self.assertIn('isKindOf "HeadlessClient_F"', self.core)
        self.assertIn("private _candidates = []", self.core)
        self.assertIn('case "OBJECT"', self.core)
        self.assertIn('case "ARRAY"', self.core)
        self.assertIn("if (_scope == 0) then {_candidates = allPlayers;}", self.core)
        self.assertIn("[_candidates] call YCD_fnc_filterPlayerUnits", self.core)

    def test_scenario_requires_independent_locality_and_recipient_receipts(self) -> None:
        self.assertEqual(self.scenario.review.test_type, "specification")
        self.assertTrue(all(key.startswith("biki-page:") for key in self.scenario.evidence_contract["knowledge_subject"]["biki_context"]))
        self.assertTrue({
            "cordis.result.states", "cordis.failure.noClaim",
            "cordis.dedupe.operationTtl", "cordis.destination.noClaim",
            "cordis.group.serverOwner", "cordis.owner.remote",
            "cordis.client.serverRoute", "cordis.recipient.fixture",
            "cordis.emit.decisions", "cordis.notify.decisions",
            "cordis.recipients.exact",
            "cordis.cleanup",
        }.issubset(self.scenario.server_expected))
        self.assertTrue({
            "cordis.client.identity", "cordis.client.queued",
            "cordis.client.ownerExecution", "cordis.client.fanout",
        }.issubset(self.scenario.client_expected))
        combined = self.scenario.server_sqf + self.scenario.client_sqf
        self.assertIn("remoteExecutedOwner", combined)
        self.assertIn("groupOwner", combined)
        self.assertIn("TRIBUNAL_CORDIS_CLIENT_RECORDS", combined)
        self.assertNotIn("BIS_fnc_showCuratorFeedbackMessage =", self.scenario.client_sqf)
        self.assertNotIn("BIS_fnc_curatorHint =", self.scenario.client_sqf)
        self.assertNotIn("replaces the exact feedback endpoints", str(self.scenario.evidence_contract))
        self.assertIn('east, format ["%1-wrong"', combined)
        self.assertIn("uiSleep 1.5", combined)


if __name__ == "__main__":
    unittest.main()

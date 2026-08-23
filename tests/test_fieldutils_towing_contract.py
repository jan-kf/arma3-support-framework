"""Static contract for Field Utilities authoritative towing."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tribunal.discovery import discover  # noqa: E402


class FieldUtilitiesTowingContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = discover(
            [ROOT / "source" / "field-utilities" / "tests" / "tribunal"]
        )["fieldutils-towing"]
        self.addon = ROOT / "source/field-utilities/addons/FieldUtils"
        self.server = (
            self.addon / "functions/ropes/fn_towingServer.sqf"
        ).read_text()
        self.init = (
            self.addon / "functions/ropes/fn_initRopes.sqf"
        ).read_text()
        self.actions = (
            self.addon / "functions/ropes/fn_ropeActions.sqf"
        ).read_text()

    def test_reachable_actions_use_authoritative_requests(self) -> None:
        self.assertIn("call YFU_fnc_towRequestAttach", self.init)
        self.assertIn("call YFU_fnc_towRequestStow", self.init)
        self.assertIn("call YFU_fnc_towRequestStow", self.actions)
        self.assertIn(
            'class towingServer { preInit = 1; };',
            (self.addon / "config.cpp").read_text(),
        )

    def test_server_retains_and_scopes_exact_rope_state(self) -> None:
        for fragment in (
            "remoteExecutedOwner",
            "YFU_TOW_OPERATIONS",
            "YFU_TOW_OBJECT_CLAIMS",
            '["ropes", _ropes]',
            "{ropeDestroy _x;};} forEach _featureRopes",
            "YFU_fnc_towMonitor",
            '"rope-lost"',
            '"active-conflict"',
            '"rope-conflict"',
            '"requester-range"',
            '"cargo-vehicle"',
        ):
            self.assertIn(fragment, self.server)
        self.assertNotIn(
            "{ ropeDestroy _x } forEach _ropes",
            self.actions,
        )

    def test_scenario_has_independent_physical_control_and_lifecycle(self) -> None:
        server = self.scenario.server_sqf
        self.assertLess(
            server.index("field.towing.noTowControl"),
            server.index('TRIBUNAL_FIELD_TOW_PHASE", "attach"'),
        )
        self.assertIn("_cargo distance2D _startCargo", server)
        self.assertIn("(_control # 5) < 1", server)
        self.assertIn("(_treatment # 5) > 15", server)
        self.assertIn("(_treatment # 5) > ((_control # 5) + 10)", server)
        self.assertIn("private _unrelated = ropeCreate", server)
        self.assertIn("_unrelated in ropes _tow", server)
        self.assertIn("ropeDestroy (_breakRopes # 0)", server)
        self.assertIn("field.towing.reuse", self.scenario.server_expected)

    def test_client_proves_action_data_receipts_and_replication(self) -> None:
        client = self.scenario.client_sqf
        for fragment in (
            "YOSHI_towRopeActions",
            "field.towing.clientAction",
            "field.towing.clientAttachResult",
            "field.towing.clientReplica",
            "field.towing.clientConflict",
            "field.towing.clientScopedStow",
            "field.towing.clientBreak",
            "field.towing.clientReuse",
            "field.towing.clientNegatives",
            "field.towing.clientIdentity",
        ):
            self.assertIn(fragment, client)
        self.assertNotIn("visual_driver", self.scenario.metadata)

    def test_evidence_contract_covers_all_permanent_assertions(self) -> None:
        contract = self.scenario.evidence_contract
        declared = {
            name
            for arm in contract["arms"]
            for name in arm["assertions"]
        }
        expected = set(self.scenario.server_expected) | set(
            self.scenario.client_expected
        )
        self.assertEqual(declared, expected)
        self.assertEqual(
            contract["knowledge_subject"]["key"],
            "pontifex:field-utilities:towing",
        )
        self.assertLessEqual(
            {arm["role"] for arm in contract["arms"]},
            {"treatment", "negative_control", "positive_control", "baseline", "counterfactual", "replicate"},
        )
        self.assertEqual(
            {p["intended_use"] for p in contract["propositions"]},
            {"primary_result"},
        )


if __name__ == "__main__":
    unittest.main()

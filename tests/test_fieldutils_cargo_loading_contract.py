"""Static contract for Field Utilities authoritative nearby supply loading."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tribunal.discovery import discover  # noqa: E402


class FieldUtilitiesCargoLoadingContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = discover(
            [ROOT / "source" / "field-utilities" / "tests" / "tribunal"]
        )["fieldutils-cargo-loading"]
        self.product = (
            ROOT / "source/field-utilities/addons/FieldUtils/functions/global/fn_objectHandling.sqf"
        ).read_text()

    def test_registered_child_routes_to_authenticated_server_request(self) -> None:
        for fragment in (
            "call YFU_fnc_cargoRequestLoad",
            'remoteExecCall ["YFU_fnc_cargoLoadRequestServer", 2]',
            "remoteExecutedOwner",
            "YFU_fnc_cargoLoadPlayer",
            "YFU_fnc_cargoLoadPairEligible",
        ):
            self.assertIn(fragment, self.product)
        self.assertNotIn("_vic setVehicleCargo _target;", self.product)

    def test_acceptance_requires_command_and_exact_membership(self) -> None:
        for fragment in (
            "private _commandAccepted = _carrier setVehicleCargo _supply",
            "private _membership = (isVehicleCargo _supply) isEqualTo _carrier",
            "private _accepted = _commandAccepted && {_membership}",
            '"duplicate"',
            '"requester-range"',
            '"pair-range"',
            '"supply-state"',
            '"capacity"',
        ):
            self.assertIn(fragment, self.product)

    def test_scenario_uses_exact_action_receipt_negatives_and_cleanup(self) -> None:
        combined = self.scenario.server_sqf + self.scenario.client_sqf
        for fragment in (
            "YOSHI_getSuppliesAction",
            "private _statement = _action param [3, {}]",
            "call _statement",
            "isVehicleCargo _supply",
            "field.cargo.noCollateral",
            "field.cargo.clientNegatives",
            "objNull setVehicleCargo _supply",
            "field.cargo.cleanup",
        ):
            self.assertIn(fragment, combined)
        self.assertNotIn("visual_driver", self.scenario.metadata)

    def test_evidence_contract_covers_every_permanent_assertion(self) -> None:
        declared = {
            assertion
            for arm in self.scenario.evidence_contract["arms"]
            for assertion in arm["assertions"]
        }
        expected = set(self.scenario.server_expected) | set(self.scenario.client_expected)
        self.assertEqual(declared, expected)
        self.assertEqual(
            self.scenario.evidence_contract["knowledge_subject"]["key"],
            "pontifex:field-utilities:cargo-loading",
        )


if __name__ == "__main__":
    unittest.main()

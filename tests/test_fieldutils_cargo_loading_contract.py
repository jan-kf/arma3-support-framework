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
        discovered = discover(
            [ROOT / "mods" / "field-utilities" / "tests" / "tribunal"]
        )
        self.scenario = discovered["fieldutils-cargo-loading"]
        self.policy_scenario = discovered["fieldutils-ace-cargo-policy"]
        self.product = (
            ROOT / "mods/field-utilities/addons/FieldUtils/functions/global/fn_objectHandling.sqf"
        ).read_text()
        self.field_config = (
            ROOT / "mods/field-utilities/addons/FieldUtils/config.cpp"
        ).read_text()
        self.advanced_config = (
            ROOT / "mods/advanced-systems/addons/AdvSys/config.cpp"
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

    def test_pontifex_boxes_explicitly_preserve_their_ace_cargo_contract(self) -> None:
        self.assertIn('configOf _object >> "YFU_preserveAceCargo"', self.product)
        self.assertGreaterEqual(self.product.count("ace_cargo_fnc_setSize"), 3)
        for config, class_name in (
            (self.field_config, "class YFU_Bridge_Box"),
            (self.advanced_config, "class YAS_OPHANIM_box"),
        ):
            body = config[config.index(class_name):]
            self.assertIn("YFU_preserveAceCargo = 1;", body[:1500])
            self.assertIn("ace_cargo_size = 2;", body[:1500])

    def test_selective_policy_scenario_uses_exact_runtime_and_load_evidence(self) -> None:
        combined = self.policy_scenario.server_sqf + self.policy_scenario.client_sqf
        for fragment in (
            "YFU_Bridge_Box",
            "YAS_OPHANIM_box",
            "B_supplyCrate_F",
            "ace_cargo_fnc_getSizeItem",
            "ace_cargo_fnc_canLoadItemIn",
            "ace_cargo_fnc_loadItem",
            'getVariable ["ace_cargo_loaded", []]',
            "field.aceCargo.selectivePolicy",
            "field.aceCargo.clientLoad",
            "field.aceCargo.cleanup",
        ):
            self.assertIn(fragment, combined)

        declared = {
            assertion
            for arm in self.policy_scenario.evidence_contract["arms"]
            for assertion in arm["assertions"]
        }
        expected = (
            set(self.policy_scenario.server_expected)
            | set(self.policy_scenario.client_expected)
        )
        self.assertEqual(declared, expected)

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

    def test_contact_lifecycle_repeats_physical_stimulus_and_deletes_attached_crate(self) -> None:
        combined = self.scenario.server_sqf + self.scenario.client_sqf
        for fragment in (
            'setVariable ["TRIBUNAL_FIELD_CONTACT_PHASE", "repeat", false]',
            '(_x # 0) isEqualTo "repeat"',
            'field.contact.repeatAttachment',
            'field.contact.clientRepeatReplica',
            'private _wasAttached = (attachedTo _treatmentCrate) isEqualTo _treatmentCarrier',
            'deleteVehicle _treatmentCrate',
            'isNull objectFromNetId _deletedCrateId',
            'attachedObjects _treatmentCarrier',
            'field.contact.deleteAttached',
            'field.contact.clientDeleteReplica',
        ):
            self.assertIn(fragment, combined)

        lifecycle = next(
            arm
            for arm in self.scenario.evidence_contract["arms"]
            if arm["key"] == "contact-lifecycle"
        )
        self.assertEqual(lifecycle["role"], "treatment")
        self.assertEqual(
            set(lifecycle["assertions"]),
            {
                "field.contact.repeatAttachment",
                "field.contact.clientRepeatReplica",
                "field.contact.deleteAttached",
                "field.contact.clientDeleteReplica",
            },
        )
        self.assertEqual(self.scenario.evidence_contract["scenario"]["version"], 3)

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

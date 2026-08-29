"""Static permanence guards for representative towing ownership migration."""

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from tribunal.discovery import discover  # noqa: E402


class FieldUtilitiesTowingMigrationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = discover(
            [ROOT / "mods" / "field-utilities" / "tests" / "tribunal"]
        )["fieldutils-towing-ownership-migration"]

    def test_exact_migration_and_finalization_contract_is_permanent(self) -> None:
        self.assertIn("field.towingMigration.activeOnClientOwner", self.scenario.server_expected)
        self.assertIn("field.towingMigration.activeSurvivesMigration", self.scenario.server_expected)
        self.assertIn("field.towingMigration.exactOnceFinalization", self.scenario.server_expected)
        self.assertIn("field.towingMigration.attachReceipt", self.scenario.client_expected)
        self.assertIn("field.towingMigration.stowReceipt", self.scenario.client_expected)

    def test_scenario_uses_public_request_entry_and_real_owner_transfers(self) -> None:
        self.assertIn("call YFU_fnc_towRequestAttach", self.scenario.client_sqf)
        self.assertIn("call YFU_fnc_towRequestStow", self.scenario.client_sqf)
        self.assertNotIn("call YFU_fnc_towRequestServer", self.scenario.server_sqf)
        self.assertIn("_tow setOwner _clientOwner", self.scenario.server_sqf)
        self.assertIn("_cargo setOwner _clientOwner", self.scenario.server_sqf)
        self.assertIn("_tow setOwner 2", self.scenario.server_sqf)
        self.assertIn("_cargo setOwner 2", self.scenario.server_sqf)

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
            "pontifex:field-utilities:towing-ownership-migration",
        )
        self.assertTrue(self.scenario.evidence_contract["knowledge_subject"]["biki_context"])
        self.assertEqual(
            self.scenario.evidence_contract["causal_relationships"][0]["relation"],
            "COMPARES_WITH",
        )


if __name__ == "__main__":
    unittest.main()

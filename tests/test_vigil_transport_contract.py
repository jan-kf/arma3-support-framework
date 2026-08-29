"""Static contract guards for the permanent Vigil transport scenario."""

from __future__ import annotations

import unittest
from pathlib import Path

from tribunal.discovery import discover


ROOT = Path(__file__).parents[1]


class VigilTransportContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenario = discover([
            ROOT / "mods" / "visual-support-tablet" / "tests" / "tribunal"
        ])["vigil-transport"]

    def test_evidence_contract_covers_every_feature_assertion_once(self) -> None:
        contract = self.scenario.evidence_contract
        self.assertEqual(contract["scenario"]["id"], self.scenario.identifier)
        self.assertEqual(contract["scenario"]["version"], 1)
        flattened = [
            assertion
            for arm in contract["arms"]
            for assertion in arm["assertions"]
        ]
        expected = set(self.scenario.server_expected) | set(self.scenario.client_expected)
        self.assertEqual(set(flattened), expected)
        self.assertEqual(len(flattened), len(set(flattened)))
        self.assertEqual(len(flattened), 25)
        proposition_assertions = {
            assertion
            for proposition in contract["propositions"]
            for assertion in proposition["assertions"]
        }
        self.assertEqual(proposition_assertions, expected)
        self.assertTrue(contract["knowledge_subject"]["biki_context"])
        arm_keys = {arm["key"] for arm in contract["arms"]}
        for relationship in contract["causal_relationships"]:
            self.assertIn(relationship["source"], arm_keys)
            self.assertIn(relationship["target"], arm_keys)
            self.assertIn(
                relationship["relation"],
                {"COMPARES_WITH", "CONTROLS_FOR", "CAUSAL_PAIR_WITH", "REPLICATES"},
            )

    def test_abnormal_arm_uses_real_request_then_exact_airborne_destruction(self) -> None:
        server = self.scenario.server_sqf
        client = self.scenario.client_sqf
        self.assertIn("call YOSHI_taskTRN_submit", client)
        self.assertIn('TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_ARMED', client)
        self.assertIn('TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_ARMED', client)
        self.assertIn('(_abnormalTask getOrDefault ["stage", -1]) isEqualTo 3', server)
        self.assertIn('_abnormalTask getOrDefault ["lzPad", objNull]', server)
        self.assertIn('!isTouchingGround _abnormalAircraft', server)
        self.assertIn('_abnormalAircraft setDamage 1;', server)
        self.assertLess(
            server.index('TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_ARMED'),
            server.index('_abnormalAircraft setDamage 1;'),
        )

    def test_abnormal_arm_proves_exact_task_pad_and_fixture_cleanup(self) -> None:
        server = self.scenario.server_sqf
        client = self.scenario.client_sqf
        for fragment in (
            '_abnormalTask getOrDefault ["id", ""]',
            '_abnormalTask getOrDefault ["gen", -1]',
            '_abnormalTask getOrDefault ["state", ""]',
            '_abnormalTask getOrDefault ["status", ""]',
            '_abnormalTask getOrDefault ["finalized", false]',
            '_abnormalManager getOrDefault ["enabled", true]',
            'objectFromNetId _abnormalPadId isEqualTo objNull',
            '["vigil.transport.abnormal.padCleanup", _padCleanupOk',
            '["vigil.transport.abnormal.cleanup", _abnormalCleanupOk',
        ):
            self.assertIn(fragment, server)
        self.assertIn('uiNamespace getVariable ["YSF_task_request_results", []]', client)
        self.assertIn('(_x # 1) isEqualTo "terminal"', client)
        self.assertIn('(_x # 5) isEqualTo "failed"', client)
        self.assertIn('TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_TERMINAL', client)
        self.assertIn('TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLEANED', client)
        self.assertIn('TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_CLEANED', client)
        self.assertIn('isNull objectFromNetId _abnormalAircraftId', client)
        self.assertIn('isNull objectFromNetId _abnormalPadId', client)
        self.assertLess(
            server.index('TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_TERMINAL'),
            server.index('deleteVehicleCrew _abnormalAircraft;'),
        )
        self.assertLess(
            server.index('TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLEANED'),
            server.index('TRIBUNAL_VIGIL_TRANSPORT_ABNORMAL_CLIENT_CLEANED'),
        )
        product = (
            ROOT
            / "mods"
            / "visual-support-tablet"
            / "addons"
            / "VIGIL"
            / "functions"
            / "task_transport"
            / "fn_transport_task.sqf"
        ).read_text(encoding="utf-8")
        self.assertIn('_t getOrDefault ["deletePadOnFinish", false]', product)
        self.assertNotIn('_t get ["deletePadOnFinish", false]', product)


if __name__ == "__main__":
    unittest.main()

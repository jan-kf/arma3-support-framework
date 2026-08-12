"""Contracts for Tribunal locality, client, evidence, and visual primitives."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tribunal.discovery import discover
from tribunal.observability.visual import frame_metrics, visual_transition
from tribunal.network import NETWORK_PROFILES
from tribunal.reporting.evidence import EvidenceAttachment, attach_evidence
from tribunal.runner.model import ClientIdentity, client_identity_map


ROOT = Path(__file__).resolve().parents[1]


class TribunalCapabilityTests(unittest.TestCase):
    def test_clients_are_keyed_without_fixed_count_or_shared_state(self) -> None:
        clients = (
            ClientIdentity("client-a", "Alpha", Path("/state/a"), 20, 5904),
            ClientIdentity("client-b", "Bravo", Path("/state/b"), 21, 5905),
            ClientIdentity("client-c", "Charlie", Path("/state/c"), 22),
        )
        keyed = client_identity_map(clients)
        self.assertEqual(tuple(keyed), ("client-a", "client-b", "client-c"))
        self.assertEqual(keyed["client-b"].address_offset, 21)
        with self.assertRaises(ValueError):
            client_identity_map((clients[0], ClientIdentity("client-b", "Bravo", Path("/state/a"), 21)))

    def test_framework_capability_scenarios_are_product_neutral(self) -> None:
        scenarios = discover([ROOT / "tribunal" / "scenarios"])
        self.assertEqual(set(scenarios), {"locality-probe", "visual-framebuffer"})
        locality = scenarios["locality-probe"]
        self.assertIn("TRIBUNAL_fnc_waitForLocality", locality.server_sqf)
        self.assertIn("tribunal.locality.clientOwned", locality.client_expected)
        self.assertEqual(scenarios["visual-framebuffer"].metadata["observability_backend"], "authenticated-rfb")

    def test_visual_transition_is_tolerant_and_fail_closed(self) -> None:
        baseline = frame_metrics(bytes((100, 120, 140)) * 100)
        present = frame_metrics(bytes((0, 0, 0)) * 90 + bytes((20, 20, 20)) * 10)
        absent = frame_metrics(bytes((90, 115, 135)) * 100)
        passed, evidence = visual_transition(baseline, present, absent)
        self.assertTrue(passed)
        self.assertTrue(evidence["appeared"])
        self.assertTrue(evidence["disappeared"])
        self.assertFalse(visual_transition(baseline, baseline, absent)[0])

    def test_evidence_attachments_extend_existing_result_schema(self) -> None:
        result = {"schema": 2, "status": "PASS", "assertions": []}
        with tempfile.TemporaryDirectory() as temporary:
            attachment = EvidenceAttachment("screenshot", "client-b", "dialog-open", Path(temporary) / "frame.png", {"matched": True})
            attach_evidence(result, attachment)
        self.assertEqual(result["schema"], 2)
        self.assertEqual(result["evidence"][0]["origin"], "client-b")
        self.assertEqual(result["evidence"][0]["metadata"], {"matched": True})

    def test_network_profiles_are_declarative_and_bounded(self) -> None:
        self.assertEqual(tuple(NETWORK_PROFILES), ("lan", "normal", "remote", "poor"))
        self.assertEqual(NETWORK_PROFILES["normal"].tc_netem_arguments(), ("delay", "25ms", "5ms"))
        self.assertEqual(NETWORK_PROFILES["poor"].tc_netem_arguments(), ("delay", "175ms", "40ms", "loss", "1%"))


if __name__ == "__main__":
    unittest.main()

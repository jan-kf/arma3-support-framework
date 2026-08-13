"""Contracts for Tribunal locality, client, evidence, and visual primitives."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from tribunal.discovery import discover
from tribunal.mission.aviation import aviation_observer_sqf
from tribunal.mission.combat import combat_observer_sqf
from tribunal.mission.designation import designation_observer_sqf
from tribunal.observability.visual import frame_metrics, visual_transition
from tribunal.observability.ui import Region, changed_pixel_fraction, region_difference, selected_region_index
from tribunal.network import NETWORK_PROFILES
from tribunal.reporting.evidence import EvidenceAttachment, attach_evidence
from tribunal.runner.model import ClientIdentity, client_identity_map


ROOT = Path(__file__).resolve().parents[1]


class TribunalCapabilityTests(unittest.TestCase):
    def test_combat_observer_correlates_fire_damage_and_locality(self) -> None:
        source = combat_observer_sqf()
        for token in (
            "TRIBUNAL_fnc_combatObserverStart",
            "TRIBUNAL_fnc_combatObserveSource",
            "TRIBUNAL_fnc_combatObserveTarget",
            'addEventHandler ["Fired"',
            'addEventHandler ["HandleDamage"',
            'addEventHandler ["HitPart"',
            'addEventHandler ["Killed"',
            'assignedTarget _controller',
            '["hitDetails", []]',
            '["projectile", if (isNull _projectile)',
            '["sourceLocal", local _source]',
            '["projectileLocal", !isNull _projectile',
            "TRIBUNAL_fnc_combatObserverStop",
        ):
            self.assertIn(token, source)
        for product_token in ("YOSHI_", "YSF_", "cas_state", "transport_state"):
            self.assertNotIn(product_token, source)

    def test_designation_observer_is_identity_locality_and_lifetime_generic(self) -> None:
        source = designation_observer_sqf()
        for token in (
            "TRIBUNAL_fnc_designationRecord",
            "TRIBUNAL_fnc_observeDesignation",
            "TRIBUNAL_fnc_designationEvidence",
            '["designation", if (isNull _designation)',
            '["designationLocal", !isNull _designation',
            '["designationOwner", if (isNull _designation)',
            '["positionASL", if (isNull _designation)',
            '["stableIdentity", (count _identities) isEqualTo 1]',
        ):
            self.assertIn(token, source)
        for product_token in ("YOSHI_", "YSF_", "Vigil", "irFakeLaserTarget"):
            self.assertNotIn(product_token, source)

    def test_aviation_observer_is_physical_and_product_neutral(self) -> None:
        source = aviation_observer_sqf()
        for token in (
            "TRIBUNAL_fnc_aviationSample",
            "TRIBUNAL_fnc_observeFlight",
            "TRIBUNAL_fnc_flightEvidence",
            "isTouchingGround",
            "velocity _aircraft",
            '"landed"',
        ):
            self.assertIn(token, source)
        for product_token in ("YOSHI_", "YSF_", "Vigil", "transport_state"):
            self.assertNotIn(product_token, source)

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

    def test_tabbed_control_detection_uses_regions_and_contrast(self) -> None:
        width, height = 8, 2
        frame = bytearray((0, 15, 0) * width * height)
        regions = (Region(0, 0, 4, 2), Region(4, 0, 4, 2))
        for y in range(2):
            for x in range(4, 8):
                offset = (y * width + x) * 3
                frame[offset:offset + 3] = bytes((0, 100, 0))
        selected, metrics = selected_region_index(bytes(frame), width, height, regions)
        self.assertEqual(selected, 1)
        self.assertGreater(metrics[1].mean_luma, metrics[0].mean_luma)
        self.assertGreater(changed_pixel_fraction(bytes((0, 0, 0)) * width * height, bytes(frame)), 0.4)
        self.assertIsNone(selected_region_index(bytes((0, 50, 0)) * width * height, width, height, regions)[0])

    def test_region_difference_is_bounded_and_reports_position(self) -> None:
        width, height = 8, 4
        baseline = bytes((0, 0, 0)) * width * height
        changed = bytearray(baseline)
        for x, y in ((3, 1), (4, 1), (4, 2)):
            offset = (y * width + x) * 3
            changed[offset:offset + 3] = bytes((0, 255, 0))

        evidence = region_difference(
            baseline, bytes(changed), width, height, Region(2, 1, 4, 2)
        )
        self.assertEqual(evidence.changed_pixels, 3)
        self.assertEqual(evidence.bounding_box, (3, 1, 4, 2))
        self.assertEqual(evidence.centroid, (11 / 3, 4 / 3))
        self.assertEqual(evidence.changed_fraction, 3 / 8)
        self.assertEqual(
            region_difference(
                baseline, bytes(changed), width, height, Region(0, 0, 2, 4)
            ).changed_pixels,
            0,
        )

    def test_tabbed_control_driver_retries_cold_key_chord_by_state(self) -> None:
        source = (ROOT / "tools" / "tribunal_ui_probe.py").read_text(encoding="utf-8")
        self.assertIn("while time.monotonic() < deadline and open_pixels is None", source)
        self.assertIn('"state_driven": True', source)
        self.assertIn('"backend": "x11-xtest"', source)
        self.assertIn("XTestFakeKeyEvent", source)
        self.assertIn("timed out opening UI after", source)

    def test_designation_driver_uses_real_bounded_input_and_state_markers(self) -> None:
        source = (ROOT / "tools" / "tribunal_designation_probe.py").read_text(encoding="utf-8")
        for token in (
            'keyboard.chord(ord("b"))',
            "keyboard.button(1)",
            'keyboard.chord(ord("l"))',
            "keyboard.relative_motion(0, 80)",
            '"aim": "state-driven-downward"',
            'while time.monotonic() < deadline and "TRIBUNAL_FIXED_WING|HANDHELD_ACTIVE" not in rpt_text()',
            '"activation_attempts": handheld_attempts, "state_driven": True',
            "TRIBUNAL_FIXED_WING|HANDHELD_ACTIVE",
            "TRIBUNAL_FIXED_WING|HANDHELD_DONE",
            "TRIBUNAL_FIXED_WING|IR_ACTIVE",
            "TRIBUNAL_FIXED_WING|IR_DONE",
            "TRIBUNAL_FIXED_WING|DESIGNATIONS_CLEAN",
            '"status"] = "PASS"',
        ):
            self.assertIn(token, source)

        input_source = (ROOT / "tools" / "tribunal_ui_probe.py").read_text(encoding="utf-8")
        self.assertIn("XTestFakeRelativeMotionEvent", input_source)
        button_body = input_source.split("def button", 1)[1].split("def relative_motion", 1)[0]
        motion_body = input_source.split("def relative_motion", 1)[1].split("def close", 1)[0]
        self.assertEqual(button_body.count("XTestFakeButtonEvent"), 2)
        self.assertEqual(motion_body.count("XTestFakeRelativeMotionEvent"), 1)
        self.assertNotIn("XTestFakeButtonEvent", motion_body)

    def test_tabbed_control_reopen_rejects_false_selected_region_on_game_surface(self) -> None:
        source = (ROOT / "tools" / "tribunal_ui_probe.py").read_text(encoding="utf-8")
        self.assertIn("reference_rgb=closed_rgb", source)
        self.assertIn("minimum_changed_fraction=0.50", source)
        self.assertIn(
            "selected == expected and last_changed_fraction >= minimum_changed_fraction",
            source,
        )

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

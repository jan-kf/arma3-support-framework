"""Contracts for generic artillery observation and spatial evidence."""

from __future__ import annotations

import unittest
from pathlib import Path

from tribunal.mission.artillery import artillery_observer_sqf, spatial_evidence
from tribunal.discovery import discover


class TribunalArtilleryTests(unittest.TestCase):
    def test_spatial_evidence_distinguishes_a_line_from_radial_error(self) -> None:
        evidence = spatial_evidence(((100, 80), (100, 90), (100, 110), (100, 120)), (100, 100), 0)
        self.assertEqual(evidence.count, 4)
        self.assertEqual(evidence.centroid, (100, 100))
        self.assertEqual(evidence.along_axis, (-20.0, -10.0, 10.0, 20.0))
        self.assertEqual(evidence.perpendicular_error, (0.0, 0.0, 0.0, 0.0))
        self.assertEqual(evidence.maximum_radial_error, 20.0)

    def test_spatial_evidence_rejects_missing_impacts(self) -> None:
        with self.assertRaises(ValueError):
            spatial_evidence((), (0, 0))

    def test_sqf_observer_correlates_exact_sources_projectiles_and_termination(self) -> None:
        source = artillery_observer_sqf()
        self.assertIn('addMissionEventHandler ["ArtilleryShellFired"', source)
        self.assertIn('_source addEventHandler ["Fired"', source)
        self.assertIn('["projectile", _uid]', source)
        self.assertIn('["projectileObject", _projectile]', source)
        self.assertIn('isEqualTo _shell', source)
        self.assertIn('["pendingArtillery", []]', source)
        self.assertIn('_pending findIf {(_x # 0) isEqualTo _projectile}', source)
        self.assertIn('_event set ["artilleryEvent", true]', source)
        self.assertIn('["sourceLocal", local _source]', source)
        self.assertIn('["projectileLocal", !isNull _projectile', source)
        self.assertIn('["lastPosition", []]', source)
        self.assertIn('["terminated", false]', source)
        self.assertIn('TRIBUNAL_ARTILLERY|%1|FIRED', source)
        self.assertIn('TRIBUNAL_ARTILLERY|%1|TERMINAL', source)

    def test_long_artillery_flight_completes_before_client_ack_window(self) -> None:
        scenario = (Path(__file__).parents[1] / "mods/visual-support-tablet/tests/tribunal/vigil_artillery.py").read_text(encoding="utf-8")
        self.assertIn('missionNamespace setVariable ["TRIBUNAL_VIGIL_ARTILLERY_COMPLETE", _token, true]', scenario)
        self.assertIn("private _completionDeadline = diag_tickTime + 300;", scenario)
        self.assertIn('(missionNamespace getVariable ["TRIBUNAL_VIGIL_ARTILLERY_COMPLETE", ""]) isEqualTo _token', scenario)

    def test_vls_scenario_proves_exact_product_target_deletion(self) -> None:
        scenario = (Path(__file__).parents[1] / "mods/visual-support-tablet/tests/tribunal/vigil_artillery.py").read_text(encoding="utf-8")
        self.assertIn('private _vlsTargetsBefore = allMissionObjects "Land_HelipadEmpty_F";', scenario)
        self.assertIn('!(_x in _vlsTargetsBefore) && {_x distance2D _vlsTarget < 2}', scenario)
        self.assertIn('&& {(count _vlsOwnedTargets) isEqualTo 1}', scenario)
        self.assertIn('&& {(_vlsOwnedTargets # 0) isEqualTo _vlsProductTarget}', scenario)
        self.assertIn('waitUntil {uiSleep 0.1; isNull _vlsProductTarget', scenario)
        self.assertIn('["vigil.artillery.vls.targetCleanup", _vlsTargetCleanupOk', scenario)
        product_source = (Path(__file__).parents[1] / "mods/visual-support-tablet/addons/VIGIL/functions/task_artillery/fn_artillery_task.sqf").read_text(encoding="utf-8")
        self.assertIn('private _target = createVehicle ["Land_HelipadEmpty_F", _position', product_source)
        self.assertIn('[_target] spawn {params ["_t"]; sleep 100; deleteVehicle _t;};', product_source)

    def test_evidence_contract_covers_every_feature_assertion_once(self) -> None:
        root = Path(__file__).parents[1]
        scenario = discover([
            root / "mods" / "visual-support-tablet" / "tests" / "tribunal"
        ])["vigil-artillery"]
        contract = scenario.evidence_contract
        self.assertEqual(contract["scenario"]["id"], scenario.identifier)
        self.assertEqual(contract["scenario"]["version"], 1)
        flattened = [
            assertion
            for arm in contract["arms"]
            for assertion in arm["assertions"]
        ]
        expected = set(scenario.server_expected) | set(scenario.client_expected)
        self.assertEqual(set(flattened), expected)
        self.assertEqual(len(flattened), len(set(flattened)))
        self.assertEqual(len(flattened), 24)
        proposition_assertions = {
            assertion
            for proposition in contract["propositions"]
            for assertion in proposition["assertions"]
        }
        self.assertEqual(proposition_assertions, expected)
        required = {"scenario", "knowledge_subject", "arms", "causal_relationships", "propositions"}
        self.assertTrue(required <= set(contract))
        arm_keys = {arm["key"] for arm in contract["arms"]}
        self.assertEqual(len(arm_keys), len(contract["arms"]))
        for relationship in contract["causal_relationships"]:
            self.assertIn(relationship["source"], arm_keys)
            self.assertIn(relationship["target"], arm_keys)
        self.assertTrue(contract["causal_relationships"])
        self.assertTrue(contract["knowledge_subject"]["biki_context"])
        vls_arm = next(arm for arm in contract["arms"] if arm["key"] == "vls-success")
        self.assertEqual(
            vls_arm["assertions"][-1],
            "vigil.artillery.vls.targetCleanup",
        )


if __name__ == "__main__":
    unittest.main()

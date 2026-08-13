"""Contracts for generic artillery observation and spatial evidence."""

from __future__ import annotations

import unittest
from pathlib import Path

from tribunal.mission.artillery import artillery_observer_sqf, spatial_evidence


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
        scenario = (Path(__file__).parents[1] / "source/visual-support-tablet/tests/tribunal/vigil_artillery.py").read_text(encoding="utf-8")
        self.assertIn('missionNamespace setVariable ["TRIBUNAL_VIGIL_ARTILLERY_COMPLETE", _token, true]', scenario)
        self.assertIn('(missionNamespace getVariable ["TRIBUNAL_VIGIL_ARTILLERY_COMPLETE", ""]) isEqualTo _token', scenario)


if __name__ == "__main__":
    unittest.main()

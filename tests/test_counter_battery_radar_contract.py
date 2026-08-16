"""Focused regression contracts for the reviewed Counter Battery Radar boundary."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from tribunal.discovery import discover  # noqa: E402
from tribunal.mission.markers import marker_observer_sqf  # noqa: E402
import pontifex_multiplayer as multiplayer  # noqa: E402


class CounterBatteryRadarContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.scenario = discover([
            ROOT / "source" / "advanced-systems" / "tests" / "tribunal"
        ])["advsys-counter-battery-radar"]
        self.source = (
            ROOT / "source" / "advanced-systems" / "addons" / "AdvSys"
            / "functions" / "cbr" / "fn_cbr.sqf"
        ).read_text(encoding="utf-8")

    def test_impact_prediction_resolves_ground_not_sea_level(self) -> None:
        """The reviewed defect: integrating to ASL 0 overshoots every elevated target."""

        self.assertIn("YOSHI_CB_groundHeightAt", self.source)
        self.assertIn("getTerrainHeightASL", self.source)
        predict = self.source[self.source.index("YOSHI_predictFallTimeAndPos ="):]
        self.assertIn("(_position select 2) > _ground", predict)
        # The pre-review sea-level termination must not come back.
        self.assertNotIn("while {_position select 2 >= 0} do", self.source)
        # Fail-closed: the integration loop is bounded.
        self.assertIn("YOSHI_CB_PREDICT_MAX_TIME", predict)
        self.assertIn("_time < YOSHI_CB_PREDICT_MAX_TIME", predict)

    def test_detection_remains_owner_scoped_and_server_authoritative(self) -> None:
        self.assertIn('addMissionEventHandler ["ArtilleryShellFired"', self.source)
        self.assertIn("if (isNull _shell || {!local _shell}) exitWith {}", self.source)
        self.assertIn('remoteExecCall ["YOSHI_fnc_cbrReceiveTrackUpdate", 2]', self.source)
        self.assertIn('remoteExecCall ["YOSHI_fnc_cbrHandleLocalArtilleryFire", 2]', self.source)
        for guarded in ("YOSHI_fnc_cbrReceiveTrackUpdate", "YOSHI_fnc_cbrStart", "YOSHI_fnc_cbrStop"):
            body = self.source[self.source.index(f"{guarded} ="):]
            self.assertIn("isServer", body[:200], guarded)

    def test_launch_warning_stays_side_filtered(self) -> None:
        warn = self.source[self.source.index("YOSHI_fnc_cbrWarnSidePlayers ="):]
        warn = warn[:warn.index("YOSHI_fnc_cbrReset =")]
        self.assertIn("if (_unitSide isEqualTo _artySide) then { continue; }", warn)
        self.assertIn("_unit distance2D _impactPos) > _radius", warn)
        self.assertIn("YAS_CBR_WarningLaunchDetected", warn)

    def test_permanent_scenario_is_causal_and_fail_closed(self) -> None:
        review = self.scenario.review
        self.assertEqual(review.outcome, "REFINE BEFORE PERMANENT COVERAGE")
        self.assertEqual(review.test_type, "specification")
        self.assertIn("map-marker", review.evidence_types)
        self.assertIn("negative-control", review.evidence_types)
        # Contract must promise behavior, not private layout.
        self.assertNotIn("YOSHI_", review.behavior_contract)

        server = self.scenario.server_sqf
        client = self.scenario.client_sqf
        # Prediction is proven against Tribunal's independent trajectory oracle.
        self.assertIn("TRIBUNAL_fnc_artilleryObserveSource", server)
        self.assertIn("TRIBUNAL_fnc_markerObserve", server)
        self.assertIn("_worstError < 20", server)
        self.assertIn("_targetHeight > 100", server)
        # Disabled control must precede enabling.
        self.assertLess(server.index("cbr.control.disabledNoDetection"), server.index("YOSHI_fnc_cbrStart"))
        # Marker properties are captured live, not read after cleanup.
        self.assertIn("_peakType = markerType", server)
        self.assertNotIn("{(markerType _peakIcon) isEqualTo", server)
        # Both warning controls are present on the client.
        self.assertIn("cbr.client.warningControls", client)
        self.assertIn("TRIBUNAL_CBR_ORIGINAL_RADIO", client)
        self.assertIn("YCD_fnc_playSideRadioLocal = TRIBUNAL_CBR_ORIGINAL_RADIO", client)
        for scope in (server, client):
            self.assertNotIn("while {true}", scope)

    def test_scenario_joins_gameplay_tier_and_shares_the_tier_player_spawn(self) -> None:
        gameplay = multiplayer.select_plan("gameplay")
        self.assertIn("advsys-counter-battery-radar", gameplay.selected)
        self.assertTrue(self.scenario.server_expected.issubset(gameplay.server_expected))
        self.assertTrue(self.scenario.client_expected.issubset(gameplay.client_expected))
        # A conflicting spawn would break every other gameplay scenario.
        self.assertNotIn("player_spawn", self.scenario.metadata)

    def test_marker_capability_is_generic(self) -> None:
        sqf = marker_observer_sqf()
        for name in (
            "TRIBUNAL_fnc_markerRecord",
            "TRIBUNAL_fnc_markerNames",
            "TRIBUNAL_fnc_markerCensus",
            "TRIBUNAL_fnc_markerCensusDiff",
            "TRIBUNAL_fnc_markerObserve",
            "TRIBUNAL_fnc_markerLifecycleEvidence",
        ):
            self.assertIn(name, sqf)
        lowered = sqf.casefold()
        for product in ("cbr", "yoshi", "yas_", "artillery", "battery"):
            self.assertNotIn(product, lowered)

    def test_live_command_guard_rejects_unpreprocessed_and_oversized_snippets(self) -> None:
        """`call compile` does not preprocess, and callExtension truncates silently."""

        self.assertLessEqual(multiplayer.LIVE_COMMAND_MAX_BYTES, 20 * 1024)
        with self.assertRaises(RuntimeError):
            multiplayer.write_live_command("server", 'diag_log "x"; // comment')
        with self.assertRaises(RuntimeError):
            multiplayer.write_live_command("server", 'diag_log "x"; /* comment */')
        with self.assertRaises(RuntimeError):
            multiplayer.write_live_command("server", "x" * (multiplayer.LIVE_COMMAND_MAX_BYTES + 1))


if __name__ == "__main__":
    unittest.main()

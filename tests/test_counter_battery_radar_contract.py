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
        self.assertEqual(review.outcome, "KEEP AS-IS AND SPEC-TEST")
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
        # Observation rows and client-local visual markers are captured live,
        # before normal expiry clears both.
        self.assertIn("_peakObservations = _current", server)
        self.assertIn("TRIBUNAL_CBR_REPLICATED_PEAK", client)
        self.assertIn("TRIBUNAL_fnc_markerObserve", client)
        self.assertIn("TRIBUNAL_CBR_ORIGINAL_RADIO", client)
        self.assertIn("YCD_fnc_playSideRadioLocal = TRIBUNAL_CBR_ORIGINAL_RADIO", client)
        for scope in (server, client):
            self.assertNotIn("while {true}", scope)

    def test_disabled_control_independently_proves_a_real_shot(self) -> None:
        """Without shot evidence the control passes even if the gun never fires."""

        server = self.scenario.server_sqf
        self.assertIn("cbr.control.disabledShotProven", self.scenario.server_expected)
        control = server[server.index("cbr-control"):server.index("cbr.control.disabledNoDetection")]
        # The shell must be seen to launch, fly, and terminate near the target.
        self.assertIn('_controlEvent getOrDefault ["artilleryEvent", false]', control)
        self.assertIn('_controlEvent getOrDefault ["terminated", false]', control)
        self.assertIn('(_controlLast distance2D _target) < 250', control)
        self.assertIn('(count (_controlEvent getOrDefault ["samples", []])) > 10', control)
        # Silence is only meaningful once the shot itself is proven.
        self.assertIn("private _disabledOk = _controlShotOk", server)

    def test_warning_travels_the_real_launch_pipeline(self) -> None:
        """Positive and both controls must be real launches, not helper calls."""

        server = self.scenario.server_sqf
        client = self.scenario.client_sqf
        # The scenario may wrap the warning helper to observe emissions, but must
        # never invoke it: a warning has to be produced by a real launch.
        self.assertNotIn("call YOSHI_fnc_cbrWarnSidePlayers", server)
        self.assertNotIn("YOSHI_fnc_cbrWarnSidePlayers", client)
        # The wrap must delegate to the saved original and be restored again.
        self.assertIn("_this call TRIBUNAL_CBR_WARN_ORIGINAL", server)
        self.assertIn("YOSHI_fnc_cbrWarnSidePlayers = TRIBUNAL_CBR_WARN_ORIGINAL", server)
        self.assertIn("cbr.warning.launchPipeline", self.scenario.server_expected)
        # Hostile and friendly launches, each proven to raise ArtilleryShellFired.
        self.assertIn('"O_Mortar_01_F" createVehicle _warnGunPos', server)
        self.assertIn('"B_Mortar_01_F" createVehicle _warnGunPos', server)
        self.assertIn('{_x getOrDefault ["artilleryEvent", false]} count _warnEvents', server)
        self.assertIn("(side (group (gunner _warnGun))) isEqualTo east", server)
        self.assertIn("(side (group (gunner _sameGun))) isEqualTo west", server)
        # A warning fires only on the first shell of a cycle, so each phase must
        # begin from a proven-idle tracker or the control is vacuous.
        self.assertIn("TRIBUNAL_CBR_fnc_waitIdle", server)
        # Transient emptiness between rounds of a still-firing salvo must not count.
        self.assertIn("_stableFor", server)
        self.assertIn("_stableSince = -1", server)
        # Fixture guns must be firing platforms, not combatants.
        self.assertIn("TRIBUNAL_CBR_fnc_firingPlatform", server)
        # Disabling TARGET/FSM stops an AI gunner accepting doArtilleryFire.
        self.assertNotIn('disableAI "AUTOTARGET"', server)
        self.assertNotIn('disableAI "FSM"', server)
        self.assertIn("{_farIdle} && {_warnIdle} && {_sameIdle}", server)
        # Emission and receipt are recorded separately so a failure localises.
        self.assertIn("TRIBUNAL_CBR_WARN_CALLS", server)
        self.assertIn("YOSHI_fnc_cbrWarnSidePlayers = TRIBUNAL_CBR_WARN_ORIGINAL", server)
        self.assertIn("(count _naming) isEqualTo 1", server)
        # Impact must be inside the warning radius but clear of the observer.
        self.assertIn("_warnDistance > 100", server)
        self.assertIn("_warnDistance < 1000", server)
        # Once-per-cycle: several shells, exactly one warning.
        self.assertIn("_warnShells = 3", server)
        self.assertIn("(count _afterWarn) isEqualTo 1", client)
        self.assertIn("_warnShells > 1", client)
        self.assertIn("(count _afterFar) isEqualTo 0", client)
        self.assertIn("(count _afterSame) isEqualTo (count _afterWarn)", client)

    def test_observations_are_durable_and_presentation_is_derived(self) -> None:
        source = self.source
        self.assertIn("YOSHI_CB_observations = []", source)
        self.assertIn('["ellipse", [YOSHI_CB_UNCERTAINTY_RADIUS, YOSHI_CB_UNCERTAINTY_RADIUS], 0]', source)
        self.assertIn("_observation set [4, _observedAt]", source)
        self.assertIn("_observation set [7, +_provenance]", source)
        self.assertIn('missionNamespace setVariable ["YOSHI_CBR_OBSERVATIONS"', source)
        self.assertNotIn("YOSHI_CB_LINK_DIST", source)
        self.assertNotIn("YOSHI_CB_clusters", source)
        self.assertNotIn("YOSHI_CB_MAX", source)

        client = self.scenario.client_sqf
        self.assertIn("TRIBUNAL_CBR_ZONE_RECORD", client)
        self.assertIn("TRIBUNAL_CBR_REPLICATED_PEAK", client)
        self.assertIn('(_x # 2) isEqualTo ["ellipse", [100,100], 0]', client)
        self.assertIn("YOSHI_CB_visualClusters", client)
        self.assertIn("_zoomInCount > _zoomOutCount", client)
        self.assertIn("_zoomOutCount isEqualTo 1", client)
        self.assertIn("_halfLength > (3 * _radius)", client)
        self.assertIn("YOSHI_CB_renderMarkers", client)
        self.assertIn("TRIBUNAL_CBR_ORIGIN_SEEN", client)
        self.assertIn('(_originSeen findIf {(_x find "YOSHI_origin") isEqualTo 0}) >= 0', client)

    def test_icon_label_is_checked_against_an_independent_physical_oracle(self) -> None:
        """Comparing the label with the fields that drew it only proves self-consistency."""

        server = self.scenario.server_sqf
        client = self.scenario.client_sqf
        # The stored count and remaining time come from observed projectiles.
        self.assertIn("_peakAt = diag_tickTime", server)
        self.assertIn('_firedAt = _x getOrDefault ["firedAt", -1]', server)
        self.assertIn('_endedAt = _x getOrDefault ["terminatedAt", -1]', server)
        self.assertIn("_remaining pushBack (_endedAt - _peakAt)", server)
        self.assertIn("_peakMembers >= (count _strictLive)", server)
        self.assertIn("_peakMembers <= (count _looseLive)", server)
        # Asymmetric: a stale/rounded label may run ahead of truth, not behind.
        self.assertIn("_minDelta <= _etaOverTolerance", server)
        self.assertIn("_minDelta >= -_etaUnderTolerance", server)
        self.assertIn("_maxDelta <= _etaOverTolerance", server)
        self.assertIn("_maxDelta >= -_etaUnderTolerance", server)
        self.assertIn("_countOk", server)
        self.assertIn("_etaOk", server)
        # The superseded one-sided total-flight check must not come back.
        self.assertNotIn("_peakEtaMax <= (_maximumFlight + 2)", server)
        # Tolerance is explicit and justified in-place, not an unexplained number.
        self.assertIn("_etaOverTolerance = 4", server)
        self.assertIn("_etaUnderTolerance = 1.5", server)
        self.assertIn("deliberately asymmetric", server)
        # Shell identity is the observer's event index: netId is "0:0" for shells.
        self.assertIn('_identity = [_x getOrDefault ["index", -1]', server)
        self.assertIn("liveDetail=%13", server)
        # The label itself must replicate to the client.
        self.assertIn("_countPrefix = format [\"%1 shells | ETA \", _expectedCount]", client)
        self.assertIn("_labelSeen", client)

    def test_scenario_is_client_identity_keyed_and_cleans_up(self) -> None:
        self.assertEqual(set(self.scenario.client_expected_by_identity), {"client-a"})
        self.assertEqual(set(self.scenario.client_sqf_by_identity), {"client-a"})
        self.assertEqual(self.scenario.expected_for("client-b"), frozenset())
        server = self.scenario.server_sqf
        # The observer is a declared identity, not whichever player sorts first.
        self.assertNotIn("allPlayers select {isPlayer _x}", server)
        self.assertIn("TRIBUNAL_CBR_OBSERVER_client-a", server)
        self.assertIn("cbr.cleanup", self.scenario.server_expected)
        self.assertIn("deleteVehicleCrew _x; deleteVehicle _x", server)
        self.assertIn('scriptDone (missionNamespace getVariable ["YOSHI_CBR_ORIGIN_THREAD", scriptNull])', server)

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

    def test_comment_guard_does_not_reject_string_literals(self) -> None:
        """A URL or a quoted /* is data, not a comment, and must survive the guard."""

        strip = multiplayer.strip_sqf_string_literals
        for literal in (
            'diag_log "https://example.invalid/path";',
            'diag_log "literal /* text */";',
            "diag_log 'http://example.invalid';",
            'diag_log "a""b//c";',
        ):
            stripped = strip(literal)
            self.assertNotIn("//", stripped, literal)
            self.assertNotIn("/*", stripped, literal)
        for commented in ('diag_log "x"; // c', '/* c */ diag_log "x";'):
            stripped = strip(commented)
            self.assertTrue("//" in stripped or "/*" in stripped, commented)
        # Blanking preserves offsets so reported positions stay meaningful.
        self.assertEqual(len(strip('diag_log "a""b";')), len('diag_log "a""b";'))

    def test_size_guard_measures_the_delivered_payload_not_the_source(self) -> None:
        """Client relay wrapping plus quote doubling can double a compliant source."""

        source = 'diag_log "' + ("a" * 4000) + '";' + ('"' * 9000) + ("x" * 4000)
        self.assertLess(len(source.encode()), multiplayer.LIVE_COMMAND_MAX_BYTES)
        delivered = multiplayer.build_live_payload("client", source, "0" * 32)
        self.assertGreater(len(delivered.encode()), multiplayer.LIVE_COMMAND_MAX_BYTES)
        # The same source is fine on the server endpoint, which has no relay.
        self.assertLess(
            len(multiplayer.build_live_payload("server", source, "0" * 32).encode()),
            multiplayer.LIVE_COMMAND_MAX_BYTES,
        )


if __name__ == "__main__":
    unittest.main()

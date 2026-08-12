"""Contracts for the scalable in-mission test framework."""

from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_multiplayer as multiplayer  # noqa: E402
from tribunal.assertions.protocol import parse_protocol  # noqa: E402


class TierFrameworkTests(unittest.TestCase):
    def test_integration_selection_composes_only_requested_checks(self) -> None:
        plan = multiplayer.select_plan("integration", "config,round-trip")
        self.assertNotIn("integration.missionNamespace", plan.server_expected)
        self.assertIn("integration.config", plan.server_expected)
        self.assertIn("integration.roundTrip", plan.server_expected)
        self.assertIn("integration.hasInterface", plan.client_expected)

        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "Tier.Stratis"
            multiplayer.write_tier_mission(mission, "integration-test-deadbeef", plan)
            server = (mission / "initServer.sqf").read_text(encoding="ascii")
            client = (mission / "initPlayerLocal.sqf").read_text(encoding="ascii")
        self.assertNotIn("integration.missionNamespace", server)
        self.assertIn("integration.config", server)
        self.assertIn("integration.roundTrip", server)
        self.assertIn("integration.roundTrip", client)

    def test_gameplay_plan_uses_authoritative_observable_vehicle_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "Tier.Stratis"
            multiplayer.write_tier_mission(mission, "gameplay-test-deadbeef", multiplayer.GAMEPLAY_PLAN)
            server = (mission / "initServer.sqf").read_text(encoding="ascii")
            client = (mission / "initPlayerLocal.sqf").read_text(encoding="ascii")
        self.assertIn("PONTIFEX_TIER_vehicleNetId", server)
        self.assertIn("gameplay.driverAuthoritative", server)
        self.assertIn("getPlayerUID (driver _vehicle)", server)
        self.assertIn("remoteExecutedOwner", server)
        self.assertIn("allPlayers select { owner _x isEqualTo _actionOwner }", server)
        self.assertIn("objectFromNetId _vehicleId", client)
        self.assertIn("gameplay.enterVehicle", client)

    def test_aps_gameplay_fixture_requires_causal_interception_evidence(self) -> None:
        plan = multiplayer.select_plan("gameplay", "aps-intercept")
        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "Tier.Stratis"
            multiplayer.write_tier_mission(mission, "gameplay-test-deadbeef", plan)
            server = (mission / "initServer.sqf").read_text(encoding="ascii")
            client = (mission / "initPlayerLocal.sqf").read_text(encoding="ascii")
        for assertion in ("aps.positive.projectileSpawned", "aps.positive.collisionCourse", "aps.positive.engaged", "aps.positive.neutralized", "aps.positive.chargeConsumed", "aps.positive.protected", "aps.control.disabledImpact", "aps.control.disabledNoEngagement", "aps.control.outsideEnvelope", "aps.control.directionAway", "aps.softkill.deflection"):
            self.assertIn(assertion, server)
        self.assertIn('TRIBUNAL_fnc_directProjectileLaunch', server)
        self.assertIn('TRIBUNAL_PROJECTILE|%1|LAUNCH', server)
        self.assertIn('createVehicle [_class, ASLToATL _requestedPosition, [], 0, "CAN_COLLIDE"]', server)
        self.assertIn('["R_PG32V_F", _origin, _direction, 250', server)
        self.assertNotIn('{direct_fixture_sqf()}', server)
        self.assertNotIn('private _projectile = "R_PG32V_F" createVehicle', server)
        self.assertIn('[_softVehicle, "softkill", 0, 0, false, 8, 0] call _injectThreat', server)
        self.assertIn('PONTIFEX_APS_FIXTURE|softkill|SAMEFRAME', server)
        self.assertIn('PONTIFEX_APS_FIXTURE|softkill|NEXTFRAME', server)
        self.assertIn('[_projectile] call YOSHI_fnc_apsTrackProjectileLocal', server)
        self.assertIn("TRIBUNAL_PROJECTILE|%1|LAUNCH", server)
        self.assertIn("TRIBUNAL_PROJECTILE|%1|SAMPLE", server)
        self.assertNotIn('"B_static_AT_F" createVehicle', server)
        self.assertIn("aps.replication", client)

    def test_terminal_lifecycle_outcomes_short_circuit_only_complete_non_live_runs(self) -> None:
        passed = {"status": "PASS", "assertions": 1, "failures": 0}
        failed = {"status": "FAIL", "assertions": 1, "failures": 1}
        self.assertTrue(multiplayer.terminal_results_ready(passed, passed, manual=False, live=False))
        self.assertTrue(multiplayer.terminal_results_ready(failed, passed, manual=False, live=False))
        self.assertFalse(multiplayer.terminal_results_ready(passed, None, manual=False, live=False))
        self.assertFalse(multiplayer.terminal_results_ready(None, None, manual=False, live=False))
        self.assertFalse(multiplayer.terminal_results_ready(passed, passed, manual=True, live=False))
        self.assertFalse(multiplayer.terminal_results_ready(passed, passed, manual=False, live=True))
        self.assertTrue(multiplayer.terminal_results_ready(passed, passed, manual=False, live=True, server_text="PONTIFEX_LIVE|server|READY", client_text="PONTIFEX_LIVE|client-a|READY"))

    def test_protocol_parser_reads_terminal_assertions_and_completion(self) -> None:
        records, complete = parse_protocol(
            "\n".join((
                "PONTIFEX_TIER|PASS|server|aps.positive.engaged|projectile=2:145",
                "PONTIFEX_TIER|FAIL|server|aps.softkill.deflection|fuel=1:1",
                "PONTIFEX_TIER|COMPLETE|server|status=FAIL|assertions=2|failures=1",
            )),
            prefix="PONTIFEX_TIER",
        )
        self.assertEqual([record["name"] for record in records], ["aps.positive.engaged", "aps.softkill.deflection"])
        self.assertEqual(records[0]["detail"], "projectile=2:145")
        self.assertEqual(complete, {"origin": "server", "status": "FAIL", "assertions": 2, "failures": 1})

    def test_live_command_is_scoped_and_atomically_replaces_the_inbox(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            control = Path(temporary) / "live-control"
            control.mkdir()
            state = {"live": True, "live_control": str(control), "run_id": "test"}
            with patch.object(multiplayer, "live_state", return_value=state):
                target = multiplayer.write_live_command("server", 'diag_log "hello";')
            self.assertEqual(target, control / "server.sqf")
            payload = target.read_text(encoding="utf-8")
            self.assertIn("PONTIFEX_LIVE|server|COMMAND", payload)
            self.assertIn('diag_log "hello";', payload)
            records = [json.loads(line) for line in (control / "commands.jsonl").read_text().splitlines()]
            self.assertEqual(records[0]["endpoint"], "server")

    def test_live_command_rejects_empty_or_oversized_source(self) -> None:
        with self.assertRaises(RuntimeError):
            multiplayer.write_live_command("server", "")
        with self.assertRaises(RuntimeError):
            multiplayer.write_live_command("server", "x" * (32 * 1024 + 1))

    def test_live_mission_uses_a_distinct_extension_request_per_poll(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "Live.Stratis"
            multiplayer.write_tier_mission(mission, "live-test-deadbeef", multiplayer.LIVE_PLAN, live=True)
            server = (mission / "initServer.sqf").read_text(encoding="ascii")
        self.assertIn('format ["next-%1", _poll]', server)
        self.assertIn('diag_log "PONTIFEX_LIVE|server|POLLER_REGISTERED";\n while {true} do {', server)
        self.assertIn('sleep 0.5;', server)
        self.assertIn('PONTIFEX_LIVE|server|POLL', server)
        self.assertIn('PONTIFEX_LIVE|server|POLLER_REGISTERED', server)


if __name__ == "__main__":
    unittest.main()

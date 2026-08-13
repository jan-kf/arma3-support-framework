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

    def test_vigil_transport_requires_physical_round_trip_and_rejects_duplicate(self) -> None:
        plan = multiplayer.select_plan("gameplay", "vigil-transport")
        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "Tier.Stratis"
            multiplayer.write_tier_mission(mission, "transport-test-deadbeef", plan)
            server = (mission / "initServer.sqf").read_text(encoding="ascii")
            client = (mission / "initPlayerLocal.sqf").read_text(encoding="ascii")
        self.assertIn("TRIBUNAL_fnc_aviationSample", server)
        self.assertIn("TRIBUNAL_fnc_observeFlight", server)
        self.assertIn('"duplicate_rejected"', server)
        self.assertIn("vigil.transport.dispatch.flight", server)
        self.assertIn("vigil.transport.arrival", server)
        self.assertIn("vigil.transport.rtb.flight", server)
        self.assertIn("vigil.transport.home", server)
        self.assertIn("isTouchingGround _aircraft", server)
        self.assertIn("call YOSHI_taskTRN_submit", client)
        self.assertIn("call YOSHI_taskTRN_rtb", client)
        self.assertIn("!isNull effectiveCommander _aircraft", client)

    def test_vigil_transport_product_refinements_are_fail_closed(self) -> None:
        root = ROOT / "source" / "visual-support-tablet" / "addons" / "VIGIL"
        core = (root / "functions" / "global" / "fn_core.sqf").read_text(encoding="utf-8")
        request = (root / "functions" / "task_transport" / "fn_transport.sqf").read_text(encoding="utf-8")
        task = (root / "functions" / "task_transport" / "fn_transport_task.sqf").read_text(encoding="utf-8")
        self.assertIn("side (group _commander)", core)
        self.assertIn("YOSHI_taskTRN_rtb", request)
        self.assertIn("_ignoreEn, true, \"dispatch\"", request)
        self.assertIn("YSF_TRX_TASK_TIMEOUT", task)
        self.assertIn("YSF_TRX_SETTLE_SECONDS", task)
        self.assertIn("setPosATL _newPadLoc", task)
        self.assertNotIn("setPosASL _newPadLoc", task)
        self.assertIn('"duplicate_rejected"', task)
        self.assertIn('["waiting", "home"] select', task)

    def test_vigil_cas_is_scoped_fail_closed_and_uses_real_rtb(self) -> None:
        root = ROOT / "source" / "visual-support-tablet" / "addons" / "VIGIL"
        request = (root / "functions" / "task_cas" / "fn_cas.sqf").read_text(encoding="utf-8")
        task = (root / "functions" / "task_cas" / "fn_cas_task.sqf").read_text(encoding="utf-8")
        engage = (root / "functions" / "task_cas" / "fn_airAutoEngage.sqf").read_text(encoding="utf-8")
        self.assertIn("YSF_taskCASAssignRemote", request)
        self.assertIn('"duplicate_rejected"', request)
        self.assertIn("YSF_CAS_TASK_TIMEOUT", task)
        self.assertIn("YSF_CAS_hasLethalAmmo", task)
        self.assertIn('getPosATL _v', task)
        self.assertNotIn('getPosASL _v', task)
        self.assertIn('YSF_transport_homeATL", _home', task)
        self.assertIn('[_v] call YOSHI_rebootAI;', task)
        self.assertIn('[_destPos, 20, true, false, false, "rtb", "YSF_cas_state"]', task)
        self.assertIn('[_v, _dest, "MOVE", 2]', task)
        self.assertIn('[_v, _dest, "LOITER", 2]', task)
        self.assertLess(task.index('[_v, _dest, "MOVE", 2]'), task.index('[_v, _dest, "LOITER", 2]'))
        self.assertNotIn('[_v, _dest, "SAD"', task)
        self.assertIn('_group setCombatMode "BLUE"', task)
        self.assertIn('_group setBehaviourStrong "AWARE"', task)
        self.assertIn('YSF_cas_state", "on_station"', task)
        self.assertIn('YSF_cas_state", "returning"', task)
        self.assertIn('YSF_cas_active", false', task)
        self.assertIn('YSF_cas_active", false]) exitWith {false}', engage)
        self.assertIn("YSF_AAE_effectiveSide", engage)
        self.assertIn("YSF_cas_areaATL", engage)
        self.assertIn('!(_obj isKindOf "Air")', engage)
        self.assertIn("YSF_CAS_EngagementEvents", engage)
        self.assertIn("YSF_AAE_getDirectGunOptions", engage)
        self.assertIn("YSF_AAE_weaponModeMaxRange", engage)
        self.assertIn('getNumber (_modeCfg >> "maxRange")', engage)
        self.assertIn('_maxRange max ([_weapon] call YSF_AAE_weaponModeMaxRange)', engage)
        self.assertIn('if ("shotbullet" in _simulation)', engage)
        self.assertIn('missionNamespace getVariable ["YSF_AAE_FIRE_COOLDOWN", 8]', engage)
        self.assertIn('"shotbullet" in _simulation', engage)
        self.assertIn('_guns + _missiles', engage)
        self.assertIn('YSF_AAE_pendingWeapon', engage)
        self.assertIn('_unit removeEventHandler ["Fired", _thisEventHandler]', engage)

    def test_vigil_cas_scenario_requires_correlated_combat_and_controls(self) -> None:
        plan = multiplayer.select_plan("gameplay", "vigil-cas")
        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "Tier.Stratis"
            multiplayer.write_tier_mission(mission, "cas-test-deadbeef", plan)
            server = (mission / "initServer.sqf").read_text(encoding="ascii")
            client = (mission / "initPlayerLocal.sqf").read_text(encoding="ascii")
        for assertion in (
            "vigil.cas.dispatch.accepted",
            "vigil.cas.dispatch.duplicateRejected",
            "vigil.cas.transit",
            "vigil.cas.onStation",
            "vigil.cas.target.controls",
            "vigil.cas.attack.fired",
            "vigil.cas.attack.correlated",
            "vigil.cas.attack.effect",
            "vigil.cas.timer",
            "vigil.cas.disengaged",
            "vigil.cas.rtb",
            "vigil.cas.home",
            "vigil.cas.noTarget",
            "vigil.cas.noAmmo",
            "vigil.cas.cleanup",
        ):
            self.assertIn(assertion, server)
        self.assertIn("TRIBUNAL_fnc_observeFlight", server)
        self.assertIn("TRIBUNAL_fnc_combatObserveSource", server)
        self.assertIn("TRIBUNAL_fnc_combatObserveTarget", server)
        self.assertIn('"O_MBT_02_cannon_F" createVehicle _area', server)
        self.assertIn('"ACE_gatling_20mm_Comanche"', server)
        self.assertIn("YSF_CAS_EngagementEvents", server)
        self.assertIn("call YOSHI_taskCAS_submit", client)

    def test_vigil_fixed_wing_preserves_state_and_does_not_rewrite_native_laser_bombs(self) -> None:
        root = ROOT / "source" / "visual-support-tablet" / "addons" / "VIGIL"
        source = (root / "functions" / "task_fixedWing" / "fn_initFixedWingFunctions.sqf").read_text(encoding="utf-8")
        self.assertIn("_newVehicle setFuel", source)
        self.assertIn("_vehicle setAmmoOnPylon", source)
        self.assertIn("YSF_FW_RTB_TIMEOUT", source)
        self.assertIn('[_id, _vehicle, "timeout"] call YSF_fwFinalizeRtb', source)
        self.assertNotIn('_row set [1, "PylonRack_Bomb_GBU12_x2"]', source)
        self.assertIn('_row set [1, "PylonRack_4Rnd_LG_scalpel"]', source)

    def test_vigil_fixed_wing_scenario_is_causal_repeated_and_cleans_up(self) -> None:
        plan = multiplayer.select_plan("gameplay", "vigil-fixed-wing")
        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "Tier.Stratis"
            multiplayer.write_tier_mission(mission, "fixed-wing-test-deadbeef", plan)
            server = (mission / "initServer.sqf").read_text(encoding="ascii")
            client = (mission / "initPlayerLocal.sqf").read_text(encoding="ascii")
            mission_sqm = (mission / "mission.sqm").read_text(encoding="ascii")
            description = (mission / "description.ext").read_text(encoding="ascii")
        for assertion in (
            "vigil.fixedWing.registration.snapshot",
            "vigil.fixedWing.registration.originalRemoved",
            "vigil.fixedWing.dispatch.reconstructed",
            "vigil.fixedWing.dispatch.ingress",
            "vigil.fixedWing.designation.normal",
            "vigil.fixedWing.strike.normal.release",
            "vigil.fixedWing.strike.normal.guidance",
            "vigil.fixedWing.strike.normal.effect",
            "vigil.fixedWing.designation.ir",
            "vigil.fixedWing.strike.ir.release",
            "vigil.fixedWing.strike.ir.guidance",
            "vigil.fixedWing.strike.ir.effect",
            "vigil.fixedWing.strike.repeated",
            "vigil.fixedWing.control.noDesignation",
            "vigil.fixedWing.egress.flight",
            "vigil.fixedWing.egress.cleanup",
        ):
            self.assertIn(assertion, server)
        self.assertIn("TRIBUNAL_fnc_designationRecord", server)
        self.assertIn("TRIBUNAL_fnc_combatObserveSource", server)
        self.assertIn("TRIBUNAL_fnc_observeFlight", server)
        self.assertIn('"PylonMissile_1Rnd_Bomb_04_F"', server)
        self.assertIn('"Bomb_04_F"', server)
        self.assertIn("TRIBUNAL_FIXED_WING|HANDHELD_ARMED", client)
        self.assertIn("TRIBUNAL_FIXED_WING|IR_ARMED", client)
        self.assertIn('call YOSHI_taskFW_deploy', client)
        self.assertIn('call YOSHI_taskFW_rtb', client)
        self.assertIn("position[]={ 2000.0,5.0,5600.0 }", mission_sqm)
        self.assertIn("respawnOnStart = 0", description)
        self.assertTrue({
            name for name in plan.server_expected if name.startswith("vigil.fixedWing.")
        }.issuperset({
            "vigil.fixedWing.registration.snapshot",
            "vigil.fixedWing.strike.normal.effect",
            "vigil.fixedWing.strike.ir.effect",
            "vigil.fixedWing.egress.cleanup",
        }))

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

        records, complete = parse_protocol(
            "PONTIFEX_TIER|PASS|client-b|replication.visible|ok\n"
            "PONTIFEX_TIER|COMPLETE|client-b|status=PASS|assertions=1|failures=0",
            prefix="PONTIFEX_TIER",
        )
        self.assertEqual(records[0]["origin"], "client-b")
        self.assertEqual(complete["origin"], "client-b")

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

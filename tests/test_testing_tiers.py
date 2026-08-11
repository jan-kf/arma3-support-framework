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
        self.assertIn("objectFromNetId _vehicleId", client)
        self.assertIn("gameplay.enterVehicle", client)

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


if __name__ == "__main__":
    unittest.main()

"""Regression coverage for launcher-to-join-adapter endpoint wiring."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_multiplayer as multiplayer  # noqa: E402


class JoinAdapterContractTests(unittest.TestCase):
    def test_runtime_endpoint_is_passed_without_manifest_lookup(self) -> None:
        captured: list[list[str]] = []

        def fake_docker(args: list[str], **_: object) -> subprocess.CompletedProcess:
            captured.append(args)
            return subprocess.CompletedProcess(args, 0, "", "")

        with patch.object(multiplayer, "docker", fake_docker):
            multiplayer.run_join_adapter(
                "pontifex-client-a-test",
                ROOT / "runs" / "test" / "client-a" / "join-adapter.json",
                server_ip="172.31.99.2",
                server_port=2322,
            )

        self.assertEqual(
            captured,
            [[
                "exec", "pontifex-client-a-test", "/opt/pontifex/vnc-join-adapter.py",
                "--output", "/run/pontifex/join-adapter.json",
                "--join", "172.31.99.2", "2322",
            ]],
        )

    def test_e2e_playable_group_has_required_empty_attributes_block(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "PfxE2E.Stratis"
            multiplayer.write_e2e_mission(mission, "e2e-regression-token-deadbeef")
            sqm = (mission / "mission.sqm").read_text(encoding="ascii")

        self.assertIn('class Attributes { isPlayer=1; }; id=1;', sqm)
        self.assertIn('class Attributes {}; id=0;', sqm)

    def test_e2e_action_protocol_uses_netid_and_strict_boolean_assertions(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            mission = Path(temporary) / "PfxE2E.Stratis"
            multiplayer.write_e2e_mission(mission, "e2e-regression-token-deadbeef")
            server = (mission / "initServer.sqf").read_text(encoding="ascii")
            client = (mission / "initPlayerLocal.sqf").read_text(encoding="ascii")

        self.assertIn('PONTIFEX_E2E_vehicleNetId", netId _vehicle, true', server)
        self.assertIn('_condition isEqualTo true', server)
        self.assertIn('private _status = "FAIL";', server)
        self.assertIn('if (_passed) then { _status = "PASS"; }', server)
        self.assertNotIn('select _passed', server)
        self.assertIn('["e2e.token", _tokenMatches, _tokenDetail]', server)
        self.assertIn('objectFromNetId _vehicleId', client)
        self.assertIn('e2e.vehicleResolved', client)
        self.assertIn('private _tokenMatches = _token isEqualTo _expectedToken;', server)
        self.assertIn('private _tokenDetail = format ["actual=%1|expected=%2"', server)
        self.assertTrue(server.startswith('[] spawn {\n private _token ='))
        self.assertTrue(client.startswith('[] spawn {\n private _token ='))
        self.assertIn('PONTIFEX_E2E_serverResults', server)
        self.assertIn('PONTIFEX_E2E_clientResults', client)
        self.assertIn('private _driverDeadline = diag_tickTime + 30;', server)
        self.assertIn('_player moveInDriver _vehicle;', server)



if __name__ == "__main__":
    unittest.main()

"""Regression checks for the dedicated Steam runtime boundary."""

from __future__ import annotations

import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_server as dedicated  # noqa: E402


class SteamRuntimeContractTests(unittest.TestCase):
    def test_distribution_and_runtime_app_ids_are_distinct(self) -> None:
        self.assertEqual(dedicated.INSTALLER_STEAM_APP_ID, "233780")
        self.assertEqual(dedicated.RUNTIME_STEAM_APP_ID, "107410")

    def test_runtime_ca_bundle_has_a_fixed_private_staging_path(self) -> None:
        self.assertEqual(
            dedicated.CA_CERTIFICATE_BUNDLE,
            dedicated.RUNTIME / "ca-certificates.crt",
        )

    def test_steam_readiness_survives_console_log_rotation(self) -> None:
        script = (ROOT / "client" / "container" / "run-test.sh").read_text(encoding="utf-8")
        self.assertIn('steam_ready_marker="$log_dir/.steam-ready-started"', script)
        self.assertIn(': >"$steam_ready_marker"', script)
        self.assertIn('[[ "$steam_console_log" -nt "$steam_ready_marker" ]]', script)
        self.assertIn("grep -Fq 'Waiting for compat in post-logon took:' \"$steam_console_log\"", script)
        self.assertNotIn("steam_console_offset", script)


if __name__ == "__main__":
    unittest.main()

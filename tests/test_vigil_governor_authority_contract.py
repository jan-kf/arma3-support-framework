"""Static contract for Vigil's declarative governor request boundary."""

from pathlib import Path
import unittest

from tribunal.discovery import discover


ROOT = Path(__file__).resolve().parents[1]
VIGIL = ROOT / "mods" / "visual-support-tablet" / "addons" / "VIGIL"


class VigilGovernorAuthorityContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.governor = (VIGIL / "functions" / "governor" / "fn_governor.sqf").read_text(encoding="utf-8")
        self.request_server = (VIGIL / "functions" / "governor" / "fn_taskRequestServer.sqf").read_text(encoding="utf-8")
        self.request_result = (VIGIL / "functions" / "governor" / "fn_taskRequestResult.sqf").read_text(encoding="utf-8")

    def test_all_live_ui_paths_submit_declarative_payloads(self) -> None:
        sources = {
            "artillery": VIGIL / "functions" / "task_artillery" / "fn_arty.sqf",
            "transport": VIGIL / "functions" / "task_transport" / "fn_transport.sqf",
            "cas": VIGIL / "functions" / "task_cas" / "fn_cas.sqf",
        }
        for task_type, path in sources.items():
            text = path.read_text(encoding="utf-8")
            self.assertIn(f'"{task_type}"', text)
            self.assertIn("call YSF_taskRequestRemote", text)
        combined = "\n".join(path.read_text(encoding="utf-8") for path in sources.values())
        self.assertNotIn("call YSF_taskNew", combined)
        self.assertIn("clientOwner", self.governor)

    def test_server_authenticates_requester_and_asset(self) -> None:
        for fragment in (
            "remoteExecutedOwner",
            "isPlayer _requester",
            "owner _requester isNotEqualTo _requestOwner",
            "forEach allPlayers",
            "_requesterClaim isNotEqualTo _requestOwner",
            'localNamespace getVariable ["YSF_task_authority_token"',
            '"wrong_side"',
            '"asset_not_whitelisted"',
            '"invalid_requester"',
        ):
            self.assertIn(fragment, self.governor)

    def test_server_owns_handlers_and_schema(self) -> None:
        for fragment in (
            "YSF_taskRequestBuild",
            "YSF_taskKey = {",
            "call YSF_handlers_artillery",
            "call YSF_handlers_transport",
            "call YSF_handlers_cas",
            '["serverBuilt", true]',
            '["requestId", _requestId]',
            '["requestOwner", _requestOwner]',
            'typeName _assigned isNotEqualTo "HASHMAP"',
        ):
            self.assertIn(fragment, self.governor)

    def test_legacy_remote_task_maps_fail_closed(self) -> None:
        legacy = self.governor[self.governor.index("YSF_taskAssignRemote = {"):self.governor.index("YSF_taskRequestReply = {")]
        self.assertIn("!isServer", legacy)
        self.assertIn("remoteExecutedOwner > 2", legacy)
        self.assertNotIn("YCD_fnc_runOnServerOnce", legacy)
        self.assertIn('remoteExecutedOwner > 2', self.governor[self.governor.index("YSF_taskAssign = {"):])

    def test_receipts_cover_accept_reject_and_terminal(self) -> None:
        for fragment in (
            '"rejected", "accepted"',
            '"duplicate"',
            '"asset_busy"',
            '"malformed_payload"',
            '"unsupported_task_type"',
            '"terminal"',
            "YSF_fnc_taskRequestResult",
        ):
            self.assertIn(fragment, self.governor)
        self.assertIn("remoteExecutedOwner", self.request_server)
        self.assertIn("YSF_task_authority_token", self.request_server)
        self.assertIn("remoteExecutedOwner > 2", self.request_result)

    def test_permanent_scenario_has_complete_evidence_contract(self) -> None:
        scenario = discover(
            [ROOT / "mods" / "visual-support-tablet" / "tests" / "tribunal"]
        )["vigil-governor-authority"]
        self.assertEqual(scenario.tier, "gameplay")
        self.assertEqual(len(scenario.server_expected), 9)
        self.assertEqual(len(scenario.client_expected), 2)
        self.assertIsNotNone(scenario.evidence_contract)
        self.assertEqual(len(scenario.evidence_contract["propositions"]), 2)
        covered = {
            assertion
            for proposition in scenario.evidence_contract["propositions"]
            for assertion in proposition["assertions"]
        }
        self.assertEqual(covered, set(scenario.server_expected | scenario.client_expected))


if __name__ == "__main__":
    unittest.main()

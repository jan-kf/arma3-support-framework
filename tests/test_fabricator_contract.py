"""Contracts for the Field Utilities Fabricator product decisions.

These guard the four recorded product decisions and the module attribute that
gates the local virtual inventory. Runtime behavior is proven by the
`fieldutils-fabricator` gameplay scenario; these keep the source honest about
which machine is allowed to act.
"""

from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

ADDON = ROOT / "source" / "field-utilities" / "addons" / "FieldUtils"
SERVER = ADDON / "functions" / "server" / "fn_fabricatorServer.sqf"
ASSETS = ADDON / "functions" / "fabricator" / "fn_assets.sqf"
PACKING = ADDON / "functions" / "fabricator" / "fn_boxPacking.sqf"
ACTIONS = ADDON / "functions" / "fabricator" / "fn_fabricationActions.sqf"
SETTERS = ADDON / "functions" / "global" / "fn_initModuleLogicSetters.sqf"
CLONE = ADDON / "functions" / "global" / "fn_fabricator.sqf"
CONFIG = ADDON / "config.cpp"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="replace")


class FabricatorAuthorityTests(unittest.TestCase):
    def test_the_order_terminal_never_creates_a_fabricated_object(self) -> None:
        """The client asks; only the server builds."""

        body = read(ASSETS)[read(ASSETS).index("YFU_assetsSubmitOrder = {"):]
        self.assertNotIn("YOSHI_SPAWN_SAVED_ITEM_ACTION", body)
        self.assertNotIn("YOSHI_spawnContainersNearObjectsAndPackMulti", body)
        self.assertNotIn("createVehicle", body)
        self.assertNotIn("deleteVehicle", body)
        self.assertIn('remoteExecCall ["YFU_fnc_fabricateOrder", 2]', body)

    def test_exactly_one_endpoint_is_reachable_by_a_client(self) -> None:
        """Every other consequential helper refuses a remote caller."""

        server = read(SERVER)
        # The secret is generated per machine and never published, so a client
        # compiling the same file cannot produce a matching value.
        self.assertIn('YFU_FABRICATOR_TOKEN = format ["yfu-%1-%2-%3"', server)
        self.assertNotIn('publicVariable "YFU_FABRICATOR_TOKEN"', server)
        guarded = (
            "YFU_fnc_fabricateOrderWorker", "YFU_fnc_fabricatorTrack", "YFU_fnc_fabricatorFinalize",
            "YFU_fnc_fabricatorPublishResult", "YFU_fnc_fabricatorRefuse", "YFU_fnc_fabricatorSetState",
            "YFU_fnc_fabricatorRetire",
        )
        for function in guarded:
            body = server[server.index(f"{function} = {{"):]
            self.assertIn("if (_token isNotEqualTo YFU_FABRICATOR_TOKEN) exitWith", body[:400], function)
        # The trusted airdrop entry point may use remoteExecutedOwner: it is
        # evaluated in the remote-executed frame, where it is meaningful.
        authorized = server[server.index("YFU_fnc_fabricateAuthorizedOrder = {"):]
        self.assertIn("if (remoteExecutedOwner isNotEqualTo 0) exitWith {};", authorized[:400])

    def test_caller_identity_comes_from_the_transport_not_the_payload(self) -> None:
        server = read(SERVER)
        self.assertIn("private _owner = remoteExecutedOwner;", server)
        self.assertIn("if ((owner _x) isEqualTo _owner) exitWith {_caller = _x};", server)
        self.assertNotIn("_callerId", server)

    def test_transaction_state_is_owner_bound_everywhere(self) -> None:
        """Two owners with the same client-generated id cannot collide."""

        server = read(SERVER)
        self.assertIn('format ["%1#%2", _owner, _requestId]', server)
        self.assertIn('format ["YFU_ORDER_RESULT_%1", _txId]', server)
        # Claim, result, ledger, finalize and retire are all keyed by the same id.
        for function in ("YFU_fnc_fabricatorTrack", "YFU_fnc_fabricatorFinalize", "YFU_fnc_fabricatorRetire"):
            body = server[server.index(f"{function} = {{"):]
            self.assertIn("_txId", body[:400], function)
        # The terminal waits on the owner-bound key.
        self.assertIn('format ["YFU_ORDER_RESULT_%1#%2", clientOwner, _requestId]', read(ASSETS))

    def test_a_discard_only_reaches_the_callers_own_transaction(self) -> None:
        server = read(SERVER)
        body = server[server.index("YFU_fnc_fabricatorDiscardOrder = {"):]
        self.assertIn("private _owner = remoteExecutedOwner;", body)
        self.assertIn("[_owner, _requestId] call YFU_fnc_fabricatorTxId;", body)

    def test_a_claim_precedes_scheduling_and_a_duplicate_cannot_overwrite(self) -> None:
        server = read(SERVER)
        accept = server[server.index("YFU_fnc_fabricatorAccept = {"):]
        claim = accept.index('_tx set ["claimed", true];')
        schedule = accept.index("spawn YFU_fnc_fabricateOrderWorker;")
        self.assertLess(claim, schedule)
        self.assertIn('exitWith {\n\t\t// The original transaction keeps its result', accept)
        # A terminal result is written once.
        publish = server[server.index("YFU_fnc_fabricatorPublishResult = {"):]
        self.assertIn('if (_state in ["delivered", "refused", "finalized"]) exitWith {_state};', publish)

    def test_the_schema_is_validated_before_claim_scheduling_or_creation(self) -> None:
        server = read(SERVER)
        accept = server[server.index("YFU_fnc_fabricatorAccept = {"):]
        validate = accept.index("call YFU_fnc_fabricatorValidateRequest;")
        claim = accept.index('_tx set ["claimed", true];')
        self.assertLess(validate, claim)
        for reason in ("malformed-request-id", "malformed-station", "malformed-mode",
                       "malformed-entries", "malformed-quantity", "too-large"):
            self.assertIn(f'"{reason}"', server, reason)

    def test_airdrop_mode_is_not_a_client_choice(self) -> None:
        """A client naming an arbitrary Air object authorizes nothing."""

        server = read(SERVER)
        self.assertIn('_stationVerdict = "airdrop-unauthorized";', server)
        self.assertIn("call YFU_fnc_fabricatorAirAssetAuthorized", server)
        # Authorization is Vigil's server-side registry, not the payload.
        auth = server[server.index("YFU_fnc_fabricatorAirAssetAuthorized = {"):]
        self.assertIn("call YSF_fwEnsureRegistry", auth)
        self.assertIn('getOrDefault ["spawnedVeh", objNull]', auth)

    def test_a_finalizer_covers_failures_the_code_does_not_anticipate(self) -> None:
        server = read(SERVER)
        # Objects are tracked as they are created, not only at known failures.
        worker = server[server.index("YFU_fnc_fabricateOrderWorker = {"):]
        self.assertIn("[YFU_FABRICATOR_TOKEN, _txId, [_clone]] call YFU_fnc_fabricatorTrack;", worker)
        # A watchdog finalizes a transaction that never reaches a terminal state.
        self.assertIn('_txId, "abandoned"] call YFU_fnc_fabricatorRefuse;', server)
        # The finalizer can only reach ids the transaction itself recorded.
        finalize = server[server.index("YFU_fnc_fabricatorFinalize = {"):]
        self.assertIn('_tx getOrDefault ["created", []]', finalize)
        self.assertIn("objectFromNetId _x", finalize)

    def test_delivery_placement_is_bounded_but_not_yet_suitability_checked(self) -> None:
        """Bounded to the recipient; terrain suitability is not claimed."""

        assets = read(ASSETS)
        self.assertIn("(vectorMagnitude _offset) <= (_radiusMax + 5)", assets)
        self.assertIn("It is NOT a suitability", assets)


class FabricatorProductDecisionTests(unittest.TestCase):
    def test_orders_are_atomic(self) -> None:
        """A short order produces nothing, and nothing is left staged."""

        server = read(SERVER)
        # Every refusal goes through one path that finalizes before it publishes.
        for reason in ("clone-failed", "unpackable", "caller", "no-storage",
                       "unregistered", "abandoned"):
            self.assertIn(f'_txId, "{reason}"] call YFU_fnc_fabricatorRefuse;', server, reason)
        # Station verdicts (no-station / out-of-range / airdrop-unauthorized)
        # travel through one variable to the same refusal path.
        self.assertIn("[YFU_FABRICATOR_TOKEN, _txId, _stationVerdict] call YFU_fnc_fabricatorRefuse;", server)
        refuse = server[server.index("YFU_fnc_fabricatorRefuse = {"):]
        self.assertIn("call YFU_fnc_fabricatorFinalize;", refuse[:400])

    def test_the_packer_reports_what_it_could_not_fit(self) -> None:
        packing = read(PACKING)
        self.assertIn("[(count _skipped) isEqualTo 0, _containers, _allocOut, _skipped]", packing)
        self.assertNotIn("\t[true, _containers, _allocOut]", packing)

    def test_the_catalogue_is_a_template_source_and_is_never_consumed(self) -> None:
        """Nothing in the order path mutates or removes a registered source."""

        server = read(SERVER)
        catalogue_block = server[server.index("YFU_fnc_fabricatorCatalogue = {"):server.index("YFU_fnc_fabricatorStations = {")]
        self.assertIn("synchronizedObjects _storage", catalogue_block)
        # The only deletions in the server path target clones and containers.
        for match in re.finditer(r"deleteVehicle (\w+)", server):
            self.assertIn(match.group(1), {"_x", "_object"}, match.group(0))
        self.assertNotIn("synchronizeObjectsRemove", server)
        self.assertNotIn("clearWeaponCargoGlobal _source", server)

    def test_the_delivery_mass_cap_is_preserved_as_intended_behavior(self) -> None:
        """Fabricated crates stay carryable; this is usability, not fidelity.

        The rule is preserved and kept in one place, but it is NOT currently
        provable at runtime: a fabricated crate on the dedicated server reports a
        mass of ~1e-12 and never gains a real one, so `getMass > 200` never fires.
        The gameplay scenario therefore asserts nothing about mass rather than
        accepting a degenerate value as "capped". See the review.
        """

        clone = read(CLONE)
        self.assertIn('if ((getMass _object) > 200) then {', clone)
        self.assertIn("_object setMass 200;", clone)
        # A newly created object reports no mass for a while; reading it straight
        # away makes the cap a no-op instead of a rule.
        self.assertIn("(getMass _object) > 0 || {diag_tickTime > _deadline}", clone)
        # A staged clone has no initialised mass, so the rule has to be applied
        # again once the delivery is standing where the player will find it.
        server = read(SERVER)
        self.assertIn("[_single] call YOSHI_capDeliveryMass;", server)
        self.assertIn("forEach (_clones + _containers);", server)
        # Built on the surface and hidden, never inside terrain: an object created
        # in terrain never initialises a mass and never recovers one.
        self.assertIn("_clone hideObjectGlobal true;", server)
        self.assertNotIn("YFU_FABRICATOR_STAGE_DEPTH", server)


class FabricatorLocalInventoryTests(unittest.TestCase):
    def test_the_module_attribute_is_published_by_the_module_setter(self) -> None:
        setters = read(SETTERS)
        self.assertIn(
            'YOSHI_FABRICATOR_LOCAL_INVENTORY = _logic getVariable ["Fabricator_Module_EnableLocalArsenal", true];',
            setters,
        )
        self.assertIn('publicVariable "YOSHI_FABRICATOR_LOCAL_INVENTORY";', setters)

    def test_the_virtual_inventory_action_is_gated_by_that_attribute(self) -> None:
        """The escape hatch for unsynchronized stock is opt-out per mission."""

        actions = read(ACTIONS)
        block = actions[actions.index("YFU_initVirtualInventoryActions = {"):]
        self.assertIn('missionNamespace getVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", true]', block)
        self.assertIn("&& {_inventoryEnabled}", block)
        # It still opens ZEN's inventory editor, which is what lets an operator
        # add stock that was never synchronized to the catalogue.
        self.assertIn("zen_inventory_fnc_configure", block)

    def test_the_module_still_declares_the_attribute_the_code_now_reads(self) -> None:
        config = read(CONFIG)
        self.assertIn('property = "Fabricator_Module_EnableLocalArsenal";', config)
        self.assertIn('class fabricatorServer { preInit = 1; };', config)


class FabricatorScenarioTests(unittest.TestCase):
    def test_the_scenario_drives_the_real_terminal_submit_path(self) -> None:
        """Not the server function at the end of it."""

        import importlib.util

        path = ROOT / "source" / "field-utilities" / "tests" / "tribunal" / "fabricator.py"
        spec = importlib.util.spec_from_file_location("fabricator_scenario", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        client = module.CLIENT_SQF
        # Honest orders go through the terminal.
        honest = client[client.index("TRIBUNAL_FAB_fnc_order = {"):client.index("TRIBUNAL_FAB_fnc_rawSend = {")]
        self.assertIn("call YFU_assetsSubmitOrder;", honest)
        self.assertNotIn("remoteExecCall", honest)
        # Adversarial controls deliberately speak to the remote boundary, because
        # that is what an attacker does, and they never build anything locally.
        self.assertIn("TRIBUNAL_FAB_fnc_rawSend", client)
        self.assertNotIn("YOSHI_SPAWN_SAVED_ITEM_ACTION", client)
        self.assertNotIn("createVehicle", client)

    def test_the_scenario_proves_absence_mission_wide_not_near_the_player(self) -> None:
        import importlib.util

        path = ROOT / "source" / "field-utilities" / "tests" / "tribunal" / "fabricator.py"
        spec = importlib.util.spec_from_file_location("fabricator_scenario", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        server = module.TRIBUNAL_SCENARIO.server_sqf
        self.assertIn("allMissionObjects", server)
        self.assertIn("TRIBUNAL_FAB_fnc_census", server)
        # Each refusal compares a full before/after census, so a control cannot
        # pass by leaving an object somewhere the scenario never looked.
        for control in ("_unpackable", "_rogue", "_far", "_noStorage"):
            self.assertIn(f"{{({control} # 1) isEqualTo ({control} # 0)}}", server, control)


if __name__ == "__main__":
    unittest.main()

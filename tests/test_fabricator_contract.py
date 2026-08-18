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

        submit = read(ASSETS)
        start = submit.index("YFU_assetsSubmitOrder = {")
        body = submit[start:]
        self.assertNotIn("YOSHI_SPAWN_SAVED_ITEM_ACTION", body)
        self.assertNotIn("YOSHI_spawnContainersNearObjectsAndPackMulti", body)
        self.assertNotIn("createVehicle", body)
        # ...and it must not undo the server's work either.
        self.assertNotIn("deleteVehicle", body)
        self.assertIn('remoteExecCall ["YFU_fnc_fabricateOrder", 2]', body)
        # The client says what it wants built, never who is asking.
        self.assertNotIn("netId _caller, netId _fabricator", body)

    def test_the_server_order_path_refuses_to_run_anywhere_else(self) -> None:
        server = read(SERVER)
        for function in ("YFU_fnc_fabricateOrder", "YFU_fnc_fabricateOrderWorker", "YFU_fnc_fabricatorDiscardOrder"):
            body = server[server.index(f"{function} = {{"):]
            self.assertIn("if (!isServer) exitWith {};", body[:400], function)

    def test_an_order_is_assembled_in_a_scheduled_script(self) -> None:
        """remoteExecCall arrives unscheduled, where uiSleep is a no-op."""

        server = read(SERVER)
        self.assertIn("(_this + [_owner]) spawn YFU_fnc_fabricateOrderWorker;", server)

    def test_an_order_is_validated_against_the_registered_catalogue_and_station(self) -> None:
        server = read(SERVER)
        for reason in ("no-storage", "no-station", "out-of-range", "unregistered", "too-large", "caller"):
            self.assertIn(f'"{reason}"', server, reason)
        self.assertIn("YFU_FABRICATOR_ORDER_RANGE", server)
        self.assertIn("_source in _catalogue", server)

    def test_caller_identity_comes_from_the_transport_not_the_payload(self) -> None:
        server = read(SERVER)
        self.assertIn("private _owner = remoteExecutedOwner;", server)
        self.assertIn("(_this + [_owner]) spawn YFU_fnc_fabricateOrderWorker;", server)
        # The worker resolves the player from the owner id it was handed.
        self.assertIn("if ((owner _x) isEqualTo _owner) exitWith {_caller = _x};", server)
        self.assertNotIn("_callerId", server)

    def test_a_request_id_is_claimed_before_anything_is_built(self) -> None:
        server = read(SERVER)
        claim = server.index("_claims set [_claimKey, true];")
        build = server.index("call YOSHI_SPAWN_SAVED_ITEM_ACTION")
        self.assertLess(claim, build)
        self.assertIn('[_requestId, false, "replay"]', server)

    def test_the_airdrop_flag_alone_cannot_skip_validation(self) -> None:
        server = read(SERVER)
        self.assertIn('_stationVerdict = "not-an-air-asset";', server)
        self.assertIn('!(_station isKindOf "Air")', server)

    def test_order_entries_are_schema_checked_before_expansion(self) -> None:
        server = read(SERVER)
        for guard in ("(_x # 1) isEqualType 0", "(_x # 1) isEqualTo (floor (_x # 1))", "(_x # 0) isEqualType \"\""):
            self.assertIn(guard, server, guard)

    def test_a_result_and_its_ledger_entry_retire_together(self) -> None:
        server = read(SERVER)
        block = server[server.index("YFU_fnc_fabricatorPublishResult = {"):server.index("YFU_fnc_fabricatorCatalogue = {")]
        self.assertIn("_ledger deleteAt _requestId;", block)
        self.assertIn("missionNamespace setVariable [_key, nil, true];", block)

    def test_delivery_placement_is_bounded_but_not_yet_suitability_checked(self) -> None:
        """Bounded to the player; water/gradient/obstruction remain unverified."""

        assets = read(ASSETS)
        self.assertIn("(vectorMagnitude _offset) <= (_radiusMax + 5)", assets)
        self.assertIn("It is NOT a suitability", assets)

    def test_station_verdict_is_not_returned_from_inside_a_then_block(self) -> None:
        """`exitWith` in a `then` block exits the block, not the function."""

        server = read(SERVER)
        branch = server[server.index("private _stationVerdict"):server.index('if (_stationVerdict isNotEqualTo ""')]
        self.assertNotIn("exitWith", branch)
        self.assertIn('if (_stationVerdict isNotEqualTo "") exitWith {', server)


class FabricatorProductDecisionTests(unittest.TestCase):
    def test_orders_are_atomic(self) -> None:
        """A short order produces nothing, and nothing is left staged."""

        server = read(SERVER)
        self.assertIn('[_requestId, false, "clone-failed"]', server)
        self.assertIn('[_requestId, false, "unpackable"]', server)
        # Both refusal paths delete what was already built.
        for marker in ('"clone-failed"', '"unpackable"'):
            block = server[: server.index(marker)]
            self.assertIn("call _abort;", block.rsplit("exitWith", 1)[-1], marker)

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
        self.assertIn("call YFU_assetsSubmitOrder;", client)
        self.assertNotIn("YFU_fnc_fabricateOrder", client)
        self.assertNotIn("YOSHI_SPAWN_SAVED_ITEM_ACTION", client)

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

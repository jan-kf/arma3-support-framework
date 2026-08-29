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

ADDON = ROOT / "mods" / "field-utilities" / "addons" / "FieldUtils"
SERVER = ADDON / "functions" / "server" / "fn_fabricatorServer.sqf"
ASSETS = ADDON / "functions" / "fabricator" / "fn_assets.sqf"
PACKING = ADDON / "functions" / "fabricator" / "fn_boxPacking.sqf"
ACTIONS = ADDON / "functions" / "fabricator" / "fn_fabricationActions.sqf"
SETTERS = ADDON / "functions" / "global" / "fn_initModuleLogicSetters.sqf"
CLONE = ADDON / "functions" / "global" / "fn_fabricator.sqf"
CONFIG = ADDON / "config.cpp"
VIGIL_FW = ROOT / "mods" / "visual-support-tablet" / "addons" / "VIGIL" / "functions" / "task_fixedWing" / "fn_initFixedWingFunctions.sqf"
SCENARIO = ROOT / "mods" / "field-utilities" / "tests" / "tribunal" / "fabricator.py"


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

    def test_only_order_and_owner_bound_discard_are_client_operations(self) -> None:
        """Every internal consequential helper requires server capability."""

        server = read(SERVER)
        # The secret is generated per machine and never published, so a client
        # compiling the same file cannot produce a matching value.
        self.assertIn('YFU_FABRICATOR_TOKEN = format ["yfu-%1-%2-%3"', server)
        self.assertNotIn('publicVariable "YFU_FABRICATOR_TOKEN"', server)
        guarded = (
            "YFU_fnc_fabricateOrderWorker", "YFU_fnc_fabricatorTrack", "YFU_fnc_fabricatorFinalize",
            "YFU_fnc_fabricatorPublishResult", "YFU_fnc_fabricatorRefuse", "YFU_fnc_fabricatorSetState",
            "YFU_fnc_fabricatorRetire", "YFU_fnc_fabricatorAccept",
        )
        for function in guarded:
            body = server[server.index(f"{function} = {{"):]
            self.assertIn("if (_token isNotEqualTo YFU_FABRICATOR_TOKEN) exitWith", body[:400], function)
        self.assertNotIn("YFU_fnc_fabricateAuthorizedOrder", server)
        self.assertIn("[YFU_FABRICATOR_TOKEN, _this, _owner] call YFU_fnc_fabricatorAccept;", server)
        self.assertIn('YFU_fnc_fabricatorDiscardOrder = {', server)

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
        self.assertIn('"replay-rejected"', accept)
        self.assertIn('// The original transaction keeps its result', accept)
        # A terminal result is written once.
        publish = server[server.index("YFU_fnc_fabricatorPublishResult = {"):]
        self.assertIn('if (_state in ["delivered", "refused", "finalized"]) exitWith {_state};', publish)

    def test_registry_forge_stimulus_reaches_the_real_server_guard(self) -> None:
        scenario = read(SCENARIO)
        self.assertIn('["client-guessed-token", "tribunal-forged", []] call YSF_fwSetEntry;', scenario)
        self.assertIn("_registryAuditAfter - _registryAuditBefore", scenario)
        self.assertIn("_registryCensusAfter isEqualTo _registryCensusBefore", scenario)
        self.assertNotIn("TRIBUNAL_FAB_fnc_probeRegistryForge", scenario)
        self.assertNotIn("private _forgedEntry = createHashMapFromArray", scenario)

    def test_watchdog_fault_stimulus_stalls_without_uncaught_throw(self) -> None:
        scenario = read(SCENARIO)
        watchdog = scenario[scenario.index('// Stall after the creation callback'):]
        self.assertIn("uiSleep 30;", watchdog[:800])
        self.assertNotIn("throw format", watchdog[:800])

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
        # Authorization is Vigil's own current-state validator, not a Field
        # Utilities reinterpretation of registry fields.
        auth = server[server.index("YFU_fnc_fabricatorAirAssetAuthorized = {"):]
        self.assertIn("call YSF_fwValidateLogisticsAsset", auth)
        self.assertNotIn("call YSF_fwEnsureRegistry", auth[:800])
        vigil = read(VIGIL_FW)
        validator = vigil[vigil.index("YSF_fwValidateLogisticsAsset = {"):vigil.index("YSF_fwRequestLogistics = {")]
        for condition in ("aircraft_not_registered", "aircraft_not_on_station", "aircraft_not_logistics", "wrong_side", "duplicate_active_task"):
            self.assertIn(condition, validator)
        request = vigil[vigil.index("YSF_fwRequestLogistics = {"):]
        self.assertIn("call YSF_fwValidateLogisticsAsset", request[:3500])

    def test_vigil_registry_mutation_requires_an_unpublished_capability(self) -> None:
        vigil = read(VIGIL_FW)
        self.assertIn('YSF_FW_REGISTRY_TOKEN = format ["ysf-fw-%1-%2-%3"', vigil)
        self.assertNotIn('publicVariable "YSF_FW_REGISTRY_TOKEN"', vigil)
        for function in ("YSF_fwCommitPublicRegistry", "YSF_fwCommitRegistry", "YSF_fwSetEntry", "YSF_fwSetEntryPrivate"):
            body = vigil[vigil.index(f"{function} = {{"):]
            self.assertIn("if (_token isNotEqualTo YSF_FW_REGISTRY_TOKEN) exitWith", body[:500], function)
        self.assertIn('if (_id isEqualType "") then {_id} else {str _id}', vigil)

    def test_a_finalizer_covers_failures_the_code_does_not_anticipate(self) -> None:
        server = read(SERVER)
        # Objects are tracked by callbacks at the exact creation boundary, not
        # after a helper containing later fallible work returns.
        worker = server[server.index("YFU_fnc_fabricateOrderWorker = {"):]
        clone = read(CLONE)
        packing = read(PACKING)
        self.assertIn("[_newObject, _onCreatedArgs] call _onCreated;", clone)
        self.assertIn("[_container, _onContainerCreatedArgs] call _onContainerCreated;", packing)
        self.assertIn('params ["_created", "_txId"]', worker)
        self.assertIn("[_created]] call YFU_fnc_fabricatorTrack;", worker)
        # A watchdog finalizes a transaction that never reaches a terminal state.
        self.assertIn("private _worker = [YFU_FABRICATOR_TOKEN", server)
        self.assertIn('_tx set ["worker", _worker];', server)
        self.assertIn("terminate _worker;", server)
        self.assertIn('"watchdog", "worker-terminated"', server)
        self.assertIn('_txId, "abandoned"] call YFU_fnc_fabricatorRefuse;', server)
        # The finalizer can only reach ids the transaction itself recorded.
        finalize = server[server.index("YFU_fnc_fabricatorFinalize = {"):]
        self.assertIn('_tx getOrDefault ["created", []]', finalize)
        self.assertIn("objectFromNetId _x", finalize)

    def test_delivery_placement_is_bounded_and_fails_closed_over_water(self) -> None:
        """Nearby suitable land is required before a local result is published."""

        assets = read(ASSETS)
        server = read(SERVER)
        self.assertIn("(vectorMagnitude _offset) <= (_radiusMax + 5)", assets)
        self.assertIn("surfaceIsWater _candidate", assets)
        self.assertIn("private _fallbacks = [];", assets)
        self.assertIn("surfaceNormal _x", assets)
        self.assertEqual(server.count('_txId, "no-safe-drop"] call YFU_fnc_fabricatorRefuse;'), 2)
        self.assertLess(server.index("private _positions = [];"), server.index("_x setPosATL (_positions # _forEachIndex);"))


class FabricatorProductDecisionTests(unittest.TestCase):
    def test_orders_are_atomic(self) -> None:
        """A short order produces nothing, and nothing is left staged."""

        server = read(SERVER)
        # Every refusal goes through one path that finalizes before it publishes.
        for reason in ("clone-failed", "unpackable", "caller", "no-storage",
                       "unregistered", "abandoned", "no-safe-drop"):
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

        The rule is preserved and kept in one place. Authentic boundary coverage
        proves mass 200 before publication and exact ACE carry afterward. A cold
        repeat also proved that newly unhidden PhysX state can restore class mass
        after an initial cap, so single delivery now requires a bounded stable cap
        before publication and waits for that replication before ACE admission.
        """

        clone = read(CLONE)
        self.assertIn('if ((getMass _object) > 200) then {', clone)
        self.assertIn("[\"ace_common_setMass\", [_target, 200]] call CBA_fnc_globalEvent;", clone)
        # A newly created object reports no mass for a while; reading it straight
        # away makes the cap a no-op instead of a rule.
        self.assertIn("(getMass _object) > 0 || {diag_tickTime > _deadline}", clone)
        # A staged clone has no initialised mass, so the rule has to be applied
        # again once the delivery is standing where the player will find it.
        server = read(SERVER)
        self.assertIn("[_single, 10, 1] call YOSHI_capDeliveryMass;", server)
        self.assertIn("_stabilityWindow", clone)
        self.assertIn("[_object] call _applyCap;", clone)
        assets = read(ASSETS)
        self.assertIn("private _massDeadline = diag_tickTime + 5;", assets)
        self.assertIn("(_mass > 0 && {_mass <= 200})", assets)
        self.assertIn("ace_dragging_isCarrying", assets)
        self.assertIn("(attachedTo _single) isEqualTo _caller", assets)
        self.assertIn("forEach (_clones + _containers);", server)
        # Built on the surface and hidden, never inside terrain: an object created
        # in terrain never initialises a mass and never recovers one.
        self.assertIn("_clone hideObjectGlobal true;", server)
        self.assertNotIn("YFU_FABRICATOR_STAGE_DEPTH", server)


class FabricatorLocalInventoryTests(unittest.TestCase):
    def test_the_module_attribute_is_published_by_the_module_setter(self) -> None:
        setters = read(SETTERS)
        self.assertIn(
            '_logic getVariable ["Fabricator_Module_EnableLocalArsenal", true]',
            setters,
        )
        self.assertIn('_inventoryValues pushBackUnique (_row # 2)', setters)
        self.assertIn('(count _inventoryValues) isEqualTo 1', setters)
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
    def test_client_replication_wait_is_bounded_and_identity_preserving(self) -> None:
        import importlib.util

        path = ROOT / "mods" / "field-utilities" / "tests" / "tribunal" / "fabricator.py"
        spec = importlib.util.spec_from_file_location("fabricator_scenario_replication", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        client = module.TRIBUNAL_SCENARIO.client_sqf
        self.assertIn("private _deliveryDeadline = diag_tickTime + 15;", client)
        self.assertIn("(_clone distance player) < 12", client)
        self.assertNotIn("nearestObjects", client)

    def test_the_scenario_drives_the_real_terminal_submit_path(self) -> None:
        """Not the server function at the end of it."""

        import importlib.util

        path = ROOT / "mods" / "field-utilities" / "tests" / "tribunal" / "fabricator.py"
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

        path = ROOT / "mods" / "field-utilities" / "tests" / "tribunal" / "fabricator.py"
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

    def test_adversarial_controls_require_server_receipt_evidence(self) -> None:
        import importlib.util

        path = ROOT / "mods" / "field-utilities" / "tests" / "tribunal" / "fabricator.py"
        spec = importlib.util.spec_from_file_location("fabricator_scenario_receipts", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        server = module.TRIBUNAL_SCENARIO.server_sqf
        for marker in (
            '"worker", "token-rejected"',
            '"accept", "token-rejected"',
            '"order", "replay-rejected"',
            '"discard", "owner-miss-rejected"',
            '"set-entry", "token-rejected"',
            '"watchdog", "worker-terminated"',
        ):
            self.assertIn(marker, server)
        self.assertIn("TRIBUNAL_FAB_fnc_auditMatches", server)

    def test_watchdog_and_retirement_are_exercised_not_only_inspected(self) -> None:
        import importlib.util

        path = ROOT / "mods" / "field-utilities" / "tests" / "tribunal" / "fabricator.py"
        spec = importlib.util.spec_from_file_location("fabricator_scenario_lifecycle", path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        server = module.TRIBUNAL_SCENARIO.server_sqf
        self.assertIn("uiSleep 30;", server)
        self.assertNotIn('throw format ["tribunal-post-create-%1"', server)
        self.assertIn('isEqualTo "abandoned"', server)
        self.assertIn("_watchdogReceipt", server)
        self.assertIn('YFU_FABRICATOR_RESULT_TTL = 3;', server)
        self.assertIn('isEqualTo "unknown"', server)
        self.assertIn("_resultKeysGone", server)

    def test_water_boundary_uses_authentic_orders_and_distinct_causal_arms(self) -> None:
        scenario = read(SCENARIO)
        self.assertIn('"terrainShore"', scenario)
        self.assertIn('"terrainDeepWater"', scenario)
        self.assertIn('"fabricator.delivery.shoreline"', scenario)
        self.assertIn('"fabricator.control.deepWaterAtomic"', scenario)
        self.assertIn('"fabricator.delivery.severeGradientRecovery"', scenario)
        self.assertIn('"fabricator.control.severeGradientAtomic"', scenario)
        self.assertIn('"pontifex:fabricator:bounded-severe-gradient-placement"', scenario)
        self.assertIn('_refusalFloor > 20', scenario)
        self.assertIn('isEqualTo "no-safe-drop"', scenario)
        self.assertIn("_deepSamples findIf", scenario)
        self.assertIn('"id": "pontifex:fabricator:bounded-water-placement"', scenario)

    def test_multi_container_policy_and_atomic_control_are_retained(self) -> None:
        packing = read(PACKING)
        self.assertIn("if (_preferMultiple && {_maxSmallCountCap > 0})", packing)
        self.assertIn("_objectsInBin select [_offset, _cap]", packing)
        self.assertIn("_allocs = _boundedAllocs;", packing)

        server = read(SERVER)
        reserve_all = server.index("private _positions = [];")
        move_first = server.index("_x setPosATL (_positions # _forEachIndex);")
        self.assertLess(reserve_all, move_first)
        self.assertIn("if ((count _positions) isNotEqualTo (count _containers)) exitWith", server)
        self.assertIn("_created hideObjectGlobal true;", server)
        self.assertGreaterEqual(server.count("_x setPosATL (_positions # _forEachIndex);"), 2)
        self.assertIn("_x setVelocity [0, 0, 0];", server)
        self.assertIn("_single setVariable [\"ace_dragging_ignoreWeightCarry\", true, true];", server)

        scenario = read(SCENARIO)
        self.assertIn("multiContainerSuccess", scenario)
        self.assertIn("multiContainerRefusal", scenario)
        self.assertIn("fabricator.delivery.multiContainerPlacement", scenario)
        self.assertIn("fabricator.control.multiContainerAtomic", scenario)
        self.assertIn("pontifex:fabricator:multi-container-placement-atomicity", scenario)
        self.assertIn("(count _preRefusal) isEqualTo (8 + count _multiPlacementContainers)", scenario)
        self.assertIn("player playMoveNow \"AmovPercMstpSnonWnonDnon\"", scenario)
        self.assertIn("_busyEntry set [\"side\", _requesterSide]", scenario)
        self.assertIn("_multiPlacementStableSince", scenario)
        self.assertIn("for \"_index\" from 0 to ((count _multiPlacementContainers) - 1)", scenario)
        self.assertNotIn("_multiPlacementSpeeds # _forEachIndex", scenario)
        self.assertIn("(diag_tickTime - _multiPlacementStableSince) >= 2", scenario)
        self.assertIn("_ready getVariable [\"ace_dragging_ignoreWeightCarry\", false]", scenario)
        self.assertIn("TRIBUNAL_FAB_BASE_client-a", scenario)
        self.assertIn("_pos distance2D _declaredBase < 2", scenario)
        self.assertIn("private _fixture = [4700, 2780", scenario)

    def test_single_item_terrain_boundary_uses_authentic_matched_orders(self) -> None:
        scenario = read(SCENARIO)
        self.assertIn("singleTerrainShore", scenario)
        self.assertIn("singleTerrainDeepWater", scenario)
        self.assertIn("fabricator.delivery.singleTerrainBoundary", scenario)
        self.assertIn("fabricator.control.singleDeepWaterAtomic", scenario)
        self.assertIn("pontifex:fabricator:single-item-bounded-water-placement", scenario)
        self.assertIn("ace_dragging_fnc_dropObject_carry", scenario)
        self.assertIn("private _entries = if (_singleItem)", scenario)
        self.assertIn("TRIBUNAL_FAB_SINGLE_ORIGINAL_SAFE_DROP", scenario)
        self.assertIn("(count _singleShorePreDecision) isEqualTo 1", scenario)
        self.assertIn("(count _singleDeepPreDecision) isEqualTo 1", scenario)
        self.assertIn("_singleDeep # 1) isEqualTo (_singleDeep # 0", scenario)

    def test_active_owner_discard_terminates_worker_before_rollback(self) -> None:
        server = read(SERVER)
        discard = server[server.index("YFU_fnc_fabricatorDiscardOrder = {"):]
        terminate_at = discard.index("terminate _worker;")
        finalize_at = discard.index("call YFU_fnc_fabricatorFinalize;")
        self.assertLess(terminate_at, finalize_at)
        self.assertIn('"discard", "worker-terminated"', discard)
        self.assertIn("call YFU_fnc_fabricatorRetire", discard)

        scenario = read(SCENARIO)
        self.assertIn('"fabricator.control.activeDiscardAtomic"', scenario)
        self.assertIn('"TRIBUNAL_FAB_CANCEL_CREATED"', scenario)
        self.assertIn('_activeDiscard # 1) isEqualTo (_activeDiscard # 0', scenario)


if __name__ == "__main__":
    unittest.main()

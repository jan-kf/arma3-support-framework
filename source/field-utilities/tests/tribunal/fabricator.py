"""Permanent Tier 3 contract for Field Utilities Fabricator and Virtual Storage."""

from tribunal.runner.model import Scenario, ScenarioReview


EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "pontifex.field-utilities.fabricator.transaction",
        "version": 5,
        "feature_family": "field-utilities/fabricator",
        "name": "Fabricator bounded terrain placement",
        "definition": {
            "kind": "dedicated-multiplayer product specification",
            "reference": "source/field-utilities/tests/tribunal/fabricator.py",
            "legacy_experiment_key": "tribunal:fieldutils-fabricator",
            "applicability": "Arma 3 2.22 dedicated multiplayer with CBA, ACE and Field Utilities; server-owned fabrication; one authenticated client; Stratis land, shoreline, deep-water and severe-gradient fixtures",
        },
    },
    "knowledge_subject": {
        "key": "pontifex:field-utilities:fabricator",
        "label": "Pontifex Fabricator",
        "kind": "pontifex.feature",
        "aliases": ["Fabricator"],
        "biki_context": ["arma:createvehicle", "biki-page:2091"],
    },
    "arms": [
        {
            "key": "fixture",
            "role": "baseline",
            "description": "One authenticated client and exact server-owned catalogue, station, source, transaction and census identities",
            "assertions": ["fabricator.fixture", "fabricator.authority.serverOwned"],
        },
        {
            "key": "accepted_land_matrix",
            "role": "positive_control",
            "description": "Authentic packed orders settle on the already accepted flat, moderate-gradient and dense-obstruction land fixtures",
            "assertions": ["fabricator.delivery.terrainMatrix"],
        },
        {
            "key": "shoreline_treatment",
            "role": "treatment",
            "description": "An authentic packed order from a water recipient adjacent to independently identified land selects a bounded non-water target and settles there",
            "assertions": ["fabricator.delivery.shoreline"],
        },
        {
            "key": "deep_water_control",
            "role": "negative_control",
            "description": "The same authentic packed order with every sampled point in the bounded neighborhood over water refuses atomically instead of publishing a water delivery",
            "assertions": ["fabricator.control.deepWaterAtomic"],
        },
        {
            "key": "severe_gradient_recovery_treatment",
            "role": "treatment",
            "description": "An authentic packed order from a severe-gradient recipient recovers to independently sampled moderate non-water terrain inside the bounded search and settles there",
            "assertions": ["fabricator.delivery.severeGradientRecovery"],
        },
        {
            "key": "severe_gradient_refusal_control",
            "role": "negative_control",
            "description": "The same authentic packed order in a severe-gradient neighborhood with no sampled moderate point refuses atomically before publication",
            "assertions": ["fabricator.control.severeGradientAtomic"],
        },
        {
            "key": "multi_container_success_treatment",
            "role": "treatment",
            "description": "An authentic eight-object order allocates multiple containers, reserves one distinct bounded target per container, and publishes the complete settled delivery",
            "assertions": ["fabricator.delivery.multiContainerPlacement"],
        },
        {
            "key": "multi_container_target_refusal_control",
            "role": "negative_control",
            "description": "The same authentic eight-object order with only its first distinct target available refuses every container before movement, visibility, or publication",
            "assertions": ["fabricator.control.multiContainerAtomic"],
        },
        {
            "key": "single_item_shoreline_treatment",
            "role": "treatment",
            "description": "An authentic single-item order from the accepted shoreline water recipient publishes the exact hidden clone at bounded moderate non-water land and client-a carries that identity",
            "assertions": ["fabricator.delivery.singleTerrainBoundary"],
        },
        {
            "key": "single_item_deep_water_control",
            "role": "negative_control",
            "description": "The same authentic single-item order in the accepted all-water neighborhood deletes its exact hidden clone and refuses without publication",
            "assertions": ["fabricator.control.singleDeepWaterAtomic"],
        },
        {
            "key": "closeout",
            "role": "treatment",
            "description": "All created objects, transaction records, result keys and fixtures close cleanly",
            "assertions": ["fabricator.cleanup"],
        },
    ],
    "causal_relationships": [
        {
            "key": "nearby-land-v-deep-water",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "shoreline_treatment",
            "target": "deep_water_control",
            "controlled_dimensions": ["same authenticated client", "same server authority", "same registered station and catalogue", "same two-object packed order", "same bounded placement helper", "nearby suitable land availability is the varied dimension"],
        },
        {
            "key": "moderate-slope-available-v-unavailable",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "severe_gradient_recovery_treatment",
            "target": "severe_gradient_refusal_control",
            "controlled_dimensions": ["same authenticated client", "same server authority", "same registered station and catalogue", "same two-object packed order", "same bounded placement helper", "moderate non-water terrain inside the bounded search is the varied dimension"],
        },
        {
            "key": "all-container-targets-v-first-only",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "multi_container_success_treatment",
            "target": "multi_container_target_refusal_control",
            "controlled_dimensions": ["same authenticated client", "same server authority", "same registered station and catalogue", "same eight-object terminal order", "same multi-container allocator", "same attempt-zero target", "availability of target attempts one and above is the varied dimension"],
        },
        {
            "key": "single-nearby-land-v-deep-water",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "single_item_shoreline_treatment",
            "target": "single_item_deep_water_control",
            "controlled_dimensions": ["same authenticated client", "same server authority", "same registered station and catalogue", "same one-object terminal order", "same bounded placement helper", "nearby suitable land availability is the varied dimension"],
        },
    ],
    "propositions": [
        {
            "id": "pontifex:fabricator:bounded-water-placement",
            "text": "Under the tested dedicated-server and one-client conditions, an authentic packed Fabricator order from a shoreline water recipient selects bounded moderate non-water land and settles there, while the same order in a bounded all-water neighborhood is refused atomically without publishing or leaking a delivery.",
            "intended_use": "primary_result",
            "assertions": ["fabricator.delivery.shoreline", "fabricator.control.deepWaterAtomic", "fabricator.cleanup"],
            "rationale": "Matched authentic order paths vary nearby suitable-land availability; exact result identities, surface sampling, physical settling, mission-wide census and cleanup distinguish success from an atomic refusal.",
        },
        {
            "id": "pontifex:fabricator:bounded-severe-gradient-placement",
            "text": "Under the tested dedicated-server and one-client conditions, an authentic packed Fabricator order from a severe-gradient recipient recovers to bounded moderate non-water terrain and settles when such terrain is available, while the same order in a sampled all-severe neighborhood is refused atomically without publishing or leaking a delivery.",
            "intended_use": "primary_result",
            "assertions": ["fabricator.delivery.severeGradientRecovery", "fabricator.control.severeGradientAtomic", "fabricator.cleanup"],
            "rationale": "Matched authentic order paths vary bounded moderate-slope availability; independent surface-normal samples, exact result identities, physical settling, mission-wide census and cleanup distinguish recovery from atomic refusal.",
        },
        {
            "id": "pontifex:fabricator:multi-container-placement-atomicity",
            "text": "Under the tested dedicated-server and one-client conditions, an authentic Fabricator order that allocates multiple containers publishes the complete delivery at distinct bounded targets when every target is available, while the same order with only the first target available is refused atomically before any container is moved, revealed, or published.",
            "intended_use": "primary_result",
            "assertions": ["fabricator.delivery.multiContainerPlacement", "fabricator.control.multiContainerAtomic", "fabricator.cleanup"],
            "rationale": "Matched authentic eight-object terminal orders vary only later target availability; exact attempt records, tracked pre-refusal object state, result identities, mission-wide census and cleanup distinguish complete publication from atomic refusal.",
        },
        {
            "id": "pontifex:fabricator:single-item-bounded-water-placement",
            "text": "Under the tested dedicated-server and one-client conditions, an authentic single-item Fabricator order from a shoreline water recipient publishes its exact hidden clone at bounded moderate non-water land and hands that identity to ACE carry, while the same order in a bounded all-water neighborhood is refused atomically without publication or leakage.",
            "intended_use": "primary_result",
            "assertions": ["fabricator.delivery.singleTerrainBoundary", "fabricator.control.singleDeepWaterAtomic", "fabricator.cleanup"],
            "rationale": "Matched authentic one-object terminal orders vary nearby suitable-land availability; pre-decision hidden-object snapshots, the exact publication and carry identity, terrain samples, mission-wide census and cleanup distinguish direct delivery from atomic refusal.",
        },
    ],
    "unresolved": [
        "Pond objects are detected by surfaceIsWater only when loaded and no deterministic pond fixture is present on Stratis; ponds remain unproven.",
        "Other islands, coastline shapes, terrain shapes outside the sampled severe-gradient matrix, suitable terrain farther than 15 m, multi-container orders beyond the tested allocator/order/target matrix, single-item terrain boundaries beyond the tested shoreline/all-water pair, client-B/JIP and ownership migration remain outside this proof.",
    ],
}


OBSERVER_IDENTITIES = ("client-a",)

CLIENT_EXPECTED = frozenset({
    "fabricator.client.modulesReplicated",
    "fabricator.client.inventoryGate",
    "fabricator.client.orderAccepted",
    "fabricator.client.noLocalCreation",
    "fabricator.client.deliveryReplicated",
    "fabricator.client.carryStarted",
    "fabricator.client.rejectionSurfaced",
})


CLIENT_SQF = r'''
// Wait for this client to actually believe it is where the server has put it.
// Sampled too early, the client still reports the map origin while the server
// reports the land spawn, and every distance measured here is wrong by kilometres.
private _selfDeadline = diag_tickTime + 180;
private _selfLast = [0, 0, 0];
private _selfSteady = 0;
waitUntil {
    uiSleep 0.25;
    private _pos = getPosATL player;
    private _placed = alive player && {(_pos # 0) > 100} && {(_pos # 1) > 100};
    if (_placed && {(_pos distance _selfLast) < 1}) then {
        if (_selfSteady isEqualTo 0) then {_selfSteady = diag_tickTime;};
    } else {
        _selfSteady = 0;
    };
    _selfLast = _pos;
    (_selfSteady > 0 && {(diag_tickTime - _selfSteady) > 3}) || {diag_tickTime > _selfDeadline}
};

// Anchor the accepted baseline to independently known interior Stratis land;
// the natural respawn varies along a narrow coastal strip and is not a stable
// land fixture for a fail-closed placement contract.
private _fixtureCenter = [4700, 2780, 0];
player setPosATL _fixtureCenter;
private _fixturePlacedDeadline = diag_tickTime + 20;
waitUntil {uiSleep 0.1; player distance2D _fixtureCenter < 2 || {diag_tickTime > _fixturePlacedDeadline}};

// Declare which unit this identity actually controls, rather than letting the
// server guess from allPlayers ordering. A second client must not silently
// change which player the fixture is built around.
missionNamespace setVariable ["TRIBUNAL_FAB_BASE_client-a", _fixtureCenter, true];
missionNamespace setVariable ["TRIBUNAL_FAB_PLAYER_client-a", netId player, true];

private _fixtureDeadline = diag_tickTime + 240;
private _fixture = [];
waitUntil {
    uiSleep 0.1;
    _fixture = missionNamespace getVariable ["TRIBUNAL_FAB_FIXTURE", []];
    !(_fixture isEqualTo []) || {diag_tickTime > _fixtureDeadline}
};
_fixture params [["_fixtureToken", ""], ["_stationId", ""], ["_stationFarId", ""], ["_heavyId", ""], ["_lightId", ""], ["_oversizeId", ""], ["_unregisteredId", ""], ["_rogueAirId", ""], ["_ineligibleAirId", ""], ["_busyAirId", ""]];
private _station = objectFromNetId _stationId;

// What the client can be shown to receive is the module handshake itself: both
// logics arrive by publicVariable, which is how the product discovers them.
//
// Two things are deliberately NOT claimed here. ACE 3.21 keeps object actions in
// neither an object variable nor the class-keyed ActNamespace the Bridge Builder
// scenario reads. And editor synchronization created at runtime does not
// replicate: `synchronizedObjects` returns the stations on the server and stays
// empty on the client, so per-station client registration cannot be proven with
// a runtime-built fixture. Both are recorded in the review.
private _logicDeadline = diag_tickTime + 180;
waitUntil {
    uiSleep 0.25;
    (!isNil "YOSHI_FABRICATOR" && {!isNil "YOSHI_VIRTUAL_STORAGE"}) || {diag_tickTime > _logicDeadline}
};
private _clientStations = if (isNil "YOSHI_FABRICATOR") then {[]} else {synchronizedObjects YOSHI_FABRICATOR};
private _registry = uiNamespace getVariable ["YFU_registered_fabricator_actions", []];
call YFU_registerFabricatorMenuActions;
uiSleep 0.5;
private _registryAfter = uiNamespace getVariable ["YFU_registered_fabricator_actions", []];
private _modulesOk = !isNil "YOSHI_FABRICATOR"
    && {!isNil "YOSHI_VIRTUAL_STORAGE"}
    && {!isNull YOSHI_FABRICATOR}
    && {!isNull YOSHI_VIRTUAL_STORAGE}
    && {!isNull _station}
    && {_registryAfter isEqualTo _registry}
    && {!isNil "ace_interact_menu_fnc_addActionToObject"};
["fabricator.client.modulesReplicated", _modulesOk, format ["fabricator=%1|storage=%2|syncVisibleHere=%3|registry=%4|idempotent=%5|aceApi=%6|aceVersion=%7", !isNull YOSHI_FABRICATOR, !isNull YOSHI_VIRTUAL_STORAGE, count _clientStations, _registryAfter, _registryAfter isEqualTo _registry, !isNil "ace_interact_menu_fnc_addActionToObject", getText (configFile >> "CfgPatches" >> "ace_interact_menu" >> "versionStr")]] call _assert;

// The Fabricator module's local-inventory attribute reaches this client with the
// value the module published.
private _gate = missionNamespace getVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", "unset"];
["fabricator.client.inventoryGate", (typeName _gate) isEqualTo "BOOL" && {_gate}, format ["gate=%1|type=%2", _gate, typeName _gate]] call _assert;

TRIBUNAL_FAB_fnc_order = {
    params ["_phase", "_stationObj", "_entries", "_timeout"];

    private _map = createHashMap;
    private _order = [];
    {
        private _obj = objectFromNetId (_x # 0);
        if (!isNull _obj) then {
            _map set [_x # 0, [_obj, _x # 1]];
            _order pushBack (_x # 0);
        };
    } forEach _entries;
    uiNamespace setVariable ["YFU_fabricator_queue_map", _map];
    uiNamespace setVariable ["YFU_fabricator_queue_order", _order];
    uiNamespace setVariable ["YFU_open_context", createHashMapFromArray [
        ["fabricator", _stationObj],
        ["isAirdrop", false],
        ["grid", "1234-5678"]
    ]];
    uiNamespace setVariable ["YFU_submit_in_progress", false];
    uiNamespace setVariable ["YFU_submit_success", false];
    uiNamespace setVariable ["YFU_last_order_result", []];

    missionNamespace setVariable ["TRIBUNAL_FAB_READY", _phase, true];
    private _goDeadline = diag_tickTime + 240;
    waitUntil {
        uiSleep 0.1;
        ((missionNamespace getVariable ["TRIBUNAL_FAB_GO", ""]) isEqualTo _phase) || {diag_tickTime > _goDeadline}
    };

    // The real terminal submit path, not a helper at the end of it.
    call YFU_assetsSubmitOrder;

    private _deadline = diag_tickTime + _timeout;
    waitUntil {
        uiSleep 0.1;
        !(uiNamespace getVariable ["YFU_submit_in_progress", false]) || {diag_tickTime > _deadline}
    };

    private _request = uiNamespace getVariable ["YFU_last_order_request", []];
    private _result = uiNamespace getVariable ["YFU_last_order_result", []];
    private _success = uiNamespace getVariable ["YFU_submit_success", false];
    private _report = [_request param [0, ""], _result, _success, clientOwner];
    missionNamespace setVariable ["TRIBUNAL_FAB_REPORT", _report, true];
    missionNamespace setVariable ["TRIBUNAL_FAB_DONE", _phase, true];
    _report
};

// Adversarial controls speak to the remote boundary directly, because that is
// what an attacker does: they do not go through the terminal. The honest orders
// above and below still use the real submit path.
TRIBUNAL_FAB_fnc_rawSend = {
    params ["_phase", "_function", "_payloads", "_requestId", "_timeout"];
    private _key = format ["YFU_ORDER_RESULT_%1#%2", clientOwner, _requestId];
    missionNamespace setVariable [_key, nil, false];

    missionNamespace setVariable ["TRIBUNAL_FAB_READY", _phase, true];
    private _goDeadline = diag_tickTime + 240;
    waitUntil {
        uiSleep 0.1;
        ((missionNamespace getVariable ["TRIBUNAL_FAB_GO", ""]) isEqualTo _phase) || {diag_tickTime > _goDeadline}
    };

    {_x remoteExecCall [_function, 2];} forEach _payloads;

    private _deadline = diag_tickTime + _timeout;
    waitUntil {
        uiSleep 0.1;
        !isNil {missionNamespace getVariable _key} || {diag_tickTime > _deadline}
    };
    // Give a refused-and-silent path its full budget before calling it silent.
    if (isNil {missionNamespace getVariable _key}) then {uiSleep 3;};
    private _result = missionNamespace getVariable [_key, []];
    missionNamespace setVariable ["TRIBUNAL_FAB_REPORT", [_requestId, _result, false, clientOwner], true];
    missionNamespace setVariable ["TRIBUNAL_FAB_DONE", _phase, true];
    _result
};

player setUnitPos "UP";
player playMoveNow "AmovPercMstpSnonWnonDnon";
private _standDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; stance player isEqualTo "STAND" || {diag_tickTime > _standDeadline}};
private _singleReport = ["single", _station, [[_heavyId, 1]], 60] call TRIBUNAL_FAB_fnc_order;
private _singleResult = _singleReport param [1, []];
private _clone = objectFromNetId (_singleResult param [3, ""]);
["fabricator.client.orderAccepted", (_singleReport param [2, false]) isEqualTo true && {(_singleResult param [2, ""]) isEqualTo "single"}, format ["report=%1", _singleReport]] call _assert;

// The terminal asked; it did not build. The delivered object is replicated here
// but owned by the server.
private _noLocalOk = !isNull _clone && {!(local _clone)} && {typeOf _clone isEqualTo "Box_NATO_Ammo_F"};
["fabricator.client.noLocalCreation", _noLocalOk, format ["clone=%1|localHere=%2|type=%3", netId _clone, local _clone, typeOf _clone]] call _assert;

// The result variable and object identity can replicate before the server's
// final setPosATL. Wait only for that exact object's state; never substitute a
// nearby object or relax the delivery bound.
private _deliveryDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    (!isNull _clone && {(_clone distance player) < 12}) || {diag_tickTime > _deliveryDeadline}
};
private _deliveryOk = !isNull _clone
    && {(_clone distance player) < 12}
    && {(getWeaponCargo _clone) isEqualTo [["arifle_MX_F"], [3]]}
    && {(getItemCargo _clone) isEqualTo [["FirstAidKit"], [5]]};
["fabricator.client.deliveryReplicated", _deliveryOk, format ["dist=%1|weapons=%2|items=%3", _clone distance player, getWeaponCargo _clone, getItemCargo _clone]] call _assert;

private _carryDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (attachedTo _clone) isEqualTo player || {diag_tickTime > _carryDeadline}};
private _carryOk = (attachedTo _clone) isEqualTo player;
["fabricator.client.carryStarted", _carryOk, format ["clone=%1|player=%2|attached=%3|mass=%4|commonOwner=%5|isCarrying=%6|canCarry=%7|dist=%8|stance=%9", netId _clone, netId player, netId (attachedTo _clone), getMass _clone, netId (_clone getVariable ["ace_common_owner", objNull]), player getVariable ["ace_dragging_isCarrying", false], _clone getVariable ["ace_dragging_canCarry", false], player distance _clone, stance player]] call _assert;

["multi", _station, [[_lightId, 2]], 90] call TRIBUNAL_FAB_fnc_order;
["multiContainerSuccess", _station, [[_lightId, 8]], 120] call TRIBUNAL_FAB_fnc_order;
["multiContainerRefusal", _station, [[_lightId, 8]], 120] call TRIBUNAL_FAB_fnc_order;

TRIBUNAL_FAB_fnc_terrainOrder = {
    params ["_phase", ["_singleItem", false]];
    private _setupDeadline = diag_tickTime + 240;
    private _setup = [];
    waitUntil {
        uiSleep 0.1;
        _setup = missionNamespace getVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", []];
        (_setup param [0, ""]) isEqualTo _phase
            || {diag_tickTime > _setupDeadline}
    };
    private _center = _setup param [1, []];
    private _carried = player getVariable ["ace_dragging_carriedObject", objNull];
    if (!isNull _carried) then {
        [player, _carried, false] call ace_dragging_fnc_dropObject_carry;
        private _dropDeadline = diag_tickTime + 5;
        waitUntil {uiSleep 0.05; !(player getVariable ["ace_dragging_isCarrying", false]) || {diag_tickTime > _dropDeadline}};
    };
    player enableSimulation false;
    player setVelocity [0, 0, 0];
    player setPosATL _center;
    private _placedDeadline = diag_tickTime + 20;
    waitUntil {uiSleep 0.1; (player distance2D _center) < 2 || {diag_tickTime > _placedDeadline}};
    missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_READY", _phase, true];
    private _entries = if (_singleItem) then {[[_heavyId, 1]]} else {[[_lightId, 2]]};
    [_phase, _station, _entries, 90] call TRIBUNAL_FAB_fnc_order
};

private _shoreProbeDeadline = diag_tickTime + 240;
private _shoreProbe = [];
waitUntil {
    uiSleep 0.1;
    _shoreProbe = missionNamespace getVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", []];
    (_shoreProbe param [0, ""]) isEqualTo "terrainShoreProbe"
        || {diag_tickTime > _shoreProbeDeadline}
};
private _shoreProbeCenter = _shoreProbe param [1, []];
player enableSimulation false;
player setVelocity [0, 0, 0];
player setPosATL _shoreProbeCenter;
private _shoreProbePlaced = diag_tickTime + 20;
waitUntil {uiSleep 0.1; player distance2D _shoreProbeCenter < 2 || {diag_tickTime > _shoreProbePlaced}};
missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_READY", "terrainShoreProbe", true];

{[_x] call TRIBUNAL_FAB_fnc_terrainOrder;} forEach [
    "terrainFlat",
    "terrainGradient",
    "terrainBlocked",
    "terrainShore",
    "terrainDeepWater"
];
["singleTerrainShore", true] call TRIBUNAL_FAB_fnc_terrainOrder;
["singleTerrainDeepWater", true] call TRIBUNAL_FAB_fnc_terrainOrder;

private _slopeProbeDeadline = diag_tickTime + 240;
private _slopeProbe = [];
waitUntil {
    uiSleep 0.1;
    _slopeProbe = missionNamespace getVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", []];
    (_slopeProbe param [0, ""]) isEqualTo "terrainSlopeProbe"
        || {diag_tickTime > _slopeProbeDeadline}
};
private _slopeProbeCenter = _slopeProbe param [1, []];
player setPosATL _slopeProbeCenter;
private _slopeProbePlaced = diag_tickTime + 20;
waitUntil {uiSleep 0.1; player distance2D _slopeProbeCenter < 2 || {diag_tickTime > _slopeProbePlaced}};
missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_READY", "terrainSlopeProbe", true];

{[_x] call TRIBUNAL_FAB_fnc_terrainOrder;} forEach [
    "terrainSevereRecovery",
    "terrainSevereRefusal"
];

private _restoreDeadline = diag_tickTime + 240;
private _restore = [];
waitUntil {
    uiSleep 0.1;
    _restore = missionNamespace getVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", []];
    (_restore param [0, ""]) isEqualTo "terrainRestore"
        || {diag_tickTime > _restoreDeadline}
};
private _restoreCenter = _restore param [1, []];
player setPosATL _restoreCenter;
private _restorePlaced = diag_tickTime + 20;
waitUntil {uiSleep 0.1; player distance2D _restoreCenter < 2 || {diag_tickTime > _restorePlaced}};
missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_READY", "terrainRestore", true];
player enableSimulation true;

private _unpackableReport = ["unpackable", _station, [[_oversizeId, 1], [_lightId, 1]], 90] call TRIBUNAL_FAB_fnc_order;
private _unpackableResult = _unpackableReport param [1, []];
private _rejectionOk = (_unpackableReport param [2, true]) isEqualTo false
    && {(_unpackableResult param [1, true]) isEqualTo false}
    && {(_unpackableResult param [2, ""]) isEqualTo "unpackable"};
["fabricator.client.rejectionSurfaced", _rejectionOk, format ["report=%1", _unpackableReport]] call _assert;

["unregistered", _station, [[_unregisteredId, 1], [_lightId, 1]], 60] call TRIBUNAL_FAB_fnc_order;
private _stationFar = objectFromNetId _stationFarId;
["outOfRange", _stationFar, [[_lightId, 1]], 60] call TRIBUNAL_FAB_fnc_order;
["noStorage", _station, [[_lightId, 1]], 60] call TRIBUNAL_FAB_fnc_order;

// 1. Reaching past the endpoint straight into the worker.
["bypass", "YFU_fnc_fabricateOrderWorker",
    [["client-guessed-token", "guessed#tribunal-bypass", _stationId, [[_heavyId, 1]], false, clientOwner]],
    "tribunal-bypass", 20] call TRIBUNAL_FAB_fnc_rawSend;

// 2. Reaching the internal accept function and supplying a forged owner.
["acceptBypass", "YFU_fnc_fabricatorAccept",
    [["client-guessed-token", ["tribunal-accept-bypass", _stationId, [[_heavyId, 1]], false], 2]],
    "tribunal-accept-bypass", 20] call TRIBUNAL_FAB_fnc_rawSend;

// 3. The same request id sent twice, back to back.
["duplicate", "YFU_fnc_fabricateOrder",
    [["tribunal-dup", _stationId, [[_heavyId, 1]], false], ["tribunal-dup", _stationId, [[_heavyId, 1]], false]],
    "tribunal-dup", 60] call TRIBUNAL_FAB_fnc_rawSend;

// 4. Airdrop mode selected by the client, naming an unregistered aircraft.
["rogueAirdrop", "YFU_fnc_fabricateOrder",
    [["tribunal-air", _rogueAirId, [[_heavyId, 1]], true]],
    "tribunal-air", 40] call TRIBUNAL_FAB_fnc_rawSend;

// A registered strike aircraft is still not a current logistics capability.
["ineligibleAirdrop", "YFU_fnc_fabricateOrder",
    [["tribunal-air-role", _ineligibleAirId, [[_heavyId, 1]], true]],
    "tribunal-air-role", 40] call TRIBUNAL_FAB_fnc_rawSend;

// A logistics aircraft with an active task cannot authorize a second one.
["busyAirdrop", "YFU_fnc_fabricateOrder",
    [["tribunal-air-busy", _busyAirId, [[_heavyId, 1]], true]],
    "tribunal-air-busy", 40] call TRIBUNAL_FAB_fnc_rawSend;

// Payloads that are simply not orders.
["malformed", "YFU_fnc_fabricateOrder",
    [["tribunal-bad", _stationId, [[_heavyId, "many"]], false]],
    "tribunal-bad", 40] call TRIBUNAL_FAB_fnc_rawSend;

["oversized", "YFU_fnc_fabricateOrder",
    [["tribunal-big", _stationId, [[_heavyId, 9999]], false]],
    "tribunal-big", 40] call TRIBUNAL_FAB_fnc_rawSend;

// 5. Discarding a transaction this client does not own.
["foreignDiscard", "YFU_fnc_fabricatorDiscardOrder",
    [["tribunal-server-order"]],
    "tribunal-discard", 25] call TRIBUNAL_FAB_fnc_rawSend;

// The server fixture stalls this order after its exact clone is tracked. The
// owner then cancels through the public discard endpoint. This is a separate
// race from the watchdog: cancellation must terminate the live worker before
// rollback, or it can resume and create/publish after cleanup.
missionNamespace setVariable ["TRIBUNAL_FAB_READY", "activeDiscard", true];
private _cancelGoDeadline = diag_tickTime + 240;
waitUntil {
    uiSleep 0.1;
    ((missionNamespace getVariable ["TRIBUNAL_FAB_GO", ""]) isEqualTo "activeDiscard") || {diag_tickTime > _cancelGoDeadline}
};
["tribunal-cancel", _stationId, [[_lightId, 1]], false] remoteExecCall ["YFU_fnc_fabricateOrder", 2];
private _cancelCreatedDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_FAB_CANCEL_CREATED", false]) || {diag_tickTime > _cancelCreatedDeadline}
};
["tribunal-cancel"] remoteExecCall ["YFU_fnc_fabricatorDiscardOrder", 2];
uiSleep 1;
missionNamespace setVariable ["TRIBUNAL_FAB_REPORT", ["tribunal-cancel", missionNamespace getVariable ["TRIBUNAL_FAB_CANCEL_CREATED", false]], true];
missionNamespace setVariable ["TRIBUNAL_FAB_DONE", "activeDiscard", true];

// The server fixture stalls after creation for this honest order; the watchdog
// must return an explicit refusal and remove the tracked clone.
["watchdog", _station, [[_lightId, 1]], 60] call TRIBUNAL_FAB_fnc_order;

// A short test-only TTL lets the server prove complete state retirement without
// making the proof wait for the production 120-second retention period.
["retirement", "YFU_fnc_fabricateOrder",
    [["tribunal-retire", _stationId, [[_heavyId, "invalid"]], false]],
    "tribunal-retire", 30] call TRIBUNAL_FAB_fnc_rawSend;

private _serverDeadline = diag_tickTime + 180;
waitUntil {
    uiSleep 0.1;
    !isNil {missionNamespace getVariable "TRIBUNAL_FAB_SERVER_DONE"} || {diag_tickTime > _serverDeadline}
};
'''


TRIBUNAL_SCENARIO = Scenario(
    identifier="fieldutils-fabricator",
    tier="gameplay",
    server_expected=frozenset({
        "fabricator.fixture",
        "fabricator.authority.serverOwned",
        "fabricator.delivery.massIsolation",
        "fabricator.fidelity.cargo",
        "fabricator.delivery.landPlacement",
        "fabricator.catalogue.notConsumed",
        "fabricator.delivery.packed",
        "fabricator.delivery.terrainMatrix",
        "fabricator.delivery.shoreline",
        "fabricator.control.deepWaterAtomic",
        "fabricator.delivery.severeGradientRecovery",
        "fabricator.control.severeGradientAtomic",
        "fabricator.delivery.multiContainerPlacement",
        "fabricator.control.multiContainerAtomic",
        "fabricator.delivery.singleTerrainBoundary",
        "fabricator.control.singleDeepWaterAtomic",
        "fabricator.control.unpackableAtomic",
        "fabricator.control.unregistered",
        "fabricator.control.outOfRange",
        "fabricator.control.noStorage",
        "fabricator.control.workerBypass",
        "fabricator.control.acceptBypass",
        "fabricator.control.duplicateRequest",
        "fabricator.control.airdropUnauthorized",
        "fabricator.control.airdropEligibility",
        "fabricator.control.registryForge",
        "fabricator.control.malformedRefused",
        "fabricator.control.foreignDiscardRefused",
        "fabricator.control.activeDiscardAtomic",
        "fabricator.control.watchdogAtomic",
        "fabricator.result.lifecycle",
        "fabricator.result.retirement",
        "fabricator.cleanup",
    }),
    client_expected=CLIENT_EXPECTED,
    server_sqf=r'''
// The whole fixture is anchored to where the player is standing, so a position
// sampled the instant the player object appears is not good enough: the player
// is still being placed and the station would be built kilometres away. Require
// the position to hold still before anchoring anything to it.
private _scenarioPlayer = objNull;
private _declaredBase = [];
private _lastPos = [0, 0, 0];
private _steadySince = 0;
private _playerDeadline = diag_tickTime + 180;
waitUntil {
    uiSleep 0.25;
    // The observer names its own unit; allPlayers ordering is not an identity.
    private _declared = missionNamespace getVariable ["TRIBUNAL_FAB_PLAYER_client-a", ""];
    _declaredBase = missionNamespace getVariable ["TRIBUNAL_FAB_BASE_client-a", []];
    _scenarioPlayer = if (_declared isEqualTo "") then {objNull} else {objectFromNetId _declared};
    private _settled = false;
    if (!isNull _scenarioPlayer && {alive _scenarioPlayer}) then {
        private _pos = getPosATL _scenarioPlayer;
        private _placed = (count _declaredBase) isEqualTo 3
            && {_pos distance2D _declaredBase < 2};
        if (_placed && {(_pos distance _lastPos) < 1}) then {
            if (_steadySince isEqualTo 0) then {_steadySince = diag_tickTime;};
            _settled = (diag_tickTime - _steadySince) > 3;
        } else {
            _steadySince = 0;
        };
        _lastPos = _pos;
    };
    _settled || {diag_tickTime > _playerDeadline}
};

private _base = +_declaredBase;

// Mission-maker registration, through the real module setters rather than by
// assigning the globals the setters publish.
private _logicGroup = createGroup sideLogic;
private _storageLogic = _logicGroup createUnit ["Logic", [0, 0, 0], [], 0, "NONE"];
private _fabricatorLogic = _logicGroup createUnit ["Logic", [0, 0, 0], [], 0, "NONE"];

private _station = createVehicle ["Land_CargoBox_V1_F", _base vectorAdd [6, 0, 0], [], 0, "CAN_COLLIDE"];
_station setPosATL (_base vectorAdd [6, 0, 0]);
private _stationFar = createVehicle ["Land_CargoBox_V1_F", _base vectorAdd [200, 0, 0], [], 0, "CAN_COLLIDE"];

// Catalogue: one heavy crate with known cargo, one light crate, one vehicle that
// no container can hold.
private _heavy = createVehicle ["Box_NATO_Ammo_F", _base vectorAdd [0, 60, 0], [], 0, "CAN_COLLIDE"];
clearWeaponCargoGlobal _heavy; clearMagazineCargoGlobal _heavy;
clearItemCargoGlobal _heavy; clearBackpackCargoGlobal _heavy;
_heavy addWeaponCargoGlobal ["arifle_MX_F", 3];
_heavy addMagazineCargoGlobal ["30Rnd_65x39_caseless_mag", 12];
_heavy addItemCargoGlobal ["FirstAidKit", 5];
_heavy addBackpackCargoGlobal ["B_AssaultPack_rgr", 2];

private _light = createVehicle ["Box_NATO_Support_F", _base vectorAdd [0, 66, 0], [], 0, "CAN_COLLIDE"];
clearWeaponCargoGlobal _light; clearMagazineCargoGlobal _light;
clearItemCargoGlobal _light; clearBackpackCargoGlobal _light;
_light addItemCargoGlobal ["ToolKit", 1];

private _oversize = createVehicle ["B_Truck_01_transport_F", _base vectorAdd [0, 74, 0], [], 0, "CAN_COLLIDE"];

// Registered by the mission maker but deliberately absent from the catalogue.
private _unregistered = createVehicle ["Box_NATO_Wps_F", _base vectorAdd [0, 82, 0], [], 0, "CAN_COLLIDE"];

// An aircraft the mission maker never registered with Vigil. Naming it must not
// authorize airdrop mode.
private _rogueAir = createVehicle ["B_Heli_Light_01_F", _base vectorAdd [0, 120, 0], [], 0, "CAN_COLLIDE"];
_rogueAir setFuel 0;

// Two real registry entries that fail distinct current-capability predicates.
private _ineligibleAir = createVehicle ["B_Heli_Light_01_F", _base vectorAdd [0, 130, 0], [], 0, "CAN_COLLIDE"];
private _busyAir = createVehicle ["B_Heli_Light_01_F", _base vectorAdd [0, 140, 0], [], 0, "CAN_COLLIDE"];
{_x setFuel 0; _x engineOn false;} forEach [_ineligibleAir, _busyAir];
private _ineligibleEntry = createHashMapFromArray [
    ["id", "tribunal-strike"], ["state", YSF_FW_STATE_ON_STATION],
    ["roleMask", YSF_FW_ROLE_STRIKE], ["side", side _scenarioPlayer],
    ["spawnedVeh", _ineligibleAir], ["logisticsActive", false]
];
private _busyEntry = createHashMapFromArray [
    ["id", "tribunal-busy-logi"], ["state", YSF_FW_STATE_ON_STATION],
    ["roleMask", YSF_FW_ROLE_LOGI], ["side", side _scenarioPlayer],
    ["spawnedVeh", _busyAir], ["logisticsActive", true],
    ["logisticsTaskId", "already-active"]
];
[YSF_FW_REGISTRY_TOKEN, "tribunal-strike", _ineligibleEntry] call YSF_fwSetEntry;
[YSF_FW_REGISTRY_TOKEN, "tribunal-busy-logi", _busyEntry] call YSF_fwSetEntry;

_storageLogic synchronizeObjectsAdd [_heavy];
_storageLogic synchronizeObjectsAdd [_light];
_storageLogic synchronizeObjectsAdd [_oversize];
_fabricatorLogic synchronizeObjectsAdd [_station];
_fabricatorLogic synchronizeObjectsAdd [_stationFar];

[_storageLogic, 0, []] call YOSHI_setVirtualStorageLogic;
[_fabricatorLogic, 0, []] call YOSHI_setFabricatorLogic;
uiSleep 1;

private _heavySourceMass = getMass _heavy;
private _heavySourceCargo = [getWeaponCargo _heavy, getMagazineCargo _heavy, getItemCargo _heavy, getBackpackCargo _heavy];

// Mission-wide census. Orders are atomic, so "produced nothing" has to mean
// nothing anywhere, not nothing near the player.
TRIBUNAL_FAB_fnc_census = {
    private _classes = ["Box_NATO_Ammo_F", "Box_NATO_Support_F", "Box_NATO_Wps_F", "B_Truck_01_transport_F", "Land_Pallet_F"];
    private _all = [];
    {_all append (allMissionObjects _x);} forEach _classes;
    private _staged = _all select {(getPosATL _x) select 2 < -50};
    // Identities, not counts: one leaked clone and one deleted source leave the
    // count unchanged, so a count-only census can pass a refusal that leaked.
    [(_all apply {netId _x}) call BIS_fnc_sortAlphabetically, count _staged]
};

private _fixture = [_token, netId _station, netId _stationFar, netId _heavy, netId _light, netId _oversize, netId _unregistered, netId _rogueAir, netId _ineligibleAir, netId _busyAir];
missionNamespace setVariable ["TRIBUNAL_FAB_FIXTURE", _fixture, true];

private _catalogue = synchronizedObjects _storageLogic;
private _stations = synchronizedObjects _fabricatorLogic;
private _fixtureOk = !isNull _scenarioPlayer
    && {!isNull _station} && {!isNull _heavy} && {!isNull _light} && {!isNull _oversize}
    && {(count _catalogue) isEqualTo 3}
    && {(count _stations) isEqualTo 2}
    && {!(_unregistered in _catalogue)}
    && {!isNull _rogueAir}
    && {!([_rogueAir, _scenarioPlayer] call YFU_fnc_fabricatorAirAssetAuthorized)}
    && {!([_ineligibleAir, _scenarioPlayer] call YFU_fnc_fabricatorAirAssetAuthorized)}
    && {!([_busyAir, _scenarioPlayer] call YFU_fnc_fabricatorAirAssetAuthorized)}
    && {!isNil "YOSHI_VIRTUAL_STORAGE"} && {!isNil "YOSHI_FABRICATOR"}
    && {_heavySourceMass > 200}
    && {(_scenarioPlayer distance _station) < YFU_FABRICATOR_ORDER_RANGE}
    && {(_scenarioPlayer distance _stationFar) > YFU_FABRICATOR_ORDER_RANGE};
["fabricator.fixture", _fixtureOk, format ["fixture=%1|catalogue=%2|stations=%3|sourceMass=%4|stationDist=%5|farDist=%6", _fixture, count _catalogue, count _stations, _heavySourceMass, _scenarioPlayer distance _station, _scenarioPlayer distance _stationFar]] call _assert;

TRIBUNAL_FAB_fnc_auditMatches = {
    params ["_ledger", "_operation", "_decision", ["_detail", ""]];
    _ledger select {
        (_x param [1, ""]) isEqualTo _operation
        && {(_x param [2, ""]) isEqualTo _decision}
        && {_detail isEqualTo "" || {(_x param [4, ""]) isEqualTo _detail}}
    }
};

// One bounded handshake per order: the client announces readiness, the server
// takes a baseline census, the client submits, the server censuses again.
TRIBUNAL_FAB_fnc_runPhase = {
    params ["_phase", "_timeout"];
    private _readyDeadline = diag_tickTime + 240;
    waitUntil {
        uiSleep 0.1;
        ((missionNamespace getVariable ["TRIBUNAL_FAB_READY", ""]) isEqualTo _phase) || {diag_tickTime > _readyDeadline}
    };
    private _before = call TRIBUNAL_FAB_fnc_census;
    private _auditBefore = +(missionNamespace getVariable ["YFU_fabricatorAudit", []]);
    private _vigilAuditBefore = +(missionNamespace getVariable ["YSF_FW_REGISTRY_AUDIT", []]);
    missionNamespace setVariable ["TRIBUNAL_FAB_GO", _phase, true];
    private _doneDeadline = diag_tickTime + _timeout;
    waitUntil {
        uiSleep 0.1;
        ((missionNamespace getVariable ["TRIBUNAL_FAB_DONE", ""]) isEqualTo _phase) || {diag_tickTime > _doneDeadline}
    };
    private _after = call TRIBUNAL_FAB_fnc_census;
    private _report = missionNamespace getVariable ["TRIBUNAL_FAB_REPORT", []];
    private _auditAfter = +(missionNamespace getVariable ["YFU_fabricatorAudit", []]);
    private _vigilAuditAfter = +(missionNamespace getVariable ["YSF_FW_REGISTRY_AUDIT", []]);
    [_before, _after, _report, ((missionNamespace getVariable ["TRIBUNAL_FAB_DONE", ""]) isEqualTo _phase), _auditAfter - _auditBefore, _vigilAuditAfter - _vigilAuditBefore]
};

// Capture the exact server state at the publication boundary. Post-result state
// is intentionally different because the client starts ACE carry immediately.
TRIBUNAL_FAB_ORIGINAL_PUBLISH = YFU_fnc_fabricatorPublishResult;
YFU_fnc_fabricatorPublishResult = {
    params ["_capability", "_txId", "_ok", "_mode", ["_objectId", ""], ["_containerIds", []], ["_positions", []]];
    if (_ok && {_mode isEqualTo "single"}) then {
        private _ready = objectFromNetId _objectId;
        missionNamespace setVariable ["TRIBUNAL_FAB_MASS_READY", [
            _txId, _objectId, getMass _ready, netId (attachedTo _ready),
            isObjectHidden _ready, local _ready, getPosATL _ready,
            _ready getVariable ["ace_dragging_ignoreWeightCarry", false],
            _ready call ace_dragging_fnc_getWeight,
            missionNamespace getVariable ["ACE_maxWeightCarry", 1e11]
        ], true];
    };
    _this call TRIBUNAL_FAB_ORIGINAL_PUBLISH
};

// Phase 1: a single local order.
private _single = ["single", 90] call TRIBUNAL_FAB_fnc_runPhase;
private _singleReport = _single # 2;
private _singleResult = _singleReport param [1, []];
private _clone = objectFromNetId (_singleResult param [3, ""]);
private _authorityOk = (_single # 3)
    && {(_singleResult param [1, false]) isEqualTo true}
    && {(_singleResult param [2, ""]) isEqualTo "single"}
    && {!isNull _clone}
    && {local _clone}
    && {typeOf _clone isEqualTo typeOf _heavy}
    && {(_clone distance _scenarioPlayer) < 12};
private _clientOwnerSeen = _singleReport param [3, -1];
private _serverTxGuess = [owner _scenarioPlayer, _singleReport param [0, ""]] call YFU_fnc_fabricatorTxId;
private _serverKnownTx = keys (call YFU_fnc_fabricatorTransactions);
private _serverResult = missionNamespace getVariable [[_serverTxGuess] call YFU_fnc_fabricatorResultKey, []];
["fabricator.authority.serverOwned", _authorityOk, format ["result=%1|clone=%2|localOnServer=%3|owner=%4|type=%5|dist=%6|playerOwner=%7|clientOwner=%8|txGuess=%9|serverResult=%10|knownTx=%11|attached=%12|mass=%13", _singleResult, netId _clone, local _clone, owner _clone, typeOf _clone, _clone distance _scenarioPlayer, owner _scenarioPlayer, _clientOwnerSeen, _serverTxGuess, _serverResult, _serverKnownTx, netId (attachedTo _clone), getMass _clone]] call _assert;

private _massReady = missionNamespace getVariable ["TRIBUNAL_FAB_MASS_READY", []];
private _massIsolationOk = (_massReady param [1, ""]) isEqualTo netId _clone
    && {(_massReady param [2, 0]) >= 199} && {(_massReady param [2, 0]) <= 201}
    && {(_massReady param [3, ""]) isEqualTo ""}
    && {!(_massReady param [4, true])} && {_massReady param [5, false]}
    && {_massReady param [7, false]};
["fabricator.delivery.massIsolation", _massIsolationOk, format ["ready=%1|postPublish=[%2,%3,%4]|player=%5", _massReady, netId (attachedTo _clone), getMass _clone, getPosATL _clone, netId _scenarioPlayer]] call _assert;

private _cloneCargo = [getWeaponCargo _clone, getMagazineCargo _clone, getItemCargo _clone, getBackpackCargo _clone];
["fabricator.fidelity.cargo", _cloneCargo isEqualTo _heavySourceCargo, format ["clone=%1|source=%2", _cloneCargo, _heavySourceCargo]] call _assert;

// Fabricated crates are capped so a player can still carry the delivery. This is
// intended usability behavior, not mass fidelity.

// The fixture deliberately supplies both sides of the surface oracle: the
// recipient and exact delivered object are on Stratis land, while the map
// origin is known open water. This proves the bounded land placement claim
// without pretending to cover gradients, ponds, or obstruction clearance.
private _baseIsWater = surfaceIsWater _base;
private _originIsWater = surfaceIsWater [0, 0, 0];
private _cloneIsWater = surfaceIsWater (getPosATL _clone);
private _resultDrop = (_singleResult param [5, []]) param [0, []];
private _landPlacementOk = !_baseIsWater
    && {_originIsWater}
    && {!_cloneIsWater}
    && {(count _resultDrop) isEqualTo 3}
    && {!surfaceIsWater _resultDrop}
    && {(_clone distance _scenarioPlayer) < 12};
["fabricator.delivery.landPlacement", _landPlacementOk, format ["base=%1|baseWater=%2|originWater=%3|clonePos=%4|cloneWater=%5|resultDrop=%6|distToResult=%7", _base, _baseIsWater, _originIsWater, getPosATL _clone, _cloneIsWater, _resultDrop, (getPosATL _clone) distance _resultDrop]] call _assert;

// The catalogue is a template source, never stock.
private _catalogueAfter = synchronizedObjects _storageLogic;
private _sourceCargoAfter = [getWeaponCargo _heavy, getMagazineCargo _heavy, getItemCargo _heavy, getBackpackCargo _heavy];
private _notConsumed = !isNull _heavy
    && {_heavy in _catalogueAfter}
    && {(count _catalogueAfter) isEqualTo 3}
    && {_sourceCargoAfter isEqualTo _heavySourceCargo}
    && {(getMass _heavy) isEqualTo _heavySourceMass};
["fabricator.catalogue.notConsumed", _notConsumed, format ["catalogue=%1|sourceAlive=%2|cargo=%3|mass=%4", count _catalogueAfter, !isNull _heavy, _sourceCargoAfter, getMass _heavy]] call _assert;

// Phase 2: a packed multi-item order.
private _multi = ["multi", 120] call TRIBUNAL_FAB_fnc_runPhase;
private _multiReport = _multi # 2;
private _multiResult = _multiReport param [1, []];
private _containers = (_multiResult param [4, []]) apply {objectFromNetId _x};
private _attachedCount = 0;
{
    if (!isNull _x) then {_attachedCount = _attachedCount + count (attachedObjects _x);};
} forEach _containers;
private _packedOk = (_multi # 3)
    && {(_multiResult param [1, false]) isEqualTo true}
    && {(_multiResult param [2, ""]) isEqualTo "multi"}
    && {(count _containers) > 0}
    && {(_containers findIf {isNull _x || {!(local _x)}}) < 0}
    && {_attachedCount isEqualTo 2}
    && {(_containers findIf {(_x distance _scenarioPlayer) > 25}) < 0};
["fabricator.delivery.packed", _packedOk, format ["result=%1|containers=%2|attached=%3|allLocal=%4", _multiResult, count _containers, _attachedCount, (_containers findIf {isNull _x || {!(local _x)}}) < 0]] call _assert;

// Matched authentic eight-object orders exercise the multi-container publication
// boundary. The observer supplies independently validated deterministic bounded targets
// so this causal pair cannot perturb later BIS_fnc_findSafePos random choices. In the control it preserves the real attempt-zero result and makes only
// later targets unavailable, while capturing exact transaction-owned state before
// the worker can refuse and delete it.
TRIBUNAL_FAB_ORIGINAL_SAFE_DROP = YFU_assetsFindSafeDropPos;
missionNamespace setVariable ["TRIBUNAL_FAB_MULTI_DROP_MODE", "allow", false];
missionNamespace setVariable ["TRIBUNAL_FAB_MULTI_DROP_OBS", [], false];
YFU_assetsFindSafeDropPos = {
    params ["_center", ["_distance", 4], ["_attempt", 0]];
    private _mode = missionNamespace getVariable ["TRIBUNAL_FAB_MULTI_DROP_MODE", "allow"];
    private _drop = if (_mode isEqualTo "first-only" && {_attempt > 0}) then {
        []
    } else {
        private _radius = _distance + (_attempt * 4);
        private _fixture = [4700, 2780, _center param [2, 0]];
        [_fixture # 0, (_fixture # 1) + _radius, _fixture # 2]
    };
    private _snapshot = [];
    if (_mode isEqualTo "first-only" && {_attempt isEqualTo 1}) then {
        private _all = call YFU_fnc_fabricatorTransactions;
        {
            private _tx = _all get _x;
            if ((_tx getOrDefault ["state", ""]) isEqualTo "building") then {
                {
                    private _object = objectFromNetId _x;
                    if (!isNull _object) then {
                        _snapshot pushBack [netId _object, typeOf _object, isObjectHidden _object, getPosATL _object, netId (attachedTo _object)];
                    };
                } forEach (_tx getOrDefault ["created", []]);
            };
        } forEach (keys _all);
    };
    private _observations = missionNamespace getVariable ["TRIBUNAL_FAB_MULTI_DROP_OBS", []];
    _observations pushBack [_attempt, _drop, _snapshot];
    missionNamespace setVariable ["TRIBUNAL_FAB_MULTI_DROP_OBS", _observations, false];
    _drop
};

private _multiPlacement = ["multiContainerSuccess", 150] call TRIBUNAL_FAB_fnc_runPhase;
private _multiPlacementResult = (_multiPlacement # 2) param [1, []];
private _multiPlacementContainers = (_multiPlacementResult param [4, []]) apply {objectFromNetId _x};
private _multiPlacementPositions = _multiPlacementResult param [5, []];
private _multiPlacementAttempts = +(missionNamespace getVariable ["TRIBUNAL_FAB_MULTI_DROP_OBS", []]);
private _multiPlacementBefore = _multiPlacementContainers apply {getPosATL _x};
private _multiPlacementDeadline = diag_tickTime + 10;
private _multiPlacementStableSince = -1;
private _multiPlacementAfter = +_multiPlacementBefore;
private _multiPlacementSpeeds = [];
waitUntil {
    uiSleep 0.1;
    private _previous = +_multiPlacementAfter;
    _multiPlacementAfter = _multiPlacementContainers apply {getPosATL _x};
    _multiPlacementSpeeds = _multiPlacementContainers apply {vectorMagnitude (velocity _x)};
    private _still = (count _previous) isEqualTo count _multiPlacementAfter;
    if (_still) then {
        for "_index" from 0 to ((count _multiPlacementContainers) - 1) do {
            if ((_multiPlacementSpeeds # _index) > 0.1
                || {(_multiPlacementAfter # _index) distance2D (_previous # _index) > 0.05}) exitWith {
                _still = false;
            };
        };
    };
    if (_still) then {
        if (_multiPlacementStableSince < 0) then {_multiPlacementStableSince = diag_tickTime;};
    } else {
        _multiPlacementStableSince = -1;
    };
    (_multiPlacementStableSince >= 0 && {(diag_tickTime - _multiPlacementStableSince) >= 2})
        || {diag_tickTime > _multiPlacementDeadline}
};
private _multiPlacementSettled = _multiPlacementStableSince >= 0
    && {(diag_tickTime - _multiPlacementStableSince) >= 2};
private _multiPlacementAttached = 0;
{if (!isNull _x) then {_multiPlacementAttached = _multiPlacementAttached + count attachedObjects _x;};} forEach _multiPlacementContainers;
private _multiPlacementUnique = _multiPlacementPositions apply {format ["%1:%2", (_x # 0) toFixed 3, (_x # 1) toFixed 3]};
_multiPlacementUnique = _multiPlacementUnique arrayIntersect _multiPlacementUnique;
private _multiPlacementExpectedAttempts = [];
for "_index" from 0 to ((count _multiPlacementContainers) - 1) do {_multiPlacementExpectedAttempts pushBack _index;};
private _multiPlacementAtTargets = true;
{
    if ((getPosATL _x) distance2D (_multiPlacementPositions # _forEachIndex) > 2) exitWith {_multiPlacementAtTargets = false;};
} forEach _multiPlacementContainers;
private _multiPlacementAttemptsOk = (_multiPlacementAttempts apply {_x # 0}) isEqualTo _multiPlacementExpectedAttempts;
private _multiPlacementObjectsOk = (_multiPlacementContainers findIf {isNull _x || {!local _x} || {isObjectHidden _x}}) < 0;
private _multiPlacementTerrainOk = (_multiPlacementPositions findIf {
    surfaceIsWater _x || {acos (((surfaceNormal _x) # 2) max -1 min 1) > 20} || {_scenarioPlayer distance2D _x > 15}
}) < 0;
private _multiPlacementOk = (_multiPlacement # 3)
    && {(_multiPlacementResult param [1, false])}
    && {(_multiPlacementResult param [2, ""]) isEqualTo "multi"}
    && {(count _multiPlacementContainers) >= 2}
    && {(count _multiPlacementPositions) isEqualTo count _multiPlacementContainers}
    && {(count _multiPlacementUnique) isEqualTo count _multiPlacementContainers}
    && {_multiPlacementAttemptsOk}
    && {_multiPlacementAttached isEqualTo 8}
    && {_multiPlacementObjectsOk}
    && {_multiPlacementTerrainOk}
    && {_multiPlacementSettled}
    && {_multiPlacementAtTargets};
_containers append _multiPlacementContainers;
["fabricator.delivery.multiContainerPlacement", _multiPlacementOk, format ["result=%1|attempts=%2|containers=%3|positions=%4|unique=%5|attached=%6|before=%7|after=%8|speeds=%9|settled=%10|atTargets=%11|attemptsOk=%12|objectsOk=%13|terrainOk=%14|player=%15", _multiPlacementResult, _multiPlacementAttempts, count _multiPlacementContainers, _multiPlacementPositions, count _multiPlacementUnique, _multiPlacementAttached, _multiPlacementBefore, _multiPlacementAfter, _multiPlacementSpeeds, _multiPlacementSettled, _multiPlacementAtTargets, _multiPlacementAttemptsOk, _multiPlacementObjectsOk, _multiPlacementTerrainOk, getPosATL _scenarioPlayer]] call _assert;

missionNamespace setVariable ["TRIBUNAL_FAB_MULTI_DROP_MODE", "first-only", false];
missionNamespace setVariable ["TRIBUNAL_FAB_MULTI_DROP_OBS", [], false];
private _multiRefusal = ["multiContainerRefusal", 150] call TRIBUNAL_FAB_fnc_runPhase;
private _multiRefusalResult = (_multiRefusal # 2) param [1, []];
private _multiRefusalAttempts = +(missionNamespace getVariable ["TRIBUNAL_FAB_MULTI_DROP_OBS", []]);
private _firstAttemptIndex = _multiRefusalAttempts findIf {(_x # 0) isEqualTo 0};
private _secondAttemptIndex = _multiRefusalAttempts findIf {(_x # 0) isEqualTo 1};
private _firstAttempt = if (_firstAttemptIndex < 0) then {[]} else {_multiRefusalAttempts # _firstAttemptIndex};
private _secondAttempt = if (_secondAttemptIndex < 0) then {[]} else {_multiRefusalAttempts # _secondAttemptIndex};
private _firstTarget = _firstAttempt param [1, []];
private _preRefusal = _secondAttempt param [2, []];
private _preRefusalContainers = _preRefusal select {(_x # 1) isEqualTo "Land_Pallet_F"};
private _multiRefusalOk = (_multiRefusal # 3)
    && {!(_firstTarget isEqualTo [])}
    && {(_secondAttempt param [1, [1]]) isEqualTo []}
    && {(count _preRefusalContainers) isEqualTo count _multiPlacementContainers}
    && {(count _preRefusal) isEqualTo (8 + count _multiPlacementContainers)}
    && {(_preRefusal findIf {!(_x # 2)}) < 0}
    && {(_preRefusalContainers findIf {(_x # 3) distance2D _firstTarget <= 0.25}) < 0}
    && {!(_multiRefusalResult param [1, true])}
    && {(_multiRefusalResult param [2, ""]) isEqualTo "no-safe-drop"}
    && {(_multiRefusalResult param [4, []]) isEqualTo []}
    && {(_multiRefusalResult param [5, []]) isEqualTo []}
    && {(_multiRefusal # 1) isEqualTo (_multiRefusal # 0)};
["fabricator.control.multiContainerAtomic", _multiRefusalOk, format ["result=%1|attempts=%2|firstTarget=%3|preRefusal=%4|census=%5:%6", _multiRefusalResult, _multiRefusalAttempts, _firstTarget, _preRefusal, _multiRefusal # 0, _multiRefusal # 1]] call _assert;
YFU_assetsFindSafeDropPos = TRIBUNAL_FAB_ORIGINAL_SAFE_DROP;
missionNamespace setVariable ["TRIBUNAL_FAB_MULTI_DROP_MODE", nil, false];
missionNamespace setVariable ["TRIBUNAL_FAB_MULTI_DROP_OBS", nil, false];

// Four authentic successful packed orders hold class, quantity, authority, terminal entry,
// placement helper, settling window and observation constant. Only terrain and
// the declared barrier ring differ. A two-metre seating bound allows one pallet
// footprint of initial PhysX adjustment; continuous rest and final speed remain
// independent requirements.
private _shoreProbe = [1465, 4888, 0];
missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", ["terrainShoreProbe", _shoreProbe], true];
private _shoreProbeDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_TERRAIN_READY", ""]) isEqualTo "terrainShoreProbe"
        || {diag_tickTime > _shoreProbeDeadline}
};

// surfaceIsWater pond/object results depend on the area being loaded. Scan only
// after client-a has loaded this coastline, and use the product fallback matrix
// itself to select a water recipient with independently observed nearby land.
private _shorePair = [[], []];
private _shoreLandCount = 0;
for "_gridX" from -10 to 10 do {
    for "_gridY" from -10 to 10 do {
        private _candidateCenter = _shoreProbe vectorAdd [_gridX * 5, _gridY * 5, 0];
        if (surfaceIsWater _candidateCenter) then {
            private _landCandidates = [];
            {
                private _radius = _x;
                for "_bearing" from 0 to 345 step 15 do {
                    _landCandidates pushBack (_candidateCenter vectorAdd [_radius * sin _bearing, _radius * cos _bearing, 0]);
                };
            } forEach [4, 6.5, 9];
            private _validLand = _landCandidates select {
                !surfaceIsWater _x
                    && {acos (((surfaceNormal _x) # 2) max -1 min 1) <= 20}
            };
            if ((count _validLand) > _shoreLandCount) then {
                _shoreLandCount = count _validLand;
                _shorePair = [_candidateCenter, _validLand # 0];
            };
        };
    };
};
private _shoreCenter = _shorePair param [0, []];
private _shoreLand = _shorePair param [1, []];
private _shoreCenterIsWater = !(_shoreCenter isEqualTo []) && {surfaceIsWater _shoreCenter};

private _terrainBarriers = [];
private _terrainRows = [];
{
    _x params ["_label", "_center", "_blocked"];
    private _armBarriers = [];
    if (_blocked) then {
        {
            private _radius = _x;
            for "_bearing" from 0 to 337.5 step 22.5 do {
                private _position = _center vectorAdd [_radius * sin _bearing, _radius * cos _bearing, 0];
                private _barrier = createVehicle ["Land_CncBarrier_F", _position, [], 0, "CAN_COLLIDE"];
                _barrier setPosATL _position;
                _barrier setDir _bearing;
                _armBarriers pushBack _barrier;
            };
        } forEach [3, 5, 7, 9];
        _terrainBarriers append _armBarriers;
    };

    _station setPosATL (_center vectorAdd [0, 1, 0]);
    _station setVectorUp (surfaceNormal (getPosATL _station));
    missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", [_label, _center], true];
    private _readyDeadline = diag_tickTime + 60;
    waitUntil {
        uiSleep 0.1;
        (missionNamespace getVariable ["TRIBUNAL_FAB_TERRAIN_READY", ""]) isEqualTo _label
            || {diag_tickTime > _readyDeadline}
    };

    private _arm = [_label, 120] call TRIBUNAL_FAB_fnc_runPhase;
    private _result = _arm # 2 param [1, []];
    private _armContainers = (_result param [4, []]) apply {objectFromNetId _x};
    private _container = _armContainers param [0, objNull];
    private _drop = (_result param [5, []]) param [0, []];
    private _start = getPosATL _container;
    private _previous = _start;
    private _stableSince = -1;
    private _maxSpeed = 0;
    private _settleDeadline = diag_tickTime + 8;
    waitUntil {
        uiSleep 0.1;
        private _position = getPosATL _container;
        private _speed = vectorMagnitude (velocity _container);
        _maxSpeed = _maxSpeed max _speed;
        if (!isNull _container && {_speed <= 0.1} && {(_position distance _previous) <= 0.05}) then {
            if (_stableSince < 0) then {_stableSince = diag_tickTime;};
        } else {
            _stableSince = -1;
        };
        _previous = _position;
        (_stableSince >= 0 && {(diag_tickTime - _stableSince) >= 2}) || {diag_tickTime > _settleDeadline}
    };
    private _final = getPosATL _container;
    private _nearestBarrier = -1;
    if !(_armBarriers isEqualTo []) then {
        _nearestBarrier = selectMin (_armBarriers apply {_x distance2D _drop});
    };
    private _row = [
        _label, (_arm # 3) && {(_result param [1, false])} && {(_result param [2, ""]) isEqualTo "multi"},
        acos (((surfaceNormal _center) # 2) max -1 min 1),
        acos (((surfaceNormal _drop) # 2) max -1 min 1),
        _center distance2D _drop, surfaceIsWater _drop, count _armBarriers, _nearestBarrier,
        netId _container, local _container, count (attachedObjects _container),
        _stableSince >= 0 && {(diag_tickTime - _stableSince) >= 2},
        _drop distance2D _final, _maxSpeed, vectorMagnitude (velocity _container), _drop, _final,
        surfaceIsWater _center
    ];
    _terrainRows pushBack _row;
    _containers append _armContainers;
} forEach [
    ["terrainFlat", [1500, 5000, 0], false],
    ["terrainGradient", [2100, 2500, 0], false],
    ["terrainBlocked", [1600, 5000, 0], true],
    ["terrainShore", _shoreCenter, false]
];

private _flatTerrain = _terrainRows param [0, []];
private _gradientTerrain = _terrainRows param [1, []];
private _blockedTerrain = _terrainRows param [2, []];
private _shoreTerrain = _terrainRows param [3, []];
private _terrainCommonOk = (count _terrainRows) isEqualTo 4
    && {(_terrainRows findIf {
        !(_x param [1, false]) || {_x param [5, true]} || {!(_x param [9, false])}
        || {(_x param [10, 0]) isNotEqualTo 2} || {!(_x param [11, false])}
        || {(_x param [12, 99]) > 2} || {(_x param [14, 99]) > 0.1}
        || {(_x param [4, 99]) > 15}
    }) < 0};
private _terrainMatrixOk = _terrainCommonOk
    && {(_flatTerrain param [2, 99]) <= 1} && {(_flatTerrain param [3, 99]) <= 10}
    && {(_gradientTerrain param [2, 0]) >= 10} && {(_gradientTerrain param [2, 99]) <= 20}
    && {(_gradientTerrain param [3, 0]) >= 10} && {(_gradientTerrain param [3, 99]) <= 20}
    && {(_blockedTerrain param [2, 99]) <= 1} && {(_blockedTerrain param [6, 0]) isEqualTo 64}
    && {(_blockedTerrain param [7, 99]) >= 0} && {(_blockedTerrain param [7, 99]) <= 1.6};
["fabricator.delivery.terrainMatrix", _terrainMatrixOk, format ["rows=%1", _terrainRows]] call _assert;

// A shoreline recipient varies only water adjacency: the authentic order must
// find bounded moderate land and settle there. At deep-water origin every point
// in a 15 m control matrix is water, so the same order must refuse atomically.
_station setPosATL [0, 1, 0];
missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", ["terrainDeepWater", [0, 0, 0]], true];
private _deepReadyDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_TERRAIN_READY", ""]) isEqualTo "terrainDeepWater"
        || {diag_tickTime > _deepReadyDeadline}
};
private _deep = ["terrainDeepWater", 120] call TRIBUNAL_FAB_fnc_runPhase;
private _deepResult = (_deep # 2) param [1, []];
private _deepSamples = [];
{
    private _radius = _x;
    for "_bearing" from 0 to 345 step 15 do {
        private _sample = [_radius * sin _bearing, _radius * cos _bearing, 0];
        _deepSamples pushBack [_sample, surfaceIsWater _sample];
    };
} forEach [0, 3, 6, 9, 12, 15];
private _shoreOk = _shoreCenterIsWater
    && {!(_shoreLand isEqualTo [])}
    && {_shoreCenter distance2D _shoreLand <= 9}
    && {_shoreLandCount >= 12}
    && {(_shoreTerrain param [1, false])}
    && {!(_shoreTerrain param [5, true])}
    && {(_shoreTerrain param [3, 99]) <= 20}
    && {(_shoreTerrain param [4, 99]) <= 15};
private _deepOk = (_deep # 3)
    && {!(_deepResult param [1, true])}
    && {(_deepResult param [2, ""]) isEqualTo "no-safe-drop"}
    && {(_deep # 1) isEqualTo (_deep # 0)}
    && {((_deepResult param [4, []]) isEqualTo [])}
    && {((_deepResult param [5, []]) isEqualTo [])}
    && {(_deepSamples findIf {!(_x param [1, false])}) < 0};
["fabricator.delivery.shoreline", _shoreOk, format ["shore=%1|shoreLand=%2|landRays=%3|selectedWater=%4", _shoreTerrain, _shoreLand, _shoreLandCount, _shoreCenterIsWater]] call _assert;
["fabricator.control.deepWaterAtomic", _deepOk, format ["result=%1|census=%2:%3|samples=%4", _deepResult, _deep # 0, _deep # 1, _deepSamples]] call _assert;

// Repeat the accepted shoreline/all-water comparison through the distinct
// single-item branch. Observe the exact hidden transaction clone before the real
// helper decides, then retain the authentic helper and publication behavior.
TRIBUNAL_FAB_SINGLE_ORIGINAL_SAFE_DROP = YFU_assetsFindSafeDropPos;
missionNamespace setVariable ["TRIBUNAL_FAB_SINGLE_DROP_MODE", "shore", false];
missionNamespace setVariable ["TRIBUNAL_FAB_SINGLE_DROP_OBS", [], false];
YFU_assetsFindSafeDropPos = {
    private _mode = missionNamespace getVariable ["TRIBUNAL_FAB_SINGLE_DROP_MODE", "unknown"];
    private _snapshot = [];
    private _all = call YFU_fnc_fabricatorTransactions;
    {
        private _tx = _all get _x;
        if ((_tx getOrDefault ["state", ""]) isEqualTo "building") then {
            {
                private _object = objectFromNetId _x;
                if (!isNull _object) then {
                    _snapshot pushBack [netId _object, typeOf _object, isObjectHidden _object, getPosATL _object, local _object];
                };
            } forEach (_tx getOrDefault ["created", []]);
        };
    } forEach (keys _all);
    private _drop = _this call TRIBUNAL_FAB_SINGLE_ORIGINAL_SAFE_DROP;
    private _observations = missionNamespace getVariable ["TRIBUNAL_FAB_SINGLE_DROP_OBS", []];
    _observations pushBack [_mode, _drop, _snapshot];
    missionNamespace setVariable ["TRIBUNAL_FAB_SINGLE_DROP_OBS", _observations, false];
    _drop
};

_station setPosATL (_shoreCenter vectorAdd [0, 1, 0]);
_station setVectorUp (surfaceNormal (getPosATL _station));
missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", ["singleTerrainShore", _shoreCenter], true];
private _singleShoreReadyDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_TERRAIN_READY", ""]) isEqualTo "singleTerrainShore"
        || {diag_tickTime > _singleShoreReadyDeadline}
};
private _singleShore = ["singleTerrainShore", 120] call TRIBUNAL_FAB_fnc_runPhase;
private _singleShoreResult = (_singleShore # 2) param [1, []];
private _singleShoreId = _singleShoreResult param [3, ""];
private _singleShoreObject = objectFromNetId _singleShoreId;
private _singleShoreDrop = (_singleShoreResult param [5, []]) param [0, []];
private _singleShoreReady = +(missionNamespace getVariable ["TRIBUNAL_FAB_MASS_READY", []]);
private _singleShoreObs = +(missionNamespace getVariable ["TRIBUNAL_FAB_SINGLE_DROP_OBS", []]);
private _singleShoreObsIndex = _singleShoreObs findIf {(_x # 0) isEqualTo "shore"};
private _singleShoreDecision = if (_singleShoreObsIndex < 0) then {[]} else {_singleShoreObs # _singleShoreObsIndex};
private _singleShorePreDecision = _singleShoreDecision param [2, []];
private _singleShorePublishPos = _singleShoreReady param [6, []];
private _singleShoreCargo = if (isNull _singleShoreObject) then {[]} else {[
    getWeaponCargo _singleShoreObject, getMagazineCargo _singleShoreObject,
    getItemCargo _singleShoreObject, getBackpackCargo _singleShoreObject
]};
private _singleShoreProtocolOk = (_singleShore # 3)
    && {(_singleShore # 2) param [2, false]}
    && {(_singleShoreResult param [1, false])}
    && {(_singleShoreResult param [2, ""]) isEqualTo "single"};
private _singleShoreIdentityOk = !(_singleShoreId isEqualTo "") && {!isNull _singleShoreObject}
    && {local _singleShoreObject} && {typeOf _singleShoreObject isEqualTo typeOf _heavy}
    && {(count _singleShorePreDecision) isEqualTo 1}
    && {((_singleShorePreDecision # 0) # 0) isEqualTo _singleShoreId}
    && {((_singleShorePreDecision # 0) # 2)} && {((_singleShorePreDecision # 0) # 4)}
    && {(_singleShoreDecision param [1, []]) isEqualTo _singleShoreDrop};
private _singleShoreReadyOk = (_singleShoreReady param [1, ""]) isEqualTo _singleShoreId
    && {(_singleShoreReady param [2, 0]) >= 199} && {(_singleShoreReady param [2, 0]) <= 201}
    && {!(_singleShoreReady param [4, true])} && {_singleShoreReady param [5, false]}
    && {_singleShoreReady param [7, false]};
private _singleShoreTerrainOk = _shoreCenterIsWater && {!(_singleShoreDrop isEqualTo [])}
    && {!surfaceIsWater _singleShoreDrop}
    && {acos (((surfaceNormal _singleShoreDrop) # 2) max -1 min 1) <= 20}
    && {_shoreCenter distance2D _singleShoreDrop <= 15}
    && {_singleShorePublishPos distance2D _singleShoreDrop <= 2};
private _singleShoreDeliveryOk = _singleShoreCargo isEqualTo _heavySourceCargo
    && {(attachedTo _singleShoreObject) isEqualTo _scenarioPlayer};
private _singleShoreOk = _singleShoreProtocolOk && {_singleShoreIdentityOk}
    && {_singleShoreReadyOk} && {_singleShoreTerrainOk} && {_singleShoreDeliveryOk};
_containers pushBack _singleShoreObject;
["fabricator.delivery.singleTerrainBoundary", _singleShoreOk, format ["result=%1|decision=%2|ready=%3|drop=%4|cargo=%5|attached=%6|protocolOk=%7|identityOk=%8|readyOk=%9|terrainOk=%10|deliveryOk=%11|shoreCenter=%12|slope=%13|publishDistance=%14", _singleShoreResult, _singleShoreDecision, _singleShoreReady, _singleShoreDrop, _singleShoreCargo, netId (attachedTo _singleShoreObject), _singleShoreProtocolOk, _singleShoreIdentityOk, _singleShoreReadyOk, _singleShoreTerrainOk, _singleShoreDeliveryOk, _shoreCenter, acos (((surfaceNormal _singleShoreDrop) # 2) max -1 min 1), _singleShorePublishPos distance2D _singleShoreDrop]] call _assert;

missionNamespace setVariable ["TRIBUNAL_FAB_SINGLE_DROP_MODE", "deep", false];
_station setPosATL [0, 1, 0];
missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", ["singleTerrainDeepWater", [0, 0, 0]], true];
private _singleDeepReadyDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_TERRAIN_READY", ""]) isEqualTo "singleTerrainDeepWater"
        || {diag_tickTime > _singleDeepReadyDeadline}
};
private _singleDeep = ["singleTerrainDeepWater", 120] call TRIBUNAL_FAB_fnc_runPhase;
private _singleDeepResult = (_singleDeep # 2) param [1, []];
private _singleDeepObs = +(missionNamespace getVariable ["TRIBUNAL_FAB_SINGLE_DROP_OBS", []]);
private _singleDeepObsIndex = _singleDeepObs findIf {(_x # 0) isEqualTo "deep"};
private _singleDeepDecision = if (_singleDeepObsIndex < 0) then {[]} else {_singleDeepObs # _singleDeepObsIndex};
private _singleDeepPreDecision = _singleDeepDecision param [2, []];
private _singleDeepOk = (_singleDeep # 3)
    && {(count _singleDeepPreDecision) isEqualTo 1}
    && {((_singleDeepPreDecision # 0) # 1) isEqualTo typeOf _heavy}
    && {((_singleDeepPreDecision # 0) # 2)} && {((_singleDeepPreDecision # 0) # 4)}
    && {(_singleDeepDecision param [1, [1]]) isEqualTo []}
    && {!(_singleDeepResult param [1, true])}
    && {(_singleDeepResult param [2, ""]) isEqualTo "no-safe-drop"}
    && {(_singleDeepResult param [3, ""]) isEqualTo ""}
    && {(_singleDeepResult param [4, []]) isEqualTo []}
    && {(_singleDeepResult param [5, []]) isEqualTo []}
    && {(_singleDeep # 1) isEqualTo (_singleDeep # 0)}
    && {(_deepSamples findIf {!(_x param [1, false])}) < 0};
["fabricator.control.singleDeepWaterAtomic", _singleDeepOk, format ["result=%1|decision=%2|census=%3:%4|samples=%5", _singleDeepResult, _singleDeepDecision, _singleDeep # 0, _singleDeep # 1, _deepSamples]] call _assert;
YFU_assetsFindSafeDropPos = TRIBUNAL_FAB_SINGLE_ORIGINAL_SAFE_DROP;
TRIBUNAL_FAB_SINGLE_ORIGINAL_SAFE_DROP = nil;
missionNamespace setVariable ["TRIBUNAL_FAB_SINGLE_DROP_MODE", nil, false];
missionNamespace setVariable ["TRIBUNAL_FAB_SINGLE_DROP_OBS", nil, false];

// Revisit the rejected steep face with the fail-closed product rule now in
// place. The matched arms vary only whether a moderate non-water point exists
// inside the bounded search; both use the authentic packed terminal order.
private _slopeProbe = [4600, 6700, 0];
missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", ["terrainSlopeProbe", _slopeProbe], true];
private _slopeProbeDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_TERRAIN_READY", ""]) isEqualTo "terrainSlopeProbe"
        || {diag_tickTime > _slopeProbeDeadline}
};

private _recoveryCenter = [4573, 6664, 0];
private _recoverySamples = [];
{
    private _radius = _x;
    for "_bearing" from 0 to 345 step 15 do {
        private _samplePos = _recoveryCenter vectorAdd [_radius * sin _bearing, _radius * cos _bearing, 0];
        private _sampleSlope = acos (((surfaceNormal _samplePos) # 2) max -1 min 1);
        _recoverySamples pushBack [_samplePos, _sampleSlope, surfaceIsWater _samplePos];
    };
} forEach [4, 6.5, 9];
private _recoveryModerate = _recoverySamples select {!(_x # 2) && {(_x # 1) <= 20}};
private _recoveryScore = count _recoveryModerate;

private _refusalCenter = [4603, 6727, 0];
private _refusalSamples = [];
for "_offsetX" from -14 to 14 step 2 do {
    for "_offsetY" from -14 to 14 step 2 do {
        if (sqrt ((_offsetX * _offsetX) + (_offsetY * _offsetY)) <= 15) then {
            private _samplePos = _refusalCenter vectorAdd [_offsetX, _offsetY, 0];
            private _sampleSlope = acos (((surfaceNormal _samplePos) # 2) max -1 min 1);
            _refusalSamples pushBack [_samplePos, _sampleSlope, surfaceIsWater _samplePos];
        };
    };
};
private _refusalFloor = if (_refusalSamples isEqualTo []) then {-1} else {selectMin (_refusalSamples apply {_x # 1})};

_station setPosATL (_recoveryCenter vectorAdd [0, 1, 0]);
_station setVectorUp (surfaceNormal (getPosATL _station));
missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", ["terrainSevereRecovery", _recoveryCenter], true];
private _recoveryReadyDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_TERRAIN_READY", ""]) isEqualTo "terrainSevereRecovery"
        || {diag_tickTime > _recoveryReadyDeadline}
};
private _severeRecovery = ["terrainSevereRecovery", 120] call TRIBUNAL_FAB_fnc_runPhase;
private _recoveryResult = (_severeRecovery # 2) param [1, []];
private _recoveryContainers = (_recoveryResult param [4, []]) apply {objectFromNetId _x};
private _recoveryContainer = _recoveryContainers param [0, objNull];
private _recoveryDrop = (_recoveryResult param [5, []]) param [0, []];
private _recoveryPrevious = getPosATL _recoveryContainer;
private _recoveryStableSince = -1;
private _recoverySettleDeadline = diag_tickTime + 8;
waitUntil {
    uiSleep 0.1;
    private _position = getPosATL _recoveryContainer;
    private _speed = vectorMagnitude (velocity _recoveryContainer);
    if (!isNull _recoveryContainer && {_speed <= 0.1} && {(_position distance _recoveryPrevious) <= 0.05}) then {
        if (_recoveryStableSince < 0) then {_recoveryStableSince = diag_tickTime;};
    } else {
        _recoveryStableSince = -1;
    };
    _recoveryPrevious = _position;
    (_recoveryStableSince >= 0 && {(diag_tickTime - _recoveryStableSince) >= 2}) || {diag_tickTime > _recoverySettleDeadline}
};
private _recoveryFinal = getPosATL _recoveryContainer;
private _recoveryDropSlope = if (_recoveryDrop isEqualTo []) then {99} else {acos (((surfaceNormal _recoveryDrop) # 2) max -1 min 1)};
private _recoveryOk = (_severeRecovery # 3)
    && {acos (((surfaceNormal _recoveryCenter) # 2) max -1 min 1) >= 30}
    && {_recoveryScore > 0}
    && {(_recoveryResult param [1, false])}
    && {(_recoveryResult param [2, ""]) isEqualTo "multi"}
    && {!(_recoveryDrop isEqualTo [])}
    && {!surfaceIsWater _recoveryDrop}
    && {_recoveryDropSlope <= 20}
    && {_recoveryCenter distance2D _recoveryDrop <= 15}
    && {!isNull _recoveryContainer}
    && {local _recoveryContainer}
    && {(count attachedObjects _recoveryContainer) isEqualTo 2}
    && {_recoveryStableSince >= 0 && {(diag_tickTime - _recoveryStableSince) >= 2}}
    && {_recoveryDrop distance2D _recoveryFinal <= 2}
    && {vectorMagnitude (velocity _recoveryContainer) <= 0.1};
_containers append _recoveryContainers;
["fabricator.delivery.severeGradientRecovery", _recoveryOk, format ["center=%1|centerSlope=%2|moderate=%3|result=%4|drop=%5|dropSlope=%6|final=%7", _recoveryCenter, acos (((surfaceNormal _recoveryCenter) # 2) max -1 min 1), count _recoveryModerate, _recoveryResult, _recoveryDrop, _recoveryDropSlope, _recoveryFinal]] call _assert;

_station setPosATL (_refusalCenter vectorAdd [0, 1, 0]);
_station setVectorUp (surfaceNormal (getPosATL _station));
missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", ["terrainSevereRefusal", _refusalCenter], true];
private _refusalReadyDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_TERRAIN_READY", ""]) isEqualTo "terrainSevereRefusal"
        || {diag_tickTime > _refusalReadyDeadline}
};
private _severeRefusal = ["terrainSevereRefusal", 120] call TRIBUNAL_FAB_fnc_runPhase;
private _refusalResult = (_severeRefusal # 2) param [1, []];
private _refusalOk = (_severeRefusal # 3)
    && {acos (((surfaceNormal _refusalCenter) # 2) max -1 min 1) >= 30}
    && {_refusalFloor > 20}
    && {(_refusalSamples findIf {(_x # 2) || {(_x # 1) <= 20}}) < 0}
    && {!(_refusalResult param [1, true])}
    && {(_refusalResult param [2, ""]) isEqualTo "no-safe-drop"}
    && {(_severeRefusal # 1) isEqualTo (_severeRefusal # 0)}
    && {((_refusalResult param [4, []]) isEqualTo [])}
    && {((_refusalResult param [5, []]) isEqualTo [])};
["fabricator.control.severeGradientAtomic", _refusalOk, format ["center=%1|centerSlope=%2|floor=%3|sampleCount=%4|result=%5|census=%6:%7", _refusalCenter, acos (((surfaceNormal _refusalCenter) # 2) max -1 min 1), _refusalFloor, count _refusalSamples, _refusalResult, _severeRefusal # 0, _severeRefusal # 1]] call _assert;

_station setPosATL (_base vectorAdd [6, 0, 0]);
missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", ["terrainRestore", _base], true];
private _restoreDeadline = diag_tickTime + 60;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FAB_TERRAIN_READY", ""]) isEqualTo "terrainRestore"
        || {diag_tickTime > _restoreDeadline}
};

// Phase 3: an order containing something no container can hold. Atomic means the
// whole order is refused and nothing at all survives, anywhere on the map.
private _unpackable = ["unpackable", 120] call TRIBUNAL_FAB_fnc_runPhase;
private _unpackableReport = _unpackable # 2;
private _unpackableResult = _unpackableReport param [1, []];
private _atomicOk = (_unpackable # 3)
    && {(_unpackableResult param [1, true]) isEqualTo false}
    && {(_unpackableResult param [2, ""]) isEqualTo "unpackable"}
    && {(_unpackable # 1) isEqualTo (_unpackable # 0)}
    && {(netId _heavy) in ((_unpackable # 1) # 0)}
    && {(netId _oversize) in ((_unpackable # 1) # 0)}
    && {((_unpackable # 1) # 1) isEqualTo 0}
    && {(_unpackableReport param [2, true]) isEqualTo false};
["fabricator.control.unpackableAtomic", _atomicOk, format ["result=%1|censusBefore=%2|censusAfter=%3|clientSuccess=%4", _unpackableResult, _unpackable # 0, _unpackable # 1, _unpackableReport param [2, "unset"]]] call _assert;

// Phase 4: an order naming an object the mission maker never registered.
private _rogue = ["unregistered", 90] call TRIBUNAL_FAB_fnc_runPhase;
private _rogueReport = _rogue # 2;
private _rogueResult = _rogueReport param [1, []];
private _rogueOk = (_rogue # 3)
    && {(_rogueResult param [1, true]) isEqualTo false}
    && {(_rogueResult param [2, ""]) isEqualTo "unregistered"}
    && {(_rogue # 1) isEqualTo (_rogue # 0)};
["fabricator.control.unregistered", _rogueOk, format ["result=%1|censusBefore=%2|censusAfter=%3", _rogueResult, _rogue # 0, _rogue # 1]] call _assert;

// Phase 5: an order placed against a registered station the player is nowhere near.
private _far = ["outOfRange", 90] call TRIBUNAL_FAB_fnc_runPhase;
private _farReport = _far # 2;
private _farResult = _farReport param [1, []];
private _farOk = (_far # 3)
    && {(_farResult param [1, true]) isEqualTo false}
    && {(_farResult param [2, ""]) isEqualTo "out-of-range"}
    && {(_far # 1) isEqualTo (_far # 0)};
["fabricator.control.outOfRange", _farOk, format ["result=%1|censusBefore=%2|censusAfter=%3|farDist=%4", _farResult, _far # 0, _far # 1, _scenarioPlayer distance _stationFar]] call _assert;

// Phase 6: with no Virtual Storage registered there is no catalogue to order from.
private _registeredCatalogue = +(localNamespace getVariable ["YFU_MODULE_CATALOGUE", []]);
localNamespace setVariable ["YFU_MODULE_CATALOGUE", []];
uiSleep 0.5;
private _noStorage = ["noStorage", 90] call TRIBUNAL_FAB_fnc_runPhase;
private _noStorageReport = _noStorage # 2;
private _noStorageResult = _noStorageReport param [1, []];
private _noStorageOk = (_noStorage # 3)
    && {(_noStorageResult param [1, true]) isEqualTo false}
    && {(_noStorageResult param [2, ""]) isEqualTo "no-storage"}
    && {(_noStorage # 1) isEqualTo (_noStorage # 0)};
["fabricator.control.noStorage", _noStorageOk, format ["result=%1|censusBefore=%2|censusAfter=%3", _noStorageResult, _noStorage # 0, _noStorage # 1]] call _assert;
localNamespace setVariable ["YFU_MODULE_CATALOGUE", _registeredCatalogue];

// A transaction this client does not own, seeded server-side so the discard
// control has something real to fail to destroy.
private _victim = createVehicle ["Box_NATO_Support_F", _base vectorAdd [0, 95, 0], [], 0, "CAN_COLLIDE"];
private _serverTxId = [2, "tribunal-server-order"] call YFU_fnc_fabricatorTxId;
private _allTx = call YFU_fnc_fabricatorTransactions;
private _seeded = createHashMap;
_seeded set ["claimed", true];
_seeded set ["owner", 2];
_seeded set ["state", "delivered"];
_seeded set ["created", [netId _victim]];
_allTx set [_serverTxId, _seeded];

// Reaching past the endpoint into the worker itself.
private _bypass = ["bypass", 90] call TRIBUNAL_FAB_fnc_runPhase;
private _bypassAudit = [_bypass # 4, "worker", "token-rejected", "guessed#tribunal-bypass"] call TRIBUNAL_FAB_fnc_auditMatches;
private _bypassOk = (_bypass # 3)
    && {((_bypass # 2) param [1, []]) isEqualTo []}
    && {(_bypass # 1) isEqualTo (_bypass # 0)}
    && {(count _bypassAudit) isEqualTo 1}
    && {(["guessed#tribunal-bypass"] call YFU_fnc_fabricatorTxState) isEqualTo "unknown"};
["fabricator.control.workerBypass", _bypassOk, format ["result=%1|censusHeld=%2|receipt=%3|txState=%4", (_bypass # 2) param [1, []], (_bypass # 1) isEqualTo (_bypass # 0), _bypassAudit, ["guessed#tribunal-bypass"] call YFU_fnc_fabricatorTxState]] call _assert;

private _acceptBypass = ["acceptBypass", 90] call TRIBUNAL_FAB_fnc_runPhase;
private _acceptAudit = [_acceptBypass # 4, "accept", "token-rejected", "2"] call TRIBUNAL_FAB_fnc_auditMatches;
private _acceptTx = [2, "tribunal-accept-bypass"] call YFU_fnc_fabricatorTxId;
private _acceptBypassOk = (_acceptBypass # 3)
    && {(_acceptBypass # 1) isEqualTo (_acceptBypass # 0)}
    && {(count _acceptAudit) isEqualTo 1}
    && {([_acceptTx] call YFU_fnc_fabricatorTxState) isEqualTo "unknown"};
["fabricator.control.acceptBypass", _acceptBypassOk, format ["receipt=%1|censusHeld=%2|tx=%3|state=%4", _acceptAudit, (_acceptBypass # 1) isEqualTo (_acceptBypass # 0), _acceptTx, [_acceptTx] call YFU_fnc_fabricatorTxState]] call _assert;

// The same request id twice: exactly one order may exist.
private _dup = ["duplicate", 150] call TRIBUNAL_FAB_fnc_runPhase;
private _dupResult = (_dup # 2) param [1, []];
private _dupNew = ((_dup # 1) # 0) - ((_dup # 0) # 0);
private _dupTx = [owner _scenarioPlayer, "tribunal-dup"] call YFU_fnc_fabricatorTxId;
private _dupAccepted = [_dup # 4, "order", "accepted", _dupTx] call TRIBUNAL_FAB_fnc_auditMatches;
private _dupRejected = [_dup # 4, "order", "replay-rejected", _dupTx] call TRIBUNAL_FAB_fnc_auditMatches;
private _dupOk = (_dup # 3)
    && {(_dupResult param [1, false]) isEqualTo true}
    && {(_dupResult param [2, ""]) isEqualTo "single"}
    && {(count _dupNew) isEqualTo 1}
    && {(_dupResult param [3, ""]) in _dupNew}
    && {(count _dupAccepted) isEqualTo 1}
    && {(count _dupRejected) isEqualTo 1};
["fabricator.control.duplicateRequest", _dupOk, format ["result=%1|created=%2|accepted=%3|rejected=%4", _dupResult, _dupNew, _dupAccepted, _dupRejected]] call _assert;

// Airdrop mode named an aircraft nobody registered.
private _rogue = ["rogueAirdrop", 90] call TRIBUNAL_FAB_fnc_runPhase;
private _rogueResult = (_rogue # 2) param [1, []];
private _rogueOk = (_rogue # 3)
    && {(_rogueResult param [1, true]) isEqualTo false}
    && {(_rogueResult param [2, ""]) isEqualTo "airdrop-unauthorized"}
    && {(_rogue # 1) isEqualTo (_rogue # 0)};
["fabricator.control.airdropUnauthorized", _rogueOk, format ["result=%1|before=%2|after=%3|authorized=%4", _rogueResult, (_rogue # 0) # 0, (_rogue # 1) # 0, [_rogueAir, _scenarioPlayer] call YFU_fnc_fabricatorAirAssetAuthorized]] call _assert;

private _requesterSide = side _scenarioPlayer;
_ineligibleEntry set ["side", _requesterSide];
_busyEntry set ["side", _requesterSide];
[YSF_FW_REGISTRY_TOKEN, "tribunal-strike", _ineligibleEntry] call YSF_fwSetEntry;
[YSF_FW_REGISTRY_TOKEN, "tribunal-busy-logi", _busyEntry] call YSF_fwSetEntry;
private _ineligible = ["ineligibleAirdrop", 90] call TRIBUNAL_FAB_fnc_runPhase;
private _busy = ["busyAirdrop", 90] call TRIBUNAL_FAB_fnc_runPhase;
private _ineligibleResult = (_ineligible # 2) param [1, []];
private _busyResult = (_busy # 2) param [1, []];
private _roleVerdict = [_ineligibleAir, _scenarioPlayer] call YSF_fwValidateLogisticsAsset;
private _busyVerdict = [_busyAir, _scenarioPlayer] call YSF_fwValidateLogisticsAsset;
private _eligibilityOk = (_ineligible # 3) && {_busy # 3}
    && {(_ineligibleResult param [2, ""]) isEqualTo "airdrop-unauthorized"}
    && {(_busyResult param [2, ""]) isEqualTo "airdrop-unauthorized"}
    && {!(_roleVerdict # 0)} && {(_roleVerdict # 1) isEqualTo "aircraft_not_logistics"}
    && {!(_busyVerdict # 0)} && {(_busyVerdict # 1) isEqualTo "duplicate_active_task"}
    && {(_ineligible # 1) isEqualTo (_ineligible # 0)}
    && {(_busy # 1) isEqualTo (_busy # 0)};
["fabricator.control.airdropEligibility", _eligibilityOk, format ["roleResult=%1|roleVerdict=%2|busyResult=%3|busyVerdict=%4", _ineligibleResult, _roleVerdict, _busyResult, _busyVerdict]] call _assert;

// Directly exercise the actual server-side capability guard with a guessed
// token. Client-originated public-boundary behavior is covered above by the
// real airdrop requests; this control makes no unobserved network claim.
private _registryCensusBefore = call TRIBUNAL_FAB_fnc_census;
private _registryAuditBefore = +(missionNamespace getVariable ["YSF_FW_REGISTRY_AUDIT", []]);
["client-guessed-token", "tribunal-forged", []] call YSF_fwSetEntry;
private _registryCensusAfter = call TRIBUNAL_FAB_fnc_census;
private _registryAuditAfter = +(missionNamespace getVariable ["YSF_FW_REGISTRY_AUDIT", []]);
private _registryAudit = [_registryAuditAfter - _registryAuditBefore, "set-entry", "token-rejected", "tribunal-forged"] call TRIBUNAL_FAB_fnc_auditMatches;
private _forgedPresent = (call YSF_fwEnsureRegistry) getOrDefault ["tribunal-forged", objNull];
private _registryForgeOk = (count _registryAudit) isEqualTo 1
    && {typeName _forgedPresent isNotEqualTo "HASHMAP"}
    && {!([_rogueAir, _scenarioPlayer] call YFU_fnc_fabricatorAirAssetAuthorized)}
    && {_registryCensusAfter isEqualTo _registryCensusBefore};
["fabricator.control.registryForge", _registryForgeOk, format ["receipt=%1|forgedType=%2|rogueAuthorized=%3", _registryAudit, typeName _forgedPresent, [_rogueAir, _scenarioPlayer] call YFU_fnc_fabricatorAirAssetAuthorized]] call _assert;

// Payloads that are not orders at all.
private _bad = ["malformed", 90] call TRIBUNAL_FAB_fnc_runPhase;
private _badResult = (_bad # 2) param [1, []];
private _big = ["oversized", 90] call TRIBUNAL_FAB_fnc_runPhase;
private _bigResult = (_big # 2) param [1, []];
private _malformedOk = (_bad # 3) && {(_big # 3)}
    && {(_badResult param [1, true]) isEqualTo false}
    && {(_badResult param [2, ""]) isEqualTo "malformed-quantity"}
    && {(_bigResult param [1, true]) isEqualTo false}
    && {(_bigResult param [2, ""]) isEqualTo "too-large"}
    && {(_bad # 1) isEqualTo (_bad # 0)}
    && {(_big # 1) isEqualTo (_big # 0)};
["fabricator.control.malformedRefused", _malformedOk, format ["malformed=%1|oversized=%2|badCensusHeld=%3|bigCensusHeld=%4", _badResult, _bigResult, (_bad # 1) isEqualTo (_bad # 0), (_big # 1) isEqualTo (_big # 0)]] call _assert;

// Discarding somebody else's transaction.
private _foreign = ["foreignDiscard", 90] call TRIBUNAL_FAB_fnc_runPhase;
private _foreignTx = [owner _scenarioPlayer, "tribunal-server-order"] call YFU_fnc_fabricatorTxId;
private _foreignAudit = [_foreign # 4, "discard", "owner-miss-rejected", _foreignTx] call TRIBUNAL_FAB_fnc_auditMatches;
private _foreignOk = (_foreign # 3)
    && {!isNull _victim}
    && {(netId _victim) in ((_foreign # 1) # 0)}
    && {(_foreign # 1) isEqualTo (_foreign # 0)}
    && {(count _foreignAudit) isEqualTo 1}
    && {((call YFU_fnc_fabricatorTransactions) getOrDefault [_serverTxId, createHashMap] getOrDefault ["created", []]) isEqualTo [netId _victim]};
["fabricator.control.foreignDiscardRefused", _foreignOk, format ["receipt=%1|victim=%2|alive=%3|txCreated=%4|censusHeld=%5", _foreignAudit, netId _victim, !isNull _victim, (call YFU_fnc_fabricatorTransactions) getOrDefault [_serverTxId, createHashMap] getOrDefault ["created", []], (_foreign # 1) isEqualTo (_foreign # 0)]] call _assert;

// Cancel a live owner transaction after its exact object is registered. The
// product must stop the worker before rollback; merely deleting the current
// ledger would allow the stalled script to resume and escape the transaction.
missionNamespace setVariable ["TRIBUNAL_FAB_ORIGINAL_CLONE", YOSHI_SPAWN_SAVED_ITEM_ACTION, false];
YOSHI_SPAWN_SAVED_ITEM_ACTION = {
    private _created = _this call (missionNamespace getVariable ["TRIBUNAL_FAB_ORIGINAL_CLONE", {}]);
    missionNamespace setVariable ["TRIBUNAL_FAB_CANCEL_CREATED", true, true];
    uiSleep 30;
    _created
};
private _activeDiscard = ["activeDiscard", 60] call TRIBUNAL_FAB_fnc_runPhase;
YOSHI_SPAWN_SAVED_ITEM_ACTION = missionNamespace getVariable ["TRIBUNAL_FAB_ORIGINAL_CLONE", {}];
missionNamespace setVariable ["TRIBUNAL_FAB_ORIGINAL_CLONE", nil, false];
missionNamespace setVariable ["TRIBUNAL_FAB_CANCEL_CREATED", nil, true];
private _activeDiscardTx = [owner _scenarioPlayer, "tribunal-cancel"] call YFU_fnc_fabricatorTxId;
private _activeDiscardTerminated = [_activeDiscard # 4, "discard", "worker-terminated", _activeDiscardTx] call TRIBUNAL_FAB_fnc_auditMatches;
private _activeDiscardAccepted = [_activeDiscard # 4, "discard", "accepted", _activeDiscardTx] call TRIBUNAL_FAB_fnc_auditMatches;
private _activeDiscardOk = (_activeDiscard # 3)
    && {((_activeDiscard # 2) param [1, false]) isEqualTo true}
    && {(count _activeDiscardTerminated) isEqualTo 1}
    && {(count _activeDiscardAccepted) isEqualTo 1}
    && {(_activeDiscard # 1) isEqualTo (_activeDiscard # 0)}
    && {([_activeDiscardTx] call YFU_fnc_fabricatorTxState) isEqualTo "finalized"};
["fabricator.control.activeDiscardAtomic", _activeDiscardOk, format ["created=%1|terminated=%2|accepted=%3|state=%4|censusBefore=%5|censusAfter=%6", (_activeDiscard # 2) param [1, false], _activeDiscardTerminated, _activeDiscardAccepted, [_activeDiscardTx] call YFU_fnc_fabricatorTxState, _activeDiscard # 0, _activeDiscard # 1]] call _assert;

// Stall after the creation callback has recorded the exact clone. This exercises
// the deadline without relying on Arma's uncaught-throw behavior, which can keep
// re-evaluating and flood the RPT rather than terminating the scheduled script.
missionNamespace setVariable ["TRIBUNAL_FAB_ORIGINAL_CLONE", YOSHI_SPAWN_SAVED_ITEM_ACTION, false];
YOSHI_SPAWN_SAVED_ITEM_ACTION = {
    private _created = _this call (missionNamespace getVariable ["TRIBUNAL_FAB_ORIGINAL_CLONE", {}]);
    uiSleep 30;
    _created
};
private _oldDeadline = YFU_FABRICATOR_BUILD_DEADLINE;
YFU_FABRICATOR_BUILD_DEADLINE = 2;
private _watchdog = ["watchdog", 90] call TRIBUNAL_FAB_fnc_runPhase;
YOSHI_SPAWN_SAVED_ITEM_ACTION = missionNamespace getVariable ["TRIBUNAL_FAB_ORIGINAL_CLONE", {}];
missionNamespace setVariable ["TRIBUNAL_FAB_ORIGINAL_CLONE", nil, false];
YFU_FABRICATOR_BUILD_DEADLINE = _oldDeadline;
private _watchdogResult = (_watchdog # 2) param [1, []];
private _watchdogReceipt = [_watchdog # 4, "watchdog", "worker-terminated", _watchdogResult param [0, ""]] call TRIBUNAL_FAB_fnc_auditMatches;
private _watchdogOk = (_watchdog # 3)
    && {(_watchdogResult param [1, true]) isEqualTo false}
    && {(_watchdogResult param [2, ""]) isEqualTo "abandoned"}
    && {(count _watchdogReceipt) isEqualTo 1}
    && {(_watchdog # 1) isEqualTo (_watchdog # 0)};
["fabricator.control.watchdogAtomic", _watchdogOk, format ["result=%1|receipt=%2|censusBefore=%3|censusAfter=%4", _watchdogResult, _watchdogReceipt, _watchdog # 0, _watchdog # 1]] call _assert;

private _oldTtl = YFU_FABRICATOR_RESULT_TTL;
YFU_FABRICATOR_RESULT_TTL = 3;
private _retirement = ["retirement", 60] call TRIBUNAL_FAB_fnc_runPhase;
YFU_FABRICATOR_RESULT_TTL = _oldTtl;
private _retirementResult = (_retirement # 2) param [1, []];
private _retirementTx = [owner _scenarioPlayer, "tribunal-retire"] call YFU_fnc_fabricatorTxId;
private _retirementKey = [_retirementTx] call YFU_fnc_fabricatorResultKey;
private _retirementDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.1;
    (([_retirementTx] call YFU_fnc_fabricatorTxState) isEqualTo "unknown" && {isNil {missionNamespace getVariable _retirementKey}})
    || {diag_tickTime > _retirementDeadline}
};
private _retired = (_retirementResult param [2, ""]) isEqualTo "malformed-quantity"
    && {([_retirementTx] call YFU_fnc_fabricatorTxState) isEqualTo "unknown"}
    && {isNil {missionNamespace getVariable _retirementKey}};
["fabricator.result.retirement", _retired, format ["result=%1|tx=%2|state=%3|resultPresent=%4", _retirementResult, _retirementTx, [_retirementTx] call YFU_fnc_fabricatorTxState, !isNil {missionNamespace getVariable _retirementKey}]] call _assert;

// A result is a handshake the server publishes and then withdraws, and only the
// server may undo its own work.
private _singleRequestId = _singleReport param [0, ""];
private _singleTxId = [owner _scenarioPlayer, _singleRequestId] call YFU_fnc_fabricatorTxId;
private _wasPublished = _singleResult isNotEqualTo [] && {(_singleResult param [0, ""]) isEqualTo _singleTxId};
// Finalizing is proven on a transaction whose lifetime this scenario controls,
// rather than on one the retirement timer may already have cleared.
private _discarded = [YFU_FABRICATOR_TOKEN, _serverTxId] call YFU_fnc_fabricatorFinalize;
uiSleep 0.5;
private _lifecycleOk = _singleRequestId isNotEqualTo ""
    && {_wasPublished}
    && {_discarded isEqualTo 1}
    && {isNull _victim}
    && {((call YFU_fnc_fabricatorTransactions) getOrDefault [_serverTxId, createHashMap] getOrDefault ["created", []]) isEqualTo []};
["fabricator.result.lifecycle", _lifecycleOk, format ["txId=%1|publishedAtTheTime=%2|finalized=%3|victimGone=%4|serverTx=%5", _singleTxId, _wasPublished, _discarded, isNull _victim, _serverTxId]] call _assert;

// Teardown.
private _packed = [];
{
    if (!isNull _x) then {_packed append (attachedObjects _x);};
} forEach _containers;
{
    if (!isNull _x) then {deleteVehicle _x;};
} forEach (_packed + _containers + _terrainBarriers + [_station, _stationFar, _heavy, _light, _oversize, _unregistered, _rogueAir, _ineligibleAir, _busyAir, _victim]);
{
    private _leftover = objectFromNetId _x;
    if (!isNull _leftover) then {deleteVehicle _leftover;};
} forEach ((call TRIBUNAL_FAB_fnc_census) # 0);
{deleteVehicle _x;} forEach [_storageLogic, _fabricatorLogic];
deleteGroup _logicGroup;
localNamespace setVariable ["YFU_MODULE_STORAGE_RECORDS", createHashMap];
localNamespace setVariable ["YFU_MODULE_FABRICATOR_RECORDS", createHashMap];
call YFU_fnc_rebuildModuleRegistration;
missionNamespace setVariable ["YOSHI_VIRTUAL_STORAGE", nil, true];
missionNamespace setVariable ["YOSHI_FABRICATOR", nil, true];
missionNamespace setVariable ["TRIBUNAL_FAB_FIXTURE", nil, true];
missionNamespace setVariable ["TRIBUNAL_FAB_GO", nil, true];
missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_SETUP", nil, true];
missionNamespace setVariable ["TRIBUNAL_FAB_TERRAIN_READY", nil, true];

// Explicitly retire every retained handshake and prove both maps and result
// variables are gone. The production TTL remains 120 seconds; teardown need not
// keep a completed Tribunal run alive merely to observe it.
private _cleanupTxIds = keys (call YFU_fnc_fabricatorTransactions);
{[YFU_FABRICATOR_TOKEN, _x, 0] call YFU_fnc_fabricatorRetire;} forEach _cleanupTxIds;
private _registryCleanup = call YSF_fwEnsureRegistry;
_registryCleanup deleteAt "tribunal-strike";
_registryCleanup deleteAt "tribunal-busy-logi";
[YSF_FW_REGISTRY_TOKEN, _registryCleanup] call YSF_fwCommitRegistry;
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {
    uiSleep 0.1;
    ((keys (call YFU_fnc_fabricatorTransactions)) isEqualTo []) || {diag_tickTime > _cleanupDeadline}
};

private _finalCensus = call TRIBUNAL_FAB_fnc_census;
private _resultKeysGone = (_cleanupTxIds findIf {
    !isNil {missionNamespace getVariable ([_x] call YFU_fnc_fabricatorResultKey)}
}) < 0;
private _cleanupOk = (_finalCensus # 0) isEqualTo []
    && {(_finalCensus # 1) isEqualTo 0}
    && {isNull _station} && {isNull _heavy} && {isNull _oversize}
    && {isNil "YOSHI_FABRICATOR"}
    && {(keys (call YFU_fnc_fabricatorTransactions)) isEqualTo []}
    && {_resultKeysGone}
    && {typeName (_registryCleanup getOrDefault ["tribunal-strike", objNull]) isNotEqualTo "HASHMAP"};
["fabricator.cleanup", _cleanupOk, format ["census=%1|stationGone=%2|logicsCleared=%3|txRemaining=%4|resultKeysGone=%5|registryKeys=%6", _finalCensus, isNull _station, isNil "YOSHI_FABRICATOR", keys (call YFU_fnc_fabricatorTransactions), _resultKeysGone, keys _registryCleanup]] call _assert;
YFU_fnc_fabricatorPublishResult = TRIBUNAL_FAB_ORIGINAL_PUBLISH;
TRIBUNAL_FAB_ORIGINAL_PUBLISH = nil;
missionNamespace setVariable ["TRIBUNAL_FAB_MASS_READY", nil, true];
missionNamespace setVariable ["YFU_fabricatorAudit", nil, false];
missionNamespace setVariable ["YSF_FW_REGISTRY_AUDIT", nil, false];
missionNamespace setVariable ["TRIBUNAL_FAB_SERVER_DONE", _token, true];
''',
    client_expected_by_identity={identity: CLIENT_EXPECTED for identity in OBSERVER_IDENTITIES},
    client_sqf=CLIENT_SQF,
    client_sqf_by_identity={identity: CLIENT_SQF for identity in OBSERVER_IDENTITIES},
    metadata={
        "product": "field-utilities",
        "feature": "fabricator",
        # Without this the player respawns at the map origin, which on Stratis is
        # open water: every fixture and every delivery would be built over the
        # sea. Matches the counter-battery and fixed-wing scenarios.
        "respawn_on_start": "0",
        "observer_identities": ",".join(OBSERVER_IDENTITIES),
        "future_client_isolation": "client-b/JIP must observe server-owned deliveries and the published catalogue without receiving client-a queue state",
    },
    evidence_contract=EVIDENCE_CONTRACT,
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A player at a registered fabrication station can order copies of mission-maker virtual storage; the server validates the catalogue and player presence and is the only machine that creates anything. Copies preserve stored weapons, magazines, items and backpacks. In the proven terrain fixtures, an authentic two-object packed order produces one server-local container that settles within 2 m of its bounded target. In the tested eight-light-crate matrix, the order publishes two distinct server-local four-crate pallets only after both bounded targets exist; if the later target is unavailable, every transaction object remains hidden and the order refuses without publication. For the tested shoreline/all-water pair, an authentic one-item order publishes its exact hidden clone at bounded moderate non-water land and hands that identity to ACE carry, while the matched all-water order refuses without publication or leakage. Immediately before publication, a heavy single clone is visible, unattached, server-local, capped at mass 200, and exempt from the ACE cargo-inclusive carry-weight gate; client-a starts ACE carry on that exact clone. Registration is an unlimited template source, and incomplete orders refuse whole without leaks.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="Baseline fabrication ran entirely on the ordering client with no server validation, reported partial orders as success, and ignored its declared multi-container cap. Coverage is permanent only after orders became server-authoritative, owner-bound and atomic, with runtime adversarial controls for authority, replay, cancellation, terrain refusal, and cleanup. The exact single publication boundary now preserves physical mass and the promised ACE carry handoff despite cargo-inclusive ACE weight. Terrain, single-item, and multi-container continuations use authentic terminal orders, independent terrain and target observations, matched recovery/refusal controls, exact transaction census, and continuous physical settling rather than treating helper returns or object creation as delivery success.",
        dependencies=(
            "ACE 3.21 interaction registration",
            "Arma editor module logic synchronization",
            "one independently authenticated client",
        ),
        evidence_types=frozenset({
            "module-registration", "server-authority", "transaction-identity", "adversarial-control", "exact-netid",
            "cargo-inventory", "pre-publication-mass", "mass-replication", "ace-carry-identity",
            "terrain-gradient", "terrain-shoreline", "terrain-all-water", "single-item-publication", "terrain-severe-recovery", "terrain-severe-refusal", "obstruction-ring", "multi-container-allocation", "distinct-target-reservation", "physical-settling",
            "mission-wide-census", "replication", "cleanup",
        }),
        locality_requirements="Client-a owns the terminal, queue and request, declares its own unit by net id, and moves that real player to each terrain fixture only after a server signal. The dedicated server owns the station, obstruction fixtures, and every created, packed, placed, finalized and discarded object. It snapshots the exact clone at the real pre-publication boundary; client-a proves the real post-publication ACE carry attachment on the same net id. One authenticated client is the proof boundary: the foreign-discard control uses a server-owned transaction, so the client-b case remains unproven.",
    ),
)

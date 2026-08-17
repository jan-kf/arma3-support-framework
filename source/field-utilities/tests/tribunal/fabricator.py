"""Permanent Tier 3 contract for Field Utilities Fabricator and Virtual Storage."""

from tribunal.runner.model import Scenario, ScenarioReview


OBSERVER_IDENTITIES = ("client-a",)

CLIENT_EXPECTED = frozenset({
    "fabricator.client.stationsRegistered",
    "fabricator.client.inventoryGate",
    "fabricator.client.orderAccepted",
    "fabricator.client.noLocalCreation",
    "fabricator.client.deliveryReplicated",
    "fabricator.client.rejectionSurfaced",
})


CLIENT_SQF = r'''
private _fixtureDeadline = diag_tickTime + 240;
private _fixture = [];
waitUntil {
    uiSleep 0.1;
    _fixture = missionNamespace getVariable ["TRIBUNAL_FAB_FIXTURE", []];
    !(_fixture isEqualTo []) || {diag_tickTime > _fixtureDeadline}
};
_fixture params [["_fixtureToken", ""], ["_stationId", ""], ["_stationFarId", ""], ["_heavyId", ""], ["_lightId", ""], ["_oversizeId", ""], ["_unregisteredId", ""]];
private _station = objectFromNetId _stationId;

// ACE keeps object actions in an object variable whose name is an ACE internal.
// Walk every variable the station carries rather than hard-coding one, so an
// ACE rename fails this assertion loudly instead of silently finding nothing.
// ACE 3.21 keeps object actions in neither an object variable nor the
// class-keyed ActNamespace that the Bridge Builder scenario reads, so this
// scenario deliberately does not claim to have found the action inside ACE.
// What it does prove is that the client resolves the registered stations from
// the replicated module logic and registers each of them exactly once, with
// ACE's registration API present. ACE-side presence of the action is recorded
// as unproven in the review rather than asserted from a guess.
private _syncDeadline = diag_tickTime + 60;
private _clientStations = [];
waitUntil {
    uiSleep 0.25;
    _clientStations = if (isNil "YOSHI_FABRICATOR") then {[]} else {synchronizedObjects YOSHI_FABRICATOR};
    (count _clientStations) isEqualTo 2 || {diag_tickTime > _syncDeadline}
};
private _registry = uiNamespace getVariable ["YFU_registered_fabricator_actions", []];
call YFU_registerFabricatorMenuActions;
uiSleep 0.5;
private _registryAfter = uiNamespace getVariable ["YFU_registered_fabricator_actions", []];
private _stationIds = _clientStations apply {netId _x};
private _registrationOk = !isNull _station
    && {(count _clientStations) isEqualTo 2}
    && {_stationId in _stationIds}
    && {_stationFarId in _stationIds}
    && {_registryAfter isEqualTo _registry}
    && {(_registryAfter select {_x isEqualTo _stationId}) isEqualTo [_stationId]}
    && {!isNil "ace_interact_menu_fnc_addActionToObject"};
["fabricator.client.stationsRegistered", _registrationOk, format ["station=%1|clientStations=%2|registry=%3|idempotent=%4|aceApi=%5|aceVersion=%6", _stationId, _stationIds, _registryAfter, _registryAfter isEqualTo _registry, !isNil "ace_interact_menu_fnc_addActionToObject", getText (configFile >> "CfgPatches" >> "ace_interact_menu" >> "versionStr")]] call _assert;

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
    private _report = [_request param [0, ""], _result, _success];
    missionNamespace setVariable ["TRIBUNAL_FAB_REPORT", _report, true];
    missionNamespace setVariable ["TRIBUNAL_FAB_DONE", _phase, true];
    _report
};

private _singleReport = ["single", _station, [[_heavyId, 1]], 60] call TRIBUNAL_FAB_fnc_order;
private _singleResult = _singleReport param [1, []];
private _clone = objectFromNetId (_singleResult param [3, ""]);
["fabricator.client.orderAccepted", (_singleReport param [2, false]) isEqualTo true && {(_singleResult param [2, ""]) isEqualTo "single"}, format ["report=%1", _singleReport]] call _assert;

// The terminal asked; it did not build. The delivered object is replicated here
// but owned by the server.
private _noLocalOk = !isNull _clone && {!(local _clone)} && {typeOf _clone isEqualTo "Box_NATO_Ammo_F"};
["fabricator.client.noLocalCreation", _noLocalOk, format ["clone=%1|localHere=%2|type=%3", netId _clone, local _clone, typeOf _clone]] call _assert;

private _deliveryOk = !isNull _clone
    && {(_clone distance player) < 12}
    && {(getWeaponCargo _clone) isEqualTo [["arifle_MX_F"], [3]]}
    && {(getItemCargo _clone) isEqualTo [["FirstAidKit"], [5]]};
["fabricator.client.deliveryReplicated", _deliveryOk, format ["dist=%1|weapons=%2|items=%3", _clone distance player, getWeaponCargo _clone, getItemCargo _clone]] call _assert;

["multi", _station, [[_lightId, 2]], 90] call TRIBUNAL_FAB_fnc_order;

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

private _serverDeadline = diag_tickTime + 60;
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
        "fabricator.fidelity.cargo",
        "fabricator.catalogue.notConsumed",
        "fabricator.delivery.packed",
        "fabricator.control.unpackableAtomic",
        "fabricator.control.unregistered",
        "fabricator.control.outOfRange",
        "fabricator.control.noStorage",
        "fabricator.result.lifecycle",
        "fabricator.cleanup",
    }),
    client_expected=CLIENT_EXPECTED,
    server_sqf=r'''
// The whole fixture is anchored to where the player is standing, so a position
// sampled the instant the player object appears is not good enough: the player
// is still being placed and the station would be built kilometres away. Require
// the position to hold still before anchoring anything to it.
private _scenarioPlayer = objNull;
private _lastPos = [0, 0, 0];
private _steadySince = 0;
private _playerDeadline = diag_tickTime + 120;
waitUntil {
    uiSleep 0.25;
    _scenarioPlayer = allPlayers param [0, objNull];
    private _settled = false;
    if (!isNull _scenarioPlayer && {alive _scenarioPlayer}) then {
        private _pos = getPosATL _scenarioPlayer;
        private _placed = (_pos select 0) > 100 && {(_pos select 1) > 100};
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

private _base = getPosATL _scenarioPlayer;

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
    [count _all, count _staged]
};

private _fixture = [_token, netId _station, netId _stationFar, netId _heavy, netId _light, netId _oversize, netId _unregistered];
missionNamespace setVariable ["TRIBUNAL_FAB_FIXTURE", _fixture, true];

private _catalogue = synchronizedObjects _storageLogic;
private _stations = synchronizedObjects _fabricatorLogic;
private _fixtureOk = !isNull _scenarioPlayer
    && {!isNull _station} && {!isNull _heavy} && {!isNull _light} && {!isNull _oversize}
    && {(count _catalogue) isEqualTo 3}
    && {(count _stations) isEqualTo 2}
    && {!(_unregistered in _catalogue)}
    && {!isNil "YOSHI_VIRTUAL_STORAGE"} && {!isNil "YOSHI_FABRICATOR"}
    && {_heavySourceMass > 200}
    && {(_scenarioPlayer distance _station) < YFU_FABRICATOR_ORDER_RANGE}
    && {(_scenarioPlayer distance _stationFar) > YFU_FABRICATOR_ORDER_RANGE};
["fabricator.fixture", _fixtureOk, format ["fixture=%1|catalogue=%2|stations=%3|sourceMass=%4|stationDist=%5|farDist=%6", _fixture, count _catalogue, count _stations, _heavySourceMass, _scenarioPlayer distance _station, _scenarioPlayer distance _stationFar]] call _assert;

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
    missionNamespace setVariable ["TRIBUNAL_FAB_GO", _phase, true];
    private _doneDeadline = diag_tickTime + _timeout;
    waitUntil {
        uiSleep 0.1;
        ((missionNamespace getVariable ["TRIBUNAL_FAB_DONE", ""]) isEqualTo _phase) || {diag_tickTime > _doneDeadline}
    };
    private _after = call TRIBUNAL_FAB_fnc_census;
    private _report = missionNamespace getVariable ["TRIBUNAL_FAB_REPORT", []];
    [_before, _after, _report, ((missionNamespace getVariable ["TRIBUNAL_FAB_DONE", ""]) isEqualTo _phase)]
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
["fabricator.authority.serverOwned", _authorityOk, format ["result=%1|clone=%2|localOnServer=%3|owner=%4|type=%5|dist=%6", _singleResult, netId _clone, local _clone, owner _clone, typeOf _clone, _clone distance _scenarioPlayer]] call _assert;

private _cloneCargo = [getWeaponCargo _clone, getMagazineCargo _clone, getItemCargo _clone, getBackpackCargo _clone];
["fabricator.fidelity.cargo", _cloneCargo isEqualTo _heavySourceCargo, format ["clone=%1|source=%2", _cloneCargo, _heavySourceCargo]] call _assert;

// Fabricated crates are capped so a player can still carry the delivery. This is
// intended usability behavior, not mass fidelity.
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

// Phase 3: an order containing something no container can hold. Atomic means the
// whole order is refused and nothing at all survives, anywhere on the map.
private _unpackable = ["unpackable", 120] call TRIBUNAL_FAB_fnc_runPhase;
private _unpackableReport = _unpackable # 2;
private _unpackableResult = _unpackableReport param [1, []];
private _atomicOk = (_unpackable # 3)
    && {(_unpackableResult param [1, true]) isEqualTo false}
    && {(_unpackableResult param [2, ""]) isEqualTo "unpackable"}
    && {(_unpackable # 1) isEqualTo (_unpackable # 0)}
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
missionNamespace setVariable ["YOSHI_VIRTUAL_STORAGE", objNull, true];
uiSleep 0.5;
private _noStorage = ["noStorage", 90] call TRIBUNAL_FAB_fnc_runPhase;
private _noStorageReport = _noStorage # 2;
private _noStorageResult = _noStorageReport param [1, []];
private _noStorageOk = (_noStorage # 3)
    && {(_noStorageResult param [1, true]) isEqualTo false}
    && {(_noStorageResult param [2, ""]) isEqualTo "no-storage"}
    && {(_noStorage # 1) isEqualTo (_noStorage # 0)};
["fabricator.control.noStorage", _noStorageOk, format ["result=%1|censusBefore=%2|censusAfter=%3", _noStorageResult, _noStorage # 0, _noStorage # 1]] call _assert;
missionNamespace setVariable ["YOSHI_VIRTUAL_STORAGE", _storageLogic, true];

// A result is a handshake the server publishes and then withdraws, and only the
// server may undo its own work.
private _singleRequestId = _singleReport param [0, ""];
private _resultKey = [_singleRequestId] call YFU_fnc_fabricatorResultKey;
private _resultStillPublished = !isNil {missionNamespace getVariable _resultKey};
private _discarded = [_singleRequestId] call YFU_fnc_fabricatorDiscardOrder;
uiSleep 0.5;
private _lifecycleOk = _singleRequestId isNotEqualTo ""
    && {_resultStillPublished}
    && {_discarded isEqualTo 1}
    && {isNull _clone};
["fabricator.result.lifecycle", _lifecycleOk, format ["requestId=%1|published=%2|discarded=%3|cloneGone=%4", _singleRequestId, _resultStillPublished, _discarded, isNull _clone]] call _assert;

// Teardown.
private _packed = [];
{
    if (!isNull _x) then {_packed append (attachedObjects _x);};
} forEach _containers;
{
    if (!isNull _x) then {deleteVehicle _x;};
} forEach (_packed + _containers + [_station, _stationFar, _heavy, _light, _oversize, _unregistered]);
{deleteVehicle _x;} forEach [_storageLogic, _fabricatorLogic];
deleteGroup _logicGroup;
missionNamespace setVariable ["YOSHI_VIRTUAL_STORAGE", nil, true];
missionNamespace setVariable ["YOSHI_FABRICATOR", nil, true];
missionNamespace setVariable ["TRIBUNAL_FAB_FIXTURE", nil, true];
missionNamespace setVariable ["TRIBUNAL_FAB_GO", nil, true];
uiSleep 1;

private _finalCensus = call TRIBUNAL_FAB_fnc_census;
private _cleanupOk = (_finalCensus # 0) isEqualTo 0
    && {(_finalCensus # 1) isEqualTo 0}
    && {isNull _station} && {isNull _heavy} && {isNull _oversize}
    && {isNil "YOSHI_FABRICATOR"};
["fabricator.cleanup", _cleanupOk, format ["census=%1|stationGone=%2|logicsCleared=%3", _finalCensus, isNull _station, isNil "YOSHI_FABRICATOR"]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FAB_SERVER_DONE", _token, true];
''',
    client_expected_by_identity={identity: CLIENT_EXPECTED for identity in OBSERVER_IDENTITIES},
    client_sqf=CLIENT_SQF,
    client_sqf_by_identity={identity: CLIENT_SQF for identity in OBSERVER_IDENTITIES},
    metadata={
        "product": "field-utilities",
        "feature": "fabricator",
        "observer_identities": ",".join(OBSERVER_IDENTITIES),
        "future_client_isolation": "client-b/JIP must observe server-owned deliveries and the published catalogue without receiving client-a queue state",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A player at a registered fabrication station can order copies of the objects a mission maker registered as virtual storage; the server validates the order against that catalogue and the player's presence at the station, and is the only machine that creates anything. A copy carries the source's stored weapons, magazines, items and backpacks, and delivery crates are capped to a carryable mass. Registration is a template source and is never consumed. An order that cannot be produced in full - because it names something unregistered, is placed away from its station, has no catalogue, or contains something no container can hold - is refused whole and leaves nothing behind.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="Baseline fabrication ran entirely on the ordering client with no server validation, and reported success for orders it had only partly filled while orphaning the remainder under the map. Coverage is permanent only after orders became server-authoritative and atomic, per the recorded product decisions.",
        dependencies=(
            "ACE 3.21 interaction registration",
            "Arma editor module logic synchronization",
            "one independently authenticated client",
        ),
        evidence_types=frozenset({
            "module-registration", "registered-action-statement", "server-authority", "exact-netid",
            "cargo-inventory", "object-mass", "mission-wide-census", "replication", "cleanup",
        }),
        locality_requirements="Client-a owns the terminal, the queue and the request; the dedicated server exclusively validates orders and creates, packs, places and discards every fabricated object. This proves one-client replication only, not client-b or JIP.",
    ),
)

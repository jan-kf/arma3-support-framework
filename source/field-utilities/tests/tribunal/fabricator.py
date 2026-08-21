"""Permanent Tier 3 contract for Field Utilities Fabricator and Virtual Storage."""

from tribunal.runner.model import Scenario, ScenarioReview


OBSERVER_IDENTITIES = ("client-a",)

CLIENT_EXPECTED = frozenset({
    "fabricator.client.modulesReplicated",
    "fabricator.client.inventoryGate",
    "fabricator.client.orderAccepted",
    "fabricator.client.noLocalCreation",
    "fabricator.client.deliveryReplicated",
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

// Declare which unit this identity actually controls, rather than letting the
// server guess from allPlayers ordering. A second client must not silently
// change which player the fixture is built around.
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
private _lastPos = [0, 0, 0];
private _steadySince = 0;
private _playerDeadline = diag_tickTime + 180;
waitUntil {
    uiSleep 0.25;
    // The observer names its own unit; allPlayers ordering is not an identity.
    private _declared = missionNamespace getVariable ["TRIBUNAL_FAB_PLAYER_client-a", ""];
    _scenarioPlayer = if (_declared isEqualTo "") then {objNull} else {objectFromNetId _declared};
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
["fabricator.authority.serverOwned", _authorityOk, format ["result=%1|clone=%2|localOnServer=%3|owner=%4|type=%5|dist=%6|playerOwner=%7|clientOwner=%8|txGuess=%9|serverResult=%10|knownTx=%11", _singleResult, netId _clone, local _clone, owner _clone, typeOf _clone, _clone distance _scenarioPlayer, owner _scenarioPlayer, _clientOwnerSeen, _serverTxGuess, _serverResult, _serverKnownTx]] call _assert;

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
} forEach (_packed + _containers + [_station, _stationFar, _heavy, _light, _oversize, _unregistered, _rogueAir, _ineligibleAir, _busyAir, _victim]);
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
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A player at a registered fabrication station can order copies of the objects a mission maker registered as virtual storage; the server validates the order against that catalogue and the player's presence at the station, and is the only machine that creates anything. A copy carries the source's stored weapons, magazines, items and backpacks. Registration is a template source and is never consumed. An order that cannot be produced in full - because it names something unregistered, is placed away from its station, has no catalogue, or contains something no container can hold - is refused whole and leaves nothing behind.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="Baseline fabrication ran entirely on the ordering client with no server validation, and reported success for orders it had only partly filled while orphaning the remainder under the map. Coverage is permanent only after orders became server-authoritative, owner-bound and atomic, with runtime adversarial controls for worker bypass, duplicate request, unauthorized airdrop, malformed orders and foreign discard.",
        dependencies=(
            "ACE 3.21 interaction registration",
            "Arma editor module logic synchronization",
            "one independently authenticated client",
        ),
        evidence_types=frozenset({
            "module-registration", "server-authority", "transaction-identity", "adversarial-control", "exact-netid",
            "cargo-inventory", "mission-wide-census", "replication", "cleanup",
        }),
        locality_requirements="Client-a owns the terminal, the queue and the request, and declares its own unit by net id rather than relying on allPlayers ordering; the dedicated server exclusively validates orders and creates, packs, places, finalizes and discards every fabricated object. One authenticated client is the proof boundary: the foreign-discard control uses a server-owned transaction, so the client-b case remains unproven.",
    ),
)

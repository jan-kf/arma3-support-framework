"""Authentic typed-Eden registration coverage for Field Utilities Fabricator."""

from tribunal.runner.model import MissionEntity, MissionSync, Scenario, ScenarioReview


SERVER_SQF = r'''
private _catalogueA = missionNamespace getVariable ["TRIBUNAL_YFU_STORAGE_A", objNull];
private _catalogueB = missionNamespace getVariable ["TRIBUNAL_YFU_STORAGE_B", objNull];
private _stationA = missionNamespace getVariable ["TRIBUNAL_YFU_STATION_A", objNull];
private _stationB = missionNamespace getVariable ["TRIBUNAL_YFU_STATION_B", objNull];
private _expectedCatalogue = [_catalogueA, _catalogueB];
private _expectedStations = [_stationA, _stationB];

private _auditDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (count (localNamespace getVariable ["YFU_MODULE_DISPATCH_AUDIT", []])) >= 4 || {diag_tickTime > _auditDeadline}};
private _audit = localNamespace getVariable ["YFU_MODULE_DISPATCH_AUDIT", []];
private _accepted = _audit select {_x # 7};
private _native = _accepted select {(_x # 8) isEqualTo "accepted_native"};
private _moduleIds = _native apply {_x # 2};
private _modules = _moduleIds apply {objectFromNetId _x};
private _dispatchOk = (count _native) isEqualTo 4
    && {({_x # 0 isEqualTo "FieldUtils_Virtual_Storage_Module"} count _native) isEqualTo 2}
    && {({_x # 0 isEqualTo "FieldUtils_Fabricator_Module"} count _native) isEqualTo 2}
    && {(_native findIf {!(_x # 3) || {!(_x # 4)} || {(_x # 5) isNotEqualTo 2} || {(_x # 6) > 2} || {(count (_x # 9)) isNotEqualTo 1}}) < 0};
["fabricator.module.dispatch", _dispatchOk, format ["audit=%1|modules=%2", _audit, _modules apply {[typeOf _x, netId _x, local _x, owner _x]}]] call _assert;

private _catalogue = call YFU_fnc_fabricatorCatalogue;
private _stations = call YFU_fnc_fabricatorStations;
private _sameObjects = {
    params ["_actual", "_expected"];
    (count _actual) isEqualTo count _expected && {(_expected findIf {!(_x in _actual)}) < 0}
};
private _aggregateOk = [_catalogue, _expectedCatalogue] call _sameObjects
    && {[_stations, _expectedStations] call _sameObjects}
    && {missionNamespace getVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", false]};
["fabricator.module.aggregate", _aggregateOk, format ["catalogue=%1|stations=%2|inventory=%3", _catalogue apply {[vehicleVarName _x, netId _x]}, _stations apply {[vehicleVarName _x, netId _x]}, missionNamespace getVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", "unset"]]] call _assert;

private _retainedOk = (_modules findIf {isNull _x || {!local _x} || {owner _x isNotEqualTo 2}}) < 0
    && {(_modules findIf {(count synchronizedObjects _x) isNotEqualTo 1}) < 0};
["fabricator.module.retained", _retainedOk, format ["modules=%1|sync=%2", _modules apply {[typeOf _x, netId _x]}, _modules apply {(synchronizedObjects _x) apply {[vehicleVarName _x, netId _x]}}]] call _assert;

missionNamespace setVariable ["TRIBUNAL_YFU_MODULE_READY", [_token, _catalogue apply {netId _x}, _stations apply {netId _x}], true];
private _initialClientDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_YFU_MODULE_INITIAL_CLIENT_DONE", ""]) isEqualTo _token
        || {diag_tickTime > _initialClientDeadline}
};
private _fabricatorModules = _modules select {typeOf _x isEqualTo "FieldUtils_Fabricator_Module"};
private _toggleCrate = _catalogueB;
private _toggleStation = _stationA;
// Authentic configured dispatch above proves the module's default enabled
// handoff. Change only its published switch here to isolate the registered
// ACE condition without manually invoking or impersonating a module setter.
missionNamespace setVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", false, true];
private _disabledState = !(missionNamespace getVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", true]);
missionNamespace setVariable ["TRIBUNAL_YFU_INVENTORY_PHASE", [_token, "disabled", netId _toggleCrate, netId _toggleStation, _disabledState], true];
private _disabledDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    private _ack = missionNamespace getVariable ["TRIBUNAL_YFU_INVENTORY_CLIENT_PHASE", []];
    ((_ack param [0, ""]) isEqualTo _token && {(_ack param [1, ""]) isEqualTo "disabled"})
        || {diag_tickTime > _disabledDeadline}
};
private _disabledAck = missionNamespace getVariable ["TRIBUNAL_YFU_INVENTORY_CLIENT_PHASE", []];
missionNamespace setVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", true, true];
private _enabledState = missionNamespace getVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", false];
missionNamespace setVariable ["TRIBUNAL_YFU_INVENTORY_PHASE", [_token, "enabled", netId _toggleCrate, netId _toggleStation, _enabledState], true];
private _enabledDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    private _ack = missionNamespace getVariable ["TRIBUNAL_YFU_INVENTORY_CLIENT_PHASE", []];
    ((_ack param [0, ""]) isEqualTo _token && {(_ack param [1, ""]) isEqualTo "enabled"})
        || {diag_tickTime > _enabledDeadline}
};
private _enabledAck = missionNamespace getVariable ["TRIBUNAL_YFU_INVENTORY_CLIENT_PHASE", []];
private _toggleOk = (count _fabricatorModules) isEqualTo 2
    && {_disabledState}
    && {(_disabledAck param [2, false])}
    && {_enabledState}
    && {(_enabledAck param [2, false])};
["fabricator.module.inventoryToggle", _toggleOk, format ["modules=%1|disabled=%2|disabledAck=%3|enabled=%4|enabledAck=%5|crate=%6|station=%7", _fabricatorModules apply {[netId _x, _x getVariable ["Fabricator_Module_EnableLocalArsenal", "unset"]]}, _disabledState, _disabledAck, _enabledState, _enabledAck, netId _toggleCrate, netId _toggleStation]] call _assert;
private _negativeDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (count ((localNamespace getVariable ["YFU_MODULE_DISPATCH_AUDIT", []]) select {(_x # 8) isEqualTo "remote_request"})) >= 2 || {diag_tickTime > _negativeDeadline}};
private _finalAudit = localNamespace getVariable ["YFU_MODULE_DISPATCH_AUDIT", []];
private _rejected = _finalAudit select {(_x # 8) isEqualTo "remote_request"};
private _privateCatalogue = localNamespace getVariable ["YFU_MODULE_CATALOGUE", []];
private _privateStations = localNamespace getVariable ["YFU_MODULE_STATIONS", []];
private _authorityOk = (count _rejected) isEqualTo 2
    && {(_rejected findIf {(_x # 6) <= 2 || {_x # 7}}) < 0}
    && {[_privateCatalogue, _expectedCatalogue] call _sameObjects}
    && {[_privateStations, _expectedStations] call _sameObjects};
["fabricator.module.authority", _authorityOk, format ["rejected=%1|privateCatalogue=%2|privateStations=%3|publicCatalogue=%4|publicStations=%5", _rejected, _privateCatalogue apply {netId _x}, _privateStations apply {netId _x}, (missionNamespace getVariable ["YFU_VIRTUAL_STORAGE_OBJECTS", []]) apply {netId _x}, (missionNamespace getVariable ["YFU_FABRICATOR_STATIONS", []]) apply {netId _x}]] call _assert;

missionNamespace setVariable ["TRIBUNAL_YFU_MODULE_RESULT", [_token, _privateCatalogue apply {netId _x}, _privateStations apply {netId _x}, _moduleIds], true];
private _clientDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["TRIBUNAL_YFU_MODULE_CLIENT_DONE", ""]) isEqualTo _token || {diag_tickTime > _clientDeadline}};
private _all = _expectedCatalogue + _expectedStations + _modules;
{if (!isNull _x) then {deleteVehicle _x;};} forEach _all;
localNamespace setVariable ["YFU_MODULE_STORAGE_RECORDS", createHashMap];
localNamespace setVariable ["YFU_MODULE_FABRICATOR_RECORDS", createHashMap];
call YFU_fnc_rebuildModuleRegistration;
private _cleanupDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (_all findIf {!isNull _x}) < 0 || {diag_tickTime > _cleanupDeadline}};
private _cleanupOk = (missionNamespace getVariable ["TRIBUNAL_YFU_MODULE_CLIENT_DONE", ""]) isEqualTo _token
    && {(_all findIf {!isNull _x}) < 0}
    && {(localNamespace getVariable ["YFU_MODULE_CATALOGUE", []]) isEqualTo []}
    && {(localNamespace getVariable ["YFU_MODULE_STATIONS", []]) isEqualTo []};
["fabricator.module.cleanup", _cleanupOk, format ["client=%1|remaining=%2|catalogue=%3|stations=%4", missionNamespace getVariable ["TRIBUNAL_YFU_MODULE_CLIENT_DONE", ""], _all select {!isNull _x}, localNamespace getVariable ["YFU_MODULE_CATALOGUE", []], localNamespace getVariable ["YFU_MODULE_STATIONS", []]]] call _assert;
'''


CLIENT_SQF = r'''
private _ready = [];
private _deadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; _ready = missionNamespace getVariable ["TRIBUNAL_YFU_MODULE_READY", []]; (count _ready) isEqualTo 3 || {diag_tickTime > _deadline}};
private _catalogueIds = _ready param [1, []];
private _stationIds = _ready param [2, []];
private _catalogue = missionNamespace getVariable ["YFU_VIRTUAL_STORAGE_OBJECTS", []];
private _stations = missionNamespace getVariable ["YFU_FABRICATOR_STATIONS", []];
private _mirrorOk = (_catalogue apply {netId _x}) isEqualTo _catalogueIds
    && {(_stations apply {netId _x}) isEqualTo _stationIds}
    && {missionNamespace getVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", false]};
["fabricator.module.clientMirrors", _mirrorOk, format ["catalogue=%1|stations=%2|inventory=%3", _catalogue apply {netId _x}, _stations apply {netId _x}, missionNamespace getVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", "unset"]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_YFU_MODULE_INITIAL_CLIENT_DONE", _token, true];

private _findAction = {
    params ["_nodes", "_wanted"];
    private _found = [];
    {
        _x params ["_data", "_children"];
        if ((_data param [0, ""]) isEqualTo _wanted) exitWith {_found = _data};
        private _child = [_children, _wanted] call _findAction;
        if (_child isNotEqualTo []) exitWith {_found = _child};
    } forEach _nodes;
    _found
};
private _collectActive = {
    params ["_target", "_data"];
    if (isNull _target || {_data isEqualTo []}) exitWith {[]};
    ace_interact_menu_objectActionList = [];
    [_target, [_data, []], [], player distance _target] call ace_interact_menu_fnc_collectActiveActionTree
};
private _phase = [];
private _disabledDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    _phase = missionNamespace getVariable ["TRIBUNAL_YFU_INVENTORY_PHASE", []];
    ((_phase param [0, ""]) isEqualTo _token
        && {(_phase param [1, ""]) isEqualTo "disabled"}
        && {!(missionNamespace getVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", true])})
        || {diag_tickTime > _disabledDeadline}
};
private _crate = objectFromNetId (_phase param [2, ""]);
private _station = objectFromNetId (_phase param [3, ""]);
private _objectsDeadline = diag_tickTime + 10;
waitUntil {uiSleep 0.05; (!isNull _crate && {!isNull _station}) || {diag_tickTime > _objectsDeadline}};
private _originalASL = getPosASL player;
private _originalSimulation = simulationEnabled player;
player enableSimulation false;
if (!isNull _crate) then {player setPosASL ((getPosASL _crate) vectorAdd [0, 2, 0]);};
private _action = [];
private _actionDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    if (!isNull _crate) then {
        [_crate] call ace_interact_menu_fnc_compileMenu;
        private _class = typeOf _crate call ace_common_fnc_getConfigName;
        _action = [ace_interact_menu_ActNamespace getOrDefault [_class, []], "zenInventoryActions"] call _findAction;
    };
    _action isNotEqualTo [] || {diag_tickTime > _actionDeadline}
};
private _disabledTree = [_crate, _action] call _collectActive;
private _disabledOk = (_phase param [4, false])
    && {!isNull _crate}
    && {!isNull _station}
    && {_crate distance _station < 20}
    && {_action isNotEqualTo []}
    && {(_action param [1, ""]) isEqualTo "Open Virtual Inventory"}
    && {_disabledTree isEqualTo []};
["fabricator.module.inventoryActionDisabled", _disabledOk, format ["phase=%1|crate=%2|station=%3|distance=%4|action=%5|active=%6|mirror=%7", _phase, netId _crate, netId _station, _crate distance _station, _action param [0, ""], _disabledTree, missionNamespace getVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", "unset"]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_YFU_INVENTORY_CLIENT_PHASE", [_token, "disabled", _disabledOk], true];

private _enabledDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    _phase = missionNamespace getVariable ["TRIBUNAL_YFU_INVENTORY_PHASE", []];
    ((_phase param [0, ""]) isEqualTo _token
        && {(_phase param [1, ""]) isEqualTo "enabled"}
        && {missionNamespace getVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", false]})
        || {diag_tickTime > _enabledDeadline}
};
private _enabledTree = [_crate, _action] call _collectActive;
private _enabledOk = (_phase param [4, false])
    && {_action isNotEqualTo []}
    && {_enabledTree isNotEqualTo []};
["fabricator.module.inventoryActionEnabled", _enabledOk, format ["phase=%1|crate=%2|station=%3|distance=%4|action=%5|active=%6|mirror=%7", _phase, netId _crate, netId _station, _crate distance _station, _action param [0, ""], _enabledTree, missionNamespace getVariable ["YOSHI_FABRICATOR_LOCAL_INVENTORY", "unset"]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_YFU_INVENTORY_CLIENT_PHASE", [_token, "enabled", _enabledOk], true];
player setPosASL _originalASL;
player enableSimulation _originalSimulation;

[player] remoteExecCall ["YOSHI_setVirtualStorageLogic", 2];
[player] remoteExecCall ["YOSHI_setFabricatorLogic", 2];
missionNamespace setVariable ["YFU_VIRTUAL_STORAGE_OBJECTS", [player], true];
missionNamespace setVariable ["YFU_FABRICATOR_STATIONS", [player], true];
["fabricator.module.clientAdversarialStimulus", !isNull player && {clientOwner > 2} && {(netId player) isNotEqualTo ""}, format ["player=%1|owner=%2|clientOwner=%3", netId player, owner player, clientOwner]] call _assert;

private _result = [];
private _resultDeadline = diag_tickTime + 30;
waitUntil {uiSleep 0.05; _result = missionNamespace getVariable ["TRIBUNAL_YFU_MODULE_RESULT", []]; (count _result) isEqualTo 4 || {diag_tickTime > _resultDeadline}};
private _replicated = (_result param [0, ""]) isEqualTo _token
    && {(_result param [1, []]) isEqualTo _catalogueIds}
    && {(_result param [2, []]) isEqualTo _stationIds}
    && {(count (_result param [3, []])) isEqualTo 4};
["fabricator.module.clientAuthorityResult", _replicated, format ["result=%1|expectedCatalogue=%2|expectedStations=%3", _result, _catalogueIds, _stationIds]] call _assert;
missionNamespace setVariable ["TRIBUNAL_YFU_MODULE_CLIENT_DONE", _token, true];
'''


TRIBUNAL_SCENARIO = Scenario(
    identifier="fieldutils-eden-modules",
    tier="gameplay",
    server_expected=frozenset({
        "fabricator.module.dispatch", "fabricator.module.aggregate",
        "fabricator.module.retained", "fabricator.module.authority",
        "fabricator.module.inventoryToggle", "fabricator.module.cleanup",
    }),
    client_expected=frozenset({
        "fabricator.module.clientMirrors", "fabricator.module.clientAdversarialStimulus",
        "fabricator.module.clientAuthorityResult", "fabricator.module.inventoryActionDisabled",
        "fabricator.module.inventoryActionEnabled",
    }),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={"product": "field-utilities", "feature": "eden-modules"},
    mission_entities=(
        MissionEntity("TRIBUNAL_YFU_STORAGE_MODULE_A", "FieldUtils_Virtual_Storage_Module", "YFU_FieldUtils", "Logic", (3300, 0, 3300)),
        MissionEntity("TRIBUNAL_YFU_STORAGE_MODULE_B", "FieldUtils_Virtual_Storage_Module", "YFU_FieldUtils", "Logic", (3310, 0, 3300)),
        MissionEntity("TRIBUNAL_YFU_FABRICATOR_MODULE_A", "FieldUtils_Fabricator_Module", "YFU_FieldUtils", "Logic", (3320, 0, 3300)),
        MissionEntity("TRIBUNAL_YFU_FABRICATOR_MODULE_B", "FieldUtils_Fabricator_Module", "YFU_FieldUtils", "Logic", (3330, 0, 3300)),
        MissionEntity("TRIBUNAL_YFU_STORAGE_A", "B_supplyCrate_F", "A3_Weapons_F_Ammoboxes", "Object", (3300, 0, 3350)),
        MissionEntity("TRIBUNAL_YFU_STORAGE_B", "B_supplyCrate_F", "A3_Weapons_F_Ammoboxes", "Object", (3310, 0, 3350)),
        MissionEntity("TRIBUNAL_YFU_STATION_A", "Land_CargoBox_V1_F", "A3_Structures_F_Mil_Cargo", "Object", (3320, 0, 3350)),
        MissionEntity("TRIBUNAL_YFU_STATION_B", "Land_CargoBox_V1_F", "A3_Structures_F_Mil_Cargo", "Object", (3330, 0, 3350)),
    ),
    mission_syncs=(
        MissionSync("TRIBUNAL_YFU_STORAGE_MODULE_A", "TRIBUNAL_YFU_STORAGE_A"),
        MissionSync("TRIBUNAL_YFU_STORAGE_MODULE_B", "TRIBUNAL_YFU_STORAGE_B"),
        MissionSync("TRIBUNAL_YFU_FABRICATOR_MODULE_A", "TRIBUNAL_YFU_STATION_A"),
        MissionSync("TRIBUNAL_YFU_FABRICATOR_MODULE_B", "TRIBUNAL_YFU_STATION_B"),
    ),
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="Authentic retained Eden storage and Fabricator modules aggregate exact synchronized catalogue and station objects into server-owned authority while replicated mirrors remain presentation-only; the published local-inventory state causally gates the registered nearby virtual-inventory ACE action in a disabled-versus-enabled A/B.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The scenario proves real typed dispatch and Sync links, multiple-module aggregation, locality, retained logic, client replication, the registered local-inventory action condition under a one-variable false/true control, direct-setter rejection, public-mirror poisoning resistance, and cleanup without re-proving fabrication transactions.",
        dependencies=("typed Eden module fixture", "one authenticated client", "accepted Fabricator transaction coverage"),
        evidence_types=frozenset({"configured-dispatch", "native-sync", "authoritative-state", "registered-action-condition", "negative-control", "adversarial-stimulus", "replication", "locality", "cleanup"}),
        locality_requirements="Module dispatch and authoritative catalogue/station registration are server-local; client-a receives mirrors and cannot replace server-private authority.",
    ),
)

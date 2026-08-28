"""Permanent cold-client ACE registration/coexistence contract for Field Utilities."""

from tribunal.runner.model import Scenario, ScenarioReview


TRIBUNAL_SCENARIO = Scenario(
    identifier="fieldutils-ace-composition",
    tier="gameplay",
    server_expected=frozenset({
        "fieldAce.fixture",
        "fieldAce.cleanup",
    }),
    client_expected=frozenset({
        "fieldAce.registry",
        "fieldAce.coexistence",
        "fieldAce.relevance",
        "fieldAce.noMutation",
    }),
    server_sqf=r'''
private _scenarioPlayer = allPlayers param [0, objNull];
private _playerDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.1;
    _scenarioPlayer = allPlayers param [0, objNull];
    !isNull _scenarioPlayer || {diag_tickTime > _playerDeadline}
};
private _origin = if (isNull _scenarioPlayer) then {[4700, 2800, 0]} else {getPosATL _scenarioPlayer};
private _spawn = {
    params ["_class", "_offset"];
    private _obj = createVehicle [_class, _origin vectorAdd _offset, [], 0, "CAN_COLLIDE"];
    _obj setPosATL (_origin vectorAdd _offset);
    _obj setFuel 0;
    _obj engineOn false;
    _obj allowDamage false;
    _obj enableSimulationGlobal false;
    _obj
};
private _crate = ["B_supplyCrate_F", [4, 0, 0]] call _spawn;
private _carrier = ["B_T_VTOL_01_vehicle_F", [11, 0, 0]] call _spawn;
private _land = ["B_MRAP_01_F", [-4, 0, 0]] call _spawn;
private _uav = ["B_UAV_01_F", [0, 4, 0]] call _spawn;
private _bridge = ["YFU_Bridge_Box", [0, -4, 0]] call _spawn;
private _objects = [_crate, _carrier, _land, _uav, _bridge];
private _cargoDeadline = diag_tickTime + 3;
waitUntil {
    uiSleep 0.05;
    private _state = _carrier canVehicleCargo _crate;
    ((_state param [0, false]) && {_state param [1, false]}) || {diag_tickTime > _cargoDeadline}
};
private _ids = _objects apply {netId _x};
private _cargo = _carrier canVehicleCargo _crate;
private _fixtureOk = !isNull _scenarioPlayer
    && {(_objects findIf {isNull _x || {!local _x} || {(netId _x) isEqualTo ""}}) < 0}
    && {(_cargo param [0, false]) && {_cargo param [1, false]}}
    && {unitIsUAV _uav}
    && {alive _crate && {alive _land} && {alive _uav} && {alive _bridge}};
missionNamespace setVariable ["TRIBUNAL_FIELD_ACE_FIXTURE", [_token, _ids, _cargo], true];
["fieldAce.fixture", _fixtureOk, format ["ids=%1|classes=%2|cargo=%3|locality=%4", _ids, _objects apply {typeOf _x}, _cargo, _objects apply {[netId _x, local _x, owner _x]}]] call _assert;

private _doneDeadline = diag_tickTime + 45;
waitUntil {
    uiSleep 0.1;
    (missionNamespace getVariable ["TRIBUNAL_FIELD_ACE_DONE", ""]) isEqualTo _token
        || {diag_tickTime > _doneDeadline}
};
private _clientDone = (missionNamespace getVariable ["TRIBUNAL_FIELD_ACE_DONE", ""]) isEqualTo _token;
{deleteVehicle _x;} forEach _objects;
missionNamespace setVariable ["TRIBUNAL_FIELD_ACE_FIXTURE", nil, true];
private _cleanupDeadline = diag_tickTime + 3;
waitUntil {uiSleep 0.05; (_ids findIf {!isNull (objectFromNetId _x)}) < 0 || {diag_tickTime > _cleanupDeadline}};
["fieldAce.cleanup", _clientDone && {(_ids findIf {!isNull (objectFromNetId _x)}) < 0}, format ["clientDone=%1|remaining=%2", _clientDone, _ids select {!isNull (objectFromNetId _x)}]] call _assert;
''',
    client_sqf=r'''
private _fixture = [];
private _fixtureDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    _fixture = missionNamespace getVariable ["TRIBUNAL_FIELD_ACE_FIXTURE", []];
    (count _fixture) isEqualTo 3 || {diag_tickTime > _fixtureDeadline}
};
private _ids = _fixture param [1, []];
private _objects = [];
private _objectsDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    _objects = _ids apply {objectFromNetId _x};
    (count _objects) isEqualTo 5 && {(_objects findIf {isNull _x}) < 0}
        || {diag_tickTime > _objectsDeadline}
};
private _crate = _objects param [0, objNull];
private _carrier = _objects param [1, objNull];
private _land = _objects param [2, objNull];
private _uav = _objects param [3, objNull];
private _bridge = _objects param [4, objNull];

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
private _actionFor = {
    params ["_target", "_wanted"];
    if (isNull _target) exitWith {[]};
    [_target] call ace_interact_menu_fnc_compileMenu;
    private _class = typeOf _target call ace_common_fnc_getConfigName;
    [ace_interact_menu_ActNamespace getOrDefault [_class, []], _wanted] call _findAction
};
private _allActionIds = {
    params ["_nodes"];
    private _idsFound = [];
    {
        _x params ["_data", "_children"];
        private _id = _data param [0, ""];
        if !(_id isEqualTo "") then {_idsFound pushBack _id;};
        _idsFound append ([_children] call _allActionIds);
    } forEach _nodes;
    _idsFound
};
private _collectActive = {
    params ["_target", "_data"];
    if (isNull _target || {_data isEqualTo []}) exitWith {[]};
    ace_interact_menu_objectActionList = [];
    [_target, [_data, []], [], player distance _target] call ace_interact_menu_fnc_collectActiveActionTree
};

private _bridgeAction = [_bridge, "YFU_BoxBridgeOpenUI_Class"] call _actionFor;
private _logiBox = [_crate, "logiActions"] call _actionFor;
private _inventory = [_crate, "zenInventoryActions"] call _actionFor;
private _logiLand = [_land, "logiActions"] call _actionFor;
private _tow = [_land, "TowActions"] call _actionFor;
private _stow = [_land, "YOSHI_StowRopes"] call _actionFor;
private _fpvAbsent = ([_uav, "UAV_field_task"] call _actionFor) isEqualTo [];
private _payloadActionDeadline = diag_tickTime + 5;
waitUntil {uiSleep 0.05; (actionIDs _uav) isNotEqualTo [] || {diag_tickTime > _payloadActionDeadline}};
private _payloadActions = actionIDs _uav;
private _payloadLabels = _payloadActions apply {(_uav actionParams _x) param [0, ""]};
private _payloadActionPresent = "Pontifex Payload Manager" in _payloadLabels;
private _actions = [_bridgeAction, _logiBox, _inventory, _logiLand, _tow, _stow];
private _actionIds = _actions apply {_x param [0, ""]};
private _registryOk = !isNil "ace_interact_menu_fnc_collectActiveActionTree"
    && {(_actions findIf {_x isEqualTo []}) < 0}
    && {_fpvAbsent}
    && {_payloadActionPresent}
    && {_actionIds isEqualTo [
        "YFU_BoxBridgeOpenUI_Class", "logiActions", "zenInventoryActions",
        "logiActions", "TowActions", "YOSHI_StowRopes"
    ]};
["fieldAce.registry", _registryOk, format ["ids=%1|labels=%2|aceVersion=%3", _actionIds, _actions apply {_x param [1, ""]}, getText (configFile >> "CfgPatches" >> "ace_interact_menu" >> "versionStr")]] call _assert;

private _crateClass = typeOf _crate call ace_common_fnc_getConfigName;
private _landClass = typeOf _land call ace_common_fnc_getConfigName;
private _uavClass = typeOf _uav call ace_common_fnc_getConfigName;
private _crateIds = [ace_interact_menu_ActNamespace getOrDefault [_crateClass, []]] call _allActionIds;
private _landIds = [ace_interact_menu_ActNamespace getOrDefault [_landClass, []]] call _allActionIds;
private _uavIds = [ace_interact_menu_ActNamespace getOrDefault [_uavClass, []]] call _allActionIds;
private _coexistenceOk = ({_x isEqualTo "logiActions"} count _crateIds) isEqualTo 1
    && {({_x isEqualTo "zenInventoryActions"} count _crateIds) isEqualTo 1}
    && {({_x isEqualTo "logiActions"} count _landIds) isEqualTo 1}
    && {({_x isEqualTo "TowActions"} count _landIds) isEqualTo 1}
    && {({_x isEqualTo "YOSHI_StowRopes"} count _landIds) isEqualTo 1}
    && {({_x isEqualTo "YOSHI_StowRopes"} count _uavIds) isEqualTo 1}
    && {! ("UAV_field_task" in _landIds)}
    && {! ("UAV_field_task" in _uavIds)};
["fieldAce.coexistence", _coexistenceOk, format ["crateClass=%1|crate=%2|landClass=%3|land=%4|uavClass=%5|uav=%6", _crateClass, _crateIds, _landClass, _landIds, _uavClass, _uavIds]] call _assert;

private _cargo = if (isNull _carrier || {isNull _crate}) then {[false, false]} else {_carrier canVehicleCargo _crate};
private _playerASL = getPosASL player;
private _bridgeASL = getPosASL _bridge;
player setPosASL (_bridgeASL vectorAdd [0, 4, 0]);
uiSleep 0.1;
private _bridgeActive = [_bridge, _bridgeAction] call _collectActive;
private _bridgeDistance = player distance _bridge;
private _logiActive = [_crate, _logiBox] call _collectActive;
private _inventoryAbsent = ([_crate, _inventory] call _collectActive) isEqualTo [];
private _towActive = [_land, _tow] call _collectActive;
private _stowAbsent = ([_land, _stow] call _collectActive) isEqualTo [];
private _payloadActionStillPresent = "Pontifex Payload Manager" in ((actionIDs _uav) apply {(_uav actionParams _x) param [0, ""]});
player setPosASL _playerASL;
private _relevanceOk = (_fixture param [2, []]) isEqualTo _cargo
    && {(_cargo param [0, false]) && {_cargo param [1, false]}}
    && {_bridgeActive isNotEqualTo []}
    && {_logiActive isNotEqualTo []}
    && {_inventoryAbsent}
    && {_towActive isNotEqualTo []}
    && {_stowAbsent}
    && {_fpvAbsent}
    && {_payloadActionStillPresent};
["fieldAce.relevance", _relevanceOk, format ["cargo=%1|bridgeActive=%2|bridgeDistance=%3|logiActive=%4|inventoryAbsent=%5|towActive=%6|stowAbsent=%7|fpvAceAbsent=%8|payloadNative=%9|distances=%10", _cargo, _bridgeActive isNotEqualTo [], _bridgeDistance, _logiActive isNotEqualTo [], _inventoryAbsent, _towActive isNotEqualTo [], _stowAbsent, _fpvAbsent, _payloadActionStillPresent, _objects apply {player distance _x}]] call _assert;

private _noMutation = !isNull _crate && {!isNull _carrier} && {!isNull _land} && {!isNull _uav} && {!isNull _bridge}
    && {isNull attachedTo _crate}
    && {isNull isVehicleCargo _crate}
    && {(count ropes _land) isEqualTo 0}
    && {(_uav getVariable ["YFU_PAYLOAD_STATE", [0, [], 0]]) isEqualTo [0, [], 0]};
["fieldAce.noMutation", _noMutation, format ["attached=%1|cargo=%2|ropes=%3|uavState=%4", attachedTo _crate, isVehicleCargo _crate, count ropes _land, _uav getVariable ["YFU_PAYLOAD_STATE", [0, [], 0]]]] call _assert;
missionNamespace setVariable ["TRIBUNAL_FIELD_ACE_DONE", _token, true];
''',
    metadata={
        "product": "field-utilities",
        "feature": "cold-client-interaction-composition",
    },
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="A cold real client registers the retained Field Utilities ACE roots exactly once while the small-UAV Payload Manager is present only as a native world action; relevant roots resolve, irrelevant roots remain absent, and discovery causes no gameplay mutation.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The shared post-init composition boundary can fail while isolated feature logic remains green; the scenario proves both retained ACE coexistence and the Payload Manager's deliberate independence from ACE interaction without invoking consequential statements.",
        dependencies=("ACE 3.21 external adapter for retained non-payload roots", "native addAction", "one independently authenticated client"),
        evidence_types=frozenset({"ace-active-action-tree", "native-world-action", "exact-netid", "negative-control", "locality", "cleanup"}),
        locality_requirements="The dedicated server owns all fixture objects; client-a owns cold ACE registration and active-tree resolution. No effect or client-B/JIP claim is made.",
    ),
)

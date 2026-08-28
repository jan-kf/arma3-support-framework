#include "..\..\ui\idc.hpp"

/*
Pontifex Payload Manager

The client proposes an ordered manifest. The dedicated server authenticates the
transport owner, revalidates the exact UAV, existing payload identities, source
container instances and eight-unit budget, then commits inventory and UAV state
through a bounded server-authorized prepare/commit protocol. Installed entries are UAV property: a later
proposal may reorder them but may not return them to a player inventory.
*/

YFU_PAYLOAD_CAPACITY = 8;
YFU_PAYLOAD_RANGE = 4;
YFU_PAYLOAD_RESULT_LIMIT = 64;
YFU_PAYLOAD_AUDIT_LIMIT = 128;
YFU_PAYLOAD_INTERNAL_TOKEN = format ["yfu-payload-%1-%2", diag_tickTime, random 1e9];

YFU_fnc_payloadDefinitions = {
    createHashMapFromArray [
        ["HandGrenade", ["M67 fragmentation grenade", 1, "drop", "GrenadeHand"]],
        ["MiniGrenade", ["RGO fragmentation grenade", 1, "drop", "GrenadeHand"]],
        ["SatchelCharge_Remote_Mag", ["Satchel charge", 8, "satchel", "ModuleExplosive_SatchelCharge_F"]]
    ]
};

YFU_fnc_payloadDefinition = {
    params [["_class", "", [""]]];
    (call YFU_fnc_payloadDefinitions) getOrDefault [_class, []]
};

YFU_fnc_payloadEligible = {
    params [["_uav", objNull, [objNull]]];
    !isNull _uav && {alive _uav} && {_uav isKindOf "UAV_01_base_F"} && {unitIsUAV _uav}
};

YFU_fnc_payloadState = {
    params [["_uav", objNull, [objNull]]];
    if (isNull _uav) exitWith {[0, [], 0]};
    private _state = _uav getVariable ["YFU_PAYLOAD_STATE", [0, [], 0]];
    if !(_state isEqualType [] && {(count _state) isEqualTo 3}) exitWith {[0, [], 0]};
    _state
};

YFU_fnc_payloadPlayerForOwner = {
    params ["_owner"];
    private _requester = objNull;
    {if ((owner _x) isEqualTo _owner) exitWith {_requester = _x;};} forEach allPlayers;
    _requester
};

YFU_fnc_payloadAudit = {
    params ["_token", "_operation", "_accepted", "_reason", "_owner", ["_detail", ""]];
    if (!isServer || {_token isNotEqualTo YFU_PAYLOAD_INTERNAL_TOKEN}) exitWith {};
    private _rows = localNamespace getVariable ["YFU_PAYLOAD_AUDIT", []];
    _rows pushBack [diag_tickTime, _operation, _accepted, _reason, _owner, _detail];
    if ((count _rows) > YFU_PAYLOAD_AUDIT_LIMIT) then {
        _rows deleteRange [0, (count _rows) - YFU_PAYLOAD_AUDIT_LIMIT];
    };
    localNamespace setVariable ["YFU_PAYLOAD_AUDIT", _rows];
};

YFU_fnc_payloadDeploymentAudit = {
    params ["_token", "_operation", "_owner", "_uav", "_payload", "_effect"];
    if (!isServer || {_token isNotEqualTo YFU_PAYLOAD_INTERNAL_TOKEN} || {isNull _effect}) exitWith {};
    private _rows = localNamespace getVariable ["YFU_PAYLOAD_DEPLOYMENTS", []];
    _rows pushBack [diag_tickTime, _operation, _owner, netId _uav, _payload # 0, _payload # 1, typeOf _effect, netId _effect, getPosATL _effect, velocity _effect, getPosATL _uav];
    if ((count _rows) > YFU_PAYLOAD_AUDIT_LIMIT) then {_rows deleteRange [0, (count _rows) - YFU_PAYLOAD_AUDIT_LIMIT];};
    localNamespace setVariable ["YFU_PAYLOAD_DEPLOYMENTS", _rows];
};

YFU_fnc_payloadResult = {
    if (!hasInterface) exitWith {};
    params ["_operation", "_accepted", "_reason", "_uavId", "_revision", ["_payloads", []]];
    private _rows = uiNamespace getVariable ["YFU_PAYLOAD_RESULTS", []];
    _rows pushBack [_operation, _accepted, _reason, _uavId, _revision, _payloads, clientOwner, diag_tickTime];
    if ((count _rows) > YFU_PAYLOAD_RESULT_LIMIT) then {
        _rows deleteRange [0, (count _rows) - YFU_PAYLOAD_RESULT_LIMIT];
    };
    uiNamespace setVariable ["YFU_PAYLOAD_RESULTS", _rows];

    if (_accepted) then {
        if (!isNull (uiNamespace getVariable ["YFU_PayloadManager_Display", displayNull]) && {_reason isEqualTo "applied"}) then {closeDialog 1;};
        private _message = switch (_reason) do {case "applied": {"loadout applied"}; case "selected": {"payload selected"}; case "deployed": {"payload deployed"}; default {_reason};};
        systemChat format ["Pontifex Payload Manager: %1.", _message];
    } else {
        private _display = uiNamespace getVariable ["YFU_PayloadManager_Display", displayNull];
        if (!isNull _display) then {
            (_display displayCtrl YFU_IDC_PAYLOAD_STATUS) ctrlSetStructuredText parseText format ["<t color='#ff7777'>APPLY REFUSED: %1. Nothing was consumed.</t>", toUpper _reason];
        } else {
            systemChat format ["Pontifex payload request refused: %1", _reason];
        };
    };
};

YFU_fnc_payloadPublish = {
    params ["_token", "_owner", "_operation", "_accepted", "_reason", "_uav"];
    if (!isServer || {_token isNotEqualTo YFU_PAYLOAD_INTERNAL_TOKEN}) exitWith {};
    private _state = [_uav] call YFU_fnc_payloadState;
    private _uavId = if (isNull _uav) then {""} else {netId _uav};
    [_operation, _accepted, _reason, _uavId, _state # 0, _state # 1] remoteExecCall ["YFU_fnc_payloadResult", _owner];
    [_token, _operation, _accepted, _reason, _owner, format ["uav=%1|revision=%2|payloads=%3", _uavId, _state # 0, count (_state # 1)]] call YFU_fnc_payloadAudit;
};

YFU_fnc_payloadSourceItems = {
    params ["_unit", "_source"];
    switch (_source) do {
        case "uniform": {uniformItems _unit};
        case "vest": {vestItems _unit};
        case "backpack": {backpackItems _unit};
        default {[]};
    }
};

YFU_fnc_payloadRemoveSourceItem = {
    params ["_unit", "_source", "_class"];
    switch (_source) do {
        case "uniform": {_unit removeItemFromUniform _class;};
        case "vest": {_unit removeItemFromVest _class;};
        case "backpack": {_unit removeItemFromBackpack _class;};
    };
};

YFU_fnc_payloadInventoryTransactions = {
    private _transactions = localNamespace getVariable ["YFU_PAYLOAD_INVENTORY_TRANSACTIONS", createHashMap];
    localNamespace setVariable ["YFU_PAYLOAD_INVENTORY_TRANSACTIONS", _transactions];
    _transactions
};

YFU_fnc_payloadInventoryPrepareLocal = {
    if (!hasInterface || {remoteExecutedOwner isNotEqualTo 2}) exitWith {};
    params ["_operation", "_claims"];
    private _snapshot = getUnitLoadout player;
    private _beforeCounts = createHashMap;
    private _verdict = "";
    {
        _x params ["_source", "_class", "_ordinal"];
        private _available = {_x isEqualTo _class} count ([player, _source] call YFU_fnc_payloadSourceItems);
        if (_ordinal < 0 || {_ordinal >= _available}) exitWith {_verdict = "inventory-changed";};
        private _countKey = format ["%1|%2", _source, _class];
        if (isNil {_beforeCounts get _countKey}) then {_beforeCounts set [_countKey, _available];};
    } forEach _claims;
    if (_verdict isEqualTo "") then {
        {[player, _x # 0, _x # 1] call YFU_fnc_payloadRemoveSourceItem;} forEach _claims;
        private _removed = createHashMap;
        {_removed set [format ["%1|%2", _x # 0, _x # 1], (_removed getOrDefault [format ["%1|%2", _x # 0, _x # 1], 0]) + 1];} forEach _claims;
        {
            private _parts = _x splitString "|";
            private _actual = {_x isEqualTo (_parts # 1)} count ([player, _parts # 0] call YFU_fnc_payloadSourceItems);
            if (_actual isNotEqualTo ((_beforeCounts get _x) - (_removed get _x))) exitWith {_verdict = "inventory-rollback";};
        } forEach keys _removed;
    };
    if (_verdict isNotEqualTo "") then {player setUnitLoadout _snapshot;};
    if (_verdict isEqualTo "") then {
        private _pending = uiNamespace getVariable ["YFU_PAYLOAD_INVENTORY_LOCAL", createHashMap];
        _pending set [_operation, _snapshot];
        uiNamespace setVariable ["YFU_PAYLOAD_INVENTORY_LOCAL", _pending];
    };
    [_operation, _verdict isEqualTo "", if (_verdict isEqualTo "") then {"prepared"} else {_verdict}] remoteExecCall ["YFU_fnc_payloadInventoryPreparedServer", 2];
};

YFU_fnc_payloadInventoryFinalizeLocal = {
    if (!hasInterface || {remoteExecutedOwner isNotEqualTo 2}) exitWith {};
    params ["_operation", "_commit", "_reason"];
    private _pending = uiNamespace getVariable ["YFU_PAYLOAD_INVENTORY_LOCAL", createHashMap];
    private _snapshot = _pending getOrDefault [_operation, []];
    if (!_commit && {_snapshot isNotEqualTo []}) then {player setUnitLoadout _snapshot;};
    _pending deleteAt _operation;
    uiNamespace setVariable ["YFU_PAYLOAD_INVENTORY_LOCAL", _pending];
    if (!_commit) then {[_operation, _snapshot isNotEqualTo [], _reason] remoteExecCall ["YFU_fnc_payloadInventoryRollbackAckServer", 2];};
};

YFU_fnc_payloadInventoryPreparedServer = {
    if (!isServer) exitWith {};
    params ["_operation", "_prepared", "_reason"];
    private _owner = remoteExecutedOwner;
    private _transactions = call YFU_fnc_payloadInventoryTransactions;
    private _key = format ["%1#%2", _owner, _operation];
    private _tx = _transactions getOrDefault [_key, createHashMap];
    if ((count _tx) isEqualTo 0) exitWith {[_operation, false, "expired"] remoteExecCall ["YFU_fnc_payloadInventoryFinalizeLocal", _owner];};
    private _uav = _tx getOrDefault ["uav", objNull];
    private _requester = _tx getOrDefault ["requester", objNull];
    private _revision = _tx getOrDefault ["revision", -1];
    private _manifest = _tx getOrDefault ["manifest", []];
    private _selected = _tx getOrDefault ["selected", 0];
    private _clear = {
        _uav setVariable ["YFU_PAYLOAD_PENDING", nil, true];
        _requester setVariable ["YFU_PAYLOAD_PENDING", nil, true];
    };
    if (!_prepared) exitWith {
        call _clear;
        _transactions deleteAt _key;
        [YFU_PAYLOAD_INTERNAL_TOKEN, _owner, _operation, false, _reason, _uav] call YFU_fnc_payloadPublish;
    };
    private _state = [_uav] call YFU_fnc_payloadState;
    private _canCommit = [_uav] call YFU_fnc_payloadEligible
        && {(_tx getOrDefault ["phase", ""]) isEqualTo "preparing"}
        && {(_state # 0) isEqualTo _revision}
        && {(_uav getVariable ["YFU_PAYLOAD_PENDING", ""]) isEqualTo _operation}
        && {(_requester getVariable ["YFU_PAYLOAD_PENDING", ""]) isEqualTo _operation};
    if (_canCommit) exitWith {
        private _newSelected = if (_manifest isEqualTo []) then {0} else {_selected min ((count _manifest) - 1) max 0};
        _uav setVariable ["YFU_PAYLOAD_STATE", [_revision + 1, _manifest, _newSelected], true];
        call _clear;
        _transactions deleteAt _key;
        [_operation, true, "applied"] remoteExecCall ["YFU_fnc_payloadInventoryFinalizeLocal", _owner];
        [YFU_PAYLOAD_INTERNAL_TOKEN, _owner, _operation, true, "applied", _uav] call YFU_fnc_payloadPublish;
    };
    _tx set ["phase", "rollback"];
    _tx set ["reason", "commit-invalidated"];
    _transactions set [_key, _tx];
    [_operation, false, "commit-invalidated"] remoteExecCall ["YFU_fnc_payloadInventoryFinalizeLocal", _owner];
};

YFU_fnc_payloadInventoryRollbackAckServer = {
    if (!isServer) exitWith {};
    params ["_operation", "_restored", "_reason"];
    private _owner = remoteExecutedOwner;
    private _transactions = call YFU_fnc_payloadInventoryTransactions;
    private _key = format ["%1#%2", _owner, _operation];
    private _tx = _transactions getOrDefault [_key, createHashMap];
    if ((count _tx) isEqualTo 0) exitWith {};
    private _uav = _tx getOrDefault ["uav", objNull];
    private _requester = _tx getOrDefault ["requester", objNull];
    _uav setVariable ["YFU_PAYLOAD_PENDING", nil, true];
    _requester setVariable ["YFU_PAYLOAD_PENDING", nil, true];
    _transactions deleteAt _key;
    [YFU_PAYLOAD_INTERNAL_TOKEN, _owner, _operation, false, if (_restored) then {_reason} else {"rollback-failed"}, _uav] call YFU_fnc_payloadPublish;
};

YFU_fnc_payloadApplyServer = {
    if (!isServer) exitWith {false};
    params [
        ["_operation", "", [""]],
        ["_uav", objNull, [objNull]],
        ["_expectedRevision", -1, [0]],
        ["_claims", [], [[]]]
    ];
    private _owner = remoteExecutedOwner;
    private _reject = {
        params ["_reason"];
        [YFU_PAYLOAD_INTERNAL_TOKEN, _owner, _operation, false, _reason, _uav] call YFU_fnc_payloadPublish;
        false
    };
    if (_owner <= 2 || {_operation isEqualTo ""} || {(count _operation) > 128} || {!(_expectedRevision isEqualType 0)} || {!(_claims isEqualType [])}) exitWith {["schema"] call _reject};

    private _requests = localNamespace getVariable ["YFU_PAYLOAD_REQUESTS", createHashMap];
    private _key = format ["%1#%2", _owner, _operation];
    if (_requests getOrDefault [_key, false]) exitWith {["duplicate"] call _reject};
    _requests set [_key, true];
    if ((count keys _requests) > 256) then {_requests = createHashMapFromArray [[_key, true]];};
    localNamespace setVariable ["YFU_PAYLOAD_REQUESTS", _requests];

    private _requester = [_owner] call YFU_fnc_payloadPlayerForOwner;
    if (isNull _requester || {!alive _requester}) exitWith {["requester"] call _reject};
    if !([_uav] call YFU_fnc_payloadEligible) exitWith {["uav"] call _reject};
    if (!isNull objectParent _requester || {(_requester distance _uav) > YFU_PAYLOAD_RANGE}) exitWith {["range"] call _reject};
    if ((_uav getVariable ["YFU_PAYLOAD_PENDING", ""]) isNotEqualTo "" || {(_requester getVariable ["YFU_PAYLOAD_PENDING", ""]) isNotEqualTo ""}) exitWith {["busy"] call _reject};

    private _state = [_uav] call YFU_fnc_payloadState;
    _state params ["_revision", "_installed", "_selected"];
    if (_revision isNotEqualTo _expectedRevision) exitWith {["stale"] call _reject};
    if ((count _claims) > YFU_PAYLOAD_CAPACITY) exitWith {["schema"] call _reject};

    private _installedById = createHashMap;
    {_installedById set [_x param [0, ""], _x];} forEach _installed;
    private _seenInstalled = createHashMap;
    private _seenInventory = createHashMap;
    private _newClaims = [];
    private _manifest = [];
    private _capacity = 0;
    private _verdict = "";

    {
        if (_verdict isEqualTo "") then {
            if !(_x isEqualType [] && {(count _x) >= 2} && {(_x # 0) isEqualType ""}) then {
                _verdict = "schema";
            } else {
                private _kind = _x # 0;
                if (_kind isEqualTo "installed") then {
                    private _id = _x param [1, "", [""]];
                    private _record = _installedById getOrDefault [_id, []];
                    if (_id isEqualTo "" || {_record isEqualTo []} || {_seenInstalled getOrDefault [_id, false]}) then {
                        _verdict = "installed";
                    } else {
                        _seenInstalled set [_id, true];
                        _manifest pushBack _record;
                        _capacity = _capacity + (_record param [3, YFU_PAYLOAD_CAPACITY]);
                    };
                } else {
                    if (_kind isEqualTo "inventory" && {(count _x) isEqualTo 4}) then {
                        private _source = _x param [1, "", [""]];
                        private _class = _x param [2, "", [""]];
                        private _ordinal = _x param [3, -1, [0]];
                        private _definition = [_class] call YFU_fnc_payloadDefinition;
                        private _instance = format ["%1|%2|%3", _source, _class, _ordinal];
                        if !(_source in ["uniform", "vest", "backpack"]) then {_verdict = "source";};
                        if (_definition isEqualTo [] || {_ordinal < 0}) then {_verdict = "payload";};
                        if (_seenInventory getOrDefault [_instance, false]) then {_verdict = "duplicate-item";};
                        if (_verdict isEqualTo "") then {
                            _seenInventory set [_instance, true];
                            _newClaims pushBack [_source, _class, _ordinal];
                            _definition params ["_label", "_cost", "_deployKind", "_ammo"];
                            _manifest pushBack [format ["%1-%2", _operation, count _manifest], _class, _label, _cost, _deployKind, _ammo];
                            _capacity = _capacity + _cost;
                        };
                    } else {
                        _verdict = "schema";
                    };
                };
            };
        };
    } forEach _claims;

    if (_verdict isEqualTo "" && {(count keys _seenInstalled) isNotEqualTo (count _installed)}) then {_verdict = "installed-missing";};
    if (_verdict isEqualTo "" && {_capacity > YFU_PAYLOAD_CAPACITY}) then {_verdict = "capacity";};
    if (_verdict isNotEqualTo "") exitWith {[_verdict] call _reject};

    _uav setVariable ["YFU_PAYLOAD_PENDING", _operation, true];
    _requester setVariable ["YFU_PAYLOAD_PENDING", _operation, true];
    if (_newClaims isEqualTo []) exitWith {
        private _newSelected = if (_manifest isEqualTo []) then {0} else {_selected min ((count _manifest) - 1) max 0};
        _uav setVariable ["YFU_PAYLOAD_STATE", [_revision + 1, _manifest, _newSelected], true];
        _uav setVariable ["YFU_PAYLOAD_PENDING", nil, true];
        _requester setVariable ["YFU_PAYLOAD_PENDING", nil, true];
        [YFU_PAYLOAD_INTERNAL_TOKEN, _owner, _operation, true, "applied", _uav] call YFU_fnc_payloadPublish;
        true
    };
    private _transactions = call YFU_fnc_payloadInventoryTransactions;
    private _txKey = format ["%1#%2", _owner, _operation];
    private _tx = createHashMapFromArray [["uav", _uav], ["requester", _requester], ["revision", _revision], ["manifest", _manifest], ["selected", _selected], ["phase", "preparing"]];
    _transactions set [_txKey, _tx];
    [_operation, _newClaims] remoteExecCall ["YFU_fnc_payloadInventoryPrepareLocal", _owner];
    [_txKey, _owner, _operation] spawn {
        params ["_txKey", "_owner", "_operation"];
        uiSleep 8;
        private _transactions = call YFU_fnc_payloadInventoryTransactions;
        private _tx = _transactions getOrDefault [_txKey, createHashMap];
        if ((count _tx) > 0 && {(_tx getOrDefault ["phase", ""]) isEqualTo "preparing"}) then {
            _tx set ["phase", "rollback"];
            _tx set ["reason", "inventory-timeout"];
            _transactions set [_txKey, _tx];
            [_operation, false, "inventory-timeout"] remoteExecCall ["YFU_fnc_payloadInventoryFinalizeLocal", _owner];
        };
    };
    true
};

YFU_fnc_payloadController = {
    params ["_requester", "_uav"];
    if (isNull _requester || {!alive _requester} || {!([_uav] call YFU_fnc_payloadEligible)}) exitWith {false};
    private _control = UAVControl _uav;
    (_control param [0, objNull]) isEqualTo _requester && {(_control param [1, ""]) in ["DRIVER", "GUNNER"]}
};

YFU_fnc_payloadControlServer = {
    if (!isServer) exitWith {false};
    params [["_operation", "", [""]], ["_action", "", [""]], ["_uav", objNull, [objNull]]];
    private _owner = remoteExecutedOwner;
    private _reject = {
        params ["_reason"];
        [YFU_PAYLOAD_INTERNAL_TOKEN, _owner, _operation, false, _reason, _uav] call YFU_fnc_payloadPublish;
        false
    };
    if (_owner <= 2 || {_operation isEqualTo ""} || {!(_action in ["next", "deploy"])}) exitWith {["schema"] call _reject};
    private _requests = localNamespace getVariable ["YFU_PAYLOAD_CONTROL_REQUESTS", createHashMap];
    private _key = format ["%1#%2", _owner, _operation];
    if (_requests getOrDefault [_key, false]) exitWith {["duplicate"] call _reject};
    _requests set [_key, true];
    if ((count keys _requests) > 256) then {_requests = createHashMapFromArray [[_key, true]];};
    localNamespace setVariable ["YFU_PAYLOAD_CONTROL_REQUESTS", _requests];

    private _requester = [_owner] call YFU_fnc_payloadPlayerForOwner;
    if !([_requester, _uav] call YFU_fnc_payloadController) exitWith {["controller"] call _reject};
    if ((_uav getVariable ["YFU_PAYLOAD_PENDING", ""]) isNotEqualTo "") exitWith {["busy"] call _reject};
    private _state = [_uav] call YFU_fnc_payloadState;
    _state params ["_revision", "_payloads", "_selected"];
    if (_payloads isEqualTo []) exitWith {["empty"] call _reject};

    if (_action isEqualTo "next") exitWith {
        private _next = (_selected + 1) mod (count _payloads);
        _uav setVariable ["YFU_PAYLOAD_STATE", [_revision + 1, _payloads, _next], true];
        [YFU_PAYLOAD_INTERNAL_TOKEN, _owner, _operation, true, "selected", _uav] call YFU_fnc_payloadPublish;
        true
    };

    private _index = _selected min ((count _payloads) - 1) max 0;
    private _payload = _payloads # _index;
    _payload params ["_id", "_class", "_label", "_cost", "_deployKind", "_ammo"];
    private _effect = switch (_deployKind) do {
        case "drop": {createVehicle [_ammo, [0, 0, 100], [], 0, "CAN_COLLIDE"]};
        case "satchel": {createVehicle [_ammo, [0, 0, 100], [], 0, "CAN_COLLIDE"]};
        default {objNull};
    };
    if (isNull _effect) exitWith {["deploy-failed"] call _reject};
    private _effectPos = if (_deployKind isEqualTo "drop") then {(getPosATL _uav) vectorAdd [0, 0, -0.15]} else {getPosATL _uav};
    _effect setPosATL _effectPos;
    if (_deployKind isEqualTo "drop") then {_effect setVelocity (velocity _uav);};

    _payloads deleteAt _index;
    private _next = if (_payloads isEqualTo []) then {0} else {_index mod (count _payloads)};
    _uav setVariable ["YFU_PAYLOAD_STATE", [_revision + 1, _payloads, _next], true];
    [YFU_PAYLOAD_INTERNAL_TOKEN, _operation, _owner, _uav, _payload, _effect] call YFU_fnc_payloadDeploymentAudit;
    if (_deployKind isEqualTo "satchel") then {
        _effect setDamage 1;
        _uav setDamage 1;
    };
    [YFU_PAYLOAD_INTERNAL_TOKEN, _owner, _operation, true, "deployed", _uav] call YFU_fnc_payloadPublish;
    true

};
YFU_fnc_configureUAVLocal = {
    params ["_entity"];
    if (isNull _entity) exitWith {};
    if (!local _entity) exitWith {["YFU_fnc_configureUAVLocal", _entity, [_entity]] call YCD_fnc_runOnObjectOwner;};
    if (_entity getVariable ["YFU_UAV_LocalConfigured", false]) exitWith {};
    _entity setVariable ["YFU_UAV_LocalConfigured", true];
    _entity addEventHandler ["Engine", {
        params ["_vehicle", "_engineState"];
        if (_engineState) then {detach _vehicle} else {_vehicle call YOSHI_attachToBelow};
    }];
    if (!isNil "ace_dragging_fnc_setDraggable") then {[_entity, true, [0, 1, 0]] call ace_dragging_fnc_setDraggable;};
    if (!isNil "ace_dragging_fnc_setCarryable") then {[_entity, true] call ace_dragging_fnc_setCarryable;};
    _entity setFuelConsumptionCoef 0.1;
    _entity setUnitTrait ["camouflageCoef", 0.3];
};

YFU_fnc_payloadEnsureActionLocal = {
    params ["_uav"];
    if (!hasInterface || {isNull _uav} || {!(_uav isKindOf "UAV_01_base_F")} || {(_uav getVariable ["YFU_PAYLOAD_ACTION_LOCAL", -1]) >= 0}) exitWith {};
    private _id = _uav addAction [
        "Pontifex Payload Manager",
        {params ["_target"]; [_target] call YFU_fnc_payloadOpen;},
        nil,
        1.5,
        true,
        true,
        "",
        "alive _target && {_target isKindOf 'UAV_01_base_F'} && {isNull objectParent _this} && {_this distance _target <= 4}",
        YFU_PAYLOAD_RANGE
    ];
    _uav setVariable ["YFU_PAYLOAD_ACTION_LOCAL", _id, false];
};

YFU_fnc_payloadTheme = {
    private _fallback = [0.15, 0.95, 0.15, 1];
    private _candidate = missionNamespace getVariable ["YFU_monochromeBaseColor", _fallback];
    if !(_candidate isEqualType [] && {(count _candidate) isEqualTo 4} && {(_candidate findIf {!(_x isEqualType 0)}) < 0}) then {_candidate = +_fallback;};
    _candidate = _candidate apply {(_x max 0) min 1};
    private _medium = [(_candidate # 0) * 0.66, (_candidate # 1) * 0.66, (_candidate # 2) * 0.66, _candidate # 3];
    private _dark = [(_candidate # 0) * 0.10, (_candidate # 1) * 0.10, (_candidate # 2) * 0.10, (_candidate # 3) max 0.72];
    [_candidate, _medium, _dark]
};

YFU_fnc_payloadDecodeSourceRow = {
    params ["_data"];
    private _parts = _data splitString "|";
    if ((count _parts) isNotEqualTo 3) exitWith {[]};
    [_parts # 0, _parts # 1, parseNumber (_parts # 2)]
};

YFU_fnc_payloadProposalCapacity = {
    private _proposal = uiNamespace getVariable ["YFU_PayloadManager_Proposal", []];
    private _capacity = 0;
    {_capacity = _capacity + (_x param [4, YFU_PAYLOAD_CAPACITY]);} forEach _proposal;
    _capacity
};

YFU_fnc_payloadRefreshDialog = {
    disableSerialization;
    private _display = uiNamespace getVariable ["YFU_PayloadManager_Display", displayNull];
    if (isNull _display) exitWith {};
    private _proposal = uiNamespace getVariable ["YFU_PayloadManager_Proposal", []];
    private _usedTokens = createHashMap;
    {if ((_x param [0, ""]) isEqualTo "inventory") then {_usedTokens set [str (_x # 1), true];};} forEach _proposal;
    private _definitions = call YFU_fnc_payloadDefinitions;
    {
        _x params ["_source", "_idc"];
        private _control = _display displayCtrl _idc;
        lbClear _control;
        private _occurrences = createHashMap;
        {
            private _definition = _definitions getOrDefault [_x, []];
            if (_definition isNotEqualTo []) then {
                private _ordinal = _occurrences getOrDefault [_x, 0];
                _occurrences set [_x, _ordinal + 1];
                private _token = [_source, _x, _ordinal];
                if !(_usedTokens getOrDefault [str _token, false]) then {
                    _definition params ["_label", "_cost"];
                    private _row = _control lbAdd format ["%1  [%2]", _label, _cost];
                    _control lbSetData [_row, format ["%1|%2|%3", _source, _x, _ordinal]];
                    private _picture = getText (configFile >> "CfgMagazines" >> _x >> "picture");
                    if (_picture isNotEqualTo "") then {_control lbSetPicture [_row, _picture];};
                };
            };
        } forEach ([player, _source] call YFU_fnc_payloadSourceItems);
    } forEach [["uniform", YFU_IDC_PAYLOAD_UNIFORM], ["vest", YFU_IDC_PAYLOAD_VEST], ["backpack", YFU_IDC_PAYLOAD_BACKPACK]];

    private _capacityControl = _display displayCtrl YFU_IDC_PAYLOAD_CAPACITY;
    lbClear _capacityControl;
    {
        _x params ["_kind", "_token", "_class", "_label", "_cost"];
        private _ownership = if (_kind isEqualTo "installed") then {"INSTALLED"} else {toUpper (_x param [5, "inventory"])};
        private _row = _capacityControl lbAdd format ["%1. %2  [%3]  %4", _forEachIndex + 1, _label, _cost, _ownership];
        _capacityControl lbSetValue [_row, _forEachIndex];
        _capacityControl lbSetData [_row, format ["proposal:%1", _forEachIndex]];
        private _picture = getText (configFile >> "CfgMagazines" >> _class >> "picture");
        if (_picture isNotEqualTo "") then {_capacityControl lbSetPicture [_row, _picture];};
    } forEach _proposal;
    private _used = call YFU_fnc_payloadProposalCapacity;
    (_display displayCtrl YFU_IDC_PAYLOAD_SUMMARY) ctrlSetStructuredText parseText format ["<t align='right'>CAPACITY %1 / %2 // %3 UNIT(S) FREE</t>", _used, YFU_PAYLOAD_CAPACITY, YFU_PAYLOAD_CAPACITY - _used];
};

YFU_fnc_payloadAddClaim = {
    params ["_claim"];
    private _proposal = uiNamespace getVariable ["YFU_PayloadManager_Proposal", []];
    private _definition = [_claim # 1] call YFU_fnc_payloadDefinition;
    if (_definition isEqualTo []) exitWith {false};
    _definition params ["_label", "_cost"];
    if ((call YFU_fnc_payloadProposalCapacity) + _cost > YFU_PAYLOAD_CAPACITY) exitWith {
        private _display = uiNamespace getVariable ["YFU_PayloadManager_Display", displayNull];
        if (!isNull _display) then {(_display displayCtrl YFU_IDC_PAYLOAD_STATUS) ctrlSetStructuredText parseText "<t color='#ff7777'>That item exceeds the UAV's eight-unit capacity.</t>";};
        false
    };
    private _token = [_claim # 0, _claim # 1, _claim # 2];
    if ((_proposal findIf {(_x param [0, ""]) isEqualTo "inventory" && {(_x # 1) isEqualTo _token}}) >= 0) exitWith {false};
    _proposal pushBack ["inventory", _token, _claim # 1, _label, _cost, _claim # 0];
    uiNamespace setVariable ["YFU_PayloadManager_Proposal", _proposal];
    call YFU_fnc_payloadRefreshDialog;
    true
};

YFU_fnc_payloadAddFromSource = {
    disableSerialization;
    params ["_source", "_row"];
    private _display = uiNamespace getVariable ["YFU_PayloadManager_Display", displayNull];
    if (isNull _display || {_row < 0}) exitWith {false};
    private _idc = switch (_source) do {case "uniform": {YFU_IDC_PAYLOAD_UNIFORM}; case "vest": {YFU_IDC_PAYLOAD_VEST}; case "backpack": {YFU_IDC_PAYLOAD_BACKPACK}; default {-1};};
    if (_idc < 0) exitWith {false};
    private _claim = [(_display displayCtrl _idc) lbData _row] call YFU_fnc_payloadDecodeSourceRow;
    if (_claim isEqualTo []) exitWith {false};
    [_claim] call YFU_fnc_payloadAddClaim
};

YFU_fnc_payloadHandleDrop = {
    disableSerialization;
    params ["_target", "_x", "_y", "_sourceIDC", "_rows"];
    if (_rows isEqualTo []) exitWith {false};
    private _destination = lbCurSel _target;
    if (_sourceIDC isEqualTo YFU_IDC_PAYLOAD_CAPACITY) then {
        private _from = (_rows # 0) param [1, -1];
        private _proposal = uiNamespace getVariable ["YFU_PayloadManager_Proposal", []];
        if (_from >= 0 && {_from < count _proposal}) then {
            private _entry = _proposal deleteAt _from;
            if (_destination < 0) then {_destination = count _proposal;};
            if (_destination > _from) then {_destination = _destination - 1;};
            _proposal insert [_destination max 0 min (count _proposal), [_entry]];
            uiNamespace setVariable ["YFU_PayloadManager_Proposal", _proposal];
            call YFU_fnc_payloadRefreshDialog;
        };
    } else {
        private _claim = [(_rows # 0) param [2, ""]] call YFU_fnc_payloadDecodeSourceRow;
        if (_claim isNotEqualTo []) then {[_claim] call YFU_fnc_payloadAddClaim;};
    };
    true
};

YFU_fnc_payloadRemoveSelected = {
    disableSerialization;
    private _display = uiNamespace getVariable ["YFU_PayloadManager_Display", displayNull];
    if (isNull _display) exitWith {};
    private _row = lbCurSel (_display displayCtrl YFU_IDC_PAYLOAD_CAPACITY);
    private _proposal = uiNamespace getVariable ["YFU_PayloadManager_Proposal", []];
    if (_row < 0 || {_row >= count _proposal}) exitWith {};
    if (((_proposal # _row) # 0) isEqualTo "installed") exitWith {
        (_display displayCtrl YFU_IDC_PAYLOAD_STATUS) ctrlSetStructuredText parseText "<t color='#ffcc66'>Installed payloads belong to the UAV and cannot be reclaimed.</t>";
    };
    _proposal deleteAt _row;
    uiNamespace setVariable ["YFU_PayloadManager_Proposal", _proposal];
    call YFU_fnc_payloadRefreshDialog;
};

YFU_fnc_payloadMoveSelected = {
    disableSerialization;
    params ["_delta"];
    private _display = uiNamespace getVariable ["YFU_PayloadManager_Display", displayNull];
    if (isNull _display) exitWith {};
    private _control = _display displayCtrl YFU_IDC_PAYLOAD_CAPACITY;
    private _from = lbCurSel _control;
    private _proposal = uiNamespace getVariable ["YFU_PayloadManager_Proposal", []];
    private _to = (_from + _delta) max 0 min ((count _proposal) - 1);
    if (_from < 0 || {_from isEqualTo _to}) exitWith {};
    private _entry = _proposal deleteAt _from;
    _proposal insert [_to, [_entry]];
    uiNamespace setVariable ["YFU_PayloadManager_Proposal", _proposal];
    call YFU_fnc_payloadRefreshDialog;
    _control lbSetCurSel _to;
};

YFU_fnc_payloadDialogLoad = {
    disableSerialization;
    private _display = uiNamespace getVariable ["YFU_PayloadManager_Display", displayNull];
    private _uav = uiNamespace getVariable ["YFU_PayloadManager_UAV", objNull];
    if (isNull _display || {!([_uav] call YFU_fnc_payloadEligible)}) exitWith {closeDialog 2;};
    private _theme = call YFU_fnc_payloadTheme;
    _theme params ["_base", "_medium", "_dark"];
    {
        private _control = _display displayCtrl _x;
        _control ctrlSetTextColor _base;
        _control ctrlSetBackgroundColor _dark;
    } forEach [YFU_IDC_PAYLOAD_UNIFORM, YFU_IDC_PAYLOAD_VEST, YFU_IDC_PAYLOAD_BACKPACK, YFU_IDC_PAYLOAD_CAPACITY, YFU_IDC_PAYLOAD_REMOVE, YFU_IDC_PAYLOAD_UP, YFU_IDC_PAYLOAD_DOWN, YFU_IDC_PAYLOAD_CANCEL, YFU_IDC_PAYLOAD_APPLY];
    call YFU_fnc_payloadRefreshDialog;
};

YFU_fnc_payloadOpen = {
    params ["_uav"];
    if (!hasInterface || {!([_uav] call YFU_fnc_payloadEligible)} || {!isNull objectParent player} || {(player distance _uav) > YFU_PAYLOAD_RANGE}) exitWith {false};
    private _state = [_uav] call YFU_fnc_payloadState;
    private _proposal = (_state # 1) apply {["installed", _x # 0, _x # 1, _x # 2, _x # 3, ""]};
    uiNamespace setVariable ["YFU_PayloadManager_UAV", _uav];
    uiNamespace setVariable ["YFU_PayloadManager_Revision", _state # 0];
    uiNamespace setVariable ["YFU_PayloadManager_Proposal", _proposal];
    createDialog "YFU_PayloadManager_Dialog"
};

YFU_fnc_payloadApply = {
    private _uav = uiNamespace getVariable ["YFU_PayloadManager_UAV", objNull];
    private _revision = uiNamespace getVariable ["YFU_PayloadManager_Revision", -1];
    private _proposal = uiNamespace getVariable ["YFU_PayloadManager_Proposal", []];
    if (isNull _uav) exitWith {false};
    private _claims = _proposal apply {
        if ((_x # 0) isEqualTo "installed") then {["installed", _x # 1]} else {["inventory", (_x # 1) # 0, (_x # 1) # 1, (_x # 1) # 2]}
    };
    private _operation = format ["payload-apply-%1-%2-%3", clientOwner, floor (diag_tickTime * 1000), floor random 1e6];
    [_operation, _uav, _revision, _claims] remoteExecCall ["YFU_fnc_payloadApplyServer", 2];
    private _display = uiNamespace getVariable ["YFU_PayloadManager_Display", displayNull];
    if (!isNull _display) then {(_display displayCtrl YFU_IDC_PAYLOAD_STATUS) ctrlSetStructuredText parseText "<t color='#ffcc66'>SERVER VALIDATING ATOMIC LOADOUT...</t>";};
    true
};

YFU_fnc_payloadControlledUAV = {
    if (!hasInterface || {isNull player} || {!alive player}) exitWith {objNull};
    private _uav = getConnectedUAV player;
    if !([_uav] call YFU_fnc_payloadEligible) exitWith {objNull};
    private _control = UAVControl _uav;
    if (!((_control param [0, objNull]) isEqualTo player) || {!((_control param [1, ""]) in ["DRIVER", "GUNNER"])}) exitWith {objNull};
    _uav
};

YFU_fnc_payloadControlRequest = {
    params ["_action"];
    private _uav = call YFU_fnc_payloadControlledUAV;
    if (isNull _uav) exitWith {false};
    private _operation = format ["payload-%1-%2-%3-%4", _action, clientOwner, floor (diag_tickTime * 1000), floor random 1e6];
    [_operation, _action, _uav] remoteExecCall ["YFU_fnc_payloadControlServer", 2];
    true
};

YFU_fnc_payloadBindingText = {
    params ["_action"];
    private _entry = ["Pontifex: Field Utilities", _action] call CBA_fnc_getKeybind;
    if (isNil "_entry") exitWith {"UNBOUND"};
    private _binding = _entry param [5, [-1, [false, false, false]]];
    if ((_binding param [0, -1]) < 0) exitWith {"UNBOUND"};
    _binding call CBA_fnc_localizeKey
};

YFU_fnc_payloadHudStart = {
    if (!hasInterface || {!isNil {uiNamespace getVariable "YFU_PAYLOAD_HUD_LOOP"}}) exitWith {};
    uiNamespace setVariable ["YFU_PAYLOAD_HUD_LOOP", [] spawn {
        disableSerialization;
        private _shown = false;
        while {hasInterface} do {
            private _uav = call YFU_fnc_payloadControlledUAV;
            if (isNull _uav) then {
                if (_shown) then {
                    ("YFU_PayloadHUD" call BIS_fnc_rscLayer) cutText ["", "PLAIN"];
                    _shown = false;
                };
            } else {
                if (!_shown) then {
                    ("YFU_PayloadHUD" call BIS_fnc_rscLayer) cutRsc ["YFU_Payload_HUD", "PLAIN", 0, false];
                    _shown = true;
                };
                private _display = uiNamespace getVariable ["YFU_Payload_HUD_Display", displayNull];
                if (!isNull _display) then {
                    private _state = [_uav] call YFU_fnc_payloadState;
                    _state params ["_revision", "_payloads", "_selected"];
                    private _current = if (_payloads isEqualTo []) then {"EMPTY"} else {(_payloads # (_selected min ((count _payloads) - 1) max 0)) # 2};
                    private _next = ["nextPayload"] call YFU_fnc_payloadBindingText;
                    private _deploy = ["deployPayload"] call YFU_fnc_payloadBindingText;
                    private _theme = call YFU_fnc_payloadTheme;
                    private _control = _display displayCtrl YFU_IDC_PAYLOAD_HUD_TEXT;
                    _control ctrlSetTextColor (_theme # 0);
                    _control ctrlSetBackgroundColor (_theme # 2);
                    _control ctrlSetStructuredText parseText format ["<t align='right' size='0.9'>PONTIFEX PAYLOAD // %1/%2</t><br/><t align='right' size='1.15'>%3</t><br/><t align='right' size='0.72'>NEXT %4   //   DEPLOY %5</t>", if (_payloads isEqualTo []) then {0} else {_selected + 1}, count _payloads, _current, _next, _deploy];
                };
            };
            uiSleep 0.15;
        };
    }];
};

YFU_initFPV_Actions = {
    if (!hasInterface) exitWith {};
    {[_x] call YFU_fnc_payloadEnsureActionLocal;} forEach (vehicles select {_x isKindOf "UAV_01_base_F"});
    addMissionEventHandler ["EntityCreated", {
        params ["_entity"];
        if (_entity isKindOf "UAV_01_base_F") then {[_entity] call YFU_fnc_payloadEnsureActionLocal;};
    }];
    call YFU_fnc_payloadHudStart;
};

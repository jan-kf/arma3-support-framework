/*
CORDIS
Common Operational Runtime & Distributed Integration Services

Multiplayer scripting primitives:
- route execution to the authoritative machine
- resolve recipients consistently
- emit once from server, then fan out locally
*/

YCD_fnc_getFn = {
    params ["_fnName"];
    private _fn = missionNamespace getVariable [_fnName, objNull];
    if !(_fn isEqualType {}) exitWith {nil};
    _fn
};

YCD_fnc_hasFn = {
    params ["_fnName"];
    (missionNamespace getVariable [_fnName, objNull]) isEqualType {}
};

YCD_fnc_routeResult = {
    params ["_state", ["_reason", ""]];
    [_state, _reason]
};

YCD_fnc_callFn = {
    params ["_fnName", ["_args", []]];

    if !([_fnName] call YCD_fnc_hasFn) exitWith {
        ["rejected", "unknown_operation"] call YCD_fnc_routeResult
    };
    private _fn = [_fnName] call YCD_fnc_getFn;
    _args call _fn;
    ["executed"] call YCD_fnc_routeResult
};

YCD_fnc_runOnServer = {
    params ["_fnName", ["_args", []]];

    if !([_fnName] call YCD_fnc_hasFn) exitWith {
        ["rejected", "unknown_operation"] call YCD_fnc_routeResult
    };
    if (isServer) exitWith {
        [_fnName, _args] call YCD_fnc_callFn
    };

    _args remoteExecCall [_fnName, 2];
    ["queued", "server"] call YCD_fnc_routeResult
};

YCD_fnc_runOnObjectOwner = {
    params ["_fnName", "_object", ["_args", []]];

    if !([_fnName] call YCD_fnc_hasFn) exitWith {
        ["rejected", "unknown_operation"] call YCD_fnc_routeResult
    };
    if (isNull _object) exitWith {
        ["rejected", "invalid_destination"] call YCD_fnc_routeResult
    };

    if (local _object) exitWith {
        [_fnName, _args] call YCD_fnc_callFn
    };

    if (!isServer) exitWith {
        [_fnName, _object, _args] remoteExecCall ["YCD_fnc_runOnObjectOwner", 2];
        ["queued", "server_resolution"] call YCD_fnc_routeResult
    };

    private _target = owner _object;
    if (_target < 2) exitWith {
        ["rejected", "invalid_destination"] call YCD_fnc_routeResult
    };
    _args remoteExecCall [_fnName, _target];
    ["queued", "object_owner"] call YCD_fnc_routeResult
};

YCD_fnc_runOnGroupOwner = {
    params ["_fnName", "_unit", ["_args", []]];

    if !([_fnName] call YCD_fnc_hasFn) exitWith {
        ["rejected", "unknown_operation"] call YCD_fnc_routeResult
    };
    if (isNull _unit) exitWith {
        ["rejected", "invalid_destination"] call YCD_fnc_routeResult
    };

    private _group = group _unit;
    if (isNull _group) exitWith {
        ["rejected", "invalid_destination"] call YCD_fnc_routeResult
    };

    if (local _group) exitWith {
        [_fnName, _args] call YCD_fnc_callFn
    };

    if (!isServer) exitWith {
        [_fnName, _unit, _args] remoteExecCall ["YCD_fnc_runOnGroupOwner", 2];
        ["queued", "server_resolution"] call YCD_fnc_routeResult
    };

    private _target = groupOwner _group;
    if (_target < 2) exitWith {
        ["rejected", "invalid_destination"] call YCD_fnc_routeResult
    };
    _args remoteExecCall [_fnName, _target];
    ["queued", "group_owner"] call YCD_fnc_routeResult
};

YCD_fnc_onceCacheKey = {
    params ["_route", "_fnName", "_onceKey"];
    format ["%1|%2|%3", _route, _fnName, _onceKey]
};

YCD_fnc_validateOnceRequest = {
    params ["_fnName", "_onceKey", "_ttl"];
    if !([_fnName] call YCD_fnc_hasFn) exitWith {[false, "unknown_operation"]};
    if (_onceKey isNotEqualTo "" && {_ttl <= 0}) exitWith {[false, "invalid_ttl"]};
    [true, ""]
};

YCD_fnc_pruneLocalOnceCache = {
    private _cache = missionNamespace getVariable ["YCD_localOnceCache", createHashMap];
    private _now = diag_tickTime;

    private _expired = [];
    {
        if (_y <= _now) then {
            _expired pushBack _x;
        };
    } forEach _cache;
    {_cache deleteAt _x;} forEach _expired;

    missionNamespace setVariable ["YCD_localOnceCache", _cache];
};

YCD_fnc_claimLocalOnceKey = {
    params ["_key", ["_ttl", 3]];

    if (_key isEqualTo "") exitWith {true};

    call YCD_fnc_pruneLocalOnceCache;

    private _cache = missionNamespace getVariable ["YCD_localOnceCache", createHashMap];
    private _now = diag_tickTime;

    if ((_cache getOrDefault [_key, -1]) > _now) exitWith {false};

    _cache set [_key, _now + _ttl];
    missionNamespace setVariable ["YCD_localOnceCache", _cache];
    true
};

YCD_fnc_pruneOnceCache = {
    if (!isServer) exitWith {};

    private _cache = missionNamespace getVariable ["YCD_onceCache", createHashMap];
    private _now = serverTime;

    private _expired = [];
    {
        if (_y <= _now) then {
            _expired pushBack _x;
        };
    } forEach _cache;
    {_cache deleteAt _x;} forEach _expired;

    missionNamespace setVariable ["YCD_onceCache", _cache];
};

YCD_fnc_claimOnceKey = {
    params ["_key", ["_ttl", 3]];

    if (!isServer) exitWith {false};
    if (_key isEqualTo "") exitWith {true};

    call YCD_fnc_pruneOnceCache;

    private _cache = missionNamespace getVariable ["YCD_onceCache", createHashMap];
    private _now = serverTime;

    if ((_cache getOrDefault [_key, -1]) > _now) exitWith {false};

    _cache set [_key, _now + _ttl];
    missionNamespace setVariable ["YCD_onceCache", _cache];
    true
};

YCD_fnc_runOnServerOnce = {
    params ["_fnName", ["_args", []], ["_onceKey", ""], ["_ttl", 3]];

    private _validation = [_fnName, _onceKey, _ttl] call YCD_fnc_validateOnceRequest;
    if !(_validation # 0) exitWith {
        ["rejected", _validation # 1] call YCD_fnc_routeResult
    };
    if (!isServer) exitWith {
        [_fnName, _args, _onceKey, _ttl] remoteExecCall ["YCD_fnc_runOnServerOnce", 2];
        ["queued", "server"] call YCD_fnc_routeResult
    };

    private _cacheKey = if (_onceKey isEqualTo "") then {""} else {["server", _fnName, _onceKey] call YCD_fnc_onceCacheKey};
    if !([_cacheKey, _ttl] call YCD_fnc_claimOnceKey) exitWith {
        ["rejected", "duplicate"] call YCD_fnc_routeResult
    };

    [_fnName, _args] call YCD_fnc_callFn
};

YCD_fnc_runOnObjectOwnerOnce = {
    params ["_fnName", "_object", ["_args", []], ["_onceKey", ""], ["_ttl", 3]];

    private _validation = [_fnName, _onceKey, _ttl] call YCD_fnc_validateOnceRequest;
    if !(_validation # 0) exitWith {
        ["rejected", _validation # 1] call YCD_fnc_routeResult
    };
    if (isNull _object) exitWith {
        ["rejected", "invalid_destination"] call YCD_fnc_routeResult
    };

    if (!isServer) exitWith {
        [_fnName, _object, _args, _onceKey, _ttl] remoteExecCall ["YCD_fnc_runOnObjectOwnerOnce", 2];
        ["queued", "server"] call YCD_fnc_routeResult
    };

    if (!local _object && {(owner _object) < 2}) exitWith {
        ["rejected", "invalid_destination"] call YCD_fnc_routeResult
    };
    private _cacheKey = if (_onceKey isEqualTo "") then {""} else {["object", _fnName, _onceKey] call YCD_fnc_onceCacheKey};
    if !([_cacheKey, _ttl] call YCD_fnc_claimOnceKey) exitWith {
        ["rejected", "duplicate"] call YCD_fnc_routeResult
    };

    private _result = [_fnName, _object, _args] call YCD_fnc_runOnObjectOwner;
    if ((_result # 0) isEqualTo "queued") exitWith {
        ["accepted", "object_owner"] call YCD_fnc_routeResult
    };
    _result
};

YCD_fnc_runOnGroupOwnerOnce = {
    params ["_fnName", "_unit", ["_args", []], ["_onceKey", ""], ["_ttl", 3]];

    private _validation = [_fnName, _onceKey, _ttl] call YCD_fnc_validateOnceRequest;
    if !(_validation # 0) exitWith {
        ["rejected", _validation # 1] call YCD_fnc_routeResult
    };
    if (isNull _unit) exitWith {
        ["rejected", "invalid_destination"] call YCD_fnc_routeResult
    };
    private _group = group _unit;
    if (isNull _group) exitWith {
        ["rejected", "invalid_destination"] call YCD_fnc_routeResult
    };

    if (!isServer) exitWith {
        [_fnName, _unit, _args, _onceKey, _ttl] remoteExecCall ["YCD_fnc_runOnGroupOwnerOnce", 2];
        ["queued", "server"] call YCD_fnc_routeResult
    };

    if (!local _group && {(groupOwner _group) < 2}) exitWith {
        ["rejected", "invalid_destination"] call YCD_fnc_routeResult
    };
    private _cacheKey = if (_onceKey isEqualTo "") then {""} else {["group", _fnName, _onceKey] call YCD_fnc_onceCacheKey};
    if !([_cacheKey, _ttl] call YCD_fnc_claimOnceKey) exitWith {
        ["rejected", "duplicate"] call YCD_fnc_routeResult
    };

    private _result = [_fnName, _unit, _args] call YCD_fnc_runOnGroupOwner;
    if ((_result # 0) isEqualTo "queued") exitWith {
        ["accepted", "group_owner"] call YCD_fnc_routeResult
    };
    _result
};

YCD_fnc_filterPlayerUnits = {
    params [["_units", []]];
    if !(_units isEqualType []) exitWith {[]};
    (_units arrayIntersect allPlayers) select {
        alive _x
        && {_x isKindOf "Man"}
        && {!(_x isKindOf "HeadlessClient_F")}
    }
};
YCD_fnc_targetsFromSide = {
    params ["_side"];

    [(allPlayers select {side _x isEqualTo _side})] call YCD_fnc_filterPlayerUnits
};

YCD_fnc_resolveTargets = {
    private _scope = if (_this isEqualTo []) then {0} else {_this # 0};

    private _candidates = [];
    switch (typeName _scope) do {
        case "SIDE": {
            _candidates = allPlayers select {side _x isEqualTo _scope};
        };
        case "ARRAY": {
            _candidates = _scope;
        };
        case "OBJECT": {
            if (!isNull _scope) then {_candidates = [_scope];};
        };
        case "SCALAR": {
            if (_scope == 0) then {_candidates = allPlayers;};
        };
    };

    [_candidates] call YCD_fnc_filterPlayerUnits
};
YCD_fnc_emitToTargets = {
    params ["_command", "_payload", ["_scope", 0], ["_onceKey", ""], ["_ttl", 3]];

    if !([_command] call YCD_fnc_hasFn) exitWith {
        ["rejected", "unknown_operation"] call YCD_fnc_routeResult
    };
    if (_onceKey isNotEqualTo "" && {_ttl <= 0}) exitWith {
        ["rejected", "invalid_ttl"] call YCD_fnc_routeResult
    };
    if (!isServer) exitWith {
        [_command, _payload, _scope, _onceKey, _ttl] remoteExecCall ["YCD_fnc_emitToTargets", 2];
        ["queued", "server"] call YCD_fnc_routeResult
    };

    private _targets = [_scope] call YCD_fnc_resolveTargets;
    if (_targets isEqualTo []) exitWith {
        ["rejected", "no_recipients"] call YCD_fnc_routeResult
    };
    private _cacheKey = if (_onceKey isEqualTo "") then {""} else {["emit", _command, _onceKey] call YCD_fnc_onceCacheKey};
    if !([_cacheKey, _ttl] call YCD_fnc_claimOnceKey) exitWith {
        ["rejected", "duplicate"] call YCD_fnc_routeResult
    };

    _payload remoteExecCall [_command, _targets];
    ["accepted", "recipients"] call YCD_fnc_routeResult
};

YCD_fnc_sideFromVehicleConfig = {
    params ["_object"];
    if (isNull _object) exitWith {sideUnknown};
    private _cfgSide = getNumber (configFile >> "CfgVehicles" >> typeOf _object >> "side");
    switch (_cfgSide) do {
        case 0: {east};
        case 1: {west};
        case 2: {resistance};
        case 3: {civilian};
        default {sideUnknown};
    };
};

YCD_fnc_normalizeRadioSpeaker = {
    params ["_speaker"];

    if (_speaker isEqualType []) exitWith {_speaker};

    if (_speaker isEqualType sideUnknown) exitWith {
        [_speaker, "Base"]
    };

    if (_speaker isEqualType objNull) exitWith {
        if (isNull _speaker) exitWith {[sideUnknown, "Base"]};

        private _radioSide = sideUnknown;
        private _voice = _speaker;
        if !(_voice isKindOf "Man") then {
            private _cmd = effectiveCommander _voice;
            if (!isNull _cmd) then {
                _voice = _cmd;
            } else {
                private _drv = driver _speaker;
                if (!isNull _drv) then {
                    _voice = _drv;
                };
            };
        };

        if (!isNull _voice && {_voice isKindOf "Man"}) then {
            _radioSide = side _voice;
        };
        if (_radioSide isEqualTo sideUnknown) then {
            _radioSide = side _speaker;
        };
        if (_radioSide isEqualTo sideUnknown) then {
            _radioSide = [_speaker] call YCD_fnc_sideFromVehicleConfig;
        };

        [_radioSide, "Base"]
    };

    _speaker
};

YCD_fnc_playSideChatLocal = {
    params ["_speaker", "_message", ["_settingName", ""]];
    if (_settingName isNotEqualTo "" && {!(missionNamespace getVariable [_settingName, true])}) exitWith {false};
    _speaker sideChat _message;
    true
};

YCD_fnc_isRadioMessageRegistered = {
    params ["_message"];

    if (_message isEqualTo "") exitWith {false};

    private _registered = false;
    {
        if (_x isEqualTo _message) exitWith {
            _registered = true;
        };
    } forEach getArray (configFile >> "CfgRadio" >> "sounds");

    _registered
};

YCD_fnc_getRadioMessageMeta = {
    params ["_message"];

    private _cfg = configFile >> "CfgRadio" >> _message;
    if (!isClass _cfg) exitWith {["", ""]};

    private _soundDef = getArray (_cfg >> "sound");
    private _soundPath = if ((count _soundDef) > 0) then {_soundDef select 0} else {""};
    private _title = getText (_cfg >> "title");

    [_soundPath, _title]
};

YCD_fnc_playSideRadioLocal = {
    params ["_speaker", "_message", ["_settingName", ""]];
    if (_settingName isNotEqualTo "" && {!(missionNamespace getVariable [_settingName, true])}) exitWith {false};

    private _radioSpeaker = [_speaker] call YCD_fnc_normalizeRadioSpeaker;

    if (_message isEqualType "" && {!(_message isEqualTo "")}) then {
        private _radioMeta = [_message] call YCD_fnc_getRadioMessageMeta;
        _radioMeta params ["_soundPath", "_title"];

        if (_soundPath isNotEqualTo "") then {
            if ([_message] call YCD_fnc_isRadioMessageRegistered) exitWith {
                _radioSpeaker sideRadio _message;
                true
            };

            _radioSpeaker sideRadio (format ["#%1", _soundPath]);
            if (_title isNotEqualTo "") then {
                _radioSpeaker sideChat _title;
            };
            true
        };
    };

    _radioSpeaker sideRadio _message;
    true
};

YCD_fnc_emitSideChat = {
    params ["_speaker", "_message", ["_scope", 0], ["_onceKey", ""], ["_ttl", 3], ["_settingName", ""]];
    ["YCD_fnc_playSideChatLocal", [_speaker, _message, _settingName], _scope, _onceKey, _ttl] call YCD_fnc_emitToTargets
};

YCD_fnc_emitSideRadio = {
    params ["_speaker", "_message", ["_scope", 0], ["_onceKey", ""], ["_ttl", 3], ["_settingName", ""]];
    ["YCD_fnc_playSideRadioLocal", [_speaker, _message, _settingName], _scope, _onceKey, _ttl] call YCD_fnc_emitToTargets
};

YCD_fnc_showDebugLine = {
    params ["_line", ["_settingName", "YSF_showDebugMessages"]];

    if (missionNamespace getVariable [_settingName, false]) then {
        systemChat _line;
    };
};

YCD_fnc_debugMsg = {
    params ["_msg", ["_prefix", "YCD"], ["_settingName", "YSF_showDebugMessages"]];

    if (!isServer) exitWith {
        [_msg, _prefix, _settingName] remoteExecCall ["YCD_fnc_debugMsg", 2];
    };

    private _line = format ["[%1] %2", _prefix, _msg];

    [_line, _settingName] remoteExecCall ["YCD_fnc_showDebugLine", 0];
    diag_log _line;
};

YCD_fnc_notifyCurator = {
    params ["_msg", ["_title", "Notification"], ["_duration", 5], ["_targets", 0], ["_onceKey", ""], ["_ttl", 3]];

    if (_onceKey isNotEqualTo "" && {_ttl <= 0}) exitWith {
        ["rejected", "invalid_ttl"] call YCD_fnc_routeResult
    };
    if (!isServer) exitWith {
        [_msg, _title, _duration, _targets, _onceKey, _ttl] remoteExecCall ["YCD_fnc_notifyCurator", 2];
        ["queued", "server"] call YCD_fnc_routeResult
    };

    private _resolvedTargets = [_targets] call YCD_fnc_resolveTargets;
    if (_resolvedTargets isEqualTo []) exitWith {
        ["rejected", "no_recipients"] call YCD_fnc_routeResult
    };
    private _cacheKey = if (_onceKey isEqualTo "") then {""} else {["notify", "YCD_fnc_notifyCurator", _onceKey] call YCD_fnc_onceCacheKey};
    if !([_cacheKey, _ttl] call YCD_fnc_claimOnceKey) exitWith {
        ["rejected", "duplicate"] call YCD_fnc_routeResult
    };

    [objNull, _msg] remoteExecCall ["BIS_fnc_showCuratorFeedbackMessage", _resolvedTargets];
    [_title, _msg, _duration] remoteExecCall ["BIS_fnc_curatorHint", _resolvedTargets];
    ["accepted", "recipients"] call YCD_fnc_routeResult
};

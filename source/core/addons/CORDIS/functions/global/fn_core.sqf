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
    missionNamespace getVariable [_fnName, {}]
};

YCD_fnc_callFn = {
    params ["_fnName", ["_args", []]];

    private _fn = [_fnName] call YCD_fnc_getFn;
    _args call _fn
};

YCD_fnc_runOnServer = {
    params ["_fnName", ["_args", []]];

    if (isServer) exitWith {
        [_fnName, _args] call YCD_fnc_callFn
    };

    _args remoteExecCall [_fnName, 2];
    nil
};

YCD_fnc_runOnObjectOwner = {
    params ["_fnName", "_object", ["_args", []]];

    if (isNull _object) exitWith {nil};

    private _target = owner _object;
    if (_target < 0) exitWith {nil};

    if (local _object) exitWith {
        [_fnName, _args] call YCD_fnc_callFn
    };

    _args remoteExecCall [_fnName, _target];
    nil
};

YCD_fnc_runOnGroupOwner = {
    params ["_fnName", "_unit", ["_args", []]];

    if (isNull _unit) exitWith {nil};

    private _group = group _unit;
    if (isNull _group) exitWith {nil};

    private _target = groupOwner _group;
    if (_target < 0) exitWith {nil};

    if (local _unit) exitWith {
        [_fnName, _args] call YCD_fnc_callFn
    };

    _args remoteExecCall [_fnName, _target];
    nil
};

YCD_fnc_pruneLocalOnceCache = {
    private _cache = missionNamespace getVariable ["YCD_localOnceCache", createHashMap];
    private _now = diag_tickTime;

    {
        if (_y <= _now) then {
            _cache deleteAt _x;
        };
    } forEach _cache;

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

    {
        if (_y <= _now) then {
            _cache deleteAt _x;
        };
    } forEach _cache;

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

    if (!isServer) exitWith {
        [_fnName, _args, _onceKey, _ttl] remoteExecCall ["YCD_fnc_runOnServerOnce", 2];
        true
    };

    if !([_onceKey, _ttl] call YCD_fnc_claimOnceKey) exitWith {false};

    [_fnName, _args] call YCD_fnc_callFn;
    true
};

YCD_fnc_runOnObjectOwnerOnce = {
    params ["_fnName", "_object", ["_args", []], ["_onceKey", ""], ["_ttl", 3]];

    if (isNull _object) exitWith {false};

    if (!isServer) exitWith {
        [_fnName, _object, _args, _onceKey, _ttl] remoteExecCall ["YCD_fnc_runOnObjectOwnerOnce", 2];
        true
    };

    if !([_onceKey, _ttl] call YCD_fnc_claimOnceKey) exitWith {false};

    [_fnName, _object, _args] call YCD_fnc_runOnObjectOwner;
    true
};

YCD_fnc_runOnGroupOwnerOnce = {
    params ["_fnName", "_unit", ["_args", []], ["_onceKey", ""], ["_ttl", 3]];

    if (isNull _unit) exitWith {false};

    if (!isServer) exitWith {
        [_fnName, _unit, _args, _onceKey, _ttl] remoteExecCall ["YCD_fnc_runOnGroupOwnerOnce", 2];
        true
    };

    if !([_onceKey, _ttl] call YCD_fnc_claimOnceKey) exitWith {false};

    [_fnName, _unit, _args] call YCD_fnc_runOnGroupOwner;
    true
};

YCD_fnc_filterPlayerUnits = {
    params ["_units"];

    if (_units isEqualType objNull) exitWith {
        if (isNull _units) then {
            []
        } else {
            if (isPlayer _units && {alive _units}) then {[_units]} else {[]}
        }
    };

    if !(_units isEqualType []) exitWith {[]};

    _units select {isPlayer _x && {alive _x}}
};

YCD_fnc_targetsFromSide = {
    params ["_side"];

    (allPlayers select {alive _x && {side _x isEqualTo _side}}) call YCD_fnc_filterPlayerUnits
};

YCD_fnc_resolveTargets = {
    params [["_scope", 0]];

    if (_scope isEqualType sideUnknown) exitWith {
        [_scope] call YCD_fnc_targetsFromSide
    };

    if (_scope isEqualType []) exitWith {
        _scope call YCD_fnc_filterPlayerUnits
    };

    if (_scope isEqualType objNull) exitWith {
        if (isNull _scope) then {[]} else {_scope call YCD_fnc_filterPlayerUnits}
    };

    if (_scope isEqualType 0) then {
        if (_scope == 0) exitWith {allPlayers select {alive _x}};
    };

    []
};

YCD_fnc_emitToTargets = {
    params ["_command", "_payload", ["_scope", 0], ["_onceKey", ""], ["_ttl", 3]];

    if (!isServer) exitWith {
        [_command, _payload, _scope, _onceKey, _ttl] remoteExecCall ["YCD_fnc_emitToTargets", 2];
    };

    if !([_onceKey, _ttl] call YCD_fnc_claimOnceKey) exitWith {false};

    private _targets = [_scope] call YCD_fnc_resolveTargets;
    if (_targets isEqualTo []) exitWith {false};

    _payload remoteExecCall [_command, _targets];
    true
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

    if (!isServer) exitWith {
        [_msg, _title, _duration, _targets, _onceKey, _ttl] remoteExecCall ["YCD_fnc_notifyCurator", 2];
    };

    if !([_onceKey, _ttl] call YCD_fnc_claimOnceKey) exitWith {false};

    private _resolvedTargets = [_targets] call YCD_fnc_resolveTargets;
    if (_resolvedTargets isEqualTo []) then {
        _resolvedTargets = allPlayers select {alive _x};
    };

    [objNull, _msg] remoteExecCall ["BIS_fnc_showCuratorFeedbackMessage", _resolvedTargets];
    [_title, _msg, _duration] remoteExecCall ["BIS_fnc_curatorHint", _resolvedTargets];
    true
};

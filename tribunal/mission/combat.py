"""Product-neutral SQF helpers for correlated combat evidence."""


def combat_observer_sqf() -> str:
    """Return mission-local fire, trajectory, hit, and damage observers."""

    return r'''
TRIBUNAL_fnc_combatObserverStart = {
    params ["_token"];
    private _state = createHashMapFromArray [
        ["token", _token], ["fires", []], ["hits", []], ["damage", []],
        ["kills", []], ["sources", []], ["targets", []], ["started", diag_tickTime]
    ];
    missionNamespace setVariable [format ["TRIBUNAL_COMBAT_%1", _token], _state];
    _state
};

TRIBUNAL_fnc_combatObserverState = {
    params ["_token"];
    missionNamespace getVariable [format ["TRIBUNAL_COMBAT_%1", _token], createHashMap]
};

TRIBUNAL_fnc_combatObserveSource = {
    params ["_token", "_source"];
    if (isNull _source) exitWith {false};
    private _state = [_token] call TRIBUNAL_fnc_combatObserverState;
    if ((count _state) isEqualTo 0) exitWith {false};
    private _sources = _state getOrDefault ["sources", []];
    _sources pushBackUnique (netId _source);
    _state set ["sources", _sources];
    _source setVariable ["TRIBUNAL_COMBAT_TOKEN", _token];
    private _old = _source getVariable ["TRIBUNAL_COMBAT_FIRED_EH", -1];
    if (_old >= 0) then {_source removeEventHandler ["Fired", _old];};
    private _eh = _source addEventHandler ["Fired", {
        params ["_source", "_weapon", "_muzzle", "_mode", "_ammo", "_magazine", "_projectile", "_gunner"];
        private _token = _source getVariable ["TRIBUNAL_COMBAT_TOKEN", ""];
        if (_token isEqualTo "") exitWith {};
        private _state = [_token] call TRIBUNAL_fnc_combatObserverState;
        private _controller = effectiveCommander _source;
        if (isNull _controller) then {_controller = _gunner;};
        private _assigned = if (isNull _controller) then {objNull} else {assignedTarget _controller};
        private _event = createHashMapFromArray [
            ["source", netId _source], ["sourceClass", typeOf _source],
            ["sourceLocal", local _source], ["sourceOwner", owner _source],
            ["gunner", if (isNull _gunner) then {""} else {netId _gunner}],
            ["weapon", _weapon], ["muzzle", _muzzle], ["mode", _mode],
            ["ammo", _ammo], ["magazine", _magazine],
            ["projectile", if (isNull _projectile) then {""} else {netId _projectile}],
            ["projectileObject", _projectile],
            ["projectileLocal", !isNull _projectile && {local _projectile}],
            ["projectileOwner", if (isNull _projectile) then {-1} else {owner _projectile}],
            ["assignedTarget", if (isNull _assigned) then {""} else {netId _assigned}],
            ["initialPosition", if (isNull _projectile) then {[]} else {getPosASL _projectile}],
            ["initialVelocity", if (isNull _projectile) then {[]} else {velocity _projectile}],
            ["samples", []], ["lastPosition", []], ["terminated", false],
            ["firedAt", diag_tickTime], ["executionMachine", if (isServer) then {"server"} else {"client"}]
        ];
        private _fires = _state getOrDefault ["fires", []];
        _fires pushBack _event;
        _state set ["fires", _fires];
        missionNamespace setVariable [format ["TRIBUNAL_COMBAT_%1", _token], _state];
        diag_log format ["TRIBUNAL_COMBAT|%1|FIRED|source=%2|target=%3|weapon=%4|ammo=%5|projectile=%6|sourceLocal=%7|projectileLocal=%8", _token, netId _source, _event get "assignedTarget", _weapon, _ammo, _event get "projectile", local _source, _event get "projectileLocal"];
        [_token, _event, _projectile] spawn {
            params ["_token", "_event", "_projectile"];
            private _deadline = diag_tickTime + 120;
            while {!isNull _projectile && {diag_tickTime < _deadline}} do {
                private _samples = _event getOrDefault ["samples", []];
                private _position = getPosASL _projectile;
                _samples pushBack [diag_tickTime, _position, velocity _projectile, local _projectile];
                _event set ["samples", _samples];
                _event set ["lastPosition", _position];
                uiSleep 0.05;
            };
            _event set ["terminated", isNull _projectile];
            _event set ["terminatedAt", diag_tickTime];
            diag_log format ["TRIBUNAL_COMBAT|%1|TERMINAL|projectile=%2|samples=%3|last=%4", _token, _event getOrDefault ["projectile", ""], count (_event getOrDefault ["samples", []]), _event getOrDefault ["lastPosition", []]];
        };
    }];
    _source setVariable ["TRIBUNAL_COMBAT_FIRED_EH", _eh];
    true
};

TRIBUNAL_fnc_combatObserveTarget = {
    params ["_token", "_target"];
    if (isNull _target) exitWith {false};
    private _state = [_token] call TRIBUNAL_fnc_combatObserverState;
    if ((count _state) isEqualTo 0) exitWith {false};
    private _targets = _state getOrDefault ["targets", []];
    _targets pushBackUnique (netId _target);
    _state set ["targets", _targets];
    _target setVariable ["TRIBUNAL_COMBAT_TOKEN", _token];
    private _damageEh = _target addEventHandler ["HandleDamage", {
        params ["_target", "_selection", "_damage", "_source", "_projectile", "_hitIndex", "_instigator", "_hitPoint"];
        private _token = _target getVariable ["TRIBUNAL_COMBAT_TOKEN", ""];
        if (_token isNotEqualTo "") then {
            private _state = [_token] call TRIBUNAL_fnc_combatObserverState;
            private _events = _state getOrDefault ["damage", []];
            _events pushBack [diag_tickTime, netId _target, _selection, _damage,
                if (isNull _source) then {""} else {netId _source}, _projectile,
                if (isNull _instigator) then {""} else {netId _instigator}, _hitPoint,
                local _target, owner _target];
            _state set ["damage", _events];
            missionNamespace setVariable [format ["TRIBUNAL_COMBAT_%1", _token], _state];
        };
        _damage
    }];
    private _hitEh = _target addEventHandler ["HitPart", {
        private _first = _this param [0, objNull];
        private _target = if (_first isEqualType []) then {_first param [0, objNull]} else {_first};
        if (isNull _target) exitWith {};
        private _token = _target getVariable ["TRIBUNAL_COMBAT_TOKEN", ""];
        if (_token isEqualTo "") exitWith {};
        private _state = [_token] call TRIBUNAL_fnc_combatObserverState;
        private _hits = _state getOrDefault ["hits", []];
        _hits pushBack [diag_tickTime, netId _target, str _this, local _target, owner _target];
        _state set ["hits", _hits];
        missionNamespace setVariable [format ["TRIBUNAL_COMBAT_%1", _token], _state];
    }];
    private _killedEh = _target addEventHandler ["Killed", {
        params ["_target", "_killer", "_instigator", "_useEffects"];
        private _token = _target getVariable ["TRIBUNAL_COMBAT_TOKEN", ""];
        if (_token isEqualTo "") exitWith {};
        private _state = [_token] call TRIBUNAL_fnc_combatObserverState;
        private _kills = _state getOrDefault ["kills", []];
        _kills pushBack [diag_tickTime, netId _target,
            if (isNull _killer) then {""} else {netId _killer},
            if (isNull _instigator) then {""} else {netId _instigator}, _useEffects];
        _state set ["kills", _kills];
        missionNamespace setVariable [format ["TRIBUNAL_COMBAT_%1", _token], _state];
    }];
    _target setVariable ["TRIBUNAL_COMBAT_TARGET_EHS", [_damageEh, _hitEh, _killedEh]];
    true
};

TRIBUNAL_fnc_combatObserverStop = {
    params ["_token"];
    private _state = [_token] call TRIBUNAL_fnc_combatObserverState;
    {
        private _source = objectFromNetId _x;
        if (!isNull _source) then {
            private _eh = _source getVariable ["TRIBUNAL_COMBAT_FIRED_EH", -1];
            if (_eh >= 0) then {_source removeEventHandler ["Fired", _eh];};
            _source setVariable ["TRIBUNAL_COMBAT_FIRED_EH", -1];
            _source setVariable ["TRIBUNAL_COMBAT_TOKEN", ""];
        };
    } forEach (_state getOrDefault ["sources", []]);
    {
        private _target = objectFromNetId _x;
        if (!isNull _target) then {
            private _handlers = _target getVariable ["TRIBUNAL_COMBAT_TARGET_EHS", []];
            if (count _handlers >= 3) then {
                _target removeEventHandler ["HandleDamage", _handlers # 0];
                _target removeEventHandler ["HitPart", _handlers # 1];
                _target removeEventHandler ["Killed", _handlers # 2];
            };
            _target setVariable ["TRIBUNAL_COMBAT_TARGET_EHS", []];
            _target setVariable ["TRIBUNAL_COMBAT_TOKEN", ""];
        };
    } forEach (_state getOrDefault ["targets", []]);
    _state
};
'''

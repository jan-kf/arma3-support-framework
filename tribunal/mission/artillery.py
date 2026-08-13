"""Generic artillery fire observation and spatial evidence helpers."""

from __future__ import annotations

from dataclasses import dataclass
from math import cos, hypot, radians, sin
from statistics import fmean
from typing import Iterable


@dataclass(frozen=True)
class SpatialEvidence:
    count: int
    centroid: tuple[float, float]
    mean_radial_error: float
    maximum_radial_error: float
    along_axis: tuple[float, ...]
    perpendicular_error: tuple[float, ...]


def spatial_evidence(
    points: Iterable[tuple[float, float]],
    target: tuple[float, float],
    bearing_degrees: float = 0.0,
) -> SpatialEvidence:
    """Describe impact geometry without demanding impossible exact impacts."""

    samples = tuple(points)
    if not samples:
        raise ValueError("spatial evidence requires at least one point")
    cx = fmean(point[0] for point in samples)
    cy = fmean(point[1] for point in samples)
    radial = tuple(hypot(point[0] - target[0], point[1] - target[1]) for point in samples)
    angle = radians(bearing_degrees)
    axis = (sin(angle), cos(angle))
    normal = (axis[1], -axis[0])
    along = tuple((point[0] - target[0]) * axis[0] + (point[1] - target[1]) * axis[1] for point in samples)
    perpendicular = tuple(abs((point[0] - target[0]) * normal[0] + (point[1] - target[1]) * normal[1]) for point in samples)
    return SpatialEvidence(
        len(samples),
        (cx, cy),
        fmean(radial),
        max(radial),
        along,
        perpendicular,
    )


def artillery_observer_sqf() -> str:
    """Return mission-local, product-neutral firing/trajectory collection SQF."""

    return r'''
TRIBUNAL_fnc_artilleryObserverStart = {
    params ["_token"];
    private _key = format ["TRIBUNAL_ARTILLERY_%1", _token];
    private _state = createHashMapFromArray [["token", _token], ["events", []], ["pendingArtillery", []], ["sources", []], ["started", diag_tickTime]];
    missionNamespace setVariable [_key, _state];
    missionNamespace setVariable ["TRIBUNAL_ARTILLERY_ACTIVE", _token];
    if ((missionNamespace getVariable ["TRIBUNAL_ARTILLERY_MISSION_EH", -1]) < 0) then {
        private _missionEh = addMissionEventHandler ["ArtilleryShellFired", {
            params ["_vehicle", "_weapon", "_ammo", "_gunner", "_instigator", "_artilleryTarget", "_targetPosition", "_shell"];
            private _token = missionNamespace getVariable ["TRIBUNAL_ARTILLERY_ACTIVE", ""];
            if (_token isEqualTo "") exitWith {};
            private _state = missionNamespace getVariable [format ["TRIBUNAL_ARTILLERY_%1", _token], createHashMap];
            private _uid = if (isNull _shell) then {""} else {netId _shell};
            private _event = (_state getOrDefault ["events", []]) select {
                ((_x getOrDefault ["projectileObject", objNull]) isEqualTo _shell)
                || {_uid isNotEqualTo "" && {_uid isNotEqualTo "0:0"} && {(_x getOrDefault ["projectile", ""]) isEqualTo _uid}}
            };
            if !(_event isEqualTo []) then {
                (_event # 0) set ["artilleryEvent", true];
                (_event # 0) set ["artilleryTarget", _artilleryTarget];
                (_event # 0) set ["targetPosition", +_targetPosition];
                (_event # 0) set ["artilleryAmmo", _ammo];
                (_event # 0) set ["instigator", if (isNull _instigator) then {""} else {netId _instigator}];
            } else {
                private _pending = _state getOrDefault ["pendingArtillery", []];
                _pending pushBack [_shell, _artilleryTarget, +_targetPosition, _ammo, if (isNull _instigator) then {""} else {netId _instigator}];
                _state set ["pendingArtillery", _pending];
                missionNamespace setVariable [format ["TRIBUNAL_ARTILLERY_%1", _token], _state];
            };
        }];
        missionNamespace setVariable ["TRIBUNAL_ARTILLERY_MISSION_EH", _missionEh];
    };
    _state
};

TRIBUNAL_fnc_artilleryObserveSource = {
    params ["_token", "_source", ["_requestedPositions", []]];
    if (isNull _source) exitWith {false};
    private _key = format ["TRIBUNAL_ARTILLERY_%1", _token];
    private _state = missionNamespace getVariable [_key, createHashMap];
    if ((count _state) isEqualTo 0) exitWith {false};
    private _sources = _state getOrDefault ["sources", []];
    _sources pushBackUnique (netId _source);
    _state set ["sources", _sources];
    _source setVariable ["TRIBUNAL_ARTILLERY_TOKEN", _token];
    _source setVariable ["TRIBUNAL_ARTILLERY_REQUESTED", +_requestedPositions];
    private _old = _source getVariable ["TRIBUNAL_ARTILLERY_FIRED_EH", -1];
    if (_old >= 0) then {_source removeEventHandler ["Fired", _old]};
    private _eh = _source addEventHandler ["Fired", {
        params ["_source", "_weapon", "_muzzle", "_mode", "_ammo", "_magazine", "_projectile", "_gunner"];
        private _token = _source getVariable ["TRIBUNAL_ARTILLERY_TOKEN", ""];
        if (_token isEqualTo "") exitWith {};
        private _key = format ["TRIBUNAL_ARTILLERY_%1", _token];
        private _state = missionNamespace getVariable [_key, createHashMap];
        private _events = _state getOrDefault ["events", []];
        private _index = count _events;
        private _requested = _source getVariable ["TRIBUNAL_ARTILLERY_REQUESTED", []];
        private _expected = _requested param [_index, []];
        private _uid = if (isNull _projectile) then {""} else {netId _projectile};
        private _event = createHashMapFromArray [
            ["token", _token], ["index", _index], ["source", netId _source], ["sourceClass", typeOf _source],
            ["weapon", _weapon], ["muzzle", _muzzle], ["mode", _mode], ["ammo", _ammo], ["magazine", _magazine],
            ["projectile", _uid], ["projectileObject", _projectile], ["projectileClass", if (isNull _projectile) then {""} else {typeOf _projectile}],
            ["expectedPosition", +_expected], ["firedAt", diag_tickTime], ["sourceLocal", local _source],
            ["projectileLocal", !isNull _projectile && {local _projectile}], ["executionMachine", if (isServer) then {"server"} else {"client"}],
            ["initialPosition", if (isNull _projectile) then {[]} else {getPosASL _projectile}],
            ["initialVelocity", if (isNull _projectile) then {[]} else {velocity _projectile}], ["samples", []],
            ["lastPosition", []], ["terminated", false], ["terminatedAt", -1], ["artilleryEvent", false]
        ];
        private _pending = _state getOrDefault ["pendingArtillery", []];
        private _pendingIndex = _pending findIf {(_x # 0) isEqualTo _projectile};
        if (_pendingIndex >= 0) then {
            private _artillery = _pending deleteAt _pendingIndex;
            _event set ["artilleryEvent", true];
            _event set ["artilleryTarget", _artillery # 1];
            _event set ["targetPosition", +(_artillery # 2)];
            _event set ["artilleryAmmo", _artillery # 3];
            _event set ["instigator", _artillery # 4];
            _state set ["pendingArtillery", _pending];
        };
        _events pushBack _event;
        _state set ["events", _events];
        missionNamespace setVariable [_key, _state];
        diag_log format ["TRIBUNAL_ARTILLERY|%1|FIRED|index=%2|source=%3|weapon=%4|magazine=%5|ammo=%6|projectile=%7|localSource=%8|localProjectile=%9", _token, _index, netId _source, _weapon, _magazine, _ammo, _uid, local _source, !isNull _projectile && {local _projectile}];
        [_token, _event, _projectile] spawn {
            params ["_token", "_event", "_projectile"];
            private _deadline = diag_tickTime + 180; private _nextSample = diag_tickTime;
            while {!isNull _projectile && {diag_tickTime < _deadline}} do {
                if (diag_tickTime >= _nextSample) then {
                    private _samples = _event getOrDefault ["samples", []];
                    private _position = getPosASL _projectile;
                    _samples pushBack [diag_tickTime, _position, velocity _projectile, local _projectile];
                    _event set ["samples", _samples];
                    _event set ["lastPosition", _position];
                    _nextSample = diag_tickTime + 0.05;
                };
                uiSleep 0.01;
            };
            _event set ["terminated", isNull _projectile];
            _event set ["terminatedAt", diag_tickTime];
            diag_log format ["TRIBUNAL_ARTILLERY|%1|TERMINAL|projectile=%2|terminated=%3|last=%4|samples=%5", _token, _event getOrDefault ["projectile", ""], _event getOrDefault ["terminated", false], _event getOrDefault ["lastPosition", []], count (_event getOrDefault ["samples", []])];
        };
    }];
    _source setVariable ["TRIBUNAL_ARTILLERY_FIRED_EH", _eh];
    true
};

TRIBUNAL_fnc_artilleryObserverState = {
    params ["_token"];
    missionNamespace getVariable [format ["TRIBUNAL_ARTILLERY_%1", _token], createHashMap]
};

TRIBUNAL_fnc_artilleryObserverStop = {
    params ["_token"];
    private _state = [_token] call TRIBUNAL_fnc_artilleryObserverState;
    {
        private _source = objectFromNetId _x;
        if (!isNull _source) then {
            private _eh = _source getVariable ["TRIBUNAL_ARTILLERY_FIRED_EH", -1];
            if (_eh >= 0) then {_source removeEventHandler ["Fired", _eh]};
            _source setVariable ["TRIBUNAL_ARTILLERY_FIRED_EH", -1];
            _source setVariable ["TRIBUNAL_ARTILLERY_TOKEN", ""];
        };
    } forEach (_state getOrDefault ["sources", []]);
    if ((missionNamespace getVariable ["TRIBUNAL_ARTILLERY_ACTIVE", ""]) isEqualTo _token) then {missionNamespace setVariable ["TRIBUNAL_ARTILLERY_ACTIVE", ""]};
    _state
};
'''

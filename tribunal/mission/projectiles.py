"""Generic Arma projectile fixtures used by Tribunal scenarios."""
from __future__ import annotations

def direct_fixture_sqf() -> str:
    """Mission-local generic deterministic direct-injection APIs."""
    return r'''
TRIBUNAL_fnc_directProjectileLaunch = {
    params ["_class", "_positionASL", "_direction", ["_speed", 250], ["_label", "projectile"], ["_target", objNull], ["_minimumTerrainClearance", 0]];
    private _requestedPosition = +_positionASL;
    private _terrain = getTerrainHeightASL _requestedPosition;
    if ((_requestedPosition # 2) < (_terrain + _minimumTerrainClearance)) then { _requestedPosition set [2, _terrain + _minimumTerrainClearance]; };
    private _requestedDirection = vectorNormalized _direction;
    private _requestedVelocity = _requestedDirection vectorMultiply _speed;
    private _executionMachine = if (isServer) then {"server"} else {"client"};
    private _hitKey = format ["TRIBUNAL_PROJECTILE_HIT_%1", _label];
    missionNamespace setVariable [_hitKey, false];
    if (!isNull _target) then { _target addEventHandler ["HitPart", compile format ["missionNamespace setVariable ['%1', true];", _hitKey]]; };
    // CAN_COLLIDE finishes construction synchronously. Default construction may
    // overwrite setters on its first simulation frame with default propulsion.
    private _projectile = createVehicle [_class, ASLToATL _requestedPosition, [], 0, "CAN_COLLIDE"];
    _projectile setPosASL _requestedPosition;
    _projectile setVectorDirAndUp [_requestedDirection, [0, 0, 1]];
    _projectile setVelocity _requestedVelocity;
    private _observedPosition = getPosASL _projectile;
    private _observedDirection = vectorDir _projectile;
    private _observedUp = vectorUp _projectile;
    private _observedVelocity = velocity _projectile;
    private _initial = [_observedPosition, _observedDirection, _observedUp, _observedVelocity, vectorMagnitude _observedVelocity, local _projectile, diag_frameNo, diag_tickTime];
    private _uid = if (isNull _projectile) then {""} else {netId _projectile};
    private _positionError = _requestedPosition distance _observedPosition;
    private _directionError = _requestedDirection distance _observedDirection;
    private _velocityError = _requestedVelocity distance _observedVelocity;
    private _launchVerified = false;
    if (!isNull _projectile && {_uid isNotEqualTo ""} && {local _projectile} && {_positionError <= 0.05} && {_directionError <= 0.01} && {_velocityError <= 1}) then { _launchVerified = true; };
    private _evidence = [_uid, _initial, _requestedPosition, _requestedDirection, _requestedVelocity, _executionMachine, _terrain, (_requestedPosition # 2) - _terrain, _positionError, _directionError, _velocityError];
    missionNamespace setVariable [format ["TRIBUNAL_PROJECTILE_EVIDENCE_%1", _label], _evidence];
    diag_log format ["TRIBUNAL_PROJECTILE|%1|LAUNCH|class=%2|uid=%3|verified=%4|requestedPosition=%5|observedPosition=%6|requestedDirection=%7|observedDirection=%8|requestedVelocity=%9|observedVelocity=%10|local=%11|machine=%12|frame=%13|time=%14", _label, _class, _uid, _launchVerified, _requestedPosition, _observedPosition, _requestedDirection, _observedDirection, _requestedVelocity, _observedVelocity, !isNull _projectile && {local _projectile}, _executionMachine, diag_frameNo, diag_tickTime];
    if (!_launchVerified) exitWith { diag_log format ["TRIBUNAL_PROJECTILE|%1|LAUNCH_FAIL|positionError=%2|directionError=%3|velocityError=%4", _label, _positionError, _directionError, _velocityError]; if (!isNull _projectile) then {deleteVehicle _projectile}; [objNull, _hitKey, false, _evidence] };
    [_label, _projectile, _target, _hitKey] spawn {
        params ["_label", "_projectile", "_target", "_hitKey"]; private _closest = 1e9; private _samples = [];
        for "_sample" from 0 to 20 do { if (isNull _projectile) exitWith {}; private _position = getPosASL _projectile; private _distance = if (isNull _target) then {-1} else {_projectile distance _target}; if (_distance >= 0 && {_distance < _closest}) then {_closest = _distance}; _samples pushBack [_sample, diag_frameNo, diag_tickTime, _position, velocity _projectile, local _projectile, _distance]; if (_sample isEqualTo 0 || {_sample isEqualTo 10} || {_sample isEqualTo 20}) then {diag_log format ["TRIBUNAL_PROJECTILE|%1|SAMPLE|index=%2|uid=%3|position=%4|velocity=%5|speed=%6|local=%7|distance=%8", _label, _sample, netId _projectile, _position, velocity _projectile, vectorMagnitude velocity _projectile, local _projectile, _distance]}; uiSleep 0.005; };
        missionNamespace setVariable [format ["TRIBUNAL_PROJECTILE_TRAJECTORY_%1", _label], [_samples, _closest, missionNamespace getVariable [_hitKey, false], isNull _projectile]];
    };
    [_projectile, _hitKey, true, _evidence]
};
TRIBUNAL_fnc_directProjectileCleanup = { params ["_projectile"]; if (!isNull _projectile) then {deleteVehicle _projectile}; };
'''

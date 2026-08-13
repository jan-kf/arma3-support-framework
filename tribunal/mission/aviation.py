"""Product-neutral SQF helpers for physical aircraft lifecycle evidence."""


def aviation_observer_sqf() -> str:
    """Return mission-local aircraft sampling and evidence helpers."""

    return r'''
TRIBUNAL_fnc_aviationSample = {
    params ["_aircraft", "_destination"];
    private _pilot = driver _aircraft;
    [diag_tickTime, netId _aircraft, getPosATL _aircraft, getPosASL _aircraft,
     velocity _aircraft, vectorMagnitude velocity _aircraft,
     _aircraft distance2D _destination, isTouchingGround _aircraft,
     unitReady _aircraft, alive _aircraft, damage _aircraft,
     local _aircraft, owner _aircraft,
     if (isNull _pilot) then {""} else {netId _pilot},
     !isNull _pilot && {alive _pilot},
     if (isNull _pilot) then {false} else {local _pilot},
     if (isNull _pilot) then {-1} else {owner _pilot},
     count waypoints (group _aircraft)]
};

TRIBUNAL_fnc_observeFlight = {
    params ["_aircraft", "_destination", "_isTerminal", ["_timeout", 180], ["_sampleInterval", 0.5]];
    private _samples = [];
    private _deadline = diag_tickTime + _timeout;
    waitUntil {
        _samples pushBack ([_aircraft, _destination] call TRIBUNAL_fnc_aviationSample);
        uiSleep _sampleInterval;
        isNull _aircraft || {!alive _aircraft}
        || {[_aircraft] call _isTerminal}
        || {diag_tickTime > _deadline}
    };
    _samples
};

TRIBUNAL_fnc_flightEvidence = {
    params ["_samples", "_start", "_destination"];
    if (_samples isEqualTo []) exitWith {createHashMap};
    private _minimumDistance = 1e9;
    private _maximumTravel = 0;
    private _maximumAltitude = 0;
    private _groundSamples = 0;
    {
        private _position = _x # 2;
        _minimumDistance = _minimumDistance min (_x # 6);
        _maximumTravel = _maximumTravel max (_position distance2D _start);
        _maximumAltitude = _maximumAltitude max (_position # 2);
        if (_x # 7) then {_groundSamples = _groundSamples + 1;};
    } forEach _samples;
    private _last = _samples select -1;
    createHashMapFromArray [
        ["samples", count _samples], ["minimumDistance", _minimumDistance],
        ["maximumTravel", _maximumTravel], ["maximumAltitudeATL", _maximumAltitude],
        ["groundSamples", _groundSamples], ["final", _last],
        ["moved", _maximumTravel > 100],
        ["approached", _minimumDistance < ((_start distance2D _destination) * 0.25)],
        ["landed", (_last # 7) && {(_last # 8)} && {(_last # 5) < 2}
            && {(_last # 9)} && {(_last # 10) < 0.5}]
    ]
};
'''

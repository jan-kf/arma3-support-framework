"""Product-neutral map-marker existence, property, and lifecycle evidence.

A marker is a rendered world annotation. Tribunal records which markers exist,
where they are, how they are drawn, and how that set changes over a bounded
window. It never decides what a marker means: the consuming scenario owns the
naming convention it observes and the meaning it assigns.
"""


def marker_observer_sqf() -> str:
    """Return mission-local marker census and lifecycle helpers."""

    return r'''
TRIBUNAL_fnc_markerRecord = {
    params ["_marker"];
    createHashMapFromArray [
        ["name", _marker], ["position", markerPos _marker], ["size", markerSize _marker],
        ["shape", markerShape _marker], ["type", markerType _marker], ["color", markerColor _marker],
        ["alpha", markerAlpha _marker], ["text", markerText _marker], ["brush", markerBrush _marker],
        ["direction", markerDir _marker], ["registered", _marker in allMapMarkers]
    ]
};

TRIBUNAL_fnc_markerNames = {
    params ["_prefix"];
    if (_prefix isEqualTo "") exitWith {+allMapMarkers};
    allMapMarkers select {(_x find _prefix) isEqualTo 0}
};

TRIBUNAL_fnc_markerCensus = {
    params ["_prefix"];
    private _names = [_prefix] call TRIBUNAL_fnc_markerNames;
    private _records = createHashMap;
    { _records set [_x, [_x] call TRIBUNAL_fnc_markerRecord]; } forEach _names;
    createHashMapFromArray [
        ["at", diag_tickTime], ["prefix", _prefix], ["names", _names],
        ["count", count _names], ["records", _records],
        ["machine", if (isServer) then {"server"} else {"client"}]
    ]
};

TRIBUNAL_fnc_markerCensusDiff = {
    params ["_before", "_after"];
    private _old = _before getOrDefault ["names", []];
    private _new = _after getOrDefault ["names", []];
    createHashMapFromArray [
        ["added", _new select {!(_x in _old)}],
        ["removed", _old select {!(_x in _new)}],
        ["retained", _new select {_x in _old}]
    ]
};

// Sample a prefixed marker set until the caller's predicate is satisfied or the
// bound expires. The predicate receives the current census.
TRIBUNAL_fnc_markerObserve = {
    params ["_prefix", "_isTerminal", ["_timeout", 120], ["_sampleInterval", 0.5]];
    private _samples = [];
    private _deadline = diag_tickTime + _timeout;
    waitUntil {
        private _census = [_prefix] call TRIBUNAL_fnc_markerCensus;
        _samples pushBack _census;
        uiSleep _sampleInterval;
        ([_census] call _isTerminal) || {diag_tickTime > _deadline}
    };
    _samples
};

TRIBUNAL_fnc_markerLifecycleEvidence = {
    params ["_samples"];
    if (_samples isEqualTo []) exitWith {createHashMap};
    private _maximum = 0;
    private _peak = _samples # 0;
    private _seen = [];
    {
        private _count = _x getOrDefault ["count", 0];
        if (_count > _maximum) then {_maximum = _count; _peak = _x;};
        { _seen pushBackUnique _x; } forEach (_x getOrDefault ["names", []]);
    } forEach _samples;
    private _final = _samples select -1;
    private _finalNames = _final getOrDefault ["names", []];
    createHashMapFromArray [
        ["samples", count _samples], ["maximumCount", _maximum], ["peak", _peak],
        ["everSeen", _seen], ["finalCount", _final getOrDefault ["count", 0]],
        ["finalNames", _finalNames],
        ["removed", _seen select {!(_x in _finalNames)}],
        ["appeared", _maximum > 0], ["cleared", (_final getOrDefault ["count", 0]) isEqualTo 0]
    ]
};
'''

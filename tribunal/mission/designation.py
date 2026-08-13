"""Product-neutral SQF helpers for target-designation evidence."""


def designation_observer_sqf() -> str:
    """Return mission-local designation identity, locality, and lifetime helpers."""

    return r'''
TRIBUNAL_fnc_designationRecord = {
    params ["_source", "_designation", ["_kind", "laser"]];
    createHashMapFromArray [
        ["time", diag_tickTime], ["kind", _kind],
        ["source", if (isNull _source) then {""} else {netId _source}],
        ["sourceClass", if (isNull _source) then {""} else {typeOf _source}],
        ["sourceLocal", !isNull _source && {local _source}],
        ["sourceOwner", if (isNull _source) then {-1} else {owner _source}],
        ["designation", if (isNull _designation) then {""} else {netId _designation}],
        ["designationClass", if (isNull _designation) then {""} else {typeOf _designation}],
        ["designationLocal", !isNull _designation && {local _designation}],
        ["designationOwner", if (isNull _designation) then {-1} else {owner _designation}],
        ["positionASL", if (isNull _designation) then {[]} else {getPosASL _designation}],
        ["alive", !isNull _designation && {alive _designation}]
    ]
};

TRIBUNAL_fnc_observeDesignation = {
    params ["_source", "_resolve", ["_kind", "laser"], ["_timeout", 10], ["_interval", 0.1]];
    private _samples = [];
    private _deadline = diag_tickTime + (_timeout max 0.1);
    waitUntil {
        private _designation = [_source] call _resolve;
        _samples pushBack ([_source, _designation, _kind] call TRIBUNAL_fnc_designationRecord);
        uiSleep (_interval max 0.02);
        diag_tickTime >= _deadline
    };
    _samples
};

TRIBUNAL_fnc_designationEvidence = {
    params ["_samples"];
    private _present = _samples select {(_x getOrDefault ["designation", ""]) isNotEqualTo ""};
    private _identities = (_present apply {_x getOrDefault ["designation", ""]}) arrayIntersect
        (_present apply {_x getOrDefault ["designation", ""]});
    private _maximumTravel = 0;
    if ((count _present) > 1) then {
        private _origin = (_present select 0) getOrDefault ["positionASL", []];
        {
            private _position = _x getOrDefault ["positionASL", []];
            if ((count _origin) >= 3 && {(count _position) >= 3}) then {
                _maximumTravel = _maximumTravel max (_origin distance _position);
            };
        } forEach _present;
    };
    createHashMapFromArray [
        ["samples", count _samples], ["presentSamples", count _present],
        ["identities", _identities], ["stableIdentity", (count _identities) isEqualTo 1],
        ["maximumTravel", _maximumTravel],
        ["first", if (_samples isEqualTo []) then {createHashMap} else {_samples select 0}],
        ["last", if (_samples isEqualTo []) then {createHashMap} else {_samples select -1}]
    ]
};
'''

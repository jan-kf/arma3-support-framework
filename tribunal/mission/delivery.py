"""Product-neutral SQF helpers for physical cargo-delivery evidence."""


def delivery_observer_sqf() -> str:
    """Return normalized inventory and paired cargo/parachute observers."""

    return r'''
TRIBUNAL_fnc_inventoryPairs = {
    params ["_cargo"];
    if !(_cargo isEqualType [] && {(count _cargo) >= 2}) exitWith {[]};
    private _classes = _cargo param [0, []];
    private _counts = _cargo param [1, []];
    private _pairs = [];
    {
        _pairs pushBack [_x, _counts param [_forEachIndex, 0]];
    } forEach _classes;
    _pairs sort true;
    _pairs
};

TRIBUNAL_fnc_inventoryRecord = {
    params ["_object"];
    if (isNull _object) exitWith {[]};
    [
        typeOf _object,
        netId _object,
        [getWeaponCargo _object] call TRIBUNAL_fnc_inventoryPairs,
        [getMagazineCargo _object] call TRIBUNAL_fnc_inventoryPairs,
        [getItemCargo _object] call TRIBUNAL_fnc_inventoryPairs,
        [getBackpackCargo _object] call TRIBUNAL_fnc_inventoryPairs,
        local _object,
        owner _object,
        alive _object,
        damage _object
    ]
};

TRIBUNAL_fnc_inventoryTree = {
    params ["_root"];
    if (isNull _root) exitWith {[]};
    private _rows = [[_root] call TRIBUNAL_fnc_inventoryRecord];
    private _children = attachedObjects _root;
    {
        _rows pushBack ([_x] call TRIBUNAL_fnc_inventoryRecord);
    } forEach _children;
    _rows
};

TRIBUNAL_fnc_inventoryContents = {
    params ["_rows"];
    private _contents = [];
    {
        if (_x isEqualType [] && {(count _x) >= 6}) then {
            _contents pushBack [_x # 0, _x # 2, _x # 3, _x # 4, _x # 5];
        };
    } forEach _rows;
    _contents sort true;
    _contents
};

TRIBUNAL_fnc_inventoryPayload = {
    params ["_rows"];
    private _payload = [];
    {
        if (_x isEqualType [] && {(count _x) >= 6}) then {
            private _content = [_x # 0, _x # 2, _x # 3, _x # 4, _x # 5];
            if ((_x # 2) isNotEqualTo [] || {(_x # 3) isNotEqualTo []} || {(_x # 4) isNotEqualTo []} || {(_x # 5) isNotEqualTo []}) then {
                _payload pushBack _content;
            };
        };
    } forEach _rows;
    _payload sort true;
    _payload
};

TRIBUNAL_fnc_deliverySample = {
    params ["_cargo", ["_chute", objNull], "_targetATL"];
    [
        diag_tickTime,
        if (isNull _cargo) then {""} else {netId _cargo},
        if (isNull _cargo) then {[]} else {getPosATL _cargo},
        if (isNull _cargo) then {[]} else {getPosASL _cargo},
        if (isNull _cargo) then {[]} else {velocity _cargo},
        if (isNull _cargo) then {-1} else {_cargo distance2D _targetATL},
        if (isNull _cargo) then {false} else {isTouchingGround _cargo},
        if (isNull _cargo) then {false} else {alive _cargo},
        if (isNull _cargo) then {-1} else {damage _cargo},
        if (isNull _cargo) then {false} else {local _cargo},
        if (isNull _cargo) then {-1} else {owner _cargo},
        if (isNull _chute) then {""} else {netId _chute},
        if (isNull _chute) then {[]} else {getPosATL _chute},
        if (isNull _chute) then {[]} else {velocity _chute},
        if (isNull _chute) then {false} else {local _chute},
        if (isNull _chute) then {-1} else {owner _chute},
        if (isNull _cargo || {isNull attachedTo _cargo}) then {""} else {netId attachedTo _cargo}
    ]
};

TRIBUNAL_fnc_observeDelivery = {
    params ["_cargo", "_targetATL", "_resultVariable", ["_timeout", 120], ["_sampleInterval", 0.1]];
    private _samples = [];
    private _deadline = diag_tickTime + _timeout;
    waitUntil {
        private _chute = _cargo getVariable ["YFU_airdropChute", objNull];
        _samples pushBack ([_cargo, _chute, _targetATL] call TRIBUNAL_fnc_deliverySample);
        uiSleep _sampleInterval;
        !isNil {missionNamespace getVariable _resultVariable}
        || {isNull _cargo}
        || {diag_tickTime > _deadline}
    };
    _samples
};

TRIBUNAL_fnc_deliveryEvidence = {
    params ["_samples", "_targetATL"];
    if (_samples isEqualTo []) exitWith {createHashMap};
    private _minimumAltitude = 1e9;
    private _maximumAltitude = -1;
    private _minimumDistance = 1e9;
    private _chuteIds = [];
    private _chuteLocalities = [];
    private _chuteOwners = [];
    private _attachedSamples = 0;
    {
        private _cargoASL = _x # 3;
        if ((count _cargoASL) >= 3) then {
            // getPosATL on an attached object is attachment-relative on this
            // engine build. Derive physical height from world-space ASL.
            private _height = (_cargoASL # 2) - (getTerrainHeightASL _cargoASL);
            _minimumAltitude = _minimumAltitude min _height;
            _maximumAltitude = _maximumAltitude max _height;
        };
        _minimumDistance = _minimumDistance min (_x # 5);
        private _chuteId = _x # 11;
        if (_chuteId isNotEqualTo "") then {
            _chuteIds pushBackUnique _chuteId;
            _chuteLocalities pushBackUnique (_x # 14);
            _chuteOwners pushBackUnique (_x # 15);
        };
        if ((_x # 16) isNotEqualTo "") then {_attachedSamples = _attachedSamples + 1};
    } forEach _samples;
    private _last = _samples select -1;
    createHashMapFromArray [
        ["samples", count _samples],
        ["minimumAltitudeATL", _minimumAltitude],
        ["maximumAltitudeATL", _maximumAltitude],
        ["minimumDistance", _minimumDistance],
        ["chuteIds", _chuteIds],
        ["chuteLocalities", _chuteLocalities],
        ["chuteOwners", _chuteOwners],
        ["attachedSamples", _attachedSamples],
        ["final", _last],
        ["descended", (_maximumAltitude - _minimumAltitude) > 25 && {_minimumAltitude < 5}],
        ["survived", (_last # 7) && {(_last # 8) < 1}],
        ["deliveryError", _last # 5]
    ]
};
'''

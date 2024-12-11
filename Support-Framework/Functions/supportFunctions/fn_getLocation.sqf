params ["_location", ["_makeLZ", true]];
private _locationName = "";
private _pos = [0,0,0];

// Check if _location is a position (array)
if (typeName _location == "ARRAY") then {
    _pos = _location;
    _locationName = [_pos] call YOSHI_fnc_getNearestLocationText;
};
// Check if _location is a marker (a string that corresponds to a marker name)
if (typeName _location == "STRING" && {getMarkerPos _location distance [0,0,0] > 0}) then {
    _pos = getMarkerPos _location;
    _locationName = markerText _location; // Markers don't have a separate display name, using the marker name itself
};
// Check if _location is an object or unit
if (typeName _location == "OBJECT") then {
    _pos = getPosASL _location;
    _locationName = [_pos] call YOSHI_fnc_getNearestLocationText;
};

if (_makeLZ) then {
    private _landingPadsNearby = [_pos, 10] call YOSHI_fnc_getPadsNearTarget;
    if (count _landingPadsNearby == 0) then {
        // No landing pad nearby, spawn one
        private _landingPad = createVehicle ["Land_HelipadEmpty_F", _pos, [], 0, "CAN_COLLIDE"];
    };
};

// Return the results
[_locationName, _pos]

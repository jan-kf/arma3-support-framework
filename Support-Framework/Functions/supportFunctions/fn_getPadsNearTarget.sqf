params ["_target", ["_distance", 250]];

private _nearbyHelipads = [];
{
    if ((_x distance _target) <= _distance) then {
        _nearbyHelipads pushBack _x;
    };
} forEach HELIPAD_INDEX;

_nearbyHelipads
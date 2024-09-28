params ["_unit", "_location", ["_type", "MOVE"]];

private _group = group _unit;
private _wp = _group addWaypoint [_location, 0];
_wp setWaypointType _type; 
_group setCurrentWaypoint _wp;

_wp
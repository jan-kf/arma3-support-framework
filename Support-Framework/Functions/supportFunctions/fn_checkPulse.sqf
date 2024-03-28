params ["_vic", ["_waypointType", "MOVE"], ["_location", nil]];
// check if the vic has a waypoint, if it does not and it has a destination, then send to destination

private _group = group _vic;

_currentWaypoint = currentWaypoint _group; // Get the index of the current waypoint
_waypointCount = count waypoints _group; // Get the total number of waypoints

// Check if the group has no active waypoint (e.g., not doing anything)
_isInactive = (_currentWaypoint >= _waypointCount) || (waypointType [_group, _currentWaypoint] == "");

if (_isInactive) then {
	private _destination = _vic getVariable ["destination", nil];
	if (!isNil "_location") then {
		private _destination = _location;
	};

	private _locationData = [_destination] call SupportFramework_fnc_getLocation;
	private _locationName = _locationData select 0;
	private _locationPOS = _locationData select 1;

	// set waypoint
	private _wp = _group addWaypoint [_locationPOS, 0];
	_wp setWaypointType _waypointType; 
	_group setCurrentWaypoint _wp;
}


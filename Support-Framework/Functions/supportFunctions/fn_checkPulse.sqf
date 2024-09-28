params ["_vic", ["_waypointType", "MOVE"], ["_location", nil]];
// check if the vic has a waypoint, if it does not and it has a destination, then send to destination

private _group = group _vic;

_currentWaypoint = currentWaypoint _group; // Get the index of the current waypoint
_waypointCount = count waypoints _group; // Get the total number of waypoints

private _currentTask = _vic getVariable ["currentTask", "waiting"];

private _restrictedTasks = ["landingAtObjective","landingAtBase", "requestBaseLZ", "requestReinsert", "requestCas", "requestRecon", "awaitOrders", "waiting"];

private _isPerformingRestrictedTask = _currentTask in _restrictedTasks;

// Check if the group has no active waypoint (e.g., not doing anything)
_isInactive = (_currentWaypoint >= _waypointCount) || (waypointType [_group, _currentWaypoint] == "");

if (_isInactive && !_isPerformingRestrictedTask) then {
	private _destination = _vic getVariable ["destination", nil];
	if (!isNil "_location") then {
		private _destination = _location;
	};

	private _locationData = [_destination, false] call YOSHI_fnc_getLocation;
	private _locationName = _locationData select 0;
	private _locationPOS = _locationData select 1;

	// set waypoint
	[_vic, _locationPOS, _waypointType] call YOSHI_fnc_setWaypoint;
}


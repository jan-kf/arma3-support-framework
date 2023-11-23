#include "findRendezvousPoint.sqf"
#include "posToGrid.sqf"

private _leaveCurrentLocation = {
	params [
		"_vic",  
		"_groupLeader",
		"_goHome", 
		["_first_message", nil]
	];
	private _location = nil;

	if (_goHome) then {
		_location = [_vic, home_base, true] call _findRendezvousPoint;
	} else {
		_location = [_vic, _groupLeader] call _findRendezvousPoint;
	};

	if (isNil "_location") exitWith {
		if (_vic getVariable ["isHeli", false]) then {
			driver _vic sideChat "No nearby LZ found!";
		} else {
			driver _vic sideChat "No nearby RP found!";
		};
		_vic setVariable ["isReinserting", false, true];
	};

	_vic setVariable ["destination", _location, true];
	private _destinationPos = getPos _location; 
	private _currentPos = getPos _vic;


	// set waypoint
	private _grp = group _vic;
	private _base_wp = _grp addWaypoint [_destinationPos, 0];
	_base_wp setWaypointType "TR UNLOAD";
	_grp setCurrentWaypoint _base_wp;

	if (!isNil "_first_message") then {
		// get gridRef if message has format specifier.
		private _gridRef = [_destinationPos] call _posToGrid;
		// msg that driver sends once waypoint is recieved 
		driver _vic sideChat format [_first_message, _gridRef];
	};

	// wait until vic leaves it's current location
	waitUntil {sleep 1; _vic distance2D _currentPos > 100};
};
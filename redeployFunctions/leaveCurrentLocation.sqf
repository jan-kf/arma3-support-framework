#include "findRendezvousPoint.sqf"
#include "posToGrid.sqf"

private _leaveCurrentLocation = {
	params [
		"_vic",  
		"_groupLeader",
		"_goHome", 
		["_first_message", nil],
		["_wavingOff", false]
	];

	if (_vic getVariable "waveOff" && !_wavingOff) exitWith {
		true
	};

	private _location = nil;

	if (_goHome) then {
		_location = [_vic, home_base, true, true] call _findRendezvousPoint;
	} else {
		_location = [_vic, _groupLeader, true] call _findRendezvousPoint;
	};

	if (isNil "_location") exitWith {
		if (_vic getVariable ["isHeli", false]) then {
			driver _vic sideChat "No nearby LZ found!";
		} else {
			driver _vic sideChat "No nearby RP found!";
		};
		_vic setVariable ["isReinserting", false];
	};


	_vic setVariable ["destination", _location];
	private _destinationPos = getPos _location; 
	private _currentPos = getPos _vic;
	

	// logic to check if Vic is already at location
	if (_vic distance2D _destinationPos < 100) exitWith {
		driver _vic sideChat "Already at location, wait one...";
	};

	if (_vic getVariable "waveOff" && !_wavingOff) exitWith {
		true
	};

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

	if (_vic getVariable "waveOff" && !_wavingOff) exitWith {
		true
	};
	// wait until vic leaves it's current location
	waitUntil {sleep 1; (_vic distance2D _currentPos > 100) || (_vic getVariable "waveOff" && !_wavingOff)};

	if (!_goHome) then {
		// vic is not going home
		private _padRegistry = home_base getVariable "padRegistry";
		{
			// systemChat format ["_x, _y: %1, %2", _x, _y];
			if (_y == (netId _vic)) then {
				// release assignment of pad if vic leaves the base
				_padRegistry set [_x, "unassigned"];
			}
		} forEach _padRegistry;
	} else {
		// vicis heading home, it can release it's parkingPass
		private _activeAwayPads = home_base getVariable "activeAwayPads";
		private _parkingPassToReturn = _vic getVariable "awayParkingPass";

		// systemChat format ["activeAwayPads: %1 | parkingPassToReturn: %2", _activeAwayPads, _parkingPassToReturn];

		if (!isNil "_parkingPassToReturn") then {
			private _index = _activeAwayPads find _parkingPassToReturn;
			if (_index != -1) then {
				// Remove the element
				_activeAwayPads deleteAt _index;
			};
		};
	};

	if (_vic getVariable "waveOff" && !_wavingOff) exitWith {
		true
	};
};
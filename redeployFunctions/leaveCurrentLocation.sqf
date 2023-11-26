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

	private _manifest = home_base getVariable "homeBaseManifest";
	private _vicStatus = [_vic] call (missionNamespace getVariable "getVehicleStatus");

	if (_vicStatus get "waveOff" && !_wavingOff) exitWith {
		true
	};

	private _location = nil;

	if (_goHome) then {
		_location = [_vic, home_base, true, true] call _findRendezvousPoint;
	} else {
		_location = [_vic, _groupLeader, true] call _findRendezvousPoint;
	};

	if (isNil "_location") exitWith {
		if (_vicStatus get "isHeli") then {
			[driver _vic, "No nearby LZ found! Staying Put."] remoteExec ["sideChat"];
		} else {
			[driver _vic, "No nearby RP found! Staying Put."] remoteExec ["sideChat"];
		};
		_vicStatus set ["isReinserting", false];
		_vicStatus set ["cancelRedeploy", true];
	};


	_vicStatus set ["destination", _location];
	private _destinationPos = getPos _location; 
	private _currentPos = getPos _vic;
	

	// logic to check if Vic is already at location
	if (_vic distance2D _destinationPos < 100) exitWith {
		[driver _vic, "Already at location, wait one..."] remoteExec ["sideChat"];
	};

	if (_vicStatus get "waveOff" && !_wavingOff) exitWith {
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
		[driver _vic, format [_first_message, _gridRef]] remoteExec ["sideChat"];
	};

	if (_vicStatus get "waveOff" && !_wavingOff) exitWith {
		true
	};
	// wait until vic leaves it's current location
	waitUntil {sleep 1; (_vic distance2D _currentPos > 100) || (_vicStatus get "waveOff" && !_wavingOff)};

	if (!_goHome) then {
		// vic is not going home
		[_vic] call (missionNamespace getVariable "removeVehicleFromPadRegistry");
	} else {
		// vicis heading home, it can release it's parkingPass
		private _activeAwayPads = _manifest get "activeAwayPads";
		private _parkingPassToReturn = _vicStatus get "awayParkingPass";

		// systemChat format ["activeAwayPads: %1 | parkingPassToReturn: %2", _activeAwayPads, _parkingPassToReturn];

		if (!isNil "_parkingPassToReturn") then {
			private _index = _activeAwayPads find _parkingPassToReturn;
			if (_index != -1) then {
				// Remove the element
				_activeAwayPads deleteAt _index;
			};
		};
	};

	if (_vicStatus get "waveOff" && !_wavingOff) exitWith {
		true
	};
};
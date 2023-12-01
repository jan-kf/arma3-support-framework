if (!isServer) exitWith {};

#include "findRendezvousPoint.sqf"
#include "posToGrid.sqf"

private _vic = _this select 0;

private _vicStatus = [_vic] call (missionNamespace getVariable "getVehicleStatus");
private _manifest = missionNamespace getVariable "homeBaseManifest";

private _vehicleClass = typeOf _vic;
private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
	

private _dustOffMessage = nil;
private _touchdownMessage = nil;

if (_vicStatus get "isHeli") then {
	_dustOffMessage = "Heading to LZ at: %1";
	_touchdownMessage = "Touchdown, Please disembark now";
} else {
	_dustOffMessage = "Heading to RP at: %1";
	_touchdownMessage = "We're here, Please disembark now";
};

[driver _vic, format["%1 On Station...", groupId group _vic]] remoteExec ["sideChat"];

while {_vic in (_manifest get "vicRegistry")} do {
	// run while the vic is registered

	/*
	should perform a heartbeat check: 
		- check it's current location

		- check what it's supposed to be doing
			- waiting
			- onMission
				- is it making it's way to the redeploy point?
			- RTB
				- is it making it's way back to base?
		
		- is it where it's meant to be?
			- if not it should remedy it 
	*/

	private _task = _vicStatus getOrDefault ["currentTask", "waiting"];

	// [format["%1 watchdog loop: %2 | %3", _vehicleDisplayName, _task, time]] remoteExec ["systemChat"];

	// [driver _vic, format["%1 -> current task: %2", _vehicleDisplayName, _task]] remoteExec ["sideChat"];
	diag_log format["[REDEPLOY] %1 watchdog loop: %2 | %3", _vehicleDisplayName, _task, time];


	switch (_task) do
	{
		case "resistered": {
			/*
			vic was just registered, should probably check that it's at base
			if it's not at base, should probably have it go back to base to sort itself out
			once ready, set task to waiting
			*/ 

			_vicStatus set ["currentTask", "waiting"];
		};
		case "begin": {
			// vic was told to begin it's mission, perform startup
			// clear out params:
			_vicStatus set ["waveOff", false];
			_vicStatus set ["cancelRedeploy", false];
			_vicStatus set ["requestingRedeploy", false];
			_vicStatus set ["performedReinsert", false];
			_vicStatus set ["destination", nil];

			_vicStatus set ["isReinserting", true];

			private _groupLeader = _vicStatus get "targetGroupLeader";

			if (isNil "_groupLeader") exitWith {
				[driver _vic, "No group leader was assigned, Staying Put."] remoteExec ["sideChat"];
				_vicStatus set ["currentTask", "waiting"];
				_vicStatus set ["isReinserting", false];
			};

			private _groupLeaderGroup = group _groupLeader;
			private _groupLeaderCallsign = groupId _groupLeaderGroup;

			private _location = [_vic, _groupLeader, true] call _findRendezvousPoint;
			
			[_groupLeader, format ["Base, this is %1, requesting redeployment from %2, over", _groupLeaderCallsign, groupId group _vic]] remoteExec ["sideChat"];
			sleep 3;
			

			if (isNil "_location") exitWith {
				if (_vicStatus get "isHeli") then {
					[[west, "base"], format ["%1, we have no available LZ for %2 near your location, out.", _groupLeaderCallsign, groupId group _vic]] remoteExec ["sideChat"];
				} else {
					[[west, "base"], format ["%1, we have no available RP for %2 near your location, out.", _groupLeaderCallsign, groupId group _vic]] remoteExec ["sideChat"];
				};
				sleep 3;
				_vicStatus set ["currentTask", "waiting"];
				_vicStatus set ["isReinserting", false];
			};

			[[west, "base"], format ["Roger %1, beginning redeployment, out.", _groupLeaderCallsign]] remoteExec ["sideChat"];
			sleep 3;

			_vicStatus set ["destination", _location];
			private _destinationPos = getPos _location; 
			private _currentPos = getPos _vic;

			// logic to check if Vic is already at location
			if (_vic distance2D _destinationPos < 100) exitWith {
				[driver _vic, "Already at location, wait one..."] remoteExec ["sideChat"];
				_vicStatus set ["requestBaseLZ", nil];
			};

			// set waypoint
			private _grp = group _vic;
			private _base_wp = _grp addWaypoint [_destinationPos, 0];
			_base_wp setWaypointType "MOVE";
			_grp setCurrentWaypoint _base_wp;

			private _gridRef = [_destinationPos] call _posToGrid;
			if ((isTouchingGround _vic) && (speed _vic < 1)) then {
				// get gridRef if message has format specifier.
				// msg that driver sends once destination grid is recieved 
				[[west, "base"], format ["Over to you %1, you are cleared for departure to %2, over.", groupId group _vic, _gridRef]] remoteExec ["sideChat"];
				sleep 3;
				[driver _vic, format ["Cleared for departure to %1, %2 out.", _gridRef, groupId group _vic]] remoteExec ["sideChat"];
			}else{
				[[west, "base"], format ["Over to you %1, you are cleared for approach to %2, over.", groupId group _vic, _gridRef]] remoteExec ["sideChat"];
				sleep 3;
				[driver _vic, format ["Cleared for approach to %1, %2 out.", _gridRef, groupId group _vic]] remoteExec ["sideChat"];
			};

			// vic is leaving base, release base pad reservation
			[_vic] call (missionNamespace getVariable "removeVehicleFromPadRegistry");

			// once vic is underway, set it's task to onMission
			_vicStatus set ["currentTask", "onMission"];
		};
		case "onMission": {
			// vic is currently making its way to the redeploy LZ

			// check if there are any issues

			// check the vic is near the objective, and ready to land 
			if (_vic distance2D getPos (_vicStatus get "destination") < 100 && unitReady _vic) then {
				// set task to land at objective
				_vic land "LAND";
				_vicStatus set ["currentTask", "landingAtObjective"];
			};

		};
		case "RTB": {
			// vic is currently making it's way back to home_base

			// check if there are any issues
			
			// check the vic is near the base, and ready to land 
			if (_vic distance2D getPos (_vicStatus get "destination") < 100 && unitReady _vic) then {
				// set task to land at base
				_vic land "LAND";
				_vicStatus set ["currentTask", "landingAtBase"];
			};

		};
		case "landingAtObjective": {
			// vic is performing it's landing procedures at the location

			if ((isTouchingGround _vic) && (speed _vic < 1)) then {
				_vic engineOn false;
				_vicStatus set ["performedReinsert", true];
				[driver _vic, _touchdownMessage] remoteExec ["sideChat"];

				// wait after touchdown
				sleep 10;
				_vicStatus set ["isReinserting", false];
				_vicStatus set ["currentTask", "requestBaseLZ"];
			};
		};
		case "requestBaseLZ": {
			// vic attempts to kickstart it's RTB procedures

			private _parkingPassToReturn = _vicStatus get "awayParkingPass";
			if (!isNil "_parkingPassToReturn") then {
				private _awayPads = _manifest get "activeAwayPads";
				private _index = _awayPads find _parkingPassToReturn;
				if (_index != -1) then {
					// Remove the element
					_awayPads deleteAt _index;
				};
			};
			[driver _vic, format ["Base, this is %1, requesting permission to land, over", groupId group _vic]] remoteExec ["sideChat"];
			sleep 3;
			_location = [_vic, home_base, true, true] call _findRendezvousPoint;
			if (isNil "_location") exitWith {
				if (_vicStatus get "isHeli") then {
					[[west, "base"], format ["%1, No helipad is available at the moment, over.", groupId group _vic]] remoteExec ["sideChat"];
				} else {
					[[west, "base"], format ["%1, No parking is available at the moment, over.", groupId group _vic]] remoteExec ["sideChat"];
				};
				sleep 3;
				[driver _vic, format ["Roger that Base, will check in again later. %1 out.", groupId group _vic]] remoteExec ["sideChat"];
				[_vic] call (missionNamespace getVariable "removeVehicleFromPadRegistry");
				// what should it's status be?
				_vicStatus set ["currentTask", "marooned"];
			};
			_vicStatus set ["destination", _location];
			_destinationPos = getPos _location; 
			_currentPos = getPos _vic;

			// logic to check if Vic is already at location
			if ((_vic distance2D _destinationPos < 100) && (isTouchingGround _vic) && (speed _vic < 1)) exitWith {
				[driver _vic, "Already at base..."] remoteExec ["sideChat"];
				_vicStatus set ["currentTask", "waiting"];
			};

			// set waypoint
			private _grp = group _vic;
			private _base_wp = _grp addWaypoint [_destinationPos, 0];
			_base_wp setWaypointType "MOVE";
			_grp setCurrentWaypoint _base_wp;

			if (!isNil "_dustOffMessage") then {
				// get gridRef if message has format specifier.
				private _gridRef = [_destinationPos] call _posToGrid;
				// msg that driver sends once destination grid is recieved 
				[[west, "base"], format ["%1, you are cleared to land at landing pad at %2, over.", groupId group _vic, _gridRef]] remoteExec ["sideChat"];
				sleep 3;
				[driver _vic, format ["Cleared for pad at %1, %2 out.", _gridRef, groupId group _vic]] remoteExec ["sideChat"];
			};

			// once complete, set task to RTB
			_vicStatus set ["currentTask", "RTB"];
			
		};
		case "waveOff": {
			// cancel reinsertion, reset request for redeploy
			_vicStatus set ["isReinserting", false];
			_vicStatus set ["requestingRedeploy", false];

			private _groupLeader = _vicStatus get "targetGroupLeader";
			private _groupLeaderGroup = group _groupLeader;
			private _groupLeaderCallsign = groupId _groupLeaderGroup;

			[_groupLeader, format ["%1, this is %2, Wave off, over.",groupId group _vic, _groupLeaderCallsign]] remoteExec ["sideChat"];
			sleep 3;
			[driver _vic, format ["Roger that %1, Waving off, out.", _groupLeaderCallsign]] remoteExec ["sideChat"];
			sleep 3;

			_vic land "NONE"; // cancel landing 

			private _group = group _vic;
			// delete waypoints 
			for "_i" from (count waypoints _group - 1) to 0 step -1 do
			{
				deleteWaypoint [_group, _i];
			};
			_vicStatus set ["currentTask", "requestBaseLZ"];
		};
		case "landingAtBase": {
			// vic is performing it's landing procedures at the base

			if ((isTouchingGround _vic) && (speed _vic < 1)) then {
				// always release parking request 
				[_vic] call (missionNamespace getVariable "removeVehicleFromPadRegistry");
				
				_vic engineOn false;
				_vicStatus set ["performedReinsert", false];
				_vicStatus set ["isReinserting", false];

				[driver _vic, format ["%1 is ready for tasking...", groupId group _vic]] remoteExec ["sideChat"];

				// once landed, go back to waiting
				_vicStatus set ["currentTask", "waiting"];
			};
		};
		case "marooned": {
			// vic was denyed a landing pad at home base
			sleep 10;
			
			_vicStatus set ["requestBaseLZ", nil];
		};
		default {
			//vic is waiting for a task, wait
			_vicStatus set ["targetGroupLeader", nil];
		};

	};


	sleep 3;
};

[driver _vic, format["%1 Off Station...", groupId group _vic]] remoteExec ["sideChat"];

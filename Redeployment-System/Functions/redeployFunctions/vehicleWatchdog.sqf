if (!isServer) exitWith {};

#include "findRendezvousPoint.sqf"
#include "posToGrid.sqf"

private _vic = _this select 0;

private _baseCallsign = [west, "base"];
private _baseName = "Base";

private _syncedObjects = synchronizedObjects (missionNamespace getVariable "home_base");
{
	if (_x isKindOf "Man") exitWith {
		_baseCallsign = _x;
		_baseName = groupId group _x;
	};
} forEach _syncedObjects;

// [format ["Starting watchdog for %1 ... ", _vic]] remoteExec ["systemChat"];
diag_log format ["Starting watchdog for %1 ... ", _vic];

private _watchdog = _vic getVariable "watchdog";
if (!isNil "_watchdog") exitWith {
	// [format ["watchdog exists for %1, skipping | %2", _vic, _watchdog]] remoteExec ["systemChat"];
	diag_log format ["watchdog exists for %1, skipping", _vic];
};

private _vehicleClass = typeOf _vic;
private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
	

private _dustOffMessage = nil;
private _touchdownMessage = nil;

if (_vic getVariable ["isHeli", false]) then {
	_dustOffMessage = "Heading to LZ at: %1";
	_touchdownMessage = "Touchdown, Please disembark now";
} else {
	_dustOffMessage = "Heading to RP at: %1";
	_touchdownMessage = "We're here, Please disembark now";
};

[driver _vic, format["%1 On Station...", groupId group _vic]] remoteExec ["sideChat"];

while {_vic getVariable ["isRegistered", false]} do {
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

	private _task = _vic getVariable ["currentTask", "waiting"];

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

			_vic setVariable ["currentTask", "waiting", true];
		};
		case "begin": {
			// vic was told to begin it's mission, perform startup
			// clear out params:
			_vic setVariable ["waveOff", false, true];
			_vic setVariable ["destination", nil, true];

			_vic setVariable ["isReinserting", true, true];

			private _groupLeader = _vic getVariable "targetGroupLeader";
			private _fullRun = _vic getVariable ["fullRun", true];

			if (isNil "_groupLeader") exitWith {
				[driver _vic, "No group leader was assigned, Staying Put."] remoteExec ["sideChat"];
				_vic setVariable ["currentTask", "waiting", true];
				_vic setVariable ["isReinserting", false, true];
			};

			private _groupLeaderGroup = group _groupLeader;
			private _groupLeaderCallsign = groupId _groupLeaderGroup;

			private _location = _vic getVariable "targetLocation";
			if (isNil "_location") then {
				private _location = [_vic, _groupLeader, true] call _findRendezvousPoint;
				private _gl_message = "%3, this is %1, requesting redeployment from %2, over";
				if (!_fullRun) then{
					_gl_message = "%3, this is %1, requesting %2 on my position, over";
				};
				[_groupLeader, format [_gl_message, _groupLeaderCallsign, groupId group _vic, _baseName]] remoteExec ["sideChat"];
			}else{
				private _gl_message = "%4, this is %1, requesting %2 at %3, over";
				[_groupLeader, format [_gl_message, _groupLeaderCallsign, groupId group _vic, markerText _location, _baseName]] remoteExec ["sideChat"];
			};

			
			sleep 3;
			

			if (isNil "_location") exitWith {
				if (_vic getVariable ["isHeli", false]) then {
					[_baseCallsign, format ["%1, we have no available LZ for %2 near your location, out.", _groupLeaderCallsign, groupId group _vic]] remoteExec ["sideChat"];
				} else {
					[_baseCallsign, format ["%1, we have no available RP for %2 near your location, out.", _groupLeaderCallsign, groupId group _vic]] remoteExec ["sideChat"];
				};
				sleep 3;
				_vic setVariable ["currentTask", "waiting", true];
				_vic setVariable ["isReinserting", false, true];
			};

			private _base_message = "Roger %1, beginning redeployment, out.";
			if (!_fullRun) then{
				_base_message = "Roger %1, dispatching %2, out.";
			};


			[_baseCallsign, format [_base_message, _groupLeaderCallsign, groupId group _vic]] remoteExec ["sideChat"];
			sleep 3;

			private _destinationPos = nil;
			if (typeName _location == "STRING") then {
				// _location is a string
				_destinationPos = getMarkerPos _location;
			} else {
				if (typeName _location == "OBJECT") then {
					// _location is an object
					_destinationPos = getPos _location;
				};
			};

			_vic setVariable ["destination", _location, true];
			 
			private _currentPos = getPos _vic;

			// logic to check if Vic is already at location
			if (_vic distance2D _destinationPos < 100) exitWith {
				[_vic] call (missionNamespace getVariable "removeVehicleFromPadRegistry");
				[driver _vic, "Already at location, wait one..."] remoteExec ["sideChat"];
				if (_fullRun) then {
					_vic setVariable ["currentTask", "requestBaseLZ", true];
				} else {
					_vic setVariable ["currentTask", "waiting", true];
				};
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
				[_baseCallsign, format ["Over to you %1, you are cleared for departure to %2, over.", groupId group _vic, _gridRef]] remoteExec ["sideChat"];
				sleep 3;
				[driver _vic, format ["Cleared for departure to %1, %2 out.", _gridRef, groupId group _vic]] remoteExec ["sideChat"];
			}else{
				[_baseCallsign, format ["Over to you %1, you are cleared for approach to %2, over.", groupId group _vic, _gridRef]] remoteExec ["sideChat"];
				sleep 3;
				[driver _vic, format ["Cleared for approach to %1, %2 out.", _gridRef, groupId group _vic]] remoteExec ["sideChat"];
			};

			// vic is leaving base, release base pad reservation
			[_vic] call (missionNamespace getVariable "removeVehicleFromPadRegistry");
			// cancel request
			_vic setVariable ["requestingRedeploy", false, true];
			// once vic is underway, set it's task to onMission
			_vic setVariable ["currentTask", "onMission", true];
		};
		case "onMission": {
			// vic is currently making its way to the redeploy LZ
			// check if there are any issues

			private _destination = _vic getVariable "destination";
			private _destinationPos = nil;
			if (typeName _destination == "STRING") then {
				// _destination is a string
				_destinationPos = getMarkerPos _destination;
			} else {
				if (typeName _destination == "OBJECT") then {
					// _destination is an object
					_destinationPos = getPos _destination;
				};
			};

			// check the vic is near the objective, and ready to land 
			if (_vic distance2D _destinationPos < 100 && unitReady _vic) then {
				// set task to land at objective
				_vic land "LAND";
				_vic setVariable ["currentTask", "landingAtObjective", true];
			};

		};
		case "RTB": {
			// vic is currently making it's way back to (missionNamespace getVariable "home_base")

			// check if there are any issues

			private _destination = _vic getVariable "destination";
			private _destinationPos = nil;
			if (typeName _destination == "STRING") then {
				// _destination is a string
				_destinationPos = getMarkerPos _destination;
			} else {
				if (typeName _destination == "OBJECT") then {
					// _destination is an object
					_destinationPos = getPos _destination;
				};
			};
			
			// check the vic is near the base, and ready to land 
			if (_vic distance2D _destinationPos < 100 && unitReady _vic) then {
				// set task to land at base
				_vic land "LAND";
				_vic setVariable ["currentTask", "landingAtBase", true];
			};

		};
		case "landingAtObjective": {
			// vic is performing it's landing procedures at the location

			if ((isTouchingGround _vic) && (speed _vic < 1)) then {
				_vic engineOn false;
				[driver _vic, _touchdownMessage] remoteExec ["sideChat"];

				// wait after touchdown
				sleep 10;
				_vic setVariable ["isReinserting", false, true];
				private _fullRun = _vic getVariable ["fullRun", true];
				if (_fullRun) then {
					_vic setVariable ["currentTask", "requestBaseLZ", true];
				} else {
					[driver _vic, format ["%1 on standby, awaiting orders.", groupId group _vic]] remoteExec ["sideChat"];
					_vic setVariable ["currentTask", "awaitOrders", true];
				};
			};
		};
		case "requestBaseLZ": {
			// vic attempts to kickstart it's RTB procedures
			[_vic] call (missionNamespace getVariable "removeVehicleFromAwayPads");
			
			[driver _vic, format ["%2, this is %1, requesting permission to land, over", groupId group _vic, _baseName]] remoteExec ["sideChat"];
			sleep 3;
			_location = [_vic, (missionNamespace getVariable "home_base"), true, true] call _findRendezvousPoint;
			if (isNil "_location") exitWith {
				if (_vic getVariable ["isHeli", false]) then {
					[_baseCallsign, format ["%1, No helipad is available at the moment, over.", groupId group _vic]] remoteExec ["sideChat"];
				} else {
					[_baseCallsign, format ["%1, No parking is available at the moment, over.", groupId group _vic]] remoteExec ["sideChat"];
				};
				sleep 3;
				[driver _vic, format ["Roger that %2, will check in again later. %1 out.", groupId group _vic, _baseName]] remoteExec ["sideChat"];
				[_vic] call (missionNamespace getVariable "removeVehicleFromPadRegistry");
				// what should it's status be?
				_vic setVariable ["currentTask", "marooned", true];
			};
			_vic setVariable ["destination", _location, true];
			_destinationPos = getPos _location; 
			_currentPos = getPos _vic;

			// logic to check if Vic is already at location
			if ((_vic distance2D _destinationPos < 100) && (isTouchingGround _vic) && (speed _vic < 1)) exitWith {
				[driver _vic, "Already at base..."] remoteExec ["sideChat"];
				_vic setVariable ["currentTask", "waiting", true];
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
				[_baseCallsign, format ["%1, you are cleared to land at landing pad at %2, over.", groupId group _vic, _gridRef]] remoteExec ["sideChat"];
				sleep 3;
				[driver _vic, format ["Cleared for pad at %1, %2 out.", _gridRef, groupId group _vic]] remoteExec ["sideChat"];
			};

			// once complete, set task to RTB
			_vic setVariable ["currentTask", "RTB", true];
			
		};
		case "waveOff": {
			// cancel reinsertion, reset request for redeploy

			private _groupLeader = _vic getVariable "targetGroupLeader";

			_vic setVariable ["isReinserting", false, true];

			private _groupLeader = _vic getVariable "targetGroupLeader";
			private _groupLeaderGroup = group _groupLeader;
			private _groupLeaderCallsign = groupId _groupLeaderGroup;

			_vic land "NONE"; // cancel landing 

			private _group = group _vic;
			// delete waypoints 
			for "_i" from (count waypoints _group - 1) to 0 step -1 do
			{
				deleteWaypoint [_group, _i];
			};
			_vic setVariable ["currentTask", "requestBaseLZ", true];
			
			[_groupLeader, format ["%1, this is %2, Wave off, over.",groupId group _vic, _groupLeaderCallsign]] remoteExec ["sideChat"];
			sleep 2;
			[driver _vic, format ["Roger that %1, Waving off, out.", _groupLeaderCallsign]] remoteExec ["sideChat"];
			sleep 1;
		};
		case "landingAtBase": {
			// vic is performing it's landing procedures at the base

			if ((isTouchingGround _vic) && (speed _vic < 1)) then {
				// always release parking request 
				[_vic] call (missionNamespace getVariable "removeVehicleFromPadRegistry");
				
				_vic engineOn false;
				_vic setVariable ["isReinserting", false, true];

				[driver _vic, format ["%1 is ready for tasking...", groupId group _vic]] remoteExec ["sideChat"];

				// once landed, go back to waiting
				_vic setVariable ["currentTask", "waiting", true];
			};
		};
		case "awaitOrders": {
			// vic was called in to land, awaiting explicit orders to RTB
			// no code, leader will set the current task manually
		};
		case "marooned": {
			// vic was denied a landing pad at home base
			sleep 10;
			
			_vic setVariable ["currentTask", "requestBaseLZ", true];
		};
		default {
			//vic is waiting for a task, wait
			_vic setVariable ["isReinserting", false, true];
			_vic setVariable ["targetGroupLeader", nil, true];
			_vic setVariable ["fullRun", true, true];
		};

	};

	
	sleep 3;
};

[driver _vic, format["%1 Off Station...", groupId group _vic]] remoteExec ["sideChat"];

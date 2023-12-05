if (!isServer) exitWith {};

#include "findRendezvousPoint.sqf"
#include "posToGrid.sqf"

private _vic = _this select 0;

[format ["Starting watchdog for %1 ... ", _vic]] remoteExec ["systemChat"];

private _watchdog = _vic getVariable "watchdog";
if (!isNil "_watchdog") exitWith {
	[format ["watchdog exists for %1, skipping | %2", _vic, _watchdog]] remoteExec ["systemChat"];
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

			if (isNil "_groupLeader") exitWith {
				[driver _vic, "No group leader was assigned, Staying Put."] remoteExec ["sideChat"];
				_vic setVariable ["currentTask", "waiting", true];
				_vic setVariable ["isReinserting", false, true];
			};

			private _groupLeaderGroup = group _groupLeader;
			private _groupLeaderCallsign = groupId _groupLeaderGroup;

			private _location = [_vic, _groupLeader, true] call _findRendezvousPoint;
			
			[_groupLeader, format ["Base, this is %1, requesting redeployment from %2, over", _groupLeaderCallsign, groupId group _vic]] remoteExec ["sideChat"];
			sleep 3;
			

			if (isNil "_location") exitWith {
				if (_vic getVariable ["isHeli", false]) then {
					[[west, "base"], format ["%1, we have no available LZ for %2 near your location, out.", _groupLeaderCallsign, groupId group _vic]] remoteExec ["sideChat"];
				} else {
					[[west, "base"], format ["%1, we have no available RP for %2 near your location, out.", _groupLeaderCallsign, groupId group _vic]] remoteExec ["sideChat"];
				};
				sleep 3;
				_vic setVariable ["currentTask", "waiting", true];
				_vic setVariable ["isReinserting", false, true];
			};

			private _actionID = _groupLeader getVariable (netId _vic);
			if (!isNil "_actionID") then {
				private _vehicleClass = typeOf _vic;
				private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
				[[MissionNamespace, "UpdateActionText", [_groupLeader, _actionID, format["Wave Off %1", _vehicleDisplayName], "#FF0000"]], BIS_fnc_callScriptedEventHandler] remoteExec ["call", 0];
			};

			[[west, "base"], format ["Roger %1, beginning redeployment, out.", _groupLeaderCallsign]] remoteExec ["sideChat"];
			sleep 3;

			_vic setVariable ["destination", _location, true];
			private _destinationPos = getPos _location; 
			private _currentPos = getPos _vic;

			// logic to check if Vic is already at location
			if (_vic distance2D _destinationPos < 100) exitWith {
				[_vic] call (missionNamespace getVariable "removeVehicleFromPadRegistry");
				[driver _vic, "Already at location, wait one..."] remoteExec ["sideChat"];
				_vic setVariable ["currentTask", "requestBaseLZ", true];
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
			_vic setVariable ["currentTask", "onMission", true];
		};
		case "onMission": {
			// vic is currently making its way to the redeploy LZ

			// check if there are any issues

			// check the vic is near the objective, and ready to land 
			if (_vic distance2D getPos (_vic getVariable "destination") < 100 && unitReady _vic) then {
				// set task to land at objective
				_vic land "LAND";
				_vic setVariable ["currentTask", "landingAtObjective", true];
			};

		};
		case "RTB": {
			// vic is currently making it's way back to home_base

			// check if there are any issues
			
			// check the vic is near the base, and ready to land 
			if (_vic distance2D getPos (_vic getVariable "destination") < 100 && unitReady _vic) then {
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
				_vic setVariable ["currentTask", "requestBaseLZ", true];
			};
		};
		case "requestBaseLZ": {
			// vic attempts to kickstart it's RTB procedures
			[_vic] call (missionNamespace getVariable "removeVehicleFromAwayPads");
			
			[driver _vic, format ["Base, this is %1, requesting permission to land, over", groupId group _vic]] remoteExec ["sideChat"];
			sleep 3;
			_location = [_vic, home_base, true, true] call _findRendezvousPoint;
			if (isNil "_location") exitWith {
				if (_vic getVariable ["isHeli", false]) then {
					[[west, "base"], format ["%1, No helipad is available at the moment, over.", groupId group _vic]] remoteExec ["sideChat"];
				} else {
					[[west, "base"], format ["%1, No parking is available at the moment, over.", groupId group _vic]] remoteExec ["sideChat"];
				};
				sleep 3;
				[driver _vic, format ["Roger that Base, will check in again later. %1 out.", groupId group _vic]] remoteExec ["sideChat"];
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
				[[west, "base"], format ["%1, you are cleared to land at landing pad at %2, over.", groupId group _vic, _gridRef]] remoteExec ["sideChat"];
				sleep 3;
				[driver _vic, format ["Cleared for pad at %1, %2 out.", _gridRef, groupId group _vic]] remoteExec ["sideChat"];
			};

			// once complete, set task to RTB
			_vic setVariable ["currentTask", "RTB", true];
			
		};
		case "waveOff": {
			// cancel reinsertion, reset request for redeploy

			private _groupLeader = _vic getVariable "targetGroupLeader";

			if (!isNil "_groupLeader") then {
				private _actionID = _groupLeader getVariable (netId _vic);
				if (!isNil "_actionID") then {
					private _vehicleClass = typeOf _vic;
					private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
					[[MissionNamespace, "UpdateActionText", [_groupLeader, _actionID, format["(waving off) Deploy %1", _vehicleDisplayName], "#FFFFFF"]], BIS_fnc_callScriptedEventHandler] remoteExec ["call", 0];
				};
			};

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

				private _groupLeader = _vic getVariable "targetGroupLeader";
				if (!isNil "_groupLeader") then {
					private _actionID = _groupLeader getVariable (netId _vic);
					if (!isNil "_actionID") then {
						private _vehicleClass = typeOf _vic;
						private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
						[[MissionNamespace, "UpdateActionText", [_groupLeader, _actionID, format["Deploy %1", _vehicleDisplayName], "#FFFFFF"]], BIS_fnc_callScriptedEventHandler] remoteExec ["call", 0];
					};
				};

				// once landed, go back to waiting
				_vic setVariable ["currentTask", "waiting", true];
			};
		};
		case "marooned": {
			// vic was denyed a landing pad at home base
			sleep 10;
			
			_vic setVariable ["currentTask", "requestBaseLZ", true];
		};
		default {
			//vic is waiting for a task, wait
			_vic setVariable ["isReinserting", false, true];
			_vic setVariable ["targetGroupLeader", nil, true];
		};

	};

	
	sleep 3;
};

[driver _vic, format["%1 Off Station...", groupId group _vic]] remoteExec ["sideChat"];
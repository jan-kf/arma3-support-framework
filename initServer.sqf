/*
	if you want to create a home base (only 1 is allowed at a time) 
	you first place down an object (or logic entity), and set it's variable name to: 
	
	home_base
	
	then provide it this code:
	
	"initHomeBase.sqf" remoteExec ["execVM", 2];
	
	---
	
	if you want some vehicles to start off being registered, 
	you need to use a logic entity (Systems > Logic entities) instead of a physical object. 
	I like the "Base" under Locations -- do the same setup as above.
	
	then you can sync the vehicles to this logic entity (home_base)
	
*/

if (!isServer) exitWith {};

diag_log "[REDEPLOY] initHomeBase is beginning initilization...";

// setup home_base variables 
private _padRegistry = createHashMap;

private _homeBaseManifest = createHashMapFromArray [
	["activeAwayPads", []]
];
home_base setVariable ["homeBaseManifest", _homeBaseManifest, true];

missionNamespace setVariable ["vicWatchdog", compile preprocessFileLineNumbers "redeployFunctions\vehicleWatchdog.sqf"];
missionNamespace setVariable ["getBasePads", compile preprocessFileLineNumbers "redeployFunctions\getPadsNearBase.sqf"];
missionNamespace setVariable ["getTargetPads", compile preprocessFileLineNumbers "redeployFunctions\getPadsNearTarget.sqf"];
missionNamespace setVariable ["getRegisteredVehicles", compile preprocessFileLineNumbers "redeployFunctions\getRegisteredVehicles.sqf"];

missionNamespace setVariable ["addVicToPlayers", {
	params ["_vehicle"];

	{
		private _player = _x;
		[[_player, _vehicle], "redeployFunctions\addVicActionToPlayer.sqf"] remoteExec ["execVM", 0];
	} forEach allPlayers;
}];

missionNamespace setVariable ["removeVicFromPlayers", {
	params ["_vehicle"];

	private _vicNetId = netId _vehicle;

	{
		private _actionID = _x getVariable _vicNetId;
		if (!isNil "_actionID") then {
			[_x, _actionID] remoteExec ["removeAction", 0, true];
			_x setVariable [_vicNetId, nil, true];
		};
	} forEach allPlayers;
}];

missionNamespace setVariable ["removeVehicleFromPadRegistry", {
	params ["_vehicle"];
	private _basePads = call (missionNamespace getVariable "getBasePads");
	// Vehicle netId to check against
    private _vehicleNetId = netId _vehicle;

    // Iterate over each pad in _basePads
    {
        // Get the stored vehicle netId for this pad
        private _storedVehicleNetId = _x getVariable ["assignment", ""];

        // Check if this pad has the vehicle registered
        if (_storedVehicleNetId isEqualTo _vehicleNetId) then {
            // If so, set the variable to nil to unregister the vehicle
            _x setVariable ["assignment", nil];
        };
    } forEach _basePads;
}];

missionNamespace setVariable ["removeVehicleFromAwayPads", {
	params ["_vehicle"];
	private _groupLeader = _vehicle getVariable "targetGroupLeader";

	if (isNil "_groupLeader") exitWith {};

	private _vehicleNetId = netId _vehicle;
	private _awayPads = [_groupLeader] call (missionNamespace getVariable "getTargetPads");
	{
		private _storedVehicleNetId = _x getVariable ["assignment", ""];
		// Check if this pad has the vehicle registered
		if (_storedVehicleNetId isEqualTo _vehicleNetId) then {
			// If so, set the variable to nil to unregister the vehicle
			_x setVariable ["assignment", nil];
		};
	} forEach _awayPads;
}];

publicVariable "homeBaseManifest";
publicVariable "vicWatchdog";
publicVariable "getBasePads";
publicVariable "getTargetPads";
publicVariable "getRegisteredVehicles";
publicVariable "addVicToPlayers";
publicVariable "removeVicFromPlayers";
publicVariable "removeVehicleFromPadRegistry";
publicVariable "removeVehicleFromAwayPads";

// register all objects that are synced to home_base

private _syncedObjects = synchronizedObjects home_base;
{
	if (_x isKindOf "Helicopter") then {

		[[MissionNamespace, "CallToRegisterVehicle", [_x]], BIS_fnc_callScriptedEventHandler] remoteExec ["call", 2];

		_x setVariable ["isHeli", true, true];
	};
} forEach _syncedObjects;

//// //// ////////////////////////////////////////////////////////////////////////////////

[missionNamespace, "VehicleRegistered", {
	// Logic for if a vehicle is called to be registered, and it currently is not 
	params ["_vehicle"];

	// register the vic
	_vehicle setVariable ["isRegistered", true, true];

	[_vehicle] call (missionNamespace getVariable "addVicToPlayers");

}] call BIS_fnc_addScriptedEventHandler;

[missionNamespace, "VehicleUnregistered", {
	
	params ["_vehicle"];

	// register the vic
	_vehicle setVariable ["isRegistered", false, true];


	[_vehicle] call (missionNamespace getVariable "removeVicFromPlayers");

}] call BIS_fnc_addScriptedEventHandler;

[missionNamespace, "UpdateActionText", {
	// Logic to update any text of an action
	// GLOBALLY executed 
	params ["_object", "_actionID", "_text", ["_color", "#FFFFFF"]];

	[_object, [_actionID, format ["<t color='%2'>%1</t>", _text, _color]]] remoteExec ["setUserActionText", 0];
}] call BIS_fnc_addScriptedEventHandler;


// Function to register a vehicle
[missionNamespace, "CallToRegisterVehicle", {
	params ["_vehicle"];

	private _isRegistered = _vehicle getVariable ["isRegistered", false];

	if (!_isRegistered) then {
		// register the vic
		[[MissionNamespace, "VehicleRegistered", [_vehicle]], BIS_fnc_callScriptedEventHandler] remoteExec ["call", 2];

		private _actionID = _vehicle getVariable "regActionID";
		if (!isNil "_actionID") then {
			private _vehicleClass = typeOf _vehicle;
			private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
			[[MissionNamespace, "UpdateActionText", [_vehicle, _actionID, format["Unregister %1", _vehicleDisplayName], "#FF8000"]], BIS_fnc_callScriptedEventHandler] remoteExec ["call", 0];
		};
	};
}] call BIS_fnc_addScriptedEventHandler;


// Function to unregister a vehicle
[missionNamespace, "CallToUnregisterVehicle", {
	params ["_vehicle"];

	private _isRegistered = _vehicle getVariable ["isRegistered", false];

	if (_isRegistered) then {
		// unregister the vic
		[[MissionNamespace, "VehicleUnregistered", [_vehicle]], BIS_fnc_callScriptedEventHandler] remoteExec ["call", 2];

		private _actionID = _vehicle getVariable "regActionID";
		if (!isNil "_actionID") then {
			private _vehicleClass = typeOf _vehicle;
			private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
			[[MissionNamespace, "UpdateActionText", [_vehicle, _actionID, format["Register %1", _vehicleDisplayName], "#00ABFF"]], BIS_fnc_callScriptedEventHandler] remoteExec ["call", 0];
		};
	};
}] call BIS_fnc_addScriptedEventHandler;



// once everything is set up, kick off the heartbeat for players (JIP true)
diag_log "[REDEPLOY] kicking off heartbeat...";
["[REDEPLOY] kicking off heartbeat..."] remoteExec ["systemChat"];

[] spawn (compile preprocessFileLineNumbers "redeployFunctions\baseHeartbeat.sqf");

diag_log "[REDEPLOY] initHomeBase is done initializing";
["[REDEPLOY] initHomeBase is done initializing"] remoteExec ["systemChat"];
/*
	if you want to create a home base (only 1 is allowed at a time) 
	you first place down an object (or logic entity), and set it's variable name to: 
	
	home_base
	
	---
	
	if you want some vehicles to start off being registered, 
	you need to use a logic entity (Systems > Logic entities) instead of a physical object. 
	I like the "Base" under Locations -- do the same setup as above.
	
	then you can sync the vehicles to this logic entity (home_base)
	
*/

if (!isServer) exitWith {};

diag_log "[REDEPLOY] initHomeBase is beginning initilization...";

missionNamespace setVariable ["vicWatchdog", compile preprocessFileLineNumbers "redeployFunctions\vehicleWatchdog.sqf"];
missionNamespace setVariable ["getBasePads", compile preprocessFileLineNumbers "redeployFunctions\getPadsNearBase.sqf"];
missionNamespace setVariable ["getTargetPads", compile preprocessFileLineNumbers "redeployFunctions\getPadsNearTarget.sqf"];
missionNamespace setVariable ["getRegisteredVehicles", compile preprocessFileLineNumbers "redeployFunctions\getRegisteredVehicles.sqf"];

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
publicVariable "removeVehicleFromPadRegistry";
publicVariable "removeVehicleFromAwayPads";

// register all objects that are synced to home_base

private _syncedObjects = synchronizedObjects home_base;
{
	if (_x isKindOf "Helicopter") then {
		_x setVariable ["isRegistered", true, true];
		_x setVariable ["isHeli", true, true];
	};
} forEach _syncedObjects;

//// //// ////////////////////////////////////////////////////////////////////////////////



// once everything is set up, kick off the heartbeat for players (JIP true)
diag_log "[REDEPLOY] kicking off heartbeat...";
// ["[REDEPLOY] kicking off heartbeat..."] remoteExec ["systemChat"];

[] spawn (compile preprocessFileLineNumbers "redeployFunctions\baseHeartbeat.sqf");

diag_log "[REDEPLOY] initHomeBase is done initializing";
// ["[REDEPLOY] initHomeBase is done initializing"] remoteExec ["systemChat"];
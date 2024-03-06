/*
	if you want to create a home base (only 1 is allowed at a time) 
	you first place down an object (or logic entity), and set it's variable name to: 
	
	(missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG")
	
	---
	
	if you want some vehicles to start off being registered, 
	you need to use a logic entity (Systems > Logic entities) instead of a physical object. 
	I like the "Base" under Locations -- do the same setup as above.
	
	then you can sync the vehicles to this logic entity ((missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG"))
	
*/

if (!isServer) exitWith {};

diag_log "[SUPPORT] initHomeBase is beginning initilization...";

missionNamespace setVariable ["vicWatchdog", compile preprocessFileLineNumbers "\Support-Framework\Functions\redeployFunctions\vehicleWatchdog.sqf"];
missionNamespace setVariable ["getBasePads", compile preprocessFileLineNumbers "\Support-Framework\Functions\redeployFunctions\getPadsNearBase.sqf"];
missionNamespace setVariable ["getTargetPads", compile preprocessFileLineNumbers "\Support-Framework\Functions\redeployFunctions\getPadsNearTarget.sqf"];
missionNamespace setVariable ["getRegisteredVehicles", compile preprocessFileLineNumbers "\Support-Framework\Functions\redeployFunctions\getRegisteredVehicles.sqf"];
missionNamespace setVariable ["sideChatter", compile preprocessFileLineNumbers "\Support-Framework\Functions\redeployFunctions\sideChatter.sqf"];
missionNamespace setVariable ["isAtBase", compile preprocessFileLineNumbers "\Support-Framework\Functions\redeployFunctions\isAtBase.sqf"];

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

// register all objects that are synced to (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG")
private _homeBase = missionNamespace getVariable ["YOSHI_HOME_BASE_CONFIG", nil];
private _homeBaseConfigured = !(isNil "_homeBase");
if (_homeBaseConfigured) then {
	private _syncedHomeObjects = synchronizedObjects (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG");
	{
		if (_x isKindOf "Helicopter") then {
			_x setVariable ["isHeli", true, true];
		};
		_x setVariable ["isRegistered", true, true];
	} forEach _syncedHomeObjects;
};

private _casConfig = missionNamespace getVariable ["YOSHI_SUPPORT_CAS_CONFIG", nil];
private _CasConfigured = !(isNil "_casConfig");
if (_CasConfigured) then {
	private _syncedCasObjects = synchronizedObjects (missionNamespace getVariable "YOSHI_SUPPORT_CAS_CONFIG");
	{
		if (_x isKindOf "Helicopter") then {
			_x setVariable ["isHeli", true, true];
		};
		_x setVariable ["isRegistered", true, true];
		_x setVariable ["isCAS", true, true];
	} forEach _syncedCasObjects;
};

private _artyConfig = missionNamespace getVariable ["YOSHI_SUPPORT_ARTILLERY_CONFIG", nil];
private _artyConfigured = !(isNil "_artyConfig");
if (_artyConfigured) then {
	private _syncedCasObjects = synchronizedObjects (missionNamespace getVariable "YOSHI_SUPPORT_ARTILLERY_CONFIG");
	{
		_x setVariable ["isRegistered", true, true];
	} forEach _syncedCasObjects;
};

//// //// ////////////////////////////////////////////////////////////////////////////////



// once everything is set up, kick off the heartbeat for players (JIP true)
diag_log "[SUPPORT] kicking off heartbeat...";
// ["[SUPPORT] kicking off heartbeat..."] remoteExec ["systemChat"];

[] spawn (compile preprocessFileLineNumbers "\Support-Framework\Functions\redeployFunctions\baseHeartbeat.sqf");

diag_log "[SUPPORT] initHomeBase is done initializing";
// ["[SUPPORT] initHomeBase is done initializing"] remoteExec ["systemChat"];
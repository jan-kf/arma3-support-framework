/*
	if you want to create a home base (only 1 is allowed at a time) 
	you first place down an object (or logic entity), and set it's variable name to: 
	
	YOSHI_HOME_BASE_CONFIG
	
	---
	
	if you want some vehicles to start off being registered, 
	you need to use a logic entity (Systems > Logic entities) instead of a physical object. 
	I like the "Base" under Locations -- do the same setup as above.
	
	then you can sync the vehicles to this logic entity (YOSHI_HOME_BASE_CONFIG)
	
*/

if (!isServer) exitWith {};

diag_log "[SUPPORT] initHomeBase is beginning initilization...";

// register all objects that are synced to YOSHI_HOME_BASE_CONFIG

private _homeBaseConfigured = !(isNil "YOSHI_HOME_BASE_CONFIG");
if (_homeBaseConfigured) then {
	private _syncedHomeObjects = synchronizedObjects YOSHI_HOME_BASE_CONFIG;
	{
		if (_x isKindOf "Helicopter") then {
			_x setVariable ["isHeli", true, true];
		};
		_x setVariable ["isRegistered", true, true];
	} forEach _syncedHomeObjects;
};

private _CasConfigured = !(isNil "YOSHI_SUPPORT_CAS_CONFIG");
if (_CasConfigured) then {
	private _syncedCasObjects = synchronizedObjects YOSHI_SUPPORT_CAS_CONFIG;
	{
		if (_x isKindOf "Helicopter") then {
			_x setVariable ["isHeli", true, true];
		};
		_x setVariable ["isRegistered", true, true];
		_x setVariable ["isCAS", true, true];
	} forEach _syncedCasObjects;
};

private _artyConfigured = !(isNil "YOSHI_SUPPORT_ARTILLERY_CONFIG");
if (_artyConfigured) then {
	private _syncedArtyObjects = synchronizedObjects YOSHI_SUPPORT_ARTILLERY_CONFIG;
	{
		_x setVariable ["isRegistered", true, true];
		_x setVariable ["isArtillery", true, true];
	} forEach _syncedArtyObjects;
};

private _reconConfigured = !(isNil "YOSHI_SUPPORT_RECON_CONFIG");
if (_reconConfigured) then {
	private _syncedReconObjects = synchronizedObjects YOSHI_SUPPORT_RECON_CONFIG;
	{
		_x setVariable ["isRegistered", true, true];
		_x setVariable ["isRecon", true, true];
	} forEach _syncedReconObjects;
};

execVM "\Support-Framework\Functions\Client\counterBatteryRadar.sqf";

///////////////////////////////////////////////////

{
    if ([_x] call YOSHI_fnc_isHeliPad) then {
        YOSHI_HELIPAD_INDEX pushBack _x;
    };
} forEach allMissionObjects "HeliH";
publicVariable "YOSHI_HELIPAD_INDEX";

//////////////////////////////////////////////////

{
    [_x] call YOSHI_fnc_setObjectLoadHandling;
} forEach entities "ReammoBox_F";

//// //// /////////////////////////////////////

{
    _x setFuelConsumptionCoef 0.1;
} forEach allMissionObjects "UAV_01_base_F";

///////////////////////////////////////////



// once everything is set up, kick off the heartbeat for players (JIP true)
diag_log "[SUPPORT] kicking off heartbeat...";
// ["[SUPPORT] kicking off heartbeat..."] remoteExec ["systemChat"];

[] spawn YOSHI_fnc_baseHeartbeat;

diag_log "[SUPPORT] initHomeBase is done initializing";
// ["[SUPPORT] initHomeBase is done initializing"] remoteExec ["systemChat"];
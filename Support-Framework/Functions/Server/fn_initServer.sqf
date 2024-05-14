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
	private _syncedArtyObjects = synchronizedObjects (missionNamespace getVariable "YOSHI_SUPPORT_ARTILLERY_CONFIG");
	{
		_x setVariable ["isRegistered", true, true];
		_x setVariable ["isArtillery", true, true];
	} forEach _syncedArtyObjects;
};

private _reconConfig = missionNamespace getVariable ["YOSHI_SUPPORT_RECON_CONFIG", nil];
private _reconConfigured = !(isNil "_reconConfig");
if (_reconConfigured) then {
	private _syncedReconObjects = synchronizedObjects (missionNamespace getVariable "YOSHI_SUPPORT_RECON_CONFIG");
	{
		_x setVariable ["isRegistered", true, true];
		_x setVariable ["isRecon", true, true];
	} forEach _syncedReconObjects;
};

private _virtualStorageConfig = missionNamespace getVariable ["YOSHI_VIRTUAL_STORAGE", nil];
private _virtualStorageConfigured = !(isNil "_virtualStorageConfig");
private _fabricatorConfig = missionNamespace getVariable ["YOSHI_FABRICATOR", nil];
private _fabricatorConfigured = !(isNil "_fabricatorConfig");
if (_virtualStorageConfigured && _fabricatorConfigured) then {
	private _syncedVirtualStorageObjects = synchronizedObjects (missionNamespace getVariable "YOSHI_VIRTUAL_STORAGE");
	private _syncedFabricatorObjects = synchronizedObjects (missionNamespace getVariable "YOSHI_FABRICATOR");
	{
		[_x, _syncedVirtualStorageObjects] remoteExec ["SupportFramework_fnc_addItemsToFabricator", -2, true];
	} forEach _syncedFabricatorObjects;
};

//// //// ////////////////////////////////////////////////////////////////////////////////



// once everything is set up, kick off the heartbeat for players (JIP true)
diag_log "[SUPPORT] kicking off heartbeat...";
// ["[SUPPORT] kicking off heartbeat..."] remoteExec ["systemChat"];

[] spawn SupportFramework_fnc_baseHeartbeat;

diag_log "[SUPPORT] initHomeBase is done initializing";
// ["[SUPPORT] initHomeBase is done initializing"] remoteExec ["systemChat"];
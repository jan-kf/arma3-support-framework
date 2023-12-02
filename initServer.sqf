/*
if you want to create a home base (only 1 is allowed at a time) 
you first place down an object (or logic entity), and set it's variable name to: 

home_base

then provide it this code:

"initHomeBase.sqf" remoteExec ["execVM", 2];

---

if you want some vehicles to start off being registered, 
you need to use a logic entity (Systems > Logic Entities) instead of a physical object. 
I like the "Base" under Locations -- do the same setup as above.

Then you can sync the vehicles to this logic entity (home_base)

*/

if (!isServer) exitWith {};

diag_log "[REDEPLOY] initHomeBase is beginning initilization...";

// setup home_base variables 
private _padRegistry = createHashMap;

private _homeBaseManifest = createHashMapFromArray [
	["padRegistry", _padRegistry],
	["vicRegistry", []],
	["landingPadClasses", ["Land_HelipadEmpty_F", "Land_HelipadCircle_F", "Land_HelipadCivil_F", "Land_HelipadRescue_F", "Land_HelipadSquare_F", "Land_JumpTarget_F"]],
	["activeAwayPads", []],
	["padsNearBase", []]
];
home_base setVariable ["homeBaseManifest", _homeBaseManifest, true];


missionNamespace setVariable ["vicWatchdog", compile preprocessFileLineNumbers "redeployFunctions\vehicleWatchdog.sqf"];


missionNamespace setVariable ["addVicToPlayers", {
	params ["_vehicle"];

	private _playerActionMapCheck = _vehicle getVariable "playerActionMap";
	if (isNil "_playerActionMapCheck") then {
		_vehicle setVariable ["playerActionMap", createHashMap, true];
	};

	private _vehicleName = getText (configFile >> "CfgVehicles" >> (typeOf _vehicle) >> "displayName");
	{
		private _player = _x;
		[[_player, _vehicle], "redeployFunctions\addVicActionToPlayer.sqf"] remoteExec ["execVM", 0]; 
	} forEach allPlayers;
}];

publicVariable "homeBaseManifest";
publicVariable "vicWatchdog";
publicVariable "addVicToPlayers";

// register all objects that are synced to home_base

private _syncedObjects = synchronizedObjects home_base;
{
	if (_x isKindOf "Helicopter") then {
		private _vicRegistry = _homeBaseManifest get "vicRegistry"; 
		_vicRegistry pushBackUnique _x;

		// spawn vechicleWatchdog
		private _watchdog = [_x] spawn {
			params ["_vehicle"];
			[_vehicle] spawn (missionNamespace getVariable "vicWatchdog");
		};

		_x setVariable ["watchdog", _watchdog, true];

		_x setVariable ["isHeli", true, true];

	};
} forEach _syncedObjects;
home_base setVariable ["homeBaseManifest", _homeBaseManifest, true];

////////////////////////////////////////////////////////////////////////////////////////

missionNamespace setVariable ["removeVicFromPlayers", {
	params ["_vehicle"];
	
	private _playerActionMap = _vehicle getVariable "playerActionMap";
	if (isNil "_playerActionMap") exitWith {};

	private _vehicleName = getText (configFile >> "CfgVehicles" >> (typeOf _vehicle) >> "displayName");
	{
		private _actionID = _playerActionMap get (netId _x);
		[_x, _actionID] remoteExec ["removeAction", 0, true]; 
	} forEach allPlayers;

	_vehicle setVariable ["playerActionMap", createHashMap, true]; // clear out the actionMap
}];

missionNamespace setVariable ["removeVehicleFromPadRegistry", {
	params ["_vehicle"];
	private _registry = home_base getVariable "homeBaseManifest" get "padRegistry";
	{
		if (_y == (netId _vehicle)) then {
			// release assignment of pad if vic leaves the base
			_registry set [_x, "unassigned"];
		}
	} forEach _registry;
}];

missionNamespace setVariable ["isVehicleRegistered", {
	params ["_vehicle"];
	private _vicRegistry = home_base getVariable "homeBaseManifest" get "vicRegistry";
	_vehicle in _vicRegistry
}];

// Function to register a vehicle
missionNamespace setVariable ["registerVehicle", {
	params ["_vehicle"];

	private _vicIsRegistered = [_vehicle] call (missionNamespace getVariable "isVehicleRegistered");

	if (!_vicIsRegistered) then {
		// register the vic
		private _manifest = home_base getVariable "homeBaseManifest";
		private _vicRegistry = _manifest get "vicRegistry";
		_vicRegistry pushBackUnique _vehicle;
		home_base setVariable ["homeBaseManifest", _manifest, true];

		// terminate vechicleWatchdog, base heatbeat will re-init
		private _watchdog = _vehicle getVariable "watchdog";
		if (!isNil "_watchdog") then{
			terminate _watchdog;
			_vehicle setVariable ["watchdog", nil, true];
		};

		[_vehicle] call (missionNamespace getVariable "addVicToPlayers"); 

		[[_vehicle], "redeployFunctions\addUnresistrationAction.sqf"] remoteExec ["execVM", 0, true]; 
	};
}];

// Function to unregister a vehicle
missionNamespace setVariable ["unregisterVehicle", {
	params ["_vehicle"];

	private _vicIsRegistered = [_vehicle] call (missionNamespace getVariable "isVehicleRegistered");

	if (_vicIsRegistered) then {
		// unregister vic
		private _manifest = home_base getVariable "homeBaseManifest";
		private _vicRegistry = _manifest get "vicRegistry";
		_vicRegistry deleteAt (_vicRegistry find _vehicle);
		home_base setVariable ["homeBaseManifest", _manifest, true];

		// terminate vechicleWatchdog
		private _watchdog = _vehicle getVariable "watchdog";
		if (!isNil "_watchdog") then{
			terminate _watchdog;
			_vehicle setVariable ["watchdog", nil, true];
		};

		[_vehicle] call (missionNamespace getVariable "removeVicFromPlayers");

		[[_vehicle], "redeployFunctions\addResistrationAction.sqf"] remoteExec ["execVM", 0, true];
	
	};
}];

publicVariable "removeVicFromPlayers";
publicVariable "removeVehicleFromPadRegistry";
publicVariable "isVehicleRegistered";
publicVariable "registerVehicle";
publicVariable "unregisterVehicle";

// once everything is set up, kick off the heartbeat for players (JIP true)
diag_log "[REDEPLOY] kicking off heartbeat...";
["[REDEPLOY] kicking off heartbeat..."] remoteExec ["systemChat"];

[] spawn (compile preprocessFileLineNumbers "redeployFunctions\baseHeartbeat.sqf");

diag_log "[REDEPLOY] initHomeBase is done initializing";
["[REDEPLOY] initHomeBase is done initializing"] remoteExec ["systemChat"];
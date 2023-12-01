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
missionNamespace setVariable ["homeBaseManifest", _homeBaseManifest];

missionNamespace setVariable ["vicWatchdog", compile preprocessFileLineNumbers "redeployFunctions\vehicleWatchdog.sqf"];

// register all objects that are synced to home_base

missionNamespace setVariable ["addVicToPlayers", {
	params ["_vehicle"];

	private _playerActionMapCheck = _vehicle getVariable "playerActionMap";
	if (isNil "_playerActionMapCheck") then {
		_vehicle setVariable ["playerActionMap", createHashMap, true];
	};

	private _vehicleName = getText (configFile >> "CfgVehicles" >> (typeOf _vehicle) >> "displayName");
	{
		_x setVariable ["show-" + netId _vehicle, true, true];
		private _condition = format["('hgun_esd_01_F' in (items %2)) && ((%2 getVariable ['show-%1', false]) isEqualTo true)", netId _vehicle, _x];
		[[_x, _vehicle, _vehicleName, _condition], "redeployFunctions\addVicActionToPlayer.sqf"] remoteExec ["execVM", 0, true];
	} forEach allPlayers;
}];


private _syncedObjects = synchronizedObjects home_base;
{
	if (_x isKindOf "Helicopter") then {
		private _vicRegistry = _homeBaseManifest get "vicRegistry"; 
		_vicRegistry pushBack _x;

		// spawn vechicleWatchdog
		private _watchdog = [_x] spawn {
			params ["_vehicle"];
			[_vehicle] spawn (missionNamespace getVariable "vicWatchdog");
		};

		_x setVariable ["vicStatus", createHashMapFromArray [
			["regActionID", nil],
			["requestActionID", nil],
			["requestingRedeploy", false],
			["isReinserting", false],
			["waveOff", false],
			["cancelRedeploy", false],
			["destination", nil],
			["isHeli", true],
			["awayParkingPass", nil],
			["watchdog", _watchdog],
			["currentTask", "resistered"]
		], true];

		[_x, (missionNamespace getVariable "addVicToPlayers")] remoteExec["call", 0, true];

	};
} forEach _syncedObjects;

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
}];

missionNamespace setVariable ["removeVehicleFromPadRegistry", {
	params ["_vehicle"];
	private _registry = missionNamespace getVariable "homeBaseManifest" get "padRegistry";
	{
		if (_y == (netId _vehicle)) then {
			// release assignment of pad if vic leaves the base
			_registry set [_x, "unassigned"];
		}
	} forEach _registry;
}];

missionNamespace setVariable ["getVehicleStatus", {
	params ["_vehicle"];
	private _vicStatus = _vehicle getVariable "vicStatus";
	if (isNil "_vicStatus") then {
		_vicStatus = createHashMapFromArray [
			["regActionID", nil],
			["requestActionID", nil],
			["requestingRedeploy", false],
			["isReinserting", false],
			["waveOff", false],
			["cancelRedeploy", false],
			["destination", nil],
			["isHeli", _vehicle isKindOf "Helicopter"],
			["awayParkingPass", nil]
		];
		_vehicle setVariable ["vicStatus", _vicStatus, true];
	};
	_vicStatus
}];

missionNamespace setVariable ["_isVehicleRegistered", {
	params ["_vehicle"];
	private _vicRegistry = missionNamespace getVariable "homeBaseManifest" get "vicRegistry";
	_vehicle in _vicRegistry
}];

// Function to register a vehicle
missionNamespace setVariable ["_registerVehicle", {
	params ["_vehicle"];

	private _vicIsRegistered = [_vehicle] call (missionNamespace getVariable "_isVehicleRegistered");

	if (!_vicIsRegistered) then {
		// register the vic
		private _vicRegistry = missionNamespace getVariable "homeBaseManifest" get "vicRegistry";
		_vicRegistry pushBackUnique _vehicle;

		private _vicStatus = [_vehicle] call (missionNamespace getVariable "getVehicleStatus");

		// spawn vechicleWatchdog
		private _watchdog = [_vehicle] spawn {
			params ["_vehicle"];
			[_vehicle] spawn (missionNamespace getVariable "vicWatchdog");
		};
		_vicStatus set ["watchdog", _watchdog];
		_vicStatus set ["currentTask", "resistered"];

		[_x, (missionNamespace getVariable "addVicToPlayers")] remoteExec["call", 0, true];

		// remove old action if it exists
		private _oldRegActionID = _vicStatus get "regActionID";
		if (!isNil "_oldRegActionID") then {
			_vehicle removeAction _oldRegActionID;
		};

		[[_vehicle], "redeployFunctions\addUnresistrationAction.sqf"] remoteExec ["execVM", 0, true];
	};
}];

// Function to unregister a vehicle
missionNamespace setVariable ["_unregisterVehicle", {
	params ["_vehicle"];

	private _vicIsRegistered = [_vehicle] call (missionNamespace getVariable "_isVehicleRegistered");

	if (_vicIsRegistered) then {
		// unregister vic
		private _vicRegistry = missionNamespace getVariable "homeBaseManifest" get "vicRegistry";
		_vicRegistry deleteAt (_vicRegistry find _vehicle);

		private _vicStatus = [_vehicle] call (missionNamespace getVariable "getVehicleStatus");

		// terminate vechicleWatchdog
		private _watchdog = _vicStatus get "watchdog";
		if (!isNil "watchdog") then{
			terminate _watchdog;
		};

		[_vehicle] call (missionNamespace getVariable "removeVicFromPlayers");

		// remove old action if it exists
		private _oldRegActionID = _vicStatus get "regActionID";
		if (!isNil "_oldRegActionID") then {
			_vehicle removeAction _oldRegActionID;
		};
		// remove any request for redeploy if it gets unregistered
		private _requestActionID = _vicStatus get "requestActionID";
		_vicStatus set ["requestingRedeploy", false];

		// remove current action to stay up to date
		if (!isNil "_requestActionID") then {
			_vehicle removeAction _requestActionID;
			_vicStatus set ["requestActionID", nil];
		};

		[[_vehicle], "redeployFunctions\addResistrationAction.sqf"] remoteExec ["execVM", 0, true];
	
	};
}];

// once everything is set up, kick off the heartbeat for players (JIP true)
diag_log "[REDEPLOY] kicking off heartbeat...";
["[REDEPLOY] kicking off heartbeat..."] remoteExec ["systemChat"];

[] execVM "redeployFunctions\baseHeartbeat.sqf";

diag_log "[REDEPLOY] initHomeBase is done initializing";
["[REDEPLOY] initHomeBase is done initializing"] remoteExec ["systemChat"];
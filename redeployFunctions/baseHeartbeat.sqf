if (!isServer) exitWith {};

diag_log "[REDEPLOY] heartbeat starting ...";
["[REDEPLOY] heartbeat starting ..."] remoteExec ["systemChat"];

private _addRegistrationChoicesToVehicles = {
	// this function kicks off the addition of the register/unregister functions on vehicles

	params ["_vic"];

	private _vicIsRegistered = [_vic] call (missionNamespace getVariable "isVehicleRegistered");

	if (_vicIsRegistered) then {
		[[_vic], "redeployFunctions\addUnresistrationAction.sqf"] remoteExec ["execVM", 0, true];
	} else {
		[[_vic], "redeployFunctions\addResistrationAction.sqf"] remoteExec ["execVM", 0, true];
	};
};


// gameloop -- consider making separate functions and "spawn" -ing them in separate threads
while {true} do {

	// ["base Heartbeat, bu bum..."] remoteExec ["systemChat"];
	diag_log "[REDEPLOY] base heartbeat, bu bum...";
	private _homeBaseManifest = home_base getVariable "homeBaseManifest";

	// Find all vehicles within a certain radius of home_base
	private _vehiclesNearBase = home_base nearEntities ["Helicopter", 500]; // Adjust the radius as needed

	// Iterate through each vehicle and perform your desired command
	{
		// Your command here. Example:
		// hint format ["Vehicle %1 is near the base", _x];
		private _vehicle = _x;

		private _hasRegistrationAction = _vehicle getVariable "regActionID";
		
		private _checkHeli = _x getVariable "isHeli";
		if (_x isKindOf "Helicopter" && isNil "_checkHeli") then {
			_x setVariable ["isHeli", true, true];
		};

		if (_x isKindOf "Helicopter" && isNil "_hasRegistrationAction") then {
			[_x] call _addRegistrationChoicesToVehicles;
		};

		private _vicIsRegistered = [_vehicle] call (missionNamespace getVariable "isVehicleRegistered");
		if (_vicIsRegistered) then {
			// check if watchdog is running, if not, start it
			private _watchdog = _vehicle getVariable "watchdog";
			if (isNil "_watchdog") then{
				_watchdog = [_vehicle] spawn {
					params ["_vehicle"];
					[_vehicle] spawn (missionNamespace getVariable "vicWatchdog");
				};
				_vehicle setVariable ["watchdog", _watchdog, true];
			};
		};

	} forEach _vehiclesNearBase;

	// register new pads, remove any pads that have been deleted
	private _padsNearBase = nearestObjects [home_base, _homeBaseManifest get "landingPadClasses", 500]; 
	_homeBaseManifest set ["padsNearBase", _padsNearBase];
	home_base setVariable ["homeBaseManifest", _homeBaseManifest, true];
	private _padIdsNearBase = _padsNearBase apply { netId _x };
	private _padRegistry = _homeBaseManifest get "padRegistry";
	{
		// add any missing pads
		if (!(_x in _padRegistry)) then {
			_padRegistry set [_x, "unassigned"]
		};
	} forEach _padIdsNearBase;
	private _allPads = keys _padRegistry;
	// find if any pads were removed
	private _padsToRemove = [];
	{
		if (!(_x in _padIdsNearBase)) then {
			_padsToRemove pushBack _x;
		}
	} forEach _allPads;
	// if any pads were removed, then delete them from registry
	{
		_padRegistry deleteAt _x;
	} forEach _padsToRemove;
	
    sleep 3; 
};
if (!isServer) exitWith {};

diag_log "[REDEPLOY] heartbeat starting ...";
["[REDEPLOY] heartbeat starting ..."] remoteExec ["systemChat"];

private _addRegistrationChoicesToVehicles = {
	// this function kicks off the addition of the register/unregister functions on vehicles

	params ["_vic"];


	[[_vic], "redeployFunctions\addRegistrationAction.sqf"] remoteExec ["execVM", 2];


	sleep 1; // should spawn a task to wait and update each action...

	private _vicIsRegistered = _vic getVariable ["isRegistered", false];
	if (_vicIsRegistered) then {
		private _actionID = _vic getVariable "regActionID";
		if (!isNil "_actionID") then {
			private _vehicleClass = typeOf _vic;
			private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
			[[MissionNamespace, "UpdateActionText", [_vic, _actionID, format["Unregister %1", _vehicleDisplayName], "#FF8000"]], BIS_fnc_callScriptedEventHandler] remoteExec ["call", 0];
		};
	};
};

private _safeIsNull = {
    params ["_var"];

    if (_var isEqualTo false) then {
        true; // The variable is undefined (nil)
    } else {
        isNull _var; // The variable is defined, check if it's a null object
    };
};


// gameloop -- consider making separate functions and "spawn" -ing them in separate threads
while {true} do {

	// ["base Heartbeat, bu bum..."] remoteExec ["systemChat"];
	diag_log "[REDEPLOY] base heartbeat, bu bum...";

	// Find all vehicles within a certain radius of home_base
	private _vehiclesNearBase = home_base nearEntities ["Helicopter", 500]; // Adjust the radius as needed

	// Iterate through each vehicle and perform your desired command
	{
		// Your command here. Example:
		// hint format ["Vehicle %1 is near the base", _x];
		private _vehicle = _x;

		private _hasRegistrationAction = _vehicle getVariable "regActionID";
		
		private _checkHeli = _vehicle getVariable "isHeli";
		if (_vehicle isKindOf "Helicopter" && isNil "_checkHeli") then {
			_vehicle setVariable ["isHeli", true, true];
		};

		if (_vehicle isKindOf "Helicopter" && isNil "_hasRegistrationAction") then {
			[_vehicle] call _addRegistrationChoicesToVehicles;
		};

		private _vicIsRegistered = _vehicle getVariable ["isRegistered", false];
		private _watchdog = _vehicle getVariable ["watchdog", false];
		if (_vicIsRegistered && [_watchdog] call _safeIsNull) then {
			// check if watchdog is running, if not, start it
			[format ["kicking off wd for: %1 ... ", _vehicle]] remoteExec ["systemChat"];

			_watchdog = [_vehicle] spawn (missionNamespace getVariable "vicWatchdog");
			sleep 2;
			_vehicle setVariable ["watchdog", _watchdog, true];
		};
		if (!_vicIsRegistered && !isNil "_watchdog" && (_watchdog isNotEqualTo false)) then {
			// if not registered, and a watchdog exists, kill it.
			[format ["terminating wd for: %1 ... ", _vehicle]] remoteExec ["systemChat"];
			terminate _watchdog;
			_vehicle setVariable ["watchdog", nil, true];
		};

	} forEach _vehiclesNearBase;
	
    sleep 3; 
};
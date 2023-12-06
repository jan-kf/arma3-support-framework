if (!isServer) exitWith {};

diag_log "[REDEPLOY] heartbeat starting ...";
// ["[REDEPLOY] heartbeat starting ..."] remoteExec ["systemChat"];

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
		
		private _checkHeli = _vehicle getVariable "isHeli";
		if (_vehicle isKindOf "Helicopter" && isNil "_checkHeli") then {
			_vehicle setVariable ["isHeli", true, true];
		};

		private _vicIsRegistered = _vehicle getVariable ["isRegistered", false];
		private _watchdog = _vehicle getVariable ["watchdog", false];
		if (_vicIsRegistered && [_watchdog] call _safeIsNull) then {
			// check if watchdog is running, if not, start it
			// [format ["kicking off wd for: %1 ... ", _vehicle]] remoteExec ["systemChat"];

			_watchdog = [_vehicle] spawn (missionNamespace getVariable "vicWatchdog");
			sleep 2;
			_vehicle setVariable ["watchdog", _watchdog, true];
		};
		if (!_vicIsRegistered && !isNil "_watchdog" && (_watchdog isNotEqualTo false)) then {
			// if not registered, and a watchdog exists, kill it.
			// [format ["terminating wd for: %1 ... ", _vehicle]] remoteExec ["systemChat"];
			terminate _watchdog;
			_vehicle setVariable ["watchdog", nil, true];
		};

	} forEach _vehiclesNearBase;
	
    sleep 3; 
};
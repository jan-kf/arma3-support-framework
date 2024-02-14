if (!isServer) exitWith {};

diag_log "[SUPPORT] heartbeat starting ...";
// ["[SUPPORT] heartbeat starting ..."] remoteExec ["systemChat"];

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
	diag_log "[SUPPORT] base heartbeat, bu bum...";

	// Find all vehicles within a certain radius of (missionNamespace getVariable "home_base")
	private _vehiclesNearBase = (missionNamespace getVariable "home_base") nearEntities ["Helicopter", ((missionNamespace getVariable "home_base") getVariable ["Radius", 500])]; // Adjust the radius as needed

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

	// Function to get markers and spawn landing pads if necessary

    {
        private _markerName = _x;
        private _displayName = toLower (markerText _markerName);
        if ((_displayName find "hls " == 0) || (_displayName find "lz " == 0)) then {
            private _markerPos = getMarkerPos _markerName;
            // Check for existing landing pads
            private _landingPadsNearby = nearestObjects [_markerPos, ["Land_HelipadEmpty_F"], 10];
            if (count _landingPadsNearby == 0) then {
                // No landing pad nearby, spawn one
                private _landingPad = createVehicle ["Land_HelipadEmpty_F", _markerPos, [], 0, "CAN_COLLIDE"];
            };
        };
    } forEach allMapMarkers;
	
    sleep 3; 
};
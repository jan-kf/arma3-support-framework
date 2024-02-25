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

private _isArtilleryCapable = {
    params ["_unit"];
    
    // Check if the unit is capable of artillery fire
    // This checks if the unit is an artillery piece by verifying it can accept the doArtilleryFire command
    private _isArtillery = !(_unit isKindOf "Air") && {(_unit isKindOf "LandVehicle") || (_unit isKindOf "Ship")}; // Exclude air units, include land vehicles and ships
    private _canDoArtilleryFire = _isArtillery && {alive _unit} && {getArtilleryAmmo [_unit] isNotEqualTo []}; // Must be alive and have artillery ammo available

    _canDoArtilleryFire // Return true if capable, false otherwise
};




// gameloop -- consider making separate functions and "spawn" -ing them in separate threads
while {true} do {
	
	private _homeBase = missionNamespace getVariable ["home_base", nil];

	if (isNil "_homeBase") exitWith {diag_log "[SUPPORT] home_base is not set, terminating process";};
	
	diag_log "[SUPPORT] base heartbeat, bu bum...";
	// Find all vehicles within a certain radius of _homeBase
	private _vehiclesNearBase = _homeBase nearEntities ["Helicopter", (_homeBase getVariable ["Radius", 500])]; 

	// Iterate through each vehicle
	{
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
	private _lzPrefixStr = (missionNamespace getVariable "home_base") getVariable ["LzPrefixes", ""];
	private _lzPrefixes = [];
	if (_lzPrefixStr != "") then {
		_lzPrefixes = _lzPrefixStr splitString ", ";
	} else {
		_lzPrefixes = ["lz ", "hls "]; // default value -- hard fallback
	};

    {
        private _markerName = _x;
        private _displayName = toLower (markerText _markerName);
		private _lzMatch = false;
		{
			private _prefix = toLower _markerName;
			if (_displayName find _prefix == 0) exitWith {
				_lzMatch = true;
			}
		} forEach _lzPrefixes;
        if (_lzMatch) then {
            private _markerPos = getMarkerPos _markerName;
            // Check for existing landing pads
            private _landingPadsNearby = nearestObjects [_markerPos, ["Land_HelipadEmpty_F"], 10];
            if (count _landingPadsNearby == 0) then {
                // No landing pad nearby, spawn one
                private _landingPad = createVehicle ["Land_HelipadEmpty_F", _markerPos, [], 0, "CAN_COLLIDE"];
            };
        };
    } forEach allMapMarkers;

	private _baseSide = (missionNamespace getVariable "home_base") getVariable ["BaseSide", ""];
	{
		private _vehicle = _x;

		private _isArtillery = [_vehicle] call _isArtilleryCapable;
		private _checkArtillery = _vehicle getVariable "isArtillery";
		if (_isArtillery && isNil "_checkArtillery") then {
			_vehicle setVariable ["isArtillery", true, true];
		};

	} forEach (vehicles select {(toLower str(side _x)) isEqualTo (toLower _baseSide)});
	
    sleep 3; 
};
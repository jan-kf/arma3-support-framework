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

private _artyConfigured = [YOSHI_SUPPORT_ARTILLERY_CONFIG_OBJECT] call YOSHI_isInitialized;
private _fixedWingsConfigured = [YOSHI_FW_CONFIG_OBJECT] call YOSHI_isInitialized;


// gameloop -- consider making separate functions and "spawn" -ing them in separate threads
while {true} do {
	

	if (!([YOSHI_HOME_BASE_CONFIG_OBJECT] call YOSHI_isInitialized) ) exitWith {diag_log "[SUPPORT] YOSHI_HOME_BASE_CONFIG_OBJECT is not set, terminating process";};
	
	diag_log "[SUPPORT] base heartbeat, bu bum...";
	// Find all vehicles within a certain radius of YOSHI_HOME_BASE_CONFIG_OBJECT
	private _vehiclesNearBase = vehicles select {(_x call YOSHI_fnc_isAtBase) && (_x isKindOf "Helicopter")}; 

	// Iterate through each vehicle
	{
		private _vehicle = _x;
		private _isAlive = alive _vehicle;
		
		private _checkHeli = _vehicle getVariable "isHeli";
		if (_vehicle isKindOf "Helicopter" && isNil "_checkHeli") then {
			_vehicle setVariable ["isHeli", true, true];
		};
		private _vicIsRegistered = _vehicle getVariable ["isRegistered", false];
		private _watchdog = _vehicle getVariable ["watchdog", false];
		private _getInIndex = _vehicle getVariable ["get_in_EH_index", false];
		if (_isAlive && _vicIsRegistered && [_watchdog] call _safeIsNull) then {
			// check if watchdog is running, if not, start it
			// [format ["kicking off wd for: %1 ... ", _vehicle]] remoteExec ["systemChat"];

			_watchdog = [_vehicle] spawn YOSHI_fnc_vehicleWatchdog;
			sleep 2;
			_vehicle setVariable ["watchdog", _watchdog, true];
			if (_getInIndex isEqualTo false) then {
				_getInIndex = _vehicle addEventHandler ["GetIn", {
					params ["_vehicle", "_role", "_unit", "_turret"];
					private _msgArray = [
						"Hello %1, make yourself comfortable as we prepare for departure.",
						"Greetings %1, your seat awaits you. Please buckle up as we get ready to move.",
						"%1 has joined us. Welcome! Please ensure your belongings are securely stowed.",
						"Good to have you with us, %1. We'll be on our way shortly.",
						"Ah, %1! We've been expecting you. Please find a seat and relax.",
						"Welcome %1! Sit back and enjoy the ride.",
						"It's a pleasure to see you, %1. I hope you find your journey comfortable.",
						"%1 is now on board. We can begin our journey together.",
						"Attention everyone, %1 has just boarded. Let’s extend a warm welcome.",
						"%1, welcome aboard! We trust you'll have a pleasant experience with us today."
					];
					private _hello = _msgArray select (floor (random (count _msgArray)));
					private _msg = format [_hello, name _unit];
					[_vehicle, _msg] call YOSHI_fnc_vehicleChatter;
				}];
				_vehicle setVariable ["get_in_EH_index", _getInIndex, true];
			};
		};
		if (!_vicIsRegistered && !isNil "_watchdog" && (_watchdog isNotEqualTo false)) then {
			// if not registered, and a watchdog exists, kill it.
			// [format ["terminating wd for: %1 ... ", _vehicle]] remoteExec ["systemChat"];
			terminate _watchdog;
			_vehicle setVariable ["watchdog", nil, true];
			if (_getInIndex isNotEqualTo false) then {
				_vehicle removeEventHandler ["GetIn", _getInIndex];
				_vehicle setVariable ["get_in_EH_index", false, true];
			};
		};

	} forEach _vehiclesNearBase;

	// Function to get markers and spawn landing pads if necessary
	{
        private _markerName = _x;
        private _displayName = toLower (markerText _markerName);
		private _lzMatch = false;


		{
			private _prefix = toLower _x;
			if (_displayName find _prefix == 0) exitWith {
				_lzMatch = true;
			}
		} forEach (YOSHI_HOME_BASE_CONFIG_OBJECT get "LzPrefixes");
        if (_lzMatch) then {
            private _markerPos = getMarkerPos _markerName;
            // Check for existing landing pads
            private _landingPadsNearby = [_markerPos, 10] call YOSHI_fnc_getPadsNearTarget;
            if (count _landingPadsNearby == 0) then {
                // No landing pad nearby, spawn one
                private _landingPad = createVehicle ["Land_HelipadEmpty_F", _markerPos, [], 0, "CAN_COLLIDE"];
            };
        };
    } forEach allMapMarkers;

	if (_artyConfigured) then {
		{
			private _vehicle = _x;

			private _isArtillery = [_vehicle] call YOSHI_isArtilleryCapable;
			private _checkArtillery = _vehicle getVariable "isArtillery";
			if (_isArtillery && isNil "_checkArtillery") then {
				_vehicle setVariable ["isArtillery", true, true];
			};

		} forEach (vehicles select {(side _x) isEqualTo (YOSHI_SUPPORT_ARTILLERY_CONFIG_OBJECT get "BaseSide")});
	};

	if (_fixedWingsConfigured) then {
		{
			private _caller = _x getVariable ["YOSHI_FW_CALLER", objNull];
			if (!isNull _caller) then {
				private _group = group _x;
				if ((getWPPos [_group, 0]) distance2D (getPosASL _caller) > 100) then {
					_currentWaypoint = currentWaypoint _group;
					_currentWaypoint setWaypointPosition (getPosASL _caller);
				};
			};
			_x flyInHeight [1000, true];
		} forEach (YOSHI_FW_CONFIG_OBJECT get "DeployedUnits");
	};
	
	
	_keysToRemove = [];
	{
		_marker = _y select 0;
		_currentMarkerAlpha = markerAlpha _marker;
		if (_currentMarkerAlpha > 0.1) then {
			_marker setMarkerAlpha (_currentMarkerAlpha - 0.1);
		}; 

		_trail = _y select 1;
		_currentTrailAlpha = markerAlpha _trail;
		if (_currentTrailAlpha > 0.1) then {
			_trail setMarkerAlpha (_currentTrailAlpha - 0.1);
		};

		_time = _y select 3;

		if ((serverTime - _time) > 30) then {
			_keysToRemove pushBack _x;
		}; 

	} forEach YOSHI_ReconMarkersMap;
	{[YOSHI_ReconMarkersMap, _x] call YOSHI_removeMarker} forEach _keysToRemove;
	
    sleep 3; 
};
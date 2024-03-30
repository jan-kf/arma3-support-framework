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


private _uavAction = [
	"UAV_field_task", // Action ID
	"Field Actions", // Title
	"", // Icon (leave blank for no icon or specify a path)
	{}, // Code executed when the action is used
	{ true }, // Condition for the action to be available
	{
		params ["_vic", "_caller", "_params"];
		// RECON search details
		private _actions = [];

		private _reconPrefixStr = (missionNamespace getVariable "YOSHI_SUPPORT_RECON_CONFIG") getVariable ["ReconPrefixes", ""];
		private _reconPrefixes = [];
		if (_reconPrefixStr != "") then {
			_reconPrefixes = _reconPrefixStr splitString ", ";
		} else {
			_reconPrefixes = ["recon ", "rp ", "watch "]; // default value -- hard fallback
		};

		{ // add all valid markers as valid locations
			
			// marker details
			private _marker = _x;
			private _markerName = markerText _marker;
			private _displayName = toLower _markerName;
			
			{
				private _prefix = toLower _x;
				if (_displayName find _prefix == 0) then {
					private _uavFieldAction = [
						format["reconTo-%2", _marker], format["Request Recon at %1", _markerName], "",
						{
							// statement 
							params ["_target", "_caller", "_args"];
							private _vic = _args select 0;
							private _marker = _args select 1;

							[_vic, getMarkerPos _marker, _caller] remoteExec ["SupportFramework_fnc_requestFieldRecon", 2];
						}, 
						{
							params ["_target", "_caller", "_args"];
							private _vic = _args select 0;
							// // Condition code here
							private _reconConfig = missionNamespace getVariable ["YOSHI_SUPPORT_RECON_CONFIG", nil];
							private _ReconConfigured = !(isNil "_reconConfig");
							private _isUAV = unitIsUAV _vic;
							_ReconConfigured && _isUAV
						},
						{}, // 5: Insert children code <CODE> (Optional)
						[_vic, _marker] // 6: Action parameters <ANY> (Optional)
					] call ace_interact_menu_fnc_createAction;
					_actions pushBack [_uavFieldAction, [], _vic];
				};
			} forEach _reconPrefixes;

		} forEach allMapMarkers;		
			
		_actions
	}
] call ace_interact_menu_fnc_createAction;


// gameloop -- consider making separate functions and "spawn" -ing them in separate threads
while {true} do {
	
	private _homeBase = missionNamespace getVariable ["YOSHI_HOME_BASE_CONFIG", nil];

	if (isNil "_homeBase") exitWith {diag_log "[SUPPORT] YOSHI_HOME_BASE_CONFIG is not set, terminating process";};
	
	diag_log "[SUPPORT] base heartbeat, bu bum...";
	// Find all vehicles within a certain radius of _homeBase
	private _vehiclesNearBase = vehicles select {(_x call SupportFramework_fnc_isAtBase) && (_x isKindOf "Helicopter")}; 

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
		if (_isAlive && _vicIsRegistered && [_watchdog] call _safeIsNull) then {
			// check if watchdog is running, if not, start it
			// [format ["kicking off wd for: %1 ... ", _vehicle]] remoteExec ["systemChat"];

			_watchdog = [_vehicle] spawn SupportFramework_fnc_vehicleWatchdog;
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
	private _lzPrefixStr = (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["LzPrefixes", ""];
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
			private _prefix = toLower _x;
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

	private _baseSide = (missionNamespace getVariable "YOSHI_SUPPORT_ARTILLERY_CONFIG") getVariable ["BaseSide", "west"];
	if ((typeName _baseSide) != "STRING") then {
		_baseSide = toLower str(_baseSide)
	};

	if (!isNil "_baseSide") then {
		{
			private _vehicle = _x;

			private _isArtillery = [_vehicle] call _isArtilleryCapable;
			private _checkArtillery = _vehicle getVariable "isArtillery";
			if (_isArtillery && isNil "_checkArtillery") then {
				_vehicle setVariable ["isArtillery", true, true];
			};

		} forEach (vehicles select {(toLower str(side _x)) isEqualTo _baseSide});
	};


	
	{
		private _uav = _x;
		if (!(_uav getVariable ["hasFieldActions", false])) then {
			[_uav, 0, ["ACE_MainActions"], _uavAction] call ace_interact_menu_fnc_addActionToObject;
			_uav setVariable ["hasFieldActions", true, true];
		}
	} forEach allUnitsUAV;
	
    sleep 3; 
};
/*
if you want to create a home base (only 1 is allowed at a time) 
you first place down an object (or logic entity), and set it's variable name to: 

home_base

then provide it this code:

execVM "initHomeBase.sqf";

---

if you want some vehicles to start off being registered, 
you need to use a logic entity (Systems > Logic Entities) instead of a physical object. 
I like the "Base" under Locations -- do the same setup as above.

Then you can sync the vehicles to this logic entity (home_base)

*/


#include "redeployFunctions\vicRegistration.sqf"

// setup home_base variables 
private _padRegistry = createHashMap;
home_base setVariable ["padRegistry", _padRegistry];
home_base setVariable ["vicRegistry", []];
home_base setVariable ["landingPadClasses", ["Land_HelipadEmpty_F", "Land_HelipadCircle_F", "Land_HelipadCivil_F", "Land_HelipadRescue_F", "Land_HelipadSquare_F", "Land_JumpTarget_F"]];
home_base setVariable ["activeAwayPads", []];

// Function to check if a vehicle is registered


// register all objects that are synced to home_base
private _syncedObjects = synchronizedObjects home_base;
{
	if (_x isKindOf "Helicopter") then {
		private _vicRegistry = home_base getVariable ["vicRegistry", []];
		_vicRegistry pushBack _x;
	};
} forEach _syncedObjects;

////////////////////////////////////////////////////////////////////////////////////////

missionNamespace setVariable ["_isVehicleRegistered", {
    params ["_vehicle"];
    private _vicRegistry = home_base getVariable ["vicRegistry", []];
    _vehicle in _vicRegistry
}];

// Function to register a vehicle
missionNamespace setVariable ["_registerVehicle", {
    params ["_vehicle"];

    private _vicIsRegistered = [_vehicle] call (missionNamespace getVariable "_isVehicleRegistered");

    if (!_vicIsRegistered) then {
        // register the vic
        private _vicRegistry = home_base getVariable ["vicRegistry", []];
        _vicRegistry pushBackUnique _vehicle;

        // remove old action if it exists
        private _oldRegActionID = _vehicle getVariable ["regActionID", nil];
        if (!isNil "_oldRegActionID") then {
            _vehicle removeAction _oldRegActionID;
        };

        // add new action
        private _vehicleClass = typeOf _vehicle;
        private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
        private _regActionID = _vehicle addAction [
            format ["<t color='#FF8000'>Unregister %1</t>", _vehicleDisplayName], 
            {
				private _vehicle = _this select 0;
                [_vehicle] call (missionNamespace getVariable "_unregisterVehicle");
            },
            nil, 6, false, true, "", "true", 5, false, "", ""
        ];

        // save action id for later
        _vehicle setVariable ["regActionID", _regActionID, true];
    };
}];

// Function to unregister a vehicle
missionNamespace setVariable ["_unregisterVehicle", {
    params ["_vehicle"];

    private _vicIsRegistered = [_vehicle] call (missionNamespace getVariable "_isVehicleRegistered");

    if (_vicIsRegistered) then {
        // unregister vic
        private _vicRegistry = home_base getVariable ["vicRegistry", []];
        _vicRegistry deleteAt (_vicRegistry find _vehicle);

        // remove old action if it exists
        private _oldRegActionID = _vehicle getVariable ["regActionID", nil];
        if (!isNil "_oldRegActionID") then {
            _vehicle removeAction _oldRegActionID;
        };

        // add new action
        private _vehicleClass = typeOf _vehicle;
        private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
        private _regActionID = _vehicle addAction [
            format ["<t color='#00ABFF'>Register %1</t>", _vehicleDisplayName], 
            {
				private _vehicle = _this select 0;
                [_vehicle] call (missionNamespace getVariable "_registerVehicle");
            },
            nil, 6, false, true, "", "true", 5, false, "", ""
        ];

		// remove any request for redeploy if it gets unregistered
		private _requestActionID = _vehicle getVariable ["requestActionID", nil];
		_vehicle setVariable ["requestingRedeploy", false, true];

		// remove current action to stay up to date
		if (!isNil "_requestActionID") then {
			_vehicle removeAction _requestActionID;
			_vehicle setVariable ["requestActionID", nil, true];
		};

        // save action id for later
        _vehicle setVariable ["regActionID", _regActionID, true];
    
    };
}];

// // Usage
// [_vehicle] call _registerVehicle;
// [_vehicle] call _unregisterVehicle;
// private _registered = [_vehicle] call _isVehicleRegistered;


// gameloop -- consider making separate functions and "spawn" -ing them in separate threads
while {true} do {

    // Find all vehicles within a certain radius of home_base
    private _vehiclesNearBase = home_base nearEntities ["AllVehicles", 1000]; // Adjust the radius as needed

    // Iterate through each vehicle and perform your desired command
    {
        // Your command here. Example:
        // hint format ["Vehicle %1 is near the base", _x];
		private _vehicle = _x;
		private _hasRegistrationAction = _x getVariable ["regActionID", nil];

		if (_x isKindOf "Helicopter" && isNil "_hasRegistrationAction") then {
			[_x] call _addRegistrationChoicesToVehicles;
		};

		// // Give players the ability to signal that they want to redeploy:
		private _vicIsRegistered = [_vehicle] call (missionNamespace getVariable "_isVehicleRegistered");
		private _requestingRedeploy = _vehicle getVariable ["requestingRedeploy", false];
		private _requestActionID = _vehicle getVariable ["requestActionID", nil];

		// remove current action to stay up to date
		if (!isNil "_requestActionID") then {
			_vehicle removeAction _requestActionID;
			_vehicle setVariable ["requestActionID", nil, true];
		};

		// only add actions if the vic is registered
		if (_vicIsRegistered) then {
			private _vehicleName = getText (configFile >> "CfgVehicles" >> (typeOf _vehicle) >> "displayName");
			if (_requestingRedeploy) then {
				// add ability to cancel redeployement request
				_requestActionID = _vehicle addAction [
					format ["<t color='#FFA200'>Cancel Redeploy Request %1</t>", _vehicleName], 
					{
						private _vehicle = _this select 0;
						_vehicle setVariable ["requestingRedeploy", false, true];
					},
					nil, 6, false, true, "", "true", 5, false, "", ""
				];
			} else {
				// add ability to request redeployement
				_requestActionID = _vehicle addAction [
					format ["<t color='#FFD500'>Request Redeploy %1</t>", _vehicleName], 
					{
						private _vehicle = _this select 0;
						_vehicle setVariable ["requestingRedeploy", true, true];
					},
					nil, 6, false, true, "", "true", 5, false, "", ""
				];
			};
			_vehicle setVariable ["requestActionID", _requestActionID, true];
		};

    } forEach _vehiclesNearBase;

	// register new pads, remove any pads that have been deleted
	private _padsNearBase = nearestObjects [home_base, home_base getVariable "landingPadClasses", 1000]; 
	home_base setVariable ["padsNearBase", _padsNearBase];
	private _padIdsNearBase = _padsNearBase apply { netId _x };
	private _padRegistry = home_base getVariable "padRegistry";
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

	// private _activeAwayPads = home_base getVariable "activeAwayPads";
	// systemChat format ["activeAwayPads: %1", _activeAwayPads];

	// Iterate through each player
    {
        // Check if the player has a radio in their inventory
		private _player = _x;
        private _hasRadio = "hgun_esd_01_F" in (items _player); 
		// hgun_esd_01_F is the spectrum device

		// Remove previous actions if any (clean-up)
		private _existingActions = _player getVariable ["deployVehicleActions", []];
		{
			_player removeAction _x;
		} forEach _existingActions;
		_player setVariable ["deployVehicleActions", [], true];  	
        
		if (_hasRadio) then {
			private _newActions = [];
			// Get the current list of registered vehicles
			private _currentRegisteredVehicles = home_base getVariable ["vicRegistry", []];

			// Add an action for each registered vehicle		
			{
				private _vehicle = _x;
				private _vehicleName = getText (configFile >> "CfgVehicles" >> (typeOf _vehicle) >> "displayName");
				private _reinserting = _vehicle getVariable ['isReinserting', false];
				private _waveOff = _vehicle getVariable ['waveOff', false];
				private _requestingRedeploy = _vehicle getVariable ['requestingRedeploy', false];
				private _extraText = "";

				if (!isTouchingGround _vehicle) then {
					_extraText = "(In Air)";
				};

				private _deployColor = "#FFFFFF";

				if (_requestingRedeploy) then {
					_deployColor = "#00FF00";
				};

				private _actionID = nil;
				if (_reinserting && !_waveOff) then {
					_actionID = _player addAction [
						format ["<t color='#FF0000'>Wave Off %1</t>", _vehicleName], 
						{
							params ["_target", "_caller", "_actionID", "_vehicle"];
							[_vehicle] execVM "redeployFunctions\waveOff.sqf";

						},
						_vehicle, 
						6, 
						false, 
						true, 
						"", 
						"true", 
						-1, 
						false, 
						"", 
						""
					];
				} else {
					_actionID = _player addAction [
						format ["<t color='%2'>%3 Deploy %1</t>", _vehicleName, _deployColor, _extraText], 
						{
							params ["_target", "_caller", "_actionID", "_args"];
							_args execVM "redeployFunctions\redeploy.sqf";

						},
						[_vehicle, _player], 
						6, 
						false, 
						true, 
						"", 
						"true", 
						-1, 
						false, 
						"", 
						""
					];
				};

				_newActions pushBack _actionID;
				
			} forEach _currentRegisteredVehicles;
		
			_player setVariable ["deployVehicleActions", _newActions, true];

		};


    } forEach allPlayers;

    sleep 3; 
};

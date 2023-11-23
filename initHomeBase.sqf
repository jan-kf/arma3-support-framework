#include "redeployFunctions\vicRegistration.sqf"

// Function to check if a vehicle is registered

missionNamespace setVariable ["_isVehicleRegistered", {
    params ["_vehicle"];
    private _registeredVehicles = home_base getVariable ["registeredVehicles", []];
    _vehicle in _registeredVehicles
}];

// Function to register a vehicle
missionNamespace setVariable ["_registerVehicle", {
    params ["_vehicle"];

    private _vicIsRegistered = [_vehicle] call (missionNamespace getVariable "_isVehicleRegistered");

    if (!_vicIsRegistered) then {
        // register the vic
        private _registeredVehicles = home_base getVariable ["registeredVehicles", []];
        _registeredVehicles pushBackUnique _vehicle;
        home_base setVariable ["registeredVehicles", _registeredVehicles, true];

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
        private _registeredVehicles = home_base getVariable ["registeredVehicles", []];
        _registeredVehicles deleteAt (_registeredVehicles find _vehicle);
        home_base setVariable ["registeredVehicles", _registeredVehicles, true];

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

        // save action id for later
        _vehicle setVariable ["regActionID", _regActionID, true];
    
    };
}];

// // Usage
// [_vehicle] call _registerVehicle;
// [_vehicle] call _unregisterVehicle;
// private _registered = [_vehicle] call _isVehicleRegistered;

while {true} do {

    // Find all vehicles within a certain radius of home_base
    private _vehiclesNearBase = home_base nearEntities ["AllVehicles", 1000]; // Adjust the radius as needed

    // Iterate through each vehicle and perform your desired command
    {
        // Your command here. Example:
        // hint format ["Vehicle %1 is near the base", _x];
		private _hasRegistrationAction = _x getVariable ["regActionID", nil];

		if (_x isKindOf "Helicopter" && isNil "_hasRegistrationAction") then {
			[_x] call _addRegistrationChoicesToVehicles;
		};

    } forEach _vehiclesNearBase;

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
			private _currentRegisteredVehicles = home_base getVariable ["registeredVehicles", []];

			// Add an action for each registered vehicle		
			{
				private _vehicle = _x;
				private _vehicleName = getText (configFile >> "CfgVehicles" >> (typeOf _vehicle) >> "displayName");
				private _reinserting = _vehicle getVariable ['isReinserting', false];
				private _actionID = nil;
				if (_reinserting) then {
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
						format ["<t color='#00FF00'>Deploy %1</t>", _vehicleName], 
						{
							params ["_target", "_caller", "_actionID", "_vehicle"];
							[_vehicle] execVM "redeployFunctions\redeploy.sqf";

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
				};

				_newActions pushBack _actionID;
				
			} forEach _currentRegisteredVehicles;
		
			_player setVariable ["deployVehicleActions", _newActions, true];

		};


    } forEach allPlayers;

    sleep 10; // Wait for 10 seconds before running the loop again
};

if (!isServer) exitWith {};

diag_log "[REDEPLOY] heartbeat starting ...";
["[REDEPLOY] heartbeat starting ..."] remoteExec ["systemChat"];

private _addRegistrationChoicesToVehicles = {
	params ["_vic"];

	private _vicIsRegistered = [_vic] call (missionNamespace getVariable "_isVehicleRegistered");
	private _vicStatus = [_vic] call (missionNamespace getVariable "getVehicleStatus");

	if (_vicIsRegistered) then {
		private _oldRegActionID =_vicStatus get "regActionID";
		if (!isNil "_oldRegActionID") then {
			_vic removeAction _oldRegActionID;
		};
		private _vehicleClass = typeOf _vic;
		private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
		private _regActionID = _vic addAction [
			format ["<t color='#FF8000'>Unregister %1</t>", _vehicleDisplayName], 
			{
				private _vehicle = _this select 0;
				[_vehicle] call (missionNamespace getVariable "_unregisterVehicle");
			},
			nil, 6, false, true, "", "true", 5, false, "", ""
		];
		_vicStatus set ["regActionID", _regActionID];
	} else {
		private _oldRegActionID = _vicStatus get "regActionID";
		if (!isNil "_oldRegActionID") then {
			_vic removeAction _oldRegActionID;
		};
		private _vehicleClass = typeOf _vic;
		private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
		private _regActionID = _vic addAction [
			format ["<t color='#00ABFF'>Register %1</t>", _vehicleDisplayName], 
			{
				private _vehicle = _this select 0;
				[_vehicle] call (missionNamespace getVariable "_registerVehicle");
			},
			nil, 6, false, true, "", "true", 5, false, "", ""
		];
		_vicStatus set ["regActionID", _regActionID];
	};
};

private _homeBaseManifest = missionNamespace getVariable "homeBaseManifest";

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

		private _vicStatus = [_vehicle] call (missionNamespace getVariable "getVehicleStatus");

		private _hasRegistrationAction = _vicStatus get "regActionID";

		if (_x isKindOf "Helicopter" && isNil "_hasRegistrationAction") then {
			[_x] call _addRegistrationChoicesToVehicles;
		};

		// // // Give players the ability to signal that they want to redeploy:
		// private _vicIsRegistered = [_vehicle] call (missionNamespace getVariable "_isVehicleRegistered");
		// private _requestingRedeploy = _vicStatus get "requestingRedeploy";
		// private _requestActionID = _vicStatus get "requestActionID";

		// // remove current action to stay up to date
		// if (!isNil "_requestActionID") then {
		// 	_vehicle removeAction _requestActionID;
		// 	_vicStatus set ["requestActionID", nil];
		// };

		// // only add actions if the vic is registered
		// if (_vicIsRegistered) then {
		// 	private _vehicleName = getText (configFile >> "CfgVehicles" >> (typeOf _vehicle) >> "displayName");
		// 	if (_requestingRedeploy) then {
		// 		// add ability to cancel redeployement request
		// 		_requestActionID = _vehicle addAction [
		// 			format ["<t color='#FFA200'>Cancel Redeploy Request %1</t>", _vehicleName], 
		// 			{
		// 				private _vehicle = _this select 0;
		// 				private _vicStatus = [_vehicle] call (missionNamespace getVariable "getVehicleStatus");
		// 				_vicStatus set ["requestingRedeploy", false];
		// 			},
		// 			nil, 6, false, true, "", "true", 5, false, "", ""
		// 		];
		// 	} else {
		// 		// add ability to request redeployement
		// 		_requestActionID = _vehicle addAction [
		// 			format ["<t color='#FFD500'>Request Redeploy %1</t>", _vehicleName], 
		// 			{
		// 				private _vehicle = _this select 0;
		// 				private _vicStatus = [_vehicle] call (missionNamespace getVariable "getVehicleStatus");
		// 				_vicStatus set ["requestingRedeploy", true];
		// 			},
		// 			nil, 6, false, true, "", "true", 5, false, "", ""
		// 		];
		// 	};
		// 	_vicStatus set ["requestActionID", _requestActionID];
		// };

	} forEach _vehiclesNearBase;

	// register new pads, remove any pads that have been deleted
	private _padsNearBase = nearestObjects [home_base, _homeBaseManifest get "landingPadClasses", 500]; 
	_homeBaseManifest set ["padsNearBase", _padsNearBase];
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
	
	// {
	// 	// Check if the player has a radio in their inventory
	// 	private _player = _x;
	// 	private _hasRadio = "hgun_esd_01_F" in (items _player); 
	// 	// hgun_esd_01_F is the spectrum device

	// 	// Remove previous actions if any (clean-up)
	// 	private _existingActions = _player getVariable ["deployVehicleActions", []];
	// 	{
	// 		_player removeAction _x;
	// 	} forEach _existingActions;
	// 	_player setVariable ["deployVehicleActions", []];  	
		
	// 	if (_hasRadio) then {
	// 		private _newActions = [];
	// 		// Get the current list of registered vehicles
	// 		private _currentRegisteredVehicles = _homeBaseManifest get "vicRegistry";

	// 		// Add an action for each registered vehicle		
	// 		{
	// 			private _vehicle = _x;
	// 			private _vicStatus = [_vehicle] call (missionNamespace getVariable "getVehicleStatus");
	// 			private _vehicleName = getText (configFile >> "CfgVehicles" >> (typeOf _vehicle) >> "displayName");
	// 			private _reinserting = _vicStatus get "isReinserting";
	// 			private _waveOff = _vicStatus get "waveOff";
	// 			private _requestingRedeploy = _vicStatus get "requestingRedeploy";
	// 			private _extraText = "";

	// 			if (!isTouchingGround _vehicle) then {
	// 				_extraText = "(In Air)";
	// 			};

	// 			private _deployColor = "#FFFFFF";

	// 			if (_requestingRedeploy) then {
	// 				_deployColor = "#00FF00";
	// 			};

	// 			private _actionID = nil;
	// 			if (_reinserting && !_waveOff) then {
	// 				_actionID = _player addAction [
	// 					format ["<t color='#FF0000'>Wave Off %1</t>", _vehicleName], 
	// 					{
	// 						params ["_target", "_caller", "_actionID", "_args"];
	// 						private _vicStatus = [_args select 0] call (missionNamespace getVariable "getVehicleStatus");
	// 						_vicStatus set ["targetGroupLeader", _args select 1];
	// 						_vicStatus set ["currentTask", "waveOff"];

	// 						// [driver (_args select 0), format["debug stat: %1", _vicStatus]] remoteExec ["sideChat"];
	// 					},
	// 					[_vehicle, _player],
	// 					6, 
	// 					false, 
	// 					true, 
	// 					"", 
	// 					"true", 
	// 					-1, 
	// 					false, 
	// 					"", 
	// 					""
	// 				];
	// 			} else {
	// 				_actionID = _player addAction [
	// 					format ["<t color='%2'>%3 Deploy %1</t>", _vehicleName, _deployColor, _extraText], 
	// 					{
	// 						params ["_target", "_caller", "_actionID", "_args"];
	// 						private _vicStatus = [_args select 0] call (missionNamespace getVariable "getVehicleStatus");
	// 						_vicStatus set ["targetGroupLeader", _args select 1];
	// 						_vicStatus set ["currentTask", "begin"];
	// 					},
	// 					[_vehicle, _player], 
	// 					6, 
	// 					false, 
	// 					true, 
	// 					"", 
	// 					"true", 
	// 					-1, 
	// 					false, 
	// 					"", 
	// 					""
	// 				];
	// 			};

	// 			_newActions pushBack _actionID;
				
	// 		} forEach _currentRegisteredVehicles;
		
	// 		_player setVariable ["deployVehicleActions", _newActions];

	// 	};
	// } forEach allPlayers;
    sleep 3; 
};
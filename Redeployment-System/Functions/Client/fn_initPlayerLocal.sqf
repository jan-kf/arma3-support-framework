// TODO: maybe add support for landing pads that already exist in the map.
private _getBuiltInPads = {
	// Define the landing pad classes
	private _landingPadClasses = [
		"Land_HelipadEmpty_F", 
		"Land_HelipadCircle_F", 
		"Land_HelipadCivil_F", 
		"Land_HelipadRescue_F", 
		"Land_HelipadSquare_F", 
		"Land_JumpTarget_F",
		// CUP pads:
		"HeliH",
		"HeliHCivil",
		"Heli_H_civil",
		"HeliHEmpty",
		"HeliHRescue",
		"Heli_H_rescue",
		"PARACHUTE_TARGET"
	];

	// Define the location types
	private _locationTypes = [
		"Airport", "CityCenter", "CivilDefense", "CulturalProperty",
		"DangerousForces", "FlatArea", "FlatAreaCity", "FlatAreaCitySmall",
		"Name", "NameCity", "NameCityCapital", "NameLocal", "NameMarine",
		"NameVillage", "SafetyZone", "Strategic", "StrongpointArea"
	];

	// Get the position of home_base
	private _homeBasePos = getPos (missionNamespace getVariable ["home_base", objNull]);

	// Find all landing pads on the map
	private _allLandingPads = [];
	{
		_allLandingPads append (allMissionObjects _x);
	} forEach _landingPadClasses;

	// Filter landing pads and check for nearby locations
	private _validLandingPads = [];
	{
		private _landingPadPos = getPos _x;
		if (_landingPadPos distance _homeBasePos > 500) then {
			private _nearbyLocations = nearestLocations [_landingPadPos, _locationTypes, 50];
			if (count _nearbyLocations > 0) then {
				private _nearestLocation = _nearbyLocations select 0;
				private _locationName = text _nearestLocation;
				if (_locationName != "") then {
					_validLandingPads pushBack _x;
				};
			};
		};
	} forEach _allLandingPads;

	// Return the array of valid landing pads
	_validLandingPads

};


private _insertVehicles = {
    params ["_target", "_caller", "_params"];
	
	private _actions = [];
	private _registeredVehicles = call (missionNamespace getVariable "getRegisteredVehicles");
	{
		private _vehicle = _x;
		private _vehicleClass = typeOf _vehicle;
		private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
		private _color = "#FFFFFF";
		private _requested = _vehicle getVariable ["requestingRedeploy", false];
		private _reinserting = _vehicle getVariable ["isReinserting", false];
		private _task = _vehicle getVariable ["currentTask", "waiting"];
		if (_reinserting) then {
			_color = "#30ADE3";
		};
		if (_requested) then {
			_color = "#5EC445";
		};
		if (_task == "awaitOrders") then {
			_color = "#f7e76a";
		};
		private _vicAction = [
			netId _vehicle, format["<t color='%3'>(%1) %2</t>",groupId group _vehicle, _vehicleDisplayName, _color], "",
			{
				params ["_target", "_caller", "_vic"];
				//statement
				private _task = _vic getVariable ["currentTask", "waiting"];
				if (_task == "waiting") then {
					private _allInVehicle = (crew _vic) - (units _vic); // Get all units in the vehicle and remove the crew members

					// Getting names of non-crew members
					private _names = [];
					{
						_names pushBack (name _x);
					} forEach _allInVehicle;

					// Format the names into a string
					private _namesString = format ["Waiting for redeploy in %2: %1", _names joinString ", ", groupId group _vic];

					// Display the names using a hint
					hint _namesString;
				} else {
					// Display the vic's current task
					hint format ["%1's current task: %2", groupId group _vic, _task];
				};
			}, 
			{
				params ["_target", "_caller", "_vic"];
				// Condition code here
				private _registered = _vic getVariable ["isRegistered", false];
				_registered
			},
			{ // 5: Insert children code <CODE> (Optional)
				params ["_target", "_caller", "_params"];
				
				private _actions = [];
				
				private _vehicle = _target;
				private _vehicleClass = typeOf _vehicle;
				private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
				private _color = "#FFFFFF";
				private _vicDeployAction = [
					format["%1-deploy", netId _vehicle], format["<t color='%1'>Deploy! (Auto dust-off after 10 sec)</t>", _color], "",
					{
						// statement 
						params ["_target", "_caller", "_vic"];
						_vic setVariable ["targetGroupLeader", _caller, true];
						_vic setVariable ["currentTask", "begin", true];
						_vic setVariable ["fullRun", true, true];
					}, 
					{
						params ["_target", "_caller", "_vic"];
						// // Condition code here
						private _notReinserting = !(_vic getVariable ["isReinserting", false]);
						private _task = _vic getVariable ["currentTask", "waiting"];
						private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "begin", "awaitOrders"]);
						_notReinserting && _notOnRestrictedTask
					},
					{}, // 5: Insert children code <CODE> (Optional)
					_vehicle // 6: Action parameters <ANY> (Optional)
				] call ace_interact_menu_fnc_createAction;
				_actions pushBack [_vicDeployAction, [], _target];
				private _vicWaveOffAction = [
					format["%1-waveOff", netId _vehicle], "<t color='#F23838'>Wave Off!</t>", "",
					{
						// statement 
						params ["_target", "_caller", "_vic"];
						_vic setVariable ["targetGroupLeader", _caller, true];
						_vic setVariable ["currentTask", "waveOff", true];
					}, 
					{
						params ["_target", "_caller", "_vic"];
						// // Condition code here
						private _isReinserting = _vic getVariable ["isReinserting", false];
						private _task = _vic getVariable ["currentTask", "waiting"];
						private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "begin", "awaitOrders"]);
						_isReinserting && _notOnRestrictedTask
					},
					{}, // 5: Insert children code <CODE> (Optional)
					_vehicle // 6: Action parameters <ANY> (Optional)
				] call ace_interact_menu_fnc_createAction;
				_actions pushBack [_vicWaveOffAction, [], _target]; 
				private _vicRequestAction = [
					format["%1-request", netId _vehicle], format["<t color='%1'>Call in (Land and wait for orders)</t>", _color], "",
					{
						// statement 
						params ["_target", "_caller", "_vic"];
						_vic setVariable ["targetGroupLeader", _caller, true];
						_vic setVariable ["currentTask", "begin", true];
						_vic setVariable ["fullRun", false, true];
					}, 
					{
						params ["_target", "_caller", "_vic"];
						// // Condition code here
						private _notReinserting = !(_vic getVariable ["isReinserting", false]);
						private _task = _vic getVariable ["currentTask", "waiting"];
						private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "begin", "awaitOrders"]);
						_notReinserting && _notOnRestrictedTask
					},
					{}, // 5: Insert children code <CODE> (Optional)
					_vehicle // 6: Action parameters <ANY> (Optional)
				] call ace_interact_menu_fnc_createAction;
				_actions pushBack [_vicRequestAction, [], _target];
				private _vicRTBAction = [
					format["%1-rtb", netId _vehicle], format["<t color='%1'>RTB</t>", _color], "",
					{
						// statement 
						params ["_target", "_caller", "_vic"];
						_vic setVariable ["targetGroupLeader", _caller, true];
						_vic setVariable ["currentTask", "requestBaseLZ", true];
						private _groupLeaderGroup = group _caller;
						private _groupLeaderCallsign = groupId _groupLeaderGroup;
						[_caller, format ["%1, this is %2, RTB.",groupId group _vic, _groupLeaderCallsign]] remoteExec ["sideChat"];
					}, 
					{
						params ["_target", "_caller", "_vic"];
						// // Condition code here
						private _notReinserting = !(_vic getVariable ["isReinserting", false]);
						private _task = _vic getVariable ["currentTask", "waiting"];
						private _awaitingOrders = _task == "awaitOrders";
						_awaitingOrders
					},
					{}, // 5: Insert children code <CODE> (Optional)
					_vehicle // 6: Action parameters <ANY> (Optional)
				] call ace_interact_menu_fnc_createAction;

				{ // add all HLS and LZ markers as valid locations
					private _marker = _x;
					private _markerName = markerText _marker;
					private _displayName = toLower _markerName;
					if ((_displayName find "hls " == 0) || (_displayName find "lz " == 0)) then {
						private _vicRequestToLZAction = [
							format["%1-requestTo-%2", netId _vehicle, _marker], format["<t color='%1'>Send to %2</t>", _color, _markerName], "",
							{
								// statement 
								params ["_target", "_caller", "_args"];
								private _vic = _args select 0;
								private _marker = _args select 1;
								_vic setVariable ["targetGroupLeader", _caller, true];
								_vic setVariable ["targetLocation", _marker, true];
								_vic setVariable ["currentTask", "begin", true];
								_vic setVariable ["fullRun", false, true];
							}, 
							{
								params ["_target", "_caller", "_args"];
								private _vic = _args select 0;
								private _marker = _args select 1;
								// // Condition code here
								private _notReinserting = !(_vic getVariable ["isReinserting", false]);
								private _task = _vic getVariable ["currentTask", "waiting"];
								private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "begin"]);
								private _notAtLZ = (_vic distance2D getMarkerPos _marker) > 100;
								_notReinserting && _notOnRestrictedTask && _notAtLZ
							},
							{}, // 5: Insert children code <CODE> (Optional)
							[_vehicle, _marker] // 6: Action parameters <ANY> (Optional)
						] call ace_interact_menu_fnc_createAction;
						_actions pushBack [_vicRequestToLZAction, [], _target];
					};
				} forEach allMapMarkers;

				

				_actions pushBack [_vicRTBAction, [], _target];
					

				_actions
			},
			_vehicle, // 6: Action parameters <ANY> (Optional)
			"", // 7: Position (Position array, Position code or Selection Name) <ARRAY>, <CODE> or <STRING> (Optional)
			4, // 8: Distance <NUMBER>
			[false, false, false, true, false] // 9: Other parameters [showDisabled,enableInside,canCollapse,runOnHover,doNotCheckLOS] <ARRAY> (Optional)
		] call ace_interact_menu_fnc_createAction;
		_actions pushBack [_vicAction, [], _vehicle]; 
		
	} forEach _registeredVehicles;

    _actions
};

private _redeploymentActions = [
	"RedeploymentActions", "Redeployment", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		('hgun_esd_01_F' in (items _caller))
	},
	_insertVehicles
] call ace_interact_menu_fnc_createAction;

[player, 1, ["ACE_SelfActions"], _redeploymentActions] call ace_interact_menu_fnc_addActionToObject;

// Define the action


private _insertVicActions = {
	params ["_target", "_caller", "_params"];
	private _registerVicAction = [
		"RegisterVehicle", "<t color='#2daaf7'>Register Vehicle</t>", "",
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Statement code here
			// hint "Action executed!";
			_target setVariable ["isRegistered", true, true];
		}, 
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Condition code here
			private _atBase = (_target distance2D (missionNamespace getVariable "home_base")) < 500;
			private _not_registered = !(_target getVariable ["isRegistered", false]);
			// show if:
			_atBase && _not_registered
		}
	] call ace_interact_menu_fnc_createAction;

	private _unregisterVicAction = [
		"UnregisterVehicle", "<t color='#f7812d'>Unregister Vehicle</t>", "",
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Statement code here
			// hint "Action executed!";
			_target setVariable ["isRegistered", false, true];
		}, 
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Condition code here
			private _atBase = (_target distance2D (missionNamespace getVariable "home_base")) < 500;
			private _registered = _target getVariable ["isRegistered", false];
			// show if:
			_atBase && _registered
		}
	] call ace_interact_menu_fnc_createAction;

	private _requestVicAction = [
		"RequestRedeploy", "<t color='#5EC445'>Request Redeploy</t>", "",
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Statement code here
			// hint "Action executed!";
			_target setVariable ["requestingRedeploy", true, true];
		}, 
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Condition code here
			private _atBase = (_target distance2D (missionNamespace getVariable "home_base")) < 500;
			private _registered = _target getVariable ["isRegistered", false];
			private _notRequested = !(_target getVariable ["requestingRedeploy", false]);
			// show if:
			_atBase && _registered && _notRequested
		}
	] call ace_interact_menu_fnc_createAction;

	private _cancelVicAction = [
		"CancelRedeploy", "<t color='#fae441'>Cancel Redeploy Request</t>", "",
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Statement code here
			// hint "Action executed!";
			_target setVariable ["requestingRedeploy", false, true];
		}, 
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Condition code here
			private _atBase = (_target distance2D (missionNamespace getVariable "home_base")) < 500;
			private _registered = _target getVariable ["isRegistered", false];
			private _requested = _target getVariable ["requestingRedeploy", false];
			// show if:
			_atBase && _registered && _requested
		}
	] call ace_interact_menu_fnc_createAction;
	private _actions = [];
	_actions pushBack [_registerVicAction, [], _target];
	_actions pushBack [_unregisterVicAction, [], _target];
	_actions pushBack [_requestVicAction, [], _target];
	_actions pushBack [_cancelVicAction, [], _target];


	_actions
};

private _heliActions = [
	"HelicopterActions", "Redeployment", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		true
	},
	_insertVicActions
] call ace_interact_menu_fnc_createAction;

// Add the actions to the Helicopter class
["Helicopter", 0, ["ACE_MainActions"], _heliActions, true] call ace_interact_menu_fnc_addActionToClass;

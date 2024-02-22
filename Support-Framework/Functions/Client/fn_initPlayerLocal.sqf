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
		if (_landingPadPos distance _homeBasePos > ((missionNamespace getVariable "home_base") getVariable ["Radius", 500])) then {
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
		private _reinserting = _vehicle getVariable ["isPerformingDuties", false];
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
						_vic setVariable ["currentTask", "requestReinsert", true];
						_vic setVariable ["fullRun", true, true];
					}, 
					{
						params ["_target", "_caller", "_vic"];
						// // Condition code here
						private _notReinserting = !(_vic getVariable ["isPerformingDuties", false]);
						private _task = _vic getVariable ["currentTask", "waiting"];
						private _isCAS = _target getVariable ["isCAS", false];
						private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "requestReinsert", "awaitOrders"]);
						_notReinserting && _notOnRestrictedTask && !_isCAS
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
						private _isPerformingDuties = _vic getVariable ["isPerformingDuties", false];
						private _task = _vic getVariable ["currentTask", "waiting"];
						private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "requestReinsert", "awaitOrders"]);
						_isPerformingDuties && _notOnRestrictedTask
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
						_vic setVariable ["currentTask", "requestReinsert", true];
						_vic setVariable ["fullRun", false, true];
					}, 
					{
						params ["_target", "_caller", "_vic"];
						// // Condition code here
						private _notReinserting = !(_vic getVariable ["isPerformingDuties", false]);
						private _task = _vic getVariable ["currentTask", "waiting"];
						private _isCAS = _target getVariable ["isCAS", false];
						private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "requestReinsert", "awaitOrders"]);
						_notReinserting && _notOnRestrictedTask && !_isCAS
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
						private _notReinserting = !(_vic getVariable ["isPerformingDuties", false]);
						private _task = _vic getVariable ["currentTask", "waiting"];
						private _awaitingOrders = _task == "awaitOrders";
						_awaitingOrders
					},
					{}, // 5: Insert children code <CODE> (Optional)
					_vehicle // 6: Action parameters <ANY> (Optional)
				] call ace_interact_menu_fnc_createAction;

				{ // add all HLS and LZ markers as valid locations
					
					// marker details
					private _marker = _x;
					private _markerName = markerText _marker;
					private _displayName = toLower _markerName;

					// LZ search details
					private _lzPrefixStr = (missionNamespace getVariable "home_base") getVariable ["LzPrefixes", ""];
					private _lzPrefixes = [];
					if (_lzPrefixStr != "") then {
						_lzPrefixes = _lzPrefixStr splitString ", ";
					} else {
						_lzPrefixes = ["lz ", "hls "]; // default value -- hard fallback
					};

					private _lzMatch = false;
					{
						private _prefix = toLower _x;
						if (_displayName find _prefix == 0) exitWith {
							_lzMatch = true;
						}
					} forEach _lzPrefixes;

					if (_lzMatch) then {
						private _vicRequestToLZAction = [
							format["%1-requestTo-%2", netId _vehicle, _marker], format["<t color='%1'>Send to %2</t>", _color, _markerName], "",
							{
								// statement 
								params ["_target", "_caller", "_args"];
								private _vic = _args select 0;
								private _marker = _args select 1;
								_vic setVariable ["targetGroupLeader", _caller, true];
								_vic setVariable ["targetLocation", _marker, true];
								_vic setVariable ["currentTask", "requestReinsert", true];
								_vic setVariable ["fullRun", false, true];
							}, 
							{
								params ["_target", "_caller", "_args"];
								private _vic = _args select 0;
								private _marker = _args select 1;
								// // Condition code here
								private _notReinserting = !(_vic getVariable ["isPerformingDuties", false]);
								private _task = _vic getVariable ["currentTask", "waiting"];
								private _isCAS = _target getVariable ["isCAS", false];
								private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "requestReinsert"]);
								private _notAtLZ = (_vic distance2D getMarkerPos _marker) > 100;
								_notReinserting && _notOnRestrictedTask && _notAtLZ && !_isCAS
							},
							{}, // 5: Insert children code <CODE> (Optional)
							[_vehicle, _marker] // 6: Action parameters <ANY> (Optional)
						] call ace_interact_menu_fnc_createAction;
						_actions pushBack [_vicRequestToLZAction, [], _target];
					};

					// CAS search details
					private _casPrefixStr = (missionNamespace getVariable "home_base") getVariable ["CasPrefixes", ""];
					private _casPrefixes = [];
					if (_casPrefixStr != "") then {
						_casPrefixes = _casPrefixStr splitString ", ";
					} else {
						_casPrefixes = ["target ", "firemission "]; // default value -- hard fallback
					};

					private _casMatch = false;
					{
						private _prefix = toLower _x;
						if (_displayName find _prefix == 0) exitWith {
							_casMatch = true;
						}
					} forEach _casPrefixes;

					if (_casMatch) then {
						private _vicRequestToLZAction = [
							format["%1-casTo-%2", netId _vehicle, _marker], format["<t color='%1'>Request Firemission at %2</t>", _color, _markerName], "",
							{
								// statement 
								params ["_target", "_caller", "_args"];
								private _vic = _args select 0;
								private _marker = _args select 1;
								_vic setVariable ["targetGroupLeader", _caller, true];
								_vic setVariable ["targetLocation", _marker, true];
								_vic setVariable ["currentTask", "requestCas", true];
								_vic setVariable ["fullRun", false, true];
							}, 
							{
								params ["_target", "_caller", "_args"];
								private _vic = _args select 0;
								private _marker = _args select 1;
								// // Condition code here
								private _isCAS = _target getVariable ["isCAS", false];
								private _notReinserting = !(_vic getVariable ["isPerformingDuties", false]);
								private _task = _vic getVariable ["currentTask", "waiting"];
								private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "requestReinsert"]);
								private _notAtLZ = (_vic distance2D getMarkerPos _marker) > 100;
								_isCAS && _notReinserting && _notOnRestrictedTask && _notAtLZ
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
		// Retrieve the custom argument value
		private _requiredItemsStr = (missionNamespace getVariable "home_base") getVariable ["RequiredItems", ""];
		private _requiredItems = [];
		if (_requiredItemsStr != "") then {
			_requiredItems = _requiredItemsStr splitString ", ";
		} else {
			_requiredItems = ["hgun_esd_01_F"]; // default value -- hard fallback
		};
		private _hasItem = false;
		{
			// Check general inventory
			if (_x in (items _caller)) exitWith {
				_hasItem = true;
			};

			// Check assigned items (like night vision, binoculars, GPS, and radio)
			if (_x in (assignedItems _caller)) exitWith {
				_hasItem = true;
			};

			// Check uniform, vest, and backpack items
			if (_x in (uniformItems _caller) || _x in (vestItems _caller) || _x in (backpackItems _caller)) exitWith {
				_hasItem = true;
			};
		} forEach _requiredItems;
		_hasItem
	},
	_insertVehicles
] call ace_interact_menu_fnc_createAction;

[player, 1, ["ACE_SelfActions"], _redeploymentActions] call ace_interact_menu_fnc_addActionToObject;


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
			private _atBase = (_target distance2D (missionNamespace getVariable "home_base")) < ((missionNamespace getVariable "home_base") getVariable ["Radius", 500]);
			private _not_registered = !(_target getVariable ["isRegistered", false]);
			// show if:
			_atBase && _not_registered
		}
	] call ace_interact_menu_fnc_createAction;

	private _unregisterVicAction = [
		"UnregisterVehicle", "<t color='#ffda36'>Unregister Vehicle</t>", "",
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Statement code here
			// hint "Action executed!";
			_target setVariable ["isRegistered", false, true];
		}, 
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Condition code here
			private _atBase = (_target distance2D (missionNamespace getVariable "home_base")) < ((missionNamespace getVariable "home_base") getVariable ["Radius", 500]);
			private _registered = _target getVariable ["isRegistered", false];
			// show if:
			_atBase && _registered
		}
	] call ace_interact_menu_fnc_createAction;

	private _assignCasVicAction = [
		"AssignCasVehicle", "<t color='#f7812d'>Assign to CAS</t>", "",
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Statement code here
			_target setVariable ["isCAS", true, true];
			[_target, format ["%1 is ready for tasking... ",groupId group _target]] remoteExec ["sideChat"];
		}, 
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Condition code here
			private _atBase = (_target distance2D (missionNamespace getVariable "home_base")) < ((missionNamespace getVariable "home_base") getVariable ["Radius", 500]);
			private _registered = _target getVariable ["isRegistered", false];
			private _isCAS = _target getVariable ["isCAS", false];
			
			_nonCombatKeywords = ["safe", "designator", "horn"];  // these are works that appear in some cases but should be disregarded as weapons
			_allWeapons = weapons _target; 
			_combatWeapons = _allWeapons select { 
				_isCombatWeapon = true;
				_weaponNameLower = toLower _x; 
				{  
					if (toLower _x in _weaponNameLower) then {
						_isCombatWeapon = false;
					}; 
				} forEach _nonCombatKeywords; 
				_isCombatWeapon; 
			}; // if count of the combat weapons is more than 0, then in theory the vic has weapons that can be used for CAS

			// show if:
			_atBase && _registered && !_isCAS && (count _combatWeapons > 0)
		}
	] call ace_interact_menu_fnc_createAction;

	private _unassignCasVicAction = [
		"UnassignCasVehicle", "<t color='#f2a974'>Remove from CAS</t>", "",
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Statement code here
			_target setVariable ["isCAS", false, true];
		}, 
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Condition code here
			private _atBase = (_target distance2D (missionNamespace getVariable "home_base")) < ((missionNamespace getVariable "home_base") getVariable ["Radius", 500]);
			private _registered = _target getVariable ["isRegistered", false];
			private _isCAS = _target getVariable ["isCAS", false];

			// show if:
			_atBase && _registered && _isCAS
		}
	] call ace_interact_menu_fnc_createAction;

	private _requestVicRedeployAction = [
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
			private _atBase = (_target distance2D (missionNamespace getVariable "home_base")) < ((missionNamespace getVariable "home_base") getVariable ["Radius", 500]);
			private _registered = _target getVariable ["isRegistered", false];
			private _notRequested = !(_target getVariable ["requestingRedeploy", false]);
			private _isCAS = _target getVariable ["isCAS", false];
			// show if:
			_atBase && _registered && _notRequested && !_isCAS
		}
	] call ace_interact_menu_fnc_createAction;

	private _cancelVicRedeployAction = [
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
			private _atBase = (_target distance2D (missionNamespace getVariable "home_base")) < ((missionNamespace getVariable "home_base") getVariable ["Radius", 500]);
			private _registered = _target getVariable ["isRegistered", false];
			private _requested = _target getVariable ["requestingRedeploy", false];
			private _isCAS = _target getVariable ["isCAS", false];
			// show if:
			_atBase && _registered && _requested && !_isCAS
		}
	] call ace_interact_menu_fnc_createAction;
	private _actions = [];
	_actions pushBack [_registerVicAction, [], _target];
	_actions pushBack [_unregisterVicAction, [], _target];
	_actions pushBack [_assignCasVicAction, [], _target];
	_actions pushBack [_unassignCasVicAction, [], _target];
	_actions pushBack [_requestVicRedeployAction, [], _target];
	_actions pushBack [_cancelVicRedeployAction, [], _target];


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
		private _atBase = (_target distance2D (missionNamespace getVariable "home_base")) < ((missionNamespace getVariable "home_base") getVariable ["Radius", 500]);
		_atBase
	},
	_insertVicActions
] call ace_interact_menu_fnc_createAction;

// Add the actions to the Helicopter class
["Helicopter", 0, ["ACE_MainActions"], _heliActions, true] call ace_interact_menu_fnc_addActionToClass;

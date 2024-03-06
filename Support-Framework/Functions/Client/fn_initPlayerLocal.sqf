// TODO: maybe add support for landing pads that already exist in the map.
// private _getBuiltInPads = {
// 	// Define the landing pad classes
// 	private _landingPadClasses = [
// 		"Land_HelipadEmpty_F", 
// 		"Land_HelipadCircle_F", 
// 		"Land_HelipadCivil_F", 
// 		"Land_HelipadRescue_F", 
// 		"Land_HelipadSquare_F", 
// 		"Land_JumpTarget_F",
// 		// CUP pads:
// 		"HeliH",
// 		"HeliHCivil",
// 		"Heli_H_civil",
// 		"HeliHEmpty",
// 		"HeliHRescue",
// 		"Heli_H_rescue",
// 		"PARACHUTE_TARGET"
// 	];

// 	// Define the location types
// 	private _locationTypes = [
// 		"Airport", "CityCenter", "CivilDefense", "CulturalProperty",
// 		"DangerousForces", "FlatArea", "FlatAreaCity", "FlatAreaCitySmall",
// 		"Name", "NameCity", "NameCityCapital", "NameLocal", "NameMarine",
// 		"NameVillage", "SafetyZone", "Strategic", "StrongpointArea"
// 	];

// 	// Get the position of YOSHI_HOME_BASE_CONFIG
// 	private _homeBasePos = getPos (missionNamespace getVariable ["YOSHI_HOME_BASE_CONFIG", objNull]);

// 	// Find all landing pads on the map
// 	private _allLandingPads = [];
// 	{
// 		_allLandingPads append (allMissionObjects _x);
// 	} forEach _landingPadClasses;

// 	// Filter landing pads and check for nearby locations
// 	private _validLandingPads = [];
// 	{
// 		private _landingPadPos = getPos _x;
// 		if (_landingPadPos call (missionNamespace getVariable "isAtBase")) then {
// 			private _nearbyLocations = nearestLocations [_landingPadPos, _locationTypes, 50];
// 			if (count _nearbyLocations > 0) then {
// 				private _nearestLocation = _nearbyLocations select 0;
// 				private _locationName = text _nearestLocation;
// 				if (_locationName != "") then {
// 					_validLandingPads pushBack _x;
// 				};
// 			};
// 		};
// 	} forEach _allLandingPads;

// 	// Return the array of valid landing pads
// 	_validLandingPads

// };


private _artyVehicles = {
    params ["_target", "_caller", "_params"];
	
	private _targetActions = [];
	
	// Artillery search details
	private _artyPrefixStr = (missionNamespace getVariable "YOSHI_SUPPORT_ARTILLERY_CONFIG") getVariable ["ArtilleryPrefixes", ""];
	private _artyPrefixes = [];
	if (_artyPrefixStr != "") then {
		_artyPrefixes = _artyPrefixStr splitString ", ";
	} else {
		_artyPrefixes = ["target ", "firemission "]; // default value -- hard fallback
	};

	{ // for each map marker
		
		// marker details
		private _marker = _x;
		private _markerName = markerText _marker;
		private _displayName = toLower _markerName;
		
		{ // for each artillery prefix
			private _prefix = toLower _x;
			if (_displayName find _prefix == 0) then {
				// if prefix matches

				private _targetAction = [
					format["%1-targetMarker", _markerName], format["%1", _markerName], "",
					{
						params ["_targetMarker", "_caller", "_args"];
						//statement
						true
					}, 
					{
						params ["_targetMarker", "_caller", "_args"];
						// Condition code here
						true
					},
					{ // 5: Insert children code <CODE> (Optional)
						params ["_targetMarker", "_caller", "_args"];
						private _vehicleActions = [];
						
						private _registeredVehicles = call (missionNamespace getVariable "getRegisteredVehicles");

						{ // for each registered vehicle
							private _vehicle = _x;
							if (_vehicle getVariable ["isArtillery", false]) then {
								// if it's registered as artillery

								private _vehicleClass = typeOf _vehicle;
								private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
								private _color = "#FFFFFF";


								private _vehicleAction = [
									format["vicActionArty-%1", netId _vehicle], format["(%1) %2",groupId group _vehicle, _vehicleDisplayName], "",
									{
										params ["_targetMarker", "_caller", "_vehicle"];
										//statement
										true
									}, 
									{
										params ["_targetMarker", "_caller", "_vehicle"];
										// Condition code here
										true
									},
									{ // 5: Insert children code <CODE> (Optional)
										params ["_targetMarker", "_caller", "_vehicle"];
										private _shellActions = [];

										{ // for every ammo type in this vehicle

											private _shellType = _x;
											private _targetPos = getMarkerPos _targetMarker;

											if (_targetPos inRangeOfArtillery [[_vehicle], _shellType]) then {
												// if that ammo type is capable of hitting the target
												private _shellDisplayName = getText (configFile >> "CfgMagazines" >> _shellType >> "displayName");
												private _shellAction = [
													format["vicActionArty-%1-%2", netId _vehicle, _shellType], format["%1", _shellDisplayName], "",
													{
														params ["_targetMarker", "_caller", "_args"];
														//statement
														true
													}, 
													{
														params ["_targetMarker", "_caller", "_args"];
														// Condition code here
														true
													},
													{ // 5: Insert children code <CODE> (Optional)
														params ["_targetMarker", "_caller", "_args"];
														private _vehicle = _args select 0;
														private _shellType = _args select 1;
														
														private _amountActions = [];
														{
															// add actions for each amount
															private _amount = _x;
															private _amountAction = [
																format["vicActionArty-%1-%2-%3-round(s)", netId _vehicle, _shellType, _amount], format["%1 Round(s)", _amount], "",
																{
																	params ["_targetMarker", "_caller", "_args"];
																	//statement
																	private _vehicle = _args select 0;
																	private _shellType = _args select 1;
																	private _amount = _args select 2;

																	private _shellDisplayName = getText (configFile >> "CfgMagazines" >> _shellType >> "displayName");
																	private _shellDescription = _shellDisplayName;
																	if (_shellDisplayName find "Shell" == -1) then {
																		_shellDescription = format["%1 Munitions", _shellDisplayName];
																	};

																	private _targetPos = getMarkerPos _targetMarker;

																	private _posToGrid = {
																		params ["_pos"];
																		private _gridX = floor ((_pos select 0) / 10); // 10m precision for X
																		private _gridY = floor ((_pos select 1) / 10); // 10m precision for Y

																		private _formattedX = if (_gridX < 10) then {format ["000%1", _gridX]} 
																							else {if (_gridX < 100) then {format ["00%1", _gridX]} 
																							else {if (_gridX < 1000) then {format ["0%1", _gridX]}
																							else {format ["%1", _gridX]}}};

																		private _formattedY = if (_gridY < 10) then {format ["000%1", _gridY]} 
																							else {if (_gridY < 100) then {format ["00%1", _gridY]} 
																							else {if (_gridY < 1000) then {format ["0%1", _gridY]}
																							else {format ["%1", _gridY]}}};

																		format ["%1-%2", _formattedX, _formattedY];
																	};

																	private _gridRef = [_targetPos] call _posToGrid;
																	private _ETA = _vehicle getArtilleryETA [_targetPos, _shellType];

																	private _groupLeaderGroup = group _caller;
																	private _groupLeaderCallsign = groupId _groupLeaderGroup;
																	[_caller, format ["%1, this is %2, Requesting immediate firesupport at %3. %4 times %5. Over.", groupId group _vehicle, _groupLeaderCallsign, _gridRef, _amount, _shellDescription]] call (missionNamespace getVariable "sideChatter");
																	private _response = format ["Affirmative %1, %2 times %3 at %4. ETA: %5 seconds, Out.", _groupLeaderCallsign, _amount, _shellDescription, _gridRef, _ETA];
																	
																	if ((missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["Hush", false]) then {
																		hint _response;
																	} else {
																		[_vehicle, _response] spawn  {
																			params ["_vehicle", "_response"];
																			
																			sleep 3;

																			[_vehicle, _response] call (missionNamespace getVariable "sideChatter");
																		};
																	};
																	

																	_vehicle doArtilleryFire [_targetPos, _shellType, _amount];
																	// BOOM

																}, 
																{
																	params ["_targetMarker", "_caller", "_args"];
																	// Condition code here
																	true
																},
																{ // 5: Insert children code <CODE> (Optional)
																},
																[_vehicle, _shellType, _amount] // 6 Params
															] call ace_interact_menu_fnc_createAction;
															_amountActions pushBack [_amountAction, [], _targetMarker];

														} forEach [1,2,4,8];

														_amountActions
													},
													[_vehicle, _shellType], // 6 Params
													"", // 7: Position (Position array, Position code or Selection Name) <ARRAY>, <CODE> or <STRING> (Optional)
													4, // 8: Distance <NUMBER>
													[false, false, false, true, false] // 9: Other parameters [showDisabled,enableInside,canCollapse,runOnHover,doNotCheckLOS] <ARRAY> (Optional)
												] call ace_interact_menu_fnc_createAction;
												_shellActions pushBack [_shellAction, [], _targetMarker];
												
											};

										} forEach (getArtilleryAmmo [_vehicle]);

										_shellActions
									},
									_vehicle, // 6 Params
									"", // 7: Position (Position array, Position code or Selection Name) <ARRAY>, <CODE> or <STRING> (Optional)
									4, // 8: Distance <NUMBER>
									[false, false, true, true, false] // 9: Other parameters [showDisabled,enableInside,canCollapse,runOnHover,doNotCheckLOS] <ARRAY> (Optional)
								] call ace_interact_menu_fnc_createAction;
								_vehicleActions pushBack [_vehicleAction, [], _targetMarker];

							};
						} forEach _registeredVehicles;						
							
						_vehicleActions
					},
					_marker, // 6: Action parameters <ANY> (Optional)
					"", // 7: Position (Position array, Position code or Selection Name) <ARRAY>, <CODE> or <STRING> (Optional)
					4, // 8: Distance <NUMBER>
					[false, false, true, true, false] // 9: Other parameters [showDisabled,enableInside,canCollapse,runOnHover,doNotCheckLOS] <ARRAY> (Optional)
				] call ace_interact_menu_fnc_createAction;
				_targetActions pushBack [_targetAction, [], _marker]; 
	
			};
		} forEach _artyPrefixes;

	} forEach allMapMarkers;
	
    _targetActions
};

private _casVehicles = {
    params ["_target", "_caller", "_params"];
	
	private _actions = [];
	private _registeredVehicles = call (missionNamespace getVariable "getRegisteredVehicles");
	{
		private _vehicle = _x;
		if (!(_vehicle getVariable ["isArtillery", false]) && _vehicle getVariable ["isCAS", false]) then {
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
						
						private _casPrefixStr = (missionNamespace getVariable "YOSHI_SUPPORT_CAS_CONFIG") getVariable ["CasPrefixes", ""];
						private _casPrefixes = [];
						if (_casPrefixStr != "") then {
							_casPrefixes = _casPrefixStr splitString ", ";
						} else {
							_casPrefixes = ["target ", "firemission "]; // default value -- hard fallback
						};

						hint format["%1 is awaiting orders, searching for markers prefixed with %2...", groupId group _vic, _casPrefixes];

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
					
					private _vicWaveOffAction = [
						format["%1-waveOff", netId _vehicle], "<t color='#F23838'>Wave Off!</t>", "",
						{
							// statement 
							params ["_target", "_caller", "_vic"];
							_vic setVariable ["targetGroupLeader", _caller, true];
							_vic setVariable ["currentTask", "waveOff", true];
							if ((missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["Hush", false]) then {
								hint "Waving off CAS...";
							}
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
					
					private _vicRTBAction = [
						format["%1-rtb", netId _vehicle], format["<t color='%1'>RTB</t>", _color], "",
						{
							// statement 
							params ["_target", "_caller", "_vic"];
							_vic setVariable ["targetGroupLeader", _caller, true];
							_vic setVariable ["currentTask", "requestBaseLZ", true];
							private _groupLeaderGroup = group _caller;
							private _groupLeaderCallsign = groupId _groupLeaderGroup;
							[_caller, format ["%1, this is %2, RTB.",groupId group _vic, _groupLeaderCallsign]] call (missionNamespace getVariable "sideChatter");
							if ((missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["Hush", false]) then {
								hint "CAS returning to base...";
							}
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

					// CAS search details
					private _casPrefixStr = (missionNamespace getVariable "YOSHI_SUPPORT_CAS_CONFIG") getVariable ["CasPrefixes", ""];
					private _casPrefixes = [];
					if (_casPrefixStr != "") then {
						_casPrefixes = _casPrefixStr splitString ", ";
					} else {
						_casPrefixes = ["target ", "firemission "]; // default value -- hard fallback
					};

					{ // add all valid markers as valid locations
						
						// marker details
						private _marker = _x;
						private _markerName = markerText _marker;
						private _displayName = toLower _markerName;
						
						{
							private _prefix = toLower _x;
							if (_displayName find _prefix == 0) then {
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
										if ((missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["Hush", false]) then {
											hint "Calling in CAS...";
										}
									}, 
									{
										params ["_target", "_caller", "_args"];
										private _vic = _args select 0;
										private _marker = _args select 1;
										// // Condition code here
										private _casConfig = missionNamespace getVariable ["YOSHI_SUPPORT_CAS_CONFIG", nil];
										private _CasConfigured = !(isNil "_casConfig");
										private _isCAS = _target getVariable ["isCAS", false];
										private _notReinserting = !(_vic getVariable ["isPerformingDuties", false]);
										private _task = _vic getVariable ["currentTask", "waiting"];
										private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "requestReinsert"]);
										private _notAtLZ = (_vic distance2D getMarkerPos _marker) > 100;
										_CasConfigured && _isCAS && _notReinserting && _notOnRestrictedTask && _notAtLZ
									},
									{}, // 5: Insert children code <CODE> (Optional)
									[_vehicle, _marker] // 6: Action parameters <ANY> (Optional)
								] call ace_interact_menu_fnc_createAction;
								_actions pushBack [_vicRequestToLZAction, [], _target];
							};
						} forEach _casPrefixes;

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
		};
	} forEach _registeredVehicles;

    _actions
};

private _insertVehicles = {
    params ["_target", "_caller", "_params"];
	
	private _actions = [];
	private _registeredVehicles = call (missionNamespace getVariable "getRegisteredVehicles");
	{
		private _vehicle = _x;
		if (!(_vehicle getVariable ["isArtillery", false]) && !(_vehicle getVariable ["isCAS", false])) then {
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

						private _lzPrefixStr = (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["LzPrefixes", ""];
						private _lzPrefixes = [];
						if (_lzPrefixStr != "") then {
							_lzPrefixes = _lzPrefixStr splitString ", ";
						} else {
							_lzPrefixes = ["lz ", "hls "]; // default value -- hard fallback
						};

						// Format the names into a string
						private _namesString = format ["Waiting for redeploy in %2: %1, searching for markers prefixed with %3...", _names joinString ", ", groupId group _vic, _lzPrefixes];

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
					// private _vicDeployAction = [
					// 	format["%1-deploy", netId _vehicle], format["<t color='%1'>Deploy! (Auto dust-off after 10 sec)</t>", _color], "",
					// 	{
					// 		// statement 
					// 		params ["_target", "_caller", "_vic"];
					// 		_vic setVariable ["targetGroupLeader", _caller, true];
					// 		_vic setVariable ["currentTask", "requestReinsert", true];
					// 		_vic setVariable ["fullRun", true, true];
					// 	}, 
					// 	{
					// 		params ["_target", "_caller", "_vic"];
					// 		// // Condition code here
					// 		private _notReinserting = !(_vic getVariable ["isPerformingDuties", false]);
					// 		private _task = _vic getVariable ["currentTask", "waiting"];
					// 		private _isCAS = _target getVariable ["isCAS", false];
					// 		private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "requestReinsert", "awaitOrders"]);
					// 		_notReinserting && _notOnRestrictedTask && !_isCAS
					// 	},
					// 	{}, // 5: Insert children code <CODE> (Optional)
					// 	_vehicle // 6: Action parameters <ANY> (Optional)
					// ] call ace_interact_menu_fnc_createAction;
					// _actions pushBack [_vicDeployAction, [], _target];
					private _vicWaveOffAction = [
						format["%1-waveOff", netId _vehicle], "<t color='#F23838'>Wave Off!</t>", "",
						{
							// statement 
							params ["_target", "_caller", "_vic"];
							_vic setVariable ["targetGroupLeader", _caller, true];
							_vic setVariable ["currentTask", "waveOff", true];
							if ((missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["Hush", false]) then {
								hint "Waving off transport...";
							}
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
					// private _vicRequestAction = [
					// 	format["%1-request", netId _vehicle], format["<t color='%1'>Call in (Land and wait for orders)</t>", _color], "",
					// 	{
					// 		// statement 
					// 		params ["_target", "_caller", "_vic"];
					// 		_vic setVariable ["targetGroupLeader", _caller, true];
					// 		_vic setVariable ["currentTask", "requestReinsert", true];
					// 		_vic setVariable ["fullRun", false, true];
					// 	}, 
					// 	{
					// 		params ["_target", "_caller", "_vic"];
					// 		// // Condition code here
					// 		private _notReinserting = !(_vic getVariable ["isPerformingDuties", false]);
					// 		private _task = _vic getVariable ["currentTask", "waiting"];
					// 		private _isCAS = _target getVariable ["isCAS", false];
					// 		private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "requestReinsert", "awaitOrders"]);
					// 		_notReinserting && _notOnRestrictedTask && !_isCAS
					// 	},
					// 	{}, // 5: Insert children code <CODE> (Optional)
					// 	_vehicle // 6: Action parameters <ANY> (Optional)
					// ] call ace_interact_menu_fnc_createAction;
					// _actions pushBack [_vicRequestAction, [], _target];
					private _vicRTBAction = [
						format["%1-rtb", netId _vehicle], format["<t color='%1'>RTB</t>", _color], "",
						{
							// statement 
							params ["_target", "_caller", "_vic"];
							_vic setVariable ["targetGroupLeader", _caller, true];
							_vic setVariable ["currentTask", "requestBaseLZ", true];
							private _groupLeaderGroup = group _caller;
							private _groupLeaderCallsign = groupId _groupLeaderGroup;
							[_caller, format ["%1, this is %2, RTB.",groupId group _vic, _groupLeaderCallsign]] call (missionNamespace getVariable "sideChatter");
							if ((missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["Hush", false]) then {
								hint "Transport returning to base...";
							}
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

					
					// LZ search details
					private _lzPrefixStr = (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["LzPrefixes", ""];
					private _lzPrefixes = [];
					if (_lzPrefixStr != "") then {
						_lzPrefixes = _lzPrefixStr splitString ", ";
					} else {
						_lzPrefixes = ["lz ", "hls "]; // default value -- hard fallback
					};
					
					{ // add all valid markers as valid locations
						
						// marker details
						private _marker = _x;
						private _markerName = markerText _marker;
						private _displayName = toLower _markerName;

						

						{
							private _prefix = toLower _x;
							if (_displayName find _prefix == 0) then {
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
										if ((missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["Hush", false]) then {
											hint "Requesting transport...";
										}
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
						} forEach _lzPrefixes;

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
		};
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
		private _homeBase = missionNamespace getVariable ["YOSHI_HOME_BASE_CONFIG", nil];
		private _homeBaseConfigured = !(isNil "_homeBase");

		if (_homeBaseConfigured) then {
			private _requiredItemsStr = (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["RequiredItems", ""];
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
		} else {
			false
		};
	},
	_insertVehicles
] call ace_interact_menu_fnc_createAction;

private _casActions = [
	"CasActions", "CAS Support", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		// Retrieve the custom argument value
		private _casConfig = missionNamespace getVariable ["YOSHI_SUPPORT_CAS_CONFIG", nil];
		private _CasConfigured = !(isNil "_casConfig");

		if (_CasConfigured) then {
			private _requiredItemsStr = (missionNamespace getVariable "YOSHI_SUPPORT_CAS_CONFIG") getVariable ["RequiredItems", ""];
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
		} else {
			false
		};
	},
	_casVehicles
] call ace_interact_menu_fnc_createAction;

private _artilleryActions = [
	"ArtilleryActions", "Artillery", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		private _artyPrefixStr = (missionNamespace getVariable "YOSHI_SUPPORT_ARTILLERY_CONFIG") getVariable ["ArtilleryPrefixes", ""];
		private _artyPrefixes = [];
		if (_artyPrefixStr != "") then {
			_artyPrefixes = _artyPrefixStr splitString ", ";
		} else {
			_artyPrefixes = ["target ", "firemission "]; // default value -- hard fallback
		};

		hint format["Awaiting orders, searching for markers prefixed with %1...", _artyPrefixes];

		true
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		// Retrieve the custom argument value
		private _artyConfig = missionNamespace getVariable ["YOSHI_SUPPORT_ARTILLERY_CONFIG", nil];
		private _artyConfigured = !(isNil "_artyConfig");

		if (_artyConfigured) then {

			private _requiredItemsStr = (missionNamespace getVariable "YOSHI_SUPPORT_ARTILLERY_CONFIG") getVariable ["RequiredItems", ""];
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

		} else {
			false
		};
	},
	_artyVehicles,
	"", // 7: Position (Position array, Position code or Selection Name) <ARRAY>, <CODE> or <STRING> (Optional)
	4, // 8: Distance <NUMBER>
	[false, false, false, true, false] // 9: Other parameters [showDisabled,enableInside,canCollapse,runOnHover,doNotCheckLOS] <ARRAY> (Optional)
] call ace_interact_menu_fnc_createAction;

[player, 1, ["ACE_SelfActions"], _redeploymentActions] call ace_interact_menu_fnc_addActionToObject;
[player, 1, ["ACE_SelfActions"], _casActions] call ace_interact_menu_fnc_addActionToObject;
[player, 1, ["ACE_SelfActions"], _artilleryActions] call ace_interact_menu_fnc_addActionToObject;


private _vicActions = {
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
			private _atBase = _target call (missionNamespace getVariable "isAtBase");
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
			private _atBase = _target call (missionNamespace getVariable "isAtBase");
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
			[_target, format ["%1 is ready for tasking... ",groupId group _target]] call (missionNamespace getVariable "sideChatter");
		}, 
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Condition code here
			private _casConfig = missionNamespace getVariable ["YOSHI_SUPPORT_CAS_CONFIG", nil];
			private _CasConfigured = !(isNil "_casConfig");
			private _atBase = _target call (missionNamespace getVariable "isAtBase");
			private _registered = _target getVariable ["isRegistered", false];
			private _isCAS = _target getVariable ["isCAS", false];
			private _isArty = _target getVariable ["isArtillery", false];
			
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
			private _canDoArtilleryFire = _target getVariable ["isArtillery", false];
			// show if:
			_CasConfigured && !_canDoArtilleryFire && _atBase && _registered && !_isCAS && (count _combatWeapons > 0) && !_isArty
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
			private _casConfig = missionNamespace getVariable ["YOSHI_SUPPORT_CAS_CONFIG", nil];
			private _CasConfigured = !(isNil "_casConfig");
			private _atBase = _target call (missionNamespace getVariable "isAtBase");
			private _registered = _target getVariable ["isRegistered", false];
			private _isCAS = _target getVariable ["isCAS", false];

			private _canDoArtilleryFire = _target getVariable ["isArtillery", false];
			// show if:
			_CasConfigured && !_canDoArtilleryFire && _atBase && _registered && _isCAS
		}
	] call ace_interact_menu_fnc_createAction;

	private _assignArtyVicAction = [
		"AssignArtyVehicle", "<t color='#f7812d'>Assign to Artillery</t>", "",
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Statement code here
			_target setVariable ["isArtillery", true, true];
			[_target, format ["%1 is ready for tasking... ",groupId group _target]] call (missionNamespace getVariable "sideChatter");
		}, 
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Condition code here
			private _artilleryConfig = missionNamespace getVariable ["YOSHI_SUPPORT_ARTILLERY_CONFIG", nil];
			private _artilleryConfigured = !(isNil "_artilleryConfig");
			
			private _registered = _target getVariable ["isRegistered", false];
			
			private _canDoArtilleryFire = _target getVariable ["isArtillery", false];

			// show if:
			_artilleryConfigured && _canDoArtilleryFire && _registered
		}
	] call ace_interact_menu_fnc_createAction;

	private _unassignArtyVicAction = [
		"UnassignArtyVehicle", "<t color='#f2a974'>Remove from Artillery</t>", "",
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Statement code here
			_target setVariable ["isArtillery", false, true];
		}, 
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Condition code here
			private _artilleryConfig = missionNamespace getVariable ["YOSHI_SUPPORT_ARTILLERY_CONFIG", nil];
			private _artilleryConfigured = !(isNil "_artilleryConfig");
			
			private _registered = _target getVariable ["isRegistered", false];
			
			private _canDoArtilleryFire = _target getVariable ["isArtillery", false];

			// show if:
			_artilleryConfigured && !_canDoArtilleryFire && _registered
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
			private _atBase = _target call (missionNamespace getVariable "isAtBase");
			private _registered = _target getVariable ["isRegistered", false];
			private _notRequested = !(_target getVariable ["requestingRedeploy", false]);
			private _isCAS = _target getVariable ["isCAS", false];
			private _isArty = _target getVariable ["isArtillery", false];
			
			// show if:
			_atBase && _registered && _notRequested && !_isCAS && !_isArty
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
			private _atBase = _target call (missionNamespace getVariable "isAtBase");
			private _registered = _target getVariable ["isRegistered", false];
			private _requested = _target getVariable ["requestingRedeploy", false];
			private _isCAS = _target getVariable ["isCAS", false];
			private _isArty = _target getVariable ["isArtillery", false];
			
			// show if:
			_atBase && _registered && _requested && !_isCAS && !_isArty
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
	"HelicopterActions", "Support Actions", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		private _homeBase = missionNamespace getVariable ["YOSHI_HOME_BASE_CONFIG", nil];
		private _homeBaseConfigured = !(isNil "_homeBase");
		if (_homeBaseConfigured) then {
			private _atBase = _target call (missionNamespace getVariable "isAtBase");
			_atBase
		} else {
			false
		};
	},
	_vicActions
] call ace_interact_menu_fnc_createAction;

// Add the actions to the Helicopter class
["Helicopter", 0, ["ACE_MainActions"], _heliActions, true] call ace_interact_menu_fnc_addActionToClass;


private _artilleryVicActions = [
	"ArtilleryVicActions", "Support Actions", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		private _homeBase = missionNamespace getVariable ["YOSHI_HOME_BASE_CONFIG", nil];
		private _homeBaseConfigured = !(isNil "_homeBase");

		private _artilleryConfig = missionNamespace getVariable ["YOSHI_SUPPORT_ARTILLERY_CONFIG", nil];
		private _artilleryConfigured = !(isNil "_artilleryConfig");

		if (_homeBaseConfigured && _artilleryConfigured) then {
			private _canDoArtilleryFire = _target getVariable ["isArtillery", false];
			_canDoArtilleryFire
		} else {
			false
		};

	},
	_vicActions
] call ace_interact_menu_fnc_createAction;

// Add the actions to the classes that might have arty support
["LandVehicle", 0, ["ACE_MainActions"], _artilleryVicActions, true] call ace_interact_menu_fnc_addActionToClass;
["Ship", 0, ["ACE_MainActions"], _artilleryVicActions, true] call ace_interact_menu_fnc_addActionToClass;

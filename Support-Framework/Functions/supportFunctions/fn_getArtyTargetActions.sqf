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
					
					private _registeredVehicles = call SupportFramework_fnc_getRegisteredVehicles;

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

																private _gridRef = [_targetPos] call SupportFramework_fnc_posToGrid;
																private _ETA = _vehicle getArtilleryETA [_targetPos, _shellType];

																private _groupLeaderGroup = group _caller;
																private _groupLeaderCallsign = groupId _groupLeaderGroup;
																[_caller, format ["%1, this is %2, Requesting immediate firesupport at %3. %4 times %5. Over.", groupId group _vehicle, _groupLeaderCallsign, _gridRef, _amount, _shellDescription]] call SupportFramework_fnc_sideChatter;
																private _response = format ["Affirmative %1, %2 times %3 at %4. ETA: %5 seconds, Out.", _groupLeaderCallsign, _amount, _shellDescription, _gridRef, _ETA];
																
																if ((missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["Hush", false]) then {
																	hint _response;
																} else {
																	[_vehicle, _response] spawn  {
																		params ["_vehicle", "_response"];
																		
																		sleep 3;

																		[_vehicle, _response] call SupportFramework_fnc_sideChatter;
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
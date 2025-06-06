params ["_targetPos", "_targetName", ["_targetObject", objNull], ["_forArtillery", false]];

private _targetActions = [];

private _targetAction = [
	format["%1-targetLocation", _targetName], format["%1", _targetName], "\a3\ui_f\data\igui\cfg\simpletasks\types\move_ca.paa",
	{
		params ["_target", "_caller", "_targetPos"];
		true
	}, 
	{
		params ["_target", "_caller", "_targetPos"];
		true
	},
	{
		params ["_target", "_caller", "_args"];
		private _vehicleActions = [];
		private _registeredVehicles = call YOSHI_fnc_getRegisteredVehicles;
		private _targetPos = _args select 0;
		private _targetObject = _args select 1;
		private _forArtillery = _args select 2;
		

		if (_forArtillery) then {
			{
				private _vehicle = _x;
				if (_vehicle getVariable ["isArtillery", false]) then {
					private _vehicleClass = typeOf _vehicle;
					private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");

					private _vehicleAction = [
						format["vicActionArty-%1", netId _vehicle], format["(%1) %2", groupId group _vehicle, _vehicleDisplayName], "",
						{
							params ["_targetArgs", "_caller", "_vehicle"];
							true
						},
						{
							params ["_targetArgs", "_caller", "_vehicle"];
							alive _vehicle
						},
						{
							params ["_targetArgs", "_caller", "_vehicle"];
							private _shellActions = [];

							private _targetPos = _targetArgs select 0;
							private _targetObject = _targetArgs select 1;

							private _artyAmmo = getArtilleryAmmo [_vehicle];
							if ((typeOf _vehicle) isEqualTo "B_Ship_MRLS_01_F" && (_targetObject isNotEqualTo objNull)) then{
								private _shellAction = [
									format["vicActionArty-%1", netId _vehicle],"Cruise Missile", "",
									{
										params ["_targetObject", "_caller", "_vehicle"];

										west reportRemoteTarget [_targetObject, 3600];
										_targetObject confirmSensorTarget [west, true];

										private _gridRef = [getPosASL _targetObject] call YOSHI_fnc_posToGrid;

										private _groupLeaderGroup = group _caller;
										private _groupLeaderCallsign = groupId _groupLeaderGroup;
										[_caller, format ["%1, this is %2, Requesting immediate firesupport at %3. Over.", groupId group _vehicle, _groupLeaderCallsign, _gridRef]] call YOSHI_fnc_sendSideText;
										private _response = format ["Affirmative %1, Deploying Cruise Missile to %2, Out.", _groupLeaderCallsign, _gridRef];
										
										if (YOSHI_HOME_BASE_CONFIG_OBJECT get "SideHush") then {
											hint _response;
										} else {
											[_vehicle, _response] spawn  {
												params ["_vehicle", "_response"];
												
												sleep 3;

												[_vehicle, _response] call YOSHI_fnc_sendSideText;
												[_vehicle, "YOSHI_ArtilleryAck"] call YOSHI_fnc_playSideRadio;

												waitUntil {sleep 5; unitReady _vehicle};

												[_vehicle, "YOSHI_ArtilleryRoundsComplete"] call YOSHI_fnc_playSideRadio;
												
											};
										};
										

										_vehicle fireAtTarget [_targetObject, "weapon_vls_01"];
									},
									{
										params ["_targetObject", "_caller", "_vehicle"];
										// Condition code here
										true
									},
									{//5
									},
									_vehicle // 6 Params
								] call ace_interact_menu_fnc_createAction;
								_shellActions pushBack [_shellAction, [], _targetObject];
							} else {
								{ // for every ammo type in this vehicle
									private _shellType = _x;

									if (_targetPos inRangeOfArtillery [[_vehicle], _shellType]) then {
										private _shellAction = [
											format["vicActionArty-%1-%2", netId _vehicle, _shellType], getText (configFile >> "CfgMagazines" >> _shellType >> "displayName"), "",
											{
												params ["_targetPos", "_caller", "_args"];
												// Fire artillery here
											},
											{
												params ["_targetPos", "_caller", "_args"];
												true
											},
											{ // 5: Insert children code <CODE> (Optional)
												params ["_targetPos", "_caller", "_args"];
												private _vehicle = _args select 0;
												private _shellType = _args select 1;
												
												private _amountActions = [];
												{
													// add actions for each amount
													private _amount = _x;
													private _amountAction = [
														format["vicActionArty-%1-%2-%3-round(s)", netId _vehicle, _shellType, _amount], format["%1 Round(s)", _amount], "",
														{
															params ["_targetPos", "_caller", "_args"];
															//statement
															private _vehicle = _args select 0;
															private _shellType = _args select 1;
															private _amount = _args select 2;

															private _shellDisplayName = getText (configFile >> "CfgMagazines" >> _shellType >> "displayName");
															private _shellDescription = _shellDisplayName;
															if (_shellDisplayName find "Shell" == -1) then {
																_shellDescription = format["%1 Munitions", _shellDisplayName];
															};

															private _gridRef = [_targetPos] call YOSHI_fnc_posToGrid;
															private _ETA = _vehicle getArtilleryETA [_targetPos, _shellType];

															private _groupLeaderGroup = group _caller;
															private _groupLeaderCallsign = groupId _groupLeaderGroup;
															[_caller, format ["%1, this is %2, Requesting immediate firesupport at %3. %4 times %5. Over.", groupId group _vehicle, _groupLeaderCallsign, _gridRef, _amount, _shellDescription]] call YOSHI_fnc_sendSideText;
															private _response = format ["Affirmative %1, %2 times %3 at %4. ETA: %5 seconds, Out.", _groupLeaderCallsign, _amount, _shellDescription, _gridRef, _ETA];
															
															if (YOSHI_HOME_BASE_CONFIG_OBJECT get "SideHush") then {
																hint _response;
															} else {
																[_vehicle, _response] spawn  {
																	params ["_vehicle", "_response"];
																	
																	sleep 3;

																	[_vehicle, _response] call YOSHI_fnc_sendSideText;
																	[_vehicle, "YOSHI_ArtilleryAck"] call YOSHI_fnc_playSideRadio;

																	waitUntil {sleep 5; unitReady _vehicle};

																	[_vehicle, "YOSHI_ArtilleryRoundsComplete"] call YOSHI_fnc_playSideRadio;
																	
																};
															};
															

															[_vehicle, [_targetPos, _shellType, _amount]] remoteExec ["doArtilleryFire", 2];
															// BOOM

														}, 
														{
															params ["_targetPos", "_caller", "_args"];
															// Condition code here
															true
														},
														{ // 5: Insert children code <CODE> (Optional)
														},
														[_vehicle, _shellType, _amount] // 6 Params
													] call ace_interact_menu_fnc_createAction;
													_amountActions pushBack [_amountAction, [], _targetPos];

												} forEach [1,2,4,8];

												_amountActions
											},
											[_vehicle, _shellType] // 6 Params
										] call ace_interact_menu_fnc_createAction;
										_shellActions pushBack [_shellAction, [], _targetPos];
									};
								} forEach (_artyAmmo);
							};


							_shellActions
						},
						_vehicle,
						"",
						4,
						[false, false, true, true, false]
					] call ace_interact_menu_fnc_createAction;
					_vehicleActions pushBack [_vehicleAction, [], [_targetPos, _targetObject]];
				};
			} forEach _registeredVehicles;
		} else {
			if ((_targetObject isNotEqualTo objNull) &&([YOSHI_FW_CONFIG_OBJECT] call YOSHI_isInitialized)) then {
				private _deployedWings = YOSHI_FW_CONFIG_OBJECT get "DeployedUnits";
				private _fixedWingActions = [];
				{
					private _ordinanceLoadout = _x call YOSHI_GET_LGM;
					private _vehicle = _x;
					{
						if (_x != "") then {
							private _ordinance = _x;
							private _vehicleClass = typeOf _vehicle;
							private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
							private _ordinanceType = if (_forEachIndex isEqualTo 0) then {"Bomb"} else {"Missile"};
							private _fixedWingAction = [
								format["vicActionDropBomb-%1", netId _vehicle], format["Release %2 from %1", _vehicleDisplayName, _ordinanceType], "",
								{
									params ["_targetObject", "_caller", "_args"];
									//statement
									private _vehicle = _args select 0;
									private _ordinance = _args select 1;

									_vehicle fireAtTarget [_targetObject, _ordinance];
									hint "Package away";
									// BOOM

								}, 
								{
									params ["_targetObject", "_caller", "_args"];
									// Condition code here
									!((_args select 0) getVariable ["YOSHI_REPORTED_BINGO_FUEL", false])
								},
								{ // 5: Insert children code <CODE> (Optional)
								},
								[_vehicle, _ordinance, _targetObject] // 6 Params
							] call ace_interact_menu_fnc_createAction;
							_fixedWingActions pushBack [_fixedWingAction, [], _targetObject];
						};
					} forEach _ordinanceLoadout;

				} forEach _deployedWings;
				_vehicleActions = _vehicleActions + _fixedWingActions;
			};
		};




		_vehicleActions
	},
	[_targetPos, _targetObject, _forArtillery], // 6 Params
	"",
	4,
	[false, false, true, true, false]
] call ace_interact_menu_fnc_createAction;

_targetActions pushBack [_targetAction, [], _targetName];
_targetActions

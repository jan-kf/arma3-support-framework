params ["_targetPos", "_targetName"];

private _targetActions = [];

private _targetAction = [
	format["%1-targetLocation", _targetName], format["%1", _targetName], "",
	{
		params ["_target", "_caller", "_targetPos"];
		true
	}, 
	{
		params ["_target", "_caller", "_targetPos"];
		true
	},
	{
		params ["_target", "_caller", "_targetPos"];
		private _vehicleActions = [];
		private _registeredVehicles = call YOSHI_fnc_getRegisteredVehicles;

		{
			private _vehicle = _x;
			if (_vehicle getVariable ["isArtillery", false]) then {
				private _vehicleClass = typeOf _vehicle;
				private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");

				private _vehicleAction = [
					format["vicActionArty-%1", netId _vehicle], format["(%1) %2", groupId group _vehicle, _vehicleDisplayName], "",
					{
						params ["_targetPos", "_caller", "_vehicle"];
						true
					},
					{
						params ["_targetPos", "_caller", "_vehicle"];
						alive _vehicle
					},
					{
						params ["_targetPos", "_caller", "_vehicle"];
						private _shellActions = [];

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
													
													if (YOSHI_HOME_BASE_CONFIG getVariable ["SideHush", false]) then {
														hint _response;
													} else {
														[_vehicle, _response] spawn  {
															params ["_vehicle", "_response"];
															
															sleep 3;

															[_vehicle, _response] call YOSHI_fnc_sendSideText;
															[_vehicle, "YOSHI_ArtilleryAck"] call YOSHI_fnc_playSideRadio;
															
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
						} forEach (getArtilleryAmmo [_vehicle]);

						_shellActions
					},
					_vehicle,
					"",
					4,
					[false, false, true, true, false]
				] call ace_interact_menu_fnc_createAction;
				_vehicleActions pushBack [_vehicleAction, [], _targetPos];
			};
		} forEach _registeredVehicles;

		_vehicleActions
	},
	_targetPos,
	"",
	4,
	[false, false, true, true, false]
] call ace_interact_menu_fnc_createAction;

_targetActions pushBack [_targetAction, [], _targetName];
_targetActions

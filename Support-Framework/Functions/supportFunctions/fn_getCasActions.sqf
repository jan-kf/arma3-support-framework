params ["_target", "_caller", "_params"];
	
private _actions = [];
private _registeredVehicles = call YOSHI_fnc_getRegisteredVehicles;
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
		if (_task == "awaitOrders" || _task == "loiter") then {
			_color = "#f7e76a";
		};
		private _vicAction = [
			netId _vehicle, format["<t color='%3'>(%1) %2</t>",groupId group _vehicle, _vehicleDisplayName, _color], "",
			{
				params ["_target", "_caller", "_vic"];
				//statement
				private _task = _vic getVariable ["currentTask", "waiting"];
				if (_task == "waiting") then {
					
					private _casPrefixStr = YOSHI_SUPPORT_CAS_CONFIG getVariable ["CasPrefixes", ""];
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
					format["%1-waveOff", netId _vehicle], "<t color='#F23838'>Wave Off!</t>", "\A3\ui_f\data\map\markers\military\pickup_CA.paa",
					{
						// statement 
						params ["_target", "_caller", "_vic"];
						_vic setVariable ["targetGroupLeader", _caller, true];
						if (YOSHI_HOME_BASE_CONFIG getVariable ["SideHush", false]) then {
							hint "Waving off CAS...";
						};
						[_vic] remoteExec ["YOSHI_fnc_waveOff", 2];
					}, 
					{
						params ["_target", "_caller", "_vic"];
						// // Condition code here
						private _isPerformingDuties = _vic getVariable ["isPerformingDuties", false];
						private _task = _vic getVariable ["currentTask", "waiting"];
						private _isLoitering = _task == "loiter";
						private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "requestReinsert", "awaitOrders"]);
						(_isPerformingDuties || _isLoitering) && _notOnRestrictedTask
					},
					{}, // 5: Insert children code <CODE> (Optional)
					_vehicle // 6: Action parameters <ANY> (Optional)
				] call ace_interact_menu_fnc_createAction;
				_actions pushBack [_vicWaveOffAction, [], _target]; 
				
				private _vicRTBAction = [
					format["%1-rtb", netId _vehicle], format["<t color='%1'>RTB</t>", _color], "\A3\ui_f\data\map\markers\military\start_CA.paa",
					{
						// statement 
						params ["_target", "_caller", "_vic"];
						_vic setVariable ["targetGroupLeader", _caller, true];
						_vic setVariable ["currentTask", "requestBaseLZ", true];
						private _groupLeaderGroup = group _caller;
						private _groupLeaderCallsign = groupId _groupLeaderGroup;
						[_caller, format ["%1, this is %2, RTB.",groupId group _vic, _groupLeaderCallsign]] call YOSHI_fnc_sendSideText;
						if (YOSHI_HOME_BASE_CONFIG getVariable ["SideHush", false]) then {
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
				private _casPrefixStr = YOSHI_SUPPORT_CAS_CONFIG getVariable ["CasPrefixes", ""];
				private _casPrefixes = [];
				if (_casPrefixStr != "") then {
					_casPrefixes = _casPrefixStr splitString ", ";
				} else {
					_casPrefixes = ["target ", "firemission "]; // default value -- hard fallback
				};

				private _loiterActions = [_vehicle, _target] call YOSHI_fnc_getLoiterActions;

				_actions = _actions + _loiterActions;

				{ // add all valid markers as valid locations
					
					// marker details
					private _marker = _x;
					private _markerName = markerText _marker;
					private _displayName = toLower _markerName;
					
					{
						private _prefix = toLower _x;
						if (_displayName find _prefix == 0) then {
							private _vicRequestToLZAction = [
								format["%1-casTo-%2", netId _vehicle, _marker], format["<t color='%1'>Request Firemission at %2</t>", _color, _markerName], "\a3\ui_f\data\igui\cfg\simpletasks\types\move_ca.paa",
								{
									// statement 
									params ["_target", "_caller", "_args"];
									private _vic = _args select 0;
									private _marker = _args select 1;
									_vic setVariable ["targetGroupLeader", _caller, true];
									_vic setVariable ["currentTask", "requestCas", true];
									_vic setVariable ["fullRun", false, true];
									if (YOSHI_HOME_BASE_CONFIG getVariable ["SideHush", false]) then {
										hint "Calling in CAS...";
									};
									[_vic, getMarkerPos _marker] remoteExec ["YOSHI_fnc_requestCas", 2];
								}, 
								{
									params ["_target", "_caller", "_args"];
									private _vic = _args select 0;
									private _marker = _args select 1;
									// // Condition code here
									private _CasConfigured = !(isNil "YOSHI_SUPPORT_CAS_CONFIG");
									private _isCAS = _target getVariable ["isCAS", false];
									private _notReinserting = !(_vic getVariable ["isPerformingDuties", false]);
									private _task = _vic getVariable ["currentTask", "waiting"];
									private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "requestReinsert"]);
									private _notAtLZ = (_vic distance2D getMarkerPos _marker) > 100;
									_CasConfigured && alive _vic && _isCAS && _notReinserting && _notOnRestrictedTask && _notAtLZ
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
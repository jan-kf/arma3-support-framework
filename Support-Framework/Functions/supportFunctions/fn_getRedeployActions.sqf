params ["_target", "_caller", "_params"];
	
private _actions = [];
private _registeredVehicles = call SupportFramework_fnc_getRegisteredVehicles;
{
	private _vehicle = _x;
	if (!(_vehicle getVariable ["isArtillery", false]) && !(_vehicle getVariable ["isCAS", false]) && !(_vehicle getVariable ["isRecon", false])) then {
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
				_registered && alive _vic
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
						if ((missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["Hush", false]) then {
							hint "Waving off transport...";
						};
						[_vic] remoteExec ["SupportFramework_fnc_waveOff", 2];
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
						[_caller, format ["%1, this is %2, RTB.",groupId group _vic, _groupLeaderCallsign]] call SupportFramework_fnc_sideChatter;
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
									_vic setVariable ["currentTask", "requestReinsert", true];
									_vic setVariable ["fullRun", false, true];
									if ((missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["Hush", false]) then {
										hint "Requesting transport...";
									};
									[_vic, getMarkerPos _marker] remoteExec ["SupportFramework_fnc_requestReinsert", 2];
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

				private _loiterActions = [_vehicle, _target] call SupportFramework_fnc_getLoiterActions;

				_actions pushBack [_vicRTBAction, [], _target];
					
				_actions + _loiterActions
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
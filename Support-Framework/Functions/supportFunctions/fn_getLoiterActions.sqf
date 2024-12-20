params ["_vehicle", "_target"];

private _actions = [];

// Loiter search details

{ // add all valid markers as valid locations
	
	// marker details
	private _marker = _x;
	private _markerName = markerText _marker;
	private _displayName = toLower _markerName;

	{
		private _prefix = toLower _x;
		if (_displayName find _prefix == 0) then {
			private _vicRequestToLoiterAction = [
				format["%1-loiterAt-%2", netId _vehicle, _marker], format["Loiter at %1", _markerName], "\a3\ui_f\data\igui\cfg\simpletasks\types\move_ca.paa",
				{
					// statement 
					params ["_target", "_caller", "_args"];
					private _vic = _args select 0;
					private _marker = _args select 1;
					_vic setVariable ["targetGroupLeader", _caller, true];
					_vic setVariable ["currentTask", "loiter", true];
					_vic setVariable ["fullRun", false, true];
					_vic setVariable ["destination", getMarkerPos _marker, true];
					_vic setVariable ["isPerformingDuties", false, true];
					if (YOSHI_HOME_BASE_CONFIG_OBJECT call ["SideHush"]) then {
						hint "Moving to loiter point...";
					} else {
						private _groupLeaderGroup = group _caller;
						private _groupLeaderCallsign = groupId _groupLeaderGroup;
						[_caller, format ["%2, this is %1, loiter at %3, over.", _groupLeaderCallsign, groupId group _vic, markerText _marker]] call YOSHI_fnc_sendSideText;
						[_vic, format ["%1, this is %2, moving to loiter at %3, out.", _groupLeaderCallsign, groupId group _vic, markerText _marker]] spawn  {
							params ["_vehicle", "_response"];
							sleep 3;
							[_vehicle, _response] call YOSHI_fnc_sendSideText;
						};
					};
					[_vic, format["Moving to hold at %1", markerText _marker]] call YOSHI_fnc_vehicleChatter;
					private _group = group _vic;
					// delete waypoints 
					for "_i" from (count waypoints _group - 1) to 0 step -1 do
					{
						deleteWaypoint [_group, _i];
					};
					[_vic] remoteExec ["YOSHI_fnc_loiter", 2];
				}, 
				{
					params ["_target", "_caller", "_args"];
					private _vic = _args select 0;
					private _marker = _args select 1;
					// // Condition code here
					private _task = _vic getVariable ["currentTask", "waiting"];
					private _notOnRestrictedTask = !(_task in ["loiter", "landingAtObjective","landingAtBase", "requestBaseLZ", "requestReinsert"]);
					private _notAtLoiter = (_vic distance2D getMarkerPos _marker) > 100;
					_notOnRestrictedTask && _notAtLoiter
				},
				{}, // 5: Insert children code <CODE> (Optional)
				[_vehicle, _marker] // 6: Action parameters <ANY> (Optional)
			] call ace_interact_menu_fnc_createAction;
			_actions pushBack [_vicRequestToLoiterAction, [], _target];
			};
	} forEach (YOSHI_HOME_BASE_CONFIG_OBJECT call ["LoiterPrefixes"]);

} forEach allMapMarkers;

_actions
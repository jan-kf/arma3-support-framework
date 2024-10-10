params ["_vic", "_touchdownMessage"];
// vic is performing it's landing procedures at the location

if ([_vic] call YOSHI_fnc_hasLanded) then {
	_vic engineOn false;
	[driver _vic, _touchdownMessage] call YOSHI_fnc_sendSideText;
	[_vic, _touchdownMessage] call YOSHI_fnc_vehicleChatter;
	[_vic, "YOSHI_TransportComplete"] call YOSHI_fnc_playVehicleRadio;

	// wait after touchdown
	sleep 10;
	_vic setVariable ["isPerformingDuties", false, true];
	private _fullRun = _vic getVariable ["fullRun", false];
	if (_fullRun) then {
		_vic setVariable ["currentTask", "requestBaseLZ", true];
	} else {
		[_vic, format ["%1 on standby, awaiting orders.", groupId group _vic]] call YOSHI_fnc_sendSideText;
		_vic setVariable ["currentTask", "awaitOrders", true];
	};
};
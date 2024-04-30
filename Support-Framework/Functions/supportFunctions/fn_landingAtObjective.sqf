params ["_vic", "_touchdownMessage"];
// vic is performing it's landing procedures at the location

if ((isTouchingGround _vic) && (speed _vic < 1)) then {
	_vic engineOn false;
	[driver _vic, _touchdownMessage] call SupportFramework_fnc_sideChatter;
	[_vic, _touchdownMessage] call SupportFramework_fnc_vehicleChatter;

	// wait after touchdown
	sleep 10;
	_vic setVariable ["isPerformingDuties", false, true];
	private _fullRun = _vic getVariable ["fullRun", false];
	if (_fullRun) then {
		_vic setVariable ["currentTask", "requestBaseLZ", true];
	} else {
		[_vic, format ["%1 on standby, awaiting orders.", groupId group _vic]] call SupportFramework_fnc_sideChatter;
		_vic setVariable ["currentTask", "awaitOrders", true];
	};
};
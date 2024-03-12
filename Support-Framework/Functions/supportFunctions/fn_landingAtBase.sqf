params ["_vic"];
// vic is performing it's landing procedures at the base

if ((isTouchingGround _vic) && (speed _vic < 1)) then {
	// always release parking request 
	[_vic] call SupportFramework_fnc_removeVehicleFromPadRegistry;
	
	_vic engineOn false;
	_vic setVariable ["isPerformingDuties", false, true];

	[driver _vic, format ["%1 is ready for tasking...", groupId group _vic]] call SupportFramework_fnc_sideChatter;

	// once landed, go back to waiting
	_vic setVariable ["currentTask", "waiting", true];
};
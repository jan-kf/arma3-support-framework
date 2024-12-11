params ["_vic"];
// vic is performing it's landing procedures at the base
_vic setCaptive false; // catch for certain situations where I needed the vic to be incognito

_vic setCollisionLight true;

if ([_vic] call YOSHI_fnc_hasLanded) then {
	// always release parking request 
	[_vic] call YOSHI_fnc_removeVehicleFromPadRegistry;
	
	_vic engineOn false;
	_vic setVariable ["isPerformingDuties", false, true];

	[driver _vic, format ["%1 is ready for tasking...", groupId group _vic]] call YOSHI_fnc_sendSideText;

	// once landed, go back to waiting
	_vic setVariable ["currentTask", "waiting", true];
};
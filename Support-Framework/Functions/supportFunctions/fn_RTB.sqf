params ["_vic"];
// vic is currently making it's way back to YOSHI_HOME_BASE_CONFIG_OBJECT



private _destination = _vic getVariable "destination";

private _locationData = [_destination, false] call YOSHI_fnc_getLocation;
private _locationName = _locationData select 0;
private _locationPOS = _locationData select 1;

// check the vic is near the base, and ready to land 
if (_vic distance2D _locationPOS < 100 && unitReady _vic) then {
	// set task to land at base
	_vic land "LAND";
	[_vic, "LAND"] remoteExec ["land"];
	_vic setVariable ["currentTask", "landingAtBase", true];
} else {
	// check if there are any issues
	[_vic] call YOSHI_fnc_checkPulse;
};



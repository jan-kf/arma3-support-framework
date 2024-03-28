params ["_vic"];
// vic is currently making it's way back to (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG")

// check if there are any issues
[_vic] call SupportFramework_fnc_checkPulse;

private _destination = _vic getVariable "destination";

private _locationData = [_destination] call SupportFramework_fnc_getLocation;
private _locationName = _locationData select 0;
private _locationPOS = _locationData select 1;

// check the vic is near the base, and ready to land 
if (_vic distance2D _locationPOS < 100 && unitReady _vic) then {
	// set task to land at base
	_vic land "LAND";
	_vic setVariable ["currentTask", "landingAtBase", true];
};



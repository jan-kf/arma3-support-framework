params ["_vic"];
// vic is currently making it's way back to (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG")

// check if there are any issues

private _destination = _vic getVariable "destination";
private _destinationPos = nil;
if (typeName _destination == "STRING") then {
	// _destination is a string
	_destinationPos = getMarkerPos _destination;
} else {
	if (typeName _destination == "OBJECT") then {
		// _destination is an object
		_destinationPos = getPos _destination;
	};
};

// check the vic is near the base, and ready to land 
if (_vic distance2D _destinationPos < 100 && unitReady _vic) then {
	// set task to land at base
	_vic land "LAND";
	_vic setVariable ["currentTask", "landingAtBase", true];
};
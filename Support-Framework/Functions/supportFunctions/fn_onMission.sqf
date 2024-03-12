params ["_vic"];
// vic is currently making its way to the redeploy LZ
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
private _vicGroup = group _vic;
{
	_x enableAI "all";
} forEach (units _vicGroup);
_vicGroup setCombatMode "GREEN";
_vicGroup setBehaviourStrong "AWARE";

private _isCAS = _vic getVariable ["isCAS", false];
if (_isCAS) then {
	// check if near target
	if (_vic distance2D _destinationPos < 1000 ) then {
		_vicGroup setCombatMode "RED";
		//save the current time for later use 
		_vic setVariable ["taskStartTime", serverTime, true];
		//set task to CAS duties
		_vic setVariable ["currentTask", "performingCAS", true];
		[driver _vic, format ["Beginning my attack..."]] call SupportFramework_fnc_sideChatter;
	};
}else{
	// check the vic is near the objective, and ready to land 
	if (_vic distance2D _destinationPos < 100 && unitReady _vic) then {
		// set task to land at objective
		_vic land "LAND";
		_vic setVariable ["currentTask", "landingAtObjective", true];
	};
};
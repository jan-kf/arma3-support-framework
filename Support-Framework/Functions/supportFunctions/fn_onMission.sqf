params ["_vic"];
// vic is currently making its way to the redeploy LZ
// check if there are any issues

private _destination = _vic getVariable "destination";

private _locationData = [_destination] call SupportFramework_fnc_getLocation;
private _locationName = _locationData select 0;
private _locationPOS = _locationData select 1;

private _vicGroup = group _vic;
{
	_x enableAI "all";
} forEach (units _vicGroup);
_vicGroup setCombatMode "GREEN";
_vicGroup setBehaviourStrong "AWARE";

private _isCAS = _vic getVariable ["isCAS", false];
if (_isCAS) then {
	// check if near target
	if (_vic distance2D _locationPOS < 1000 ) then {
		_vicGroup setCombatMode "RED";
		//save the current time for later use 
		_vic setVariable ["taskStartTime", serverTime, true];
		//set task to CAS duties
		_vic setVariable ["currentTask", "performingCAS", true];
		[driver _vic, format ["Beginning my attack..."]] call SupportFramework_fnc_sideChatter;
	};
}else{
	// check the vic is near the objective, and ready to land 
	if (_vic distance2D _locationPOS < 100 && unitReady _vic) then {
		// set task to land at objective
		_vic land "LAND";
		_vic setVariable ["currentTask", "landingAtObjective", true];
	};
};
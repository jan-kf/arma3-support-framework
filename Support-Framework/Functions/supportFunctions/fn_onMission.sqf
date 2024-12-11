params ["_vic"];
// vic is currently making its way to the redeploy LZ

// check if there are any issues
private _isCAS = _vic getVariable ["isCAS", false];
private _isRecon = _vic getVariable ["isRecon", false];

_vic setCollisionLight false;

private _vicGroup = group _vic;
private _anyDisabled = false;
{
	if (!(_x checkAIFeature "AUTOTARGET")) then {
		_anyDisabled = true;
	};
} forEach (units _vicGroup);

if (_anyDisabled) then {
	{
		_x enableAI "all";
	} forEach (units _vicGroup);
	_vicGroup setCombatMode "GREEN";
	_vicGroup setBehaviourStrong "AWARE";
};


if (_isCAS || _isRecon) then {
	private _destination = _vic getVariable "destination";

	private _locationData = [_destination, false] call YOSHI_fnc_getLocation;
	private _locationName = _locationData select 0;
	private _locationPOS = _locationData select 1;
	if (_isCAS) then {
		// check if near target
		if (_vic distance2D _locationPOS < 1000 ) then {
			_vicGroup setCombatMode "RED";
			//save the current time for later use 
			_vic setVariable ["taskStartTime", serverTime, true];
			//set task to CAS duties
			_vic setVariable ["currentTask", "performingCAS", true];
			[driver _vic, format ["Beginning my attack..."]] call YOSHI_fnc_sendSideText;
		} else {
			// check if there are any issues
			[_vic] call YOSHI_fnc_checkPulse;
		};
	} else {
		// isRecon
		if (_vic distance2D _locationPOS < 1000 ) then {
			_vic setCaptive true;
			//save the current time for later use 
			_vic setVariable ["taskStartTime", serverTime, true];
			//set task to Recon duties
			_vic setVariable ["currentTask", "performingRecon", true];
			[driver _vic, format ["Beginning Recon..."]] call YOSHI_fnc_sendSideText;
		} else {
			// check if there are any issues
			[_vic, "LOITER"] call YOSHI_fnc_checkPulse;
		};
	};
}else{
	private _destination = _vic getVariable "destination";

	private _locationData = [_destination] call YOSHI_fnc_getLocation;
	private _locationName = _locationData select 0;
	private _locationPOS = _locationData select 1;
	// check the vic is near the objective, and ready to land 
	if (_vic distance2D _locationPOS < 100 && unitReady _vic) then {
		// set task to land at objective
		_vic land "LAND";
		[_vic, "LAND"] remoteExec ["land"];
		_vic setVariable ["currentTask", "landingAtObjective", true];
	} else {
		// check if there are any issues
		[_vic] call YOSHI_fnc_checkPulse;
	};
};
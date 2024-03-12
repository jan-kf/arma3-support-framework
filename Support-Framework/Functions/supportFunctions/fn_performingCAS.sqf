params ["_vic"];
// vic is performing close air support at the location
private _start = _vic getVariable "taskStartTime";
private _elapsedTime = serverTime - _start;
if (_elapsedTime > 210) then { // 3 minutes, 30 seconds
	// send message about finishing mission?
	// TODO: set behavior to ignore enemies when flying away
	private _vicGroup = group _vic;
	
	{
		_x disableAI "all";
		_x enableAI "ANIM";
		_x enableAI "MOVE";
		_x enableAI "PATH";
	} forEach (units _vicGroup);
	_vicGroup setCombatMode "BLUE";
	_vicGroup setBehaviourStrong "SAFE";

	[driver _vic, format ["Attack complete, returning to base."]] call SupportFramework_fnc_sideChatter;
	// requestLZ at base, and RTB
	_vic setVariable ["currentTask", "requestBaseLZ", true];
};

// should listen if it gets an early wave-off, 
// otherwise it should perform it's mission for a set amount of time
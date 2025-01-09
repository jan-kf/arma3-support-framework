params ["_vic"];

// vic is performing close air support at the location
private _start = _vic getVariable "taskStartTime";
private _elapsedTime = serverTime - _start;

private _ReconConfigured = YOSHI_SUPPORT_RECON_CONFIG_OBJECT call YOSHI_isInitialized;

if (_ReconConfigured) then {
	_timeLimit = YOSHI_SUPPORT_RECON_CONFIG_OBJECT get "TaskTime";

	private _safeIsNull = {
		params ["_var"];

		if (_var isEqualTo false) then {
			true; // The variable is undefined (nil)
		} else {
			isNull _var; // The variable is defined, check if it's a null object
		};
	};

	private _reconTask = _vic getVariable ["reconTask", false];

	private _hasNoReconTaskRunning = [_reconTask] call _safeIsNull;

	if (_hasNoReconTaskRunning) then {
		
		_reconTask = [_vic] spawn YOSHI_fnc_doRecon;
		_vic setVariable ["reconTask", _reconTask, true];
	};


	if (_elapsedTime > _timeLimit) then { 
		// set behavior to ignore enemies when flying away
		private _vicGroup = group _vic;
		
		{
			_x disableAI "all";
			_x enableAI "ANIM";
			_x enableAI "MOVE";
			_x enableAI "PATH";
		} forEach (units _vicGroup);
		_vicGroup setCombatMode "BLUE";
		_vicGroup setBehaviourStrong "SAFE";

		[driver _vic, format ["Recon complete, returning to base."]] call YOSHI_fnc_sendSideText;
		// requestLZ at base, and RTB
		_vic setVariable ["currentTask", "requestBaseLZ", true];

		terminate _reconTask;
	} else {
		[_vic, "LOITER"] call YOSHI_fnc_checkPulse;
	};
};
// should listen if it gets an early wave-off, 
// otherwise it should perform it's mission for a set amount of time
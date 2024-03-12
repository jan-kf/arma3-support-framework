if (!isServer) exitWith {};

private _homeBase = missionNamespace getVariable ["YOSHI_HOME_BASE_CONFIG", nil];

if (isNil "_homeBase") exitWith {diag_log "[SUPPORT] YOSHI_HOME_BASE_CONFIG is not set, terminating process";};

private _vic = _this select 0;

private _baseCallsign = [west, "base"];
private _baseName = "Base";

private _baseIsNotVirtual = false;

private _syncedObjects = synchronizedObjects (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG");
{
	if (_x isKindOf "Man") exitWith {
		_baseCallsign = _x;
		_baseName = groupId group _x;
		_baseIsNotVirtual = true;
	};
} forEach _syncedObjects;

// [format ["Starting watchdog for %1 ... ", _vic]] remoteExec ["systemChat"];
diag_log format ["Starting watchdog for %1 ... ", _vic];

private _watchdog = _vic getVariable "watchdog";
if (!isNil "_watchdog") exitWith {
	// [format ["watchdog exists for %1, skipping | %2", _vic, _watchdog]] remoteExec ["systemChat"];
	diag_log format ["watchdog exists for %1, skipping", _vic];
};

private _vehicleClass = typeOf _vic;
private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
	

private _dustOffMessage = nil;
private _touchdownMessage = nil;

if (_vic getVariable ["isHeli", false]) then {
	_dustOffMessage = "Heading to LZ at: %1";
	_touchdownMessage = "Touchdown, Please disembark now";
} else {
	_dustOffMessage = "Heading to RP at: %1";
	_touchdownMessage = "We're here, Please disembark now";
};

private _isCAS = _vic getVariable ["isCAS", false];

private _helloMsg = "%1 On Station...";

if (_isCAS) then {
	_helloMsg = "Close Air Support, %1 On Station...";
};

[driver _vic, format[_helloMsg, groupId group _vic]] call SupportFramework_fnc_sideChatter;

while {_vic getVariable ["isRegistered", false]} do {
	// run while the vic is registered

	/*
	should perform a heartbeat check: 
		- check it's current location

		- check what it's supposed to be doing
			- waiting
			- onMission
				- is it making it's way to the redeploy point?
			- RTB
				- is it making it's way back to base?
		
		- is it where it's meant to be?
			- if not it should remedy it 
	*/

	private _task = _vic getVariable ["currentTask", "waiting"];

	// [format["%1 watchdog loop: %2 | %3", _vehicleDisplayName, _task, time]] remoteExec ["systemChat"];

	// [driver _vic, format["%1 -> current task: %2", _vehicleDisplayName, _task]] call SupportFramework_fnc_sideChatter;
	diag_log format["[SUPPORT] %1 watchdog loop: %2 | %3", _vehicleDisplayName, _task, time];


	switch (_task) do
	{
		case "resistered": {
			/*
			vic was just registered, should probably check that it's at base
			if it's not at base, should probably have it go back to base to sort itself out
			once ready, set task to waiting
			*/ 

			_vic setVariable ["currentTask", "waiting", true];
		};
		case "requestReinsert": {
			// vic was told to begin it's mission, perform startup

			[_vic, _baseCallsign, _baseName, _baseIsNotVirtual] call SupportFramework_fnc_requestReinsert;
		};
		case "requestCas": {
			// vic was told to begin it's cas mission, perform startup
			
			[_vic, _baseCallsign, _baseName, _baseIsNotVirtual] call SupportFramework_fnc_requestCas;
		};
		case "onMission": {
			// vic is currently making its way to the redeploy LZ
			
			[_vic] call SupportFramework_fnc_onMission;
		};
		case "RTB": {
			
			[_vic] call SupportFramework_fnc_RTB;
		};
		case "performingCAS": {

			[_vic] call SupportFramework_fnc_performingCAS;
		};
		case "landingAtObjective": {
			[_vic, _touchdownMessage] call SupportFramework_fnc_landingAtObjective;
		};
		case "requestBaseLZ": {
			
			[_vic, _baseCallsign, _baseName] call SupportFramework_fnc_requestBaseLZ;
		};
		case "waveOff": {

			[_vic] call SupportFramework_fnc_waveOff;
		};
		case "landingAtBase": {

			[_vic] call SupportFramework_fnc_landingAtBase;
		};
		case "awaitOrders": {
			// vic was called in to land, awaiting explicit orders to RTB
			// no code, leader will set the current task manually
		};
		case "marooned": {
			// vic was denied a landing pad at home base
			sleep 10;
			
			_vic setVariable ["currentTask", "requestBaseLZ", true];
		};
		default {
			//vic is waiting for a task, wait
			_vic setVariable ["isPerformingDuties", false, true];
			_vic setVariable ["targetGroupLeader", nil, true];
			_vic setVariable ["fullRun", true, true];
		};

	};

	
	sleep 3;
};

[driver _vic, format["%1 Off Station...", groupId group _vic]] call SupportFramework_fnc_sideChatter;

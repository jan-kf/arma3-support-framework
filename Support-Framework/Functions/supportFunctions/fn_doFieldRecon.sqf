params ["_uav", "_location", "_caller"];

if (!isServer) exitWith {};

private _locationData = [_location] call SupportFramework_fnc_getLocation;
private _locationName = _locationData select 0;
private _locationPOS = _locationData select 1;

_uav setVariable ["destination", _locationPOS, true];
	
private _currentPos = getPos _uav;

// set waypoint
private _grp = group _uav;
private _base_wp = _grp addWaypoint [_locationPOS, 0];
_base_wp setWaypointType "LOITER";
_grp setCurrentWaypoint _base_wp;
_uav setVariable ["taskStartTime", serverTime, true];

private _start = _uav getVariable "taskStartTime";
private _elapsedTime = serverTime - _start;

private _reconConfig = missionNamespace getVariable ["YOSHI_SUPPORT_RECON_CONFIG", nil];
private _ReconConfigured = !(isNil "_reconConfig");
private _timeLimit = 300;
if (_ReconConfigured) then {
	_timeLimit = _reconConfig getVariable ["TaskTime", 300];
};

private _safeIsNull = {
	params ["_var"];

	if (_var isEqualTo false) then {
		true; // The variable is undefined (nil)
	} else {
		isNull _var; // The variable is defined, check if it's a null object
	};
};

private _reconTask = _uav getVariable ["reconTask", false];

_uav setCaptive true;

while {(_elapsedTime < _timeLimit)} do { 

	[_uav, "LOITER"] call SupportFramework_fnc_checkPulse;

	_reconTask = _uav getVariable ["reconTask", false];

	_hasNoReconTaskRunning = [_reconTask] call _safeIsNull;

	if (_hasNoReconTaskRunning) then {
		
		_reconTask = [_uav] spawn SupportFramework_fnc_doRecon;
		_uav setVariable ["reconTask", _reconTask, true];
	};

	sleep 1;

	_elapsedTime = serverTime - _start;
};

// set behavior to ignore enemies when flying away
{
	_x disableAI "all";
	_x enableAI "ANIM";
	_x enableAI "MOVE";
	_x enableAI "PATH";
} forEach (units _grp);
_grp setCombatMode "BLUE";
_grp setBehaviourStrong "SAFE";

private _lz = getPos _caller;

_uav setVariable ["destination", _lz, true];
private _return_wp = _grp addWaypoint [_lz, 0];
_return_wp setWaypointType "MOVE";
_grp setCurrentWaypoint _return_wp;

terminate _reconTask;

"Drone has completed recon, returning to you" remoteExec ["hint", _caller];

while {(_uav distance2D _caller > 50) && !(unitReady _uav)} do {
	[_uav] call SupportFramework_fnc_checkPulse;
};

_uav setCaptive false;

createVehicle ["Land_HelipadEmpty_F", getPos _caller, [], 0];

sleep 1;
// set task to land at objective
_uav land "LAND";

params ["_uav", "_location", "_caller"];

private _locationData = [_location, false] call YOSHI_fnc_getLocation;
private _locationName = _locationData select 0;
private _locationPOS = _locationData select 1;

_uav setVariable ["destination", _locationPOS, true];

private _grp = group _uav;
for "_i" from (count waypoints _grp - 1) to 0 step -1 do
{
	deleteWaypoint [_grp, _i];
};

[_uav, _locationPOS, "LOITER"] call YOSHI_fnc_setWaypoint;

_uav setVariable ["taskStartTime", serverTime, true];

private _start = _uav getVariable "taskStartTime";
private _elapsedTime = serverTime - _start;

private _ReconConfigured = [YOSHI_SUPPORT_RECON_CONFIG_OBJECT] call YOSHI_isInitialized;
private _timeLimit = 300;
if (_ReconConfigured) then {
	_timeLimit = YOSHI_SUPPORT_RECON_CONFIG_OBJECT get "TaskTime";
};
private _markerUpdateInterval = YOSHI_SUPPORT_RECON_CONFIG_OBJECT get "Interval"; 

private _safeIsNull = {
	params ["_var"];

	if (_var isEqualTo false) then {
		true; // The variable is undefined (nil)
	} else {
		isNull _var; // The variable is defined, check if it's a null object
	};
};

private _reconTask = _uav getVariable ["reconTask", false];

[_uav, true] remoteExec ["setCaptive"];

while {(alive _uav) && (_elapsedTime < (_timeLimit + (_markerUpdateInterval * 2)))} do { 

	[_uav, "LOITER"] call YOSHI_fnc_checkPulse;

	_reconTask = _uav getVariable ["reconTask", false];

	_hasNoReconTaskRunning = [_reconTask] call _safeIsNull;

	if (_hasNoReconTaskRunning) then {
		
		_reconTask = [_uav] spawn YOSHI_fnc_doRecon;
		_uav setVariable ["reconTask", _reconTask, true];
	};

	sleep 1;

	_elapsedTime = serverTime - _start;
};

private _lz = getPosATL _caller;

for "_i" from (count waypoints _grp - 1) to 0 step -1 do
{
	deleteWaypoint [_grp, _i];
};

_uav setVariable ["destination", _lz, true];

[_uav, _lz] call YOSHI_fnc_setWaypoint;

terminate _reconTask;

"Drone has completed recon, returning to you" remoteExec ["hint", _caller];

while {(_uav distance2D _caller > 50) || !(unitReady _uav)} do {
	[_uav] call YOSHI_fnc_checkPulse;
};

[_uav, false] remoteExec ["setCaptive"];

createVehicle ["Land_HelipadEmpty_F", getPosATL _caller, [], 0];

sleep 3;

_uav land "LAND";


while {!([_uav] call YOSHI_fnc_hasLanded)} do {
	sleep 5;
	[_uav, "LAND"] remoteExec ["land"];
};

[_uav, false] remoteExec ["setCaptive", 0];

// For some reason the UAV is lobotomized once it lands so this refreshes it
deleteVehicleCrew _uav;
createVehicleCrew _uav;

params ["_uav", "_location", "_caller"];

private _locationData = [_location, false] call SupportFramework_fnc_getLocation;
private _locationName = _locationData select 0;
private _locationPOS = _locationData select 1;

_uav setVariable ["destination", _locationPOS, true];

private _grp = group _uav;
for "_i" from (count waypoints _grp - 1) to 0 step -1 do
{
	deleteWaypoint [_grp, _i];
};

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
private _markerUpdateInterval = _reconConfig getVariable ["Interval", 5]; 

private _safeIsNull = {
	params ["_var"];

	if (_var isEqualTo false) then {
		true; // The variable is undefined (nil)
	} else {
		isNull _var; // The variable is defined, check if it's a null object
	};
};

private _reconTask = _uav getVariable ["reconTask", false];

[_uav, true] remoteExec ["setCaptive", 0];

while {(alive _uav) && (_elapsedTime < (_timeLimit + (_markerUpdateInterval * 2)))} do { 

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

private _lz = getPos _caller;

for "_i" from (count waypoints _grp - 1) to 0 step -1 do
{
	deleteWaypoint [_grp, _i];
};

_uav setVariable ["destination", _lz, true];
private _return_wp = _grp addWaypoint [_lz, 0];
_return_wp setWaypointType "MOVE";
_grp setCurrentWaypoint _return_wp;

terminate _reconTask;

"Drone has completed recon, returning to you" remoteExec ["hint", _caller];

while {(_uav distance2D _caller > 50) || !(unitReady _uav)} do {
	[_uav] call SupportFramework_fnc_checkPulse;
};

[_uav, false] remoteExec ["setCaptive", 0];

createVehicle ["Land_HelipadEmpty_F", getPos _caller, [], 0];

sleep 3;

_uav land "LAND";


while {!(isTouchingGround _uav) || ((speed _uav) > 1)} do {
	sleep 5;
	[_uav, "LAND"] remoteExec ["land"];
};


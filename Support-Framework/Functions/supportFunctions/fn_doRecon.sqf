params ["_uav"];

if (!isServer) exitWith {};

private _reconConfig = missionNamespace getVariable ["YOSHI_SUPPORT_RECON_CONFIG", nil];
private _ReconConfigured = !(isNil "_reconConfig");
private _timeLimit = 300;
if (_ReconConfigured) then {
	_timeLimit = _reconConfig getVariable ["TaskTime", 300];
};

private _detectionRange = 1000; 
private _markerUpdateInterval = _reconConfig getVariable ["Interval", 5]; 
private _markers = []; 


private _showNames = _reconConfig getVariable ["ShowNames", true]; 
private _hasHyperSpectralSensors = _reconConfig getVariable ["HasHyperSpectralSensors", false]; 

private _group = group _uav;

private _getReadableName = { 
	params ["_className"];
 
    private _config = configFile >> "CfgVehicles" >> _className; 
    private _displayName = getText(_config >> "displayName");
	 
    _displayName 
};

private _canSee = {
	params [
		["_looker",objNull,[objNull]],
		["_target",objNull,[objNull]],
		["_FOV",70,[0]]
	];
	if ([position _looker, getdir _looker, _FOV, position _target] call BIS_fnc_inAngleSector) then {
		if (count (lineIntersectsSurfaces [(AGLtoASL (_looker modelToWorldVisual (_looker selectionPosition "pilot"))), getPosASL _target, _target, _looker, true, 1,"GEOM","NONE"]) > 0) exitWith {false};
		true
	} else {
		false
	};
};

private _start = _uav getVariable "taskStartTime";
private _elapsedTime = serverTime - _start;

while {(alive _uav) && _elapsedTime < _timeLimit} do {
	_cwp = currentWaypoint _group;
	_wpp = waypointPosition [_group, _cwp];

	_uav lookAt _wpp;


	_all_units = _uav nearEntities [["Man", "Car", "Tank", "Ship", "Air", "Motorcycle"], _detectionRange];
	_filteredTargets = [];
	{
		if (_hasHyperSpectralSensors || ([_uav, _x, 360] call _canSee)) then {
			_filteredTargets pushBack _x;
		};
	} forEach _all_units;


    {
        deleteMarker _x;
    } forEach _markers;

    {
        _target = _x;
        _type = typeOf _target;
		_side = side _x;

        _markerName = format ["_USER_DEFINED marker_%1_%2", _type, round random 1000000];
        _markers pushBack _markerName; 

		_color = "ColorUNKNOWN";
		
		if (_side == west) then {_color = "ColorWEST"}; 
		if (_side == east) then {_color = "ColorEAST"}; 
		if (_side == resistance) then {_color = "ColorGUER"}; 
		if (_side == civilian) then {_color = "ColorCIV"};
		


        _marker = createMarker [_markerName, _target, 1, _uav];
        _marker setMarkerShape "ICON";
        _marker setMarkerType "mil_dot";
        _marker setMarkerColor _color;
		if (_showNames) then {
        	_marker setMarkerText ([_type] call _getReadableName);
		};

    } forEach _filteredTargets;

	sleep _markerUpdateInterval;

	_elapsedTime = serverTime - _start;
};


{
    deleteMarker _x;
} forEach _markers;

params ["_uav"];

private _ReconConfigured = !(isNil "YOSHI_SUPPORT_RECON_CONFIG");
private _timeLimit = 300;
if (_ReconConfigured) then {
	_timeLimit = YOSHI_SUPPORT_RECON_CONFIG getVariable ["TaskTime", 300];
};

private _detectionRange = 1000; 
private _markerUpdateInterval = YOSHI_SUPPORT_RECON_CONFIG getVariable ["Interval", 5]; 
private _markers = []; 

private _showNames = YOSHI_SUPPORT_RECON_CONFIG getVariable ["ShowNames", true]; 
private _hasHyperSpectralSensors = YOSHI_SUPPORT_RECON_CONFIG getVariable ["HasHyperSpectralSensors", false]; 

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

_uav setVariable ["taskStartTime", serverTime, true];

private _start = _uav getVariable "taskStartTime";
private _elapsedTime = serverTime - _start;

while {(alive _uav) && (_elapsedTime < _timeLimit)} do {
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

		_color = "ColorUNKNOWN";
		if (_side == west) then {_color = "ColorWEST"}; 
		if (_side == east) then {_color = "ColorEAST"}; 
		if (_side == resistance) then {_color = "ColorGUER"}; 
		if (_side == civilian) then {_color = "ColorCIV"};

        _markerName = format ["_USER_DEFINED marker_%1_%2", _type, round random 1000000];

		_text = "";
		if (_showNames) then {
        	_text = [_type] call _getReadableName;
		};
		
		_marker = [_target, _text, _color] call YOSHI_fnc_addMarker;
        _markers pushBack _marker; 

    } forEach _filteredTargets;

	sleep _markerUpdateInterval;

	_elapsedTime = serverTime - _start;
};

{
    deleteMarker _x;
} forEach _markers;

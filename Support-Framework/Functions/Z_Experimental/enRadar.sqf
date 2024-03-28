params ["_uav"];

_detectionRange = 1000; 
_markerUpdateInterval = 0.5; 
_markers = []; 

private _group = group _uav;

_getReadableName = { 
params ["_className"];
 
    private _config = configFile >> "CfgVehicles" >> _className; 
    private _displayName = getText(_config >> "displayName"); 
    _displayName 
};

_canSee = {
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



while {alive _uav} do {
	_cwp = currentWaypoint _group;
	_wpp = waypointPosition [_group, _cwp];

	_uav lookAt _wpp;


	_all_units = _uav nearEntities [["Man", "Car", "Tank", "Ship", "Air", "Motorcycle"], _detectionRange];
	_filteredTargets = [];
	{
		_filteredTargets pushBack _x;
	} forEach _all_units;


    {
        deleteMarker _x;
    } forEach _markers;

    {
        _target = _x;
        _position = getPos _target;
        _type = typeOf _target;
		_object = _target;
		_side = side _x;

        _markerName = format ["_USER_DEFINED marker_%1_%2_%3", _position select 0, _type, round random 1000000];
        _markers pushBack _markerName; 

		_color = "ColorUNKNOWN";
		
		if (_side == west) then {_color = "ColorWEST"}; 
		if (_side == east) then {_color = "ColorEAST"}; 
		if (_side == resistance) then {_color = "ColorGUER"}; 
		if (_side == civilian) then {_color = "ColorCIV"};
		


        _marker = createMarker [_markerName, _position];
        _marker setMarkerShape "ICON";
        _marker setMarkerType "mil_dot";
        _marker setMarkerColor _color;
        _marker setMarkerText ([_type] call _getReadableName);

    } forEach _filteredTargets;

	sleep _markerUpdateInterval;

     
};


{
    deleteMarker _x;
} forEach _markers;






_uav = _this; 
_detectionRange = 1000; 

_detectedTargets = _uav nearTargets _detectionRange;


hint str(_filteredTargets);
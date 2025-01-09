params ["_unit", "_location", ["_type", "MOVE"]];

private _group = group _unit;
private _viaNode = false;

private _unitAtBase = [_unit] call YOSHI_fnc_isAtBase;
private _locationAtBase = [_location] call YOSHI_fnc_isAtBase;

if (!_unitAtBase && _locationAtBase) then {

	_arriveNode = YOSHI_HOME_BASE_CONFIG_OBJECT get "BaseArriveNode";

	if (!(isNil "_arriveNode")) then {
		private _wp = _group addWaypoint [_arriveNode, 0];
		_wp setWaypointType "MOVE"; 
		_group setCurrentWaypoint _wp;
		_viaNode = true;
	};
};

if (_unitAtBase && !_locationAtBase) then {

	_departNode = YOSHI_HOME_BASE_CONFIG_OBJECT get "BaseDepartNode";

	if (!(isNil "_departNode")) then {
		private _wp = _group addWaypoint [_departNode, 0];
		_wp setWaypointType "MOVE"; 
		_group setCurrentWaypoint _wp;
		_viaNode = true;
	};
};
	
private _wp = _group addWaypoint [_location, 0];
_wp setWaypointType _type; 

if (!_viaNode) then {
	_group setCurrentWaypoint _wp;
};

_wp

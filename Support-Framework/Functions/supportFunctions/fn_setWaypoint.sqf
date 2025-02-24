params ["_unit", "_location", ["_type", "MOVE"]];

private _group = group _unit;
private _viaNode = false;

private _unitAtBase = [_unit] call YOSHI_fnc_isAtBase;
private _locationAtBase = [_location] call YOSHI_fnc_isAtBase;
private _isNotDeployedFixedWing = true;
if ([YOSHI_FW_CONFIG_OBJECT] call YOSHI_isInitialized) then {
	private _isNotDeployedFixedWing = !(typeOf _unit in (YOSHI_FW_CONFIG_OBJECT get "DeployedUnits"));
};

if (!_unitAtBase && _locationAtBase && _isNotDeployedFixedWing) then {

	_arriveNode = YOSHI_HOME_BASE_CONFIG_OBJECT get "BaseArriveNode";

	if (!(isNil "_arriveNode")) then {
		private _wp = _group addWaypoint [_arriveNode, 0];
		_wp setWaypointType "MOVE"; 
		_group setCurrentWaypoint _wp;
		_viaNode = true;
	};
};

if (_unitAtBase && !_locationAtBase && _isNotDeployedFixedWing) then {

	_departNode = YOSHI_HOME_BASE_CONFIG_OBJECT get "BaseDepartNode";

	if (!(isNil "_departNode")) then {
		private _wp = _group addWaypoint [_departNode, 0];
		_wp setWaypointType "MOVE"; 
		_group setCurrentWaypoint _wp;
		_viaNode = true;
	};
};

private _location2D = [_location select 0, _location select 1, 0];

private _wp = _group addWaypoint [_location2D, 0];
_wp setWaypointType _type; 

if (!_viaNode) then {
	_group setCurrentWaypoint _wp;
};


_wp

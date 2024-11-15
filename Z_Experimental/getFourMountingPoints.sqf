connectObjectWithRopes = { 
    params ["_object1", "_object2", "_points"]; 
    private _corners = _points; 
    private _attachmentPoint = "slingload0"; 
    private _ropes = []; 
 
    { 
        private _rope = ropeCreate [_object1, _attachmentPoint, _object2, [_x select 0, _x select 1, (_x select 2) + 0.15], 20, [], ["RopeEnd", [0, 0, -1]]]; 
        _ropes pushBack _rope; 
    } forEach _corners; 
 
    _ropes 
};


_object = _this;

_getCorners = {
	params ["_coordinates"];
	private _minX = (_coordinates select 0) select 0;
	private _minY = (_coordinates select 0) select 1;
	private _minZ = (_coordinates select 0) select 2;
	private _maxX = _minX;
	private _maxY = _minY;
	private _maxZ = _minZ;

	{
		_minX = (_x select 0) min _minX;
		_minY = (_x select 1) min _minY;
		_minZ =( _x select 2) min _minZ;
		
		_maxX = (_x select 0) max _maxX;
		_maxY = (_x select 1) max _maxY;
		_maxZ = (_x select 2) max _maxZ;
	} forEach _coordinates;


	private _corners = [
		[_minX, _minY, _minZ],
		[_maxX, _minY, _minZ], 
		[_minX, _maxY, _minZ],
		[_maxX, _maxY, _minZ]
	];

	_corners
};

private _deg = -(getDir _object);   

_center = getPosWorld _object;

_corners = [_object, false] call YOSHI_fnc_getSlimBoundingBox;


private _centerX = (((_corners select 0) select 0) + ((_corners select 1) select 0) + ((_corners select 2) select 0) + ((_corners select 3) select 0)) / 4;
private _centerY = (((_corners select 0) select 1) + ((_corners select 1) select 1) + ((_corners select 2) select 1) + ((_corners select 3) select 1)) / 4;
 
private _raisedCenter = [_centerX, _centerY, (_center select 2) *1.5];

_mountingPoints = [];

{
	_intersect_temp = lineIntersectsSurfaces [ _raisedCenter, _x, objNull, objNull, true, 5, "FIRE", "GEOM"];

	{
		if (!((_x select 2) isEqualTo objNull)) exitWith {
			_mountingPoints pushBack (_x select 0);
		}
	} forEach _intersect_temp;

} forEach _corners;

_middleMounts = lineIntersectsSurfaces [ _raisedCenter, (_raisedCenter vectorMultiply [1,1,0]), objNull, objNull, true, 5, "FIRE", "GEOM"];

{
	if (!((_x select 2) isEqualTo objNull)) exitWith {
		_mountingPoints pushBack (_x select 0);
	}
} forEach _middleMounts;

_tempCorners3 = [_center, _mountingPoints] call YOSHI_realToLocal;

_localMountingPoints = [];
{
	_localMountingPoints pushBack ([_x, -_deg] call YOSHI_rotateZ);
} forEach _tempCorners3;


[heli, _object, _localMountingPoints] call connectObjectWithRopes;

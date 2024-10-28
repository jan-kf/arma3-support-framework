_realToLocal = {
	params ["_nexus", "_coordinates"];

	_localCoordinates = [];

	{
		_localCoordinates pushBack (_x vectorDiff _nexus);
	} forEach _coordinates;

	_localCoordinates

};

_localToReal = {
	params ["_nexus", "_coordinates"];

	_realCoordinates = [];

	{
		_realCoordinates pushBack (_nexus vectorAdd _x);
	} forEach _coordinates;

	_realCoordinates
};

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

_rotateZ = {
    params ["_point", "_angle"];
    private _x = (_point select 0);
    private _y = (_point select 1);
    
    private _newX = (_x * (cos _angle)) - (_y * (sin _angle));
    private _newY = (_x * (sin _angle)) + (_y * (cos _angle));
    
    [_newX, _newY, _point select 2]
};

_center = getPosWorld _object;
_boundingBox = boundingBoxReal _object;
_bBoxMin = _boundingBox select 0;
_bBoxMax = _boundingBox select 1;
_bBoxHeight = _bBoxMax select 2;

_cornerPairs = [
	[
		_center vectorAdd (_bBoxMax vectorMultiply [0,0,1]),
		_center vectorAdd (_bBoxMin vectorMultiply [0,0,1])
	],
	[
		_center vectorAdd _bBoxMax,
		_center vectorAdd _bBoxMin
	],
	[
		_center vectorAdd (((_bBoxMax vectorMultiply [0,1,1]) vectorAdd (_bBoxMin vectorMultiply [1,0,0])) vectorMultiply 0.8),
		_center vectorAdd (((_bBoxMax vectorMultiply [1,0,0]) vectorAdd (_bBoxMin vectorMultiply [0,1,1])) vectorMultiply 0.8)
	],
	[
		_center vectorAdd (((_bBoxMax vectorMultiply [1,0,1]) vectorAdd (_bBoxMin vectorMultiply [0,1,0])) vectorMultiply 0.8),
		_center vectorAdd (((_bBoxMax vectorMultiply [0,1,0]) vectorAdd (_bBoxMin vectorMultiply [1,0,1])) vectorMultiply 0.8)
	],
	[
		_center vectorAdd (((_bBoxMax vectorMultiply [0,0,1]) vectorAdd (_bBoxMin vectorMultiply [1,1,0])) vectorMultiply 0.8),
		_center vectorAdd (((_bBoxMax vectorMultiply [1,1,0]) vectorAdd (_bBoxMin vectorMultiply [0,0,1])) vectorMultiply 0.8)
	],

	[
		_center vectorAdd ((_bBoxMax vectorMultiply [1,1,0]) vectorMultiply 0.8),
		_center vectorAdd ((_bBoxMin vectorMultiply [1,1,0]) vectorMultiply 0.8)
	],
	[
		_center vectorAdd ((_bBoxMax vectorMultiply [1,0,0]) vectorMultiply 0.8),
		_center vectorAdd ((_bBoxMin vectorMultiply [1,0,0]) vectorMultiply 0.8)
	],
	[
		_center vectorAdd ((_bBoxMax vectorMultiply [0,1,0]) vectorMultiply 0.8),
		_center vectorAdd ((_bBoxMin vectorMultiply [0,1,0]) vectorMultiply 0.8)
	],

	[
		_center vectorAdd ((_bBoxMax vectorMultiply [1,1,0.5]) vectorMultiply 0.8),
		_center vectorAdd ((_bBoxMin vectorMultiply [1,1,-0.5]) vectorMultiply 0.8)
	],
	[
		_center vectorAdd ((_bBoxMax vectorMultiply [1,0,0.5]) vectorMultiply 0.8),
		_center vectorAdd ((_bBoxMin vectorMultiply [1,0,-0.5]) vectorMultiply 0.8)
	],
	[
		_center vectorAdd ((_bBoxMax vectorMultiply [0,1,0.5]) vectorMultiply 0.8),
		_center vectorAdd ((_bBoxMin vectorMultiply [0,1,-0.5]) vectorMultiply 0.8)
	],

	[
		_center vectorAdd ((_bBoxMax vectorMultiply [1,1,-0.5]) vectorMultiply 0.8),
		_center vectorAdd ((_bBoxMin vectorMultiply [1,1,0.5]) vectorMultiply 0.8)
	],
	[
		_center vectorAdd ((_bBoxMax vectorMultiply [1,0,-0.5]) vectorMultiply 0.8),
		_center vectorAdd ((_bBoxMin vectorMultiply [1,0,0.5]) vectorMultiply 0.8)
	],
	[
		_center vectorAdd ((_bBoxMax vectorMultiply [0,1,-0.5]) vectorMultiply 0.8),
		_center vectorAdd ((_bBoxMin vectorMultiply [0,1,0.5]) vectorMultiply 0.8)
	],

	[
		_center vectorAdd (((_bBoxMax vectorMultiply [1,1,0]) vectorAdd [0,0, (_bBoxHeight * -0.75)]) vectorMultiply 0.8),
		_center vectorAdd (((_bBoxMin vectorMultiply [1,1,0]) vectorAdd [0,0, (_bBoxHeight * -0.75)]) vectorMultiply 0.8)
	],
	[
		_center vectorAdd (((_bBoxMax vectorMultiply [1,0,0]) vectorAdd [0,0, (_bBoxHeight * -0.75)]) vectorMultiply 0.8),
		_center vectorAdd (((_bBoxMin vectorMultiply [1,0,0]) vectorAdd [0,0, (_bBoxHeight * -0.75)]) vectorMultiply 0.8)
	],
	[
		_center vectorAdd (((_bBoxMax vectorMultiply [0,1,0]) vectorAdd [0,0, (_bBoxHeight * -0.75)]) vectorMultiply 0.8),
		_center vectorAdd (((_bBoxMin vectorMultiply [0,1,0]) vectorAdd [0,0, (_bBoxHeight * -0.75)]) vectorMultiply 0.8)
	],

	[
		_center vectorAdd (_bBoxMax vectorMultiply [0.8,0,0]),
		_center 
	],
	[
		_center vectorAdd (_bBoxMax vectorMultiply [0,0.8,0]),
		_center 
	],
	[
		_center vectorAdd (_bBoxMax vectorMultiply [0,0,0.8]),
		_center 
	],
	[
		_center vectorAdd (_bBoxMin vectorMultiply [0.8,0,0]),
		_center 
	],
	[
		_center vectorAdd (_bBoxMin vectorMultiply [0,0.8,0]),
		_center 
	],
	[
		_center vectorAdd (_bBoxMin vectorMultiply [0,0,0.8]),
		_center 
	]
];

_boundingBoxLandContact = boundingBoxReal [_object, "LandContact"];
_landContantMax = (_boundingBoxLandContact select 0) vectorAdd _center;
_landContantMin = (_boundingBoxLandContact select 1) vectorAdd _center;

_intersects = [_landContantMax, _landContantMin];

{
	_start = _x select 0;
	_stop = _x select 1;

	_intersect_temp = lineIntersectsSurfaces [_start, _stop, objNull, objNull, true, 5, "FIRE", "GEOM"];

	{
		if (!((_x select 2) isEqualTo objNull)) exitWith {
			_intersects pushBack (_x select 0);
		}
	} forEach _intersect_temp; 

	_intersect_temp = lineIntersectsSurfaces [_stop, _start, objNull, objNull, true, 5, "FIRE", "GEOM"];

	{
		if (!((_x select 2) isEqualTo objNull)) exitWith {
			_intersects pushBack (_x select 0);
		}
	} forEach _intersect_temp;

} forEach _cornerPairs;

private _tempCorners = [_intersects] call _getCorners;

_tempCorners2 = [_center, _tempCorners] call _realToLocal;

_preCorners = [];
{
	_preCorners pushBack ([_x, _deg] call _rotateZ);
} forEach _tempCorners2;

_corners = [_center, _preCorners] call _localToReal;


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

_tempCorners3 = [_center, _mountingPoints] call _realToLocal;

_localMountingPoints = [];
{
	_localMountingPoints pushBack ([_x, -_deg] call _rotateZ);
} forEach _tempCorners3;


[heli, _object, _localMountingPoints] call connectObjectWithRopes;

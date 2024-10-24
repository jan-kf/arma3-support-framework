// ropes need local coordinates, but line intersect needs ASL, need to be able to convert!


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

_center = getPosWorld _object;
_boundingBox = boundingBoxReal _object;
_bBoxMin = _boundingBox select 0;
_bBoxMax = _boundingBox select 1;

_cornerPairs = [
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

private _corners = [_intersects] call _getCorners;

_mountingPoints = [];
{ 
	_intersect_temp = lineIntersectsSurfaces [_center, _x, objNull, objNull, true, 5, "FIRE", "GEOM"];
	{
		if (!((_x select 2) isEqualTo objNull)) exitWith {
			_mountingPoints pushBack (_x select 0);
		}
	} forEach _intersect_temp;

} forEach _corners;


connectObjectWithRopes = { 
    params ["_object1", "_object2", "_points"]; 
    private _corners = _points; 
    private _attachmentPoint = "slingload0"; 
    private _ropes = []; 
 
    { 
        private _rope = ropeCreate [_object1, _attachmentPoint, _object2, _x, 20]; 
        _ropes pushBack _rope; 
    } forEach _corners; 
 
    _ropes 
};
hint str(_corners);
[heli, _object, _mountingPoints] call connectObjectWithRopes;
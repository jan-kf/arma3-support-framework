params ["_object", ["_3D", true]];

private _deg = -(getDir _object);  
private _center = getPosWorld _object;
private _boundingBox = boundingBoxReal _object;
private _bBoxMin = _boundingBox select 0;
private _bBoxMax = _boundingBox select 1;
private _bBoxHeight = _bBoxMax select 2;

private _cornerPairs = [
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

private _boundingBoxLandContact = boundingBoxReal [_object, "LandContact"];
private _landContantMax = (_boundingBoxLandContact select 0) vectorAdd _center;
private _landContantMin = (_boundingBoxLandContact select 1) vectorAdd _center;

private _intersects = [_landContantMax, _landContantMin];

{
	_start = _x select 0;
	_stop = _x select 1;

	private _intersect_temp = lineIntersectsSurfaces [_start, _stop, objNull, objNull, true, 5, "FIRE", "GEOM"];

	{
		if (!((_x select 2) isEqualTo objNull)) exitWith {
			_intersects pushBack (_x select 0);
		}
	} forEach _intersect_temp; 

	private _intersect_temp = lineIntersectsSurfaces [_stop, _start, objNull, objNull, true, 5, "FIRE", "GEOM"];

	{
		if (!((_x select 2) isEqualTo objNull)) exitWith {
			_intersects pushBack (_x select 0);
		}
	} forEach _intersect_temp;

} forEach _cornerPairs;

private _tempCorners = [_intersects, _3D] call YOSHI_getBoundingCorners;

private _tempCorners2 = [_center, _tempCorners] call YOSHI_realToLocal;

private _localCorners = [];
{
	_localCorners pushBack ([_x, _deg] call YOSHI_rotateZ);
} forEach _tempCorners2;

private _realCorners = [_center, _localCorners] call YOSHI_localToReal;

// realCorners are in ASL

[_realCorners, _localCorners]

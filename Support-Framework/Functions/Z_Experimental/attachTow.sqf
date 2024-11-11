params ["_towVic", "_cargo"];

// needs more work
YOSHI_getTowLocation = {
	params ["_object", ["_isTowing", true]];

	_modifier = -1;
	if (_isTowing) then {_modifier = 1};

	_corners = boundingBoxReal _object;
	_center = ([_object] call YOSHI_getCenterOfMass) select 0;
	_dir = vectorDir _object;
	_xdir = (_corners select 0) select 0;
	_ydir = ((_corners select 0) select 1);
	_magnitude = sqrt ((_xdir ^ 2) + (_ydir ^ 2));
	_vector = _dir vectorMultiply (_magnitude * _modifier);
	_checkLoc = _center vectorAdd _vector;

	_intersects = lineIntersectsSurfaces [_checkLoc, _center, objNull, objNull, true, 5, "FIRE", "GEOM"];
	if ((count _intersects) > 0) then {
		(_intersects select 0) select 0
	} else {
		_checkLoc
	};
};


_cargoFront = ([getPosWorld _cargo, [[_cargo, false] call YOSHI_getTowLocation]] call YOSHI_realToLocal) select 0;
_towRear = ([getPosWorld _towVic, [[_towVic, true] call YOSHI_getTowLocation]] call YOSHI_realToLocal) select 0;

// ropeCreate needs coords that are relative to local getPosWorld coords
ropeCreate [_towVic, _towRear, _cargo, _cargoFront, 5, ["RopeEnd", [0, 0, -1]], ["RopeEnd", [0, 0, -1]]];

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

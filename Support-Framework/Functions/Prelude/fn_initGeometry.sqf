YOSHI_getBoundingCorners = {
	params ["_coordinates", ["_3D", true]];
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

	if (_3D) then {
		_corners append [
			[_minX, _minY, _maxZ],
			[_maxX, _minY, _maxZ], 
			[_minX, _maxY, _maxZ],
			[_maxX, _maxY, _maxZ]
		];
	};

	_corners
};


YOSHI_realToLocal = {
	params ["_nexus", "_coordinates"];

	_localCoordinates = [];

	{
		_localCoordinates pushBack (_x vectorDiff _nexus);
	} forEach _coordinates;

	_localCoordinates

};

YOSHI_localToReal = {
	params ["_nexus", "_coordinates"];

	_realCoordinates = [];

	{
		_realCoordinates pushBack (_nexus vectorAdd _x);
	} forEach _coordinates;

	_realCoordinates
};

YOSHI_rotateZ = {
    params ["_point", "_angle"];
    private _x = (_point select 0);
    private _y = (_point select 1);
    
    private _newX = (_x * (cos _angle)) - (_y * (sin _angle));
    private _newY = (_x * (sin _angle)) + (_y * (cos _angle));
    
    [_newX, _newY, _point select 2]
};

YOSHI_getCenterOfMass = {
	params ["_obj"];

	private _center = getCenterOfMass _obj;
	private _pos = getPosWorld _obj;


	private _rotated = [_center, -(getDir _obj)] call YOSHI_rotateZ;

	[(_pos vectorAdd _rotated), _center]

};


YOSHI_sweepAngle = {
	// Original points A and B
	params ['_pointA', '_pointB'];

	// Angle in degrees
	private _angle = 10;

	// Calculate the vector from A to B (ignoring Z)
	private _vectorAB = [
		(_pointB select 0) - (_pointA select 0),
		(_pointB select 1) - (_pointA select 1)
	];

	// Length of the vector (distance from A to B)
	private _distance = vectorMagnitude _vectorAB;

	// Get the original angle of the line in degrees
	private _initialAngle = (_vectorAB select 1) atan2 (_vectorAB select 0);

	// Calculate the new angles for ±10 degrees rotation
	private _angleLeft = _initialAngle + _angle;
	private _angleRight = _initialAngle - _angle;

	// Calculate the rotated points
	private _pointLeft = [
		(_pointA select 0) + _distance * cos(_angleLeft),
		(_pointA select 1) + _distance * sin(_angleLeft),
		(_pointB select 2)  // Z remains the same as original B
	];

	private _pointRight = [
		(_pointA select 0) + _distance * cos(_angleRight),
		(_pointA select 1) + _distance * sin(_angleRight),
		(_pointB select 2)  // Z remains the same as original B
	];

	[_pointRight, _pointLeft]
};


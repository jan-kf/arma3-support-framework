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

	private _localCoordinates = [];

	{
		_localCoordinates pushBack (_x vectorDiff _nexus);
	} forEach _coordinates;

	_localCoordinates

};

YOSHI_localToReal = {
	params ["_nexus", "_coordinates"];

	private _realCoordinates = [];

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

YOSHI_getAccurateLocalRefCorners = {
	params ["_object"];

	if (isNull _object) exitWith {
		[
			[0, 0, 0],
			[0, 0, 0],
			[0, 0, 0]
		]
	};

	private _bounds = boundingBoxReal _object;
	private _bbMin = +(_bounds select 0);
	private _bbMax = +(_bounds select 1);

	private _minX = 1e12;
	private _minY = 1e12;
	private _minZ = 1e12;
	private _maxX = -1e12;
	private _maxY = -1e12;
	private _maxZ = -1e12;

	private _extX = (_bbMax select 0) - (_bbMin select 0);
	private _extY = (_bbMax select 1) - (_bbMin select 1);
	private _extZ = (_bbMax select 2) - (_bbMin select 2);

	private _padX = (_extX * 0.2) max 0.05;
	private _padY = (_extY * 0.2) max 0.05;
	private _padZ = (_extZ * 0.2) max 0.05;
	private _samples = 8;

	private _hitMinX = false;
	private _hitMaxX = false;
	private _hitMinY = false;
	private _hitMaxY = false;
	private _hitMinZ = false;
	private _hitMaxZ = false;

	private _getFirstHitOnObject = {
		params ["_startLocal", "_endLocal"];
		private _startASL = AGLToASL (_object modelToWorldVisual _startLocal);
		private _endASL = AGLToASL (_object modelToWorldVisual _endLocal);
		private _intersects = lineIntersectsSurfaces [_startASL, _endASL, objNull, objNull, true, 64, "FIRE", "GEOM"];
		private _hit = [];

		{
			if ((_x select 2) isEqualTo _object) exitWith {
				_hit = _x select 0;
			};
		} forEach _intersects;

		_hit
	};

	for "_i" from 0 to _samples do {
		for "_j" from 0 to _samples do {
			private _tY = _i / _samples;
			private _tZ = _j / _samples;
			private _y = (_bbMin select 1) + (_extY * _tY);
			private _z = (_bbMin select 2) + (_extZ * _tZ);

			private _hitASLMinX = [[(_bbMin select 0) - _padX, _y, _z], [(_bbMax select 0) + _padX, _y, _z]] call _getFirstHitOnObject;
			if ((count _hitASLMinX) > 0) then {
				private _hitLocal = _object worldToModelVisual (ASLToAGL _hitASLMinX);
				_minX = (_hitLocal select 0) min _minX;
				_hitMinX = true;
			};

			private _hitASLMaxX = [[(_bbMax select 0) + _padX, _y, _z], [(_bbMin select 0) - _padX, _y, _z]] call _getFirstHitOnObject;
			if ((count _hitASLMaxX) > 0) then {
				private _hitLocal = _object worldToModelVisual (ASLToAGL _hitASLMaxX);
				_maxX = (_hitLocal select 0) max _maxX;
				_hitMaxX = true;
			};
		};
	};

	for "_i" from 0 to _samples do {
		for "_j" from 0 to _samples do {
			private _tX = _i / _samples;
			private _tZ = _j / _samples;
			private _x = (_bbMin select 0) + (_extX * _tX);
			private _z = (_bbMin select 2) + (_extZ * _tZ);

			private _hitASLMinY = [[_x, (_bbMin select 1) - _padY, _z], [_x, (_bbMax select 1) + _padY, _z]] call _getFirstHitOnObject;
			if ((count _hitASLMinY) > 0) then {
				private _hitLocal = _object worldToModelVisual (ASLToAGL _hitASLMinY);
				_minY = (_hitLocal select 1) min _minY;
				_hitMinY = true;
			};

			private _hitASLMaxY = [[_x, (_bbMax select 1) + _padY, _z], [_x, (_bbMin select 1) - _padY, _z]] call _getFirstHitOnObject;
			if ((count _hitASLMaxY) > 0) then {
				private _hitLocal = _object worldToModelVisual (ASLToAGL _hitASLMaxY);
				_maxY = (_hitLocal select 1) max _maxY;
				_hitMaxY = true;
			};
		};
	};

	for "_i" from 0 to _samples do {
		for "_j" from 0 to _samples do {
			private _tX = _i / _samples;
			private _tY = _j / _samples;
			private _x = (_bbMin select 0) + (_extX * _tX);
			private _y = (_bbMin select 1) + (_extY * _tY);

			private _hitASLMinZ = [[_x, _y, (_bbMin select 2) - _padZ], [_x, _y, (_bbMax select 2) + _padZ]] call _getFirstHitOnObject;
			if ((count _hitASLMinZ) > 0) then {
				private _hitLocal = _object worldToModelVisual (ASLToAGL _hitASLMinZ);
				_minZ = (_hitLocal select 2) min _minZ;
				_hitMinZ = true;
			};

			private _hitASLMaxZ = [[_x, _y, (_bbMax select 2) + _padZ], [_x, _y, (_bbMin select 2) - _padZ]] call _getFirstHitOnObject;
			if ((count _hitASLMaxZ) > 0) then {
				private _hitLocal = _object worldToModelVisual (ASLToAGL _hitASLMaxZ);
				_maxZ = (_hitLocal select 2) max _maxZ;
				_hitMaxZ = true;
			};
		};
	};

	if (!_hitMinX) then {_minX = _bbMin select 0;};
	if (!_hitMaxX) then {_maxX = _bbMax select 0;};
	if (!_hitMinY) then {_minY = _bbMin select 1;};
	if (!_hitMaxY) then {_maxY = _bbMax select 1;};
	if (!_hitMinZ) then {_minZ = _bbMin select 2;};
	if (!_hitMaxZ) then {_maxZ = _bbMax select 2;};

	[
		[_maxX, _minY, _minZ],
		[_minX, _maxY, _minZ],
		[_minX, _minY, _maxZ]
	]
};

YOSHI_getStableLiftCorners = {
	params ["_object", ["_aboveComPct", 0.55], ["_pullInPct", 0.03]];

	if (isNull _object) exitWith {
		[
			[0, 0, 0],
			[0, 0, 0],
			[0, 0, 0],
			[0, 0, 0]
		]
	};

	private _refs = [_object] call YOSHI_getAccurateLocalRefCorners;
	private _bounds = [_refs] call YOSHI_refCornersToBounds;

	private _min = _bounds select 0;
	private _max = _bounds select 1;

	private _minX = _min select 0;
	private _minY = _min select 1;
	private _minZ = _min select 2;
	private _maxX = _max select 0;
	private _maxY = _max select 1;
	private _maxZ = _max select 2;

	private _extX = _maxX - _minX;
	private _extY = _maxY - _minY;
	private _extZ = _maxZ - _minZ;

	private _centerLocal = (([_object] call YOSHI_getCenterOfMass) select 1);

	private _z = (_centerLocal select 2) + (_extZ * _aboveComPct);

	private _pullX = (_extX * _pullInPct) min ((_extX * 0.5) - 0.001);
	private _pullY = (_extY * _pullInPct) min ((_extY * 0.5) - 0.001);
	_pullX = _pullX max 0;
	_pullY = _pullY max 0;

	[
		[_maxX - _pullX, _minY + _pullY, _z],
		[_maxX - _pullX, _maxY - _pullY, _z],
		[_minX + _pullX, _maxY - _pullY, _z],
		[_minX + _pullX, _minY + _pullY, _z]
	]
};


YOSHI_refCornersToBounds = {
	params ["_refs"];

	private _xRef = _refs select 0;
	private _yRef = _refs select 1;
	private _zRef = _refs select 2;

	private _minX = (_yRef select 0) min (_zRef select 0);
	private _minY = (_xRef select 1) min (_zRef select 1);
	private _minZ = (_xRef select 2) min (_yRef select 2);

	private _maxX = _xRef select 0;
	private _maxY = _yRef select 1;
	private _maxZ = _zRef select 2;

	[
		[_minX, _minY, _minZ],
		[_maxX, _maxY, _maxZ]
	]
};

YOSHI_boundsToSize = {
	params ["_bounds"];
	private _min = _bounds select 0;
	private _max = _bounds select 1;

	[
		(_max select 0) - (_min select 0),
		(_max select 1) - (_min select 1),
		(_max select 2) - (_min select 2)
	]
};


YOSHI_FLING_THING = { 
	params ["_object", "_target", ["_verticalOffset", 0], ["_dropHeight", 1000], ["_maxHorizontalSpeed", 60]]; 

	private _p0 = getPosASL _object; 
	private _p1 = getPosASL _target; 

	private _dx = (_p1 select 0) - (_p0 select 0); 
	private _dy = (_p1 select 1) - (_p0 select 1); 
	private _dz = (_p1 select 2) - (_p0 select 2); 

	private _distXY = sqrt (_dx*_dx + _dy*_dy); 
	private _g = 9.81; 

	private _t = (_distXY / (_maxHorizontalSpeed max 0.001)) max 0.3; 

	private _vz = (_dz / _t) + (0.5 * _g * _t); 

	if (_dz <= -_dropHeight) then { 
		private _tDrop = sqrt ((2 * (-_dz)) / _g); 
		_t = (_tDrop max 0.3); 
		_vz = 0; 
	}; 

	private _vx = _dx / (_t max 0.001); 
	private _vy = _dy / (_t max 0.001); 

	_object setVelocity [_vx, _vy, _vz];

	[_object, _verticalOffset] call YOSHI_safeFallV2;

}; 


YOSHI_safeFallV2 = {
	params ["_thing", ["_verticalOffset", 0], ["_deployAlt", 200]];
	[_thing, _verticalOffset, _deployAlt] spawn {

		params ["_obj", "_verticalOffset", "_deployAlt"];


		waitUntil {sleep 0.1; ((getPosATL _obj) select 2) < _deployAlt};

		smokeGrenade = "SmokeShellGreen" createVehicle (getPosASL _obj);

		smokeGrenade attachTo [_obj, [0, 0, 0]];

		_para = "B_Parachute_02_F";

		_velocity = (velocity _obj); 

		_chute1 = createVehicle [_para, [0,0,0], [], 0, "CAN_COLLIDE"];

		_chute1 attachTo [_obj, [0, 0, 0]];
		detach _chute1;
		_chute1 setVelocity _velocity;

		_obj attachTo [_chute1, [0, 0, _verticalOffset]];

		
	};
};

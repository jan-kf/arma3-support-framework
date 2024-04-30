
params ["_container"];

private _checkHeight = {
	params ["_item", "_conZPos", "_conHeight", "_rotationalOffset"];
	private _itemPosZ = (getPosATL _item) select 2;
	// param _rotationalDelta = -_rotationalOffset + 1; // ?

	if (_rotationalOffset > 0) then {
		((_conZPos + (_conHeight * _rotationalOffset)) > _itemPosZ) && (_conZPos < _itemPosZ)
	} else {
		(_conZPos > _itemPosZ) && (_conZPos + (_conHeight * _rotationalOffset) < _itemPosZ)
	};
};

while {true} do {

	private _objectsNearby = nearestObjects [_container, [], 10];
	private _boundingBox = boundingBoxReal _container;
	private _size = [((_boundingBox select 1) select 0), ((_boundingBox select 1) select 1), ((_boundingBox select 1) select 2)]; 
	private _center = getPosATL _container; 
	private _dir = direction _container;
	private _rotationalOffset =  ((vectorUp _container) select 2);
	private _height = (abs (((_boundingBox select 1) select 2)))*2;
	private _conZPos = _center select 2;	


	private _objectsToAttach = _objectsNearby select {
		!(_x isKindOf "Man") && 
		( getMass _x < 18000) && 
		( getMass _x > 0) && 
		(_x != _container) && 
		(
			((getPosATL _x) inArea [_center, _size select 0, _size select 1, _dir, true]) && ([_x, _conZPos, _height, _rotationalOffset] call _checkHeight)
		)
	};


	{
		private _isCar = _x isKindOf "Car";
		if (!(_x in (attachedObjects _container)) && (isNull attachedTo _x) && (!_isCar || (_isCar && !(isEngineOn _x)))) then {

			private _objectToAttach = _x; 
			private _targetObject = _container; 
			private _dirObjectToAttach = getDir _objectToAttach;
			private _dirTargetObject = getDir _targetObject;
			private _relativeDir = _dirObjectToAttach - _dirTargetObject;
			_objectToAttach attachTo [_targetObject];
			_objectToAttach setDir ( _dirObjectToAttach - _dirTargetObject);

			
		};
		if (_isCar && (isEngineOn _x)) then {
			detach _x;
		}
	} forEach _objectsToAttach;

	{
		if (!(_x in _objectsToAttach)) then {
			detach _x;
		}
	} forEach (attachedObjects _container);

	hint format["%1 | height: %3 | %2", time, (attachedObjects _container), _height];
	sleep 1; 
};

	


	private _vectorDir = vectorDir _x;
			private _vectorUp = vectorUp _x;
			_x attachTo [_container]; 
			sleep 0.5;
			_x setVectorDirAndUp [_vectorDir, _vectorUp];
			hint format["%1 | %2 | %3 | %4 | %5", time, (attachedObjects _container), _vectorDir, _vectorUp, _objectsToAttach];


// _container = _this;
// private _boundingBox = boundingBoxReal _container; 

// private _size = [((_boundingBox select 1) select 0), ((_boundingBox select 1) select 1)]; 
// private _center = getPosASL _container; 
// private _dir = direction _container;

// hint str([_size, _dir]);


// private _objectsNearby = nearestObjects [_this, [], 10];
// private _array = [];
// {_array pushBack [_x, ]} forEach _objectsNearby;
// hint str(_array);


// Function to compute dynamic area parameters based on object orientation
getDynamicAreaParameters = {
    params ["_object"];
    
    private _center = AGLToASL (_object modelToWorld [0,0,0]);
    private _boundingBox = boundingBoxReal _object;
    private _min = _boundingBox select 0;
    private _max = _boundingBox select 1;
    private _sizeVector = _max vectorDiff _min;
    private _width = _sizeVector select 0;
    private _length = _sizeVector select 1;
    private _height = _sizeVector select 2;

    private _upVector = vectorUp _object;
    private _dirVector = vectorDir _object;
    private _angle = ((_dirVector select 1) atan2 (_dirVector select 0));
	private _a = 0;
	private _b = 0;
	private _heightDimension = 0;
	
    if (abs (_upVector select 2) > abs (_upVector select 0) && abs (_upVector select 2) > abs (_upVector select 1)) then {
        _heightDimension = _height;
        _a = _width / 2;
        _b = _length / 2;
    } else {
        if (abs (_upVector select 0) > abs (_upVector select 1)) then {
            _heightDimension = _width;
            _a = _height / 2;
            _b = _length / 2;
        } else {
            _heightDimension = _length;
            _a = _width / 2;
            _b = _height / 2;
        }
    };
	private _orange = "Land_Orange_01_NoPop_F" createVehicle [0,0,0];
    _orange enableSimulation false;
	_orange setPosASL _center;
	private _top = "Land_Orange_01_NoPop_F" createVehicle [0,0,0];
    _top enableSimulation false;
	_top setPosASL [_center select 0, _center select 1, (_center select 2) + (_heightDimension/2)];
	private _bottom = "Land_Orange_01_NoPop_F" createVehicle [0,0,0];
    _bottom enableSimulation false;
	_bottom setPosASL [_center select 0, _center select 1, (_center select 2) - (_heightDimension/2)];

    [_center, _a, _b, _angle, _heightDimension]
};

private _areaParams = [_this] call getDynamicAreaParameters;
hint format ["Center: %1, a (half-width): %2, b (half-length): %3, Angle: %4, Height: %5", _areaParams select 0, _areaParams select 1, _areaParams select 2, _areaParams select 3, _areaParams select 4];
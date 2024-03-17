
params ["_container"];

while {true} do {

	private _objectsNearby = nearestObjects [_container, [], 10];
	private _boundingBox = boundingBoxReal _container;
	private _size = [((_boundingBox select 1) select 0), ((_boundingBox select 1) select 1)]; 
	private _center = getPosASL _container; 
	private _dir = direction _container;
	


	private _objectsToAttach = _objectsNearby select {!(_x isKindOf "Man") && ( getMass _x < 2000) && ( getMass _x > 0) && (_x != _container) && (_x inArea [_center, _size select 0, _size select 1, _dir, true])};


	{
		private _isCar = _x isKindOf "Car";
		if (!(_x in (attachedObjects _container)) && (isNull attachedTo _x) && (!_isCar || (_isCar && !(isEngineOn _x)))) then {
			private _vectorDir = vectorDir _x;
			private _vectorUp = vectorUp _x;
			_x attachTo [_container]; 
			_x setVectorDirAndUp [_vectorDir, _vectorUp];
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

	hint format["%1 | %2", time, (attachedObjects _container)];

	sleep 1; 
};



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
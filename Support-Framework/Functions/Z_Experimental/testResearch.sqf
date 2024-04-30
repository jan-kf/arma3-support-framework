
params ["_container"];

private _getDir = {
	private _object=_this select 0;
	private _vehicle=_this select 1;
	private _dir=0;
	_dir=(getDir _object)-(getDir _vehicle);
	_dir
};

private _setTilt = {
	private _object=_this select 0;
	private _roll=_this select 1;
	if!(local _object)exitWith{};
	private _yaw=0;
	private _pitch=0;
	_object setVectorDirAndUp[
		[sin _yaw * cos _pitch,cos _yaw * cos _pitch,sin _pitch],
		[[sin _roll,-sin _pitch,cos _roll * cos _pitch],-_yaw]call BIS_fnc_rotateVector2D
	];
	_roll
};

private _setDirRemote = {
	private _object=_this select 0;
	private _dir=_this select 1;
	if!(local _object)exitWith{};
	private _tilt=0;
	if((count _this)>2)then{_tilt=_this select 2};
	_object setDir _dir;
	if(_tilt==0)exitWith{};
	[_object,_tilt]remoteExecCall["_setTilt"];
};

private _setDir = {
	private _object=_this select 0;
	private _dir=_this select 1;
	private _tilt=0;
	if((count _this)>2)then{_tilt=_this select 2};
	[_object,_dir,_tilt]remoteExec["_setDirRemote"];
};

private _surfacePos = {
	private _object=_this;
	private _object2=objNull;
	private _pos=getPosASL _object;
	private _height=.5;
	private _terrain=FALSE;
	if(_object isKindOf"StaticWeapon")then{_height=2};
	_pos=[_pos select 0,_pos select 1,(_pos select 2)+_height];
	private _pos2=[_pos select 0,_pos select 1,(_pos select 2)-10];
	private _out=lineIntersectsSurfaces[_pos,_pos2,_object,player,TRUE,1,"VIEW","GEOM",TRUE];
	_pos2=(_out select 0)select 0;
	_pos2=[_pos2 select 0,_pos2 select 1,(_pos2 select 2)];
	_object2=(_out select 0)select 2;
	if(isNull((_out select 0)select 2))then{_terrain=TRUE};
	if(_object2==player)then{_object2=objNull};
	if(isNull _object2)then{_object2=_object};
	[_pos2,_object2,_terrain]
};

while {true} do {

	private _objectsNearby = nearestObjects [_container, [], 10];
	private _boundingBox = boundingBoxReal _container;
	private _size = [((_boundingBox select 1) select 0), ((_boundingBox select 1) select 1), ((_boundingBox select 1) select 2)]; 
	private _center = getPosASL _container; 
	private _dir = direction _container;
	


	private _objectsToAttach = _objectsNearby select {
		!(_x isKindOf "Man") && 
		( getMass _x < 18000) && 
		( getMass _x > 0) && 
		(_x != _container) && 
		((getPosATL _x) inArea [_center, _size select 0, _size select 1, _dir, true])
	};


	{
		private _isCar = _x isKindOf "Car";
		if (!(_x in (attachedObjects _container)) && (isNull attachedTo _x) && (!_isCar || (_isCar && !(isEngineOn _x)))) then {

			private _objectToAttach = _x; 
			private _targetObject = _container; 

			private _tilt=(_objectToAttach call BIS_fnc_getPitchBank)select 1;

			private _dir=[_objectToAttach, _targetObject] call _getDir;

			private _out=_objectToAttach call _surfacePos;

			_pos=_out select 0;

			_objectToAttach setPosASL _pos;
			[_objectToAttach,_targetObject]remoteExecCall["disableCollisionWith"];
			_objectToAttach attachTo[_targetObject];
			[_objectToAttach,_dir,_tilt] call _setDir;
		
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
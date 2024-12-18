_thing = _this;

_boxPos = getPosATL _thing;
_targetPos = getPosATL chamberlain;

_gravity = 9.81;

_distance = _boxPos distance2D _targetPos;

L = 50;
d0 = 1000; 
k = 0.003; 

_timeOfFlight = L / (1 + exp(-k * (_distance - d0)));

_initialVelocityX = ((_targetPos select 0) - (_boxPos select 0)) / _timeOfFlight;
_initialVelocityY = ((_targetPos select 1) - (_boxPos select 1)) / _timeOfFlight;
_initialVelocityZ = ((_targetPos select 2) - (_boxPos select 2)) / _timeOfFlight + 0.5 * _gravity * _timeOfFlight;

_velocity = [_initialVelocityX, _initialVelocityY, _initialVelocityZ];

_thing setVelocity _velocity;

[_thing, _timeOfFlight] spawn {

	params ["_obj", "_delay"];

	getObjectHeight = {
		params ["_object"];
		_boundingBox = boundingBox _object;
		_minZ = (_boundingBox select 0) select 2;
		_maxZ = (_boundingBox select 1) select 2;
		_height = _maxZ - _minZ;
		_height
	};

	if (_delay > 5) then {
		sleep (_delay - 1.5);

		_para = "B_Parachute_02_F";

		_velocity = (velocityModelSpace _obj) vectorMultiply 0.5;


		_dropPos1 = getpos _obj;

		_chute1 = createVehicle [_para, _dropPos1, [], 0, "CAN_COLLIDE"];

		_chute1 setVelocity _velocity;

		_offset = ([_obj] call getObjectHeight)/2;

		_obj attachTo [_chute1, [0, 0, _offset]];

	};
};



/////////////////////////


_nearbyObjects = nearestObjects [getPosATL _this, [], 1];

[_nearbyObjects] spawn {
	params ["_nearbyObjects"];
{
	_this = _x;
	_boxPos = getPosATL _this;
_targetPos = getPosATL chamberlain;

_gravity = 9.81;

_distance = _boxPos distance2D _targetPos;

L = 50;
d0 = 1000; 
k = 0.003; 

_timeOfFlight = L / (1 + exp(-k * (_distance - d0)));

_initialVelocityX = ((_targetPos select 0) - (_boxPos select 0)) / _timeOfFlight;
_initialVelocityY = ((_targetPos select 1) - (_boxPos select 1)) / _timeOfFlight;
_initialVelocityZ = ((_targetPos select 2) - (_boxPos select 2)) / _timeOfFlight + 0.5 * _gravity * _timeOfFlight;

_velocity = [_initialVelocityX, _initialVelocityY, _initialVelocityZ];

_this setVelocity _velocity;

[_this, chamberlain, _timeOfFlight] spawn {

	params ["_obj", "_target", "_delay"];

	getObjectHeight = {
		params ["_object"];
		_boundingBox = boundingBox _object;
		_minZ = (_boundingBox select 0) select 2;
		_maxZ = (_boundingBox select 1) select 2;
		_height = _maxZ - _minZ;
		_height
	};

	_initSpeed = vectorMagnitude (velocityModelSpace _obj);
	hint str(_initSpeed);

	if (_delay > 5) then {
		_delta = 1;
		sleep (_delay - _delta);
		hint str(_delta);

		_para = "B_Parachute_02_F";

		_velocity = (velocityModelSpace _obj) vectorMultiply 0.3;

		_objectPos = getPosATL _obj; 
		_targetPos = getPosATL _target;
		 
		_speed = vectorMagnitude _velocity; 
		
		_direction = _targetPos vectorDiff _objectPos;
		_directionNormalized = vectorNormalized _direction;

		_newVelocity = _directionNormalized vectorMultiply _speed;

		_dropPos1 = getpos _obj;

		_chute1 = createVehicle [_para, _dropPos1, [], 0, "CAN_COLLIDE"];

		_chute1 setVelocity _newVelocity;

		_offset = ([_obj] call getObjectHeight)/2;

		_obj attachTo [_chute1, [0, 0, _offset]];

	};
};
sleep 1;
} forEach _nearbyObjects;
};

/////////////////////


// Send an arty shell anywhere:

_ex = createVehicle ["Sh_155mm_AMOS", (getPosATL _this), [], 0, "CAN_COLLIDE"];

_thing = _ex; 
 
_boxPos = getPosATL _thing; 
_targetPos = getPosATL chamberlain; 
 
_gravity = 9.81; 
 
_distance = _boxPos distance2D _targetPos; 
 
L = 50; 
d0 = 1000;  
k = 0.003;  
 
_timeOfFlight = L / (1 + exp(-k * (_distance - d0))); 
 
_initialVelocityX = ((_targetPos select 0) - (_boxPos select 0)) / _timeOfFlight; 
_initialVelocityY = ((_targetPos select 1) - (_boxPos select 1)) / _timeOfFlight; 
_initialVelocityZ = ((_targetPos select 2) - (_boxPos select 2)) / _timeOfFlight + 0.5 * _gravity * _timeOfFlight; 
 
_velocity = [_initialVelocityX, _initialVelocityY, _initialVelocityZ]; 
 
_thing setVelocity _velocity;





_ex = createVehicle ["GrenadeHand", (getPosATL _this), [], 0, "CAN_COLLIDE"];

_thing = _ex; 
 
_boxPos = getPosATL _thing; 
_targetPos = getPosATL chamberlain; 
 
_gravity = 9.81; 
 
_distance = _boxPos distance2D _targetPos; 
 
L = 50; 
d0 = 1000;  
k = 0.003;  
 
_timeOfFlight = L / (1 + exp(-k * (_distance - d0))); 
 
_initialVelocityX = ((_targetPos select 0) - (_boxPos select 0)) / _timeOfFlight; 
_initialVelocityY = ((_targetPos select 1) - (_boxPos select 1)) / _timeOfFlight; 
_initialVelocityZ = ((_targetPos select 2) - (_boxPos select 2)) / _timeOfFlight + 0.5 * _gravity * _timeOfFlight; 
 
_velocity = [_initialVelocityX, _initialVelocityY, _initialVelocityZ]; 
 
_thing setVelocity _velocity;
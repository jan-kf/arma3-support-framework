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

[_this, _timeOfFlight] spawn {

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
		sleep (_delay - 1);

		_para = "B_Parachute_02_F";

		_velocity = (velocityModelSpace _obj) vectorMultiply 0.5;
		hint str(_velocity);

		_dropPos1 = getpos _obj;

		_chute1 = createVehicle [_para, _dropPos1, [], 0, "CAN_COLLIDE"];

		_chute1 setVelocity _velocity;

		_offset = ([_obj] call getObjectHeight)/2;

		_obj attachTo [_chute1, [0, 0, _offset]];

	};
};

hint str(_timeOfFlight);
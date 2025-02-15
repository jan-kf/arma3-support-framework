YOSHI_activateInstantKill = {
	params ["_admin"];

	YOSHI_instantKillThread = [_admin] spawn {
		params ["_adminThread"];

		_radius = 100; 

		[_adminThread, ["activatingInstantKill", 500, 1]] remoteExec ["say3D"];
		sleep 1.5;

		if (_adminThread isKindOf "B_UGV_9RIFLES_F") then {
			_adminThread setObjectTextureGlobal [0, "9Rifles\Data\Vehicles\stompy_ext_instantKill.paa"];
		};

		while {alive _adminThread} do {
			_allUnits = _adminThread nearEntities ["Man", _radius];
			_allVics = _adminThread nearEntities ["AllVehicles", _radius];

			{
				{_allUnits pushBack _x} forEach crew _x;
			} forEach _allVics;
			
			_hostiles = _allUnits select { 
				(side _x) isNotEqualTo (side _adminThread) && 
				(side _x) isNotEqualTo civilian && 
				alive _x;
			};

			{ 
				_pos = (getPosASL _adminThread); 
				_gunPos = _pos vectorAdd [0,0,2]; 

				_enPos = eyePos _x;
				_modifier = [0,0,0];
				_hits = lineIntersectsSurfaces [_gunPos, _enPos, objNull, objNull, true, 3, "FIRE", "GEOM"];
				if ((count _hits) > 0) then {
					 
					private _hitCalculations = 0;
					{
						_hitObj = (_x select 2);
						// Check CfgVehicles properties
						private _armor = getNumber (configFile >> "CfgVehicles" >> typeOf _hitObj >> "armor");

						_hitCalculations = _hitCalculations + _armor;
					} forEach _hits;
					
					if (_hitCalculations < 2000) then {
						_isInVic = (vehicle _x != _x);

						_projectile = "B_127x108_APDS";
						if (_isInVic) then {
							_projectile = "B_40mm_APFSDS";
						};

						// if ((vehicle _x) isKindof "Air") then {
						// 	_projectile = "Missile_AA_04_F";
						// 	_ex = createVehicle [_projectile, _gunPos, [], 0, "NONE"];
						// 	_ex setVectorDirAndUp [[0,0,1],[0,1,0]];
						// 	_ex setMissileTarget (vehicle _x);

						// };
						_ex = createVehicle [_projectile, [0,0,0], [], 0, "CAN_COLLIDE"];
						_ex setPosASL _gunPos; 

						_direction = _gunPos vectorFromTo (_enPos vectorAdd _modifier);  
						_velocity = _direction vectorMultiply 2000; 
						_ex setVelocity _velocity;
						
					};  
				};
				
				sleep 0.1;
			
			} forEach _hostiles;

			sleep 1;

		};
		
	};

	_admin setVariable ["YOSHI_instantKillThread", YOSHI_instantKillThread, true];
};

YOSHI_deactivateInstantKill = {
	params ["_admin"];

	[_admin] spawn {
		params ["_adminThread"];

		_thread = _adminThread getVariable ["YOSHI_instantKillThread", scriptNull];

		[_adminThread, ["deactivatingInstantKill", 500, 1]] remoteExec ["say3D"];
		sleep 1.5;

		if (_adminThread isKindOf "B_UGV_9RIFLES_F") then {
			_adminThread setObjectTextureGlobal [0, "9Rifles\Data\Vehicles\stompy_ext.paa"];
		};

		terminate _thread;
	};

};


// {

// 	[_x] call YOSHI_instantKill;

// } forEach allMissionObjects "B_UGV_9RIFLES_F";


YOSHI_FLING_THING = {
	params ["_object", "_target"];

	_thing = _object;

	_boxPos = getPosASL _thing;
	_targetPos = getPosASL _target;

	_gravity = 9.81;

	_distance = _boxPos distance2D _targetPos;

	L = 50;
	d0 = 1000; 
	k = 0.003; 

	_timeOfFlight = L / (1 + exp(-k * (_distance - d0)));
	_deltaHeight = (_targetPos select 2) - (_boxPos select 2);
	_initialVelocityZ = (_deltaHeight / _timeOfFlight) + (0.5 * _gravity * _timeOfFlight);
	if (_deltaHeight < -1000) then {
		_timeOfFlight = sqrt(abs((2 * _deltaHeight) / _gravity));
		_initialVelocityZ = 0;
	};

	_initialVelocityX = ((_targetPos select 0) - (_boxPos select 0)) / _timeOfFlight;
	_initialVelocityY = ((_targetPos select 1) - (_boxPos select 1)) / _timeOfFlight;

	_velocity = [_initialVelocityX, _initialVelocityY, _initialVelocityZ];

	_thing setVelocity _velocity;

	[_thing, _timeOfFlight, _deltaHeight] spawn {

		params ["_obj", "_delay", "_deltaHeight"];

		getObjectHeight = {
			params ["_object"];
			_boundingBox = boundingBox _object;
			_minZ = (_boundingBox select 0) select 2;
			_maxZ = (_boundingBox select 1) select 2;
			_height = _maxZ - _minZ;
			_height
		};

		if (_delay > 5) then {
			if (_deltaHeight > -1000) then {
				sleep (_delay - 4.5);
				waitUntil {sleep 0.5; ((getPosASL _obj) select 2) < 300};
			} else {
				waitUntil {sleep 0.5; ((getPosASL _obj) select 2) < 200};
			};

			smokeGrenade = "SmokeShellGreen" createVehicle (getPosASL _obj);

			smokeGrenade attachTo [_obj, [0, 0, 0]];

			_para = "B_Parachute_02_F";

			_velocity = (velocityModelSpace _obj) vectorMultiply 0.5;

			_dropPos1 = getPosASL _obj;

			_chute1 = createVehicle [_para, _dropPos1, [], 0, "CAN_COLLIDE"];

			_chute1 setVelocity _velocity;

			_offset = ([_obj] call getObjectHeight)/2;

			_obj attachTo [_chute1, [0, 0, _offset]];
		};
	};
};
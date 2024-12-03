YOSHI_activateInstantKill = {
	params ["_admin"];

	YOSHI_instantKillThread = [_admin] spawn {
		params ["_adminThread"];

		_radius = 100; 

		[_adminThread, ["activatingInstantKill", 500, 1]] remoteExec ["say3D"];
		sleep 1.5;

		if (_adminThread isKindOf "B_UGV_9RIFLES_F") then {
			_adminThread setObjectTexture [0, "9Rifles\Data\Vehicles\stompy_ext_instantKill.paa"];
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
				_pos = (getPosATL _adminThread); 
				_gunPos = _pos vectorAdd [0,0,2]; 

				_isInVic = (vehicle _x != _x);

				_projectile = "B_127x99_SLAP_Tracer_Green";
				if (_isInVic) then {
					_projectile = "B_40mm_APFSDS_Tracer_Yellow";
				};

				_ex = createVehicle [_projectile, _gunPos, [], 0, "CAN_COLLIDE"]; 

				_enPos = ASLToATL(eyePos _x);
				_modifier = [0,0,0];
			
				
				_direction = _gunPos vectorFromTo (_enPos vectorAdd _modifier);  
				_velocity = _direction vectorMultiply 2000; 
				_ex setVelocity _velocity; 
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
			_adminThread setObjectTexture [0, "9Rifles\Data\Vehicles\stompy_ext.paa"];
		};

		terminate _thread;
	};

};


// {

// 	[_x] call YOSHI_instantKill;

// } forEach allMissionObjects "B_UGV_9RIFLES_F";

_obj = _this;

_initPos = getPosATL _obj;
_ex = createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]; 
_ex setVectorDirAndUp [[0,1,-10], [0,0,1]];
_ex setPosATL (_initPos vectorAdd (vectorDir _x));

(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[0,1,10], [0,0,1]];

(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[0,1,0], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[0,-1,0], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[1,0,0], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[-1,0,0], [0,0,1]];

(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[1,1,0], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[1,-1,0], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[-1,1,0], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[-1,-1,0], [0,0,1]];

(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[0,1,1], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[0,-1,1], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[1,0,1], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[-1,0,1], [0,0,1]];
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[1,1,1], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[1,-1,1], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[-1,1,1], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[-1,-1,1], [0,0,1]];

(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[1,1,-1], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[1,-1,-1], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[-1,1,-1], [0,0,1]]; //
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[-1,-1,-1], [0,0,1]];
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[0,1,-1], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[0,-1,-1], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[-1,0,-1], [0,0,1]]; 
(createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]) setVectorDirAndUp [[-1,0,-1], [0,0,1]];



{
    _ex = createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"];
    _ex setVectorDirAndUp [_x, [0,0,1]];
    _ex setPosATL (_initPos vectorAdd (vectorDir _ex));
} forEach [
    [0,1,0], [0,-1,0], [1,0,0], [-1,0,0],
    [1,1,0], [1,-1,0], [-1,1,0], [-1,-1,0],
    [0,1,1], [0,-1,1], [1,0,1], [-1,0,1],
    [1,1,-1], [1,-1,-1], [-1,1,-1], [-1,-1,-1],
	[0,1,10], [0,-1,-10], [1,1,1], [1,-1,1],
	[-1,1,1], [-1,-1,1], [-1,0,-1], [0,-1,-1],
	[0,1,-1] 
];

_obj = _this;

_initPos = getPosASL _obj;
{ 
    _ex = createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"]; 
    _ex setVectorDirAndUp [_x, [0,0,1]]; 
    _ex setPosASL (_initPos vectorAdd (vectorDir _ex)); 
} forEach [ 
    [-1,-1,-1], [-1,-1,0], [-1,-1,1], 
    [-1,0,-1], [-1,0,0], [-1,0,1], 
    [-1,1,-1], [-1,1,0], [-1,1,1], 
    [0,-1,-1], [0,-1,0], [0,-1,1], 
    [0,0,-1], [0,0,0], [0,0,1], 
    [0,1,-1], [0,1,0], [0,1,1], 
    [1,-1,-1], [1,-1,0], [1,-1,1], 
    [1,0,-1], [1,0,0], [1,0,1], 
    [1,1,-1], [1,1,0], [1,1,1],
	[0,1,10], [0,-1,-10] 
];

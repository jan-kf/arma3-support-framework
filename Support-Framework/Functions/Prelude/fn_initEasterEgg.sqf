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
				_pos = (getPosASL _adminThread); 
				_gunPos = _pos vectorAdd [0,0,2]; 

				_isInVic = (vehicle _x != _x);

				_projectile = "B_127x99_SLAP_Tracer_Green";
				if (_isInVic) then {
					_projectile = "B_40mm_APFSDS_Tracer_Yellow";
				};

				_ex = createVehicle [_projectile, [0,0,0], [], 0, "CAN_COLLIDE"];
				_ex setPosASL _gunPos; 

				_enPos = eyePos _x;
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
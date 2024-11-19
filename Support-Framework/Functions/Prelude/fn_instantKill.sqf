beans = [_this] spawn {
	params ["_admin"];
	
	_radius = 100; 
	
	
	while {true} do {
		_allUnits = _admin nearEntities ["Man", _radius];
		_allVics = _admin nearEntities ["AllVehicles", _radius];

		{
			{_allUnits pushBack _x} forEach crew _x;
		} forEach _allVics;
		
		_hostiles = _allUnits select { 
			(side _x) isNotEqualTo (side _admin) && 
			(side _x) isNotEqualTo civilian && 
			alive _x;
		};
 

		{ 
			_pos = (getPosATL _admin); 
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

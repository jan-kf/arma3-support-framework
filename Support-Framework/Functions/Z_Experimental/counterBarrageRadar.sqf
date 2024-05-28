con = [] spawn {
	_detectProjectiles = {
		private _detectedProjectiles = [];
		_projectileClasses = [
			"ShellBase", 
			"RocketBase", 
			"MissileBase", 
			"BulletBase" 
		];
		
		
		private _projectiles = radar nearObjects ["Default", 1000]; 
		
		{
			if ((alive _x) && (speed _x > 0)) then {
				_detectedProjectiles pushBack _x;
			};
		} forEach _projectiles;
			

		_detectedProjectiles
	};

    while {true} do {
        private _projectiles = call _detectProjectiles;
        
		if (count _projectiles > 0) then {
			{
				radar sideChat format ["Detected projectile: %1 at position %2", typeOf _x, getPos _x];
			} forEach _projectiles;

			radar say3D ["IncomingKlaxon", 200, 1];
			sleep 7.4;
		} else {
			sleep 1;
		};
    };
};


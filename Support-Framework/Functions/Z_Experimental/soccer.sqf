YOSHI_soccer_thread = [_this] spawn {
	params ["_soccer"];
	private _ball = _soccer; 
	private _kickDistance = 0.5;  
	
	while {true} do { 
		{ 
			if (_x distance _ball < _kickDistance) then { 
				private _direction = ((getPosATL _x) vectorFromTo (getPosATL _ball)); 
				private _kickVector = _direction vectorMultiply (abs ((speed _x)/2)); 
				private _ballVelocity = velocity _ball;
				_ball setVelocity (_ballVelocity vectorAdd _kickVector); 
			}; 
		} forEach allPlayers; 
	
		sleep 0.1; 
	}; 
};

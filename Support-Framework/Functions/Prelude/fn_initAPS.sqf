YOSHI_getPosTop = {  
	params ["_obj"];  
	
	_loc = getPosASL _obj;  
	
	_locAbove = _loc vectorAdd [0,0,10];  
	
	_hits = lineIntersectsSurfaces [_locAbove, _loc, objNull, objNull, true, 10, "FIRE", "GEOM"];  
	if ((count _hits) > 0) then {  
	_hit = _hits select 0;  
	_dist = (_hit select 0) select 2;  
	_loc = (_hit select 0);  
	};  
	_loc  
};


YOSHI_getFrontPosition = {
    params ["_projectile", "_distanceAhead"];

    private _currentPos = getPosATL _projectile; 
    private _velocity = velocity _projectile;
    private _directionNormalized = vectorNormalized _velocity; 

    private _frontPos = _currentPos vectorAdd (_directionNormalized vectorMultiply _distanceAhead);

    _frontPos
};


YOSHI_detectRockets = { 
    params ["_vehicle", ["_charges", 40], ["_range", -1], ["_interval", 0.05], ["_cooldown", 0.1]];
	// if (isServer) exitWith {};
	_thread = _vehicle getVariable ["YOSHI_APS_Thread", objNull];
	if (isNull _thread) exitWith {}; // prevent multiple APS on one vehicle

	if (_range == -1) then{
		_boundingBox = boundingBoxReal _vehicle;
		_range = ((_boundingBox select 0) distance (_boundingBox select 1)) * 2;
	};

	_vehicle setVariable ["APS_Charges", _charges, true];
    
	while {(alive _vehicle) && ((_vehicle getVariable ["APS_Charges", 0]) > 0)} do { 
        private _projectiles = nearestObjects [_vehicle, ["MissileBase", "RocketBase"], _range];
		private _uavs = allUnitsUAV select { ((_x distance _vehicle) <= _range) && (_x isKindOf "Air") }; 

        { 	
			private _relativeDir = _x getRelDir _vehicle;

			if ((_relativeDir < 30) || (_relativeDir > 330)) then {
				_stop = [_x, 1] call YOSHI_getFrontPosition;
				_charge = createVehicle ["Land_Orange_01_F", _stop, [], 0, "CAN_COLLIDE"];	
						
	
				private _pos = getPosATL _x;
				[[_vehicle, _pos], YOSHI_beamVic2Pos] remoteExec ["spawn"];
				_vehicle say3D ["ApsHit", 200, 1];
				
				_chargesRemaining = _vehicle getVariable ["APS_Charges", 0];
				_vehicle setVariable ["APS_Charges", _chargesRemaining - 1, true];
				sleep 0.01;
				deleteVehicle _x;
				deleteVehicle _charge;

				sleep _cooldown;
			};
			
        } forEach _projectiles;

		{ 
			private _isHit = _x getVariable ["YOSHI_APS_HIT", false];
			if (speed _x > 40 && !_isHit) then {						
				_vehicle say3D ["ApsDrone", 200, 1];

	
				private _pos = getPosATL _x;
				[[_vehicle, _pos, 2, [0, 1, 1, 1], 15], YOSHI_beamVic2Pos] remoteExec ["spawn"];

				_x removeAllEventHandlers "Killed";
				_x removeAllEventHandlers "Hit";
				_x removeAllEventHandlers "HitPart";
				_x removeAllEventHandlers "HandleDamage";
				_x removeAllEventHandlers "Dammaged";
				_x removeAllEventHandlers "Deleted";
				_x removeAllEventHandlers "EpeContact";
				_x removeAllEventHandlers "EpeContactStart";
				_x removeAllEventHandlers "EpeContactEnd";
				_x removeAllEventHandlers "Fired";
				_x removeAllEventHandlers "LandedStopped";
				_x removeAllEventHandlers "Landing";
				_x removeAllEventHandlers "LandedTouchDown";

				_x setDamage [1, false];

				_x setVariable ["YOSHI_APS_HIT", true, true];

				sleep _cooldown;
			};
			
        } forEach _uavs;

        sleep _interval; 
    }; 
};
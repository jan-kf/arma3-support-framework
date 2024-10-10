params ["_logic", "_id", "_params"];


private _chargeCount = _logic getVariable ["ChargeCount", 40];
private _range = _logic getVariable ["Range", -1];
private _interval = _logic getVariable ["Interval", 0.05];
private _cooldown = _logic getVariable ["Cooldown", 0.1];
private _syncedVehicles = synchronizedObjects _logic;

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

YOSHI_beamA2B = {
	params ["_posA", "_posB"];
    
	drawLine3D [_posA, _posB, [1, 0, 0, 1], 20];
};

YOSHI_beamVic2Pos = {
	params ["_vic", "_pos"];

	_count = 5;

	while {(alive _vic) && (_count > 0)} do {
		_topOfVic = ASLToATL ([_vic] call YOSHI_getPosTop); 
		[_topOfVic, _pos] call YOSHI_beamA2B;
		sleep 0.05;
		_count = _count - 1;
	};

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
	if (isServer) exitWith {};
	if (_range == -1) then{
		_boundingBox = boundingBoxReal _vehicle;
		_range = ((_boundingBox select 0) distance (_boundingBox select 1)) * 2;
	};

	_vehicle setVariable ["APS_Charges", _charges, true];
    
	while {(alive _vehicle) && ((_vehicle getVariable ["APS_Charges", 0]) > 0)} do { 
        private _projectiles = nearestObjects [_vehicle, ["MissileBase", "RocketBase"], _range]; 
        { 
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
			
        } forEach _projectiles; 
        sleep _interval; 
    }; 
};

{
	_thread = [_x, _chargeCount, _range, _interval, _cooldown] spawn YOSHI_detectRockets;

	_x setVariable ["YOSHI_APS_Thread", _thread];
} forEach _syncedVehicles;

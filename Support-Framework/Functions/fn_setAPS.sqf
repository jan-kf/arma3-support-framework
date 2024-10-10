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

// 2.18: set the width of the beam to be easier to see
YOSHI_beamA2B = {
	params ["_posA", "_posB"];
    
	drawLine3D [_posA, _posB, [1, 0, 0, 1], 6];
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
			private _pos = getPosATL _x;

			deleteVehicle _x;			
 
			[[_vehicle, _pos], YOSHI_beamVic2Pos] remoteExec ["spawn"];

			// consider destroying the rocket, since only one exists...
			_charge = createVehicle ["ModuleAPERSMineDispenser_Mine_F", _pos, [], 0, "CAN_COLLIDE"];
			_charge setDamage 1;
			
			_chargesRemaining = _vehicle getVariable ["APS_Charges", 0];
			_vehicle setVariable ["APS_Charges", _chargesRemaining - 1, true];

			sleep _cooldown;
			
        } forEach _projectiles; 
        sleep _interval; 
    }; 
};

{
	_thread = [_x, _chargeCount, _range, _interval, _cooldown] spawn YOSHI_detectRockets;

	_x setVariable ["YOSHI_APS_Thread", _thread];
} forEach _syncedVehicles;

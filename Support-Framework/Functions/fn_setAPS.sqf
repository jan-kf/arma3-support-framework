params ["_logic", "_id", "_params"];


private _chargeCount = _logic getVariable ["ChargeCount", 40];
private _range = _logic getVariable ["Range", -1];
private _interval = _logic getVariable ["Interval", 0.05];
private _cooldown = _logic getVariable ["Cooldown", 0.1];
private _syncedVehicles = synchronizedObjects _logic;

private _detectRockets = { 
    params ["_vehicle", ["_charges", 40], ["_range", -1], ["_interval", 0.05], ["_cooldown", 0.1]];
	if (isServer) exitWith {};

	if (_range == -1) then{
		_boundingBox = boundingBoxReal _vehicle;
		_range = ((_boundingBox select 0) distance (_boundingBox select 1));
	};

	_chargesRemaining = _charges;
    
	while {(alive _vehicle) && (_chargesRemaining > 0)} do { 
        private _projectiles = nearestObjects [_vehicle, ["MissileBase", "RocketBase"], _range]; 
        { 
			private _pos = getPosATL _x;
			deleteVehicle _x;

			hint format["detected: %1", _x];

			_orange = createVehicle ["ModuleAPERSMineDispenser_Mine_F", _pos, [], 0, "CAN_COLLIDE"];
			_orange setDamage 1;
			
			_chargesRemaining = _chargesRemaining - 1;
			sleep _cooldown;

			_vehicle say3D ["apsHit", 500, 1];

        } forEach _projectiles; 
        sleep _interval; 
    }; 
};

{
	_thread = [_x, _chargeCount, _range, _interval, _cooldown] spawn _detectRockets;

	_x setVariable ["YOSHI_APS_Thread", _thread];
} forEach _syncedVehicles;

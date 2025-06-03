params ["_logic", "_id", "_params"];


private _chargeCount = _logic getVariable ["ChargeCount", 40];
private _range = _logic getVariable ["Range", -1];
private _interval = _logic getVariable ["Interval", 0.05];
private _cooldown = _logic getVariable ["Cooldown", 0.1];
private _syncedVehicles = synchronizedObjects _logic;

{
	_thread = [_x, _chargeCount, _range, _interval, _cooldown] spawn YOSHI_detectRockets;

	_x setVariable ["YOSHI_APS_Thread", _thread];
} forEach _syncedVehicles;

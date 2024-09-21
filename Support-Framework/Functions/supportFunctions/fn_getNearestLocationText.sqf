params ["_pos"];

private _locationParams = [_pos] call YOSHI_fnc_getNearestLocationParams;

private _distance = _locationParams select 0;
private _direction = _locationParams select 1;
private _name = _locationParams select 2;

if (_distance == 0) then{
	_name
} else {
	format ["%1m %2 of %3", _distance, _direction, _name]
}


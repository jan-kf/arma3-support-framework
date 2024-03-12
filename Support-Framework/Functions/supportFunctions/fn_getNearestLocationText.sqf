params ["_pos"];

private _locationParams = [_pos] call SupportFramework_fnc_getNearestLocationParams;

private _distance = _locationParams select 0;
private _direction = _locationParams select 1;
private _name = _locationParams select 2;

format ["%1m %2 of %3", _distance, _direction, _name]

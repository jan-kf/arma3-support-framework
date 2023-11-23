// posToGrid.sqf
private _posToGrid = {
	params ["_pos"];
	private _gridX = floor ((_pos select 0) / 100);
	private _gridY = floor ((_pos select 1) / 100);
	private _formattedX = if (_gridX < 10) then {format ["00%1", _gridX]} else {if (_gridX < 100) then {format ["0%1", _gridX]} else {format ["%1", _gridX]}};
	private _formattedY = if (_gridY < 10) then {format ["00%1", _gridY]} else {if (_gridY < 100) then {format ["0%1", _gridY]} else {format ["%1", _gridY]}};
	format ["%1-%2", _formattedX, _formattedY];
};
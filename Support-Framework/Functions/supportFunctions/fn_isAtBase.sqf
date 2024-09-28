params ["_object"];

private _module = YOSHI_HOME_BASE_CONFIG;
private _rawArea = _module getVariable ["objectArea", [500, 500, 0, false, 0]];

_object inArea [getPosWorld _module, _rawArea select 0, _rawArea select 1, _rawArea select 2, _rawArea select 3, _rawArea select 4]

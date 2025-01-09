params ["_object"];

private _rawArea = YOSHI_HOME_BASE_CONFIG_OBJECT get "objectArea";
private _location = YOSHI_HOME_BASE_CONFIG_OBJECT get "location";

_object inArea [_location, _rawArea select 0, _rawArea select 1, _rawArea select 2, _rawArea select 3, _rawArea select 4]

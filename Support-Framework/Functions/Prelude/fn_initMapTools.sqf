YOSHI_addMarker = {
	params ["_obj", ["_text", ""], ["_color", "ColorRed"], ["_type", "mil_dot"], ["_shape", "ICON"]];

	_markerName = format ["_USER_DEFINED YOSHI_MARKER_%1_%2_%3", str(_obj), serverTime, random 1000];
	_marker = createMarker [_markerName, _obj]; 
	_marker setMarkerShape _shape; 
	_marker setMarkerType _type;  
	_marker setMarkerColor _color;
	_marker setMarkerText _text;
	_marker setMarkerShadow false;

	_marker
};
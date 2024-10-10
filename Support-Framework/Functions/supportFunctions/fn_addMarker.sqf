params ["_obj", ["_text", ""], ["_color", "ColorRed"], ["_type", "mil_dot"], ["_shape", "ICON"]];

_markerName = format ["_USER_DEFINED YOSHI_MARKER_%1", _obj];
_marker = createMarker [_markerName, _obj]; 
_marker setMarkerShape _shape; 
_marker setMarkerType _type;  
_marker setMarkerColor _color;
_marker setMarkerText _text;
_marker setMarkerShadow false;  

_marker

params ["_obj", ["_color", "ColorRed"], ["_type", "mil_dot"], ["_shape", "ICON"]];

_markerName = format ["_USER_DEFINED YOSHI_MARKER_%1", _obj];
_marker = createMarkerLocal [_markerName, _obj]; 
_marker setMarkerShapeLocal _shape; 
_marker setMarkerTypeLocal _type;  
_marker setMarkerColor _color;
_marker setMarkerShadow false;  

_marker

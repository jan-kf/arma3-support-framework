YOSHI_addMarker = {
	params ["_obj", ["_text", ""], ["_color", "ColorRed"], ["_type", "mil_dot"], ["_shape", "ICON"], ["_size", [1,1]]];

	_markerName = format ["_USER_DEFINED YOSHI_MARKER_%1_%2_%3", str(_obj), serverTime, random 1000];
	_marker = createMarker [_markerName, _obj]; 
	_marker setMarkerShape _shape; 
	_marker setMarkerType _type;  
	_marker setMarkerColor _color;
	_marker setMarkerText _text;
	_marker setMarkerShadow false;
	_marker setMarkerSize _size;

	_marker
};


YOSHI_createIdMarker = {
	params ["_object"];

	_side = side _object;

	_text = format ["%1", groupId group _object];

	_color = "ColorUNKNOWN";
	_factionChar = "n";
	if (_side == west) then {
		_color = "ColorWEST";
		_factionChar = "b";
	}; 
	if (_side == east) then {
		_color = "ColorEAST";
		_factionChar = "o";
	}; 
	if (_side == resistance) then {
		_color = "ColorGUER";
	}; 
	if (_side == civilian) then {
		_color = "ColorCIV";
	};

	_type = "mil_dot";
	if (_object isKindOf "Car") then {
		_type = format["%1_motor_inf", _factionChar];
	};
	if (_object isKindOf "Plane") then {
		_type = format["%1_plane", _factionChar];
	};
	if (_object isKindOf "Ship") then {
		_type = format["%1_naval", _factionChar];
	};
	if (_object isKindOf "Helicopter") then {
		_type = format["%1_air", _factionChar];
	};
	if (_object isKindOf "Tank") then {
		_type = format["%1_armor", _factionChar];
	};
	if (unitIsUAV _object) then {
		_type = format["%1_uav", _factionChar];
	};
	if (_object isKindOf "StaticWeapon") then {
		_type = format["%1_installation", _factionChar];
	};
	if (_object isKindOf "StaticCannon" || [_object] call YOSHI_isArtilleryCapable) then {
		_type = format["%1_art", _factionChar];
	};
	if (_object isKindOf "StaticMortar") then {
		_type = format["%1_mortar", _factionChar];
	};

	[_object, _text, _color, _type, "ICON", [0.75, 0.75]] call YOSHI_addMarker
};


YOSHI_updateDisplayLocationMarkerLoop = {
	params ["_object"];

	private _marker = _object getVariable ["YOSHI_displayLocationDataOnMap", ""];
	if (_marker isEqualTo "" || (!alive _object)) exitWith {};

	deleteMarker _marker;

	private _newMarker = [_object] call YOSHI_createIdMarker;

	_object setVariable ["YOSHI_displayLocationDataOnMap", _newMarker, true];
}; 

YOSHI_toggleDisplayLocationDataOnMap = {
	params ["_object", ["_canMove", false]];

	private _marker = _object getVariable ["YOSHI_displayLocationDataOnMap", ""];
	private _thread = _object getVariable ["YOSHI_displayLocationDataOnMapThread", objNull];

	if (!(_marker isEqualTo "")) exitWith {
		deleteMarker _marker;
		_object setVariable ["YOSHI_displayLocationDataOnMap", "", true];
		if (!isNull _thread) then {
			terminate _thread;
			_object setVariable ["YOSHI_displayLocationDataOnMapThread", objNull, true];
		};
	};

	_marker = [_object] call YOSHI_createIdMarker;

	_object setVariable ["YOSHI_displayLocationDataOnMap", _marker, true];

	if (_canMove) then {
		_thread = [_object] spawn {
			params ["_object"];
   
			while {alive _object} do {
				[_object] call YOSHI_updateDisplayLocationMarkerLoop;
				sleep 1;
			};
			
		};
		_object setVariable ["YOSHI_displayLocationDataOnMapThread", _thread, true];
	};

};
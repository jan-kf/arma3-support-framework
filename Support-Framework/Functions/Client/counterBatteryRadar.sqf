YOSHI_mapDrawingEnabled = true;
YOSHI_projectileIdCounter = 0;
YOSHI_detectedTargets = [];
YOSHI_CBRMarkersArray = [];

YOSHI_mapProjectilesDrawTimeout = 5;
YOSHI_markerCounter = 0;
YOSHI_markerPrefix = "_USER_DEFINED YOSHI_markerNo";

YOSHI_numToTextArray = {
    params ["_number"];

	if (_number > 999000000) exitWith {["error"]};
    
    private _ones = ["", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"];
    private _teens = ["", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"];
    private _tens = ["", "ten", "twenty", "thirty", "fourty", "fifty", "sixty", "seventy", "eighty", "ninety"];
    private _hundred = "hundred";
    private _thousand = "thousand";
    private _million = "million";
    
    private _result = [];
    
    private _addWords = {
        params ["_digits", "_scale"];
        private _count = count _digits;

        if (_count > 0 && (_digits select 0) > 0) then {
            _result pushBack (_ones select (_digits select 0));
			if (_count == 3) then {
            	_result pushBack _hundred;
			};	
        };
        if (_count == 3 && ((_digits select 1) == 1) && ((_digits select 2) > 0)) then {
            _result pushBack (_teens select (_digits select 2));
        } else {
            if (_count > 1 && ((_digits select 1) > 0)) then {
                _result pushBack (_tens select (_digits select 1));
            };
            if (_count > 2 && ((_digits select 2) > 0)) then {
                _result pushBack (_ones select (_digits select 2));
            };
        };
        if (_scale != "") then {
            _result pushBack _scale;
        };
    };
    
    private _getDigits = {
        params ["_num"];
        private _digits = (str(_num) splitString "") apply {parseNumber _x};
		private _count = count _digits;
		if (_count != 3) then {
			if (_count == 2) then {
				reverse _digits;
				_digits pushBack 0;
				reverse _digits;
			};
			if (_count == 1) then {
				_digits pushBack 0;
				_digits pushBack 0;
				reverse _digits;
			};
		};
		_digits
    };
    
    private _millions = floor (_number / 1000000);
    private _thousands = floor ((_number % 1000000) / 1000);
    private _hundreds = _number % 1000;
    
    if (_millions > 0) then {
        private _millionsDigits = _millions call _getDigits;
        [_millionsDigits, _million] call _addWords;
    };
    
    if (_thousands > 0) then {
        private _thousandsDigits = _thousands call _getDigits;
        [_thousandsDigits, _thousand] call _addWords;
    };
    
    if (_hundreds > 0) then {
        private _hundredsDigits = _hundreds call _getDigits;
        [_hundredsDigits, ""] call _addWords;
    };
    
    _result = _result - [""];
    _result
};

YOSHI_predictFallTime = {
	params["_projectile"];

	private _position = getPosASL _projectile;
	private _velocity = velocity _projectile;
	private _gravity = [0,0,-9.81];
	private _time = 0;

	while {_position select 2 >= 0} do {
		_position = _position vectorAdd (_velocity vectorMultiply 0.1);
		_velocity = _velocity vectorAdd (_gravity vectorMultiply 0.1);

		_time = _time + 0.1;
	};

	round _time
};

YOSHI_predictFallPos = {
	params["_projectile"];
	
	private _position = getPosASL _projectile;
	private _velocity = velocity _projectile;
	private _gravity = [0,0,-9.81];
	private _time = 0;
	private _iterations = 0;
	
	while {_position select 2 >= 0} do {
		
		_position = _position vectorAdd (_velocity vectorMultiply 0.1);
		_velocity = _velocity vectorAdd (_gravity vectorMultiply 0.1);
		
		_time = _time + 0.1;
		_iterations = _iterations + 1;
	};	

	_position;
};

YOSHI_safeIsNull = {
    params ["_var"];

    if (_var isEqualTo false) then {
        true; // The variable is undefined (nil)
    } else {
        isNull _var; // The variable is defined, check if it's a null object
    };
};

// future plan: combine nearby targets to a single area, maybe have a size limit on the shape?
// YOSHI_drawBoundingBox = {};

YOSHI_areAllProjectilesDead = {
	params ["_arrayOfArrays"];
	_isClear = true;
	{
		private _object = _x select 1; 
		if (alive _object) then {_isClear = false}; 
	} forEach _arrayOfArrays;
	_isClear
};

YOSHI_baseMessageTime = 0;

YOSHI_handleArtilleryFire = {
	params ["_vehicle", "_targetPosition", "_shell"];

	YOSHI_detectedTargets pushBack [_targetPosition, _shell, _vehicle];

	[_shell, getPosASL _vehicle] spawn {
		params ["_shell", "_originPosition"];
		while {alive _shell} do {
			private _projectileImpactETA = _shell call YOSHI_predictFallTime;
			private _projectileImpactPosition = _shell call YOSHI_predictFallPos;

			private _hasMarker = _shell getVariable ["YOSHI_markerForShell", false];
			if (!_hasMarker) then {
				_shell setVariable ["YOSHI_markerForShell", true];
				private _targetMarker = [_projectileImpactPosition, format["ETA: %1s", _projectileImpactETA], "ColorRed", "mil_destroy"] call YOSHI_addMarker;
				private _shellMarker = [_shell, "", "ColorRed", "mil_triangle"] call YOSHI_addMarker;
				_shellMarker setMarkerDir ((getPosASL _shell) getDir _projectileImpactPosition);
				private _originMarker = [_originPosition] call YOSHI_addMarker;


				sleep 1;
				deleteMarker _targetMarker;
				deleteMarker _shellMarker;
				deleteMarker _originMarker;
				_shell setVariable ["YOSHI_markerForShell", false];
			};
		};
		
	};

	if ((serverTime - YOSHI_baseMessageTime) > 20) then {
		private _baseParams = call YOSHI_fnc_getBaseCallsign;
		private _baseCallsign = _baseParams select 0;
		private _baseName = _baseParams select 1;
		[_baseCallsign, "YOSHI_LaunchDetected"] call YOSHI_fnc_playSideRadio;
		YOSHI_baseMessageTime = serverTime;
	};
};

if(isServer) then {
	addMissionEventHandler ["ArtilleryShellFired", {
		params ["_vehicle", "_weapon", "_ammo", "_gunner", "_instigator", "_artilleryTarget", "_targetPosition", "_shell"];

		[_vehicle, _targetPosition, _shell] call YOSHI_handleArtilleryFire;
	}];
};
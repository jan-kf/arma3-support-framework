YOSHI_mapDrawingEnabled = true;
YOSHI_projectileIdCounter = 0;
YOSHI_detectedTargets = [];

YOSHI_projectileDetectionRange = (missionNamespace getVariable "YOSHI_CBR") getVariable ["DetectionRange", 5000];
YOSHI_projectileCautionRange = (missionNamespace getVariable "YOSHI_CBR") getVariable ["CautionRange", 4000];
YOSHI_projectileWarningRange = (missionNamespace getVariable "YOSHI_CBR") getVariable ["WarningRange", 2000];
YOSHI_projectileIncomingRange = (missionNamespace getVariable "YOSHI_CBR") getVariable ["IncomingRange", 500];

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


YOSHI_detectIncomingProjectiles = {
	params ["_radarVic"];
	
	private _detectedProjectiles = [];
	_projectileClasses = [
		"ShellCore",
		"Shell",
		"MissileCore",
		"Missile",
		"BombCore",
		"SubmunitionCore",
		"R_min_rf_122mm_Grad",
		"R_min_rf_122mm_Grad_fly"
	];
	
	
	private _projectiles = _radarVic nearObjects ["Default", YOSHI_projectileDetectionRange]; 

	_incomingProjectiles = _projectiles select {
		private _projectile = _x;

		private _type = typeOf _projectile;
		private _isClassAllowedAmmo = false;
		{
			if(_type isKindOf [_x, configFile >> "CfgAmmo"]) exitWith {
				_isClassAllowedAmmo = true;
			};
		} foreach _projectileClasses;		
		

		if (_isClassAllowedAmmo && (_type find "ace_frag" == -1)) then {
			true;
		} else {
			false;
		};
	};
	
	{
		_detectedProjectiles pushBack _x;
	} forEach _incomingProjectiles;
		

	_detectedProjectiles
};

YOSHI_predictFallTime = {
	params["_projectile"];

	private _position = getPosATL _projectile;
	private _velocity = velocity _projectile;
	private _gravity = [0,0,-9.81];
	private _time = 0;

	while {_position select 2 >= 0} do {
		_position = _position vectorAdd (_velocity vectorMultiply 0.1);
		_velocity = _velocity vectorAdd (_gravity vectorMultiply 0.1);

		_time = _time + 0.1;
	};

	_time
};

YOSHI_predictFallPos = {
	params["_projectile"];
	
	private _position = getPosATL _projectile;
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

YOSHI_triggerRadarScan = {
	params["_vehicle"];

	private _radarEnabled = _vehicle getVariable ["radarEnabled", false];
	
	if (alive _vehicle && _radarEnabled) then {

		private _incomingProjectiles = _vehicle call YOSHI_detectIncomingProjectiles;
		private _clearStated = _vehicle getVariable ["YOSHI_clearStated", true];
		if(count _incomingProjectiles <= 0) exitWith {
			// all clear
			if (!_clearStated) then {
				_vehicle setVariable ["YOSHI_clearStated", true];
				[_vehicle] spawn {
					params ["_vehicle"];
					sleep 2;
					_vehicle say3D ["sector", 200, 1];
					sleep 0.6;
					_vehicle say3D ["clear", 200, 1];
					sleep 0.4;
					_vehicle setVariable ["YOSHI_vicBeeped", false];
					_vehicle setVariable ["YOSHI_vicBeeping", false];
					_vehicle setVariable ["YOSHI_vicCounted", false];
					_vehicle setVariable ["YOSHI_vicCounting", false];
					_vehicle setVariable ["YOSHI_statedProjectileCount", 0];
					YOSHI_detectedTargets = []; // clear out history of targets
				};
			};
		};

		_vehicle setVariable ["YOSHI_clearStated", false];
		_incomingProjectiles apply {
			private _currentId = _x getVariable["YOSHI_projectileId", -1];
			if(_currentId == -1) then {
				_x setVariable ["YOSHI_projectileId", YOSHI_projectileIdCounter];
				YOSHI_projectileIdCounter = YOSHI_projectileIdCounter + 1;
			};
		};

		_incomingProjectiles apply {
			private _projectile = _x;
			private _allSideUnits = units (side player);
			_allSideUnits apply {
				_x reveal _projectile;
			};		
			
			private _projectilePos = getPos _projectile;		
			private _projectileHeight = (getPos _projectile) select 2;		
			private _projectileImpactETA = _projectile call YOSHI_predictFallTime;
			private _projectileImpactPosition = _projectile call YOSHI_predictFallPos;

			private _currentKnownProjectiles = YOSHI_detectedTargets;
			private _projectileId = _projectile getVariable["YOSHI_projectileId", -1];
			private _projectileIndex = _currentKnownProjectiles findIf {
				(_x select 0) isEqualTo _projectileId;
			};

			if(_projectileIndex != -1) then {
				private _currentProjectileData = _currentKnownProjectiles select _projectileIndex;

				_currentProjectileData set [2, getPos _projectile];
				_currentProjectileData set [3, _projectileImpactPosition];
				_currentProjectileData set [4, _projectileImpactETA];
				_currentProjectileData set [5, serverTime];
				_currentKnownProjectiles set [_projectileIndex, _currentProjectileData];
			} else {		
				private _projectileReportData  = [_projectileId, _projectilePos, getPos _projectile, _projectileImpactPosition, _projectileImpactETA, serverTime];
				_currentKnownProjectiles pushBack _projectileReportData;			
			};	
			_distanceFromVic = _vehicle distance2D _projectileImpactPosition;

			_projectileThreat = _vehicle getVariable["YOSHI_projectile_threat", 0];
			_spawnSound = {
				params ["_vehicle", "_projectile", "_soundName", "_sleepTime"];
				_thread = [_vehicle, _projectile, _soundName, _sleepTime] spawn {
					params ["_vehicle", "_projectile", "_soundName", "_sleepTime"];
					while {alive _projectile} do {
						_vehicle say3D [_soundName, 200, 1];
						sleep _sleepTime;
					};
					_vehicle setVariable["YOSHI_projectile_threat", 0];
				};
				_thread
			};

			_playedSound = false;

			if (!_playedSound && YOSHI_projectileIncomingRange > 0 && _distanceFromVic <= YOSHI_projectileIncomingRange && _projectileThreat < 100) then {
				_oldThread = _vehicle getVariable "YOSHI_projectile_thread";
				terminate _oldThread;

				_thread = [_vehicle, _projectile, "IncomingKlaxon", 5] call _spawnSound;
				_vehicle setVariable["YOSHI_projectile_thread", _thread];
				_vehicle setVariable["YOSHI_projectile_threat", 100];
				_projectileThreat = 100;
				_playedSound = true;
			};
			if (!_playedSound && YOSHI_projectileWarningRange > 0 && _distanceFromVic <= YOSHI_projectileWarningRange && _projectileThreat < 50) then {
				_oldThread = _vehicle getVariable "YOSHI_projectile_thread";
				terminate _oldThread;

				_thread = [_vehicle, _projectile, "WarningWarning", 5] call _spawnSound;
				_vehicle setVariable["YOSHI_projectile_thread", _thread];
				_vehicle setVariable["YOSHI_projectile_threat", 50];
				_projectileThreat = 50;
				_playedSound = true;
			};
			if (!_playedSound && YOSHI_projectileCautionRange > 0 && _distanceFromVic <= YOSHI_projectileCautionRange && _projectileThreat < 10) then {
				_oldThread = _vehicle getVariable "YOSHI_projectile_thread";
				terminate _oldThread;

				_thread = [_vehicle, _projectile, "CautionCaution", 3] call _spawnSound;
				_vehicle setVariable["YOSHI_projectile_thread", _thread];
				_vehicle setVariable["YOSHI_projectile_threat", 10];
				_projectileThreat = 10;
				_playedSound = true;
			};
			private _projectileBeeped = _vehicle getVariable ["YOSHI_vicBeeped", false];
			private _projectileBeepedTime = _vehicle getVariable ["YOSHI_vicBeepedTime", 0];
			private _projectileBeeping = _vehicle getVariable ["YOSHI_vicBeeping", false];
			private _projectileCounted = _vehicle getVariable ["YOSHI_vicCounted", false];
			private _projectileCounting = _vehicle getVariable ["YOSHI_vicCounting", false];
			private _statedProjectileCount = _vehicle getVariable ["YOSHI_statedProjectileCount", 0];
			if (!_playedSound && !_projectileBeeped && YOSHI_projectileDetectionRange > 0 && _distanceFromVic <= YOSHI_projectileDetectionRange && _projectileThreat < 1) then {
				_oldThread = _vehicle getVariable "YOSHI_projectile_thread";
				terminate _oldThread;

				// beep once while detected targets, but are not in caution/warn/danger area
				if ((!_projectileBeeped || ((_statedProjectileCount < (count _incomingProjectiles)) && ((serverTime - _projectileBeepedTime) > 10))) && !_projectileBeeping) then {
					_vehicle setVariable ["YOSHI_vicBeeping", true];
					[_vehicle] spawn {
						params ["_vehicle"];
						_vehicle say3D ["launchDetected", 200, 1];
						sleep 5;
						_vehicle setVariable ["YOSHI_vicBeeping", false];
						_vehicle setVariable ["YOSHI_vicBeeped", true];
						_vehicle setVariable ["YOSHI_vicBeepedTime", serverTime];
						_vehicle setVariable ["YOSHI_vicCounted", false];
					};
				};
			};
			if (_projectileBeeped && (!_projectileCounted || (_statedProjectileCount < (count _incomingProjectiles))) && !_projectileBeeping && !_projectileCounting) then {
				_vehicle setVariable ["YOSHI_vicCounting", true];
				[_vehicle, count _incomingProjectiles] spawn {
					params ["_vehicle", "_countProjectiles"];
					_projectileCount = [_countProjectiles ] call YOSHI_numToTextArray;
					{
						_vehicle say3D [_x, 200, 1];
						sleep 0.6;
					} forEach _projectileCount;
					_vehicle say3D ["targets", 200, 1];
					sleep 0.7;
					_vehicle say3D ["detected", 200, 1];
					sleep 2;
					_vehicle setVariable ["YOSHI_vicCounting", false];
					_vehicle setVariable ["YOSHI_vicCounted", true];
					_vehicle setVariable ["YOSHI_statedProjectileCount", _countProjectiles];
				};

			};

			YOSHI_detectedTargets = _currentKnownProjectiles;
					
		};
	};

};

// future plan: combine nearby targets to a single area, maybe have a size limit on the shape?
YOSHI_drawBoundingBox = { 
    params["_projectiles"];

	_targetLocations = [];
	{
		_x params ["_projectileId", "_projectileFiringPos", "_projectilePos", "_projectileImpactPosition", "_projectileImpactETA", "_projectileLastReportAt"];
		
		_targetLocations pushBack _projectileImpactPosition;

	} forEach _projectiles;


 
    if (count _targetLocations == 0) exitWith {}; 
 
    private _minX = (_targetLocations select 0) select 0; 
    private _minY = (_targetLocations select 0) select 1; 
    private _maxX = _minX; 
    private _maxY = _minY; 
 
    { 
        private _posX = _x select 0; 
        private _posY = _x select 1; 
 
        if (_posX < _minX) then { 
            _minX = _posX; 
        }; 
        if (_posX > _maxX) then { 
            _maxX = _posX; 
        }; 
        if (_posY < _minY) then { 
            _minY = _posY; 
        }; 
        if (_posY > _maxY) then { 
            _maxY = _posY; 
        };
     } forEach _targetLocations; 
 
     
    private _marker = createMarker ["_USER_DEFINED BoundingBoxMarker2", [(_minX + _maxX) / 2, (_minY + _maxY) / 2]]; 
    _marker setMarkerShape "ELLIPSE"; 
    _marker setMarkerSize [(_maxX - _minX) / 2, (_maxY - _minY) / 2]; 
    _marker setMarkerColor "ColorRed"; 
    _marker setMarkerAlpha 0.5; 
    _marker setMarkerText "Covered Area"; 
};


YOSHI_drawTarget = {
	params["_targetData"];
	_targetData params ["_projectileId", "_projectileFiringPos", "_projectilePos", "_projectileImpactPosition", "_projectileImpactETA", "_projectileLastReportAt"];

	if(serverTime - _projectileLastReportAt > YOSHI_mapProjectilesDrawTimeout) then {		
		continue;
	};

	if(_projectilePos distance2d _projectileImpactPosition < 10) then {		
		continue;
	};

	// projectile marker

	_projectileMarkerName = format ["_USER_DEFINED YoshiCounterBatteryRadar projectile-marker_%1_%2", _projectileId, round random 1000000];

	_projectileMarker = createMarkerLocal [_projectileMarkerName, _projectilePos];
	_projectileMarker setMarkerShapeLocal "ICON";
    _projectileMarker setMarkerTypeLocal "mil_triangle";
	_projectileMarker setMarkerDirLocal (_projectilePos getDir _projectileImpactPosition);
	_projectileMarker setMarkerColor "ColorRed";

	// target marker

	_targetMarkerName = format ["_USER_DEFINED YoshiCounterBatteryRadar target-marker_%1_%2", _projectileId, round random 1000000];

	_targetMarker = createMarkerLocal [_targetMarkerName, _projectileImpactPosition];
	_targetMarker setMarkerShapeLocal "ICON";
    _targetMarker setMarkerTypeLocal "mil_destroy";
	_targetMarker setMarkerTextLocal format["ETA: %1s", _projectileImpactETA ];
	_targetMarker setMarkerColor "ColorRed";

};

YOSHI_monitorLoop = {
	private _syncedRadars = synchronizedObjects (missionNamespace getVariable "YOSHI_CBR");

	_syncedRadars apply {
		_x call YOSHI_triggerRadarScan;
	};

	if(YOSHI_mapDrawingEnabled) then {
		{
			private _marker = _x;

			if (_marker find "_USER_DEFINED YoshiCounterBatteryRadar" == 0) then {
				deleteMarker _marker;
			};
		} forEach allMapMarkers;
		
		// [YOSHI_detectedTargets] call YOSHI_drawBoundingBox;

		YOSHI_detectedTargets apply {
			
			[_x] call YOSHI_drawTarget;
		};
	};
};


if(hasInterface) then {
	[] spawn {
		private _fName = "YOSHI_initThread: ";
		diag_log format[_fName + "enter"];
		
		waitUntil{
			sleep 3;
			diag_log format[_fName + "waiting till client is loaded.."];		
			!isNull findDisplay 46 && !(getPlayerUID player isEqualTo '');
		};

		YOSHI_perFrameEH_handle = [
			{		
				if(!(YOSHI_mapDrawingEnabled)) exitWith {};
				call YOSHI_monitorLoop;
			}, 
			1
		] call CBA_fnc_addPerFrameHandler;
		diag_log format[_fName + "YOSHI_perFrameEH_handle: %1", YOSHI_perFrameEH_handle];

		diag_log format[_fName + "exit"];

	};
};

YOSHI_GET_PYLON_INFO = {
    params ["_vehicle"];
    private _allPylonInfo = getAllPylonsInfo _vehicle;
    private _pylonData = [];
    {
        _pylonData pushBack [_x select 0, _x select 3, _x select 2, _x select 4];
    } forEach _allPylonInfo;
    _pylonData
};

YOSHI_SET_VEHICLE_PYLONS = {
    params ["_vehicle", "_pylonData"];
    {
        _vehicle setPylonLoadout  [_x select 0, _x select 1, true, _x select 2];
        // _vehicle setAmmoOnPylon [_x select 0, _x select 3]; // skip so that they're fully rearmed after deploying
    } forEach _pylonData;
};

YOSHI_REARM_ALL_PYLONS = {
    params ["_vehicle"];
    private _allPylonInfo = getAllPylonsInfo _vehicle;
    {
        _vehicle setAmmoOnPylon [_x select 0, 1000];
    } forEach _allPylonInfo;
};

YOSHI_GET_DAMAGE_INFO = {
    params ["_vehicle"];
    private _damageInfo = getAllHitPointsDamage _vehicle;
    if (count _damageInfo == 0) exitWith {[damage _vehicle, []]};
    private _damageLocations = _damageInfo select 0;
    private _damageValues = _damageInfo select 2;
    private _damageData = [];
    {
        _damageData pushBack [_damageLocations select _forEachIndex, _x];
    } forEach _damageValues; 
    [damage _vehicle, _damageData]
};

YOSHI_SET_DAMAGE_INFO = {
    params ["_vehicle", "_fullDamageData"];
    private _specificDamageData = _fullDamageData select 1;
    private _basicDamage = _fullDamageData select 0;
    _vehicle setDamage [_basicDamage, false];
    {
        _vehicle setHitPointDamage [_x select 0, _x select 1, false];
    } forEach _specificDamageData;
};

YOSHI_FULL_REPAIR_VEHICLE = {
    params ["_vehicle"];
    _vehicle setDamage 0;
};

// Function to copy a vehicle
YOSHI_COPY_VEHICLE = {
    params ["_vehicle"];
    
    private _data = [
        typeOf _vehicle,
        getObjectTextures _vehicle,
        fuel _vehicle,
        _vehicle call YOSHI_GET_PYLON_INFO,
        _vehicle call YOSHI_GET_DAMAGE_INFO
        // damage _vehicle, // getAllHitPointsDamage
        // getObjectMaterials _vehicle,
        // crew _vehicle apply { [typeOf _x, getUnitLoadout _x] }, // keep it simple for now
        // [magazinesCargo _vehicle, weaponsCargo _vehicle, itemsCargo _vehicle]
    ];
    _data
};

// Function to paste a vehicle
YOSHI_PASTE_VEHICLE = {
    params ["_pos", "_data", ["_dir", 0], ["_altitude", 0]];
    
    private _vehicleType = _data select 0;
    private _textures = _data select 1;
    private _fuel = _data select 2;
    private _ammo = _data select 3;
    private _fullDamageData = _data select 4;
    
    private _newVehicle = createVehicle [_vehicleType, _pos, [], 0, "FLY"];
    if (_altitude > 0) then {
        _pos set [2, _altitude];
        _newVehicle setPosASL _pos;
    };
    private _velocity = velocity _newVehicle; 
    _newVehicle setDir _dir;
    _newVehicle setVelocity (_velocity vectorMultiply (cos _dir));
    // _newVehicle setFuel _fuel; // skipping for the moment since we want them to be refueled
    [_newVehicle, _ammo] call YOSHI_SET_VEHICLE_PYLONS;
    [_newVehicle, _fullDamageData] call YOSHI_SET_DAMAGE_INFO;

    {
        _newVehicle setObjectTextureGlobal [_forEachIndex, _x];
    } forEach _textures;


    createVehicleCrew _newVehicle;

    _newVehicle
};

YOSHI_GET_LGM = { 
    params ["_vehicle"]; 
    private _bomb = ""; 
    private _missile = ""; 
 
    { 
        private _weapon = _x; 
        private _mags = getArray (configFile >> "CfgWeapons" >> _weapon >> "magazines"); 
 
        { 
            private _magazine = _x; 
            private _ammoType = getText (configFile >> "CfgMagazines" >> _magazine >> "ammo"); 
            private _isLaserGuided = getNumber (configFile >> "CfgAmmo" >> _ammoType >> "laserLock") > 0; 
            private _isBomb = _isLaserGuided && ((toLower _weapon) find "bomb" > -1 || (toLower _weapon) find "gbu" > -1 || (toLower _weapon) find "vblauncher" > -1); 
            private _hasAmmo = ((magazinesAmmoFull _vehicle) findIf {(_x select 0) isEqualTo _magazine && (_x select 1) > 0}) > -1; 
 
            if (_isLaserGuided && _hasAmmo) then { 
                if (_bomb == "" && _isBomb) then { 
                    _bomb = _weapon; 
                } else { 
                    if (_missile == "" && !_isBomb) then { 
                        _missile = _weapon; 
                    }; 
                }; 
 
                if (_bomb != "" && _missile != "") exitWith {}; 
            }; 
        } forEach _mags; 
 
        if (_bomb != "" && _missile != "") exitWith {}; 
    } forEach (weapons _vehicle); 
 
    [_bomb, _missile] 
};

YOSHI_GET_FW_ROLE = {
    params ["_vehicle"];

    private _role = 0; // default to No Role
    private _munitions = _vehicle call YOSHI_GET_LGM;
    if ((_munitions select 0) != "" || (_munitions select 1) != "") then {
        _role = _role + 1; // CAS
    };
    if (unitIsUAV  _vehicle) then {
        _role = _role + 2; // Recon
    };
    if (isClass (configFile >> "CfgVehicles" >> typeOf _vehicle >> "vehicleTransport")) then {
        _role = _role + 4; // Logistics
    };
    _role
};

YOSHI_CALCULATE_FUEL_CONSUMPTION = {
    // local function

	params ["_vehicle"];
    private _fuelHistory = _vehicle getVariable ["YOSHI_FUEL_HISTORY", []];
    private _currentFuel = fuel _vehicle;
    _fuelHistory pushBack _currentFuel;
    _vehicle setVariable ["YOSHI_FUEL_HISTORY", _fuelHistory];
    private _historyLength = count _fuelHistory;
    if (_historyLength > 10) then {
        _fuelHistory deleteAt 0;
    };
    private _firstValue = _fuelHistory select 0;
    private _fuelConsumptionRate = (_firstValue - _currentFuel) / (_historyLength * 5);
    
    if (_fuelConsumptionRate == 0) exitWith {-1};

    private _estimatedTimeToEmpty = _currentFuel / _fuelConsumptionRate;
    _estimatedTimeToEmpty

};

YOSHI_ADJUST_LOITER_POINT = {
    params ["_vehicle"];
    private _group = group _vehicle;

    _group setBehaviourStrong "CARELESS";
    _group setCombatMode "GREEN";

    if ((waypointType [_group, currentWaypoint _group]) isEqualTo "LOITER") then {
        [_group, currentWaypoint _group] setWaypointLoiterRadius 2000;
    };

    private _caller = _vehicle getVariable ["YOSHI_FW_CALLER", objNull];
    if (!isNull _caller) then {
        if ((getWPPos [_group, 0]) distance2D (getPosASL _caller) > 100) then {
            _currentWaypointIndex = currentWaypoint _group;
            [_group, _currentWaypointIndex] setWaypointPosition [(getPosASL _caller), 0];
        };
    };
};


YOSHI_CREATE_FW_THREAD = {
	params ["_vehicle"];
	private _thread = [_vehicle] spawn {
		params ["_vehicle"];
		while {alive _vehicle} do {
			sleep 5;
            _vehicle flyInHeightASL [2000, 2000, 2000];
			_vehicle flyInHeight 2000;


		    private _fuelTimeRemaining = _vehicle call YOSHI_CALCULATE_FUEL_CONSUMPTION;
            if (_fuelTimeRemaining > -1  && _fuelTimeRemaining < 420) then {
				// 5 minutes of fuel remaining
				_vehicle call YOSHI_SEND_FW_AWAY;
                if (!(_vehicle getVariable ["YOSHI_REPORTED_LOW_FUEL", false])) then {
                    _vehicle setVariable ["YOSHI_REPORTED_LOW_FUEL", true, true];
                    if (!(unitIsUAV _vehicle)) then {
                        if ((_vehicle call YOSHI_GET_FW_ROLE) >= 4) then {
                            [_vehicle, selectRandom ["YOSHI_AlbatrossLowFuel1", "YOSHI_AlbatrossLowFuel2", "YOSHI_AlbatrossLowFuel3"]] call YOSHI_fnc_playSideRadio;
                        } else {
                            //[_vehicle, selectRandom ["YOSHI_ValkyrieLowFuel1", "YOSHI_ValkyrieLowFuel2", "YOSHI_ValkyrieLowFuel3"]] call YOSHI_fnc_playSideRadio;
                        };
                    };
                    
                };
			};
            if (_fuelTimeRemaining > -1  && _fuelTimeRemaining < 300) then {
				// 5 minutes of fuel remaining
				_vehicle call YOSHI_SEND_FW_AWAY;
                if (!(_vehicle getVariable ["YOSHI_REPORTED_BINGO_FUEL", false])) then {
                    _vehicle setVariable ["YOSHI_REPORTED_BINGO_FUEL", true, true];
                    if (!(unitIsUAV _vehicle)) then {
                        if ((_vehicle call YOSHI_GET_FW_ROLE) >= 4) then {
                            [_vehicle, selectRandom ["YOSHI_AlbatrossNoFuel1", "YOSHI_AlbatrossNoFuel2", "YOSHI_AlbatrossNoFuel3"]] call YOSHI_fnc_playSideRadio;
                        } else {
                            //[_vehicle, selectRandom ["YOSHI_ValkyrieNoFuel1", "YOSHI_ValkyrieNoFuel2", "YOSHI_ValkyrieNoFuel3"]] call YOSHI_fnc_playSideRadio;
                        };
                    };
                    
                };
			};

            _vehicle call YOSHI_ADJUST_LOITER_POINT;
            
		};
	};
	_vehicle setVariable ["YOSHI_FW_THREAD", _thread, true];
};
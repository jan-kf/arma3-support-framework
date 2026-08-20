/*
Phase 1:
  - Fixed-wing registry
  - Snapshot/despawn lifecycle
  - Deploy/RTB server actions
*/

YSF_FW_STATE_STOWED = "stowed";
YSF_FW_STATE_DEPLOYING = "deploying";
YSF_FW_STATE_ON_STATION = "on_station";
YSF_FW_STATE_RTB = "rtb";
YSF_FW_STATE_COOLDOWN = "cooldown";

YSF_FW_ROLE_STRIKE = 1;
YSF_FW_ROLE_RECON = 2;
YSF_FW_ROLE_LOGI = 4;

YSF_FW_RTB_TIMEOUT = 300;
YSF_FW_LOGISTICS_INGRESS_TIMEOUT = 180;
YSF_FW_LOGISTICS_DELIVERY_TIMEOUT = 180;
YSF_FW_LOGISTICS_RELEASE_RADIUS = 25;
YSF_FW_LOGISTICS_FLIGHT_HEIGHT = 180;
YSF_FW_LOGISTICS_RELEASE_ALTITUDE_TOLERANCE = 60;

// Registry mutation is a server capability, not an implication of knowing a
// globally named SQF function. Each machine compiles a different value and it
// is never published.
YSF_FW_REGISTRY_TOKEN = format ["ysf-fw-%1-%2-%3", diag_tickTime, random 1e9, random 1e9];

YSF_fwRegistryAudit = {
	params ["_token", "_operation", "_decision", ["_detail", ""]];
	if (_token isNotEqualTo YSF_FW_REGISTRY_TOKEN) exitWith {};
	private _rows = missionNamespace getVariable ["YSF_FW_REGISTRY_AUDIT", []];
	_rows pushBack [diag_tickTime, _operation, _decision, remoteExecutedOwner, _detail];
	if ((count _rows) > 64) then {_rows deleteRange [0, (count _rows) - 64];};
	missionNamespace setVariable ["YSF_FW_REGISTRY_AUDIT", _rows, false];
};

YSF_fwSideToId = {
    params ["_side"];
    if (_side isEqualType 0) exitWith {_side};
    _side call BIS_fnc_sideID
};

YSF_fwSideFromId = {
    params ["_sideId"];
    if (_sideId isEqualType west) exitWith {_sideId};
    switch (_sideId) do {
        case 0: {east};
        case 1: {west};
        case 2: {resistance};
        case 3: {civilian};
        default {sideUnknown};
    };
};

YSF_fwResolveObjectRef = {
    params ["_value"];
    if (_value isEqualType objNull) exitWith {_value};
    if (_value isEqualType "") exitWith {
        if (_value isEqualTo "") then {objNull} else {objectFromNetId _value}
    };
    objNull
};

YSF_fwBuildPublicRegistry = {
    params ["_reg"];
    private _out = [];
    {
        private _id = _x;
        private _entry = _y;
        if (typeName _entry isEqualTo "HASHMAP") then {
            _out pushBack [
                _id,
                _entry getOrDefault ["state", YSF_FW_STATE_STOWED],
                _entry getOrDefault ["callsign", ""],
                _entry getOrDefault ["vehicleType", ""],
                _entry getOrDefault ["roleMask", 0],
                [_entry getOrDefault ["side", sideUnknown]] call YSF_fwSideToId,
                netId (_entry getOrDefault ["spawnedVeh", objNull]),
                _entry getOrDefault ["cooldownUntil", -1],
                _entry getOrDefault ["cooldownSeconds", 0],
                _entry getOrDefault ["lastUpdate", -1]
            ];
        };
    } forEach _reg;
    _out
};

YSF_fwCommitPublicRegistry = {
	params ["_token", "_reg"];
	if (!isServer) exitWith {};
	if (_token isNotEqualTo YSF_FW_REGISTRY_TOKEN) exitWith {
		[YSF_FW_REGISTRY_TOKEN, "commit-public", "token-rejected"] call YSF_fwRegistryAudit;
	};
    private _public = [_reg] call YSF_fwBuildPublicRegistry;
    missionNamespace setVariable [
        "YSF_FW_PUBLIC_REGISTRY",
        _public,
        true
    ];
    private _stateSummary = (_public apply {
        if (_x isEqualType [] && {(count _x) >= 2}) then {
            format ["%1:%2", _x select 0, _x select 1]
        } else {
            "<bad>"
        }
    }) select [0, 6];
    diag_log format [
        "[YSF][FWDBG] scope=SERVER owner=%1 publicCommit count=%2 states=%3",
        clientOwner,
        count _public,
        _stateSummary joinString ","
    ];
};

YSF_fwCommitRegistry = {
	params ["_token", "_reg"];
	if (_token isNotEqualTo YSF_FW_REGISTRY_TOKEN) exitWith {
		[YSF_FW_REGISTRY_TOKEN, "commit", "token-rejected"] call YSF_fwRegistryAudit;
	};
	missionNamespace setVariable ["YSF_FW_REGISTRY", _reg, false];
	if (isServer) then {
		[YSF_FW_REGISTRY_TOKEN, _reg] call YSF_fwCommitPublicRegistry;
    };
};

YSF_fwEnsureRegistry = {
    private _reg = missionNamespace getVariable ["YSF_FW_REGISTRY", objNull];
    if !(typeName _reg isEqualTo "HASHMAP") then {
        _reg = createHashMap;
		[YSF_FW_REGISTRY_TOKEN, _reg] call YSF_fwCommitRegistry;
    };
    _reg
};

YSF_fwGetPublicRegistry = {
    private _reg = missionNamespace getVariable ["YSF_FW_PUBLIC_REGISTRY", []];
    if (_reg isEqualType []) exitWith {_reg};
    []
};

YSF_fwPublicEntryToMap = {
    params ["_row"];
    if !(_row isEqualType [] && {(count _row) >= 10}) exitWith {objNull};
    createHashMapFromArray [
        ["id", _row select 0],
        ["state", _row select 1],
        ["callsign", _row select 2],
        ["vehicleType", _row select 3],
        ["roleMask", _row select 4],
        ["side", [(_row select 5)] call YSF_fwSideFromId],
        ["spawnedVeh", [(_row select 6)] call YSF_fwResolveObjectRef],
        ["cooldownUntil", _row select 7],
        ["cooldownSeconds", _row select 8],
        ["lastUpdate", _row select 9]
    ]
};

YSF_fwDefaultPos = {
    params ["_kind"]; // "infil" | "exfil"
    private _var = if (_kind isEqualTo "infil") then {"YSF_FW_DEFAULT_INFIL_POS"} else {"YSF_FW_DEFAULT_EXFIL_POS"};
    private _pos = missionNamespace getVariable [_var, []];
    if ((count _pos) < 3) then {
        private _mid = worldSize / 2;
        _pos = [_mid, _mid, 1200];
    };
    _pos
};

YSF_fwConfigSide = {
    params ["_vehicleType"];
    private _cfgSide = getNumber (configFile >> "CfgVehicles" >> _vehicleType >> "side");
    switch (_cfgSide) do {
        case 0: {east};
        case 1: {west};
        case 2: {resistance};
        case 3: {civilian};
        default {sideUnknown};
    };
};

YSF_fwCreateUavCrew = {
    params ["_vehicle"];
    if (isNull _vehicle) exitWith {0};

    private _vehicleType = typeOf _vehicle;
    private _crewClass = getText (configFile >> "CfgVehicles" >> _vehicleType >> "crew");
    if (_crewClass isEqualTo "") then {
        _crewClass = "B_UAV_AI";
    };

    private _side = [_vehicleType] call YSF_fwConfigSide;
    private _group = createGroup [_side, true];
    _group deleteGroupWhenEmpty true;

    private _created = 0;
    private _createdSeats = [];
    {
        _x params [
            ["_unit", objNull],
            ["_role", ""],
            ["_cargoIndex", -1],
            ["_turretPath", []]
        ];
        if (isNull _unit && {!(_role in ["cargo", "personTurret"])}) then {
            private _crewman = _group createUnit [_crewClass, [0, 0, 0], [], 0, "NONE"];
            switch (_role) do {
                case "driver": {
                    _crewman moveInDriver _vehicle;
                };
                case "commander": {
                    _crewman moveInCommander _vehicle;
                };
                case "gunner": {
                    if (_turretPath isEqualType [] && {(count _turretPath) > 0}) then {
                        _crewman moveInTurret [_vehicle, _turretPath];
                    } else {
                        _crewman moveInGunner _vehicle;
                    };
                };
                case "turret": {
                    if (_turretPath isEqualType [] && {(count _turretPath) > 0}) then {
                        _crewman moveInTurret [_vehicle, _turretPath];
                    } else {
                        deleteVehicle _crewman;
                        _crewman = objNull;
                    };
                };
                default {
                    deleteVehicle _crewman;
                    _crewman = objNull;
                };
            };

            if (!isNull _crewman && {vehicle _crewman isEqualTo _vehicle}) then {
                _created = _created + 1;
                _createdSeats pushBack format ["%1:%2", _role, _turretPath];
            } else {
                if (!isNull _crewman) then {
                    deleteVehicle _crewman;
                };
            };
        };
    } forEach (fullCrew [_vehicle, "", true]);

    diag_log format [
        "[YSF][FWDBG] scope=SERVER owner=%1 manualUavCrew veh=%2 crewClass=%3 created=%4 seats=%5",
        clientOwner,
        _vehicleType,
        _crewClass,
        _created,
        _createdSeats joinString ","
    ];

    _created
};

YOSHI_GET_PYLON_INFO = {
    params ["_vehicle"];
    private _allPylonInfo = getAllPylonsInfo _vehicle;
    private _pylonData = [];
    {
        _pylonData pushBack [_x select 0, _x select 3, _x select 2, _x select 4];
    } forEach _allPylonInfo;
    _pylonData
};

YSF_fwAmmoInheritsFrom = {
    params ["_ammoClass", "_baseClass"];
    if (_ammoClass isEqualTo "" || {_baseClass isEqualTo ""}) exitWith {false};

    private _cfg = configFile >> "CfgAmmo" >> _ammoClass;
    if !(isClass _cfg) exitWith {false};

    private _needle = toLower _baseClass;
    private _cur = _cfg;
    private _safe = 0;
    private _inherits = false;

    while {isClass _cur && {_safe < 32}} do {
        private _name = toLower (configName _cur);
        if ((_name find _needle) >= 0) exitWith {_inherits = true};
        _cur = inheritsFrom _cur;
        _safe = _safe + 1;
    };

    _inherits
};

YSF_fwSanitizeSnapshotPylons = {
    params ["_pylonData"];
    if !(_pylonData isEqualType []) exitWith {[[], 0, 0]};

    private _sanitized = [];
    private _hellfireSwaps = 0;
    private _laserBombSwaps = 0;

    {
        private _row = +_x;
        if !(_row isEqualType [] && {(count _row) >= 3}) then {
            _sanitized pushBack _row;
        } else {
            private _mag = _row param [1, ""];
            if (_mag isEqualType "" && {_mag isNotEqualTo ""}) then {
                private _tag = toLower _mag;
                if (((_tag find "uk3cb_baf_pylonrack_") >= 0) && {(_tag find "hellfire") >= 0}) then {
                    _row set [1, "PylonRack_4Rnd_LG_scalpel"];
                    _hellfireSwaps = _hellfireSwaps + 1;
                };
            };

            _sanitized pushBack _row;
        };
    } forEach _pylonData;

    [_sanitized, _hellfireSwaps, _laserBombSwaps]
};

YOSHI_SET_VEHICLE_PYLONS = {
    params ["_vehicle", "_pylonData"];
    private _sanitizedResult = [_pylonData] call YSF_fwSanitizeSnapshotPylons;
    private _sanitizedPylons = _sanitizedResult select 0;

    {
        if (_x isEqualType [] && {(count _x) >= 3}) then {
            _vehicle setPylonLoadout [_x select 0, _x select 1, true, _x select 2];
            private _savedAmmo = _x param [3, -1];
            if (_savedAmmo >= 0) then {
                _vehicle setAmmoOnPylon [_x select 0, _savedAmmo];
            };
        };
    } forEach _sanitizedPylons;

    [_sanitizedResult select 1, _sanitizedResult select 2]
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

YOSHI_COPY_VEHICLE = {
    params ["_vehicle"];
    [
        typeOf _vehicle,
        getObjectTextures _vehicle,
        fuel _vehicle,
        _vehicle call YOSHI_GET_PYLON_INFO,
        _vehicle call YOSHI_GET_DAMAGE_INFO,
        _vehicle call YOSHI_GET_FW_ROLE,
        unitIsUAV _vehicle
    ]
};

YOSHI_PASTE_VEHICLE = {
    params ["_posASL", "_data", ["_dir", 0], ["_altitude", 2200], ["_targetPosASL", []], ["_initialSpeed", -1]];

    private _vehicleType = _data select 0;
    private _textures = _data select 1;
    private _ammo = _data select 3;
    private _fullDamageData = _data select 4;

    private _spawnPos = +_posASL;
    if ((count _spawnPos) < 3) then {_spawnPos set [2, _altitude max 2200];};
    if (_altitude > 0) then {_spawnPos set [2, _altitude];};

    private _newVehicle = createVehicle [_vehicleType, [0, 0, 0], [], 0, "FLY"];
    _newVehicle setPosASL _spawnPos;

    private _finalDir = _dir;
    if ((count _targetPosASL) >= 2) then {
        if ((_spawnPos distance2D _targetPosASL) > 150) then {
            _finalDir = [_spawnPos, _targetPosASL] call BIS_fnc_dirTo;
        };
    };
    _newVehicle setDir _finalDir;

    private _swapCounts = [_newVehicle, _ammo] call YOSHI_SET_VEHICLE_PYLONS;
    _newVehicle setFuel (((_data param [2, 1]) max 0) min 1);
    [_newVehicle, _fullDamageData] call YOSHI_SET_DAMAGE_INFO;
    {
        _newVehicle setObjectTextureGlobal [_forEachIndex, _x];
    } forEach _textures;

    // Freshly pasted aircraft should arrive already normalized and get a short
    // warmup window before any automated engagement logic touches them.
    _newVehicle setVariable ["YSF_AAE_hellfireSwapDone", true, false];
    _newVehicle setVariable ["YSF_AAE_laserBombSwapDone", true, false];
    _newVehicle setVariable [
        "YSF_AAE_warmupUntil",
        serverTime + ((missionNamespace getVariable ["YSF_AAE_SPAWN_WARMUP", 10]) max 0),
        false
    ];

    if ((_swapCounts param [0, 0]) > 0) then {
        diag_log format [
            "[YSF][FW] normalized %1 Hellfire pylon(s) before spawn on %2",
            _swapCounts select 0,
            _vehicleType
        ];
    };
    if ((_swapCounts param [1, 0]) > 0) then {
        diag_log format [
            "[YSF][FW] normalized %1 LaserBomb pylon(s) before spawn on %2",
            _swapCounts select 1,
            _vehicleType
        ];
    };

    if (unitIsUAV _newVehicle) then {
        [_newVehicle] call YSF_fwCreateUavCrew;
    } else {
        createVehicleCrew _newVehicle;
    };

    // Spawn with forward energy to avoid the "drop then recover" behavior.
    private _cfgMaxSpeed = getNumber (configFile >> "CfgVehicles" >> _vehicleType >> "maxSpeed");
    private _speed = _initialSpeed;
    if (_speed <= 0) then {
        _speed = if (_cfgMaxSpeed > 0) then {((_cfgMaxSpeed * 0.45) max 150) min 300} else {220};
    };

    _newVehicle engineOn true;
    _newVehicle setDir _finalDir;
    _newVehicle flyInHeightASL [(_spawnPos select 2), (_spawnPos select 2), (_spawnPos select 2)];
    _newVehicle flyInHeight (_spawnPos select 2);
    _newVehicle setVelocity [
        (sin _finalDir) * _speed,
        (cos _finalDir) * _speed,
        8
    ];
    

    _newVehicle
};

YOSHI_GET_FW_ROLE = {
    params ["_vehicle"];
    private _role = 0;

    private _munitions = _vehicle call YOSHI_GET_LGO;
    if ((count (_munitions select 0)) > 0 || (count (_munitions select 1)) > 0) then {
        _role = _role + YSF_FW_ROLE_STRIKE;
    };
    if (unitIsUAV _vehicle) then {
        _role = _role + YSF_FW_ROLE_RECON;
    };
    if (isClass (configFile >> "CfgVehicles" >> typeOf _vehicle >> "vehicleTransport")) then {
        _role = _role + YSF_FW_ROLE_LOGI;
    };
    _role
};

YSF_fwDeleteVehicleAndCrew = {
    params ["_vehicle"];
    if (isNull _vehicle) exitWith {};
    { deleteVehicle _x; } forEach crew _vehicle;
    deleteVehicle _vehicle;
};

YSF_fwSetEntry = {
	params ["_token", "_id", "_entry"];
	if (_token isNotEqualTo YSF_FW_REGISTRY_TOKEN) exitWith {
		private _detail = if (_id isEqualType "") then {_id} else {str _id};
		[YSF_FW_REGISTRY_TOKEN, "set-entry", "token-rejected", _detail] call YSF_fwRegistryAudit;
	};
	private _reg = call YSF_fwEnsureRegistry;
	_reg set [_id, _entry];
	[YSF_FW_REGISTRY_TOKEN, _reg] call YSF_fwCommitRegistry;
};

YSF_fwSetEntryPrivate = {
	params ["_token", "_id", "_entry"];
	if (!isServer) exitWith {};
	if (_token isNotEqualTo YSF_FW_REGISTRY_TOKEN) exitWith {
		private _detail = if (_id isEqualType "") then {_id} else {str _id};
		[YSF_FW_REGISTRY_TOKEN, "set-entry-private", "token-rejected", _detail] call YSF_fwRegistryAudit;
	};
    private _reg = call YSF_fwEnsureRegistry;
    _reg set [_id, _entry];
    missionNamespace setVariable ["YSF_FW_REGISTRY", _reg, false];
};

YSF_fwGetEntry = {
    params ["_id"];
    if (!isServer) exitWith {
        private _public = call YSF_fwGetPublicRegistry;
        private _idx = _public findIf {
            _x isEqualType [] && {(count _x) >= 1} && {(_x select 0) isEqualTo _id}
        };
        if (_idx < 0) exitWith {objNull};
        [(_public select _idx)] call YSF_fwPublicEntryToMap
    };

    private _reg = call YSF_fwEnsureRegistry;
    private _entry = _reg getOrDefault [_id, objNull];
    if (typeName _entry isEqualTo "HASHMAP") then {
        if ((_entry getOrDefault ["state", ""]) isEqualTo YSF_FW_STATE_COOLDOWN) then {
            private _until = _entry getOrDefault ["cooldownUntil", -1];
            if (_until > -1 && {serverTime >= _until}) then {
                _entry set ["state", YSF_FW_STATE_STOWED];
                _entry set ["cooldownUntil", -1];
                _entry set ["cooldownSeconds", 0];
                _entry set ["lastUpdate", serverTime];
                _reg set [_id, _entry];
				[YSF_FW_REGISTRY_TOKEN, _reg] call YSF_fwCommitRegistry;
            };
        };
    };
    _entry
};

YSF_fwPylonAmmoRatio = {
    params ["_basePylons", "_currentPylons"];
    private _baseTotal = 0;
    private _currentTotal = 0;

    {
        private _pylonIndex = _x select 0;
        private _baseAmmo = (_x select 3) max 0;
        if (_baseAmmo > 0) then {
            _baseTotal = _baseTotal + _baseAmmo;
            private _currIdx = _currentPylons findIf { (_x select 0) isEqualTo _pylonIndex };
            private _currAmmo = 0;
            if (_currIdx > -1) then {
                _currAmmo = ((_currentPylons select _currIdx) select 3) max 0;
            };
            _currentTotal = _currentTotal + (_currAmmo min _baseAmmo);
        };
    } forEach _basePylons;

    if (_baseTotal <= 0) exitWith {1};
    ((_currentTotal / _baseTotal) max 0) min 1
};

YSF_fwComputeCooldownSeconds = {
    params ["_entry", "_vehicle", "_newSnapshot"];
    private _healthDeficit = ((damage _vehicle) max 0) min 1;
    private _fuelDeficit = ((1 - fuel _vehicle) max 0) min 1;

    private _oldSnapshot = _entry getOrDefault ["snapshot", []];
    private _ammoRatio = 1;
    if (!(_oldSnapshot isEqualTo []) && {!(_newSnapshot isEqualTo [])}) then {
        private _oldPylons = _oldSnapshot select 3;
        private _newPylons = _newSnapshot select 3;
        if ((typeName _oldPylons isEqualTo "ARRAY") && {(typeName _newPylons isEqualTo "ARRAY")}) then {
            _ammoRatio = [_oldPylons, _newPylons] call YSF_fwPylonAmmoRatio;
        };
    };
    private _ammoDeficit = ((1 - _ammoRatio) max 0) min 1;

    round ((_healthDeficit + _fuelDeficit + _ammoDeficit) * 300)
};

YSF_fwApplyDefaultPointToRegistry = {
    params ["_kind", "_posASL"]; // "infil" | "exfil"
    if (!isServer) exitWith {};
    private _reg = call YSF_fwEnsureRegistry;
    {
        private _entry = _y;
        if (typeName _entry isEqualTo "HASHMAP") then {
            private _key = if (_kind isEqualTo "infil") then {"infilPosASL"} else {"exfilPosASL"};
            _entry set [_key, _posASL];
            _entry set ["lastUpdate", serverTime];
            _reg set [_x, _entry];
        };
    } forEach _reg;
	[YSF_FW_REGISTRY_TOKEN, _reg] call YSF_fwCommitRegistry;
};

YSF_fwRegisterAsset = {
    params ["_vehicle", ["_infilPos", []], ["_exfilPos", []], ["_callsign", ""]];

    if (!isServer) exitWith {false};
    if (isNull _vehicle) exitWith {false};
    if (!(_vehicle isKindOf "Plane")) exitWith {false};

    private _id = _vehicle getVariable ["YSF_FW_ID", ""];
    if (_id isEqualTo "") then {
        _id = format ["FW_%1", netId _vehicle];
    };

    if ((count _infilPos) < 3) then {_infilPos = ["infil"] call YSF_fwDefaultPos;};
    if ((count _exfilPos) < 3) then {_exfilPos = ["exfil"] call YSF_fwDefaultPos;};

    private _entry = createHashMapFromArray [
        ["id", _id],
        ["state", YSF_FW_STATE_STOWED],
        ["callsign", _callsign],
        ["vehicleType", typeOf _vehicle],
        ["snapshot", [_vehicle] call YOSHI_COPY_VEHICLE],
        ["roleMask", [_vehicle] call YOSHI_GET_FW_ROLE],
        ["side", side _vehicle],
        ["infilPosASL", _infilPos],
        ["exfilPosASL", _exfilPos],
        ["heading", getDir _vehicle],
        ["spawnedVeh", objNull],
        ["lastUpdate", serverTime]
    ];

    _vehicle setVariable ["YSF_FW_ID", _id, true];
	[YSF_FW_REGISTRY_TOKEN, _id, _entry] call YSF_fwSetEntry;
    [_vehicle] call YSF_fwDeleteVehicleAndCrew;
    true
};

YSF_fwSetLoiter = {
    params ["_vehicle", "_centerASL", ["_radius", 1800], ["_altitude", 2200]];
    private _grp = group _vehicle;
    if (isNull _grp) exitWith {};

    _vehicle flyInHeightASL [_altitude, _altitude, _altitude];
    _vehicle flyInHeight _altitude;

    for "_i" from (count waypoints _grp - 1) to 0 step -1 do {
        deleteWaypoint [_grp, _i];
    };

    private _wp = _grp addWaypoint [[_centerASL select 0, _centerASL select 1, 0], 0];
    _wp setWaypointType "LOITER";
    _wp setWaypointLoiterType "CIRCLE_L";
    _wp setWaypointLoiterRadius _radius;
    _wp setWaypointLoiterAltitude _altitude;
    _grp setCurrentWaypoint _wp;
    _grp setSpeedMode "NORMAL";
    _grp setBehaviourStrong "CARELESS";
    _grp setCombatMode "GREEN";
};

YSF_fwMonitorCallerLoiter = {
    params ["_id", "_vehicle", ["_caller", objNull], ["_recenterDistance", 500], ["_checkInterval", 10]];
    if (!isServer) exitWith {};
    if (isNull _vehicle) exitWith {};

    [{
        params ["_args", "_handle"];
        _args params ["_id", "_vehicle", "_caller", "_recenterDistance"];

        if (isNull _vehicle || {!alive _vehicle}) exitWith {
            [_handle] call CBA_fnc_removePerFrameHandler;
        };

        private _entry = [_id] call YSF_fwGetEntry;
        if !(typeName _entry isEqualTo "HASHMAP") exitWith {
            [_handle] call CBA_fnc_removePerFrameHandler;
        };

        private _state = _entry getOrDefault ["state", YSF_FW_STATE_STOWED];
        if !(_state isEqualTo YSF_FW_STATE_ON_STATION) exitWith {
            [_handle] call CBA_fnc_removePerFrameHandler;
        };

        if (isNull _caller || {!alive _caller}) exitWith {};

        private _callerPos = getPosASL _caller;
        private _loiterCenter = _vehicle getVariable ["YSF_FW_LOITER_CENTER_ASL", _callerPos];
        if ((_callerPos distance2D _loiterCenter) >= _recenterDistance) then {
            [_vehicle, _callerPos] call YSF_fwSetLoiter;
            _vehicle setVariable ["YSF_FW_LOITER_CENTER_ASL", _callerPos, false];
        };
    }, _checkInterval, [_id, _vehicle, _caller, _recenterDistance]] call CBA_fnc_addPerFrameHandler;
};

YSF_fwDeployAck = {
    params ["_requestId", "_accepted", "_reason", ["_owner", 0], ["_assetId", ""]];
    if (!isServer || {_requestId isEqualTo ""}) exitWith {};
    private _payload = [_accepted isEqualTo true, _reason, _assetId, serverTime];
    missionNamespace setVariable [format ["YSF_FW_DEPLOY_ACK_%1", _requestId], _payload, _owner];

    private _audit = missionNamespace getVariable ["YSF_FW_DEPLOY_AUDIT", []];
    _audit pushBack [_requestId, _assetId, _accepted isEqualTo true, _reason, _owner, serverTime];
    if ((count _audit) > 50) then {_audit deleteRange [0, (count _audit) - 50];};
    missionNamespace setVariable ["YSF_FW_DEPLOY_AUDIT", _audit, false];
};

YSF_fwDeployAsset = {
    params ["_id", ["_caller", objNull], ["_requestId", ""]];

    if (!isServer) exitWith {
        if (_requestId isEqualTo "") then {
            _requestId = format ["FW_DEPLOY_%1_%2_%3", clientOwner, floor (diag_tickTime * 1000), floor random 1000000];
        };
        private _callerRef = if (_caller isEqualType objNull) then {
            if (isNull _caller) then {""} else {netId _caller}
        } else {
            _caller
        };
        missionNamespace setVariable [format ["YSF_FW_DEPLOY_ACK_%1", _requestId], nil, false];
        diag_log format [
            "[YSF][FWDBG] scope=CLIENT owner=%1 deployClick id=%2 caller=%3",
            clientOwner,
            _id,
            if (isNull _caller) then {"<null>"} else {name _caller}
        ];
        [_id, _callerRef, _requestId] remoteExecCall ["YSF_fwDeployAsset", 2];
        diag_log format [
            "[YSF][FWDBG] scope=CLIENT owner=%1 deployDispatchQueued id=%2 callerRef=%3",
            clientOwner,
            _id,
            _callerRef
        ];
        objNull
    };

    private _requestOwner = remoteExecutedOwner;
    private _reject = {
        params ["_reason"];
        [_requestId, false, _reason, _requestOwner, _id] call YSF_fwDeployAck;
        objNull
    };
    if !(_requestId isEqualType "" && {_requestId isNotEqualTo ""}) exitWith {objNull};

    if (_caller isEqualType "") then {
        _caller = [_caller] call YSF_fwResolveObjectRef;
    };
    if (isNull _caller || {!isPlayer _caller} || {owner _caller isNotEqualTo _requestOwner}) exitWith {
        ["invalid_requester"] call _reject
    };

    private _entry = [_id] call YSF_fwGetEntry;
    if !(typeName _entry isEqualTo "HASHMAP") exitWith {["asset_not_registered"] call _reject};

    private _vehicleType = _entry getOrDefault ["vehicleType", ""];
    if (isNil "YSF_fwIsDisabledDeployType") exitWith {["deploy_classifier_unavailable"] call _reject};
    if ([_vehicleType] call YSF_fwIsDisabledDeployType) exitWith {
        ["uav_deploy_disabled"] call _reject
    };

    private _state = _entry getOrDefault ["state", YSF_FW_STATE_STOWED];
    if (!(_state isEqualTo YSF_FW_STATE_STOWED)) exitWith {
        diag_log format [
            "[YSF][FWDBG] scope=SERVER owner=%1 deploySkipped id=%2 state=%3",
            clientOwner,
            _id,
            _state
        ];
        _entry getOrDefault ["spawnedVeh", objNull]
    };

    diag_log format [
        "[YSF][FWDBG] scope=SERVER owner=%1 deployStart id=%2 state=%3 caller=%4 vehicleType=%5",
        clientOwner,
        _id,
        _state,
        if (isNull _caller) then {"<null>"} else {format ["%1/%2", name _caller, netId _caller]},
        _entry getOrDefault ["vehicleType", ""]
    ];

    _entry set ["state", YSF_FW_STATE_DEPLOYING];
    _entry set ["lastUpdate", serverTime];
	[YSF_FW_REGISTRY_TOKEN, _id, _entry] call YSF_fwSetEntryPrivate;
    diag_log format [
        "[YSF][FWDBG] scope=SERVER owner=%1 deployPrepared id=%2 state=%3 visibility=private_only",
        clientOwner,
        _id,
        _entry getOrDefault ["state", ""]
    ];

    private _spawnPos = _entry getOrDefault ["infilPosASL", ["infil"] call YSF_fwDefaultPos];
    private _heading = _entry getOrDefault ["heading", 0];
    private _snapshot = _entry getOrDefault ["snapshot", []];
    if (_snapshot isEqualTo []) exitWith {
        _entry set ["state", YSF_FW_STATE_STOWED];
        _entry set ["lastUpdate", serverTime];
		[YSF_FW_REGISTRY_TOKEN, _id, _entry] call YSF_fwSetEntry;
        diag_log format [
            "[YSF][FWDBG] scope=SERVER owner=%1 deployAbort id=%2 reason=no_snapshot",
            clientOwner,
            _id
        ];
        objNull
    };

    private _spawnTarget = if (!isNull _caller) then {getPosASL _caller} else {_spawnPos};
    private _veh = [_spawnPos, _snapshot, _heading, (_spawnPos select 2), _spawnTarget, -1] call YOSHI_PASTE_VEHICLE;
    diag_log format [
        "[YSF][FWDBG] scope=SERVER owner=%1 deploySpawn id=%2 veh=%3 vehNetId=%4 vehOwner=%5 crew=%6 spawnPos=%7 target=%8",
        clientOwner,
        _id,
        if (isNull _veh) then {"<null>"} else {typeOf _veh},
        if (isNull _veh) then {"<null>"} else {netId _veh},
        if (isNull _veh) then {-1} else {owner _veh},
        if (isNull _veh) then {0} else {count crew _veh},
        _spawnPos,
        _spawnTarget
    ];
    _veh setVariable ["YSF_FW_ID", _id, false];

    private _center = _spawnTarget;
    [_veh, _center] call YSF_fwSetLoiter;
    _veh setVariable ["YSF_FW_LOITER_CENTER_ASL", _center, false];

    _entry set ["spawnedVeh", _veh];
    _entry set ["state", YSF_FW_STATE_ON_STATION];
    _entry set ["lastUpdate", serverTime];
	[YSF_FW_REGISTRY_TOKEN, _id, _entry] call YSF_fwSetEntry;
    [_requestId, true, "accepted", _requestOwner, _id] call YSF_fwDeployAck;
    diag_log format [
        "[YSF][FWDBG] scope=SERVER owner=%1 deployCommitted id=%2 finalState=%3 vehNetId=%4",
        clientOwner,
        _id,
        _entry getOrDefault ["state", ""],
        if (isNull _veh) then {"<null>"} else {netId _veh}
    ];
    [_id, _veh, _caller, 500, 10] call YSF_fwMonitorCallerLoiter;

    _veh
};

YSF_fwLogisticsAck = {
    params ["_requestId", "_accepted", "_reason", ["_owner", 0], ["_assetId", ""]];
    if (!isServer || {_requestId isEqualTo ""}) exitWith {};
    private _payload = [_accepted isEqualTo true, _reason, _assetId, serverTime];
    missionNamespace setVariable [format ["YSF_FW_LOGISTICS_ACK_%1", _requestId], _payload, _owner];
};

YSF_fwLogisticsEvent = {
    params ["_taskId", "_phase", "_assetId", "_aircraft", "_containers", "_targetATL", ["_details", []]];
    if (!isServer) exitWith {};
    private _event = [
        _taskId,
        _phase,
        _assetId,
        if (isNull _aircraft) then {""} else {netId _aircraft},
        _containers apply {if (isNull _x) then {""} else {netId _x}},
        _targetATL,
        _details,
        serverTime
    ];
    private _history = missionNamespace getVariable ["YSF_FW_LOGISTICS_EVENTS", []];
    _history pushBack _event;
    missionNamespace setVariable ["YSF_FW_LOGISTICS_EVENTS", _history, false];
    // Keep high-frequency ingress evidence server-private. Clients need the
    // physical identities and terminal state, not every trajectory sample.
    private _publicDetails = _details;
    if (_phase isEqualTo "released") then {
        _publicDetails = [_details param [0, []], count (_details param [1, []])];
    };
    if (_phase isEqualTo "failed") then {
        _publicDetails = [_details param [0, "unknown"]];
    };
    private _publicEvent = +_event;
    _publicEvent set [6, _publicDetails];
    missionNamespace setVariable ["YSF_FW_LOGISTICS_LAST_EVENT", _publicEvent, true];
    diag_log format ["YSF_FW_LOGISTICS|%1|%2|asset=%3|aircraft=%4|cargo=%5|target=%6|details=%7", _taskId, _phase, _assetId, _event # 3, _event # 4, _targetATL, _publicDetails];
};

YSF_fwLogisticsSetIdle = {
    params ["_assetId", "_taskId", "_result"];
    if (!isServer) exitWith {};
    private _entry = [_assetId] call YSF_fwGetEntry;
    if !(typeName _entry isEqualTo "HASHMAP") exitWith {};
    if ((_entry getOrDefault ["logisticsTaskId", ""]) isEqualTo _taskId) then {
        _entry set ["logisticsActive", false];
        _entry set ["logisticsTaskId", ""];
        _entry set ["lastLogisticsResult", _result];
        _entry set ["lastUpdate", serverTime];
		[YSF_FW_REGISTRY_TOKEN, _assetId, _entry] call YSF_fwSetEntry;
    };
};

YSF_fwRunLogisticsTask = {
    params ["_assetId", "_taskId", "_aircraft", "_containers", "_targetATL"];
    if (!isServer) exitWith {};

    [_assetId, _taskId, _aircraft, _containers, _targetATL] spawn {
        params ["_assetId", "_taskId", "_aircraft", "_containers", "_targetATL"];
        private _fail = {
            params ["_reason", ["_details", []]];
            [_taskId, "failed", _assetId, _aircraft, _containers, _targetATL, [_reason, _details]] call YSF_fwLogisticsEvent;
            [_assetId, _taskId, [false, _reason]] call YSF_fwLogisticsSetIdle;
            [_assetId] call YSF_fwRtbAsset;
        };

        private _ownershipDeadline = diag_tickTime + 15;
        {
            private _tree = [_x] + attachedObjects _x;
            { _x setOwner 2; } forEach _tree;
        } forEach _containers;
        waitUntil {
            uiSleep 0.05;
            (_containers findIf {!local _x || {(attachedObjects _x) findIf {!local _x} >= 0}}) < 0
            || {diag_tickTime > _ownershipDeadline}
        };
        if ((_containers findIf {isNull _x || {!local _x} || {(attachedObjects _x) findIf {!local _x} >= 0}}) >= 0) exitWith {
            ["cargo_locality_timeout", _containers apply {[netId _x, local _x, owner _x, attachedObjects _x apply {[netId _x, local _x, owner _x]}]}] call _fail;
        };

        private _group = group _aircraft;
        if (isNull _group) exitWith {["aircraft_group_missing"] call _fail};
        for "_i" from (count waypoints _group - 1) to 0 step -1 do {
            deleteWaypoint [_group, _i];
        };
        private _waypoint = _group addWaypoint [[_targetATL # 0, _targetATL # 1, 0], 0];
        _waypoint setWaypointType "MOVE";
        _waypoint setWaypointSpeed "NORMAL";
        _group setCurrentWaypoint _waypoint;
        _group setBehaviourStrong "CARELESS";
        _group setCombatMode "BLUE";
        _aircraft flyInHeight YSF_FW_LOGISTICS_FLIGHT_HEIGHT;
        private _targetASLAltitude = (getTerrainHeightASL _targetATL) + YSF_FW_LOGISTICS_FLIGHT_HEIGHT;
        _aircraft flyInHeightASL [_targetASLAltitude, _targetASLAltitude, _targetASLAltitude];
        [_taskId, "ingress", _assetId, _aircraft, _containers, _targetATL, [getPosASL _aircraft, local _aircraft, owner _aircraft, count crew _aircraft]] call YSF_fwLogisticsEvent;

        private _ingressSamples = [];
        private _ingressDeadline = diag_tickTime + YSF_FW_LOGISTICS_INGRESS_TIMEOUT;
        waitUntil {
            if (!isNull _aircraft) then {
                _ingressSamples pushBack [diag_tickTime, getPosATL _aircraft, getPosASL _aircraft, velocity _aircraft, _aircraft distance2D _targetATL, local _aircraft, owner _aircraft];
            };
            uiSleep 0.1;
            isNull _aircraft
            || {!alive _aircraft}
            || {
                _aircraft distance2D _targetATL <= YSF_FW_LOGISTICS_RELEASE_RADIUS
                && {((getPosASL _aircraft) # 2) - (getTerrainHeightASL getPosASL _aircraft) <= (YSF_FW_LOGISTICS_FLIGHT_HEIGHT + YSF_FW_LOGISTICS_RELEASE_ALTITUDE_TOLERANCE)}
            }
            || {diag_tickTime > _ingressDeadline}
        };
        if (isNull _aircraft || {!alive _aircraft}) exitWith {["aircraft_lost", _ingressSamples] call _fail};
        if (diag_tickTime > _ingressDeadline) exitWith {["ingress_timeout", _ingressSamples] call _fail};
        if (isNil "YFU_beginPhysicalAirdrop") exitWith {["airdrop_api_missing"] call _fail};

        private _aircraftBox = boundingBoxReal _aircraft;
        private _aircraftHeight = abs (((_aircraftBox # 1) # 2) - ((_aircraftBox # 0) # 2));
        private _releaseBase = (getPosASL _aircraft) vectorAdd [0, 0, -((_aircraftHeight / 2) + 4)];
        private _releaseRows = [];
        private _launchOk = true;
        {
            private _offset = [(_forEachIndex mod 2) * 1.5, floor (_forEachIndex / 2) * 1.5, 0];
            private _releaseASL = _releaseBase vectorAdd _offset;
            private _ok = [_x, _targetATL, _releaseASL, _taskId, _forEachIndex, 160] call YFU_beginPhysicalAirdrop;
            _launchOk = _launchOk && {_ok};
            _releaseRows pushBack [netId _x, _releaseASL, local _x, owner _x];
            if (_forEachIndex < ((count _containers) - 1)) then {uiSleep 1};
        } forEach _containers;
        [_taskId, "released", _assetId, _aircraft, _containers, _targetATL, [_releaseRows, _ingressSamples]] call YSF_fwLogisticsEvent;
        if (!_launchOk) exitWith {["release_failed", _releaseRows] call _fail};

        private _deliveryDeadline = diag_tickTime + YSF_FW_LOGISTICS_DELIVERY_TIMEOUT;
        private _results = [];
        waitUntil {
            _results = [];
            {
                private _resultVariable = [_taskId, _forEachIndex] call YFU_airdropResultVariable;
                private _result = missionNamespace getVariable [_resultVariable, []];
                if (_result isNotEqualTo []) then {_results pushBack _result};
            } forEach _containers;
            uiSleep 0.1;
            (count _results) isEqualTo (count _containers)
            || {diag_tickTime > _deliveryDeadline}
        };
        if ((count _results) isNotEqualTo (count _containers)) exitWith {["delivery_timeout", _results] call _fail};
        if ((_results findIf {(_x param [1, ""]) isNotEqualTo "landed"}) >= 0) exitWith {["delivery_failed", _results] call _fail};

        private _resultSummary = _results apply {[_x # 0, _x # 1, _x # 2, _x # 3, _x # 4, _x # 5, _x # 6, _x # 7, _x # 9, _x # 10]};
        [_taskId, "completed", _assetId, _aircraft, _containers, _targetATL, _resultSummary] call YSF_fwLogisticsEvent;
        [_assetId, _taskId, [true, "completed", _resultSummary]] call YSF_fwLogisticsSetIdle;
        [_assetId] call YSF_fwRtbAsset;
    };
};

// One authoritative capability decision shared by Vigil's task endpoint and
// Field Utilities' airdrop preparation. The returned entry remains
// server-private; callers consume only this current-state verdict.
YSF_fwValidateLogisticsAsset = {
	params ["_aircraft", "_requester"];
	if (!isServer) exitWith {[false, "not_server", "", objNull]};
	if (isNull _aircraft || {!alive _aircraft}) exitWith {[false, "aircraft_unavailable", "", objNull]};
	if (isNull _requester || {!isPlayer _requester} || {!alive _requester}) exitWith {[false, "invalid_requester", "", objNull]};

	private _registry = call YSF_fwEnsureRegistry;
	private _assetId = "";
	private _entry = objNull;
	{
		private _candidate = _y;
		if (typeName _candidate isEqualTo "HASHMAP" && {(_candidate getOrDefault ["spawnedVeh", objNull]) isEqualTo _aircraft}) exitWith {
			_assetId = _x;
			_entry = _candidate;
		};
	} forEach _registry;
	if (_assetId isEqualTo "" || {typeName _entry isNotEqualTo "HASHMAP"}) exitWith {[false, "aircraft_not_registered", "", objNull]};
	if ((_entry getOrDefault ["state", ""]) isNotEqualTo YSF_FW_STATE_ON_STATION) exitWith {[false, "aircraft_not_on_station", _assetId, _entry]};
	private _roleMask = _entry getOrDefault ["roleMask", 0];
	if ((((floor (_roleMask / YSF_FW_ROLE_LOGI)) mod 2) isNotEqualTo 1)) exitWith {[false, "aircraft_not_logistics", _assetId, _entry]};
	if ((_entry getOrDefault ["side", sideUnknown]) isNotEqualTo side _requester) exitWith {[false, "wrong_side", _assetId, _entry]};
	if (_entry getOrDefault ["logisticsActive", false]) exitWith {[false, "duplicate_active_task", _assetId, _entry]};
	[true, "eligible", _assetId, _entry]
};

YSF_fwRequestLogistics = {
    params ["_aircraftRef", "_containerRefs", "_targetATL", "_requestId", ["_requesterRef", ""]];
    if (!isServer) exitWith {
        [_aircraftRef, _containerRefs, _targetATL, _requestId, _requesterRef] remoteExecCall ["YSF_fwRequestLogistics", 2];
        false
    };

    private _requestOwner = remoteExecutedOwner;
    private _reject = {
        params ["_reason", ["_assetId", ""]];
        [_requestId, false, _reason, _requestOwner, _assetId] call YSF_fwLogisticsAck;
        false
    };
    if !(_requestId isEqualType "" && {_requestId isNotEqualTo ""}) exitWith {false};
    if !(_targetATL isEqualType [] && {(count _targetATL) >= 3}) exitWith {["invalid_destination"] call _reject};
    if ((_targetATL # 0) < 0 || {(_targetATL # 1) < 0} || {(_targetATL # 0) > worldSize} || {(_targetATL # 1) > worldSize}) exitWith {["invalid_destination"] call _reject};
    if !(_containerRefs isEqualType [] && {_containerRefs isNotEqualTo []}) exitWith {["empty_manifest"] call _reject};

    private _aircraft = [_aircraftRef] call YSF_fwResolveObjectRef;
    if (isNull _aircraft || {!alive _aircraft}) exitWith {["aircraft_unavailable"] call _reject};
    private _requester = [_requesterRef] call YSF_fwResolveObjectRef;
    if (isNull _requester || {!isPlayer _requester} || {owner _requester isNotEqualTo _requestOwner}) exitWith {["invalid_requester"] call _reject};

	private _assetVerdict = [_aircraft, _requester] call YSF_fwValidateLogisticsAsset;
	if !(_assetVerdict # 0) exitWith {[_assetVerdict # 1, _assetVerdict # 2] call _reject};
	private _assetId = _assetVerdict # 2;
	private _entry = _assetVerdict # 3;

    private _containers = _containerRefs apply {[_x] call YSF_fwResolveObjectRef};
    if ((_containers findIf {isNull _x || {!alive _x}}) >= 0) exitWith {["invalid_manifest_object", _assetId] call _reject};
    private _containerIds = _containers apply {netId _x};
    if ((count (_containerIds arrayIntersect _containerIds)) isNotEqualTo (count _containerIds)) exitWith {["duplicate_manifest_object", _assetId] call _reject};

    _entry set ["logisticsActive", true];
    _entry set ["logisticsTaskId", _requestId];
    _entry set ["lastUpdate", serverTime];
	[YSF_FW_REGISTRY_TOKEN, _assetId, _entry] call YSF_fwSetEntry;
    [_requestId, true, "accepted", _requestOwner, _assetId] call YSF_fwLogisticsAck;
    [_requestId, "accepted", _assetId, _aircraft, _containers, _targetATL, [netId _requester, _requestOwner]] call YSF_fwLogisticsEvent;
    [_assetId, _requestId, _aircraft, _containers, _targetATL] call YSF_fwRunLogisticsTask;
    true
};

YSF_fwFinalizeRtb = {
    params ["_id", "_vehicle", ["_result", "success"]];
    if (!isServer) exitWith {};

    private _entry = [_id] call YSF_fwGetEntry;
    if !(typeName _entry isEqualTo "HASHMAP") exitWith {};

    if (!isNull _vehicle && {alive _vehicle}) then {
        private _newSnapshot = [_vehicle] call YOSHI_COPY_VEHICLE;
        private _cooldownSeconds = [_entry, _vehicle, _newSnapshot] call YSF_fwComputeCooldownSeconds;
        _entry set ["snapshot", _newSnapshot];
        _entry set ["cooldownSeconds", _cooldownSeconds];
        if (_cooldownSeconds > 0) then {
            _entry set ["state", YSF_FW_STATE_COOLDOWN];
            _entry set ["cooldownUntil", serverTime + _cooldownSeconds];
        } else {
            _entry set ["state", YSF_FW_STATE_STOWED];
            _entry set ["cooldownUntil", -1];
        };
    } else {
        _entry set ["state", YSF_FW_STATE_STOWED];
        _entry set ["cooldownSeconds", 0];
        _entry set ["cooldownUntil", -1];
    };

    [_vehicle] call YSF_fwDeleteVehicleAndCrew;

    _entry set ["spawnedVeh", objNull];
    _entry set ["lastRtbResult", _result];
    _entry set ["lastUpdate", serverTime];
	[YSF_FW_REGISTRY_TOKEN, _id, _entry] call YSF_fwSetEntry;
};

YSF_fwRtbMonitor = {
    params ["_id", "_vehicle", "_exfilPosASL"];
    if (!isServer) exitWith {};

    private _deadline = serverTime + (YSF_FW_RTB_TIMEOUT max 1);

    [{
        params ["_args", "_handle"];
        _args params ["_id", "_vehicle", "_exfilPosASL", "_deadline"];

        if (isNull _vehicle || {!alive _vehicle}) exitWith {
            [_handle] call CBA_fnc_removePerFrameHandler;
            [_id, _vehicle, "destroyed"] call YSF_fwFinalizeRtb;
        };

        if ((_vehicle distance2D _exfilPosASL) < 600) exitWith {
            [_handle] call CBA_fnc_removePerFrameHandler;
            [_id, _vehicle, "success"] call YSF_fwFinalizeRtb;
        };

        if (serverTime >= _deadline) exitWith {
            [_handle] call CBA_fnc_removePerFrameHandler;
            diag_log format [
                "[YSF][FW] RTB timed out: id=%1 vehicle=%2 distance=%3 deadline=%4",
                _id,
                if (isNull _vehicle) then {"<null>"} else {netId _vehicle},
                if (isNull _vehicle) then {-1} else {_vehicle distance2D _exfilPosASL},
                _deadline
            ];
            [_id, _vehicle, "timeout"] call YSF_fwFinalizeRtb;
        };
    }, 2, [_id, _vehicle, _exfilPosASL, _deadline]] call CBA_fnc_addPerFrameHandler;
};

YSF_fwRtbAsset = {
    params ["_id"];

    if (!isServer) exitWith {
        [_id] remoteExecCall ["YSF_fwRtbAsset", 2];
        false
    };

    private _entry = [_id] call YSF_fwGetEntry;
    if !(typeName _entry isEqualTo "HASHMAP") exitWith {false};

    private _vehicle = _entry getOrDefault ["spawnedVeh", objNull];
    if (isNull _vehicle || {!alive _vehicle}) exitWith {
        _entry set ["spawnedVeh", objNull];
        _entry set ["state", YSF_FW_STATE_STOWED];
		[YSF_FW_REGISTRY_TOKEN, _id, _entry] call YSF_fwSetEntry;
        true
    };

    private _exfil = _entry getOrDefault ["exfilPosASL", ["exfil"] call YSF_fwDefaultPos];
    _entry set ["state", YSF_FW_STATE_RTB];
    _entry set ["lastUpdate", serverTime];
	[YSF_FW_REGISTRY_TOKEN, _id, _entry] call YSF_fwSetEntry;

    private _grp = group _vehicle;
    if (!isNull _grp) then {
        for "_i" from (count waypoints _grp - 1) to 0 step -1 do {
            deleteWaypoint [_grp, _i];
        };
        private _wp = _grp addWaypoint [[_exfil select 0, _exfil select 1, 0], 0];
        _wp setWaypointType "MOVE";
        _wp setWaypointSpeed "FULL";
        _grp setCurrentWaypoint _wp;
        _grp setBehaviourStrong "CARELESS";
        _grp setCombatMode "BLUE";
    };

    _vehicle flyInHeightASL [_exfil select 2, _exfil select 2, _exfil select 2];
    _vehicle flyInHeight (_exfil select 2);

    [_id, _vehicle, _exfil] call YSF_fwRtbMonitor;
    true
};

YSF_fwGetRegistrySnapshot = {
    if (isServer) then {
        private _reg = call YSF_fwEnsureRegistry;
        private _dirty = false;
        {
            private _entry = _y;
            if ((_entry getOrDefault ["state", ""]) isEqualTo YSF_FW_STATE_COOLDOWN) then {
                private _until = _entry getOrDefault ["cooldownUntil", -1];
                if (_until > -1 && {serverTime >= _until}) then {
                    _entry set ["state", YSF_FW_STATE_STOWED];
                    _entry set ["cooldownUntil", -1];
                    _entry set ["cooldownSeconds", 0];
                    _entry set ["lastUpdate", serverTime];
                    _reg set [_x, _entry];
                    _dirty = true;
                };
            };
        } forEach _reg;
        if (_dirty) then {
			[YSF_FW_REGISTRY_TOKEN, _reg] call YSF_fwCommitRegistry;
        };
    };

    private _out = [];
    {
        if (_x isEqualType [] && {(count _x) >= 5}) then {
            _out pushBack [
                _x select 0,
                _x select 1,
                _x select 2,
                _x select 3,
                _x select 4
            ];
        };
    } forEach (call YSF_fwGetPublicRegistry);
    _out
};

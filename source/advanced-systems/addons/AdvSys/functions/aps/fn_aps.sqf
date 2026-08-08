// Active Protection System
// LORICA
// Layered
// Omnidirectional
// Reactive
// Interception &
// Countermeasure
// Array

/*
St. Michael the Archangel,
defend us in battle.
Be our protection against the wickedness and snares of the devil.
May God rebuke him, we humbly pray;
and do thou, O Prince of the heavenly host,
by the power of God,
cast into hell Satan and all the evil spirits
who prowl about the world seeking the ruin of souls.
Amen.
*/

YOSHI_APS_HARDKILL_MAG_CLASS = "1Rnd_HE_Grenade_shell";
YOSHI_APS_DEFAULT_HARDKILL_CHARGES = 40;
YOSHI_APS_SOFTKILL_FUEL_COST = 0.02; // 2% absolute tank capacity per use
YOSHI_APS_PROJECTILE_PFH_INTERVAL = 0;
YOSHI_APS_PROJECTILE_TRACK_TTL = 15;
YOSHI_APS_PROJECTILE_SEARCH_RADIUS = 150;
YOSHI_APS_PROJECTILE_TTI_MAX = 0.25;
YOSHI_APS_PROJECTILE_MISS_MARGIN = 3;
YOSHI_APS_HARDKILL_TRIGGER_SOUNDS = ["ApsHardKillShot2", "ApsHardKillShot3", "ApsHardKillShot4"];
YOSHI_APS_SOFTKILL_TRIGGER_SOUNDS = ["ApsSoftKillGlitch1", "ApsSoftKillGlitch2", "ApsSoftKillGlitch3", "ApsSoftKillGlitch4", "ApsSoftKillGlitch5"];
YOSHI_APS_ANTIDRONE_TRIGGER_SOUNDS = ["ApsDronePulse1", "ApsDronePulse2"];

YOSHI_effects = {
    params ["_posATL"];

    private _ps1 = "#particlesource" createVehicleLocal _posATL;
    _ps1 setParticleParams [
        ["\A3\Data_F\ParticleEffects\Universal\Universal", 16, 10, 32], "", "Billboard",
        1, 1, [0, 0, 0], [0, 0, 0.5], 0, 1, 1, 3, [0.5,1.5],
        [[1,1,1,0.4], [1,1,1,0.2], [1,1,1,0]],
        [0.25,1], 1, 1, "", "", _ps1
    ];
    _ps1 setParticleRandom [0.2, [0.5, 0.5, 0.25], [0.125, 0.125, 0.125], 0.2, 0.2, [0, 0, 0, 0], 0, 0];
    _ps1 setDropInterval 0.05;

    private _ps2 = "#particlesource" createVehicleLocal _posATL;
    _ps2 setParticleParams [
        ["\A3\Data_F\ParticleEffects\Universal\Universal", 16, 7, 16, 1], "", "Billboard",
        1, 8, [0, 0, 0], [0, 0, 1.5], 0, 10, 7.9, 0.066, [1, 3, 6],
        [[0, 0, 0, 0], [0.05, 0.05, 0.05, 1], [0.05, 0.05, 0.05, 1], [0.05, 0.05, 0.05, 1], [0.1, 0.1, 0.1, 0.5], [0.125, 0.125, 0.125, 0]],
        [0.25], 1, 0, "", "", _ps2
    ];
    _ps2 setParticleRandom [0, [0.25, 0.25, 0], [0.2, 0.2, 0], 0, 0.25, [0, 0, 0, 0.1], 0, 0];
    _ps2 setDropInterval 0.05;

    sleep 0.1;
    deleteVehicle _ps1;
    deleteVehicle _ps2;
};

YOSHI_animateAPS = {
    params ["_aps", "_obj", ["_pulseCount", 5], ["_pulseDurationOn", 0.05], ["_pulseDurationOff", 0.05], ["_color", [1, 0, 0, 1]], ["_width", 10], ["_soundName", "ApsHit"], ["_playEffects", true], ["_soundDistance", 200]];

    if (_aps getVariable ["YOSHI_APS_VoiceEnabled", true]) then {
        [[_aps, _soundName, _soundDistance, 2], YOSHI_serverSay3dOnce] remoteExec ["spawn", 2];
    };
    [[_aps, getPosATL _obj, _pulseCount, _pulseDurationOn, _pulseDurationOff, _color, _width], YOSHI_serverBeamVic2Pos] remoteExec ["spawn", 2];
    if (_playEffects) then {
        [[_obj modelToWorld [0,0,0]], YOSHI_effects] remoteExec ["spawn", 2];
    };
};

YOSHI_fnc_apsSelectTriggerSound = {
    params [["_mode", ""]];

    private _modeKey = toLowerANSI _mode;
    private _pool = switch (_modeKey) do {
        case "hardkill": {YOSHI_APS_HARDKILL_TRIGGER_SOUNDS};
        case "softkill": {YOSHI_APS_SOFTKILL_TRIGGER_SOUNDS};
        case "drone": {YOSHI_APS_ANTIDRONE_TRIGGER_SOUNDS};
        default {[]};
    };

    if !(_pool isEqualTo []) exitWith {
        selectRandom _pool
    };

    switch (_modeKey) do {
        case "hardkill": {"ApsHit"};
        case "softkill": {"ApsSoftKillGlitch1"};
        case "drone": {"ApsDrone"};
        default {"ApsHit"};
    }
};

YOSHI_fnc_apsHardKillChargeCount = {
    params ["_vehicle", ["_magClass", YOSHI_APS_HARDKILL_MAG_CLASS]];

    private _cargo = getMagazineCargo _vehicle;
    private _mags = _cargo select 0;
    private _counts = _cargo select 1;

    private _total = 0;
    for "_i" from 0 to ((count _mags) - 1) do {
        private _mag = _mags select _i;
        if (_mag isKindOf [_magClass, configFile >> "CfgMagazines"]) then {
            _total = _total + (_counts select _i);
        };
    };

    _total
};

YOSHI_fnc_apsTopUpHardKillCharges = {
    params ["_vehicle", ["_targetCharges", YOSHI_APS_DEFAULT_HARDKILL_CHARGES], ["_magClass", YOSHI_APS_HARDKILL_MAG_CLASS]];

    if (isNull _vehicle) exitWith {0};

    private _current = [_vehicle, _magClass] call YOSHI_fnc_apsHardKillChargeCount;
    private _toAdd = ((_targetCharges max 0) - _current) max 0;

    if (_toAdd > 0) then {
        _vehicle addMagazineCargoGlobal [_magClass, _toAdd];
    };

    _toAdd
};

YOSHI_fnc_apsConsumeHardKillCharge = {
    params ["_vehicle"];

    private _cargo = getMagazineCargo _vehicle;
    private _mags = _cargo select 0;
    private _counts = _cargo select 1;

    private _idx = -1;
    for "_i" from 0 to ((count _mags) - 1) do {
        private _mag = _mags select _i;
        if (
            _mag isKindOf [YOSHI_APS_HARDKILL_MAG_CLASS, configFile >> "CfgMagazines"] &&
            {(_counts select _i) > 0}
        ) exitWith {
            _idx = _i;
        };
    };
    if (_idx < 0) exitWith {false};

    private _oldCount = _counts select _idx;
    if (_oldCount <= 0) exitWith {false};

    _counts set [_idx, _oldCount - 1];

    clearMagazineCargoGlobal _vehicle;
    for "_i" from 0 to ((count _mags) - 1) do {
        private _mag = _mags select _i;
        private _cnt = _counts select _i;
        if (_cnt > 0) then {
            _vehicle addMagazineCargoGlobal [_mag, _cnt];
        };
    };

    true
};

YOSHI_fnc_apsSoftKillChargeCount = {
    params ["_vehicle"];

    floor ((fuel _vehicle) / YOSHI_APS_SOFTKILL_FUEL_COST)
};

YOSHI_fnc_apsConsumeSoftKillCharge = {
    params ["_vehicle"];

    private _fuelNow = fuel _vehicle;
    if (_fuelNow < YOSHI_APS_SOFTKILL_FUEL_COST) exitWith {false};

    _vehicle setFuel ((_fuelNow - YOSHI_APS_SOFTKILL_FUEL_COST) max 0);
    true
};

YOSHI_fnc_apsNotifyPlayer = {
    params ["_player", "_msg"];

    if (isNull _player) exitWith {};
    [_msg] remoteExecCall ["hint", _player];
};

YOSHI_fnc_apsScheduleDelete = {
    params ["_object", ["_delay", 30]];

    if (isNull _object) exitWith {false};
    if (_object getVariable ["YOSHI_APS_DeleteScheduled", false]) exitWith {false};

    _object setVariable ["YOSHI_APS_DeleteScheduled", true, true];

    [_object, _delay] spawn {
        params ["_object", "_delay"];
        sleep (_delay max 0);

        if (!isNull _object) then {
            deleteVehicle _object;
        };
    };

    true
};

YOSHI_fnc_apsCancelVoice = {
    params ["_vehicle"];

    if (isNull _vehicle) exitWith {};

    private _thread = _vehicle getVariable ["YOSHI_APS_VoiceSeqThread", scriptNull];
    if (!scriptDone _thread) then {
        terminate _thread;
    };

    private _nonce = _vehicle getVariable ["YOSHI_APS_VoiceNonce", 0];
    _vehicle setVariable ["YOSHI_APS_VoiceNonce", _nonce + 1, true];
    _vehicle setVariable ["YOSHI_APS_VoiceSeqThread", scriptNull];
    [_vehicle] call YOSHI_fnc_apsStopSoundGlobal;
};

YOSHI_fnc_apsLocalStopSound = {
    params ["_vehicle"];

    if (isNull _vehicle) exitWith {};
    private _src = _vehicle getVariable ["YOSHI_APS_VoiceSource_Local", objNull];
    if (!isNull _src) then {
        deleteVehicle _src;
        _vehicle setVariable ["YOSHI_APS_VoiceSource_Local", objNull];
    };
};

YOSHI_fnc_apsLocalStartSound = {
    params ["_vehicle", "_sound", "_distance"];

    if (isNull _vehicle) exitWith {};

    // Hard-cut previous clip on this client.
    [_vehicle] call YOSHI_fnc_apsLocalStopSound;

    private _src = "Land_HelipadEmpty_F" createVehicleLocal [0,0,0];
    _src hideObject true;
    _src attachTo [_vehicle, [0,0,0]];
    _src say3D [_sound, _distance, 1];

    _vehicle setVariable ["YOSHI_APS_VoiceSource_Local", _src];
};

YOSHI_fnc_apsStopSoundGlobal = {
    params ["_vehicle"];

    if (isNull _vehicle) exitWith {};
    [_vehicle] remoteExecCall ["YOSHI_fnc_apsLocalStopSound", 0];
};

YOSHI_fnc_apsStartSoundGlobal = {
    params ["_vehicle", "_sound", "_distance"];

    if (isNull _vehicle) exitWith {};
    [_vehicle, _sound, _distance] remoteExecCall ["YOSHI_fnc_apsLocalStartSound", 0];
};

YOSHI_fnc_apsSaySound = {
    params ["_vehicle", "_sound", ["_distance", 200], ["_pause", -1], ["_force", false], ["_nonce", -1]];

    if (isNull _vehicle) exitWith {};
    if (_nonce >= 0 && {_nonce != (_vehicle getVariable ["YOSHI_APS_VoiceNonce", 0])}) exitWith {};

    private _voiceEnabled = _vehicle getVariable ["YOSHI_APS_VoiceEnabled", true];
    if (!_force && {!_voiceEnabled}) exitWith {};

    [_vehicle, _sound, _distance] call YOSHI_fnc_apsStartSoundGlobal;
    if (_pause < 0) then {
        _pause = [_sound] call YOSHI_fnc_apsGetSoundDuration;
    };
    sleep _pause + 0.1;
};

YOSHI_fnc_apsSaySequence = {
    params ["_vehicle", "_sounds", ["_distance", 50], ["_pause", -1], ["_force", false], ["_cull", true]];

    if (isNull _vehicle) exitWith {};

    if (_cull) then {
        [_vehicle] call YOSHI_fnc_apsCancelVoice;
    };

    private _nonce = _vehicle getVariable ["YOSHI_APS_VoiceNonce", 0];
    _vehicle setVariable ["YOSHI_APS_VoiceSeqThread", _thisScript];

    {
        if (_nonce != (_vehicle getVariable ["YOSHI_APS_VoiceNonce", 0])) exitWith {};
        [_vehicle, _x, _distance, _pause, _force, _nonce] call YOSHI_fnc_apsSaySound;
    } forEach _sounds;

    if (_nonce == (_vehicle getVariable ["YOSHI_APS_VoiceNonce", 0])) then {
        [_vehicle] call YOSHI_fnc_apsStopSoundGlobal;
        _vehicle setVariable ["YOSHI_APS_VoiceSeqThread", scriptNull];
    };
};

YOSHI_fnc_setVelocityLocal = {
    params ["_object", "_velocity"];

    if (isNull _object) exitWith {};

    if (!local _object) exitWith {
        ["YOSHI_fnc_setVelocityLocal", _object, [_object, _velocity]] call YCD_fnc_runOnObjectOwner;
    };

    _object setVelocity _velocity;
};

YOSHI_fnc_apsGetSoundDuration = {
    params ["_soundClass"];

    private _durations = createHashMapFromArray [
        ["ApsActiveProtectionSystem", 2.224],
        ["ApsAmmunitionAcquired", 1.884],
        ["ApsAmmunitionDepleted", 2.053],
        ["ApsDrone", 2.213],
        ["ApsHit", 0.501],
        ["ApsFail", 0.237],
        ["ApsInsufficientPower", 1.643],
        ["ApsPowerLevelIs", 2.153],
        ["ApsPercent", 0.762],
        ["ApsRemaining", 1.049],
        ["ApsSelfPropelledGrenade", 2.108],
        ["ApsActivated", 0.874],
        ["ApsDeactivated", 1.130],
        ["ApsExperimentalEnergyWeapon", 2.635],
        ["ApsOnline", 0.795],
        ["ApsVoiceOn", 2.815],
        ["ApsVoiceOff", 2.705],
        ["ApsSuccess", 0.109],
        ["one", 0.703],
        ["two", 0.674],
        ["three", 0.776],
        ["four", 0.776],
        ["five", 0.879],
        ["six", 0.832],
        ["seven", 0.744],
        ["eight", 0.580],
        ["nine", 0.832],
        ["ten", 0.582],
        ["eleven", 0.744],
        ["twelve", 0.800],
        ["thirteen", 0.996],
        ["fourteen", 0.940],
        ["fifteen", 0.982],
        ["sixteen", 1.038],
        ["seventeen", 1.059],
        ["eighteen", 0.809],
        ["nineteen", 0.906],
        ["twenty", 0.822],
        ["thirty", 0.867],
        ["forty", 0.903],
        ["fifty", 0.998],
        ["sixty", 0.991],
        ["seventy", 0.956],
        ["eighty", 0.708],
        ["ninety", 0.956],
        ["one_hundred", 0.987],
        ["comma", 0.249],
        ["period", 0.431]
    ];

    (_durations getOrDefault [_soundClass, 1.0]) + 0.12
};

YOSHI_fnc_apsAnnounceHardKillDepleted = {
    params ["_vehicle"];

    private _already = _vehicle getVariable ["YOSHI_APS_HardKill_EmptyAnnounced", false];
    if (_already) exitWith {};

    _vehicle setVariable ["YOSHI_APS_HardKill_EmptyAnnounced", true, true];
    [_vehicle, ["ApsSelfPropelledGrenade", "ApsAmmunitionDepleted"]] spawn YOSHI_fnc_apsSaySequence;
};

YOSHI_fnc_apsAnnounceInsufficientPower = {
    params ["_vehicle"];

    private _already = _vehicle getVariable ["YOSHI_APS_SoftKill_LowPowerAnnounced", false];
    if (_already) exitWith {};

    _vehicle setVariable ["YOSHI_APS_SoftKill_LowPowerAnnounced", true, true];
    [_vehicle, ["ApsInsufficientPower"]] spawn YOSHI_fnc_apsSaySequence;
};

YOSHI_fnc_apsStatusText = {
    params ["_vehicle"];

    private _hkEnabled = _vehicle getVariable ["YOSHI_APS_HardKill_Enabled", false];
    private _hkOnline = _vehicle getVariable ["YOSHI_APS_HardKill_Online", false];
    private _skEnabled = _vehicle getVariable ["YOSHI_APS_SoftKill_Enabled", false];

    private _hkState = if (_hkEnabled && _hkOnline) then {"ONLINE"} else {"OFFLINE"};
    private _skState = if (_skEnabled) then {"ENABLED"} else {"DISABLED"};

    private _hkCharges = [_vehicle] call YOSHI_fnc_apsHardKillChargeCount;
    private _skCharges = [_vehicle] call YOSHI_fnc_apsSoftKillChargeCount;

    format [
        "APS Status\nHard-Kill: %1 (%2 rounds of 40mm)\nSoft-Kill: %3 (%4 fuel-charges)",
        _hkState,
        _hkCharges,
        _skState,
        _skCharges
    ]
};

YOSHI_fnc_apsSetHardKillState = {
    params ["_vehicle", ["_enabled", true]];

    _vehicle setVariable ["YOSHI_APS_HardKill_Enabled", _enabled, true];
    _vehicle setVariable ["YOSHI_APS_HardKill_Online", _enabled, true];
    if (_enabled) then {
        _vehicle setVariable ["YOSHI_APS_HardKill_EmptyAnnounced", false, true];
    };
};

YOSHI_fnc_apsSetSoftKillState = {
    params ["_vehicle", ["_enabled", true]];

    _vehicle setVariable ["YOSHI_APS_SoftKill_Enabled", _enabled, true];
};

YOSHI_fnc_apsProjectileUid = {
    params ["_projectile"];

    if (isNull _projectile) exitWith {""};

    private _uid = netId _projectile;
    if (_uid isEqualTo "") then {
        _uid = str _projectile;
    };

    _uid
};

YOSHI_fnc_apsIsTrackableProjectile = {
    params ["_projectile"];

    if (isNull _projectile) exitWith {false};
    if (_projectile isKindOf "MissileBase") exitWith {true};
    if (_projectile isKindOf "RocketBase") exitWith {true};

    private _cfg = configOf _projectile;
    private _simulation = toLowerANSI getText (_cfg >> "simulation");
    _simulation in ["shotmissile", "shotrocket"]
};

YOSHI_fnc_apsVehicleThreatRadius = {
    params ["_vehicle"];

    if (isNull _vehicle) exitWith {0};

    private _bounds = boundingBoxReal _vehicle;
    (((_bounds select 0) distance (_bounds select 1)) * 0.5) max 2
};

YOSHI_fnc_apsEvaluateProjectileThreat = {
    params ["_vehicle", "_projectile"];

    if (isNull _vehicle || {isNull _projectile}) exitWith {[]};
    if (!alive _vehicle) exitWith {[]};
    if !(_vehicle getVariable ["YOSHI_APS_Enabled", false]) exitWith {[]};

    private _relativeDir = _projectile getRelDir _vehicle;
    if !((_relativeDir < 30) || (_relativeDir > 330)) exitWith {[]};

    private _velocity = velocity _projectile;
    private _speed = vectorMagnitude _velocity;
    if (_speed < 10) exitWith {[]};

    private _velocityDir = vectorNormalized _velocity;
    private _toVehicle = (getPosWorld _vehicle) vectorDiff (getPosWorld _projectile);
    private _forwardDistance = _toVehicle vectorDotProduct _velocityDir;
    if (_forwardDistance <= 0) exitWith {[]};

    private _tti = _forwardDistance / _speed;
    if (_tti > YOSHI_APS_PROJECTILE_TTI_MAX) exitWith {[]};

    private _missVector = _toVehicle vectorDiff (_velocityDir vectorMultiply _forwardDistance);
    private _missDistance = vectorMagnitude _missVector;
    private _threatRadius = ([_vehicle] call YOSHI_fnc_apsVehicleThreatRadius) + YOSHI_APS_PROJECTILE_MISS_MARGIN;
    if (_missDistance > _threatRadius) exitWith {[]};

    [_tti, _forwardDistance, _missDistance]
};

YOSHI_fnc_apsSelectProjectileResponse = {
    params ["_vehicle", "_projectile"];

    private _threat = [_vehicle, _projectile] call YOSHI_fnc_apsEvaluateProjectileThreat;
    if (_threat isEqualTo []) exitWith {[]};

    private _tti = _threat select 0;
    private _hardKillOnline =
        (_vehicle getVariable ["YOSHI_APS_HardKill_Enabled", false]) &&
        (_vehicle getVariable ["YOSHI_APS_HardKill_Online", false]) &&
        {([_vehicle] call YOSHI_fnc_apsHardKillChargeCount) > 0};

    if (_hardKillOnline) exitWith {["hardkill", _tti]};

    private _softKillEnabled = _vehicle getVariable ["YOSHI_APS_SoftKill_Enabled", false];
    if (_softKillEnabled && {(fuel _vehicle) >= YOSHI_APS_SOFTKILL_FUEL_COST}) exitWith {
        ["softkill", _tti]
    };

    []
};

YOSHI_fnc_apsConsumeHardKillChargeAuthoritative = {
    params ["_vehicle"];

    if (isNull _vehicle) exitWith {false};

    if (!local _vehicle) exitWith {
        ["YOSHI_fnc_apsConsumeHardKillChargeAuthoritative", _vehicle, [_vehicle]] call YCD_fnc_runOnObjectOwner;
        true
    };

    if !([_vehicle] call YOSHI_fnc_apsConsumeHardKillCharge) exitWith {false};

    if (([_vehicle] call YOSHI_fnc_apsHardKillChargeCount) <= 0) then {
        _vehicle setVariable ["YOSHI_APS_HardKill_Enabled", false, true];
        _vehicle setVariable ["YOSHI_APS_HardKill_Online", false, true];
        _vehicle setVariable ["YOSHI_APS_SoftKill_Enabled", true, true];
        [_vehicle] call YOSHI_fnc_apsAnnounceHardKillDepleted;
    };

    true
};

YOSHI_fnc_apsConsumeSoftKillChargeAuthoritative = {
    params ["_vehicle"];

    if (isNull _vehicle) exitWith {false};

    if (!local _vehicle) exitWith {
        ["YOSHI_fnc_apsConsumeSoftKillChargeAuthoritative", _vehicle, [_vehicle]] call YCD_fnc_runOnObjectOwner;
        true
    };

    if !([_vehicle] call YOSHI_fnc_apsConsumeSoftKillCharge) exitWith {
        _vehicle setVariable ["YOSHI_APS_SoftKill_Enabled", false, true];
        [_vehicle] call YOSHI_fnc_apsAnnounceInsufficientPower;
        false
    };

    if ((fuel _vehicle) < YOSHI_APS_SOFTKILL_FUEL_COST) then {
        _vehicle setVariable ["YOSHI_APS_SoftKill_Enabled", false, true];
        [_vehicle] call YOSHI_fnc_apsAnnounceInsufficientPower;
    };

    true
};

YOSHI_fnc_apsCommitIntercept = {
    params ["_vehicle", "_projectileUid", "_mode"];

    if (!isServer) exitWith {
        [_vehicle, _projectileUid, _mode] remoteExecCall ["YOSHI_fnc_apsCommitIntercept", 2];
        true
    };

    if (isNull _vehicle) exitWith {false};
    if (_projectileUid isEqualTo "") exitWith {false};

    private _vehicleUid = netId _vehicle;
    if (_vehicleUid isEqualTo "") then {
        _vehicleUid = str _vehicle;
    };

    private _onceKey = format ["YOSHI_APS_INTERCEPT|%1|%2|%3", _vehicleUid, _projectileUid, _mode];
    if !([_onceKey, 5] call YCD_fnc_claimOnceKey) exitWith {false};

    switch (toLowerANSI _mode) do {
        case "hardkill": {
            [_vehicle] call YOSHI_fnc_apsConsumeHardKillChargeAuthoritative;
        };
        case "softkill": {
            [_vehicle] call YOSHI_fnc_apsConsumeSoftKillChargeAuthoritative;
        };
    };

    true
};

YOSHI_fnc_apsInterceptProjectileHardKillLocal = {
    params ["_vehicle", "_projectile"];

    if (isNull _vehicle || {isNull _projectile}) exitWith {false};
    if (!local _projectile) exitWith {false};
    if (_projectile getVariable ["YOSHI_APS_InterceptedLocal", false]) exitWith {false};

    _projectile setVariable ["YOSHI_APS_InterceptedLocal", true];

    private _uid = [_projectile] call YOSHI_fnc_apsProjectileUid;
    private _stop = [_projectile, 1] call YOSHI_getFrontPosition;
    private _charge = "Land_Orange_01_F" createVehicleLocal _stop;
    private _triggerSound = ["hardkill"] call YOSHI_fnc_apsSelectTriggerSound;

    [_vehicle, _projectile, 5, 0.05, 0.05, [1, 0, 0, 1], 10, _triggerSound, true, 200] call YOSHI_animateAPS;

    _projectile setDamage 1;
    deleteVehicle _projectile;
    deleteVehicle _charge;

    [_vehicle, _uid, "hardkill"] remoteExecCall ["YOSHI_fnc_apsCommitIntercept", 2];
    true
};

YOSHI_fnc_apsInterceptProjectileSoftKillLocal = {
    params ["_vehicle", "_projectile"];

    if (isNull _vehicle || {isNull _projectile}) exitWith {false};
    if (!local _projectile) exitWith {false};
    if (_projectile getVariable ["YOSHI_APS_InterceptedLocal", false]) exitWith {false};

    private _relativeDir = _projectile getRelDir _vehicle;
    private _vecUp = vectorNormalized (vectorUp _projectile);
    private _toVehicle = vectorNormalized ((getPosWorld _vehicle) vectorDiff (getPosWorld _projectile));
    private _dot = _vecUp vectorDotProduct _toVehicle;
    private _yaw = 0;
    private _pitch = 0;

    if (_relativeDir < 5 || {_relativeDir > 355}) then {
        if (_dot > -0.1) then {
            _pitch = -45;
        } else {
            _pitch = -70;
        };

        if ((_relativeDir > 355) && {_relativeDir < 357}) then {
            _yaw = -10;
        };
        if ((_relativeDir < 5) && {_relativeDir > 2}) then {
            _yaw = 10;
        };
    } else {
        if ((_relativeDir < 355) && {_relativeDir > 330}) then {
            _yaw = -45;
        };
        if ((_relativeDir > 5) && {_relativeDir < 30}) then {
            _yaw = 45;
        };
    };

    private _velocity = velocity _projectile;
    private _speed = vectorMagnitude _velocity;
    if (_speed <= 0.1) exitWith {false};

    _projectile setVariable ["YOSHI_APS_InterceptedLocal", true];

    private _velocityDir = vectorNormalized _velocity;
    private _rotation = [[_velocityDir, [0, 0, 1]], _yaw, _pitch, 0] call BIS_fnc_transformVectorDirAndUp;
    private _newVelocityDir = _rotation select 0;
    private _triggerSound = ["softkill"] call YOSHI_fnc_apsSelectTriggerSound;

    [_projectile, (_newVelocityDir vectorMultiply _speed)] call YOSHI_fnc_setVelocityLocal;
    [_vehicle, _projectile, 1, 0.1, 0.1, [1, 1, 0, 1], 15, _triggerSound, false, 200] call YOSHI_animateAPS;

    private _uid = [_projectile] call YOSHI_fnc_apsProjectileUid;
    [_vehicle, _uid, "softkill"] remoteExecCall ["YOSHI_fnc_apsCommitIntercept", 2];
    true
};

YOSHI_fnc_apsTryInterceptProjectileLocal = {
    params ["_projectile"];

    if (isNull _projectile) exitWith {false};
    if (!local _projectile) exitWith {false};
    if !([_projectile] call YOSHI_fnc_apsIsTrackableProjectile) exitWith {false};
    if (_projectile getVariable ["YOSHI_APS_InterceptedLocal", false]) exitWith {false};

    private _candidates = nearestObjects [_projectile, ["LandVehicle", "Air", "Ship"], YOSHI_APS_PROJECTILE_SEARCH_RADIUS];
    private _selectedVehicle = objNull;
    private _selectedMode = "";
    private _selectedTti = 1e9;

    {
        private _response = [_x, _projectile] call YOSHI_fnc_apsSelectProjectileResponse;
        if !(_response isEqualTo []) then {
            private _mode = _response select 0;
            private _tti = _response select 1;
            if (_tti < _selectedTti) then {
                _selectedVehicle = _x;
                _selectedMode = _mode;
                _selectedTti = _tti;
            };
        };
    } forEach _candidates;

    if (isNull _selectedVehicle) exitWith {false};

    switch (_selectedMode) do {
        case "hardkill": {
            [_selectedVehicle, _projectile] call YOSHI_fnc_apsInterceptProjectileHardKillLocal
        };
        case "softkill": {
            [_selectedVehicle, _projectile] call YOSHI_fnc_apsInterceptProjectileSoftKillLocal
        };
        default {
            false
        };
    }
};

YOSHI_fnc_apsProcessTrackedProjectiles = {
    private _tracked = missionNamespace getVariable ["YOSHI_APS_TrackedProjectiles", []];
    if (_tracked isEqualTo []) exitWith {};

    private _remaining = [];
    {
        private _projectile = _x;
        if (
            !isNull _projectile &&
            {local _projectile} &&
            {!(_projectile getVariable ["YOSHI_APS_InterceptedLocal", false])}
        ) then {
            private _trackedAt = _projectile getVariable ["YOSHI_APS_TrackedAt", diag_tickTime];
            if (
                ((diag_tickTime - _trackedAt) <= YOSHI_APS_PROJECTILE_TRACK_TTL) &&
                {(vectorMagnitude (velocity _projectile)) >= 5}
            ) then {
                if !([_projectile] call YOSHI_fnc_apsTryInterceptProjectileLocal) then {
                    _remaining pushBack _projectile;
                };
            };
        };
    } forEach _tracked;

    missionNamespace setVariable ["YOSHI_APS_TrackedProjectiles", _remaining];
};

YOSHI_fnc_apsTrackProjectileLocal = {
    params ["_projectile"];

    if !([_projectile] call YOSHI_fnc_apsIsTrackableProjectile) exitWith {false};
    if (!local _projectile) exitWith {false};
    if (_projectile getVariable ["YOSHI_APS_TrackedLocal", false]) exitWith {false};

    _projectile setVariable ["YOSHI_APS_TrackedLocal", true];
    _projectile setVariable ["YOSHI_APS_TrackedAt", diag_tickTime];

    private _tracked = missionNamespace getVariable ["YOSHI_APS_TrackedProjectiles", []];
    _tracked pushBack _projectile;
    missionNamespace setVariable ["YOSHI_APS_TrackedProjectiles", _tracked];

    true
};

YOSHI_fnc_apsHandleFiredLocal = {
    params ["_unit", "_weapon", "_muzzle", "_mode", "_ammo", "_magazine", "_projectile"];

    [_projectile] call YOSHI_fnc_apsTrackProjectileLocal;
};

YOSHI_fnc_apsEnsureLocalRuntime = {
    if (missionNamespace getVariable ["YOSHI_APS_LocalRuntimeReady", false]) exitWith {true};
    if (isNil "CBA_fnc_addPerFrameHandler") exitWith {false};
    if (isNil "CBA_fnc_addClassEventHandler") exitWith {false};

    missionNamespace setVariable ["YOSHI_APS_LocalRuntimeReady", true];
    missionNamespace setVariable ["YOSHI_APS_TrackedProjectiles", []];

    {
        [_x, "Fired", {
            _this call YOSHI_fnc_apsHandleFiredLocal;
        }, true, [], true] call CBA_fnc_addClassEventHandler;
    } forEach ["CAManBase", "LandVehicle", "Air", "Ship"];

    private _pfhId = [{
        call YOSHI_fnc_apsProcessTrackedProjectiles;
    }, YOSHI_APS_PROJECTILE_PFH_INTERVAL, []] call CBA_fnc_addPerFrameHandler;

    missionNamespace setVariable ["YOSHI_APS_LocalTrackerPFH", _pfhId];
    true
};

YOSHI_detectDrones = {
    params ["_vehicle", ["_range", -1], ["_interval", 0.5], ["_cooldown", 0.5]];

    if (_range == -1) then {
        private _boundingBox = boundingBoxReal _vehicle;
        _range = ((_boundingBox select 0) distance (_boundingBox select 1)) * 2;
    };

    while {alive _vehicle && (_vehicle getVariable ["YOSHI_APS_Enabled", false])} do {
        private _antiDroneEnabled = _vehicle getVariable ["YOSHI_APS_AntiDrone_Enabled", true];
        if (!_antiDroneEnabled) then {
            sleep _interval;
            continue;
        };

        if ((fuel _vehicle) < YOSHI_APS_SOFTKILL_FUEL_COST) then {
            _vehicle setVariable ["YOSHI_APS_AntiDrone_Enabled", false, true];
            [_vehicle] call YOSHI_fnc_apsAnnounceInsufficientPower;
            sleep _interval;
            continue;
        };

        private _uavs = allUnitsUAV select { (_x isKindOf "Air") && ((getMass _x) < 1000) && ((_x distance _vehicle) <= _range) };
        {
            private _isHit = _x getVariable ["YOSHI_APS_HIT", false];
            if (abs (speed _x) > 40 && !_isHit) then {
                if !([_vehicle] call YOSHI_fnc_apsConsumeSoftKillChargeAuthoritative) exitWith {
                    _vehicle setVariable ["YOSHI_APS_AntiDrone_Enabled", false, true];
                    [_vehicle] call YOSHI_fnc_apsAnnounceInsufficientPower;
                };

                private _triggerSound = ["drone"] call YOSHI_fnc_apsSelectTriggerSound;
                [_vehicle, _x, 1, 0.2, 0.2, [0, 1, 1, 1], 15, _triggerSound, true, 300] call YOSHI_animateAPS;

                _x removeAllEventHandlers "Killed";
                _x removeAllEventHandlers "Hit";
                _x removeAllEventHandlers "HitPart";
                _x removeAllEventHandlers "HandleDamage";
                _x removeAllEventHandlers "Dammaged";
                _x removeAllEventHandlers "Deleted";
                _x removeAllEventHandlers "EpeContact";
                _x removeAllEventHandlers "EpeContactStart";
                _x removeAllEventHandlers "EpeContactEnd";
                _x removeAllEventHandlers "Fired";
                _x removeAllEventHandlers "LandedStopped";
                _x removeAllEventHandlers "Landing";
                _x removeAllEventHandlers "LandedTouchDown";
                _x setDamage [1, false];
                _x setVariable ["YOSHI_APS_HIT", true, true];
                [_x, 30] call YOSHI_fnc_apsScheduleDelete;

                sleep _cooldown;
            };
        } forEach _uavs;

        sleep _interval;
    };

    _vehicle setVariable ["YOSHI_APS_Drone_Thread", scriptNull];
};

YOSHI_fnc_apsHandleHardKillTurnOff = {
    params ["_vehicle", "_player"];

    if (!isServer) exitWith {};
    if (isNull _vehicle) exitWith {};

    private _isApsEnabled = _vehicle getVariable ["YOSHI_APS_Enabled", false];
    if (!_isApsEnabled) exitWith {
        [_player, "APS is not installed on this vehicle."] call YOSHI_fnc_apsNotifyPlayer;
    };

    [_vehicle, false] call YOSHI_fnc_apsSetHardKillState;
    [_player, "Hard-Kill APS turned OFF."] call YOSHI_fnc_apsNotifyPlayer;
};

YOSHI_fnc_apsHandleHardKillReboot = {
    params ["_vehicle", "_player"];

    if (!isServer) exitWith {};
    if (isNull _vehicle) exitWith {};

    private _isApsEnabled = _vehicle getVariable ["YOSHI_APS_Enabled", false];
    if (!_isApsEnabled) exitWith {
        [_player, "APS is not installed on this vehicle."] call YOSHI_fnc_apsNotifyPlayer;
    };

    private _charges = [_vehicle] call YOSHI_fnc_apsHardKillChargeCount;
    if (_charges > 0) then {
        [_vehicle, true] call YOSHI_fnc_apsSetHardKillState;
        [_vehicle, false] call YOSHI_fnc_apsSetSoftKillState;
        [_player, "Hard-Kill APS reboot successful."] call YOSHI_fnc_apsNotifyPlayer;
        private _tokens = [_charges] call YOSHI_numToTextArray;
        private _sequence = ["ApsSuccess"];
        _sequence append _tokens;
        _sequence pushBack "ApsSelfPropelledGrenade";
        _sequence pushBack "ApsAmmunitionAcquired";
        [_vehicle, _sequence] spawn YOSHI_fnc_apsSaySequence;
    } else {
        [_player, "Hard-Kill APS reboot failed: no compatible hard-kill charges in vehicle inventory."] call YOSHI_fnc_apsNotifyPlayer;
        [_vehicle, ["ApsFail"]] spawn YOSHI_fnc_apsSaySequence;
    };
};

YOSHI_fnc_apsHandleSoftKillTurnOn = {
    params ["_vehicle", "_player"];

    if (!isServer) exitWith {};
    if (isNull _vehicle) exitWith {};

    private _isApsEnabled = _vehicle getVariable ["YOSHI_APS_Enabled", false];
    if (!_isApsEnabled) exitWith {
        [_player, "APS is not installed on this vehicle."] call YOSHI_fnc_apsNotifyPlayer;
    };

    [_vehicle, true] call YOSHI_fnc_apsSetSoftKillState;
    [_player, "Soft-Kill APS turned ON."] call YOSHI_fnc_apsNotifyPlayer;
};

YOSHI_fnc_apsHandleSoftKillTurnOff = {
    params ["_vehicle", "_player"];

    if (!isServer) exitWith {};
    if (isNull _vehicle) exitWith {};

    private _isApsEnabled = _vehicle getVariable ["YOSHI_APS_Enabled", false];
    if (!_isApsEnabled) exitWith {
        [_player, "APS is not installed on this vehicle."] call YOSHI_fnc_apsNotifyPlayer;
    };

    [_vehicle, false] call YOSHI_fnc_apsSetSoftKillState;
    [_player, "Soft-Kill APS turned OFF."] call YOSHI_fnc_apsNotifyPlayer;
};

YOSHI_fnc_apsHandleVoiceTurnOn = {
    params ["_vehicle", "_player"];

    if (!isServer) exitWith {};
    if (isNull _vehicle) exitWith {};

    _vehicle setVariable ["YOSHI_APS_VoiceEnabled", true, true];
    [_player, "APS voice enabled."] call YOSHI_fnc_apsNotifyPlayer;
    [_vehicle, ["ApsVoiceOn"], 50, -1, true] spawn YOSHI_fnc_apsSaySequence;
};

YOSHI_fnc_apsHandleVoiceTurnOff = {
    params ["_vehicle", "_player"];

    if (!isServer) exitWith {};
    if (isNull _vehicle) exitWith {};

    [_vehicle] call YOSHI_fnc_apsCancelVoice;
    [_vehicle, ["ApsVoiceOff"], 50, -1, true, false] spawn YOSHI_fnc_apsSaySequence;
    _vehicle setVariable ["YOSHI_APS_VoiceEnabled", false, true];
    [_player, "APS voice disabled."] call YOSHI_fnc_apsNotifyPlayer;
};

YOSHI_fnc_apsHandleAntiDroneTurnOn = {
    params ["_vehicle", "_player"];

    if (!isServer) exitWith {};
    if (isNull _vehicle) exitWith {};

    if ((fuel _vehicle) < YOSHI_APS_SOFTKILL_FUEL_COST) exitWith {
        _vehicle setVariable ["YOSHI_APS_AntiDrone_Enabled", false, true];
        [_player, "Anti-Drone offline: insufficient fuel."] call YOSHI_fnc_apsNotifyPlayer;
        [_vehicle, ["ApsInsufficientPower"]] spawn YOSHI_fnc_apsSaySequence;
    };

    _vehicle setVariable ["YOSHI_APS_AntiDrone_Enabled", true, true];
    [_player, "Anti-Drone online."] call YOSHI_fnc_apsNotifyPlayer;
    [_vehicle, ["ApsExperimentalEnergyWeapon", "ApsOnline"]] spawn YOSHI_fnc_apsSaySequence;
};

YOSHI_fnc_apsHandleAntiDroneTurnOff = {
    params ["_vehicle", "_player"];

    if (!isServer) exitWith {};
    if (isNull _vehicle) exitWith {};

    _vehicle setVariable ["YOSHI_APS_AntiDrone_Enabled", false, true];
    [_player, "Anti-Drone disabled."] call YOSHI_fnc_apsNotifyPlayer;
    [_vehicle, ["ApsExperimentalEnergyWeapon", "ApsDeactivated"]] spawn YOSHI_fnc_apsSaySequence;
};

YOSHI_fnc_apsHandleAntiDroneStatusAction = {
    params ["_vehicle", "_player"];

    if (!isServer) exitWith {};
    if (isNull _vehicle) exitWith {};

    private _online = _vehicle getVariable ["YOSHI_APS_AntiDrone_Enabled", true];
    private _fuelPct = round ((fuel _vehicle) * 100);
    _fuelPct = (_fuelPct max 0) min 199;
    private _onlineSound = if (_online) then {"ApsOnline"} else {"ApsDeactivated"};
    private _sequence = ["ApsExperimentalEnergyWeapon", _onlineSound];
    if (_fuelPct > 0) then {
        private _fuelTokens = [_fuelPct] call YOSHI_numToTextArray;
        _sequence pushBack "ApsPowerLevelIs";
        _sequence append _fuelTokens;
        _sequence pushBack "ApsPercent";
    } else {
        _sequence pushBack "ApsInsufficientPower";
    };

    private _status = format ["Anti-Drone: %1 | Fuel-Cell: %2%%", if (_online) then {"ONLINE"} else {"OFFLINE"}, _fuelPct];
    [_player, _status] call YOSHI_fnc_apsNotifyPlayer;
    [_vehicle, _sequence] spawn YOSHI_fnc_apsSaySequence;
};

YOSHI_fnc_apsHandleStatusAction = {
    params ["_vehicle", "_player"];

    if (!isServer) exitWith {};
    if (isNull _vehicle) exitWith {};

    private _status = [_vehicle] call YOSHI_fnc_apsStatusText;
    [_player, _status] call YOSHI_fnc_apsNotifyPlayer;

    private _hardKillOnline = (_vehicle getVariable ["YOSHI_APS_HardKill_Enabled", false]) &&
        (_vehicle getVariable ["YOSHI_APS_HardKill_Online", false]);

    private _sequence = ["ApsActiveProtectionSystem"];
    _sequence pushBack (if (_hardKillOnline) then {"ApsActivated"} else {"ApsDeactivated"});

    private _charges = [_vehicle] call YOSHI_fnc_apsHardKillChargeCount;
    if (_charges > 0) then {
        private _tokens = [_charges] call YOSHI_numToTextArray;
        _sequence append _tokens;
        _sequence pushBack "ApsSelfPropelledGrenade";
        _sequence pushBack "ApsRemaining";
    } else {
        _sequence append ["ApsSelfPropelledGrenade", "ApsAmmunitionDepleted"];
    };

    private _fuelPct = round ((fuel _vehicle) * 100);
    _fuelPct = (_fuelPct max 0) min 199;
    if (_fuelPct > 0) then {
        private _fuelTokens = [_fuelPct] call YOSHI_numToTextArray;
        _sequence pushBack "ApsPowerLevelIs";
        _sequence append _fuelTokens;
        _sequence pushBack "ApsPercent";
    } else {
        _sequence pushBack "ApsInsufficientPower";
    };

    [_vehicle, _sequence] spawn YOSHI_fnc_apsSaySequence;
};

YOSHI_fnc_apsRegisterActionsLocal = {
    params ["_vehicle"];

    if (isNull _vehicle) exitWith {};
    if (isNil "ace_interact_menu_fnc_createAction") exitWith {};
    if (_vehicle getVariable ["YOSHI_APS_ActionsAdded_Local", false]) exitWith {};

    private _menuAction = [
        "YOSHI_APS_Menu",
        "APS",
        "",
        {},
        { _target getVariable ["YOSHI_APS_Enabled", false] }
    ] call ace_interact_menu_fnc_createAction;

    [_vehicle, 0, ["ACE_MainActions"], _menuAction] call ace_interact_menu_fnc_addActionToObject;

    private _hardKillOffAction = [
        "YOSHI_APS_HardKill_TurnOff",
        "Turn Off Hard-Kill APS",
        "",
        {
            params ["_target", "_player"];
            [_target, _player] remoteExecCall ["YOSHI_fnc_apsHandleHardKillTurnOff", 2];
        },
        {
            (_target getVariable ["YOSHI_APS_Enabled", false]) &&
            (_target getVariable ["YOSHI_APS_HardKill_Enabled", false]) &&
            (_target getVariable ["YOSHI_APS_HardKill_Online", false])
        }
    ] call ace_interact_menu_fnc_createAction;

    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_Menu"], _hardKillOffAction] call ace_interact_menu_fnc_addActionToObject;

    private _hardKillRebootAction = [
        "YOSHI_APS_HardKill_Reboot",
        "Reboot Hard-Kill APS",
        "",
        {
            params ["_target", "_player"];
            [_target, _player] remoteExecCall ["YOSHI_fnc_apsHandleHardKillReboot", 2];
        },
        {
            (_target getVariable ["YOSHI_APS_Enabled", false]) &&
            !((_target getVariable ["YOSHI_APS_HardKill_Enabled", false]) &&
              (_target getVariable ["YOSHI_APS_HardKill_Online", false]))
        }
    ] call ace_interact_menu_fnc_createAction;    

    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_Menu"], _hardKillRebootAction] call ace_interact_menu_fnc_addActionToObject;

    private _softKillOnAction = [
        "YOSHI_APS_SoftKill_TurnOn",
        "Turn On Soft-Kill APS",
        "",
        {
            params ["_target", "_player"];
            [_target, _player] remoteExecCall ["YOSHI_fnc_apsHandleSoftKillTurnOn", 2];
        },
        {
            (_target getVariable ["YOSHI_APS_Enabled", false]) &&
            !(_target getVariable ["YOSHI_APS_HardKill_Online", false]) &&
            !(_target getVariable ["YOSHI_APS_SoftKill_Enabled", false])
        }
    ] call ace_interact_menu_fnc_createAction;

    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_Menu"], _softKillOnAction] call ace_interact_menu_fnc_addActionToObject;

    private _softKillOffAction = [
        "YOSHI_APS_SoftKill_TurnOff",
        "Turn Off Soft-Kill APS",
        "",
        {
            params ["_target", "_player"];
            [_target, _player] remoteExecCall ["YOSHI_fnc_apsHandleSoftKillTurnOff", 2];
        },
        {
            (_target getVariable ["YOSHI_APS_Enabled", false]) &&
            !(_target getVariable ["YOSHI_APS_HardKill_Online", false]) &&
            (_target getVariable ["YOSHI_APS_SoftKill_Enabled", false])
        }
    ] call ace_interact_menu_fnc_createAction;

    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_Menu"], _softKillOffAction] call ace_interact_menu_fnc_addActionToObject;

    private _antiDroneMenu = [
        "YOSHI_APS_AntiDrone_Menu",
        "Anti-Drone",
        "",
        {},
        { _target getVariable ["YOSHI_APS_Enabled", false] }
    ] call ace_interact_menu_fnc_createAction;
    [_vehicle, 0, ["ACE_MainActions"], _antiDroneMenu] call ace_interact_menu_fnc_addActionToObject;

    private _antiDroneOnAction = [
        "YOSHI_APS_AntiDrone_TurnOn",
        "Turn On Experimental Energy Weapon",
        "",
        {
            params ["_target", "_player"];
            [_target, _player] remoteExecCall ["YOSHI_fnc_apsHandleAntiDroneTurnOn", 2];
        },
        {
            (_target getVariable ["YOSHI_APS_Enabled", false]) &&
            !(_target getVariable ["YOSHI_APS_AntiDrone_Enabled", true])
        }
    ] call ace_interact_menu_fnc_createAction;
    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_AntiDrone_Menu"], _antiDroneOnAction] call ace_interact_menu_fnc_addActionToObject;

    private _antiDroneOffAction = [
        "YOSHI_APS_AntiDrone_TurnOff",
        "Turn Off Experimental Energy Weapon",
        "",
        {
            params ["_target", "_player"];
            [_target, _player] remoteExecCall ["YOSHI_fnc_apsHandleAntiDroneTurnOff", 2];
        },
        {
            (_target getVariable ["YOSHI_APS_Enabled", false]) &&
            (_target getVariable ["YOSHI_APS_AntiDrone_Enabled", true])
        }
    ] call ace_interact_menu_fnc_createAction;
    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_AntiDrone_Menu"], _antiDroneOffAction] call ace_interact_menu_fnc_addActionToObject;

    private _antiDroneStatusAction = [
        "YOSHI_APS_AntiDrone_Status",
        "Check Anti-Drone Status",
        "",
        {
            params ["_target", "_player"];
            [_target, _player] remoteExecCall ["YOSHI_fnc_apsHandleAntiDroneStatusAction", 2];
        },
        { _target getVariable ["YOSHI_APS_Enabled", false] }
    ] call ace_interact_menu_fnc_createAction;
    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_AntiDrone_Menu"], _antiDroneStatusAction] call ace_interact_menu_fnc_addActionToObject;

    private _statusAction = [
        "YOSHI_APS_Status",
        "Check APS Status",
        "",
        {
            params ["_target", "_player"];
            [_target, _player] remoteExecCall ["YOSHI_fnc_apsHandleStatusAction", 2];
        },
        { _target getVariable ["YOSHI_APS_Enabled", false] }
    ] call ace_interact_menu_fnc_createAction;

    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_Menu"], _statusAction] call ace_interact_menu_fnc_addActionToObject;

    private _voiceOnAction = [
        "YOSHI_APS_Voice_On",
        "Turn On Voice Assistant",
        "",
        {
            params ["_target", "_player"];
            [_target, _player] remoteExecCall ["YOSHI_fnc_apsHandleVoiceTurnOn", 2];
        },
        {
            (_target getVariable ["YOSHI_APS_Enabled", false]) &&
            !(_target getVariable ["YOSHI_APS_VoiceEnabled", true])
        }
    ] call ace_interact_menu_fnc_createAction;
    [_vehicle, 0, ["ACE_MainActions"], _voiceOnAction] call ace_interact_menu_fnc_addActionToObject;

    private _voiceOffAction = [
        "YOSHI_APS_Voice_Off",
        "Turn Off Voice Assistant",
        "",
        {
            params ["_target", "_player"];
            [_target, _player] remoteExecCall ["YOSHI_fnc_apsHandleVoiceTurnOff", 2];
        },
        {
            (_target getVariable ["YOSHI_APS_Enabled", false]) &&
            (_target getVariable ["YOSHI_APS_VoiceEnabled", true])
        }
    ] call ace_interact_menu_fnc_createAction;
    [_vehicle, 0, ["ACE_MainActions"], _voiceOffAction] call ace_interact_menu_fnc_addActionToObject;

    _vehicle setVariable ["YOSHI_APS_ActionsAdded_Local", true];
};

YOSHI_fnc_apsUnregisterActionsLocal = {
    params ["_vehicle"];

    if (isNull _vehicle) exitWith {};
    if (isNil "ace_interact_menu_fnc_removeActionFromObject") exitWith {};
    if !(_vehicle getVariable ["YOSHI_APS_ActionsAdded_Local", false]) exitWith {};

    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_Menu"], "YOSHI_APS_HardKill_TurnOff"] call ace_interact_menu_fnc_removeActionFromObject;
    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_Menu"], "YOSHI_APS_HardKill_Reboot"] call ace_interact_menu_fnc_removeActionFromObject;
    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_Menu"], "YOSHI_APS_SoftKill_TurnOn"] call ace_interact_menu_fnc_removeActionFromObject;
    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_Menu"], "YOSHI_APS_SoftKill_TurnOff"] call ace_interact_menu_fnc_removeActionFromObject;
    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_AntiDrone_Menu"], "YOSHI_APS_AntiDrone_TurnOn"] call ace_interact_menu_fnc_removeActionFromObject;
    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_AntiDrone_Menu"], "YOSHI_APS_AntiDrone_TurnOff"] call ace_interact_menu_fnc_removeActionFromObject;
    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_AntiDrone_Menu"], "YOSHI_APS_AntiDrone_Status"] call ace_interact_menu_fnc_removeActionFromObject;
    [_vehicle, 0, ["ACE_MainActions"], "YOSHI_APS_AntiDrone_Menu"] call ace_interact_menu_fnc_removeActionFromObject;
    [_vehicle, 0, ["ACE_MainActions", "YOSHI_APS_Menu"], "YOSHI_APS_Status"] call ace_interact_menu_fnc_removeActionFromObject;
    [_vehicle, 0, ["ACE_MainActions"], "YOSHI_APS_Menu"] call ace_interact_menu_fnc_removeActionFromObject;
    [_vehicle, 0, ["ACE_MainActions"], "YOSHI_APS_Voice_On"] call ace_interact_menu_fnc_removeActionFromObject;
    [_vehicle, 0, ["ACE_MainActions"], "YOSHI_APS_Voice_Off"] call ace_interact_menu_fnc_removeActionFromObject;

    _vehicle setVariable ["YOSHI_APS_ActionsAdded_Local", false];
};

YOSHI_fnc_apsRegisterActionsGlobal = {
    params ["_vehicle"];

    if (isNull _vehicle) exitWith {};
    [_vehicle] remoteExecCall ["YOSHI_fnc_apsRegisterActionsLocal", 0, _vehicle];
};

YOSHI_fnc_apsUnregisterActionsGlobal = {
    params ["_vehicle"];

    if (isNull _vehicle) exitWith {};
    [_vehicle] remoteExecCall ["YOSHI_fnc_apsUnregisterActionsLocal", 0, _vehicle];
};

YOSHI_fnc_apsEnableVehicle = {
    params ["_vehicle", ["_charges", YOSHI_APS_DEFAULT_HARDKILL_CHARGES]];

    if (!isServer) exitWith {false};
    if (isNull _vehicle) exitWith {false};
    if !(_vehicle isKindOf "AllVehicles") exitWith {false};

    [_vehicle, _charges] call YOSHI_fnc_apsTopUpHardKillCharges;

    _vehicle setVariable ["YOSHI_APS_Enabled", true, true];
    _vehicle setVariable ["YOSHI_APS_VoiceEnabled", true, true];
    _vehicle setVariable ["YOSHI_APS_AntiDrone_Enabled", true, true];
    _vehicle setVariable ["YOSHI_APS_HardKill_EmptyAnnounced", false, true];
    _vehicle setVariable ["YOSHI_APS_SoftKill_LowPowerAnnounced", false, true];
    [_vehicle, true] call YOSHI_fnc_apsSetHardKillState;
    [_vehicle, false] call YOSHI_fnc_apsSetSoftKillState;
    [] remoteExecCall ["YOSHI_fnc_apsEnsureLocalRuntime", 0];

    _vehicle setVariable ["YOSHI_APS_Thread", scriptNull];

    private _droneThread = _vehicle getVariable ["YOSHI_APS_Drone_Thread", scriptNull];
    if (scriptDone _droneThread) then {
        _droneThread = [_vehicle] spawn YOSHI_detectDrones;
        _vehicle setVariable ["YOSHI_APS_Drone_Thread", _droneThread];
    };

    _vehicle setVariable ["YOSHI_APS_soft_Thread", scriptNull];

    [_vehicle] call YOSHI_fnc_apsRegisterActionsGlobal;

    true
};

YOSHI_fnc_apsDisableVehicle = {
    params ["_vehicle"];

    if (!isServer) exitWith {false};
    if (isNull _vehicle) exitWith {false};

    [_vehicle] call YOSHI_fnc_apsCancelVoice;

    private _droneThread = _vehicle getVariable ["YOSHI_APS_Drone_Thread", scriptNull];
    if (!scriptDone _droneThread) then {
        terminate _droneThread;
    };

    _vehicle setVariable ["YOSHI_APS_Thread", scriptNull];
    _vehicle setVariable ["YOSHI_APS_Drone_Thread", scriptNull];
    _vehicle setVariable ["YOSHI_APS_soft_Thread", scriptNull];
    _vehicle setVariable ["YOSHI_APS_Enabled", false, true];
    _vehicle setVariable ["YOSHI_APS_AntiDrone_Enabled", false, true];
    [_vehicle, false] call YOSHI_fnc_apsSetHardKillState;
    [_vehicle, false] call YOSHI_fnc_apsSetSoftKillState;

    [_vehicle] call YOSHI_fnc_apsUnregisterActionsGlobal;

    true
};

YOSHI_fnc_apsToggleVehicle = {
    params ["_vehicle"];

    private _enabled = _vehicle getVariable ["YOSHI_APS_Enabled", false];
    if (_enabled) exitWith {
        [_vehicle] call YOSHI_fnc_apsDisableVehicle;
        false
    };

    [_vehicle] call YOSHI_fnc_apsEnableVehicle;
    true
};

[] spawn {
    waitUntil {time > 0};
    [] call YOSHI_fnc_apsEnsureLocalRuntime;
};

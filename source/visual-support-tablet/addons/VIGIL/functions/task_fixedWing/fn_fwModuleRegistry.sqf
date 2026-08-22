YSF_fnc_fwModuleIdentity = {
    params ["_object"];
    if (isNull _object) exitWith {""};
    private _id = netId _object;
    if (_id isEqualTo "") then {str _object} else {_id}
};

YSF_fnc_fwModulePublishPoints = {
    if (!isServer) exitWith {false};
    {
        _x params ["_kind", "_publicName"];
        private _records = localNamespace getVariable [format ["YSF_FW_MODULE_%1_POINTS", toUpper _kind], createHashMap];
        private _points = [];
        {private _pos = (_y param [1, []]); if ((count _pos) >= 3) then {_points pushBack _pos;};} forEach _records;
        missionNamespace setVariable [_publicName, _points, true];
    } forEach [["infil", "YSF_FW_MISSION_INFIL_POINTS"], ["exfil", "YSF_FW_MISSION_EXFIL_POINTS"]];
    true
};

YSF_fnc_fwModuleAudit = {
    params ["_kind", "_logic", "_accepted", "_reason", ["_details", []]];
    private _audit = localNamespace getVariable ["YSF_FW_MODULE_DISPATCH_AUDIT", []];
    _audit pushBack [
        _kind, if (isNull _logic) then {""} else {typeOf _logic}, if (isNull _logic) then {""} else {netId _logic},
        isServer, !isNull _logic && {local _logic}, if (isNull _logic) then {-1} else {owner _logic},
        remoteExecutedOwner, _accepted, _reason, _details, diag_tickTime
    ];
    if ((count _audit) > 64) then {_audit deleteRange [0, (count _audit) - 64];};
    localNamespace setVariable ["YSF_FW_MODULE_DISPATCH_AUDIT", _audit];
};

YSF_fnc_fwModuleRegisterAssets = {
    params ["_logic"];
    private _native = isServer && {!isNull _logic} && {typeOf _logic isEqualTo "YSF_FixedWing_Asset_Module"}
        && {local _logic} && {owner _logic isEqualTo 2} && {remoteExecutedOwner <= 2};
    if (!_native) exitWith {
        ["asset", _logic, false, if (remoteExecutedOwner > 2) then {"remote_request"} else {"invalid_logic"}] call YSF_fnc_fwModuleAudit;
        false
    };
    private _synced = synchronizedObjects _logic;
    private _syncRows = _synced apply {[typeOf _x, vehicleVarName _x, netId (vehicle _x)]};
    private _registered = [];
    {
        private _object = vehicle _x;
        if (!isNull _object && {_object isKindOf "Plane"}) then {
            private _id = _object getVariable ["YSF_FW_ID", format ["FW_%1", netId _object]];
            if ([_object] call YSF_fwRegisterAsset) then {_registered pushBackUnique _id;};
        };
    } forEach _synced;
    ["asset", _logic, true, "accepted_native", [_syncRows, _registered]] call YSF_fnc_fwModuleAudit;
    true
};

YSF_fnc_fwModuleRegisterPoint = {
    params ["_logic", "_kind"];
    private _expectedClass = if (_kind isEqualTo "infil") then {"YSF_FixedWing_Infil_Module"} else {"YSF_FixedWing_Exfil_Module"};
    private _native = isServer && {_kind in ["infil", "exfil"]} && {!isNull _logic} && {typeOf _logic isEqualTo _expectedClass}
        && {local _logic} && {owner _logic isEqualTo 2} && {remoteExecutedOwner <= 2};
    if (!_native) exitWith {
        [_kind, _logic, false, if (remoteExecutedOwner > 2) then {"remote_request"} else {"invalid_logic"}] call YSF_fnc_fwModuleAudit;
        false
    };
    private _pos = getPosASL _logic;
    if ((_pos param [2, 0]) < 200) then {_pos set [2, 1200];};
    private _name = format ["YSF_FW_MODULE_%1_POINTS", toUpper _kind];
    private _records = localNamespace getVariable [_name, createHashMap];
    _records set [[_logic] call YSF_fnc_fwModuleIdentity, [_logic, _pos]];
    localNamespace setVariable [_name, _records];
    call YSF_fnc_fwModulePublishPoints;
    [_kind, _logic, true, "accepted_native", [_pos]] call YSF_fnc_fwModuleAudit;
    true
};

YSF_fnc_fwSelectMissionPoint = {
    params ["_kind", ["_reference", []]];
    if (!isServer || {!(_kind in ["infil", "exfil"])}) exitWith {[]};
    private _records = localNamespace getVariable [format ["YSF_FW_MODULE_%1_POINTS", toUpper _kind], createHashMap];
    private _best = [];
    private _bestDistance = 1e12;
    {
        private _pos = _y param [1, []];
        if ((count _pos) >= 3) then {
            private _distance = if ((count _reference) >= 2) then {_reference distance2D _pos} else {0};
            if (_distance < _bestDistance) then {_best = +_pos; _bestDistance = _distance;};
        };
    } forEach _records;
    _best
};

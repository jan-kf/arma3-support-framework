#include "..\..\ui\idc.hpp"

YFU_fabricatorGetItems = {
    private _catalogue = missionNamespace getVariable ["YFU_VIRTUAL_STORAGE_OBJECTS", []];
    if (_catalogue isNotEqualTo []) exitWith {+_catalogue};
    private _virtualStorage = missionNamespace getVariable ["YOSHI_VIRTUAL_STORAGE", objNull];
    if (isNull _virtualStorage) exitWith {[]};
    synchronizedObjects _virtualStorage
};

YFU_assetsGetDisplayName = {
    params ["_obj"];
    private _className = typeOf _obj;
    private _displayName = getText (configFile >> "CfgVehicles" >> _className >> "displayName");
    if (_displayName isEqualTo "") then {_displayName = _className};
    _displayName
};

YFU_assetsGetClassDisplayName = {
    params ["_className"];

    private _paths = [
        ["CfgWeapons", "displayName"],
        ["CfgMagazines", "displayName"],
        ["CfgVehicles", "displayName"],
        ["CfgGlasses", "displayName"]
    ];

    private _displayName = "";
    {
        private _cfgRoot = _x # 0;
        private _cfgField = _x # 1;
        private _cfg = configFile >> _cfgRoot >> _className;
        if (isClass _cfg) exitWith {
            _displayName = getText (_cfg >> _cfgField);
        };
    } forEach _paths;

    if (_displayName isEqualTo "") then {_displayName = _className};
    _displayName
};

YFU_assetsIsImagePath = {
    params ["_path"];
    if (_path isEqualTo "") exitWith {false};
    private _lower = toLower _path;
    ((_lower find ".paa") >= 0) || {((_lower find ".pac") >= 0)} || {((_lower find ".jpg") >= 0)} || {((_lower find ".jpeg") >= 0)} || {((_lower find ".png") >= 0)}
};

YFU_assetsGetClassImage = {
    params ["_className"];

    private _lookups = [
        ["CfgVehicles", "picture"],
        ["CfgVehicles", "editorPreview"],
        ["CfgWeapons", "picture"],
        ["CfgWeapons", "UiPicture"],
        ["CfgMagazines", "picture"],
        ["CfgGlasses", "picture"]
    ];

    private _image = "";
    {
        private _cfgRoot = _x # 0;
        private _cfgField = _x # 1;
        private _cfg = configFile >> _cfgRoot >> _className;
        if (isClass _cfg) then {
            private _candidate = getText (_cfg >> _cfgField);
            if ([_candidate] call YFU_assetsIsImagePath) exitWith {
                _image = _candidate;
            };
        };
    } forEach _lookups;

    if (_image isEqualTo "") then {
        _image = "\a3\ui_f\data\igui\cfg\simpletasks\types\box_ca.paa";
    };
    _image
};

YFU_assetsGetPicture = {
    params ["_obj"];
    private _className = typeOf _obj;
    [_className] call YFU_assetsGetClassImage
};

YFU_assetsInitPage = {
    [] spawn {
        disableSerialization;
        private _tries = 0;
        private _ready = false;

        while {_tries < 20 && !_ready} do {
            private _ret = [YFU_IDC_ASSETS_LIST] call YFU_getControl;
            _ready = _ret # 1;
            if (!_ready) then {
                _tries = _tries + 1;
                uiSleep 0.02;
            };
        };
        call YFU_UI_SetCorrectTablet;

        ["set", "assets"] call YFU_UI_Nav;
        uiNamespace setVariable ["YFU_fabricator_queue_map", createHashMap];
        uiNamespace setVariable ["YFU_fabricator_queue_order", []];
        uiNamespace setVariable ["YFU_fabricator_queue_dynamic", []];
        uiNamespace setVariable ["YFU_submit_in_progress", false];
        uiNamespace setVariable ["YFU_submit_success", false];

        call YFU_assetsRefreshList;
        call YFU_assetsRefreshQueue;
        call YFU_assetsApplyDeliveryDefaults;
        [] call YFU_assetsSetSubmitOverlay;
    };
};

YFU_assetsQueueKeyForObject = {
    params ["_obj"];
    if (isNull _obj) exitWith {""};
    netId _obj
};

YFU_assetsQueueEntries = {
    private _map = uiNamespace getVariable ["YFU_fabricator_queue_map", createHashMap];
    private _order = uiNamespace getVariable ["YFU_fabricator_queue_order", []];
    private _entries = [];

    {
        private _key = _x;
        private _entry = _map getOrDefault [_key, []];
        if !(_entry isEqualTo []) then {
            _entries pushBack [_key, _entry # 0, _entry # 1];
        };
    } forEach _order;

    _entries
};

YFU_assetsQueueExpandedObjects = {
    private _entries = call YFU_assetsQueueEntries;
    private _objects = [];
    {
        private _obj = _x # 1;
        private _count = _x # 2;
        for "_i" from 1 to _count do {
            _objects pushBack _obj;
        };
    } forEach _entries;
    _objects
};

YFU_pad4 = {
    params ["_n"];
    private _v = floor _n;
    if (_v < 0) then {_v = 0;};
    private _s = str _v;
    while {(count _s) < 4} do {_s = "0" + _s;};
    if ((count _s) > 4) then {_s = _s select [0,4];};
    _s
};

YFU_posToGrid = {
    params ["_pos"];
    if ((typeName _pos) != "ARRAY" || {(count _pos) < 2}) exitWith {"0000-0000"};
    private _gx = floor ((_pos # 0) / 10);
    private _gy = floor ((_pos # 1) / 10);
    format ["%1-%2", [_gx] call YFU_pad4, [_gy] call YFU_pad4]
};

YFU_parseGrid = {
    params ["_txt"];
    private _parts = (_txt splitString " -,:;") select {_x != ""};
    private _gx = "";
    private _gy = "";
    private _isDigitsLen = {
        params ["_s", "_len"];
        private _a = toArray _s;
        (count _a == _len) && {({ _x >= 48 && _x <= 57 } count _a) == _len}
    };

    if ((count _parts) == 1) then {
        private _s = _parts # 0;
        if ([_s, 8] call _isDigitsLen) then {
            _gx = _s select [0,4];
            _gy = _s select [4,4];
        };
    } else {
        if ((count _parts) == 2) then {
            if ([_parts # 0, 4] call _isDigitsLen && [_parts # 1, 4] call _isDigitsLen) then {
                _gx = _parts # 0;
                _gy = _parts # 1;
            };
        };
    };

    if (_gx isEqualTo "" || _gy isEqualTo "") exitWith {[]};
    [parseNumber _gx, parseNumber _gy]
};

YFU_deliveryGridChanged = {
    params ["_ctrl"];
    private _r = [ctrlText _ctrl] call YFU_parseGrid;
    if (_r isEqualTo []) exitWith {
        uiNamespace setVariable ["YFU_delivery_target_pos", []];
        hintSilent "Enter XY: 12345678 or 1234-5678";
    };

    _r params ["_gx", "_gy"];
    private _pos = [_gx * 10, _gy * 10, 0];
    uiNamespace setVariable ["YFU_delivery_target_pos", _pos];
};

YFU_assetsGetOpenContext = {
    private _ctx = uiNamespace getVariable ["YFU_open_context", createHashMap];
    if (typeName _ctx != "HASHMAP") then {
        _ctx = createHashMapFromArray [];
    };

    if (isNil {_ctx get "fabricator"}) then {
        _ctx set ["fabricator", uiNamespace getVariable ["YFU_selected_fabricator", objNull]];
    };
    if (isNil {_ctx get "isAirdrop"}) then {
        _ctx set ["isAirdrop", false];
    };
    if (isNil {_ctx get "grid"}) then {
        _ctx set ["grid", mapGridPosition player];
    };

    _ctx
};

YFU_assetsReadDeliveryGrid = {
    private _ret = [YFU_IDC_DELIVERY_GRID] call YFU_getControl;
    private _ctrl = _ret # 0;
    private _ok = _ret # 1;
    if (_ok) exitWith {
        private _g = ctrlText _ctrl;
        if (_g isEqualTo "") then {_g = mapGridPosition player;};
        _g
    };
    mapGridPosition player
};

YFU_assetsApplyDeliveryDefaults = {
    disableSerialization;

    private _ctx = call YFU_assetsGetOpenContext;
    private _fabricator = _ctx getOrDefault ["fabricator", objNull];
    private _isAirdrop = _ctx getOrDefault ["isAirdrop", false];
    private _grid = _ctx getOrDefault ["grid", ""];
    private _parsed = [_grid] call YFU_parseGrid;
    if (_parsed isEqualTo []) then {
        _grid = [getPosATL player] call YFU_posToGrid;
    };

    uiNamespace setVariable ["YFU_selected_fabricator", _fabricator];

    private _methodCtrl = ([YFU_IDC_DELIVERY_METHOD] call YFU_getControl) # 0;
    private _notesCtrl = ([YFU_IDC_DELIVERY_NOTES] call YFU_getControl) # 0;
    private _gridCtrl = ([YFU_IDC_DELIVERY_GRID] call YFU_getControl) # 0;

    if (!isNull _methodCtrl) then {
        _methodCtrl ctrlSetText (["Direct from nearby fabricator", "Airdrop"] select _isAirdrop);
    };
    if (!isNull _notesCtrl) then {
        _notesCtrl ctrlSetText ([
            "Local pickup",
            "Air drop at grid"
        ] select _isAirdrop);
    };
    if (!isNull _gridCtrl) then {
        _gridCtrl ctrlSetText _grid;
        _gridCtrl ctrlEnable _isAirdrop;
        [_gridCtrl] call YFU_deliveryGridChanged;
    };
};

YFU_assetsSetSubmitOverlay = {
    params [
        ["_show", false],
        ["_title", ""],
        ["_status", ""],
        ["_progress", -1],
        ["_clickable", false]
    ];

    disableSerialization;
    private _bg = ([YFU_IDC_SUBMIT_OVERLAY_BG] call YFU_getControl) # 0;
    private _click = ([YFU_IDC_SUBMIT_OVERLAY_CLICK] call YFU_getControl) # 0;
    private _titleCtrl = ([YFU_IDC_SUBMIT_OVERLAY_TITLE] call YFU_getControl) # 0;
    private _statusCtrl = ([YFU_IDC_SUBMIT_OVERLAY_STATUS] call YFU_getControl) # 0;
    private _progressCtrl = ([YFU_IDC_SUBMIT_OVERLAY_PROGRESS] call YFU_getControl) # 0;

    if !(isNull _bg) then {_bg ctrlShow _show;};
    if !(isNull _click) then {_click ctrlShow _show;};
    if !(isNull _titleCtrl) then {
        _titleCtrl ctrlShow _show;
        if !(_title isEqualTo "") then {_titleCtrl ctrlSetText _title;};
    };
    if !(isNull _statusCtrl) then {
        _statusCtrl ctrlShow _show;
        if !(_status isEqualTo "") then {_statusCtrl ctrlSetText _status;};
    };
    if !(isNull _progressCtrl) then {
        _progressCtrl ctrlShow _show;
        if (_progress >= 0) then {
            _progressCtrl progressSetPosition (_progress max 0 min 1);
        };
    };
};

YFU_assetsFindSafeDropPos = {
    params ["_center", ["_distance", 4], ["_attempt", 0]];
    private _radiusMin = (_distance + (_attempt * 2)) max 2;
    private _radiusMax = _radiusMin + 5;
    private _pos2D = [_center, _radiusMin, _radiusMax, 1, 0, 20 * (pi / 180), 0] call BIS_fnc_findSafePos;

    private _z = 0;
    if ((typeName _center) isEqualTo "ARRAY" && {(count _center) >= 3}) then {
        _z = _center # 2;
    };

    private _fallbackCenter = if ((typeName _center) isEqualTo "ARRAY" && {(count _center) >= 2}) then {
        _center
    } else {
        [0, 0, 0]
    };

    // BIS_fnc_findSafePos answers a failed search with a random position
    // somewhere on the map, which would deliver an order kilometres from the
    // player who ordered it. A drop that is not near the requested centre is not
    // a drop; fall back to a deterministic ring around the centre instead.
    private _candidate = [];
    if ((typeName _pos2D) isEqualTo "ARRAY" && {(count _pos2D) >= 2}) then {
        private _offset = [(_pos2D # 0) - (_fallbackCenter # 0), (_pos2D # 1) - (_fallbackCenter # 1), 0];
        if ((vectorMagnitude _offset) <= (_radiusMax + 5)) then {
            _candidate = [_pos2D # 0, _pos2D # 1, _z];
        };
    };

    // The fallback ring keeps a delivery beside the player instead of wherever
    // BIS_fnc_findSafePos lands after a failed search. It is NOT a suitability
    // check: water, gradient, obstruction and final settling are still unverified,
    // and a real check needs terrain the validation world does not have. Recorded
    // as an open finding rather than approximated here.
    if (_candidate isEqualTo []) then {
        private _bearing = (_attempt * 47) % 360;
        _candidate = [
            (_fallbackCenter # 0) + (_radiusMin * sin _bearing),
            (_fallbackCenter # 1) + (_radiusMin * cos _bearing),
            _z
        ];
    };

    _candidate
};

// Placement is the server's; this only tells the player where its work landed.
YFU_assetsAnnounceDelivery = {
    params ["_caller", "_positions"];
    if (_positions isEqualTo []) exitWith {false};

    private _center = getPosATL _caller;
    private _relativeLines = [];

    private _dirLabelFromPos = {
        params ["_from", "_to"];
        private _dx = (_to # 0) - (_from # 0);
        private _dy = (_to # 1) - (_from # 1);
        private _bearing = _dx atan2 _dy;
        if (_bearing < 0) then {_bearing = _bearing + 360;};
        private _labels = ["North", "North East", "East", "South East", "South", "South West", "West", "North West"];
        private _idx = round (_bearing / 45);
        if (_idx >= 8) then {_idx = 0;};
        _labels # _idx
    };

    {
        private _dist = round (_center distance2D _x);
        private _dirLabel = [_center, _x] call _dirLabelFromPos;
        _relativeLines pushBack format ["%1. %2m %3", (_forEachIndex + 1), _dist, _dirLabel];
    } forEach _positions;

    if !(_relativeLines isEqualTo []) then {
        hint format ["Containers delivered at:\n%1", _relativeLines joinString "\n"];
    };

    true
};

YFU_assetsAirdropAnnounce = {
    params ["_airAsset", "_targetATL", "_count", "_sourceASL"];

    if (isNull _airAsset) exitWith {};
    if ((typeName _sourceASL) != "ARRAY" || {(count _sourceASL) < 3}) then {
        _sourceASL = getPosASL _airAsset;
    };

    private _assetATL = getPosATL _airAsset;

    private _bearing = _targetATL getDir _assetATL;
    private _dirLabel = [_bearing] call YOSHI_GET_DIRECTION;
    private _eta = [_assetATL select 2, _targetATL select 2] call YOSHI_GET_FALL_TIME;

    private _speaker = effectiveCommander _airAsset;
    if (isNull _speaker) then { _speaker = driver _airAsset; };
    if (isNull _speaker) then { _speaker = player; };

    private _msg = format [
        "Airdrop in-bound. %1 package(s), %2, ETA %3s.",
        _count,
        _dirLabel,
        _eta
    ];
    [_speaker, _msg] call YFU_fnc_emitSideChat;
};

YFU_airdropResultVariable = {
    params ["_taskId", "_index"];
    format ["YFU_AIRDROP_RESULT_%1_%2", _taskId, _index]
};

YFU_beginPhysicalAirdrop = {
    params [
        "_container",
        "_targetATL",
        "_releaseASL",
        "_taskId",
        ["_index", 0],
        ["_deployAltitude", 160]
    ];

    if (!isServer || {isNull _container} || {!local _container}) exitWith {false};
    if !(_targetATL isEqualType [] && {(count _targetATL) >= 3}) exitWith {false};
    if !(_releaseASL isEqualType [] && {(count _releaseASL) >= 3}) exitWith {false};

    private _resultVariable = [_taskId, _index] call YFU_airdropResultVariable;
    missionNamespace setVariable [_resultVariable, nil, false];
    _container setVariable ["YFU_airdropTaskId", _taskId, true];
    _container setVariable ["YFU_airdropState", "released", true];
    _container setVariable ["YFU_airdropChute", objNull, true];
    detach _container;
    _container setPosASL _releaseASL;
    _container setVectorUp [0, 0, 1];

    private _releaseATL = ASLToATL _releaseASL;
    private _fallDistance = ((_releaseATL # 2) - _deployAltitude) max 10;
    private _fallTime = sqrt ((2 * _fallDistance) / 9.81);
    private _targetASL = ATLToASL _targetATL;
    private _horizontal = [
        ((_targetASL # 0) - (_releaseASL # 0)) / (_fallTime max 0.1),
        ((_targetASL # 1) - (_releaseASL # 1)) / (_fallTime max 0.1),
        0
    ];
    private _horizontalSpeed = vectorMagnitude _horizontal;
    if (_horizontalSpeed > 70) then {
        _horizontal = _horizontal vectorMultiply (70 / _horizontalSpeed);
    };
    private _launchVelocity = [_horizontal # 0, _horizontal # 1, 0];
    _container setVelocity _launchVelocity;
    _container setVariable ["YFU_airdropLaunchState", [_releaseASL, _targetATL, _launchVelocity, local _container, owner _container], true];

    [_container, _targetATL, _releaseASL, _taskId, _index, _deployAltitude, _resultVariable] spawn {
        params ["_container", "_targetATL", "_releaseASL", "_taskId", "_index", "_deployAltitude", "_resultVariable"];
        private _samples = [];
        private _deadline = diag_tickTime + 150;
        private _chute = objNull;
        private _chuteId = "";
        private _deployASL = [];
        private _terminal = "";
        private _deployAt = diag_tickTime + 0.75;

        waitUntil {
            if (!isNull _container) then {
                _samples pushBack [diag_tickTime, getPosATL _container, getPosASL _container, velocity _container, local _container, owner _container];
            };
            uiSleep 0.05;
            isNull _container
            || {!alive _container}
            || {((getPosATL _container) # 2) <= _deployAltitude}
            || {diag_tickTime >= _deployAt}
            || {diag_tickTime > _deadline}
        };

        if (isNull _container || {!alive _container}) then {
            _terminal = "cargo_lost_before_chute";
        } else {
            if (diag_tickTime > _deadline) then {
                _terminal = "chute_timeout";
            } else {
                _deployASL = getPosASL _container;
                private _verticalSpeed = ((velocity _container) # 2) min -3;
                _chute = createVehicle ["B_Parachute_02_F", ASLToATL _deployASL, [], 0, "CAN_COLLIDE"];
                _chute setPosASL _deployASL;
                _chute setDir getDir _container;
                _chute allowDamage false;
                _chute setVelocity [0, 0, _verticalSpeed];
                _container attachTo [_chute, [0, 0, -1.2]];
                _chuteId = netId _chute;
                _container setVariable ["YFU_airdropChute", _chute, true];
                _container setVariable ["YFU_airdropState", "under_chute", true];
                _chute setVariable ["YFU_airdropTaskId", _taskId, true];
                diag_log format ["YFU_AIRDROP|%1|chute_created|cargo=%2|chute=%3|asl=%4|atl=%5|height=%6|local=%7/%8|alive=%9", _taskId, netId _container, _chuteId, getPosASL _chute, getPosATL _chute, ((getPosASL _chute) # 2) - (getTerrainHeightASL getPosASL _chute), local _chute, owner _chute, alive _chute];

                private _groundReached = false;
                waitUntil {
                    if (!isNull _container) then {
                        _samples pushBack [diag_tickTime, getPosATL _container, getPosASL _container, velocity _container, local _container, owner _container];
                    };
                    uiSleep 0.1;
                    if (!isNull _chute && {(((getPosASL _chute) # 2) - (getTerrainHeightASL getPosASL _chute)) <= 3}) then {
                        _groundReached = true;
                    };
                    isNull _container
                    || {!alive _container}
                    || {isNull _chute}
                    || {_groundReached}
                    || {diag_tickTime > _deadline}
                };

                if (isNull _container || {!alive _container}) then {
                    _terminal = "cargo_lost_under_chute";
                } else {
                    if (isNull _chute && {!_groundReached}) then {
                        _terminal = "chute_lost";
                    } else {
                    if (diag_tickTime > _deadline) then {
                        _terminal = "landing_timeout";
                    } else {
                        detach _container;
                        _container setVelocity [0, 0, 0];
                        _container setVectorUp [0, 0, 1];
                        _container setVariable ["YFU_airdropState", "landed", true];
                        _terminal = "landed";
                    };
                    };
                };
                diag_log format ["YFU_AIRDROP|%1|chute_terminal|terminal=%2|ground=%3|cargoAsl=%4|cargoAtl=%5|chuteNull=%6|chuteAsl=%7|chuteAtl=%8", _taskId, _terminal, _groundReached, getPosASL _container, getPosATL _container, isNull _chute, if (isNull _chute) then {[]} else {getPosASL _chute}, if (isNull _chute) then {[]} else {getPosATL _chute}];
            };
        };

        private _result = [
            _taskId,
            _terminal,
            if (isNull _container) then {""} else {netId _container},
            _chuteId,
            _releaseASL,
            _deployASL,
            if (isNull _container) then {[]} else {getPosATL _container},
            if (isNull _container) then {1} else {damage _container},
            _samples,
            if (isNull _container) then {false} else {local _container},
            if (isNull _container) then {-1} else {owner _container}
        ];
        missionNamespace setVariable [_resultVariable, _result, false];
        if (!isNull _container) then {
            // Keep high-frequency trajectory samples server-private. Only the
            // compact terminal record crosses the network boundary.
            private _summary = [_result # 0, _result # 1, _result # 2, _result # 3, _result # 4, _result # 5, _result # 6, _result # 7, _result # 9, _result # 10];
            _container setVariable ["YFU_airdropResult", _summary, true];
        };
        diag_log format ["YFU_AIRDROP|%1|%2|cargo=%3|chute=%4|release=%5|landing=%6|damage=%7|samples=%8", _taskId, _terminal, _result # 2, _result # 3, _releaseASL, _result # 6, _result # 7, count _samples];
        if (!isNull _chute) then {
            uiSleep 2;
            deleteVehicle _chute;
        };
    };

    true
};

YFU_assetsFinalizeDeliveryAirdrop = {
    params ["_caller", "_airAsset", "_containers", "_targetATL"];
    if (_containers isEqualTo []) exitWith {false};
    if (isNull _airAsset) exitWith {false};
    if (isNil "YSF_fwRequestLogistics") exitWith {false};

    private _requestId = format ["LOGI_%1_%2_%3", clientOwner, floor (diag_tickTime * 1000), floor random 1000000];
    private _ackVariable = format ["YSF_FW_LOGISTICS_ACK_%1", _requestId];
    missionNamespace setVariable [_ackVariable, nil, false];
    private _containerRefs = _containers apply {netId _x};
    [netId _airAsset, _containerRefs, _targetATL, _requestId, netId _caller] remoteExecCall ["YSF_fwRequestLogistics", 2];

    private _deadline = diag_tickTime + 20;
    waitUntil {
        uiSleep 0.05;
        !isNil {missionNamespace getVariable _ackVariable} || {diag_tickTime > _deadline}
    };
    private _ack = missionNamespace getVariable [_ackVariable, []];
    private _accepted = (_ack param [0, false]) isEqualTo true;
    uiNamespace setVariable ["YFU_last_airdrop_request", [_requestId, _airAsset, _containers, _targetATL, _ack]];
    if (_accepted) then {
        [_airAsset, _targetATL, count _containers, getPosASL _airAsset] call YFU_assetsAirdropAnnounce;
    };
    _accepted
};

YFU_assetsSubmitDismiss = {
    if (uiNamespace getVariable ["YFU_submit_in_progress", false]) exitWith {};

    [] call YFU_assetsSetSubmitOverlay;

    private _ok = uiNamespace getVariable ["YFU_submit_success", false];
    if (_ok) then {
        uiNamespace setVariable ["YFU_fabricator_queue_map", createHashMap];
        uiNamespace setVariable ["YFU_fabricator_queue_order", []];
        call YFU_assetsRefreshQueue;
    };

    uiNamespace setVariable ["YFU_submit_success", false];
};

YFU_assetsQueueAdjust = {
    params ["_key", "_delta"];
    if (_key isEqualTo "") exitWith {};

    private _map = uiNamespace getVariable ["YFU_fabricator_queue_map", createHashMap];
    private _order = uiNamespace getVariable ["YFU_fabricator_queue_order", []];

    private _entry = _map getOrDefault [_key, []];
    if (_entry isEqualTo []) exitWith {};

    private _obj = _entry # 0;
    private _count = (_entry # 1) + _delta;

    if (_count <= 0) then {
        _map deleteAt _key;
        _order = _order - [_key];
    } else {
        _map set [_key, [_obj, _count]];
    };

    uiNamespace setVariable ["YFU_fabricator_queue_map", _map];
    uiNamespace setVariable ["YFU_fabricator_queue_order", _order];
    call YFU_assetsRefreshQueue;
};

YFU_assetsRefreshList = {
    disableSerialization;

    private _ret = [YFU_IDC_ASSETS_LIST] call YFU_getControl;
    private _list = _ret # 0;
    private _ok = _ret # 1;
    if (!_ok) exitWith {};

    private _items = call YFU_fabricatorGetItems;
    uiNamespace setVariable ["YFU_fabricator_items", _items];

    lbClear _list;
    {
        private _idx = _list lbAdd ([_x] call YFU_assetsGetDisplayName);
        _list lbSetData [_idx, netId _x];
        private _pic = [_x] call YFU_assetsGetPicture;
        if ([_pic] call YFU_assetsIsImagePath) then {
            _list lbSetPicture [_idx, _pic];
        };
    } forEach _items;

    if (_items isEqualTo []) then {
        _list lbAdd "<No virtual storage items found>";
    };
};

YFU_assetsBuildInspectEntries = {
    params ["_obj"];

    private _entries = [];

    private _weapons = getWeaponCargo _obj;
    {
        private _className = (_weapons # 0) # _forEachIndex;
        private _count = (_weapons # 1) # _forEachIndex;
        _entries pushBack [
            format ["%1x Weapon: %2", _count, ([_className] call YFU_assetsGetClassDisplayName)],
            ([_className] call YFU_assetsGetClassImage)
        ];
    } forEach (_weapons # 0);

    private _magazines = getMagazineCargo _obj;
    {
        private _className = (_magazines # 0) # _forEachIndex;
        private _count = (_magazines # 1) # _forEachIndex;
        _entries pushBack [
            format ["%1x Magazine: %2", _count, ([_className] call YFU_assetsGetClassDisplayName)],
            ([_className] call YFU_assetsGetClassImage)
        ];
    } forEach (_magazines # 0);

    private _items = getItemCargo _obj;
    {
        private _className = (_items # 0) # _forEachIndex;
        private _count = (_items # 1) # _forEachIndex;
        _entries pushBack [
            format ["%1x Item: %2", _count, ([_className] call YFU_assetsGetClassDisplayName)],
            ([_className] call YFU_assetsGetClassImage)
        ];
    } forEach (_items # 0);

    private _backpacks = getBackpackCargo _obj;
    {
        private _className = (_backpacks # 0) # _forEachIndex;
        private _count = (_backpacks # 1) # _forEachIndex;
        _entries pushBack [
            format ["%1x Backpack: %2", _count, ([_className] call YFU_assetsGetClassDisplayName)],
            ([_className] call YFU_assetsGetClassImage)
        ];
    } forEach (_backpacks # 0);

    if (_entries isEqualTo []) then {
        _entries pushBack ["No nested inventory detected.", "\a3\ui_f\data\igui\cfg\simpletasks\types\box_ca.paa"];
    };

    _entries
};

YFU_assetsItemSelected = {
    params ["_ctrl", "_index"];
    if (_index < 0) exitWith {};

    private _items = uiNamespace getVariable ["YFU_fabricator_items", []];
    if (_index >= count _items) exitWith {};

    private _obj = _items select _index;
    uiNamespace setVariable ["YFU_selected_fabricator_item", _obj];

    disableSerialization;
    private _ret = [YFU_IDC_INSPECT_LIST] call YFU_getControl;
    private _inspect = _ret # 0;
    private _ok = _ret # 1;
    if (!_ok) exitWith {};

    lbClear _inspect;
    {
        private _idx = _inspect lbAdd (_x # 0);
        private _pic = _x # 1;
        if ([_pic] call YFU_assetsIsImagePath) then {
            _inspect lbSetPicture [_idx, _pic];
        };
    } forEach ([_obj] call YFU_assetsBuildInspectEntries);
};

YFU_assetsListDblClick = {
    params ["_ctrl", "_index"];
    if (_index < 0) exitWith {};

    private _items = uiNamespace getVariable ["YFU_fabricator_items", []];
    if (_index >= count _items) exitWith {};

    uiNamespace setVariable ["YFU_selected_fabricator_item", _items select _index];
    call YFU_assetsQueueAdd;
};

YFU_assetsRefreshQueue = {
    disableSerialization;
    private _ret = [YFU_IDC_QUEUE_GROUP] call YFU_getControl;
    private _queueCtrl = _ret # 0;
    private _ok = _ret # 1;
    if (!_ok) exitWith {};

    {
        ctrlDelete _x;
    } forEach (uiNamespace getVariable ["YFU_fabricator_queue_dynamic", []]);

    private _display = uiNamespace getVariable ["YFU_FieldUtils_Display", displayNull];
    if (isNull _display) exitWith {};

    private _baseColor = missionNamespace getVariable ["YFU_monochromeBaseColor", [0.15, 0.95, 0.15, 1]];
    private _darkColor = [(_baseColor # 0) * 0.1, (_baseColor # 1) * 0.1, (_baseColor # 2) * 0.1, _baseColor # 3];

    private _groupPos = ctrlPosition _queueCtrl;
    private _groupW = _groupPos # 2;
    private _btnW = 0.04;
    private _rowH = 0.04;
    private _rowGap = 0.005;
    private _y = 0;
    private _made = [];
    private _entries = call YFU_assetsQueueEntries;

    {
        private _key = _x # 0;
        private _obj = _x # 1;
        private _count = _x # 2;

        private _name = [_obj] call YFU_assetsGetDisplayName;
        private _countW = 0.05;
        private _labelW = _groupW - (_btnW * 2) - _countW;

        private _label = _display ctrlCreate ["RscText", -1, _queueCtrl];
        _label ctrlSetPosition [0, _y, _labelW, _rowH];
        _label ctrlSetText _name;
        _label ctrlSetTextColor _baseColor;
        _label ctrlSetBackgroundColor [0, 0, 0, 0];
        _label ctrlCommit 0;
        _made pushBack _label;

        private _countCtrl = _display ctrlCreate ["RscText", -1, _queueCtrl];
        _countCtrl ctrlSetPosition [_labelW, _y, _countW, _rowH];
        _countCtrl ctrlSetText format ["%1x", _count];
        _countCtrl ctrlSetTextColor _baseColor;
        _countCtrl ctrlSetBackgroundColor [0, 0, 0, 0];
        _countCtrl ctrlCommit 0;
        _made pushBack _countCtrl;

        private _plus = _display ctrlCreate ["RscButton", -1, _queueCtrl];
        _plus ctrlSetPosition [_labelW + _countW, _y, _btnW, _rowH];
        _plus ctrlSetText "+";
        _plus ctrlSetTextColor _baseColor;
        _plus ctrlSetBackgroundColor _darkColor;
        _plus setVariable ["YFU_queue_key", _key];
        _plus ctrlAddEventHandler ["ButtonClick", {
            params ["_ctrl"];
            private _queueKey = _ctrl getVariable ["YFU_queue_key", ""];
            [_queueKey, 1] call YFU_assetsQueueAdjust;
        }];
        _plus ctrlCommit 0;
        _made pushBack _plus;

        private _minus = _display ctrlCreate ["RscButton", -1, _queueCtrl];
        _minus ctrlSetPosition [_labelW + _countW + _btnW, _y, _btnW, _rowH];
        _minus ctrlSetText "-";
        _minus ctrlSetTextColor _baseColor;
        _minus ctrlSetBackgroundColor _darkColor;
        _minus setVariable ["YFU_queue_key", _key];
        _minus ctrlAddEventHandler ["ButtonClick", {
            params ["_ctrl"];
            private _queueKey = _ctrl getVariable ["YFU_queue_key", ""];
            [_queueKey, -1] call YFU_assetsQueueAdjust;
        }];
        _minus ctrlCommit 0;
        _made pushBack _minus;

        _y = _y + _rowH + _rowGap;
    } forEach _entries;

    uiNamespace setVariable ["YFU_fabricator_queue_dynamic", _made];
};

YFU_assetsQueueAdd = {
    private _obj = uiNamespace getVariable ["YFU_selected_fabricator_item", objNull];
    if (isNull _obj) exitWith {hint "Select an item to add to queue.";};

    private _key = [_obj] call YFU_assetsQueueKeyForObject;
    if (_key isEqualTo "") exitWith {};

    private _map = uiNamespace getVariable ["YFU_fabricator_queue_map", createHashMap];
    private _order = uiNamespace getVariable ["YFU_fabricator_queue_order", []];
    private _entry = _map getOrDefault [_key, []];

    if (_entry isEqualTo []) then {
        _map set [_key, [_obj, 1]];
        _order pushBack _key;
    } else {
        _map set [_key, [_entry # 0, (_entry # 1) + 1]];
    };

    uiNamespace setVariable ["YFU_fabricator_queue_map", _map];
    uiNamespace setVariable ["YFU_fabricator_queue_order", _order];
    call YFU_assetsRefreshQueue;
};

YFU_assetsSubmitOrder = {
    if (uiNamespace getVariable ["YFU_submit_in_progress", false]) exitWith {};

    private _sourceObjects = call YFU_assetsQueueExpandedObjects;
    private _totalCount = count _sourceObjects;
    if (_totalCount <= 0) exitWith {hint "Queue is empty.";};

    private _ctx = call YFU_assetsGetOpenContext;
    private _isAirdrop = _ctx getOrDefault ["isAirdrop", false];
    private _submitTargetATL = [];
    private _isValidGrid = true;
    if (_isAirdrop) then {
        private _gridText = call YFU_assetsReadDeliveryGrid;
        private _parsed = [_gridText] call YFU_parseGrid;
        _isValidGrid = !(_parsed isEqualTo []);
        if (_isValidGrid) then {
            _submitTargetATL = [(_parsed # 0) * 10, (_parsed # 1) * 10, 0];
            uiNamespace setVariable ["YFU_delivery_target_pos", _submitTargetATL];
        };
    };
    if (_isAirdrop && {!_isValidGrid}) exitWith {
        hint "Enter XY: 12345678 or 1234-5678";
    };

    uiNamespace setVariable ["YFU_submit_in_progress", true];
    uiNamespace setVariable ["YFU_submit_success", false];

    [_submitTargetATL] spawn {
        params [["_submitTargetATL", []]];
        disableSerialization;

        private _caller = player;
        private _ctx = call YFU_assetsGetOpenContext;
        private _fabricator = _ctx getOrDefault ["fabricator", objNull];
        private _isAirdrop = _ctx getOrDefault ["isAirdrop", false];
        private _grid = call YFU_assetsReadDeliveryGrid;
        private _targetATL = if (_isAirdrop) then {
            _submitTargetATL
        } else {
            uiNamespace getVariable ["YFU_delivery_target_pos", []]
        };
        private _entries = (call YFU_assetsQueueEntries) apply {[_x # 0, _x # 2]};
        private _totalCount = count (call YFU_assetsQueueExpandedObjects);
        uiNamespace setVariable ["YFU_last_submit_payload", [_fabricator, _grid, _isAirdrop]];

        [true, "Processing Order", "Initializing...", 0, false] call YFU_assetsSetSubmitOverlay;

        // The terminal asks; the server decides and builds. Nothing on this
        // machine creates a fabricated object.
        private _requestId = format ["YFU_%1_%2_%3", clientOwner, floor (diag_tickTime * 1000), floor random 1000000];
        // Transaction state is owner-bound, so the key this terminal waits on
        // includes its own owner id.
        private _resultKey = format ["YFU_ORDER_RESULT_%1#%2", clientOwner, _requestId];
        missionNamespace setVariable [_resultKey, nil, false];
        uiNamespace setVariable ["YFU_last_order_request", [_requestId, netId _fabricator, _entries, _isAirdrop]];
        [_requestId, netId _fabricator, _entries, _isAirdrop] remoteExecCall ["YFU_fnc_fabricateOrder", 2];

        private _duration = _totalCount max 1;
        private _start = diag_tickTime;
        private _nextStatusAt = _start;
        private _deadline = _start + 30;
        private _result = [];
        waitUntil {
            uiSleep 0.05;
            _result = missionNamespace getVariable [_resultKey, []];
            private _elapsed = diag_tickTime - _start;
            private _p = (_elapsed / _duration) min 1;
            if (diag_tickTime >= _nextStatusAt) then {
                [true, "Processing Order", selectRandom YFU_FABRICATOR_MESSAGES, _p, false] call YFU_assetsSetSubmitOverlay;
                _nextStatusAt = diag_tickTime + 2;
            } else {
                [true, "", "", _p, false] call YFU_assetsSetSubmitOverlay;
            };
            // Hold the overlay for the nominal duration so a fast order still
            // reads as work, but never wait past the deadline for a silent server.
            (!(_result isEqualTo []) && {_elapsed >= _duration}) || {diag_tickTime > _deadline}
        };

        [true, "", "", 1, false] call YFU_assetsSetSubmitOverlay;

        private _accepted = (_result param [1, false]) isEqualTo true;
        private _mode = _result param [2, "timeout"];
        private _containers = (_result param [4, []]) apply {objectFromNetId _x};
        private _positions = _result param [5, []];
        uiNamespace setVariable ["YFU_last_order_result", _result];

        private _success = _accepted;
        if (_accepted) then {
            switch (_mode) do {
                case "single": {
                    private _single = objectFromNetId (_result param [3, ""]);
                    if (isNull _single) then {
                        _success = false;
                    } else {
                        [_caller, _single] call ace_dragging_fnc_startCarry;
                        uiNamespace setVariable ["YFU_last_delivery_positions", _positions];
                    };
                };
                case "multi": {
                    uiNamespace setVariable ["YFU_last_delivery_positions", _positions];
                    [_caller, _positions] call YFU_assetsAnnounceDelivery;
                };
                case "airdrop": {
                    _success = [_caller, _fabricator, _containers, _targetATL] call YFU_assetsFinalizeDeliveryAirdrop;
                    // Vigil owns the aircraft and the cargo from here. Only the
                    // server may undo its own work if the handoff is refused.
                    if (!_success) then {
                        [_requestId] remoteExecCall ["YFU_fnc_fabricatorDiscardOrder", 2];
                    };
                };
                default {
                    _success = false;
                };
            };
        };

        if (!_success) then {
            [true, "Order Failed", "Unable to complete order. Click anywhere to continue.", 1, true] call YFU_assetsSetSubmitOverlay;
            uiNamespace setVariable ["YFU_submit_success", false];
        } else {
            [true, "Success", "Success! (Click anywhere to continue)", 1, true] call YFU_assetsSetSubmitOverlay;
            uiNamespace setVariable ["YFU_submit_success", true];
        };

        uiNamespace setVariable ["YFU_submit_in_progress", false];
    };
};

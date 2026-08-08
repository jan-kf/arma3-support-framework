#include "..\..\ui\idc.hpp"

YFU_fabricatorGetItems = {
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

    if ((typeName _pos2D) isEqualTo "ARRAY" && {(count _pos2D) >= 2}) then {
        [_pos2D # 0, _pos2D # 1, _z]
    } else {
        if ((typeName _center) isEqualTo "ARRAY" && {(count _center) >= 3}) then {
            _center
        } else {
            [0, 0, 0]
        };
    }
};

YFU_assetsFinalizeDeliverySingle = {
    params ["_caller", "_obj"];
    if (isNull _obj) exitWith {false};
    private _drop = [getPosATL _caller, 3, 0] call YFU_assetsFindSafeDropPos;
    _obj setPosATL _drop;
    [_caller, _obj] call ace_dragging_fnc_startCarry;
    true
};

YFU_assetsFinalizeDeliveryMulti = {
    params ["_caller", "_containers"];
    if (_containers isEqualTo []) exitWith {false};

    private _center = getPosATL _caller;
    private _deliveredPositions = [];
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
        private _c = _x;
        if (!isNull _c) then {
            private _drop = [_center, 4, _forEachIndex] call YFU_assetsFindSafeDropPos;
            _c setPosATL _drop;
            _c setVectorUp [0, 0, 1];
            _deliveredPositions pushBack _drop;

            private _dist = round (_center distance2D _drop);
            private _dirLabel = [_center, _drop] call _dirLabelFromPos;
            _relativeLines pushBack format ["%1. %2m %3", (_forEachIndex + 1), _dist, _dirLabel];
        };
    } forEach _containers;

    uiNamespace setVariable ["YFU_last_delivery_positions", _deliveredPositions];
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

YFU_assetsFinalizeDeliveryAirdrop = {
    params ["_caller", "_airAsset", "_containers", "_targetATL"];
    if (_containers isEqualTo []) exitWith {false};
    if (isNull _airAsset) exitWith {false};

    private _assetASL = getPosASL _airAsset;
    private _bb = boundingBoxReal _airAsset;
    private _assetHeight = abs (((_bb # 1) # 2) - ((_bb # 0) # 2));
    private _dropASLBase = _assetASL vectorAdd [0, 0, -((_assetHeight / 2) + 3)];


    private _targetMarker = "Sign_Sphere10cm_F" createVehicle [0, 0, 0];
    _targetMarker setPosATL _targetATL;
    _targetMarker hideObjectGlobal true;

    {
        private _container = _x;
        if (!isNull _container) then {
            private _offset = [(_forEachIndex mod 2) * 1.5, floor (_forEachIndex / 2) * 1.5, 0];
            _container setPosASL (_dropASLBase vectorAdd _offset);
            _container setVectorUp [0, 0, 1];
            [_container, _targetMarker, -2] call YOSHI_FLING_THING;
            if (_forEachIndex < ((count _containers) - 1)) then {
                uiSleep 3;
            };
        };
    } forEach _containers;

    deleteVehicle _targetMarker;
    [_airAsset, _targetATL, count _containers, _dropASLBase] call YFU_assetsAirdropAnnounce;
    true
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
        private _sourceObjects = call YFU_assetsQueueExpandedObjects;
        private _totalCount = count _sourceObjects;
        uiNamespace setVariable ["YFU_last_submit_payload", [_fabricator, _grid, _isAirdrop]];

        [true, "Processing Order", "Initializing...", 0, false] call YFU_assetsSetSubmitOverlay;

        private _mode = "error";
        private _success = false;
        private _singleObj = objNull;
        private _containers = [];
        private _tempSpawned = [];

        if (!_isAirdrop && {_totalCount isEqualTo 1}) then {
            private _stash = (getPosATL _caller) vectorAdd [0, 0, -40];
            _singleObj = [objNull, _caller, [_fabricator, _sourceObjects # 0, _stash]] call YOSHI_SPAWN_SAVED_ITEM_ACTION;
            _success = !(isNull _singleObj);
            _mode = "single";
        } else {
            private _stashBase = [0, 0, -200];

            {
                private _stash = _stashBase vectorAdd [(_forEachIndex mod 5) * 1.5, floor (_forEachIndex / 5) * 1.5, 0];
                private _obj = [objNull, _caller, [_fabricator, _x, _stash]] call YOSHI_SPAWN_SAVED_ITEM_ACTION;
                if (!isNull _obj) then {_tempSpawned pushBack _obj;};
            } forEach _sourceObjects;

            if ((count _tempSpawned) isEqualTo _totalCount) then {
                // Let newly spawned objects finish one simulation tick so raycast sizing is stable.
                {
                    _x setVectorUp [0, 0, 1];
                    _x setVelocity [0, 0, 0];
                } forEach _tempSpawned;
                uiSleep 0.1;

                private _pack = [_tempSpawned] call YOSHI_spawnContainersNearObjectsAndPackMulti;
                _success = _pack # 0;
                if (_success) then {
                    _containers = _pack # 1;
                };
            } else {
                _success = false;
            };
            _mode = (["multi", "airdrop"] select _isAirdrop);
        };

        private _duration = _totalCount max 1;
        private _start = diag_tickTime;
        private _nextStatusAt = _start;
        while {(diag_tickTime - _start) < _duration} do {
            private _elapsed = diag_tickTime - _start;
            private _p = _elapsed / _duration;
            if (diag_tickTime >= _nextStatusAt) then {
                [true, "Processing Order", selectRandom YFU_FABRICATOR_MESSAGES, _p, false] call YFU_assetsSetSubmitOverlay;
                _nextStatusAt = diag_tickTime + 2;
            } else {
                [true, "", "", _p, false] call YFU_assetsSetSubmitOverlay;
            };
            uiSleep 0.05;
        };

        [true, "", "", 1, false] call YFU_assetsSetSubmitOverlay;

        if (_success) then {
            private _delivered = false;
            switch (_mode) do {
                case "single": {
                    _delivered = [_caller, _singleObj] call YFU_assetsFinalizeDeliverySingle;
                };
                case "multi": {
                    _delivered = [_caller, _containers] call YFU_assetsFinalizeDeliveryMulti;
                };
                case "airdrop": {
                    _delivered = [_caller, _fabricator, _containers, _targetATL] call YFU_assetsFinalizeDeliveryAirdrop;
                };
                default {
                    _delivered = false;
                };
            };
            _success = _delivered;
        };

        if (!_success) then {
            { if (!isNull _x) then { deleteVehicle _x; }; } forEach _tempSpawned;
            { if (!isNull _x) then { deleteVehicle _x; }; } forEach _containers;
            [true, "Order Failed", "Unable to complete order. Click anywhere to continue.", 1, true] call YFU_assetsSetSubmitOverlay;
            uiNamespace setVariable ["YFU_submit_success", false];
        } else {
            [true, "Success", "Success! (Click anywhere to continue)", 1, true] call YFU_assetsSetSubmitOverlay;
            uiNamespace setVariable ["YFU_submit_success", true];
        };

        uiNamespace setVariable ["YFU_submit_in_progress", false];
    };
};

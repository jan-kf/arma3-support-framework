#include "..\..\ui\idc.hpp"

YFU_getControl = {
    params ["_idc"];

    disableSerialization;
    private _display = uiNamespace getVariable ["YFU_FieldUtils_Display", displayNull];
    if (isNull _display) exitWith {[controlNull, false]};

    private _ctrl = _display displayCtrl _idc;
    [_ctrl, !(isNull _ctrl)]
};

YFU_UI_OpenFabricator = {
    params [
        ["_fabricator", objNull],
        ["_isAirdrop", false],
        ["_grid", ""]
    ];

    if (_grid isEqualTo "") then {
        _grid = mapGridPosition player;
    };

    uiNamespace setVariable ["YFU_selected_fabricator", _fabricator];
    uiNamespace setVariable ["YFU_open_context", createHashMapFromArray [
        ["fabricator", _fabricator],
        ["isAirdrop", _isAirdrop],
        ["grid", _grid]
    ]];

    private _display = uiNamespace getVariable ["YFU_FieldUtils_Display", displayNull];
    if (isNull _display) then {
        // If VIGIL is open, create Fabricator as a child display so VIGIL stays visible.
        private _tabletDisplay = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
        if (!isNull _tabletDisplay) then {
            _display = _tabletDisplay createDisplay "YFU_FieldUtils_Dialog";
            if (isNull _display) then {
                createDialog "YFU_FieldUtils_Dialog";
            };
        } else {
            createDialog "YFU_FieldUtils_Dialog";
        };
    } else {
        if !(isNil "YFU_assetsApplyDeliveryDefaults") then {
            [] call YFU_assetsApplyDeliveryDefaults;
        };
    };
};

YFU_UI_RegisterPage = {
    params ["_key", "_idc"];
    private _reg = uiNamespace getVariable ["YFU_ui_registry", createHashMap];
    _reg set [_key, _idc];
    uiNamespace setVariable ["YFU_ui_registry", _reg];
};

YFU_UI_SetPage = {
    params ["_key"];

    disableSerialization;
    private _display = uiNamespace getVariable ["YFU_FieldUtils_Display", displayNull];
    if (isNull _display) exitWith {};

    private _reg = uiNamespace getVariable ["YFU_ui_registry", createHashMap];
    private _idc = _reg getOrDefault [_key, -1];
    if (_idc < 0) exitWith {};

    {
        private _ctrl = _display displayCtrl _x;
        if (!isNull _ctrl) then {
            _ctrl ctrlShow false;
            _ctrl ctrlEnable false;
        };
    } forEach (values _reg);

    private _ctrl = _display displayCtrl _idc;
    if (!isNull _ctrl) then {
        _ctrl ctrlShow true;
        _ctrl ctrlEnable true;
    };
};

YFU_UI_Nav = {
    params [["_mode", ""], ["_key", ""]];

    switch (_mode) do {
        case "set": {
            [_key] call YFU_UI_SetPage;
        };
        default {
            ["set", "assets"] call YFU_UI_Nav;
        };
    };
};

YFU_UI_SetCorrectTablet = {
	private _slottedItems = assignedItems player;
	{
		if (_x in _slottedItems) exitWith {
			private _filename = format ["\FieldUtils\ui\assets\ui_tablet_%1.paa", toLower _x];
			ctrlSetText [YFU_IDC_TABLET_WRAPPER, _filename];
			[_filename] call YFU_fnc_debugMsg;
		};
	} forEach [
		"YSF_VigilTerminal_B",
		"YSF_VigilTerminal_I",
		"YSF_VigilTerminal_O"
	];
};

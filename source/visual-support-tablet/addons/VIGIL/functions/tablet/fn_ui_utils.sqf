#include "..\..\ui\idc.hpp"

YSF_UI_OpenTablet = {
	private _shouldHaveTablet = missionNamespace getVariable ['YSF_enableTablet', true];
	private _slottedItems = assignedItems player;
	if (_shouldHaveTablet && !("YSF_VigilTerminal_B" in _slottedItems || "YSF_VigilTerminal_I" in _slottedItems || "YSF_VigilTerminal_O" in _slottedItems))  exitWith {
		hint "'Tablet Required' is enabled in addon options, You will need to have a VIGIL Tablet in your GPS slot to use the combat tablet, or disable the setting in the addon options.";
	};
	private _display = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
	if (isNull _display) exitWith {
		createDialog "YSF_Tablet_Dialog";
	};
};

YSF_UI_SetCorrectTablet = {
	private _slottedItems = assignedItems player;
	{
		if (_x in _slottedItems) exitWith {
			private _filename = format ["\VIGIL\ui\assets\ui_tablet_%1.paa", toLower _x];
			ctrlSetText [IDC_TABLET_BG, _filename];
			[_filename] call YSF_fnc_debugMsg;
		};
	} forEach [
		"YSF_VigilTerminal_B",
		"YSF_VigilTerminal_I",
		"YSF_VigilTerminal_O"
	];
};

YSF_UI_RegisterPage = {
	params ["_key","_idc"];
	private _reg = uiNamespace getVariable ["YSF_tablet_registry", createHashMap];
	_reg set [_key, _idc];
	uiNamespace setVariable ["YSF_tablet_registry", _reg];
};

YSF_UI_SetPage = {
	params ["_key"];

	private _display = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
	if (isNull _display) exitWith {};
	private _reg = uiNamespace getVariable ["YSF_tablet_registry", createHashMap];
	private _idc = _reg getOrDefault [_key, -1];
	if (_idc < 0) exitWith {};
	
	{
		private _ctrl = _display displayCtrl _x;
		if (!isNull _ctrl) then {_ctrl ctrlShow false};
	} forEach values _reg;

	private _ctrl = _display displayCtrl _idc;
	
	if (!isNull _ctrl) then {_ctrl ctrlShow true};

	private _list = _display displayCtrl IDC_TABLET_LIST;

	if (!isNull _list) then {
		private _n = lbSize _list;
		for "_i" from 0 to (_n - 1) do {
			if ((_list lbData _i) isEqualTo _key) exitWith {
			if ((lbCurSel _list) != _i) then {
				uiNamespace setVariable ["YSF_tablet_silent", true];
				_list lbSetCurSel _i;
				uiNamespace setVariable ["YSF_tablet_silent", false];
			};
			};
		};
	};
};

YSF_UI_Nav = {
	params ["_mode","_key"];

	private _display = uiNamespace getVariable ["YSF_Tablet_Display", displayNull];
	if (isNull _display) exitWith {};
	private _reg = uiNamespace getVariable ["YSF_tablet_registry", createHashMap];
	private _list = _display displayCtrl IDC_TABLET_LIST;
	if (isNull _list) exitWith {};

	switch (_mode) do {
	case "build": {
		lbClear _list;
		{
		private _k = _x;
		private _i = _list lbAdd (toUpper _k);
		_list lbSetData [_i, _k];
		} forEach keys _reg;
	};
	case "set": {
		[_key] call YSF_UI_SetPage;
	};
	default {
		["build",""] call YSF_UI_Nav;
		["set","assets"] call YSF_UI_Nav;
	};
	};

};

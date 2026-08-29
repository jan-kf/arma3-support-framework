YFU_initLoadingActions = {
	private _logiActions = [
		"logiActions", "Logistics", "\a3\ui_f\data\igui\cfg\simpletasks\types\Container_ca.paa",
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Statement code
			true
		}, 
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Conditional Code
			private _isNearVehicles = (count ([_target, _caller, []] call YOSHI_getSuppliesAction)) > 0;
			private _isNotAttached = (attachedTo _target) isEqualTo objNull;

			_isNearVehicles && _isNotAttached
		},
		{
			params ["_target", "_caller", "_params"];
			
			[_target, _caller, _params] call YOSHI_getSuppliesAction;
		}
	] call ace_interact_menu_fnc_createAction;

	["Land_Pallet_F", 0, ["ACE_MainActions"], _logiActions, true] call ace_interact_menu_fnc_addActionToClass;
	["ReammoBox_F", 0, ["ACE_MainActions"], _logiActions, true] call ace_interact_menu_fnc_addActionToClass;
	["LandVehicle", 0, ["ACE_MainActions"], _logiActions, true] call ace_interact_menu_fnc_addActionToClass;
	["UAV_01_base_F", 0, ["ACE_MainActions"], _logiActions, true] call ace_interact_menu_fnc_addActionToClass;
};

YFU_initObjectHandling = {
	{
		[_x] call YOSHI_setObjectLoadHandling;
	} forEach entities "ReammoBox_F";

	{
       [_x, true, [0, 1.6, 0]] call ace_dragging_fnc_setDraggable;
       [_x, true, [0, 1.6, 1]] call ace_dragging_fnc_setCarryable;
	} forEach entities "Land_Pallet_F";
};
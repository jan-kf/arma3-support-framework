/*
Bear one another’s burdens,
and so fulfill the law of Christ.
(Galatians 6:2)

Lord, give strength to those who carry,
patience to those who pull,
and safe passage to those in need of aid.
Amen.
*/

YFU_initTowingActions = {
	private _TowActions = [
		"TowActions", "Towing", "\a3\ui_f\data\igui\cfg\simpletasks\types\Use_ca.paa",
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Statement code
			true
		}, 
		{
			params ["_target", "_caller", "_actionId", "_arguments"];
			// Condition code here
			true
		},
		{
			params ["_target", "_caller", "_params"];
			private _actions = [_target, _caller, _params] call YOSHI_towRopeActions;
			_actions 

		}
	] call ace_interact_menu_fnc_createAction;

	private _stowRopesAction = [
		"YOSHI_StowRopes", "Stow ropes", "\A3\ui_f\data\map\markers\nato\respawn_unknown_ca.paa",
		{
			params ["_target", "_caller", "_args"];
			[_target] call YFU_fnc_towRequestStow;
		},
		{
			params ["_target", "_caller", "_args"];
			(vehicle _caller == _target) &&
			{(driver _target) isEqualTo _caller} &&
			{(_target getVariable ["YFU_TOW_ACTIVE", []]) isNotEqualTo []}
		}
	] call ace_interact_menu_fnc_createAction;
	
	["LandVehicle", 0, ["ACE_MainActions"], _TowActions, true] call ace_interact_menu_fnc_addActionToClass;
	["AllVehicles", 0, ["ACE_MainActions"], _stowRopesAction, true] call ace_interact_menu_fnc_addActionToClass;
};
params ["_admin", "_caller", "_params"];

private _actions = [];

private _ik_thread = _admin getVariable ["YOSHI_instantKillThread", scriptNull];

if (isNull _ik_thread) then {
	private _activateInstantKillAction = [
		format["activateInstantKill-%1", netId _admin], "Activate Instant Kill", "\a3\Ui_F_Curator\Data\CfgMarkers\kia_ca.paa",
		{
			params ["_target", "_caller", "_admin"];

			[_admin] call YOSHI_activateInstantKill;

			
		}, 
		{
			params ["_target", "_caller", "_admin"];

			true
		},
		{},
		_admin
	] call ace_interact_menu_fnc_createAction;
	_actions pushBack [_activateInstantKillAction, [], _admin];
} else {
	private _deactivateInstantKillAction = [
		format["deactivateInstantKill-%1", netId _admin], "Deactivate Instant Kill", "",
		{
			params ["_target", "_caller", "_admin"];

			[_admin] call YOSHI_deactivateInstantKill;

		}, 
		{
			params ["_target", "_caller", "_admin"];

			true
		},
		{},
		_admin
	] call ace_interact_menu_fnc_createAction;
	_actions pushBack [_deactivateInstantKillAction, [], _admin];
};

_actions

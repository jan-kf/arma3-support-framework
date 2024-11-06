params ["_box", "_caller", "_params"];

private _actions = [];


{
	private _vic = _x;
	private _checks = _vic canVehicleCargo _box;

	if ((_checks select 0) && (_checks select 1)) then {
		private _loadSuppliesAction = [
			format["loadSupplies-%1", netId _vic], format ["Load Into %1", getText (configFile >> "CfgVehicles" >> typeOf _vic >> "displayName")], "",
			{
				params ["_target", "_caller", "_vic"];

				_vic setVehicleCargo _target;
			}, 
			{
				params ["_target", "_caller", "_vic"];

				true
			},
			{},
			_vic
		] call ace_interact_menu_fnc_createAction;
		_actions pushBack [_loadSuppliesAction, [], _box];
	};

} forEach (_box nearEntities ['AllVehicles', 10]);

_actions

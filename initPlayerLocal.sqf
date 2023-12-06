
private _insertVehicles = {
    params ["_target", "_caller", "_params"];
	
	private _actions = [];
	private _registeredVehicles = call (missionNamespace getVariable "getRegisteredVehicles");
	{
		private _vehicle = _x;
		private _vehicleClass = typeOf _vehicle;
		private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
		private _vicAction = [
			netId _vehicle, format["%1", _vehicleDisplayName], "",
			{
				//statement
				true		
			}, 
			{
				params ["_target", "_caller", "_vic"];
				// Condition code here
				private _registered = _vic getVariable ["isRegistered", false];
				_registered
			},
			{
				params ["_target", "_caller", "_params"];
				
				private _actions = [];
				
				private _vehicle = _target;
				private _vehicleClass = typeOf _vehicle;
				private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
				
				private _vicDeployAction = [
					format["%1-deploy", netId _vehicle], "Deploy!", "",
					{
						// statement 
						params ["_target", "_caller", "_vic"];
						_vic setVariable ["targetGroupLeader", _caller, true];
						_vic setVariable ["currentTask", "begin", true];
					}, 
					{
						params ["_target", "_caller", "_vic"];
						// // Condition code here
						private _notReinserting = !(_vic getVariable ["isReinserting", false]);
						private _task = _vic getVariable ["currentTask", "waiting"];
						private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "begin"]);
						_notReinserting && _notOnRestrictedTask
					},
					{},
					_vehicle
				] call ace_interact_menu_fnc_createAction;
				_actions pushBack [_vicDeployAction, [], _target];
				private _vicWaveOffAction = [
					format["%1-waveOff", netId _vehicle], "Wave Off!", "",
					{
						// statement 
						params ["_target", "_caller", "_vic"];
						_vic setVariable ["targetGroupLeader", _caller, true];
						_vic setVariable ["currentTask", "waveOff", true];
					}, 
					{
						params ["_target", "_caller", "_vic"];
						// // Condition code here
						private _isReinserting = _vic getVariable ["isReinserting", false];
						private _task = _vic getVariable ["currentTask", "waiting"];
						private _notOnRestrictedTask = !(_task in ["landingAtObjective","landingAtBase", "requestBaseLZ", "begin"]);
						_isReinserting && _notOnRestrictedTask
					},
					{},
					_vehicle
				] call ace_interact_menu_fnc_createAction;
				_actions pushBack [_vicWaveOffAction, [], _target]; 
					

				_actions
			},
			_vehicle
		] call ace_interact_menu_fnc_createAction;
		_actions pushBack [_vicAction, [], _vehicle]; 
		
	} forEach _registeredVehicles;

    _actions
};

private _redeploymentActions = [
	"RedeploymentActions", "Redeployment", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code
		true
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		('hgun_esd_01_F' in (items _caller))
	},
	_insertVehicles
] call ace_interact_menu_fnc_createAction;

[player, 1, ["ACE_SelfActions"], _redeploymentActions] call ace_interact_menu_fnc_addActionToObject;

// Define the action
private _registerVicAction = [
	"RegisterVehicle", "Register Vehicle", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code here
		// hint "Action executed!";
		_target setVariable ["isRegistered", true, true];
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		private _atBase = (_target distance2D home_base) < 500;
		private _not_registered = !(_target getVariable ["isRegistered", false]);
		// show if:
		_atBase && _not_registered
	}
] call ace_interact_menu_fnc_createAction;

private _unregisterVicAction = [
	"UnregisterVehicle", "Unregister Vehicle", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code here
		// hint "Action executed!";
		_target setVariable ["isRegistered", false, true];
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		private _atBase = (_target distance2D home_base) < 500;
		private _registered = _target getVariable ["isRegistered", false];
		// show if:
		_atBase && _registered
	}
] call ace_interact_menu_fnc_createAction;

// Add the actions to the Helicopter class
["Helicopter", 0, ["ACE_MainActions"], _registerVicAction, true] call ace_interact_menu_fnc_addActionToClass;
["Helicopter", 0, ["ACE_MainActions"], _unregisterVicAction, true] call ace_interact_menu_fnc_addActionToClass;

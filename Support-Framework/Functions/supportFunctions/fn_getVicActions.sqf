params ["_target", "_caller", "_params"];
private _registerVicAction = [
	"RegisterVehicle", "<t color='#2daaf7'>Register Vehicle</t>", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code here
		// hint "Action executed!";
		_target setVariable ["isRegistered", true, true];
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		private _atBase = _target call YOSHI_fnc_isAtBase;
		private _not_registered = !(_target getVariable ["isRegistered", false]);
		private _isArty = _target getVariable ["isArtillery", false];
		// show if:
		(_atBase || _isArty) && _not_registered
	}
] call ace_interact_menu_fnc_createAction;

private _unregisterVicAction = [
	"UnregisterVehicle", "<t color='#ffda36'>Unregister Vehicle</t>", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code here
		// hint "Action executed!";
		_target setVariable ["isRegistered", false, true];
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		private _atBase = _target call YOSHI_fnc_isAtBase;
		private _registered = _target getVariable ["isRegistered", false];
		private _isArty = _target getVariable ["isArtillery", false];
		// show if:
		(_atBase || _isArty) && _registered
	}
] call ace_interact_menu_fnc_createAction;

private _assignCasVicAction = [
	"AssignCasVehicle", "<t color='#f7812d'>Assign to CAS</t>", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code here
		_target setVariable ["isCAS", true, true];
		[_target, format ["%1 is ready for tasking... ",groupId group _target]] call YOSHI_fnc_sendSideText;
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here

		private _CasConfigured = YOSHI_SUPPORT_CAS_CONFIG_OBJECT call ["isInitialized"];
		private _atBase = _target call YOSHI_fnc_isAtBase;
		private _registered = _target getVariable ["isRegistered", false];
		private _isCAS = _target getVariable ["isCAS", false];
		private _isArty = _target getVariable ["isArtillery", false];
		
		_nonCombatKeywords = ["safe", "designator", "horn"];  // these are works that appear in some cases but should be disregarded as weapons
		_allWeapons = weapons _target; 
		_combatWeapons = _allWeapons select { 
			_isCombatWeapon = true;
			_weaponNameLower = toLower _x; 
			{  
				if (toLower _x in _weaponNameLower) then {
					_isCombatWeapon = false;
				}; 
			} forEach _nonCombatKeywords; 
			_isCombatWeapon; 
		}; // if count of the combat weapons is more than 0, then in theory the vic has weapons that can be used for CAS
		private _canDoArtilleryFire = _target getVariable ["isArtillery", false];
		// show if:
		_CasConfigured && !_canDoArtilleryFire && _atBase && _registered && !_isCAS && (count _combatWeapons > 0) && !_isArty
	}
] call ace_interact_menu_fnc_createAction;

private _unassignCasVicAction = [
	"UnassignCasVehicle", "<t color='#f2a974'>Remove from CAS</t>", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code here
		_target setVariable ["isCAS", false, true];
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		private _CasConfigured = YOSHI_SUPPORT_CAS_CONFIG_OBJECT call ["isInitialized"];
		private _atBase = _target call YOSHI_fnc_isAtBase;
		private _registered = _target getVariable ["isRegistered", false];
		private _isCAS = _target getVariable ["isCAS", false];

		private _canDoArtilleryFire = _target getVariable ["isArtillery", false];
		// show if:
		_CasConfigured && !_canDoArtilleryFire && _atBase && _registered && _isCAS
	}
] call ace_interact_menu_fnc_createAction;

private _assignArtyVicAction = [
	"AssignArtyVehicle", "<t color='#f7812d'>Assign to Artillery</t>", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code here
		_target setVariable ["isArtillery", true, true];
		[_target, format ["%1 is ready for tasking... ",groupId group _target]] call YOSHI_fnc_sendSideText;
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		private _artilleryConfigured = YOSHI_SUPPORT_ARTILLERY_CONFIG_OBJECT call ["isInitialized"];
		
		private _registered = _target getVariable ["isRegistered", false];
		
		private _canDoArtilleryFire = _target getVariable ["isArtillery", false];

		// show if:
		_artilleryConfigured && _canDoArtilleryFire && _registered
	}
] call ace_interact_menu_fnc_createAction;

private _unassignArtyVicAction = [
	"UnassignArtyVehicle", "<t color='#f2a974'>Remove from Artillery</t>", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code here
		_target setVariable ["isArtillery", false, true];
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		private _artilleryConfigured = YOSHI_SUPPORT_ARTILLERY_CONFIG_OBJECT call ["isInitialized"];
		
		private _registered = _target getVariable ["isRegistered", false];
		
		private _canDoArtilleryFire = _target getVariable ["isArtillery", false];

		// show if:
		_artilleryConfigured && !_canDoArtilleryFire && _registered
	}
] call ace_interact_menu_fnc_createAction;

private _requestVicRedeployAction = [
	"RequestRedeploy", "<t color='#5EC445'>Request Redeploy</t>", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code here
		// hint "Action executed!";
		_target setVariable ["requestingRedeploy", true, true];
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		private _atBase = _target call YOSHI_fnc_isAtBase;
		private _registered = _target getVariable ["isRegistered", false];
		private _notRequested = !(_target getVariable ["requestingRedeploy", false]);
		private _isCAS = _target getVariable ["isCAS", false];
		private _isArty = _target getVariable ["isArtillery", false];
		
		// show if:
		_atBase && _registered && _notRequested && !_isCAS && !_isArty
	}
] call ace_interact_menu_fnc_createAction;

private _cancelVicRedeployAction = [
	"CancelRedeploy", "<t color='#fae441'>Cancel Redeploy Request</t>", "",
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Statement code here
		// hint "Action executed!";
		_target setVariable ["requestingRedeploy", false, true];
	}, 
	{
		params ["_target", "_caller", "_actionId", "_arguments"];
		// Condition code here
		private _atBase = _target call YOSHI_fnc_isAtBase;
		private _registered = _target getVariable ["isRegistered", false];
		private _requested = _target getVariable ["requestingRedeploy", false];
		private _isCAS = _target getVariable ["isCAS", false];
		private _isArty = _target getVariable ["isArtillery", false];
		
		// show if:
		_atBase && _registered && _requested && !_isCAS && !_isArty
	}
] call ace_interact_menu_fnc_createAction;
private _actions = [];
_actions pushBack [_registerVicAction, [], _target];
_actions pushBack [_unregisterVicAction, [], _target];
_actions pushBack [_assignCasVicAction, [], _target];
_actions pushBack [_unassignCasVicAction, [], _target];
_actions pushBack [_requestVicRedeployAction, [], _target];
_actions pushBack [_cancelVicRedeployAction, [], _target];

_actions
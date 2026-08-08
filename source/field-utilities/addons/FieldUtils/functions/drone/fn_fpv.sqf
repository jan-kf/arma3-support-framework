/*
Lord, you have searched me and you know me.
You discern my thoughts from afar.
(Psalm 139)

Guide our sight from above,
that what is hidden may be revealed,
and what is revealed may be rightly judged.
Amen.
*/

YFU_fnc_configureUAVLocal = {
	params ["_entity"];

	if (isNull _entity) exitWith {};
	if (!local _entity) exitWith {
		["YFU_fnc_configureUAVLocal", _entity, [_entity]] call YCD_fnc_runOnObjectOwner;
	};
	if (_entity getVariable ["YFU_UAV_LocalConfigured", false]) exitWith {};

	_entity setVariable ["YFU_UAV_LocalConfigured", true];

	_entity addEventHandler ["Engine", {
		params ["_vehicle", "_engineState"];
		if (_engineState) then {detach _vehicle} else {_vehicle call YOSHI_attachToBelow};
	}];

	[_entity, true, [0,1,0]] call ace_dragging_fnc_setDraggable;
	[_entity, true] call ace_dragging_fnc_setCarryable;
	_entity setFuelConsumptionCoef 0.1;
	_entity setUnitTrait ["camouflageCoef", 0.3];
};

YFU_fnc_playRandomFpvClickLocal = {
	playSound (selectRandom ["YFU_FpvClick1", "YFU_FpvClick2"]);
};

YFU_fnc_uavAttachIED = {
	params ["_vic"];

	if (isNull _vic) exitWith {};
	if (!local _vic) exitWith {
		["YFU_fnc_uavAttachIED", _vic, [_vic]] call YCD_fnc_runOnObjectOwner;
	};

	_vic setVariable ["YOSHI_UavHasIED", true, true];
	_vic say3D ["DufflebagShuffle", 100, 1];

	private _explosive = createVehicle ["ModuleExplosive_SatchelCharge_F", [0,0,0], [], 0, "CAN_COLLIDE"];
	_explosive attachTo [_vic, [0,0,0.1]];
	_vic setVariable ["YOSHI_UavIEDObject", _explosive, true];

	if !(_vic getVariable ["YOSHI_UavKilledHandlerAdded", false]) then {
		_vic setVariable ["YOSHI_UavKilledHandlerAdded", true, true];
		_vic addEventHandler ["Killed", {
			params ["_unit", "_killer", "_instigator", "_useEffects"];
			{ _x setDamage 1; } forEach (attachedObjects _unit);

			private _exploPos = getPosATL _unit;
			if ((_exploPos select 2) < 15) then {
				"Bo_Mk82" createVehicle (_exploPos vectorAdd [0,0,0.1]);
			} else {
				private _initPos = getPosASL _unit;
				{
					private _ex = createVehicle ["ModuleExplosive_Claymore_F", _initPos, [], 0, "CAN_COLLIDE"];
					_ex setVectorDirAndUp [_x, [0,0,1]];
					_ex setPosASL (_initPos vectorAdd (vectorDir _ex));
					_ex setDamage 1;
				} forEach [
					[-1,-1,-1], [-1,-1,0], [-1,-1,1],
					[-1,0,-1], [-1,0,0], [-1,0,1],
					[-1,1,-1], [-1,1,0], [-1,1,1],
					[0,-1,-1], [0,-1,0], [0,-1,1],
					[0,0,-1], [0,0,0], [0,0,1],
					[0,1,-1], [0,1,0], [0,1,1],
					[1,-1,-1], [1,-1,0], [1,-1,1],
					[1,0,-1], [1,0,0], [1,0,1],
					[1,1,-1], [1,1,0], [1,1,1],
					[0,1,10], [0,-1,-10]
				];
			};
			"HelicopterExploBig" createVehicle _exploPos;
		}];
	};
};

YFU_fnc_uavAttachMortars = {
	params ["_vic"];

	if (isNull _vic) exitWith {};
	if (!local _vic) exitWith {
		["YFU_fnc_uavAttachMortars", _vic, [_vic]] call YCD_fnc_runOnObjectOwner;
	};

	_vic setVariable ["YOSHI_UavOrdinanceCount", 2, true];
	_vic say3D ["DufflebagShuffle", 100, 0.75];
};

YFU_fnc_uavAttachGrenades = {
	params ["_vic"];

	if (isNull _vic) exitWith {};
	if (!local _vic) exitWith {
		["YFU_fnc_uavAttachGrenades", _vic, [_vic]] call YCD_fnc_runOnObjectOwner;
	};

	_vic setVariable ["YOSHI_UavGrenadeCount", 4, true];
	_vic say3D ["DufflebagShuffle", 100, 2];
};

YFU_fnc_uavDetonateIED = {
	params ["_vic"];

	if (isNull _vic) exitWith {};
	if (!local _vic) exitWith {
		["YFU_fnc_uavDetonateIED", _vic, [_vic]] call YCD_fnc_runOnObjectOwner;
	};

	_vic setDamage 1;
};

YFU_fnc_uavReleaseMortar = {
	params ["_vic"];

	if (isNull _vic) exitWith {};
	if (!local _vic) exitWith {
		["YFU_fnc_uavReleaseMortar", _vic, [_vic]] call YCD_fnc_runOnObjectOwner;
	};

	private _explosive = createVehicle ["Sh_82mm_AMOS", [0,0,0]];
	_explosive attachTo [_vic, [0,0.2,0]];
	detach _explosive;

	private _vicMortarCount = _vic getVariable ["YOSHI_UavOrdinanceCount", 1];
	_vic setVariable ["YOSHI_UavOrdinanceCount", _vicMortarCount - 1, true];
};

YFU_fnc_uavDropGrenade = {
	params ["_vic"];

	if (isNull _vic) exitWith {};
	if (!local _vic) exitWith {
		["YFU_fnc_uavDropGrenade", _vic, [_vic]] call YCD_fnc_runOnObjectOwner;
	};

	"GrenadeHand" createVehicle ((getPosATL _vic) vectorAdd [0,0,-0.1]);

	private _vicGrenadeCount = _vic getVariable ["YOSHI_UavGrenadeCount", 1];
	_vic setVariable ["YOSHI_UavGrenadeCount", _vicGrenadeCount - 1, true];
};

YFU_initFPV_Actions = {
	private _uavAction = [
		"UAV_field_task",
		"Field Actions",
		"\a3\ui_f\data\igui\cfg\simpletasks\types\Use_ca.paa",
		{},
		{
			params ["_vic", "_caller", "_params"];
			unitIsUAV _vic && alive _vic
		},
		{
			params ["_vic", "_caller", "_params"];
			private _actions = [];

			private _uavFieldActionIED = [
				"uavIED_attach",
				"Attach IED",
				"\a3\ui_f\data\igui\cfg\simpletasks\types\interact_ca.paa",
				{
					params ["_target", "_caller", "_args"];
					private _vic = _args select 0;
					call YFU_fnc_playRandomFpvClickLocal;
					[_vic] call YFU_fnc_uavAttachIED;
				},
				{
					params ["_target", "_caller", "_args"];
					private _vic = _args select 0;
					private _isUAV = unitIsUAV _vic;
					private _vicHasIED = _vic getVariable ["YOSHI_UavHasIED", false];
					private _vicHasMortar = _vic getVariable ["YOSHI_UavOrdinanceCount", 0] > 0;
					_isUAV && !_vicHasIED && !_vicHasMortar
				},
				{},
				[_vic]
			] call ace_interact_menu_fnc_createAction;
			_actions pushBack [_uavFieldActionIED, [], _vic];

			private _uavFieldActionMortar = [
				"uavMortar_attach",
				"Attach 2 Mortar Rounds",
				"\a3\ui_f\data\igui\cfg\simpletasks\types\interact_ca.paa",
				{
					params ["_target", "_caller", "_args"];
					private _vic = _args select 0;
					call YFU_fnc_playRandomFpvClickLocal;
					[_vic] call YFU_fnc_uavAttachMortars;
				},
				{
					params ["_target", "_caller", "_args"];
					private _vic = _args select 0;
					private _isUAV = unitIsUAV _vic;
					private _vicHasMortar = _vic getVariable ["YOSHI_UavOrdinanceCount", 0] > 0;
					private _vicHasIED = _vic getVariable ["YOSHI_UavHasIED", false];
					_isUAV && !_vicHasMortar && !_vicHasIED
				},
				{},
				[_vic]
			] call ace_interact_menu_fnc_createAction;
			_actions pushBack [_uavFieldActionMortar, [], _vic];

			private _uavFieldActionGrenade = [
				"uavGrenade_attach",
				"Attach 4 Grenades",
				"\a3\ui_f\data\igui\cfg\simpletasks\types\interact_ca.paa",
				{
					params ["_target", "_caller", "_args"];
					private _vic = _args select 0;
					call YFU_fnc_playRandomFpvClickLocal;
					[_vic] call YFU_fnc_uavAttachGrenades;
				},
				{
					params ["_target", "_caller", "_args"];
					private _vic = _args select 0;
					private _isUAV = unitIsUAV _vic;
					private _vicHasGrenades = _vic getVariable ["YOSHI_UavGrenadeCount", 0] > 0;
					_isUAV && !_vicHasGrenades
				},
				{},
				[_vic]
			] call ace_interact_menu_fnc_createAction;
			_actions pushBack [_uavFieldActionGrenade, [], _vic];

			_actions
		}
	] call ace_interact_menu_fnc_createAction;

	private _uavDetonateAction = [
		"uavIED_detonate",
		"Detonate",
		"\a3\ui_f\data\igui\cfg\simpletasks\types\destroy_ca.paa",
		{
			params ["_target", "_caller", "_args"];
			call YFU_fnc_playRandomFpvClickLocal;
			[_target] call YFU_fnc_uavDetonateIED;
		},
		{
			params ["_target", "_caller", "_args"];
			alive _target
			&& { _target getVariable ["YOSHI_UavHasIED", false] }
			&& { _caller == currentPilot _target || { _caller == UAVControl _target select 0 } }
		},
		{}
	] call ace_interact_menu_fnc_createAction;

	private _uavReleaseMortarAction = [
		"uavMortar_release",
		"Release Mortar Round",
		"\A3\ui_f\data\map\markers\military\warning_CA.paa",
		{
			params ["_target", "_caller", "_args"];
			call YFU_fnc_playRandomFpvClickLocal;
			[_target] call YFU_fnc_uavReleaseMortar;
		},
		{
			params ["_target", "_caller", "_args"];
			(_target getVariable ["YOSHI_UavOrdinanceCount", 0]) > 0
			&& { _caller == currentPilot _target || { _caller == UAVControl _target select 0 } }
		},
		{}
	] call ace_interact_menu_fnc_createAction;

	private _uavDropGrenadeAction = [
		"uavGrenade_drop",
		"Drop Grenade",
		"\A3\ui_f\data\map\markers\military\warning_CA.paa",
		{
			params ["_target", "_caller", "_args"];
			call YFU_fnc_playRandomFpvClickLocal;
			[_target] call YFU_fnc_uavDropGrenade;
		},
		{
			params ["_target", "_caller", "_args"];
			(_target getVariable ["YOSHI_UavGrenadeCount", 0]) > 0
			&& { _caller == currentPilot _target || { _caller == UAVControl _target select 0 } }
		},
		{}
	] call ace_interact_menu_fnc_createAction;

	["AllVehicles", 0, ["ACE_MainActions"], _uavAction, true] call ace_interact_menu_fnc_addActionToClass;
	["AllVehicles", 1, ["ACE_SelfActions"], _uavDetonateAction, true] call ace_interact_menu_fnc_addActionToClass;
	["AllVehicles", 1, ["ACE_SelfActions"], _uavReleaseMortarAction, true] call ace_interact_menu_fnc_addActionToClass;
	["AllVehicles", 1, ["ACE_SelfActions"], _uavDropGrenadeAction, true] call ace_interact_menu_fnc_addActionToClass;
};

params ["_logic", "_id", "_params"];

YOSHI_FW_RECON_CONFIG_OBJECT = createHashMapObject [[
	["#flags", ["sealed"]],
	["#create", {
		params ["_hashMap"];

		_self set ["syncedObjects", synchronizedObjects _hashMap];

		private _fw_recon_units = [];
		{
			if (_x isKindOf "Module_F") then {
				if (_x isKindOf "SupportFramework_Map_Infil_Module") then {
					_self set ["MapArriveNode", getPosASL _x];
				};
				if (_x isKindOf "SupportFramework_Map_Exfil_Module") then {
					_self set ["MapDepartNode", getPosASL _x];
				};
			} else {
				_fw_recon_units pushBack (_x call copyVehicle);
				deleteVehicleCrew _unit;
				deleteVehicle _x;
			};
		} forEach (_self get "syncedObjects");

		_self set ["SavedUnits", _fw_recon_units];

	}],
	["#clone", {  }],
	["#delete", {  }],
	["#str", { "YOSHI_SUPPORT_CAS_CONFIG_OBJECT" }],
	["SavedUnits", { _self get "SavedUnits" }],
	["MapArriveNode", { _self get ["MapArriveNode", [0,0,0]] }],
	["MapDepartNode", { _self get ["MapDepartNode", [0,0,0]] }],
	["syncedObjects", { _self get "syncedObjects" }],
	["isInitialized", { true }]
], _logic];


YOSHI_Deploy_FW_Recon = {
	params ["_type"];

	private _units = +(YOSHI_FW_RECON_CONFIG_OBJECT get "SavedUnits");
	{
		if ((_x select 0) isEqualTo _type) exitWith {
			_units deleteAt _forEachIndex;
			private _newVehicle = [YOSHI_FW_RECON_CONFIG_OBJECT get "MapArriveNode", _x, ((YOSHI_FW_RECON_CONFIG_OBJECT get "MapArriveNode") getDir (YOSHI_FW_RECON_CONFIG_OBJECT get "MapDepartNode"))] call pasteVehicle;
			YOSHI_FW_RECON_CONFIG_OBJECT set ["SavedUnits", _units];
			_newVehicle
		};
	} forEach _units;
};

YOSHI_Stash_FW_Recon = {
	params ["_unit"];

	private _units = +(YOSHI_FW_RECON_CONFIG_OBJECT get "SavedUnits");
	_units pushBack (_unit call copyVehicle);
	YOSHI_FW_RECON_CONFIG_OBJECT set ["SavedUnits", _units];
	deleteVehicleCrew _unit;
	deleteVehicle _unit;
};
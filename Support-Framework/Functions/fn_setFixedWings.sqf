params ["_logic", "_id", "_params"];

YOSHI_FW_CONFIG_OBJECT = createHashMapObject [[
	["#flags", ["sealed"]],
	["#create", {
		params ["_hashMap"];

		[_self, _hashMap, "RequiredItems", YOSHI_DefaultRequiredItems_Reinsert] call YOSHI_initList;

		_self set ["syncedObjects", synchronizedObjects _hashMap];

		private _fw_units = [];
		{
			if (_x isKindOf "Module_F") then {
				if (_x isKindOf "SupportFramework_Map_Infil_Module") then {
					_self set ["MapArriveNode", [(getPosASL _x)] call YOSHI_findNearestBorderPos];
				};
				if (_x isKindOf "SupportFramework_Map_Exfil_Module") then {
					_self set ["MapDepartNode", [(getPosASL _x)] call YOSHI_findNearestBorderPos];
				};
			} else {
				_fw_units pushBack (_x call YOSHI_COPY_VEHICLE);
				deleteVehicleCrew _x;
				deleteVehicle _x;
			};
		} forEach (_self get "syncedObjects");

		_self set ["SavedUnits", _fw_units];
        _self set ["DeployedUnits", []];

	}],
	["#clone", {  }],
	["#delete", {  }],
	["#str", { "YOSHI_FW_CONFIG_OBJECT" }],
    ["RequiredItems", { _self get "RequiredItems" }],
	["SavedUnits", { _self get "SavedUnits" }],
    ["DeployedUnits", { _self get "DeployedUnits" }],
	["MapArriveNode", { _self get ["MapArriveNode", [0,0,0]] }],
	["MapDepartNode", { _self get ["MapDepartNode", [0,0,0]] }],
	["syncedObjects", { _self get "syncedObjects" }],
	["DeployUnit", {
		params ["_self", "_type", ["_caller", objNull]];

		private _units = +(_self get "SavedUnits");
		{
			if ((_x select 0) isEqualTo _type) exitWith {
				_units deleteAt _forEachIndex;
				private _newVehicle = [_self get "MapArriveNode", _x, ((_self get "MapArriveNode") getDir (_self get "MapDepartNode")), 2000] call YOSHI_PASTE_VEHICLE;
				_self set ["SavedUnits", _units];
                _self set ["DeployedUnits", (_self get "DeployedUnits") + [_newVehicle]];
                if (!isNull _caller) then {
                    _newVehicle setVariable ["YOSHI_FW_CALLER", _caller, true];
                };
                _newVehicle call YOSHI_CREATE_FW_THREAD;
				_newVehicle
			};
		} forEach _units;
        publicVariable "YOSHI_FW_CONFIG_OBJECT";
	}],
	["StashUnit", {
		params ["_self", "_unit"];

		private _units = +(_self get "SavedUnits");
		_units pushBack (_unit call YOSHI_COPY_VEHICLE);
		_self set ["SavedUnits", _units];
        _self set ["DeployedUnits", (_self get "DeployedUnits") - [_unit]];
        private _fuelThread = _unit getVariable ["YOSHI_FW_THREAD", 0];
        terminate _fuelThread;
		deleteVehicleCrew _unit;
		deleteVehicle _unit;
        publicVariable "YOSHI_FW_CONFIG_OBJECT";
	}],
    ["isInitialized", { true }]
], _logic];
publicVariable "YOSHI_FW_CONFIG_OBJECT";

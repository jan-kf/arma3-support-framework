/*
 * Observe the native curator placement boundary on the placing client. The
 * configured module function itself executes later and cannot recover the
 * originating curator from remoteExecutedOwner.
 */
[] spawn {
	waitUntil {uiSleep 0.1; !isNull player && {clientOwner > 2}};
	private _installedOn = objNull;
	while {true} do {
		private _curator = getAssignedCuratorLogic player;
		if (_curator isNotEqualTo _installedOn) then {
			if (!isNull _installedOn) then {
				private _oldEh = _installedOn getVariable ["YAS_APS_ZeusPlacementEH", -1];
				if (_oldEh >= 0) then {_installedOn removeEventHandler ["CuratorObjectPlaced", _oldEh];};
				_installedOn setVariable ["YAS_APS_ZeusPlacementEH", nil];
			};
			_installedOn = _curator;
			if (!isNull _installedOn) then {
				private _eh = _installedOn addEventHandler ["CuratorObjectPlaced", {
					params ["_curator", "_logic"];
					if (isNull _logic || {typeOf _logic isNotEqualTo "YAS_APS_Zeus_Toggle_Module"}) exitWith {};
					private _targets = ((synchronizedObjects _logic) + [attachedTo _logic]) select {
						!isNull _x && {_x isKindOf "AllVehicles"}
					};
					_targets = _targets arrayIntersect _targets;
					private _target = if ((count _targets) isEqualTo 1) then {_targets # 0} else {objNull};
					private _operationId = format ["%1:%2:%3", clientOwner, netId _logic, diag_tickTime];
					_logic setVariable ["YAS_APS_ZeusOperationId", _operationId, true];
					private _rows = uiNamespace getVariable ["YAS_APS_ZEUS_CLIENT_PLACEMENT_AUDIT", []];
					_rows pushBack [_operationId, netId _logic, netId _target, netId _curator, clientOwner, local _logic, owner _logic, diag_tickTime];
					if ((count _rows) > 32) then {_rows deleteRange [0, (count _rows) - 32];};
					uiNamespace setVariable ["YAS_APS_ZEUS_CLIENT_PLACEMENT_AUDIT", _rows];
					[_logic, _target, _curator, _operationId] remoteExecCall ["YAS_fnc_apsZeusClaimServer", 2];
				}];
				_installedOn setVariable ["YAS_APS_ZeusPlacementEH", _eh];
			};
		};
		uiSleep 0.25;
	};
};

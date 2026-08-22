/*
St. Michael the Archangel,
defend us in battle,
be our protection against the
wickedness and snares of the Devil.
May God rebuke him, we humbly pray.
And do thou, O Prince of the Heavenly Host,
by the Power of God, thrust into hell Satan and all evil
spirits who wander the earth, seeking the ruin of souls.
Amen.
*/

[] call YSF_fwClientInit;
[] call YSF_irLaserViz_init;

[] spawn {
	waitUntil {uiSleep 0.1; !isNull player && {clientOwner > 2}};
	private _installedOn = objNull;
	while {true} do {
		private _curator = getAssignedCuratorLogic player;
		if (_curator isNotEqualTo _installedOn) then {
			if (!isNull _installedOn) then {
				private _oldEh = _installedOn getVariable ["YSF_WHITELIST_ZeusPlacementEH", -1];
				if (_oldEh >= 0) then {_installedOn removeEventHandler ["CuratorObjectPlaced", _oldEh];};
				_installedOn setVariable ["YSF_WHITELIST_ZeusPlacementEH", nil];
			};
			_installedOn = _curator;
			if (!isNull _installedOn) then {
				private _eh = _installedOn addEventHandler ["CuratorObjectPlaced", {
					params ["_curator", "_logic"];
					if (isNull _logic) exitWith {};
					private _class = typeOf _logic;
					private _route = switch (_class) do {
						case "YSF_Toggle_To_Whitelist_Module": {["whitelist", "YSF_WHITELIST_ZEUS_PLACEMENT_AUDIT", "YSF_fnc_whitelistZeusClaimServer"]};
						case "YSF_FixedWing_Zeus_Add_Module": {["fixed-wing", "YSF_FW_ZEUS_PLACEMENT_AUDIT", "YSF_fnc_fwModuleZeusClaimServer"]};
						default {[]};
					};
					if (_route isEqualTo []) exitWith {};
					_route params ["_prefix", "_auditName", "_claimFunction"];
					private _operationId = format ["%1-%2-%3-%4", _prefix, clientOwner, floor (diag_tickTime * 1000), floor random 1000000];
					private _rows = uiNamespace getVariable [_auditName, []];
					_rows pushBack [_operationId, netId _logic, _class, owner _logic, netId (attachedTo _logic), clientOwner, diag_tickTime];
					uiNamespace setVariable [_auditName, _rows];
					[_logic, _curator, _operationId] remoteExecCall [_claimFunction, 2];
				}];
				_installedOn setVariable ["YSF_WHITELIST_ZeusPlacementEH", _eh];
			};
		};
		uiSleep 0.25;
	};
};


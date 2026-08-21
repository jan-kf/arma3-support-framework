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
					if (isNull _logic || {typeOf _logic isNotEqualTo "YSF_Toggle_To_Whitelist_Module"}) exitWith {};
					private _operationId = format ["whitelist-%1-%2-%3", clientOwner, floor (diag_tickTime * 1000), floor random 1000000];
					private _rows = uiNamespace getVariable ["YSF_WHITELIST_ZEUS_PLACEMENT_AUDIT", []];
					_rows pushBack [_operationId, netId _logic, typeOf _logic, owner _logic, netId (attachedTo _logic), clientOwner, diag_tickTime];
					uiNamespace setVariable ["YSF_WHITELIST_ZEUS_PLACEMENT_AUDIT", _rows];
					[_logic, _curator, _operationId] remoteExecCall ["YSF_fnc_whitelistZeusClaimServer", 2];
				}];
				_installedOn setVariable ["YSF_WHITELIST_ZeusPlacementEH", _eh];
			};
		};
		uiSleep 0.25;
	};
};


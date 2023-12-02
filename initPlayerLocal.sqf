// Add an event handler to the player
player addEventHandler ["Take", {
    params ["_unit", "_container", "_item"];

	private _manifest = home_base getVariable "homeBaseManifest";

	[format ["%1 just took a %2 !!",_unit, _item]] remoteExec ["systemChat"];

	{
		private _vehicle = _x;
		private _playerActionMap = _vehicle getVariable "playerActionMap";

		if (isNil "_playerActionMap") then {
			_vehicle setVariable ["playerActionMap", createHashMap, true];
		};
		private _playerActionMap = _vehicle getVariable "playerActionMap";

		private _checkForAction = _playerActionMap get (netId _unit);
		if (isNil "_checkForAction") then{
			[[_unit, _vehicle], "redeployFunctions\addVicActionToPlayer.sqf"] remoteExec ["execVM", 0];
		};

	} forEach (_manifest get "vicRegistry");

}];
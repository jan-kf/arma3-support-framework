// Add an event handler to the player
player addEventHandler ["Take", {
    params ["_unit", "_container", "_item"];

	private _registeredVehicles = call (missionNamespace getVariable "getRegisteredVehicles");

	[format ["%1 just took a %2 !!",_unit, _item]] remoteExec ["systemChat"];

	{
		private _vehicle = _x;
		private _check = _unit getVariable (netId _vehicle);
		if (isNil "_check") then {
			[[_unit, _vehicle], "redeployFunctions\addVicActionToPlayer.sqf"] remoteExec ["execVM", 0];
		};
	} forEach _registeredVehicles;

}];
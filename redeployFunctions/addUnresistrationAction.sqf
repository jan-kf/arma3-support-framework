params ["_vehicle"];

diag_log "[REDEPLOY] adding unregister action...";

private _vicStatus = [_vehicle] call (missionNamespace getVariable "getVehicleStatus");

// add new action
private _vehicleClass = typeOf _vehicle;
private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
private _regActionID = _vehicle addAction [
	format ["<t color='#FF8000'>Unregister %1</t>", _vehicleDisplayName], 
	{
		private _vehicle = _this select 0;
		[_vehicle] call (missionNamespace getVariable "_unregisterVehicle");
	},
	nil, 6, false, true, "", "true", 5, false, "", ""
];

// save action id for later
_vicStatus set ["regActionID", _regActionID];

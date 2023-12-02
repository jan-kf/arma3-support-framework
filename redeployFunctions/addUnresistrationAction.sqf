params ["_vehicle"];

diag_log format ["[REDEPLOY] adding unregister action to %1", _vehicle];

// remove old action if it exists
private _oldRegActionID = _vehicle getVariable "regActionID";
if (!isNil "_oldRegActionID") then {
	_vehicle removeAction _oldRegActionID;
};

// add new action
private _vehicleClass = typeOf _vehicle;
private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
private _regActionID = _vehicle addAction [
	format ["<t color='#FF8000'>Unregister %1</t>", _vehicleDisplayName], 
	{
		private _vehicle = _this select 0;
		[[_vehicle], (missionNamespace getVariable "unregisterVehicle")] remoteExec ["call", 2];
	},
	nil, 6, false, true, "", "true", 5, false, "", ""
];

// save action id for later
_vehicle setVariable ["regActionID", _regActionID, true];

diag_log format ["[REDEPLOY] finished adding unregister action to %1", _vehicle];

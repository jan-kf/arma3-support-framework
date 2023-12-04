if (!isServer) exitWith {};

params ["_vehicle"];

[format ["adding register action to %1", _vehicle]] remoteExec ["systemChat"];
diag_log format ["[REDEPLOY] adding register action to %1", _vehicle];

// remove old action if it exists
private _oldRegActionID = _vehicle getVariable "regActionID";
if (!isNil "_oldRegActionID") exitWith {};

// add new action
private _vehicleClass = typeOf _vehicle;
private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
private _regActionID = _vehicle addAction [
	format ["<t color='#00ABFF'>Register %1</t>", _vehicleDisplayName],
	{
		params ["_target", "_caller", "_actionID", "_args"];
		private _vehicle = _this select 0;
		private _isRegistered = _vehicle getVariable ["isRegistered", false];
		if (_isRegistered) then {
			[[MissionNamespace, "CallToUnregisterVehicle", [_vehicle]], BIS_fnc_callScriptedEventHandler] remoteExec ["call", 2];
		} else {
			[[MissionNamespace, "CallToRegisterVehicle", [_vehicle]], BIS_fnc_callScriptedEventHandler] remoteExec ["call", 2];
		};
	},
	nil, 6, false, true, "", "true", 5, false, "", ""
];
// save action id for later
_vehicle setVariable ["regActionID", _regActionID, true];

diag_log format ["[REDEPLOY] finished adding registration action to %1", _vehicle];
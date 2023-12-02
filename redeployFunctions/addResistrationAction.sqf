params ["_vehicle"];

diag_log format ["[REDEPLOY] adding register action to %1", _vehicle];

// remove old action if it exists
private _oldRegActionID = _vehicle getVariable "regActionID";
if (!isNil "_oldRegActionID") then {
	_vehicle removeAction _oldRegActionID;
};

// remove any request for redeploy if it gets unregistered
// private _requestActionID = _status get "requestActionID";
// // _status set ["requestingRedeploy", false];

// // remove current action to stay up to date
// if (!isNil "_requestActionID") then {
// 	_vehicle removeAction _requestActionID;
// 	_status set ["requestActionID", nil];
// };

// add new action
private _vehicleClass = typeOf _vehicle;
private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
private _regActionID = _vehicle addAction [
	format ["<t color='#00ABFF'>Register %1</t>", _vehicleDisplayName], 
	{
		private _vehicle = _this select 0;
		[[_vehicle], (missionNamespace getVariable "registerVehicle")] remoteExec ["call", 2];
	},
	nil, 6, false, true, "", "true", 5, false, "", ""
];
// save action id for later
_vehicle setVariable ["regActionID", _regActionID, true];


diag_log format ["[REDEPLOY] finished adding register action to %1", _vehicle];

params ["_speaker", "_message"];

private _shutIt = (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["VicHush", false];

if (!_shutIt) then {
	[_speaker, _message] remoteExec ['vehicleChat'];
}

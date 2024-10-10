params ["_speaker", "_message"];

private _shutIt = YOSHI_HOME_BASE_CONFIG getVariable ["VicHush", false];

if (!_shutIt) then {
	[_speaker, _message] remoteExec ['vehicleRadio'];
}

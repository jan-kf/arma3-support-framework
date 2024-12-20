params ["_speaker", "_message"];

private _shutIt = YOSHI_HOME_BASE_CONFIG_OBJECT call ["VicHush"];

if (!_shutIt) then {
	[_speaker, _message] remoteExec ['vehicleChat'];
}

params ["_speaker", "_message"];

private _shutIt = YOSHI_HOME_BASE_CONFIG_OBJECT get "SideHush";

if (!_shutIt) then {
	[_speaker, _message] remoteExec ['sideRadio'];
}

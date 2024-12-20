params ["_speaker", "_message", ["_all", true]];

private _shutIt = YOSHI_HOME_BASE_CONFIG_OBJECT call ["SideHush"];

if (!_shutIt) then {
	if (_all) then {
		[_speaker, _message] remoteExecCall ['sideChat'];
	} else {
		_speaker sideChat _message
	};
};

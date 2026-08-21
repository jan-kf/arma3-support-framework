YSF_clearAllMarkers = {
	private _strikePatternMarkers = uiNamespace getVariable ["YOSHI_sp_markers", []];
	{
		deleteMarker _x;
	} forEach _strikePatternMarkers;

	private _displayMarkers = uiNamespace getVariable ["YSF_map_overlay_markers", []];
	{
		deleteMarker _x;
	} forEach _displayMarkers;
};

YSF_fnc_debugMsg = {
	params ["_msg"];
	[_msg, "YSF", "YSF_showDebugMessages"] call YCD_fnc_debugMsg;
};

YSF_fnc_notifyCurator = {
	params ["_msg", ["_title", "VIGIL Notification"], ["_duration", 5], ["_targets", 0], ["_onceKey", ""], ["_ttl", 3]];
	[_msg, _title, _duration, _targets, _onceKey, _ttl] call YCD_fnc_notifyCurator;
};

YSF_fnc_emitSideRadio = {
	params ["_speaker", "_message", ["_targets", 0], ["_onceKey", ""], ["_ttl", 3]];
	[_speaker, _message, _targets, _onceKey, _ttl, "YSF_playRadioMessages"] call YCD_fnc_emitSideRadio;
};

YSF_fnc_emitSideChat = {
	params ["_speaker", "_message", ["_targets", 0], ["_onceKey", ""], ["_ttl", 3]];
	[_speaker, _message, _targets, _onceKey, _ttl, "YSF_playSideMessages"] call YCD_fnc_emitSideChat;
};

YSF_toggleWhitelistedObject = {
  params ["_obj"];
  if (!isServer || {remoteExecutedOwner > 2}) exitWith {false};
  [_obj] call YSF_fnc_whitelistToggleServer
};

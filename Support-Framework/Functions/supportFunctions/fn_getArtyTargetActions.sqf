params ["_target", "_caller", "_params"];
	
private _targetActions = call YOSHI_fnc_createTargetsFromMarkers;
_targetActions append ([true] call YOSHI_fnc_createTargetsFromLasers);

_targetActions

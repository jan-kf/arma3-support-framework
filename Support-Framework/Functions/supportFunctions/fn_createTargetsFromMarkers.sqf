private _artyPrefixStr = YOSHI_SUPPORT_ARTILLERY_CONFIG getVariable ["ArtilleryPrefixes", ""];
private _artyPrefixes = if (_artyPrefixStr != "") then { _artyPrefixStr splitString ", " } else { ["target ", "firemission "] };
private _targetActions = [];
{
    private _marker = _x;
    private _markerName = markerText _marker;
    private _markerPos = getMarkerPos _marker;

    { 
        private _prefix = toLower _x;
        if (toLower _markerName find _prefix == 0) then {
            _targetActions append ([_markerPos, _markerName] call YOSHI_fnc_createTargetActions);
        };
    } forEach _artyPrefixes;
} forEach allMapMarkers;

_targetActions
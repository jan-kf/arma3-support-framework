private _targetActions = [];
{
    private _marker = _x;
    private _markerName = markerText _marker;
    private _markerPos = getMarkerPos _marker;

    { 
        private _prefix = toLower _x;
        if (toLower _markerName find _prefix == 0) then {
            _targetActions append ([_markerPos, _markerName, objNull, true] call YOSHI_fnc_createTargetActions);
        };
    } forEach (YOSHI_SUPPORT_ARTILLERY_CONFIG_OBJECT get "ArtilleryPrefixes");
} forEach allMapMarkers;

_targetActions
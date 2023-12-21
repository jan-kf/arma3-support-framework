private _getOrderedWaypoints = {
    params ["_startPosition", "_endPosition", ["_reverse", false]];

    // Create a hashmap to store marker text and positions
    private _wpMap = createHashMap;
    
    // Iterate over all markers
    {
        private _markerText = markerText _x;
        // Check if the marker text starts with "wp" and is not empty
        if ((count _markerText > 1) && {(toLower (_markerText select [0, 2])) == "wp"}) then {
            _wpMap set [_markerText, markerPos _x];
        };
    } forEach allMapMarkers;

    // Sort the keys of the hashmap alphabetically and retrieve their corresponding positions
    private _keys = keys _wpMap;
    _keys sort !_reverse;
    private _sortedPositions = (_keys) apply {_wpMap get _x};

    // Initialize the array of waypoint positions with the start position and add sorted positions
    private _waypointPositions = [_startPosition] + _sortedPositions + [_endPosition];

    _waypointPositions
};
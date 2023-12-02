private _auditPadRegistry = {
    private _manifest = home_base getVariable "homeBaseManifest";
    private _padRegistry = _manifest get "padRegistry";
    private _registeredVics = _manifest get "vicRegistry";
    private _padsNearBase = _manifest get "padsNearBase";

    // Set all padRegistry values to "unassigned"
    {
        _padRegistry set [_x, "unassigned"];
    } forEach (keys _padRegistry);

    // Iterate through registered vehicles
    {
        private _vic = _x;
        private _vicGroup = group _vic;
        private _vicWaypoints = waypoints _vicGroup;

        // Check each waypoint of the vehicle
        {
            private _wpPos = waypointPosition _x;

            // Check if waypoint is near any of the pads
            {
                private _pad = _x;
                private _padPos = getPos _pad;
                private _padNetId = netId _pad;

                if ((_wpPos distance2D _padPos) < 10) then { // Threshold distance to consider a waypoint "on" the pad
                    _padRegistry set [_padNetId, netId _vic];
                };
            } forEach _padsNearBase;
        } forEach _vicWaypoints;
    } forEach _registeredVics;
};
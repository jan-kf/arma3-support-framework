// getNearestLocationName.sqf
private _getNearestLocal = {
    params ["_pos"];
    private _locationTypes = [
        "Airport", "Area", "BorderCrossing", "CityCenter", "CivilDefense", 
        "CulturalProperty", "DangerousForces", "Flag", "FlatArea", 
        "FlatAreaCity", "FlatAreaCitySmall", "Hill", "Name", "NameCity", 
        "NameCityCapital", "NameLocal", "NameMarine", "NameVillage", 
        "SafetyZone", "Strategic", "StrongpointArea", "ViewPoint"
    ];
    private _searchRadius = 10000;
    private _nearestLocations = nearestLocations [_pos, _locationTypes, _searchRadius];
    if (!(_nearestLocations isEqualTo [])) then {
        private _nearestLocation = _nearestLocations select 0;
        private _locationName = text _nearestLocation;
        private _locationPos = position _nearestLocation;
        private _distance = _pos distance _locationPos;
        private _direction = [_pos, _locationPos] call BIS_fnc_dirTo;
        private _directionText = switch (true) do {
            case (_direction > 337.5 || _direction <= 22.5): {"north"};
            case (_direction > 22.5 && _direction <= 67.5): {"northeast"};
            case (_direction > 67.5 && _direction <= 112.5): {"east"};
            case (_direction > 112.5 && _direction <= 157.5): {"southeast"};
            case (_direction > 157.5 && _direction <= 202.5): {"south"};
            case (_direction > 202.5 && _direction <= 247.5): {"southwest"};
            case (_direction > 247.5 && _direction <= 292.5): {"west"};
            case (_direction > 292.5 && _direction <= 337.5): {"northwest"};
        };
        // Return array of distance, direction, and location name
        [round _distance, _directionText, _locationName]
    } else {
        // Return an empty array if no relevant locations found
        []
    };
};
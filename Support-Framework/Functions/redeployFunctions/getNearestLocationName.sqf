// getNearestLocationName.sqf
private _getNearestLocationName = {
    private _locationTypes = [
        "Airport", "Area", "BorderCrossing", "CityCenter", "CivilDefense", 
        "CulturalProperty", "DangerousForces", "Flag", "FlatArea", 
        "FlatAreaCity", "FlatAreaCitySmall", "Hill", "Name", "NameCity", 
        "NameCityCapital", "NameLocal", "NameMarine", "NameVillage", 
        "SafetyZone", "Strategic", "StrongpointArea", "ViewPoint"
    ];
    private _playerPos = getPos player;
    private _searchRadius = 10000;
    private _nearestLocations = nearestLocations [_playerPos, _locationTypes, _searchRadius];
    if (!(_nearestLocations isEqualTo [])) then {
        private _nearestLocation = _nearestLocations select 0;
        private _locationName = text _nearestLocation;
        player sideChat format ["I am near %1", _locationName];
    } else {
        player sideChat "No relevant locations found near me.";
    };
};
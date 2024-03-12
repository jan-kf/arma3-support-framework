private _baseCallsign = [west, "base"];
private _baseName = "Base";

private _baseIsNotVirtual = false;

private _syncedObjects = synchronizedObjects (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG");
{
	if (_x isKindOf "Man") exitWith {
		_baseCallsign = _x;
		_baseName = groupId group _x;
		_baseIsNotVirtual = true;
	};
} forEach _syncedObjects;

[_baseCallsign, _baseName, _baseIsNotVirtual]
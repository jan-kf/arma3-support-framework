params ["_player"];

// Check if the player is controlling the Zeus camera
private _isZeusCamera = cameraOn isKindOf "ModuleCurator_F";

// Check if the player owns a Zeus module
private _isZeusModuleOwner = !isNil {getAssignedCuratorLogic _player};

// Determine if the player is Zeus
private _isZeus = _isZeusCamera || _isZeusModuleOwner;

_isZeus
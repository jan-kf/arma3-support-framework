params ["_forArtillery"];

private _targetActions = [];
// Process laser targets from players

_playersAndVehicles = allPlayers;
_playersAndVehicles append vehicles;

{
    private _playerOrVehicle = _x;
    private _laserTarget = laserTarget _playerOrVehicle;
    private _laserTargetPos = getPosASL _laserTarget;
    private _normalizedLaserTargetPos = [round (_laserTargetPos select 0), round (_laserTargetPos select 1), round (_laserTargetPos select 2)];
    if (isLaserOn _playerOrVehicle && (str(_normalizedLaserTargetPos) != str([0,0,0]))) then {
        
        private _laserTargetOwner = if (_playerOrVehicle isKindOf "Man") then {name _playerOrVehicle} else {groupID group _playerOrVehicle};
        private _laserTargetName = format ["%1's Laser", _laserTargetOwner];
        _targetActions append ([_normalizedLaserTargetPos, _laserTargetName, _laserTarget, _forArtillery] call YOSHI_fnc_createTargetActions);
    };
} forEach _playersAndVehicles;

// // TODO: Process IR laser targets from players
// {
//     private _player = _x;

//     private _unit = player;  // Replace with your unit 
//     private _eyePos = eyePos _unit; 
//     private _direction = (eyeDirection _unit) vectorMultiply 1000; 
//     private _targetPos = _eyePos vectorAdd _direction; 
    
//     private _object = lineIntersectsSurfaces [_eyePos, _targetPos, _unit]; 

//     _object

//     if (_player isIRLaserOn currentWeapon _player) then {
//         private _targetPos = eyePos _player vectorAdd (aimPos _player vectorMultiply 1000);
//         private _targetName = format ["IR target by %1", name _player];

//         _targetActions append (YOSHI_fnc_createTargetActions call [_targetPos, _targetName]);
//     };
// } forEach allPlayers;


_targetActions
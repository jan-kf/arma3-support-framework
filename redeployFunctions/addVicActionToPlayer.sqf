params ["_player", "_vehicle"];

[format ["Adding %1 to %2", _vehicle, _player]] remoteExec ["systemChat"];
diag_log "[REDEPLOY] Adding Vic to Player...";

private _vehicleName = getText (configFile >> "CfgVehicles" >> (typeOf _vehicle) >> "displayName");
_player setVariable ["show-" + netId _vehicle, true, true];
private _condition = format["('hgun_esd_01_F' in (items %2)) && ((%2 getVariable ['show-%1', false]) isEqualTo true)", netId _vehicle, _player];

private _actionID = _player addAction [
	format ["<t color='#FFFFFF'>Deploy %1</t>", _vehicleName], 
	{
		params ["_target", "_caller", "_actionID", "_args"];
		private _vic = _args select 0;
		private _player = _args select 1;
		private _vehicleName = getText (configFile >> "CfgVehicles" >> (typeOf _vic) >> "displayName");
		private _reinserting = _vic getVariable ["isReinserting", false];
		private _waveOff = _vic getVariable ["waveOff", false];
		_vic setVariable ["targetGroupLeader", _player, true];
		if (_reinserting && !_waveOff) then {
			_vic setVariable ["currentTask", "waveOff", true];
		} else {
			_vic setVariable ["currentTask", "begin", true];
		};


		_player setVariable ["show-" + netId _vic, false, true];

		sleep 10;

		if (_vic getVariable ["isReinserting", false]) then {
			_player setUserActionText [_actionId, format["<t color='#FF0000'>Wave Off %1</t>", _vehicleName]];
		} else {
			_player setUserActionText [_actionId, format["<t color='#FFFFFF'>Deploy %1</t>", _vehicleName]];
		};

		_player setVariable ["show-" + netId _vic, true, true];

	},
	[_vehicle, _player], // args
	6, // priority
	false, // showWindow
	true, // hideOnUse
	"", //shortcut
	_condition, //condition
	-1, // radius
	false, // unconscious
	"",   // selection
	""    // memoryPoint
];

private _playerActionMap = _vehicle getVariable "playerActionMap";

if (isNil "_playerActionMap") then {
	_vehicle setVariable ["playerActionMap", createHashMap, true];
};
private _playerActionMap = _vehicle getVariable "playerActionMap";

_playerActionMap set [netId _player, _actionID];

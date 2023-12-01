params ["_player", "_vehicle", "_vehicleName", "_condition"];

// ["Adding Vic to Player "] remoteExec ["systemChat"];
diag_log "[REDEPLOY] Adding Vic to Player...";

private _actionID = _player addAction [
	format ["<t color='#FFFFFF'>Deploy %1</t>", _vehicleName], 
	{
		params ["_target", "_caller", "_actionID", "_args"];
		private _vic = _args select 0;
		private _player = _args select 1;
		private _vicStatus = [_vic] call (missionNamespace getVariable "getVehicleStatus");
		private _vehicleName = getText (configFile >> "CfgVehicles" >> (typeOf _vic) >> "displayName");
		private _reinserting = _vicStatus get "isReinserting";
		private _waveOff = _vicStatus get "waveOff";
		_vicStatus set ["targetGroupLeader", _player];
		if (_reinserting && !_waveOff) then {
			_vicStatus set ["currentTask", "waveOff"];
		} else {
			_vicStatus set ["currentTask", "begin"];
		};

		_player setVariable ["show-" + netId _vic, false, true];

		sleep 10;

		if (_vicStatus get "isReinserting") then {
			_player setUserActionText [_actionId, format["<t color='#FF0000'>Wave Off %1</t>", _vehicleName]];
		} else {
			_player setUserActionText [_actionId, format["<t color='#FFFFFF'>Deploy %1</t>", _vehicleName]];
		};

		_player setVariable ["show-" + netId _vic, true, true];


		// [driver (_args select 0), format["debug stat: %1", _vicStatus]] remoteExec ["sideChat"];
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

_playerActionMap set [netId _player, _actionID];

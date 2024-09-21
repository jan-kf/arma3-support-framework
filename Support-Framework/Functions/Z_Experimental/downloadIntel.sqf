private _downloadAction = ["StartDownload", "Start Download", "",  
	{
		params ["_target", "_caller", "_actionId", "_arguments"];

		_downloadHandle = [_target] spawn {
			params ["_target"];
			_progress = 0;
			_progress_speed = 1;
			_interrupt = false;
			_downloadComplete = false;

			private _randErrors = [
				"Network Error: Packet loss detected, attempting to reestablish connection. Please try again later.",
				"Server Timeout: Connection to server was lost.",
				"Data Corruption Detected: Verifying integrity of downloaded files.",
				"Signal Interference: Connection stability compromised due to local electromagnetic interference.",
				"Download Overload: Too many concurrent connections, bandwidth limit reached.",
				"Authentication Failed: User credentials have expired.",
				"Hardware Malfunction: Router overheating, cooling down to continue. Please retry later.",
				"Unexpected Error: Protocol mismatch detected in the current session.",
				"Server Maintenance: Remote server undergoing unplanned maintenance.",
				"Power Fluctuation: Voltage drop detected, stabilizing connection.",
				"Firewall Block: Security protocols triggered, temporarily halting data transfer.",
				"Disk Full: Insufficient storage to complete download. Free up space and retry.",
				"Checksum Error: Data integrity verification failed, re-downloading corrupted segments.",
				"Local Network Congestion: High traffic detected on the network. Please retry later.",
				"Software Update Required: System firmware out of date, update pending.",
				"Signal Jamming: Hostile electronic warfare detected, attempting to bypass interference.",
				"Memory Leak: System resources exhausted, clearing cache and restarting download.",
				"Protocol Update: Download protocol outdated, updating to the latest version.",
				"Environmental Disruption: Severe weather affecting satellite communications.",
				"Cable Disconnect: Physical connection lost, checking hardware status."
			];

			_target setVariable ["isDownloading", true, true];

			while { _progress < 100 && !_downloadComplete } do {
				_playersNear = (allPlayers select { (_x distance _target) < 10 });
				_enemiesNear = (allUnits select { (side _x == east) && (_x distance _target) < 30 });

				_shouldKick = _target getVariable ["shouldKick", false];

				_interrupt = false;
				if (_shouldKick) then {
					_interrupt = true;
				};
				if ((count _enemiesNear) > 0) then {
					_interrupt = true;
					_target setVariable ["shouldKick", true, true];
					systemChat "Download Interrupted! Clear any nearby hostiles!";
				}; 
				if ((count _playersNear) == 0) then {
					_interrupt = true;
					_target setVariable ["shouldKick", true, true];
					systemChat "Download Interrupted! Get closer to the terminal!";
				};

				if (!_interrupt) then {
					_progress = _progress + _progress_speed;
					_message = format ["Download Progress: %1/100", _progress];

					systemChat _message;

					if (_progress >= 100) then {
						_downloadComplete = true;
						
						systemChat "Download Complete!";
						_target setVariable ["isDownloading", false, true];
					};
					if ((random 100 < 20)) then {
						_interrupt = true;
						_lastKick = time;
						_target setVariable ["shouldKick", true, true];
						private _error = _randErrors select (floor (random (count _randErrors)));
						systemChat _error;
					};
				} else {
					systemChat "Waiting user input to continue...";
				};

				sleep 5;
			};
		};
	},
	{ 
		params ["_target", "_caller", "_params"];
		_shouldAllowDownload = !(_target getVariable ["isDownloading", false]);
		_shouldAllowDownload
	}
] call ace_interact_menu_fnc_createAction;

private _kickAction = ["KickDownload", "Kick it", "",  
	{
		params ["_target", "_caller", "_actionId", "_arguments"];

		_target setVariable ["shouldKick", false, true];
		systemChat "User override accepted, proceeding...";
	},
	{ 
		params ["_target", "_caller", "_params"];
		_shouldKick = _target getVariable ["shouldKick", false];
		_shouldKick
	}
] call ace_interact_menu_fnc_createAction;

[this, 0, ["ACE_MainActions"], _downloadAction] call ace_interact_menu_fnc_addActionToObject;
[this, 0, ["ACE_MainActions"], _kickAction] call ace_interact_menu_fnc_addActionToObject;
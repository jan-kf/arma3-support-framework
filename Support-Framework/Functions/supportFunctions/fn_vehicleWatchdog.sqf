if (!isServer) exitWith {};

private _homeBase = missionNamespace getVariable ["YOSHI_HOME_BASE_CONFIG", nil];

if (isNil "_homeBase") exitWith {diag_log "[SUPPORT] YOSHI_HOME_BASE_CONFIG is not set, terminating process";};

private _vic = _this select 0;

// [format ["Starting watchdog for %1 ... ", _vic]] remoteExec ["systemChat"];
diag_log format ["Starting watchdog for %1 ... ", _vic];

private _watchdog = _vic getVariable "watchdog";
if (!isNil "_watchdog") exitWith {
	// [format ["watchdog exists for %1, skipping | %2", _vic, _watchdog]] remoteExec ["systemChat"];
	diag_log format ["watchdog exists for %1, skipping", _vic];
};

private _vehicleClass = typeOf _vic;
private _vehicleDisplayName = getText (configFile >> "CfgVehicles" >> _vehicleClass >> "displayName");
	

private _dustOffMessage = nil;
private _touchdownMessage = nil;

if (_vic getVariable ["isHeli", false]) then {
	_dustOffMessage = "Heading to LZ at: %1";
	_touchdownMessage = "Touchdown, Please disembark now";
} else {
	_dustOffMessage = "Heading to RP at: %1";
	_touchdownMessage = "We're here, Please disembark now";
};

private _isCAS = _vic getVariable ["isCAS", false];
private _isRecon = _vic getVariable ["isRecon", false];

private _helloMsg = "%1 On Station...";

if (_isCAS) then {
	_helloMsg = "Close Air Support, %1 On Station...";
};

if (_isRecon) then {
	_helloMsg = "Recon asset, %1 On Station...";
};

[driver _vic, format[_helloMsg, groupId group _vic]] call SupportFramework_fnc_sideChatter;

while {_vic getVariable ["isRegistered", false] && alive _vic} do {
	// run while the vic is registered

	/*
	should perform a heartbeat check: 
		- check it's current location

		- check what it's supposed to be doing
			- waiting
			- onMission
				- is it making it's way to the redeploy point?
			- RTB
				- is it making it's way back to base?
		
		- is it where it's meant to be?
			- if not it should remedy it 
	*/

	private _task = _vic getVariable ["currentTask", "waiting"];

	// [format["%1 watchdog loop: %2 | %3", _vehicleDisplayName, _task, time]] remoteExec ["systemChat"];

	// [driver _vic, format["%1 -> current task: %2", _vehicleDisplayName, _task]] call SupportFramework_fnc_sideChatter;
	diag_log format["[SUPPORT] %1 watchdog loop: %2 | %3", _vehicleDisplayName, _task, time];


	switch (_task) do
	{
		case "resistered": {
			/*
			vic was just registered, should probably check that it's at base
			if it's not at base, should probably have it go back to base to sort itself out
			once ready, set task to waiting
			*/ 

			_vic setVariable ["currentTask", "waiting", true];
		};
		// case "requestReinsert": { // called directly
		// 	// vic was told to begin it's mission, perform startup

		// 	[_vic] call SupportFramework_fnc_requestReinsert;
		// };
		// case "requestCas": {
		// 	// vic was told to begin it's cas mission, perform startup
			
		// 	[_vic] call SupportFramework_fnc_requestCas;
		// };
		case "onMission": {
			// vic is currently making its way to the redeploy LZ
			
			[_vic] call SupportFramework_fnc_onMission;
		};
		case "RTB": {
			
			[_vic] call SupportFramework_fnc_RTB;
		};
		case "performingCAS": {

			[_vic] call SupportFramework_fnc_performingCAS;
		};
		case "performingRecon": {

			[_vic] call SupportFramework_fnc_performingRecon;
		};
		case "landingAtObjective": {
			[_vic, _touchdownMessage] call SupportFramework_fnc_landingAtObjective;
		};
		case "requestBaseLZ": {
			
			[_vic] call SupportFramework_fnc_requestBaseLZ;
		};
		// case "waveOff": {

		// 	[_vic] call SupportFramework_fnc_waveOff;
		// };
		case "landingAtBase": {

			[_vic] call SupportFramework_fnc_landingAtBase;
		};
		case "loiter": {

			[_vic] call SupportFramework_fnc_loiter;
		};
		case "awaitOrders": {
			// vic was called in to land, awaiting explicit orders to RTB
			// no code, leader will set the current task manually
		};
		case "marooned": {
			// vic was denied a landing pad at home base
			sleep 10;
			
			_vic setVariable ["currentTask", "requestBaseLZ", true];
		};
		default {
			//vic is waiting for a task, wait
		};

	};

	
	sleep 3;
};
private _isAlive = alive _vic;

if (_isAlive) then {
	[driver _vic, format["%1 Off Station...", groupId group _vic]] call SupportFramework_fnc_sideChatter;
} else {
	private _array = [
		"And so, this is where my story ends, but yours... yours is just beginning.",
		"Tell them I stood my ground until the very end.",
		"Tell them I stood my ground until the very end.",
		"Promise me you'll never forget the lessons we learned together.",
		"In the end, it's not the years in your life that count, but the life in your years.",
		"I finally see the light on the other side. It's beautiful...",
		"Keep moving forward, never look back, and always remember me.",
		"I have no regrets, for I lived my life as a tale worth telling.",
		"This is not goodbye, my friend, but a promise to meet again in another life.",
		"I leave my dreams to you; carry them forward.",
		"As the curtain falls on my final act, I take my bow, forever your faithful player.",
		"Free at last...",
		"Tell them to make it count.",
		"I'll see you again in the halls of Vallhalla",
		"Don't cry for me. For when the choirs of angels sing, will I not be among them?"
	];
	private _goodbye = _array select (floor (random (count _array)));
	[driver _vic, _goodbye] call SupportFramework_fnc_sideChatter;
	sleep 3;
	private _array2 = [
		"And with that, %1's journey reached its end, a final breath marking the close of an unforgettable saga.",
		"With one last sigh, %1 departed from this world, their legacy etched in the stars.",
		"And so, with a final whisper, %1's spirit ascended, leaving their mark on the fabric of time.",
		"In that quiet moment, %1 took their last breath, their story forever woven into the tapestry of life.",
		"As %1's breath faded away, so did a chapter of history, their life a story told across the ages.",
		"With a gentle exhale, %1's presence slipped into memory, their impact everlasting.",
		"And there, under the watchful eyes of destiny, %1 breathed their last, their life a mosaic of triumph and trial.",
		"In the hush that followed, %1's final breath echoed the end of an era, their essence forever a part of the world.",
		"With that last breath, %1 released their grip on the mortal realm, their spirit joining the dance of the cosmos.",
		"And with that, %1's flame was extinguished, leaving behind a trail of light for all who follow."
	];
	private _farewell = _array2 select (floor (random (count _array2)));

	private _shutIt = (missionNamespace getVariable "YOSHI_HOME_BASE_CONFIG") getVariable ["SideHush", false];
	if (!_shutIt) then {
		[format[_farewell, groupId group _vic, 'systemChat']] remoteExec ['systemChat'];
	}
};

params ["_uav"];

private _ReconConfigured = !(isNil "YOSHI_SUPPORT_RECON_CONFIG");
private _timeLimit = 300;
if (_ReconConfigured) then {
	_timeLimit = YOSHI_SUPPORT_RECON_CONFIG getVariable ["TaskTime", 300];
};

private _markerUpdateInterval = YOSHI_SUPPORT_RECON_CONFIG getVariable ["Interval", 5]; 

private _showNames = YOSHI_SUPPORT_RECON_CONFIG getVariable ["ShowNames", true]; 
private _hasHyperSpectralSensors = YOSHI_SUPPORT_RECON_CONFIG getVariable ["HasHyperSpectralSensors", false]; 

_uav setVariable ["taskStartTime", serverTime, true];

private _start = _uav getVariable "taskStartTime";
private _elapsedTime = serverTime - _start;

while {(alive _uav) && (_elapsedTime < _timeLimit)} do {
	[_uav, YOSHI_reconDetectionRange, _showNames, _hasHyperSpectralSensors] call YOSHI_PerformReconScan;

	sleep _markerUpdateInterval;

	_elapsedTime = serverTime - _start;
};

{
	deleteMarker (_x select 0); // TODO: don't delete, update instead
} forEach YOSHI_ReconMarkersArray;

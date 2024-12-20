params ["_uav"];

private _ReconConfigured = YOSHI_SUPPORT_RECON_CONFIG_OBJECT call ["isInitialized"];
private _timeLimit = 300;
if (_ReconConfigured) then {
	_timeLimit = YOSHI_SUPPORT_RECON_CONFIG_OBJECT call ["TaskTime"];
};

private _markerUpdateInterval = YOSHI_SUPPORT_RECON_CONFIG_OBJECT call ["Interval"]; 

private _showNames = YOSHI_SUPPORT_RECON_CONFIG_OBJECT call ["ShowNames"]; 
private _hasHyperSpectralSensors = YOSHI_SUPPORT_RECON_CONFIG_OBJECT call ["HasHyperSpectralSensors"]; 

_uav setVariable ["taskStartTime", serverTime, true];

private _start = _uav getVariable "taskStartTime";
private _elapsedTime = serverTime - _start;

while {(alive _uav) && (_elapsedTime < _timeLimit)} do {
	[_uav, YOSHI_reconDetectionRange, _showNames, _hasHyperSpectralSensors] call YOSHI_PerformReconScan;

	sleep _markerUpdateInterval;

	_elapsedTime = serverTime - _start;
};

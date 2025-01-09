params ["_uav"];

private _ReconConfigured = [YOSHI_SUPPORT_RECON_CONFIG_OBJECT] call YOSHI_isInitialized;
private _timeLimit = 300;
if (_ReconConfigured) then {
	_timeLimit = YOSHI_SUPPORT_RECON_CONFIG_OBJECT get "TaskTime";
};

private _markerUpdateInterval = YOSHI_SUPPORT_RECON_CONFIG_OBJECT get "Interval"; 

private _showNames = YOSHI_SUPPORT_RECON_CONFIG_OBJECT get "ShowNames"; 
private _hasHyperSpectralSensors = YOSHI_SUPPORT_RECON_CONFIG_OBJECT get "HasHyperSpectralSensors"; 

_uav setVariable ["taskStartTime", serverTime, true];

private _start = _uav getVariable "taskStartTime";
private _elapsedTime = serverTime - _start;

while {(alive _uav) && (_elapsedTime < _timeLimit)} do {
	[_uav, YOSHI_reconDetectionRange, _showNames, _hasHyperSpectralSensors] call YOSHI_PerformReconScan;

	sleep _markerUpdateInterval;

	_elapsedTime = serverTime - _start;
};

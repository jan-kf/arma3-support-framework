YOSHI_playVehicleSoundLocal = {
    params ["_soundName", "_source"];

    private _soundSource = _source say3D [_soundName, 1000, 1];
	_source setVariable ["YOSHI_soundSource", _soundSource];

};

YOSHI_stopVehicleSoundLocal = {
    params ["_source"];

    private _soundSource = _source getVariable ["YOSHI_soundSource", objNull];
    deleteVehicle _soundSource;

};

YOSHI_playVehicleSoundGlobal = {
    params ["_soundName", "_source"];

    [[_soundName, _source], YOSHI_playVehicleSoundLocal] remoteExec ["call", 0];

};

YOSHI_stopVehicleSoundGlobal = {
    params ["_source"];

    [[_source], YOSHI_stopVehicleSoundLocal] remoteExec ["call", 0];

};
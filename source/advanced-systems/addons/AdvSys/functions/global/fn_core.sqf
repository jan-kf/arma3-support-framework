/*
The fear of the Lord is the beginning of wisdom,
and knowledge of the Holy One is understanding.
(Proverbs 9:10)
*/

YAS_addMarker = {
	params ["_obj", ["_text", ""], ["_color", "ColorRed"], ["_type", "mil_dot"], ["_shape", "ICON"], ["_size", [1,1]]];

	private _markerName = format ["_USER_DEFINED YOSHI_MARKER_%1_%2_%3", str(_obj), serverTime, random 1000];
	private _marker = createMarker [_markerName, _obj]; 
	_marker setMarkerShape _shape; 
	_marker setMarkerType _type;  
	_marker setMarkerColor _color;
	_marker setMarkerText _text;
	_marker setMarkerShadow false;
	_marker setMarkerSize _size;

	_marker
};

YOSHI_getFrontPosition = {
    params ["_projectile", "_distanceAhead"];

    private _currentPos = getPosATL _projectile; 
    private _velocity = velocity _projectile;
    private _directionNormalized = vectorNormalized _velocity; 

    private _frontPos = _currentPos vectorAdd (_directionNormalized vectorMultiply _distanceAhead);

    _frontPos
};

YOSHI_getPosTop = {  
	params ["_obj"];  
	
	private _loc = getPosASL _obj;  
	
	private _locAbove = _loc vectorAdd [0,0,10];  
	
	private _hits = lineIntersectsSurfaces [_locAbove, _loc, objNull, objNull, true, 10, "FIRE", "GEOM"];  
	if ((count _hits) > 0) then {  
	_hit = _hits select 0;  
	_dist = (_hit select 0) select 2;  
	_loc = (_hit select 0);  
	};  
	_loc  
};


YOSHI_beamA2B = {
	params ["_posA", "_posB", ["_color", [1, 0, 0, 1]], ["_thickness", 20]];
    
	drawLine3D [_posA, _posB, _color, _thickness];
};

YOSHI_localBeamA2B = {
    // only to be called locally
	params ["_duration"];

    onEachFrame {
	    drawLine3D [YOSHI_BEAM_POS_A, YOSHI_BEAM_POS_B, YOSHI_BEAM_COLOR, YOSHI_BEAM_THICKNESS];
    };

    sleep _duration;

    onEachFrame {};
};

YOSHI_globalBeamA2B = {
	params ["_posA", "_posB", ["_color", [1, 0, 0, 1]], ["_thickness", 10], ["_duration", 1]];
    
    YOSHI_BEAM_POS_A = _posA;
    YOSHI_BEAM_POS_B = _posB;
    YOSHI_BEAM_COLOR = _color;
    YOSHI_BEAM_THICKNESS = _thickness;

    publicVariable "YOSHI_BEAM_POS_A";
    publicVariable "YOSHI_BEAM_POS_B";
    publicVariable "YOSHI_BEAM_COLOR";
    publicVariable "YOSHI_BEAM_THICKNESS";

    [[_duration], YOSHI_localBeamA2B] remoteExec ["spawn", 0];

};

YOSHI_serverBeamVic2Pos = {
    // only to be called on the server, should prevent repeated drawing of the beam
	params ["_vic", "_pos", ["_pulseCount", 5], ["_pulseDurationOn", 0.1], ["_pulseDurationOff", 0.05], ["_color", [1, 0, 0, 1]], ["_thickness", 20]];

    private _isDrawing = missionNamespace getVariable ["YOSHI_DRAW_DEBOUNCE", false];

    if (_isDrawing) exitWith {};

    missionNamespace setVariable ["YOSHI_DRAW_DEBOUNCE", true];

	private _count = _pulseCount;

    while {(alive _vic) && (_count > 0)} do {
        private _topOfVic = ASLToATL ([_vic] call YOSHI_getPosTop); 
        
        [_topOfVic, _pos, _color, _thickness, _pulseDurationOn] call YOSHI_globalBeamA2B;
        
        sleep (_pulseDurationOn + _pulseDurationOff);
        _count = _count - 1;
    };

    missionNamespace setVariable ["YOSHI_DRAW_DEBOUNCE", false];

};

YOSHI_serverSay3dOnce = {
    params ["_obj", "_soundName", "_distance", "_duration"];

    private _beganPlaying = missionNamespace getVariable ["YOSHI_SAY3D_ONCE_PLAYING", false];
    if (_beganPlaying) exitWith {};

    missionNamespace setVariable ["YOSHI_SAY3D_ONCE_PLAYING", true];
    [_obj, [_soundName, _distance, 1]] remoteExec ["say3D", 0];

    sleep _duration;

    missionNamespace setVariable ["YOSHI_SAY3D_ONCE_PLAYING", false];

};


YOSHI_beamVic2Pos = {
	params ["_vic", "_pos", ["_pulseCount", 5], ["_color", [1, 0, 0, 1]], ["_thickness", 20]];

	private _count = _pulseCount;

	// prevent drawing more than once per instance of APS trigger
	private _shouldDraw = player getVariable ["YOSHI_DRAW_DEBOUNCE", true];

	if (_shouldDraw) then {
		player setVariable ["YOSHI_DRAW_DEBOUNCE", false];

		while {(alive _vic) && (_count > 0)} do {
			private _topOfVic = ASLToATL ([_vic] call YOSHI_getPosTop); 
			[_topOfVic, _pos, _color, _thickness] call YOSHI_beamA2B;
			sleep 0.05;
			_count = _count - 1;
		};

		player setVariable ["YOSHI_DRAW_DEBOUNCE", true];
	};
};


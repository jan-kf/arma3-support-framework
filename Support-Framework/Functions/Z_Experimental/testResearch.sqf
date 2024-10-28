
params ["_container"];

private _getDir = {
	private _object=_this select 0;
	private _vehicle=_this select 1;
	private _dir=0;
	_dir=(getDir _object)-(getDir _vehicle);
	_dir
};

private _setTilt = {
	private _object=_this select 0;
	private _roll=_this select 1;
	if!(local _object)exitWith{};
	private _yaw=0;
	private _pitch=0;
	_object setVectorDirAndUp[
		[sin _yaw * cos _pitch,cos _yaw * cos _pitch,sin _pitch],
		[[sin _roll,-sin _pitch,cos _roll * cos _pitch],-_yaw]call BIS_fnc_rotateVector2D
	];
	_roll
};

private _setDirRemote = {
	private _object=_this select 0;
	private _dir=_this select 1;
	if!(local _object)exitWith{};
	private _tilt=0;
	if((count _this)>2)then{_tilt=_this select 2};
	_object setDir _dir;
	if(_tilt==0)exitWith{};
	[_object,_tilt]remoteExecCall["_setTilt"];
};

private _setDir = {
	private _object=_this select 0;
	private _dir=_this select 1;
	private _tilt=0;
	if((count _this)>2)then{_tilt=_this select 2};
	[_object,_dir,_tilt]remoteExec["_setDirRemote"];
};

private _surfacePos = {
	private _object=_this;
	private _object2=objNull;
	private _pos=getPosASL _object;
	private _height=.5;
	private _terrain=FALSE;
	if(_object isKindOf"StaticWeapon")then{_height=2};
	_pos=[_pos select 0,_pos select 1,(_pos select 2)+_height];
	private _pos2=[_pos select 0,_pos select 1,(_pos select 2)-10];
	private _out=lineIntersectsSurfaces[_pos,_pos2,_object,player,TRUE,1,"VIEW","GEOM",TRUE];
	_pos2=(_out select 0)select 0;
	_pos2=[_pos2 select 0,_pos2 select 1,(_pos2 select 2)];
	_object2=(_out select 0)select 2;
	if(isNull((_out select 0)select 2))then{_terrain=TRUE};
	if(_object2==player)then{_object2=objNull};
	if(isNull _object2)then{_object2=_object};
	[_pos2,_object2,_terrain]
};

while {true} do {

	private _objectsNearby = nearestObjects [_container, [], 10];
	private _boundingBox = boundingBoxReal _container;
	private _size = [((_boundingBox select 1) select 0), ((_boundingBox select 1) select 1), ((_boundingBox select 1) select 2)]; 
	private _center = getPosASL _container; 
	private _dir = direction _container;
	


	private _objectsToAttach = _objectsNearby select {
		!(_x isKindOf "Man") && 
		( getMass _x < 18000) && 
		( getMass _x > 0) && 
		(_x != _container) && 
		((getPosATL _x) inArea [_center, _size select 0, _size select 1, _dir, true])
	};


	{
		private _isCar = _x isKindOf "Car";
		if (!(_x in (attachedObjects _container)) && (isNull attachedTo _x) && (!_isCar || (_isCar && !(isEngineOn _x)))) then {

			private _objectToAttach = _x; 
			private _targetObject = _container; 

			private _tilt=(_objectToAttach call BIS_fnc_getPitchBank)select 1;

			private _dir=[_objectToAttach, _targetObject] call _getDir;

			private _out=_objectToAttach call _surfacePos;

			_pos=_out select 0;

			_objectToAttach setPosASL _pos;
			[_objectToAttach,_targetObject]remoteExecCall["disableCollisionWith"];
			_objectToAttach attachTo[_targetObject];
			[_objectToAttach,_dir,_tilt] call _setDir;
		
		};
		if (_isCar && (isEngineOn _x)) then {
			detach _x;
		}
	} forEach _objectsToAttach;

	{
		if (!(_x in _objectsToAttach)) then {
			detach _x;
		}
	} forEach (attachedObjects _container);

	hint format["%1 | %2", time, (attachedObjects _container)];
	sleep 1; 
};

	


private _vectorDir = vectorDir _x;
private _vectorUp = vectorUp _x;
_x attachTo [_container]; 
sleep 0.5;
_x setVectorDirAndUp [_vectorDir, _vectorUp];
hint format["%1 | %2 | %3 | %4 | %5", time, (attachedObjects _container), _vectorDir, _vectorUp, _objectsToAttach];


// _container = _this;
// private _boundingBox = boundingBoxReal _container; 

// private _size = [((_boundingBox select 1) select 0), ((_boundingBox select 1) select 1)]; 
// private _center = getPosASL _container; 
// private _dir = direction _container;

// hint str([_size, _dir]);


// private _objectsNearby = nearestObjects [_this, [], 10];
// private _array = [];
// {_array pushBack [_x, ]} forEach _objectsNearby;
// hint str(_array);


private _vehicle = _this;
private _interval = 0.01; 
 
private _detectRockets = { 
    params ["_vehicle", "_interval", ["_charges", 50]]; 
	_boundingBox = boundingBoxReal _vehicle;
	_radius = (_boundingBox select 0) distance2D (_boundingBox select 1);

	_chargesRemaining = _charges;
    
	while {(alive _vehicle) && (_chargesRemaining > 0)} do { 
        private _projectiles = nearestObjects [_vehicle, ["MissileBase", "RocketBase"], _radius]; 
        { 
			private _pos = getPosATL _x;
			private _vicPos = getPosATL _vehicle;

			private _vectorDir = _vicPos vectorFromTo _pos; 
			private _vectorUp = vectorUp _x;

			deleteVehicle _x;
			_grenade = createVehicle ["Land_Orange_01_F", _pos, [], 0, "CAN_COLLIDE"];
			_grenade setVectorDirAndUp [_vectorDir, _vectorUp];
			_grenade setDamage 1;
			_chargesRemaining = _chargesRemaining - 1;
			[format ["%1 Charges Remaining | %2m Protection", _chargesRemaining, _radius]] remoteExec ["hint"];
			sleep 0.1;

        } forEach _projectiles; 
        sleep _interval; 
    }; 
}; 
 
beans = [_vehicle, _interval] spawn _detectRockets; 


private _vehicle = _this;
private _interval = 0.01; 
 
private _detectRockets = { 
    params ["_vehicle", "_interval", ["_charges", 50]]; 
	_boundingBox = boundingBoxReal _vehicle;
	_radius = (_boundingBox select 0) distance2D (_boundingBox select 1);

	_chargesRemaining = _charges;
    
	while {(alive _vehicle) && (_chargesRemaining > 0)} do { 
        private _projectiles = nearestObjects [_vehicle, ["MissileBase", "RocketBase"], _radius]; 
        { 
			private _pos = getPosATL _x;

			_grenade = createVehicle ["Land_Orange_01_F", _pos, [], 0, "CAN_COLLIDE"];

			_chargesRemaining = _chargesRemaining - 1;
			
			sleep 0.1;

        } forEach _projectiles; 
        sleep _interval; 
    }; 
}; 
 
beans = [_vehicle, _interval] spawn _detectRockets; 

/////////////

YOSHI_getPosTop = {  
	params ["_obj"];  
	
	_loc = getPosASL _obj;  
	
	_locAbove = _loc vectorAdd [0,0,10];  
	
	_hits = lineIntersectsSurfaces [_locAbove, _loc, objNull, objNull, true, 10, "FIRE", "GEOM"];  
	if ((count _hits) > 0) then {  
	_hit = _hits select 0;  
	_dist = (_hit select 0) select 2;  
	_loc = (_hit select 0);  
	};  
	_loc  
};

YOSHI_beamA2B = {
	params ["_posA", "_posB"];
    
	private _fromPos = _posA;
	private _toPos = _posB;    

	private _vecDistance = (_fromPos vectorDiff _toPos ) vectorMultiply 0.5; 
	private _distance = _fromPos vectorDistance _toPos;
		
	private _vectorDir = _fromPos vectorFromTo _toPos;      
	_velocity = (_fromPos vectorDiff _toPos) vectorMultiply 20;    
	
	_e_static = "#particlesource" createVehicleLocal _toPos;      
			
	_e_static setParticleParams [["\A3\data_f\laserBeam", 1, 1, 1], "", "SpaceObject", 1, 0.05, _vecDistance, [0,0,0], 0, 1.1475, 0.9,0, [_distance], [[255, 0, 0, 1], [255, 0, 0, 1]], [1], 0, 0, "", "", "no_object",0,false, -1, [[0,30,30,0]], _vectorDir];      
	_e_static setDropInterval 0.06;     
	sleep 0.06;     
	deleteVehicle _e_static;
};

YOSHI_beamVic2Pos = {
	params ["_vic", "_pos"];


	_count = 3;

	while {(alive _vic) && (_count > 0)} do {
		_topOfVic = ASLToATL ([_vic] call YOSHI_getPosTop); 
		[_topOfVic, _pos] call YOSHI_beamA2B;
		sleep 0.05;
		_count = _count - 1;
	};

};


YOSHI_detectRockets = { 
    params ["_vehicle", ["_charges", 40], ["_range", -1], ["_interval", 0], ["_cooldown", 0.1]];
	if (isServer) exitWith {};
	if (_range == -1) then{
		_boundingBox = boundingBoxReal _vehicle;
		_range = ((_boundingBox select 0) distance (_boundingBox select 1)) * 2;
	};
	hint str(_range);

	_vehicle setVariable ["APS_Charges", _charges, true];
    
	while {(alive _vehicle) && ((_vehicle getVariable ["APS_Charges", 0]) > 0)} do { 
        private _projectiles = nearestObjects [_vehicle, ["MissileBase", "RocketBase"], _range]; 
        { 
			private _pos = getPosATL _x;

			deleteVehicle _x;			
 
			[[_vehicle, _pos], YOSHI_beamVic2Pos] remoteExec ["spawn"];


			_orange = createVehicle ["ModuleAPERSMineDispenser_Mine_F", _pos, [], 0, "CAN_COLLIDE"];
			_orange setDamage 1;
			
			_chargesRemaining = _vehicle getVariable ["APS_Charges", 0];
			_vehicle setVariable ["APS_Charges", _chargesRemaining - 1, true];

			hint format["detected: %1 | charges left: %2", _x, _vehicle getVariable ["APS_Charges", 0]];
			sleep _cooldown;
			
        } forEach _projectiles; 
        sleep _interval; 
    }; 
};

beans = [_this] spawn YOSHI_detectRockets;

///////////////////


private _detectRockets = { 
    params ["_vehicle", ["_charges", 40], ["_range", -1], ["_interval", 0.05], ["_cooldown", 0.1]];

	if (_range == -1) then{
		_boundingBox = boundingBoxReal _vehicle;
		_range = ((_boundingBox select 0) distance (_boundingBox select 1));
	};


	_chargesRemaining = _charges;
    
	while {(alive _vehicle) && (_chargesRemaining > 0)} do { 
		_frameNumber = diag_tickTime;
        private _projectiles = nearestObjects [_vehicle, ["MissileBase", "RocketBase"], _range]; 
        { 
			private _pos = getPosATL _x;
			_pre = "Client Distance: ";
			deleteVehicle _x;
			if (isServer) then {
				_grenade = createVehicle ["Sign_Arrow_F", _pos, [], 0, "CAN_COLLIDE"];
				_pre = "Server Distance: ";
			} else {
				_grenade = createVehicle ["Sign_Arrow_Blue_F", _pos, [], 0, "CAN_COLLIDE"];
			};
			private _vicPos = getPosATL _vehicle;

			private _vectorDir = _vicPos vectorFromTo _pos; 
			private _vectorUp = vectorUp _x;
			_grenade setVectorDirAndUp [_vectorDir, _vectorUp];

			
			_dist = _pos distance _vicPos;

			_sDist1 = _pos distance mySpeaker;
			_sDist2 = _vicPos distance mySpeaker;

			_sign = "+";
			if (_sDist1 > _sDist2) then{
				_sign = "-";
			};

			
			[mySpeaker, format["%1%2%3 | %4", _pre, _sign, _dist, diag_tickTime-_frameNumber]] remoteExec ["sideChat"];
			
			_chargesRemaining = _chargesRemaining - 1;
			sleep _cooldown;

        } forEach _projectiles; 
        sleep _interval; 
    }; 
};

beans = [_this, 40, 15] spawn _detectRockets;


_lightningEffect = {
    params ["_pos1", "_pos2"];

	_lamp = cone1;

	_midPoint = [_pos1, _pos2] call BIS_fnc_vectorLinearConversion;
	_direction = _pos2 vectorDiff _pos1;
	_distance = vectorMagnitude _direction;
	_directionNormalized = vectorNormalized _direction;

	_sparky_sun = ["spark1","spark3","spark11","spark2","spark22","spark5","spark4"] call BIS_fnc_selectRandom;
	_spark_type = ["white","orange"] call BIS_fnc_selectRandom;

	_drop = 0.001+(random 0.05);
	_midPoint = getPosATL cone1;
	_scantei_spark = "#particlesource" createVehicle _midPoint;

	if (_spark_type=="orange") then {
		_scantei_spark setParticleCircle [0, [0, 0, 0]];
		_scantei_spark setParticleRandom [1, [0.1, 0.1, 0.1], [_directionNormalized select 0, _directionNormalized select 1, 0], 0, 0.25, [0, 0, 0, 0], 0, 0];
		_scantei_spark setParticleParams [["\A3\data_f\proxies\muzzle_flash\muzzle_flash_silencer.p3d", 1, 0, 1], "", "Billboard", 1, 1, [0, 0, 0], _directionNormalized, 0, 15, 7.9, 0, [0.5,0.5,0.05], [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 0]], [0.08], 1, 0, "", "", _lamp,0,true,0.3,[[0,0,0,0]]];
		_scantei_spark setDropInterval _drop;


	} else {
		_scantei_spark setParticleCircle [0, [0, 0, 0]];
		_scantei_spark setParticleRandom [1, [0.05, 0.05, 0.1], [5, 5, 3], 0, 0.0025, [0, 0, 0, 0], 0, 0];
		_scantei_spark setParticleParams [["\A3\data_f\proxies\muzzle_flash\muzzle_flash_silencer.p3d", 1, 0, 1], "", "Billboard", 1, 1, [0, 0, 0], _directionNormalized, 0, 20, 7.9, 0, [0.5,0.5,0.05], [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 0]], [0.08], 1, 0, "", "", cone1,0,true,0.3,[[0,0,0,0]]];
		_scantei_spark setDropInterval 0.001;

	};

};


_startPos = getPosATL cone1;
_endPos = getPosATL cone2;

[_startPos, _endPos] call _lightningEffect;

////////////////////
[] spawn {_obj_emp	= cone;
_viz_eff	= true;
_player_viz	= true;

enableCamShake true;
addCamShake [1,50,27];

if (_viz_eff) then 
{
	_ripple = "#particlesource" createVehicleLocal getposatl _obj_emp;
	_ripple setParticleCircle [0,[0,0,0]];
	_ripple setParticleRandom [0,[0.25,0.25,0],[0.175,0.175,0],0,0.25,[0,0,0,0.1],0,0];
	_ripple setParticleParams [["\A3\data_f\ParticleEffects\Universal\Refract.p3d",1,0,1], "", "Billboard", 1, 0.5, [0, 0, 0], [0, 0, 0],0,10,7.9,0, [30,1000], [[1, 1, 1, 1], [1, 1, 1, 1]], [0.08], 1, 0, "", "", _obj_emp];
	_ripple setDropInterval 0.1;
	[_ripple] spawn {_de_sters = _this select 0;sleep 1;deleteVehicle _de_sters};

	_blast = "#particlesource" createVehicleLocal getposatl _obj_emp;
	_blast setParticleCircle [0, [0, 0, 0]];
	_blast setParticleRandom [0, [0, 0, 0], [0, 0, 0], 0, 0, [0, 0, 0, 0], 0, 0];
	_blast setParticleParams [["\A3\data_f\koule", 1, 0, 1], "", "SpaceObject", 1,1,[0,0,0],[0,0,1],3,10,7.9,0,[50,1000],[[1, 1, 1, 0.1], [1, 1, 1, 0]], [1], 1, 0, "", "", _obj_emp];
	_blast setDropInterval 50;
	[_blast] spawn {_de_sters = _this select 0;sleep 1;deleteVehicle _de_sters};

	_light_emp = "#lightpoint" createVehiclelocal getposatl _obj_emp; 
	_light_emp lightAttachObject [_obj_emp, [0,0,3]];
	_light_emp setLightAmbient [1,1,1];  
	_light_emp setLightColor [1,1,1];
	_light_emp setLightBrightness 0;
	_light_emp setLightDayLight true;
	_light_emp setLightAttenuation [10,10,50,0,50,2000];
	_range_lit=0;
	_brit =0;
	while {_brit < 50} do 
	{
		_light_emp setLightBrightness _brit;
		_brit = _brit+2;
		sleep 0.01;
	};
	deleteVehicle _light_emp;
};

};

//////////////////////

[] spawn {if (!hasInterface) exitWith {};

_lamp = cone;
_paz_emit = 1;

_bbr = boundingBoxReal vehicle _lamp;
_p1 = _bbr select 0;
_p2 = _bbr select 1;
_maxHeight = abs ((_p2 select 2) - (_p1 select 2));

_spark_poz_rel = (_maxHeight/2)-0.45;

_sparky_sun = ["spark1","spark3","spark11","spark2","spark22","spark5","spark4"] call BIS_fnc_selectRandom;
_spark_type = ["white","orange"] call BIS_fnc_selectRandom;

_drop = 0.001+(random 0.05);
_scantei_spark = "#particlesource" createVehicleLocal (getPosATL _lamp);

if (_spark_type=="orange") then 
{
	_scantei_spark setParticleCircle [0, [0, 0, 0]];
	_scantei_spark setParticleRandom [1, [0.1, 0.1, 0.1], [0, 0, 0], 0, 0.25, [0, 0, 0, 0], 0, 0];
	_scantei_spark setParticleParams [["\A3\data_f\proxies\muzzle_flash\muzzle_flash_silencer.p3d", 1, 0, 1], "", "SpaceObject", 1, 1, [0, 0,_spark_poz_rel], [0, 0, 0], 0, 15, 7.9, 0, [0.5,0.5,0.05], [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 0]], [0.08], 1, 0, "", "", _lamp,0,true,0.3,[[0,0,0,0]]];
	_scantei_spark setDropInterval _drop;

	_lamp say3D [_sparky_sun, 350];
	sleep _paz_emit;
	deleteVehicle _scantei_spark;
} else
{
	_scantei_spark setParticleCircle [0, [0, 0, 0]];
	_scantei_spark setParticleRandom [1, [0.05, 0.05, 0.1], [5, 5, 3], 0, 0.0025, [0, 0, 0, 0], 0, 0];
	_scantei_spark setParticleParams [["\A3\data_f\proxies\muzzle_flash\muzzle_flash_silencer.p3d", 1, 0, 1], "", "SpaceObject", 1, 1, [0, 0,_spark_poz_rel], [0, 0, 0], 0, 20, 7.9, 0, [0.5,0.5,0.05], [[1, 1, 1, 1], [1, 1, 1, 1], [1, 1, 1, 0]], [0.08], 1, 0, "", "", _lamp,0,true,0.3,[[0,0,0,0]]];
	_scantei_spark setDropInterval 0.001;	
	
	_lamp say3D [_sparky_sun, 350];
	sleep 0.1 +(random 0.4);
	deleteVehicle _scantei_spark;
};};

//////////////////////

// ALIAS:

[] spawn {
	if (!hasInterface) exitWith {};
	_obj = cone2;
	_e_static = "#particlesource" createVehicleLocal (getPosATL _obj);
_e_static setParticleCircle [0.1, [0, 0, 0]];
_e_static setParticleRandom [0.2, [1.5,1.5,0], [0.175, 0.175, 0], 0.15, 0.2, [0, 0, 0, 1], 1, 0];
_e_static setParticleParams [
	["\A3\data_f\blesk1", 1, 0, 1], 
	"", 					// animationName,				/* String */
	"SpaceObject", 			// particleType,				/* String - Enum: Billboard, SpaceObject */
	1,						// timerPeriod,				/* Number */
	0.25, 					// lifeTime,					/* Number */
	[0, 0, 0], 				// pos3D,		/* 3D Array of numbers as relative position to particleSource or (if object at index 18 is set) object. Or (if object at index 18 is set) String as memoryPoint of object. */
	[0, 0, 0], 				// moveVelocity,				/* 3D Array of numbers. */
	0, 						// rotationVelocity,			/* Number */
	10, 					// weight,						/* Number */
	7.9,					// volume,						/* Number */
	0, 						// rubbing,					    /* Number */
	[0, 0.02, 0], 			// sizeOverLifetime,			/* Array of Numbers */
	[						// color,						/* Array of Array of RGBA Numbers */
		[1, 1, 0.1, 1], 	//
		[1, 1, 1, 1]		//
	], 
	[0.01], 				// animationSpeed,				/* Array of Number */
	1, 						// randomDirectionPeriod,		/* Number */
	0, 						// randomDirectionIntensity,	/* Number */
	"", 					// onTimerScript,				/* String */
	"", 					// beforeDestroyScript,		/* String */
	_obj					// obj,						/* Object */
	// angle,                  // angle,						/* Optional Number - Default: 0 */
	// onSurface,			    // onSurface,					/* Optional Boolean */
	// bounceOnSurface,	    // bounceOnSurface,			/* Optional Number */
	// emissiveColor,			// emissiveColor,				/* Optional Array of Array of RGBA Numbers */
	// vectorDirOrVectorDirAndUp,// vectorDirOrVectorDirAndUp	/* Optional vector dir or [vectorDir, vectorUp]
					// Since Arma 3 v1.92 it is possible to set the initial direction of the SpaceObject
					// Since Arma 3 v2.12 it is possible to use a [vectorDir, vectorUp] array */
];
_e_static setDropInterval 0.15;
sleep 10;
deleteVehicle _e_static};


//////////////////////

// Testing:

[] spawn {
	if (!hasInterface) exitWith {};
	_obj = cone2;
	_e_static = "#particlesource" createVehicleLocal (getPosATL _obj);
	_e_static setParticleCircle [0.1, [0, 0, 0]];
	_e_static setParticleRandom [0.2, [1.5,1.5,0], [0.175, 0.175, 0], 0.15, 0.2, [0, 0, 0, 1], 1, 0];
	_e_static setParticleParams [["\A3\data_f\blesk1", 1, 0, 1],"","SpaceObject",1,0.25,[0, 0, 0],0,10,7.9,0,[0, 0.02, 0],[	[1, 1, 0.1, 1],[1, 1, 1, 1]], [0.01], 1, 	0, 	"", "", _obj];
	_e_static setDropInterval 0.15;
	sleep 3;
	deleteVehicle _e_static
};

[] spawn {
	if (!hasInterface) exitWith {};
	_source = cone2;
	_e_static = "#particlesource" createVehicleLocal (getPosATL _source); 
	_e_static setParticleCircle [0.1, [0, 0, 0]]; 
	_e_static setParticleParams [["\A3\data_f\blesk1", 1, 0, 1], "", "SpaceObject", 1, 0.25, [0, 0, 0], [0, 0, 0], 0, 10, 7.9,0, [0, 0.02, 0], [[1, 1, 0.1, 1], [1, 1, 1, 1]], [0.01], 1, 0, "", "", _source]; 
	_e_static setDropInterval 0.15;
	sleep 3;
	deleteVehicle _e_static
};



[] spawn {  
if (!hasInterface) exitWith {}; 
  
 _source = cone2;  
 private _pos = getPosATL _source; 
 private _vicPos = getPosATL cone3; 
 
 private _vectorDir = [0,0.1,10];  
 _velocity = (_vicPos vectorDiff _pos) vectorMultiply 2; 
 
 _e_static = "#particlesource" createVehicleLocal (getPosATL _source);   
     
 _e_static setParticleParams [["\A3\data_f\blesk1", 0, 0, 0], "", "SpaceObject", 1, 1, [0, 0, 0], _velocity, 0, 15, 11,0, [0, 0.02, 0], [[1, 1, 0.1, 1], [1, 1, 1, 1]], [0.1], 0, 1, "", "", _source,0,true, 0, [], _vectorDir];   
 _e_static setDropInterval 0.15;  
 sleep 3;  
 deleteVehicle _e_static  
};


//// flash lightning in place:

[] spawn {    
if (!hasInterface) exitWith {};   
    
 _source = cone2;    
 private _pos = getPosATL _source;   
 private _vicPos = getPosATL cone3;   
   
 private _vectorDir = _vicPos vectorFromTo _pos;     
 _velocity = (_vicPos vectorDiff _pos) vectorMultiply 2;   
   
 _e_static = "#particlesource" createVehicleLocal (getPosATL _source);     
       
 _e_static setParticleParams [["\A3\data_f\blesk1", 0, 0, 0], "", "SpaceObject", 1, 1, [0, 0, 0], [0,0,0], 0, 15, 11,0, [0, 0.2, 0], [[1, 1, 0.1, 1], [1, 1, 1, 1]], [1], 0, 0, "", "", _source,0,true, 0, [], _vectorDir];     
 _e_static setDropInterval 1;    
 sleep 3;    
 deleteVehicle _e_static    
};


///// flash static rapidly in one spot

[] spawn {    
if (!hasInterface) exitWith {};   
    
 _source = cone2;    
 private _pos = getPosATL _source;   
 private _vicPos = getPosATL cone3;   
   
 private _vectorDir = _vicPos vectorFromTo _pos;     
 _velocity = (_vicPos vectorDiff _pos) vectorMultiply 2;   
   
 _e_static = "#particlesource" createVehicleLocal (getPosATL _source);     
       
 _e_static setParticleParams [["\A3\data_f\blesk1", 0, 0, 0], "", "SpaceObject", 0.5, 0.1, [0, 0, 0], (velocity _source), 0, 15, 11,0, [0, 0.01], [[1, 1, 0.1, 1], [1, 1, 1, 1]], [0.01], 1, 0, "", "", _source];     
 _e_static setDropInterval 0.1;    
 sleep 0.5;    
 deleteVehicle _e_static    
};


///// rapid laser beam between 2 points 

[] spawn {     
if (!hasInterface) exitWith {};  

private _getPosTop = {  
	params ["_obj"];  
	
	_loc = getPosASL _obj;  
	
	_locAbove = _loc vectorAdd [0,0,10];  
	
	_hits = lineIntersectsSurfaces [_locAbove, _loc, objNull, objNull, true, 10, "FIRE", "GEOM"];  
	if ((count _hits) > 0) then {  
	_hit = _hits select 0;  
	_dist = (_hit select 0) select 2;  
	_loc = (_hit select 0);  
	};  
	_loc  
};
     
 _source = cone2;     
 private _pos = getPosASL _source;    
 private _vicPos = [cone3] call _getPosTop;
 [str(_vicPos)] remoteExec ['hint'];

 private _vecDistance = (_vicPos vectorDiff _pos ) vectorMultiply 0.5; 
 private _distance = _vicPos vectorDistance _pos;
    
 private _vectorDir = _vicPos vectorFromTo _pos;      
 _velocity = (_vicPos vectorDiff _pos) vectorMultiply 20;    
 
 _e_static = "#particlesource" createVehicleLocal (getPosATL _source);      
        
 _e_static setParticleParams [["\A3\data_f\laserBeam", 1, 1, 1], "", "SpaceObject", 1, 0.05, _vecDistance, [0,0,0], 0, 1.1475, 0.9,0, [_distance], [[255, 0, 0, 1], [255, 0, 0, 1]], [1], 0, 0, "", "", "no_object",0,false, -1, [[0,30,30,0]], _vectorDir];      
 _e_static setDropInterval 0.1;     
 sleep 0.25;     
 deleteVehicle _e_static     
};


/////// GET THE TOP OF AN OBJECT: (IS IN ASL)

private _getPosTop = {  
 params ["_obj"];  
  
 _loc = getPosASL _obj;  
  
 _locAbove = _loc vectorAdd [0,0,10];  
  
 _hits = lineIntersectsSurfaces [_locAbove, _loc, objNull, objNull, true, 10, "FIRE", "GEOM"];  
 hint str([_hits, _loc]); 
 if ((count _hits) > 0) then {  
  _hit = _hits select 0;  
  _dist = (_hit select 0) select 2;  
  _loc = (_hit select 0);  
 };  
 _loc  
};

_top = [_this] call _getPosTop;

//////////////////



YOSHI_getPosTop = {   
 params ["_obj"];   
  
 _loc = getPosASL _obj;   
  
 _locAbove = _loc vectorAdd [0,0,10];   
  
 _hits = lineIntersectsSurfaces [_locAbove, _loc, objNull, objNull, true, 10, "FIRE", "GEOM"];   
 if ((count _hits) > 0) then {   
 _hit = _hits select 0;   
 _dist = (_hit select 0) select 2;   
 _loc = (_hit select 0);   
 };   
 _loc   
}; 
 
YOSHI_beamA2B = { 
 params ["_posA", "_posB"]; 
     
 private _fromPos = _posA; 
 private _toPos = _posB;     
 
 private _vecDistance = (_fromPos vectorDiff _toPos ) vectorMultiply 0.5;  
 private _distance = _fromPos vectorDistance _toPos; 
   
 private _vectorDir = _fromPos vectorFromTo _toPos;       
 _velocity = (_fromPos vectorDiff _toPos) vectorMultiply 20;     
  
 _e_static = "#particlesource" createVehicleLocal _toPos;       
    
 _e_static setParticleParams [["\A3\data_f\laserBeam", 1, 1, 1], "", "SpaceObject", 1, 0.05, _vecDistance, [0,0,0], 0, 1.1475, 0.9,0, [_distance], [[255, 0, 0, 1], [255, 0, 0, 1]], [1], 0, 0, "", "", "no_object",0,false, -1, [[0,30,30,0]], _vectorDir];       
 _e_static setDropInterval 0.05;      
 sleep 0.05;      
 deleteVehicle _e_static; 
};

YOSHI_beamVic2Pos = {
	params ["_vic", "_pos"];


	_count = 3;

	while {(alive _vic) && (_count > 0)} do {
		hint "beep";
		_topOfVic = ASLToATL ([_vic] call YOSHI_getPosTop); 
		[_topOfVic, _pos] call YOSHI_beamA2B;
		sleep 0.3;
		_count = _count - 1;
	};

};

 
 
[[_this, (getPosATL cone)], YOSHI_beamVic2Pos] remoteExec ["spawn"];



///////////// Universal APS Code:


_this addEventHandler ["Fired", {
	params ["_unit", "_weapon", "_muzzle", "_mode", "_ammo", "_magazine", "_projectile"];
	if (_projectile isKindOf "MissileBase" || _projectile isKindOf "RocketBase") then {
		hint format ["Missile or rocket fired"];
		[_projectile] spawn {
			params ["_proj"];
			hint format ["Spawned at : %1", serverTime];
			while {(alive _proj)} do {
				{
					if ((_proj distance _x) < 30) exitWith {
						private _pos = getPosATL _proj;
						deleteVehicle _proj;
						_orange = createVehicle ["ModuleAPERSMineDispenser_Mine_F", _pos, [], 0, "CAN_COLLIDE"];	
						_orange setDamage 1;
						hint format ["Detected at : %1", serverTime];
					};
				} forEach (missionNamespace getVariable ["APS_objects", []]);
				sleep 0.05;
			};
		};
	};
}];

/// TODO: look into:

["CAManBase", "init", {
    params ["_unit"];
    _unit addEventHandler ["Fired", {
        params ["_unit", "_weapon", "_muzzle", "_mode", "_ammo", "_magazine", "_projectile"];
        /// ... 
    }];
}] call CBA_fnc_addClassEventHandler;


_count = 0;
{
	_this setObjectMaterialGlobal [_count, "A3\Structures_F\Data\Windows\window_set.rvmat"];
	_count = _count + 1;
} forEach (getObjectTextures _this);


/////


private _trigger = createTrigger ["EmptyDetector", (getPosATL _this), true];  
_trigger setTriggerArea [5, 5, 0, false];   
_trigger setTriggerActivation ["ANY", "PRESENT", true];   
_trigger setTriggerStatements [  
    "{if ((_x isKindOf 'Man') && (vehicle _x == _x)) exitWith {true};} forEach thisList;",  
    "{if ((_x isKindOf 'Man') && (vehicle _x == _x)) then {hint format['A %1 on foot has entered the trigger area. %2', _x, serverTime];};} forEach thisList;",  
    "hint 'A Man on foot has left the trigger area.';"  
];

// also add trigger for fired to temporarily hide the object attached
/*
The Lord is my light and my salvation;
whom shall I fear?
The Lord is the stronghold of my life;
of whom shall I be afraid?
(Psalm 27:1)
*/

YAS_IRONDOME_BOX_CLASS = "YAS_OPHANIM_box";
YAS_IRONDOME_MISSILE_CLASS = "M_Jian_AT";
YAS_IRONDOME_SPAWN_OFFSET = [0, 0, 1];
YAS_IRONDOME_FUSE_DISTANCE = 40;
YAS_IRONDOME_INITIAL_SPEED = 350;
YAS_IRONDOME_RETRY_INTERVAL = 15;
YAS_IRONDOME_MAX_SHOTS = 6;
YAS_IRONDOME_VERTICAL_LAUNCH_SPEED = 350;
YAS_IRONDOME_LAUNCH_SPACING = 4;
YAS_IRONDOME_ASSIGNMENT_WINDOW = 0.5;
YAS_IRONDOME_LAUNCH_SOUNDS = ["YAS_OphanimReload1", "YAS_OphanimReload2"];

if (isNil "YAS_IRONDOME_REGISTRY") then {
    YAS_IRONDOME_REGISTRY = [];
};
if (isNil "YAS_IRONDOME_ARTY_EH_ID") then {
    YAS_IRONDOME_ARTY_EH_ID = -1;
};
if (isNil "YAS_IRONDOME_ENTITY_CREATED_EH_ID") then {
    YAS_IRONDOME_ENTITY_CREATED_EH_ID = -1;
};
if (isNil "YAS_IRONDOME_SERVER_READY") then {
    YAS_IRONDOME_SERVER_READY = false;
};
if (isNil "YAS_IRONDOME_MANUAL_CONTROL") then {
    YAS_IRONDOME_MANUAL_CONTROL = getNumber (configFile >> "CfgAmmo" >> YAS_IRONDOME_MISSILE_CLASS >> "manualControl");
};
if (isNil "YAS_IRONDOME_TASKS") then {
    YAS_IRONDOME_TASKS = [];
};
if (isNil "YAS_IRONDOME_DISPATCHER_HANDLE") then {
    YAS_IRONDOME_DISPATCHER_HANDLE = scriptNull;
};

YAS_fnc_ironDomeLog = {
    params ["_msg"];
    private _line = format ["[Iron Dome] %1", _msg];

    if (!isNil "YAS_fnc_debugMsg") exitWith {
        [_line] call YAS_fnc_debugMsg;
    };

    diag_log _line;
};

YAS_fnc_ironDomeGetEngagementRadius = {
    (missionNamespace getVariable ["YAS_ironDomeEngagementRadius", 1500]) max 0
};

YAS_fnc_ironDomeGetAssignmentWindow = {
    (missionNamespace getVariable ["YAS_IRONDOME_ASSIGNMENT_WINDOW", 0.5]) max 0
};

YAS_fnc_ironDomeCleanupRegistry = {
    if (!isServer) exitWith {[]};

    if (isNil "YAS_IRONDOME_REGISTRY") then {
        YAS_IRONDOME_REGISTRY = [];
    };

    YAS_IRONDOME_REGISTRY = YAS_IRONDOME_REGISTRY select {
        !isNull _x
        && {alive _x}
        && {_x isKindOf YAS_IRONDOME_BOX_CLASS}
        && {_x getVariable ["YAS_ironDome_enabled", true]}
    };

    YAS_IRONDOME_REGISTRY
};

YAS_fnc_ironDomeRefreshRegistry = {
    if (!isServer) exitWith {[]};

    if (isNil "YAS_IRONDOME_REGISTRY") then {
        YAS_IRONDOME_REGISTRY = [];
    };

    {
        if (!isNull _x && {_x isKindOf YAS_IRONDOME_BOX_CLASS}) then {
            YAS_IRONDOME_REGISTRY pushBackUnique _x;
        };
    } forEach (entities YAS_IRONDOME_BOX_CLASS);

    call YAS_fnc_ironDomeCleanupRegistry
};

YAS_fnc_ironDomeRegisterBox = {
    params [["_box", objNull, [objNull]]];

    if (!isServer) exitWith {false};
    if (isNull _box) exitWith {false};
    if !(_box isKindOf YAS_IRONDOME_BOX_CLASS) exitWith {false};

    if (isNil "YAS_IRONDOME_REGISTRY") then {
        YAS_IRONDOME_REGISTRY = [];
    };

    _box setVariable ["YAS_ironDome_enabled", true, true];
    _box setVariable ["YAS_ironDome_nextLaunchAt", -1, true];

    private _before = count YAS_IRONDOME_REGISTRY;
    YAS_IRONDOME_REGISTRY pushBackUnique _box;

    if ((count YAS_IRONDOME_REGISTRY) > _before) then {
        [format ["registered Ophanim box %1", _box]] call YAS_fnc_ironDomeLog;
    };

    true
};

YAS_fnc_ironDomePlayLaunchSound = {
    params [["_launcher", objNull, [objNull]]];

    if (isNull _launcher) exitWith {false};

    private _soundName = selectRandom YAS_IRONDOME_LAUNCH_SOUNDS;
    [_launcher, [_soundName, 1200, 1]] remoteExec ["say3D", 0];
    true
};

YAS_fnc_ironDomeFindTaskForShell = {
    params [["_shell", objNull, [objNull]]];

    if (isNull _shell) exitWith {createHashMap};

    private _result = createHashMap;
    {
        if ((_x getOrDefault ["shell", objNull]) isEqualTo _shell) exitWith {
            _result = _x;
        };
    } forEach YAS_IRONDOME_TASKS;

    _result
};

YAS_fnc_ironDomeCreateTask = {
    params [
        ["_shell", objNull, [objNull]],
        ["_source", objNull, [objNull]],
        ["_ammo", "", [""]]
    ];

    if (!isServer || {isNull _shell}) exitWith {createHashMap};

    private _existing = [_shell] call YAS_fnc_ironDomeFindTaskForShell;
    if ((count _existing) > 0) exitWith {_existing};

    private _task = createHashMapFromArray [
        ["shell", _shell],
        ["source", _source],
        ["ammo", _ammo],
        ["createdAt", serverTime],
        ["attempts", 0],
        ["nextAttemptAt", serverTime],
        ["assignedLauncher", objNull],
        ["scheduledLaunchAt", -1],
        ["waitingForCoverageLogged", false],
        ["waitingForSlotLogged", false]
    ];

    YAS_IRONDOME_TASKS pushBack _task;
    _task
};

YAS_fnc_ironDomeCleanupTasks = {
    if (!isServer) exitWith {[]};

    private _keep = [];

    {
        private _task = _x;
        private _shell = _task getOrDefault ["shell", objNull];

        if (!isNull _shell && {!(_shell getVariable ["YAS_ironDome_hit", false])}) then {
            _keep pushBack _task;
        } else {
            if (!isNull _shell) then {
                _shell setVariable ["YAS_ironDome_controllerActive", false];
            };
        };
    } forEach YAS_IRONDOME_TASKS;

    YAS_IRONDOME_TASKS = _keep;
    YAS_IRONDOME_TASKS
};

YAS_fnc_ironDomeGetLauncherCandidatesForTask = {
    params [
        ["_task", createHashMap],
        ["_launchAvailability", [], [[]]]
    ];

    if (!isServer || {(count _task) <= 0}) exitWith {[]};

    private _shell = _task getOrDefault ["shell", objNull];
    if (isNull _shell) exitWith {[]};

    private _radius = call YAS_fnc_ironDomeGetEngagementRadius;
    private _candidates = [];

    {
        private _launcher = _x;
        private _shellDistance = _launcher distance2D _shell;
        if (_shellDistance <= _radius) then {
            private _candidateLaunchAt = _launcher getVariable ["YAS_ironDome_nextLaunchAt", -1];
            {
                _x params ["_availabilityLauncher", "_availabilityAt"];
                if (_availabilityLauncher isEqualTo _launcher) exitWith {
                    _candidateLaunchAt = _availabilityAt;
                };
            } forEach _launchAvailability;
            if (_candidateLaunchAt < serverTime) then {
                _candidateLaunchAt = serverTime;
            };

            _candidates pushBack [_launcher, _candidateLaunchAt, _shellDistance];
        };
    } forEach (call YAS_fnc_ironDomeRefreshRegistry);

    _candidates
};

YAS_fnc_ironDomeSelectLauncherForTask = {
    params [
        ["_task", createHashMap],
        ["_launchAvailability", [], [[]]]
    ];

    private _candidates = [_task, _launchAvailability] call YAS_fnc_ironDomeGetLauncherCandidatesForTask;
    private _bestLauncher = objNull;
    private _bestLaunchAt = 1e10;
    private _bestDistance = 1e10;

    {
        _x params ["_launcher", "_candidateLaunchAt", "_shellDistance"];

        if (
            (_candidateLaunchAt < _bestLaunchAt)
            || {
                (_candidateLaunchAt <= (_bestLaunchAt + 0.01))
                && {_shellDistance < _bestDistance}
            }
        ) then {
            _bestLauncher = _launcher;
            _bestLaunchAt = _candidateLaunchAt;
            _bestDistance = _shellDistance;
        };
    } forEach _candidates;

    if (isNull _bestLauncher) exitWith {[objNull, -1, -1, 0]};
    [_bestLauncher, _bestLaunchAt, _bestDistance, count _candidates]
};

YAS_fnc_ironDomeAssignTasks = {
    if (!isServer) exitWith {false};

    private _launchAvailability = [];
    {
        _launchAvailability pushBack [
            _x,
            ((_x getVariable ["YAS_ironDome_nextLaunchAt", -1]) max serverTime)
        ];
        _x setVariable ["YAS_ironDome_taskedShell", objNull, true];
    } forEach (call YAS_fnc_ironDomeRefreshRegistry);

    {
        private _task = _x;
        private _shell = _task getOrDefault ["shell", objNull];

        _task set ["assignedLauncher", objNull];
        _task set ["scheduledLaunchAt", -1];

        if (
            !isNull _shell
            && {!(_shell getVariable ["YAS_ironDome_hit", false])}
            && {(_task getOrDefault ["attempts", 0]) < YAS_IRONDOME_MAX_SHOTS}
            && {(_task getOrDefault ["nextAttemptAt", 0]) <= serverTime}
        ) then {
            private _selection = [_task, _launchAvailability] call YAS_fnc_ironDomeSelectLauncherForTask;
            _selection params [
                ["_launcher", objNull, [objNull]],
                ["_scheduledLaunchAt", -1, [0]],
                ["_shellDistance", -1, [0]],
                ["_candidateCount", 0, [0]]
            ];

            if (isNull _launcher) then {
                if !(_task getOrDefault ["waitingForCoverageLogged", false]) then {
                    [
                        format [
                            "task waiting for coverage: shell=%1 attempts=%2 radius=%3m",
                            _shell,
                            _task getOrDefault ["attempts", 0],
                            round (call YAS_fnc_ironDomeGetEngagementRadius)
                        ]
                    ] call YAS_fnc_ironDomeLog;
                    _task set ["waitingForCoverageLogged", true];
                    _task set ["waitingForSlotLogged", false];
                };
            } else {
                private _launchWait = (_scheduledLaunchAt - serverTime) max 0;
                _task set ["waitingForCoverageLogged", false];
                if (_launchWait <= (call YAS_fnc_ironDomeGetAssignmentWindow)) then {
                    _task set ["assignedLauncher", _launcher];
                    _task set ["scheduledLaunchAt", _scheduledLaunchAt];
                    _task set ["waitingForSlotLogged", false];
                    _launcher setVariable ["YAS_ironDome_taskedShell", _shell, true];

                    {
                        _x params ["_availabilityLauncher", "_availabilityAt"];
                        if (_availabilityLauncher isEqualTo _launcher) exitWith {
                            _launchAvailability set [_forEachIndex, [_availabilityLauncher, _scheduledLaunchAt + YAS_IRONDOME_LAUNCH_SPACING]];
                        };
                    } forEach _launchAvailability;

                    [
                        format [
                            "task assigned: shell=%1 launcher=%2 launchAt=%3 wait=%4s shellDist=%5m candidates=%6 attempts=%7",
                            _shell,
                            _launcher,
                            _scheduledLaunchAt,
                            round _launchWait,
                            round _shellDistance,
                            _candidateCount,
                            _task getOrDefault ["attempts", 0]
                        ]
                    ] call YAS_fnc_ironDomeLog;
                } else {
                    if !(_task getOrDefault ["waitingForSlotLogged", false]) then {
                        [
                            format [
                                "task waiting for launch slot: shell=%1 bestLauncher=%2 bestWait=%3s shellDist=%4m candidates=%5",
                                _shell,
                                _launcher,
                                round _launchWait,
                                round _shellDistance,
                                _candidateCount
                            ]
                        ] call YAS_fnc_ironDomeLog;
                        _task set ["waitingForSlotLogged", true];
                    };
                };
            };
        };
    } forEach YAS_IRONDOME_TASKS;

    true
};

YAS_fnc_ironDomeExecuteAssignedTasks = {
    if (!isServer) exitWith {false};

    {
        private _task = _x;
        private _shell = _task getOrDefault ["shell", objNull];
        private _launcher = _task getOrDefault ["assignedLauncher", objNull];
        private _scheduledLaunchAt = _task getOrDefault ["scheduledLaunchAt", -1];

        if (!isNull _launcher && {_scheduledLaunchAt <= serverTime}) then {
            _task set ["assignedLauncher", objNull];
            _task set ["scheduledLaunchAt", -1];

            if (
                isNull _shell
                || {_shell getVariable ["YAS_ironDome_hit", false]}
                || {!alive _launcher}
                || {!(_launcher getVariable ["YAS_ironDome_enabled", true])}
                || {(_launcher distance2D _shell) > (call YAS_fnc_ironDomeGetEngagementRadius)}
            ) then {
                _launcher setVariable ["YAS_ironDome_taskedShell", objNull, true];
            } else {
                private _attempt = (_task getOrDefault ["attempts", 0]) + 1;
                _task set ["attempts", _attempt];
                _task set ["nextAttemptAt", serverTime + YAS_IRONDOME_RETRY_INTERVAL];
                _task set ["waitingForSlotLogged", false];
                _launcher setVariable ["YAS_ironDome_taskedShell", objNull, true];
                _launcher setVariable ["YAS_ironDome_nextLaunchAt", serverTime + YAS_IRONDOME_LAUNCH_SPACING, true];

                [
                    format [
                        "launch attempt %1/%2 against shell=%3 with launcher=%4 missile=%5 retryInterval=%6s launchSpacing=%7s shellDist=%8m radius=%9m",
                        _attempt,
                        YAS_IRONDOME_MAX_SHOTS,
                        _shell,
                        _launcher,
                        YAS_IRONDOME_MISSILE_CLASS,
                        YAS_IRONDOME_RETRY_INTERVAL,
                        YAS_IRONDOME_LAUNCH_SPACING,
                        round (_launcher distance2D _shell),
                        round (call YAS_fnc_ironDomeGetEngagementRadius)
                    ]
                ] call YAS_fnc_ironDomeLog;

                private _missile = [_launcher, _shell] call YAS_fnc_ironDomeSpawnMissile;
                if (isNull _missile) then {
                    [
                        format [
                            "launch attempt %1 failed for shell=%2 with missile=%3",
                            _attempt,
                            _shell,
                            YAS_IRONDOME_MISSILE_CLASS
                        ]
                    ] call YAS_fnc_ironDomeLog;
                } else {
                    _launcher setVariable ["YAS_ironDome_interceptCount", (_launcher getVariable ["YAS_ironDome_interceptCount", 0]) + 1, true];
                    [_launcher, _missile, _shell, _task getOrDefault ["source", objNull], _attempt] spawn YAS_fnc_ironDomeMonitorIntercept;
                };
            };
        };
    } forEach YAS_IRONDOME_TASKS;

    true
};

YAS_fnc_ironDomeEnsureDispatcher = {
    if (!isServer) exitWith {false};

    if (!isNil "YAS_IRONDOME_DISPATCHER_HANDLE" && {!scriptDone YAS_IRONDOME_DISPATCHER_HANDLE}) exitWith {true};

    YAS_IRONDOME_DISPATCHER_HANDLE = [] spawn {
        while {YAS_IRONDOME_SERVER_READY} do {
            call YAS_fnc_ironDomeRefreshRegistry;
            call YAS_fnc_ironDomeCleanupTasks;

            if !((count YAS_IRONDOME_TASKS) isEqualTo 0) then {
                call YAS_fnc_ironDomeAssignTasks;
                call YAS_fnc_ironDomeExecuteAssignedTasks;
            };

            sleep 0.1;
        };
    };

    ["Iron Dome dispatcher started."] call YAS_fnc_ironDomeLog;
    true
};

YAS_fnc_ironDomeSpawnMissile = {
    params [
        ["_launcher", objNull, [objNull]],
        ["_shell", objNull, [objNull]]
    ];

    if (isNull _launcher || {isNull _shell}) exitWith {objNull};
    if (YAS_IRONDOME_MANUAL_CONTROL <= 0) exitWith {objNull};

    private _spawnPosASL = ATLToASL (_launcher modelToWorld YAS_IRONDOME_SPAWN_OFFSET);
    private _missile = createVehicle [YAS_IRONDOME_MISSILE_CLASS, ASLToAGL _spawnPosASL, [], 0, "CAN_COLLIDE"];
    if (isNull _missile) exitWith {
        [format ["failed to spawn missile class %1", YAS_IRONDOME_MISSILE_CLASS]] call YAS_fnc_ironDomeLog;
        objNull
    };

    _missile setPosASL _spawnPosASL;
    _missile setVectorDirAndUp [[0, 0, 1], [0, 1, 0]];
    _missile setVelocity [0, 0, YAS_IRONDOME_VERTICAL_LAUNCH_SPEED];

    [_launcher] call YAS_fnc_ironDomePlayLaunchSound;

    [_missile, _shell] spawn {
        params ["_missile", "_shell"];

        sleep 0.35;

        if (isNull _missile || {isNull _shell}) exitWith {};

        private _missilePosASL = getPosASL _missile;
        private _shellPosASL = getPosASL _shell;
        private _dirVec = _shellPosASL vectorDiff _missilePosASL;

        if ((vectorMagnitude _dirVec) < 0.01) then {
            _dirVec = [0, 0, 1];
        };

        private _dirNorm = vectorNormalized _dirVec;
        private _upVec = if (abs (_dirNorm select 2) > 0.95) then {[0, 1, 0]} else {[0, 0, 1]};

        _missile setVectorDirAndUp [_dirNorm, _upVec];
        _missile setVelocity ((_dirNorm vectorMultiply YAS_IRONDOME_INITIAL_SPEED) vectorAdd [0, 0, 40]);
        _missile setMissileTargetPos (getPosATL _shell);
    };

    _missile
};

YAS_fnc_ironDomeMonitorIntercept = {
    params [
        ["_launcher", objNull, [objNull]],
        ["_missile", objNull, [objNull]],
        ["_shell", objNull, [objNull]],
        ["_source", objNull, [objNull]],
        ["_attemptIndex", 1, [0]]
    ];

    if (isNull _launcher || {isNull _missile} || {isNull _shell}) exitWith {false};

    private _success = false;
    private _closestDistance = 1e10;
    private _nextReportAt = time;
    private _endReason = "timeout";

    for "_i" from 0 to 240 do {
        if (_shell getVariable ["YAS_ironDome_hit", false]) exitWith {
            _endReason = "shell-already-hit";
        };
        if (isNull _launcher || {!alive _launcher}) exitWith {
            _endReason = "launcher-dead";
        };
        if !(_launcher getVariable ["YAS_ironDome_enabled", true]) exitWith {
            _endReason = "launcher-disabled";
        };
        if (isNull _missile) exitWith {
            _endReason = "missile-null";
        };
        if (isNull _shell) exitWith {
            _endReason = "shell-null";
        };

        private _currentDistance = _missile distance _shell;
        if (_currentDistance < _closestDistance) then {
            _closestDistance = _currentDistance;
        };

        _launcher setVariable ["YAS_ironDome_lastDistance", _currentDistance, true];
        _launcher setVariable ["YAS_ironDome_closestDistance", _closestDistance, true];

        if (time >= _nextReportAt) then {
            [
                format [
                    "track attempt=%1 launcher=%2 missile=%3 shell=%4 currentDist=%5m closest=%6m",
                    _attemptIndex,
                    _launcher,
                    _missile,
                    _shell,
                    round _currentDistance,
                    round _closestDistance
                ]
            ] call YAS_fnc_ironDomeLog;

            _nextReportAt = time + 0.25;
        };

        _missile setMissileTargetPos (getPosATL _shell);

        if (_currentDistance <= YAS_IRONDOME_FUSE_DISTANCE) exitWith {
            _success = true;
            _endReason = "fuse-hit";
        };

        sleep 0.025;
    };

    if (!_success) exitWith {
        if (!isNull _missile) then {
            [
                format [
                    "guidance loop ended for missile %1 without fuse hit. reason=%2 closestDistance=%3m attempt=%4",
                    _missile,
                    _endReason,
                    round _closestDistance,
                    _attemptIndex
                ]
            ] call YAS_fnc_ironDomeLog;

            deleteVehicle _missile;
        };

        false
    };

    _launcher setVariable ["YAS_ironDome_successCount", (_launcher getVariable ["YAS_ironDome_successCount", 0]) + 1, true];
    _shell setVariable ["YAS_ironDome_hit", true];

    private _shellPosATL = if (!isNull _shell) then {getPosATL _shell} else {getPosATL _source};
    "HelicopterExploSmall" createVehicle (_shellPosATL vectorAdd [0, 0, 0.1]);

    if (!isNull _shell) then {
        _shell setVariable ["YAS_ironDome_controllerActive", false];
        deleteVehicle _shell;
    };

    if (!isNull _missile) then {
        deleteVehicle _missile;
    };

    [
        format [
            "intercept success: launcher=%1 source=%2 fuseDistance=%3 closestDistance=%4m attempt=%5",
            _launcher,
            _source,
            YAS_IRONDOME_FUSE_DISTANCE,
            round _closestDistance,
            _attemptIndex
        ]
    ] call YAS_fnc_ironDomeLog;

    true
};

YAS_fnc_ironDomeHandleShellFired = {
    params ["_vehicle", "_ammo", "_shell"];

    if (!isServer) exitWith {false};
    if (isNull _shell) exitWith {false};

    private _registry = call YAS_fnc_ironDomeRefreshRegistry;
    if (_registry isEqualTo []) exitWith {false};

    if (!local _shell) exitWith {
        [
            format [
                "shell %1 seen for source %2, but it is not local here. shellOwner=%3",
                _shell,
                _vehicle,
                owner _shell
            ]
        ] call YAS_fnc_ironDomeLog;
        false
    };

    if (_shell getVariable ["YAS_ironDome_controllerActive", false]) exitWith {false};
    _shell setVariable ["YAS_ironDome_controllerActive", true];
    _shell setVariable ["YAS_ironDome_hit", false];

    [
        format [
            "tracking shell=%1 ammo=%2 source=%3 activeOphanim=%4 radius=%5m tasking=enabled",
            _shell,
            _ammo,
            _vehicle,
            count _registry,
            round (call YAS_fnc_ironDomeGetEngagementRadius)
        ]
    ] call YAS_fnc_ironDomeLog;

    [_shell, _vehicle, _ammo] call YAS_fnc_ironDomeCreateTask;
    call YAS_fnc_ironDomeEnsureDispatcher;
    true
};

YAS_fnc_ironDomeEnsureArtilleryEH = {
    if (!isServer) exitWith {false};

    if (isNil "YAS_IRONDOME_ARTY_EH_ID") then {
        YAS_IRONDOME_ARTY_EH_ID = -1;
    };

    if (YAS_IRONDOME_ARTY_EH_ID >= 0) exitWith {true};

    YAS_IRONDOME_ARTY_EH_ID = addMissionEventHandler ["ArtilleryShellFired", {
        params ["_vehicle", "_weapon", "_ammo", "_gunner", "_instigator", "_artilleryTarget", "_targetPosition", "_shell"];
        [_vehicle, _ammo, _shell] call YAS_fnc_ironDomeHandleShellFired;
    }];

    ["server ArtilleryShellFired listener installed for Iron Dome."] call YAS_fnc_ironDomeLog;
    true
};

YAS_fnc_ironDomeInitServer = {
    if (!isServer) exitWith {false};
    if (YAS_IRONDOME_SERVER_READY) exitWith {true};

    YAS_IRONDOME_MANUAL_CONTROL = getNumber (configFile >> "CfgAmmo" >> YAS_IRONDOME_MISSILE_CLASS >> "manualControl");
    YAS_IRONDOME_SERVER_READY = true;
    call YAS_fnc_ironDomeRefreshRegistry;
    call YAS_fnc_ironDomeCleanupTasks;
    call YAS_fnc_ironDomeEnsureArtilleryEH;
    call YAS_fnc_ironDomeEnsureDispatcher;

    {
        [_x] call YAS_fnc_ironDomeRegisterBox;
    } forEach (entities YAS_IRONDOME_BOX_CLASS);

    if (YAS_IRONDOME_ENTITY_CREATED_EH_ID < 0) then {
        YAS_IRONDOME_ENTITY_CREATED_EH_ID = addMissionEventHandler ["EntityCreated", {
            params ["_entity"];

            if (_entity isKindOf YAS_IRONDOME_BOX_CLASS) then {
                [_entity] call YAS_fnc_ironDomeRegisterBox;
            };
        }];
    };

    [
        format [
            "Iron Dome server init complete. registeredOphanim=%1 queuedTasks=%2 manualControl=%3",
            count (call YAS_fnc_ironDomeRefreshRegistry),
            count (call YAS_fnc_ironDomeCleanupTasks),
            YAS_IRONDOME_MANUAL_CONTROL
        ]
    ] call YAS_fnc_ironDomeLog;

    if (YAS_IRONDOME_MANUAL_CONTROL <= 0) then {
        [
            format [
                "warning: missile class %1 does not report manualControl > 0. Ophanim launches will fail until that is corrected.",
                YAS_IRONDOME_MISSILE_CLASS
            ]
        ] call YAS_fnc_ironDomeLog;
    };

    true
};

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
YAS_IRONDOME_FUSE_DISTANCE = 150;
YAS_IRONDOME_INITIAL_SPEED = 350;
YAS_IRONDOME_RETRY_INTERVAL = 15;
YAS_IRONDOME_MAX_SHOTS = 6;
YAS_IRONDOME_VERTICAL_LAUNCH_SPEED = 350;
YAS_IRONDOME_LAUNCH_SPACING = 4;
YAS_IRONDOME_ASSIGNMENT_WINDOW = 0.5;
YAS_IRONDOME_LAUNCH_SOUNDS = ["YAS_OphanimReload1", "YAS_OphanimReload2"];
YAS_IRONDOME_EVENT_LIMIT = 64;
YAS_IRONDOME_AUDIT_LIMIT = 128;

// All consequential Iron Dome work is server-internal.  Global SQF function
// names are transport surfaces in an unrestricted Arma mission, so a server
// guard alone does not distinguish the mission event/dispatcher from a client
// remoteExec.  Each machine compiles a different unpublished capability; only
// the server's event path and workers ever receive the authoritative value.
localNamespace setVariable ["YAS_IRONDOME_TOKEN", format ["yas-iron-%1-%2-%3", diag_tickTime, random 1e9, random 1e9]];

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

YAS_fnc_ironDomeAudit = {
    params ["_token", "_operation", "_decision", ["_owner", -1], ["_detail", ""]];
    if (_token isNotEqualTo (localNamespace getVariable ["YAS_IRONDOME_TOKEN", ""])) exitWith {};
    private _rows = missionNamespace getVariable ["YAS_IRONDOME_AUDIT", []];
    _rows pushBack [diag_tickTime, _operation, _decision, _owner, _detail];
    if ((count _rows) > YAS_IRONDOME_AUDIT_LIMIT) then {
        _rows deleteRange [0, (count _rows) - YAS_IRONDOME_AUDIT_LIMIT];
    };
    missionNamespace setVariable ["YAS_IRONDOME_AUDIT", _rows, false];
};

YAS_fnc_ironDomeAuthorized = {
    params ["_provided", "_operation"];
    private _authoritative = localNamespace getVariable ["YAS_IRONDOME_TOKEN", ""];
    private _ok = isServer && {_authoritative isNotEqualTo ""} && {_provided isEqualTo _authoritative};
    if (!_ok && {isServer}) then {
        [_authoritative, _operation, "token-rejected", remoteExecutedOwner] call YAS_fnc_ironDomeAudit;
    };
    _ok
};

YAS_fnc_ironDomeObjectUid = {
    params ["_object", "_prefix", ["_token", "", [""]]];
    if !([_token, "object-uid"] call YAS_fnc_ironDomeAuthorized) exitWith {""};
    if (isNull _object) exitWith {""};
    private _uid = _object getVariable ["YAS_ironDome_uid", ""];
    if (_uid isEqualTo "") then {
        private _networkId = netId _object;
        _uid = if (_networkId isNotEqualTo "" && {_networkId isNotEqualTo "0:0"}) then {
            format ["%1-net-%2", _prefix, _networkId]
        } else {
            format ["%1-%2-%3", _prefix, round (diag_tickTime * 1000), floor random 1e9]
        };
        _object setVariable ["YAS_ironDome_uid", _uid, true];
    };
    _uid
};

YAS_fnc_ironDomeRecordEvent = {
    params ["_token", "_event"];
    if !([_token, "record-event"] call YAS_fnc_ironDomeAuthorized) exitWith {false};
    private _events = missionNamespace getVariable ["YAS_IRONDOME_ENGAGEMENT_EVENTS", []];
    _events pushBack _event;
    if ((count _events) > YAS_IRONDOME_EVENT_LIMIT) then {
        _events deleteRange [0, (count _events) - YAS_IRONDOME_EVENT_LIMIT];
    };
    missionNamespace setVariable ["YAS_IRONDOME_ENGAGEMENT_EVENTS", _events, true];
    true
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
    (missionNamespace getVariable ["YAS_ironDomeEngagementRadius", 1000]) max 0
};

YAS_fnc_ironDomeGetAssignmentWindow = {
    (missionNamespace getVariable ["YAS_IRONDOME_ASSIGNMENT_WINDOW", 0.5]) max 0
};

YAS_fnc_ironDomeCleanupRegistry = {
    params ["_token"];
    if !([_token, "cleanup-registry"] call YAS_fnc_ironDomeAuthorized) exitWith {[]};

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
    params ["_token"];
    if !([_token, "refresh-registry"] call YAS_fnc_ironDomeAuthorized) exitWith {[]};

    if (isNil "YAS_IRONDOME_REGISTRY") then {
        YAS_IRONDOME_REGISTRY = [];
    };

    {
        if (!isNull _x && {_x isKindOf YAS_IRONDOME_BOX_CLASS}) then {
            YAS_IRONDOME_REGISTRY pushBackUnique _x;
        };
    } forEach (entities YAS_IRONDOME_BOX_CLASS);

    [_token] call YAS_fnc_ironDomeCleanupRegistry
};

YAS_fnc_ironDomeRegisterBox = {
    params [["_box", objNull, [objNull]], ["_token", "", [""]]];

    if !([_token, "register-box"] call YAS_fnc_ironDomeAuthorized) exitWith {false};
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
    params [["_launcher", objNull, [objNull]], ["_token", "", [""]]];

    if !([_token, "play-launch-sound"] call YAS_fnc_ironDomeAuthorized) exitWith {false};
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
        ["_ammo", "", [""]],
        ["_impactPos", [], [[]]],
        ["_shellOwner", -1, [0]],
        ["_token", "", [""]]
    ];

    if !([_token, "create-task"] call YAS_fnc_ironDomeAuthorized) exitWith {createHashMap};
    if (isNull _shell) exitWith {createHashMap};

    private _existing = [_shell] call YAS_fnc_ironDomeFindTaskForShell;
    if ((count _existing) > 0) exitWith {_existing};

    private _task = createHashMapFromArray [
        ["shell", _shell],
        ["source", _source],
        ["ammo", _ammo],
        ["impactPos", _impactPos],
        ["shellOwner", _shellOwner],
        ["createdAt", serverTime],
        ["attempts", 0],
        ["nextAttemptAt", serverTime],
        ["assignedLauncher", objNull],
        ["scheduledLaunchAt", -1],
        ["waitingForCoverageLogged", false],
        ["waitingForSlotLogged", false],
        ["activeAttempts", 0],
        ["shellUid", [_shell, "shell", _token] call YAS_fnc_ironDomeObjectUid]
    ];

    YAS_IRONDOME_TASKS pushBack _task;
    _task
};

YAS_fnc_ironDomeCleanupTasks = {
    params ["_token"];
    if !([_token, "cleanup-tasks"] call YAS_fnc_ironDomeAuthorized) exitWith {[]};

    private _keep = [];

    {
        private _task = _x;
        private _shell = _task getOrDefault ["shell", objNull];

        private _exhausted = (_task getOrDefault ["attempts", 0]) >= YAS_IRONDOME_MAX_SHOTS
            && {(_task getOrDefault ["activeAttempts", 0]) <= 0};
        private _activeAttempts = _task getOrDefault ["activeAttempts", 0];
        if (_activeAttempts > 0 || {!isNull _shell && {!(_shell getVariable ["YAS_ironDome_hit", false])} && {!_exhausted}}) then {
            _keep pushBack _task;
        } else {
            if (!isNull _shell) then {
                _shell setVariable ["YAS_ironDome_controllerActive", false];
            };
            if (_exhausted) then {
                [_token, [
                    _task getOrDefault ["shellUid", ""], "", "", "exhausted",
                    _task getOrDefault ["attempts", 0], -1, diag_tickTime,
                    _task getOrDefault ["ammo", ""], true, true
                ]] call YAS_fnc_ironDomeRecordEvent;
            };
        };
    } forEach YAS_IRONDOME_TASKS;

    YAS_IRONDOME_TASKS = _keep;
    YAS_IRONDOME_TASKS
};

YAS_fnc_ironDomeGetLauncherCandidatesForTask = {
    params [
        ["_task", createHashMap],
        ["_launchAvailability", [], [[]]],
        ["_token", "", [""]]
    ];

    if !([_token, "launcher-candidates"] call YAS_fnc_ironDomeAuthorized) exitWith {[]};
    if ((count _task) <= 0) exitWith {[]};

    private _shell = _task getOrDefault ["shell", objNull];
    if (isNull _shell) exitWith {[]};

    private _impactPos = _task getOrDefault ["impactPos", []];
    if !(_impactPos isEqualType [] && {(count _impactPos) >= 2}) exitWith {[]};
    private _radius = call YAS_fnc_ironDomeGetEngagementRadius;
    private _candidates = [];

    {
        private _launcher = _x;
        private _impactDistance = _launcher distance2D _impactPos;
        if (_impactDistance <= _radius) then {
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

            _candidates pushBack [_launcher, _candidateLaunchAt, _impactDistance];
        };
    } forEach ([_token] call YAS_fnc_ironDomeRefreshRegistry);

    _candidates
};

YAS_fnc_ironDomeSelectLauncherForTask = {
    params [
        ["_task", createHashMap],
        ["_launchAvailability", [], [[]]],
        ["_token", "", [""]]
    ];

    if !([_token, "select-launcher"] call YAS_fnc_ironDomeAuthorized) exitWith {[objNull, -1, -1, 0]};
    private _candidates = [_task, _launchAvailability, _token] call YAS_fnc_ironDomeGetLauncherCandidatesForTask;
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
    params ["_token"];
    if !([_token, "assign-tasks"] call YAS_fnc_ironDomeAuthorized) exitWith {false};

    private _launchAvailability = [];
    {
        _launchAvailability pushBack [
            _x,
            ((_x getVariable ["YAS_ironDome_nextLaunchAt", -1]) max serverTime)
        ];
        _x setVariable ["YAS_ironDome_taskedShell", objNull, true];
    } forEach ([_token] call YAS_fnc_ironDomeRefreshRegistry);

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
            private _selection = [_task, _launchAvailability, _token] call YAS_fnc_ironDomeSelectLauncherForTask;
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
    params ["_token"];
    if !([_token, "execute-tasks"] call YAS_fnc_ironDomeAuthorized) exitWith {false};

    {
        private _task = _x;
        private _shell = _task getOrDefault ["shell", objNull];
        private _launcher = _task getOrDefault ["assignedLauncher", objNull];
        private _scheduledLaunchAt = _task getOrDefault ["scheduledLaunchAt", -1];
        private _impactPos = _task getOrDefault ["impactPos", []];

        if (!isNull _launcher && {_scheduledLaunchAt <= serverTime}) then {
            _task set ["assignedLauncher", objNull];
            _task set ["scheduledLaunchAt", -1];

            if (
                isNull _shell
                || {_shell getVariable ["YAS_ironDome_hit", false]}
                || {!alive _launcher}
                || {!(_launcher getVariable ["YAS_ironDome_enabled", true])}
                || {(_launcher distance2D _impactPos) > (call YAS_fnc_ironDomeGetEngagementRadius)}
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
                        round (_launcher distance2D _impactPos),
                        round (call YAS_fnc_ironDomeGetEngagementRadius)
                    ]
                ] call YAS_fnc_ironDomeLog;

                private _missile = [_launcher, _shell, _token] call YAS_fnc_ironDomeSpawnMissile;
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
                    _task set ["activeAttempts", (_task getOrDefault ["activeAttempts", 0]) + 1];
                    [_token, [
                        _task getOrDefault ["shellUid", ""],
                        [_launcher, "launcher", _token] call YAS_fnc_ironDomeObjectUid,
                        [_missile, "interceptor", _token] call YAS_fnc_ironDomeObjectUid,
                        "launched", _attempt, _launcher distance _shell, diag_tickTime,
                        _task getOrDefault ["ammo", ""], local _shell, local _missile
                    ]] call YAS_fnc_ironDomeRecordEvent;
                    [_launcher, _missile, _shell, _task getOrDefault ["source", objNull], _attempt, _task, _token] spawn YAS_fnc_ironDomeMonitorIntercept;
                };
            };
        };
    } forEach YAS_IRONDOME_TASKS;

    true
};

YAS_fnc_ironDomeEnsureDispatcher = {
    params ["_token"];
    if !([_token, "ensure-dispatcher"] call YAS_fnc_ironDomeAuthorized) exitWith {false};

    if (!isNil "YAS_IRONDOME_DISPATCHER_HANDLE" && {!scriptDone YAS_IRONDOME_DISPATCHER_HANDLE}) exitWith {true};

    YAS_IRONDOME_DISPATCHER_HANDLE = [_token] spawn {
        params ["_token"];
        while {YAS_IRONDOME_SERVER_READY} do {
            [_token] call YAS_fnc_ironDomeRefreshRegistry;
            [_token] call YAS_fnc_ironDomeCleanupTasks;

            if !((count YAS_IRONDOME_TASKS) isEqualTo 0) then {
                [_token] call YAS_fnc_ironDomeAssignTasks;
                [_token] call YAS_fnc_ironDomeExecuteAssignedTasks;
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
        ["_shell", objNull, [objNull]],
        ["_token", "", [""]]
    ];

    if !([_token, "spawn-missile"] call YAS_fnc_ironDomeAuthorized) exitWith {objNull};
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
    [_launcher, "launcher", _token] call YAS_fnc_ironDomeObjectUid;
    [_missile, "interceptor", _token] call YAS_fnc_ironDomeObjectUid;

    [_launcher, _token] call YAS_fnc_ironDomePlayLaunchSound;

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

YAS_fnc_ironDomeNeutralizeAckServer = {
    if (!isServer) exitWith {false};
    params ["_shellUid", "_ok", "_wasLocal"];
    private _task = createHashMap;
    {
        if ((_x getOrDefault ["shellUid", ""]) isEqualTo _shellUid) exitWith {_task = _x;};
    } forEach YAS_IRONDOME_TASKS;
    if ((count _task) <= 0) exitWith {false};
    private _expectedOwner = _task getOrDefault ["shellOwner", -1];
    private _accepted = remoteExecutedOwner isEqualTo _expectedOwner && {_ok} && {_wasLocal};
    _task set ["neutralized", _accepted];
    _task set ["neutralizeAck", true];
    if (!_accepted) then {
        private _token = localNamespace getVariable ["YAS_IRONDOME_TOKEN", ""];
        [_token, "shell-neutralize", "owner-rejected", remoteExecutedOwner, format ["expected=%1|shell=%2", _expectedOwner, _shellUid]] call YAS_fnc_ironDomeAudit;
    };
    _accepted
};

YAS_fnc_ironDomeNeutralizeShellLocal = {
    params ["_shell", "_shellUid"];
    private _wasLocal = !isNull _shell && {local _shell};
    private _ok = _wasLocal;
    if (_ok) then {
        _shell setVariable ["YAS_ironDome_controllerActive", false];
        deleteVehicle _shell;
    };
    [_shellUid, _ok, _wasLocal] remoteExecCall ["YAS_fnc_ironDomeNeutralizeAckServer", 2];
};

YAS_fnc_ironDomeMonitorIntercept = {
    params [
        ["_launcher", objNull, [objNull]],
        ["_missile", objNull, [objNull]],
        ["_shell", objNull, [objNull]],
        ["_source", objNull, [objNull]],
        ["_attemptIndex", 1, [0]],
        ["_task", createHashMap],
        ["_token", "", [""]]
    ];

    if !([_token, "monitor-intercept"] call YAS_fnc_ironDomeAuthorized) exitWith {false};
    if (isNull _launcher || {isNull _missile} || {isNull _shell}) exitWith {
        _task set ["activeAttempts", ((_task getOrDefault ["activeAttempts", 1]) - 1) max 0];
        [_token, [
            _task getOrDefault ["shellUid", ""],
            [_launcher, "launcher", _token] call YAS_fnc_ironDomeObjectUid,
            [_missile, "interceptor", _token] call YAS_fnc_ironDomeObjectUid,
            "monitor-input-null", _attemptIndex, -1, diag_tickTime,
            _task getOrDefault ["ammo", ""], !isNull _shell && {local _shell},
            !isNull _missile && {local _missile}
        ]] call YAS_fnc_ironDomeRecordEvent;
        false
    };

    private _launcherUid = [_launcher, "launcher", _token] call YAS_fnc_ironDomeObjectUid;
    private _missileUid = [_missile, "interceptor", _token] call YAS_fnc_ironDomeObjectUid;
    private _shellUid = [_shell, "shell", _token] call YAS_fnc_ironDomeObjectUid;
    private _ammo = _task getOrDefault ["ammo", ""];
    private _shellLocal = local _shell;
    private _missileLocal = local _missile;
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
        _task set ["activeAttempts", ((_task getOrDefault ["activeAttempts", 1]) - 1) max 0];
        [_token, [
            _shellUid, _launcherUid, _missileUid, _endReason, _attemptIndex,
            _closestDistance, diag_tickTime, _ammo, _shellLocal, _missileLocal
        ]] call YAS_fnc_ironDomeRecordEvent;
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

    private _interceptPosATL = getPosATL _shell;
    _shell setVariable ["YAS_ironDome_hit", true, true];
    private _effectOwner = if (isServer && {local _shell}) then {2} else {owner _shell};
    _task set ["shellOwner", _effectOwner];
    _task set ["neutralized", false];
    _task set ["neutralizeAck", false];
    if (_effectOwner isEqualTo 2 && {local _shell}) then {
        // The authoritative worker already owns this shell.  A remoteExec to
        // the server does not carry a client-owner identity, so commit the
        // owner-local delete directly and reserve the authenticated ack path
        // for genuinely remote owners.
        _shell setVariable ["YAS_ironDome_controllerActive", false];
        deleteVehicle _shell;
        _task set ["neutralized", true];
        _task set ["neutralizeAck", true];
    } else {
        [_shell, _shellUid] remoteExecCall ["YAS_fnc_ironDomeNeutralizeShellLocal", _effectOwner];
    };
    private _neutralizeDeadline = diag_tickTime + 3;
    waitUntil {
        uiSleep 0.01;
        _task getOrDefault ["neutralizeAck", false] || {diag_tickTime > _neutralizeDeadline}
    };
    if !(_task getOrDefault ["neutralized", false]) exitWith {
        _task set ["activeAttempts", ((_task getOrDefault ["activeAttempts", 1]) - 1) max 0];
        [_token, [
            _shellUid, _launcherUid, _missileUid, "neutralize-failed", _attemptIndex,
            _closestDistance, diag_tickTime, _ammo, _shellLocal, _missileLocal
        ]] call YAS_fnc_ironDomeRecordEvent;
        if (!isNull _missile) then {deleteVehicle _missile;};
        false
    };

    _launcher setVariable ["YAS_ironDome_successCount", (_launcher getVariable ["YAS_ironDome_successCount", 0]) + 1, true];
    _task set ["activeAttempts", ((_task getOrDefault ["activeAttempts", 1]) - 1) max 0];
    [_token, [
        _shellUid, _launcherUid, _missileUid, "intercepted", _attemptIndex,
        _closestDistance, diag_tickTime, _ammo, _shellLocal, _missileLocal, _effectOwner
    ]] call YAS_fnc_ironDomeRecordEvent;

    private _shellPosATL = _interceptPosATL;
    "HelicopterExploSmall" createVehicle (_shellPosATL vectorAdd [0, 0, 0.1]);

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
    params ["_vehicle", "_ammo", "_shell", "_impactPos", "_shellOwner", ["_token", "", [""]]];

    if !([_token, "handle-shell-fired"] call YAS_fnc_ironDomeAuthorized) exitWith {false};
    if (isNull _shell) exitWith {false};
    if !(_impactPos isEqualType [] && {(count _impactPos) >= 2} && {(_impactPos # 0) isEqualType 0} && {(_impactPos # 1) isEqualType 0}) exitWith {false};
    if ((count _impactPos) < 3) then {
        _impactPos pushBack (getTerrainHeightASL [_impactPos # 0, _impactPos # 1, 0]);
    };

    private _registry = [_token] call YAS_fnc_ironDomeRefreshRegistry;
    if (_registry isEqualTo []) exitWith {false};

    if (_shell getVariable ["YAS_ironDome_controllerActive", false]) exitWith {false};
    _shell setVariable ["YAS_ironDome_controllerActive", true];
    _shell setVariable ["YAS_ironDome_hit", false];

    [
        format [
            "tracking shell=%1 ammo=%2 source=%3 owner=%4 impact=%5 activeOphanim=%6 radius=%7m tasking=enabled",
            _shell,
            _ammo,
            _vehicle,
            _shellOwner,
            _impactPos,
            count _registry,
            round (call YAS_fnc_ironDomeGetEngagementRadius)
        ]
    ] call YAS_fnc_ironDomeLog;

    [_shell, _vehicle, _ammo, _impactPos, _shellOwner, _token] call YAS_fnc_ironDomeCreateTask;
    [_token] call YAS_fnc_ironDomeEnsureDispatcher;
    true
};

YAS_fnc_ironDomeSubmitShellTelemetry = {
    if (!isServer) exitWith {false};
    params ["_vehicle", "_ammo", "_shell", "_impactPos"];
    private _sourceOwner = remoteExecutedOwner;
    private _token = localNamespace getVariable ["YAS_IRONDOME_TOKEN", ""];
    if (isNull _shell || {_sourceOwner <= 0} || {_sourceOwner isNotEqualTo owner _shell}) exitWith {
        [_token, "shell-telemetry", "owner-rejected", _sourceOwner, if (isNull _shell) then {"null"} else {format ["expected=%1|shell=%2", owner _shell, netId _shell]}] call YAS_fnc_ironDomeAudit;
        false
    };
    [_vehicle, _ammo, _shell, _impactPos, _sourceOwner, _token] call YAS_fnc_ironDomeHandleShellFired
};

YAS_fnc_ironDomeEnsureLocalObserver = {
    if (isNil "YAS_IRONDOME_ARTY_EH_ID") then {
        YAS_IRONDOME_ARTY_EH_ID = -1;
    };
    if (YAS_IRONDOME_ARTY_EH_ID >= 0) exitWith {true};
    YAS_IRONDOME_ARTY_EH_ID = addMissionEventHandler ["ArtilleryShellFired", {
        params ["_vehicle", "_weapon", "_ammo", "_gunner", "_instigator", "_artilleryTarget", "_targetPosition", "_shell"];
        if (isNull _shell || {!local _shell}) exitWith {};
        private _impactPos = +_targetPosition;
        if !(_impactPos isEqualType [] && {(count _impactPos) >= 2}) then {
            _impactPos = (_shell call YOSHI_predictFallTimeAndPos) # 1;
        };
        if (isServer) then {
            [_vehicle, _ammo, _shell, _impactPos, 2, localNamespace getVariable ["YAS_IRONDOME_TOKEN", ""]] call YAS_fnc_ironDomeHandleShellFired;
        } else {
            [_vehicle, _ammo, _shell, _impactPos] remoteExecCall ["YAS_fnc_ironDomeSubmitShellTelemetry", 2];
        };
    }];
    true
};

YAS_fnc_ironDomeEnsureArtilleryEH = {
    params ["_token"];
    if !([_token, "ensure-artillery-eh"] call YAS_fnc_ironDomeAuthorized) exitWith {false};
    call YAS_fnc_ironDomeEnsureLocalObserver
};

YAS_fnc_ironDomeInitServer = {
    if (!isServer) exitWith {false};
    if (YAS_IRONDOME_SERVER_READY) exitWith {true};

    YAS_IRONDOME_MANUAL_CONTROL = getNumber (configFile >> "CfgAmmo" >> YAS_IRONDOME_MISSILE_CLASS >> "manualControl");
    YAS_IRONDOME_SERVER_READY = true;
    private _token = localNamespace getVariable ["YAS_IRONDOME_TOKEN", ""];
    missionNamespace setVariable ["YAS_IRONDOME_ENGAGEMENT_EVENTS", [], true];
    missionNamespace setVariable ["YAS_IRONDOME_AUDIT", [], false];
    [_token] call YAS_fnc_ironDomeRefreshRegistry;
    [_token] call YAS_fnc_ironDomeCleanupTasks;
    [_token] call YAS_fnc_ironDomeEnsureArtilleryEH;
    [_token] call YAS_fnc_ironDomeEnsureDispatcher;

    {
        [_x, _token] call YAS_fnc_ironDomeRegisterBox;
    } forEach (entities YAS_IRONDOME_BOX_CLASS);

    if (YAS_IRONDOME_ENTITY_CREATED_EH_ID < 0) then {
        YAS_IRONDOME_ENTITY_CREATED_EH_ID = addMissionEventHandler ["EntityCreated", {
            params ["_entity"];

            if (_entity isKindOf YAS_IRONDOME_BOX_CLASS) then {
                [_entity, localNamespace getVariable ["YAS_IRONDOME_TOKEN", ""]] call YAS_fnc_ironDomeRegisterBox;
            };
        }];
    };

    [
        format [
            "Iron Dome server init complete. registeredOphanim=%1 queuedTasks=%2 manualControl=%3",
            count ([_token] call YAS_fnc_ironDomeRefreshRegistry),
            count ([_token] call YAS_fnc_ironDomeCleanupTasks),
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

// Pre-init runs on every machine; only the machine local to a new shell emits
// authenticated trajectory telemetry to the authoritative server.
call YAS_fnc_ironDomeEnsureLocalObserver;

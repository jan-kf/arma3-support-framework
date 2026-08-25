/* =========================
   YSF Task Governor v2 (SQF)
   ========================= */

/* ---------- Stages (linear) ---------- */
#define YSF_STAGE_INIT     0
#define YSF_STAGE_START    1
#define YSF_STAGE_MISSION  2
#define YSF_STAGE_END      3
#define YSF_STAGE_FINALLY  4
#define YSF_STAGE_DONE     5 

/* ---------- Handler return codes (use these to avoid string typos) ---------- */
#define YSF_R_WAIT     "wait"     // keep ticking in same stage
#define YSF_R_ADVANCE  "advance"  // move to next stage
#define YSF_R_RETRY    "retry"    // soft failure, watchdog/backoff will decide
#define YSF_R_FAIL     "fail"     // hard failure → FINALLY
#define YSF_R_CANCEL   "cancel"   // cancelled → FINALLY
#define YSF_R_COMPLETE "complete" // hard success → FINALLY

/* ---------- Manager registry ---------- */
if (isNil { missionNamespace getVariable "YSF_task_managers" }) then {
  missionNamespace setVariable ["YSF_task_managers", createHashMap];
};

/* ---------- Small utility helpers ---------- */
YSF_now = { diag_tickTime };

YSF_sigVeh = {
  params ["_v"];
  private _p = getPosWorld _v;
  private _s = speed _v;
  private _w = count waypoints (group _v);
  private _d = getDir _v;
  // Keep it short & cheap to compare
  str [round (_p#0), round (_p#1), round (_p#2), round _s, _w, round _d]
};

/* ---------- Task object ----------

Shape (HashMap):
  id:        string  unique task id
  gen:       number  generation/random for tracing
  veh:       object  vehicle this task manages
  type:      string  task kind for your own routing/logging
  handlers:  hashMap { "init"|"start"|"mission"|"end"|"finally" => code }
  fnParams:      any     opaque payload for handlers
  state:     string  "running"|"failed"|"cancelled"|"complete"
  stage:     number  0..5 (see defines)
  t0:        number  created time
  tStage:    number  last time we changed stage / saw progress
  tries:     number  consecutive stale ticks since last progress
  maxTries:  number
  retryTimeout: number  seconds of no-signal-change before tries++
  lastLocStat: string  previous signal snapshot
  currentLocStat:     string  latest signal snapshot
  status:    string  optional human label (e.g., "complete"|"failed")
*/
YSF_taskNew = {
  params ["_type","_veh","_handlers","_fnParams",["_retryTimeout",10],["_maxTries",3]];
  private _id  = format["T%1", round (random 1e9)];
  private _gen = floor (random 1e6);
  private _t   = createHashMap;

  _t set ["id",_id];
  _t set ["gen",_gen];
  _t set ["veh",_veh];
  _t set ["type",_type];
  _t set ["handlers",_handlers];
  _t set ["fnParams",_fnParams];

  _t set ["state","running"];
  _t set ["stage",YSF_STAGE_INIT];
  _t set ["t0",call YSF_now];
  _t set ["tStage",call YSF_now];

  _t set ["tries",0];
  _t set ["maxTries",_maxTries];
  _t set ["retryTimeout",_retryTimeout];
  _t set ["lastLocStat",""];
  _t set ["currentLocStat",""];
  _t set ["finalizing",false];
  _t set ["finalized",false];
  _t
};

/* ---------- Registry helpers ---------- */
YSF__mgr = { missionNamespace getVariable "YSF_task_managers" };

YSF_taskGet = {
  params ["_veh"];
  (call YSF__mgr) getOrDefault [str _veh, objNull]
};

YSF_taskAssign = {
  params ["_veh","_task"];
  if (!isServer || {isNull _veh} || {typeName _task isNotEqualTo "HASHMAP"}) exitWith {false};

  private _existing = (call YSF__mgr) getOrDefault [str _veh, objNull];
  private _existingEnabled = typeName _existing isEqualTo "HASHMAP" && {_existing getOrDefault ["enabled", false]};
  private _existingTask = if (_existingEnabled) then {_existing getOrDefault ["task", objNull]} else {objNull};
  private _existingFinalizing = typeName _existingTask isEqualTo "HASHMAP" && {_existingTask getOrDefault ["finalizing", false]};
  if (_existingEnabled && {!_existingFinalizing}) exitWith {false};

  format ["[YSF_Governor] Assigning task %1 to vehicle %2", (_task get "id"), _veh] call YSF_fnc_debugMsg;
  private _rec = createHashMap;
  _rec set ["veh",_veh];
  _rec set ["task",_task];
  _rec set ["enabled",true];
  _rec set ["lastTick",0];
  _rec set ["tickInterval",0.5];  
  (call YSF__mgr) set [str _veh, _rec];
  _task
};

YSF_taskAssignRemote = {
  params ["_veh","_task"];
  if (isNull _veh) exitWith {false};
  if (isNil "_task") exitWith {false};

  private _taskId = if (typeName _task isEqualTo "HASHMAP") then {
    _task getOrDefault ["id", str diag_tickTime]
  } else {
    str diag_tickTime
  };

  [
    "YSF_taskAssign",
    [_veh, _task],
    format ["YSF_TASK_ASSIGN_%1_%2", netId _veh, _taskId],
    5
  ] call YCD_fnc_runOnServerOnce;
};

YSF_taskCancel = {
  params ["_veh"];
  private _rec  = (call YSF__mgr) getOrDefault [str _veh, objNull];
  if (typeName _rec isNotEqualTo "HASHMAP" || {!(_rec getOrDefault ["enabled", false])}) exitWith {false};
  private _task = _rec getOrDefault ["task", objNull];
  if (typeName _task isNotEqualTo "HASHMAP" || {(_task getOrDefault ["state", ""]) isNotEqualTo "running"}) exitWith {false};
  [_task,"cancelled"] call YSF__terminate;
  true
};

/* ---------- Stage/State internals ---------- */
YSF_nextStage = {
  params ["_task"];
  private _s = _task get "stage";
  if (_s < YSF_STAGE_FINALLY) then {
    _task set ["stage",_s+1];
    _task set ["tStage",call YSF_now];
    _task set ["tries",0];
  };
};

YSF__normalizeResult = {
  // Accept nil handlers or odd returns gracefully → treat as wait
  params ["_r"];
  if (isNil "_r") exitWith {YSF_R_WAIT};
  if (_r in [YSF_R_WAIT, YSF_R_ADVANCE, YSF_R_RETRY, YSF_R_FAIL, YSF_R_CANCEL, YSF_R_COMPLETE]) exitWith {_r};
  // Anything else is “wait”
  YSF_R_WAIT
};

YSF_runStage = {
  // Calls the current stage handler with: [veh, task, fnParams]
  params ["_task"];
  private _handlers = _task get "handlers";
  private _stage    = _task get "stage";
  private _veh      = _task get "veh";
  private _fnParams     = _task get "fnParams";

  private _fn = switch (_stage) do {
    case YSF_STAGE_INIT:     { _handlers getOrDefault ["init",{}] };
    case YSF_STAGE_START:    { _handlers getOrDefault ["start",{}] };
    case YSF_STAGE_MISSION:  { _handlers getOrDefault ["mission",{}] };
    case YSF_STAGE_END:      { _handlers getOrDefault ["end",{}] };
    case YSF_STAGE_FINALLY:  { _handlers getOrDefault ["finally",{}] };
    default { {} };
  };

  private _r = [_veh,_task,_fnParams] call _fn;
  [_r] call YSF__normalizeResult
};

YSF__terminate = {
  // Enter FINALLY and then DONE
  params ["_task","_statusText"];
  _task set ["stage",YSF_STAGE_FINALLY];
  _task set ["state",_statusText];  // "failed" | "cancelled" | "complete"
  _task set ["tStage",call YSF_now];
  _task set ["tries",0];
};

YSF__finalize = {
  params ["_task", "_rec"];
  if (_task getOrDefault ["finalized", false]) exitWith {false};

  if ((_task getOrDefault ["state", "running"]) isEqualTo "running") then {
    _task set ["state", "complete"];
  };
  _task set ["finalizing",true];
  private _result = [_task] call YSF_runStage;
  _task set ["finalizing",false];
  _task set ["finalized",true];
  _task set ["stage",YSF_STAGE_DONE];
  _task set ["status",_task getOrDefault ["state", "complete"]];

  private _currentTask = _rec getOrDefault ["task", objNull];
  private _sameGeneration = typeName _currentTask isEqualTo "HASHMAP"
    && {(_currentTask get "id") isEqualTo (_task get "id")}
    && {(_currentTask get "gen") isEqualTo (_task get "gen")};
  if (_sameGeneration) then {_rec set ["enabled",false];};
  true
};

/* ---------- The core tick (called by governor) ---------- */
YSF_taskTick = {
  params ["_veh"];

  private _rec  = (call YSF__mgr) getOrDefault [str _veh, objNull];
  if (typeName _rec isNotEqualTo "HASHMAP") exitWith {false};
  if !(_rec getOrDefault ["enabled", false]) exitWith {false};

  private _task = _rec getOrDefault ["task", objNull];
  if (typeName _task isNotEqualTo "HASHMAP") exitWith {false};

  if (!(alive _veh) && {(_task getOrDefault ["state", "running"]) isEqualTo "running"}) then {
    [_task,"failed"] call YSF__terminate;
  };

  if ((_task getOrDefault ["stage", YSF_STAGE_DONE]) isEqualTo YSF_STAGE_FINALLY) exitWith {
    [_task, _rec] call YSF__finalize
  };

  if ((_task getOrDefault ["state", "running"]) isNotEqualTo "running") exitWith {
    [_task, _task getOrDefault ["state", "failed"]] call YSF__terminate;
    [_task, _rec] call YSF__finalize
  };

  private _sig = [_veh] call YSF_sigVeh;
  _task set ["currentLocStat",_sig];
  if ((_task get "lastLocStat") isEqualTo "") then {
    _task set ["lastLocStat",_sig];
  };

  private _stale = ((_task get "lastLocStat") isEqualTo (_task get "currentLocStat"));
  private _dt    = (call YSF_now) - (_task get "tStage");
  if (_stale && {_dt > (_task get "retryTimeout")}) then {
    _task set ["tries", (_task get "tries") + 1];
  };

  private _r = [_task] call YSF_runStage;
  switch (_r) do {
    case YSF_R_ADVANCE: {
      [_task] call YSF_nextStage;
    };
    case YSF_R_RETRY: {
      private _tr = _task get "tries";
      if (_tr >= (_task get "maxTries")) then {
        [_task,"failed"] call YSF__terminate;
      } else {
        _task set ["tStage",call YSF_now];  
      };
    };
    case YSF_R_FAIL: {
      [_task,"failed"] call YSF__terminate;
    };
    case YSF_R_CANCEL: {
      [_task,"cancelled"] call YSF__terminate;
    };
    case YSF_R_COMPLETE: {
      [_task,"complete"] call YSF__terminate;
    };
    default {
      // implied YSF_R_WAIT
    };
  };

  if !((_task get "currentLocStat") isEqualTo (_task get "lastLocStat")) then {
    _task set ["lastLocStat", _task get "currentLocStat"];
    _task set ["tStage",call YSF_now];
    _task set ["tries",0];
  };
};

/* ---------- Governor loop ---------- */
YSF_governorPFH = missionNamespace getVariable ["YSF_governorPFH",-1];

YSF_governorHandle = {
  private _m = call YSF__mgr;
  {
    private _rec = _y;
    if (!isNil "_rec") then {
      private _veh = _rec get "veh";
      if (_rec getOrDefault ["enabled", false]) then {
        private _now = call YSF_now;
        if (isNull _veh) then {
          private _task = _rec getOrDefault ["task", objNull];
          if (typeName _task isEqualTo "HASHMAP") then {
            [_task,"failed"] call YSF__terminate;
            [_task,_rec] call YSF__finalize;
          };
        } else {
          if ((_now - (_rec get "lastTick")) >= (_rec get "tickInterval")) then {
            _rec set ["lastTick", _now];
            [_veh] call YSF_taskTick;
          };
        };
      };
    };
  } forEach _m;
};

YSF_governorStart = {
  params [["_pfhInterval", 1]];

  "[YSF_Governor] Starting..." call YSF_fnc_debugMsg;
  if ((missionNamespace getVariable ["YSF_governorPFH",-1]) >= 0) exitWith {"[YSF_Governor] Already running." call YSF_fnc_debugMsg;};
  private _id = [YSF_governorHandle, _pfhInterval] call CBA_fnc_addPerFrameHandler;
  "[YSF_Governor] Started" call YSF_fnc_debugMsg;

  missionNamespace setVariable ["YSF_governorPFH",_id, true];
};

YSF_governorStop = {
  private _id = missionNamespace getVariable ["YSF_governorPFH",-1];
  if (_id >= 0) then {
    [_id] call CBA_fnc_removePerFrameHandler;
    missionNamespace setVariable ["YSF_governorPFH",-1, true];
  };
};

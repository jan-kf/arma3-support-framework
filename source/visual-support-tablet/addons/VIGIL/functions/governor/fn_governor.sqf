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

#define YSF_REQUEST_REPLAY_TTL 120
#define YSF_REQUEST_AUDIT_LIMIT 128

/* ---------- Manager registry ---------- */
if (isNil { missionNamespace getVariable "YSF_task_managers" }) then {
  missionNamespace setVariable ["YSF_task_managers", createHashMap];
};
if (isNil { missionNamespace getVariable "YSF_task_request_cache" }) then {
  missionNamespace setVariable ["YSF_task_request_cache", createHashMap];
};
if (isNil { missionNamespace getVariable "YSF_task_request_audit" }) then {
  missionNamespace setVariable ["YSF_task_request_audit", []];
};
localNamespace setVariable ["YSF_task_authority_token", format ["ysf-%1-%2-%3", diag_tickTime, random 1e9, random 1e9]];

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
YSF_taskKey = {params ["_veh"]; if (isNull _veh) then {""} else {netId _veh}};

YSF_taskGet = {
  params ["_veh"];
  (call YSF__mgr) getOrDefault [[_veh] call YSF_taskKey, objNull]
};

YSF_taskAssign = {
  params ["_veh","_task", ["_authorityToken", ""]];
  private _trustedInternal = _authorityToken isEqualTo (localNamespace getVariable ["YSF_task_authority_token", "missing"]);
  if (!isServer || {remoteExecutedOwner > 2 && {!_trustedInternal}} || {isNull _veh} || {typeName _task isNotEqualTo "HASHMAP"}) exitWith {false};

  private _vehicleKey = [_veh] call YSF_taskKey;
  if (_vehicleKey isEqualTo "") exitWith {false};
  private _existing = (call YSF__mgr) getOrDefault [_vehicleKey, objNull];
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
  (call YSF__mgr) set [_vehicleKey, _rec];
  _task
};

YSF_taskAssignRemote = {
  params ["_veh","_task"];
  if (!isServer || {remoteExecutedOwner > 2}) exitWith {false};
  [_veh, _task] call YSF_taskAssign
};

YSF_taskRequestReply = {
  params ["_owner", "_requestId", "_phase", "_accepted", "_reason", ["_taskId", ""], ["_state", ""]];
  if (!isServer || {_owner <= 2}) exitWith {false};
  [_requestId, _phase, _accepted, _reason, _taskId, _state] remoteExecCall ["YSF_fnc_taskRequestResult", _owner];
  true
};

YSF_taskRequestAudit = {
  params ["_requestId", "_owner", "_taskType", "_accepted", "_reason", "_vehicle", ["_taskId", ""]];
  private _rows = missionNamespace getVariable ["YSF_task_request_audit", []];
  _rows pushBack [_requestId, _owner, _taskType, _accepted isEqualTo true, _reason, if (isNull _vehicle) then {""} else {netId _vehicle}, _taskId, serverTime];
  if ((count _rows) > YSF_REQUEST_AUDIT_LIMIT) then {
    _rows deleteRange [0, (count _rows) - YSF_REQUEST_AUDIT_LIMIT];
  };
  missionNamespace setVariable ["YSF_task_request_audit", _rows];
};

YSF_taskAssetSide = {
  params ["_vehicle"];
  private _commander = effectiveCommander _vehicle;
  if (!isNull _commander) exitWith {side group _commander};
  private _result = side _vehicle;
  if (_result isEqualTo civilian) then {
    private _sideId = getNumber (configOf _vehicle >> "side");
    _result = [east, west, independent, civilian] param [_sideId, sideUnknown];
  };
  _result
};

YSF_taskAssetAllowed = {
  params ["_requester", "_vehicle"];
  if (isNull _vehicle || {!alive _vehicle}) exitWith {[false, "invalid_asset"]};
  if ((side group _requester) isNotEqualTo ([_vehicle] call YSF_taskAssetSide)) exitWith {[false, "wrong_side"]};
  if (missionNamespace getVariable ["YSF_WHITELIST_CONFIGURED", false]) then {
    private _allowed = missionNamespace getVariable ["YSF_WHITELISTED_ASSETS", []];
    if ((_allowed findIf {(vehicle _x) isEqualTo _vehicle}) < 0) exitWith {[false, "asset_not_whitelisted"]};
  };
  [true, "accepted"]
};

YSF_taskPositionValid = {
  params ["_position"];
  _position isEqualType []
    && {count _position in [2, 3]}
    && {_position findIf {!(_x isEqualType 0)} < 0}
};

YSF_taskRequestBuild = {
  params ["_taskType", "_vehicle", "_payload"];
  if !(_payload isEqualType []) exitWith {[false, "malformed_payload", objNull]};

  private _handlers = createHashMap;
  private _fnParams = [];
  switch (_taskType) do {
    case "artillery": {
      if ((count _payload) isNotEqualTo 2) exitWith {};
      _payload params ["_positions", "_ordnance"];
      if !(_positions isEqualType [] && {count _positions > 0} && {count _positions <= 32}) exitWith {};
      if ((_positions findIf {!([_x] call YSF_taskPositionValid)}) >= 0) exitWith {};
      if !(_ordnance isEqualType "" && {_ordnance isNotEqualTo ""}) exitWith {};
      if !([_vehicle] call YSF_isArtilleryCapable) exitWith {};
      if (!((typeOf _vehicle) isEqualTo "B_Ship_MRLS_01_F") && {!(_ordnance in getArtilleryAmmo [_vehicle])}) exitWith {};
      _handlers = call YSF_handlers_artillery;
      _fnParams = [_positions, _ordnance];
    };
    case "transport": {
      if ((count _payload) isNotEqualTo 5) exitWith {};
      _payload params ["_destination", "_altitude", "_doNotClimb", "_ignoreEnemy", "_mode"];
      if !([_destination] call YSF_taskPositionValid) exitWith {};
      if !(_altitude isEqualType 0 && {_altitude >= 0} && {_altitude <= 500}) exitWith {};
      if !(_doNotClimb isEqualType false && {_ignoreEnemy isEqualType false}) exitWith {};
      if !(_mode isEqualType "" && {_mode in ["dispatch", "rtb"]}) exitWith {};
      if !(_vehicle isKindOf "Helicopter" && {(_vehicle emptyPositions "cargo") > 0} && {locked _vehicle < 2}) exitWith {};
      if (_mode isEqualTo "rtb") then {
        private _home = _vehicle getVariable ["YSF_transport_homeATL", []];
        if !([_home] call YSF_taskPositionValid) exitWith {};
        _destination = _home;
      };
      _handlers = call YSF_handlers_transport;
      _fnParams = [_destination, _altitude, _doNotClimb, _ignoreEnemy, true, _mode];
    };
    case "cas": {
      if ((count _payload) isNotEqualTo 3) exitWith {};
      _payload params ["_destination", "_altitude", "_timeLimit"];
      if !([_destination] call YSF_taskPositionValid) exitWith {};
      if !(_altitude isEqualType 0 && {_altitude >= 0} && {_altitude <= 500}) exitWith {};
      if !(_timeLimit isEqualType 0 && {_timeLimit > 0} && {_timeLimit <= 120}) exitWith {};
      if !(_vehicle isKindOf "Helicopter" && {[_vehicle] call YSF_CAS_hasLethalAmmo}) exitWith {};
      _handlers = call YSF_handlers_cas;
      _fnParams = [_destination, _altitude, _timeLimit];
    };
    default {};
  };
  if ((count _handlers) isEqualTo 0) exitWith {[false, "malformed_payload", objNull]};
  private _task = [_taskType, _vehicle, _handlers, _fnParams, 10, 3] call YSF_taskNew;
  [true, "accepted", _task]
};

YSF_taskRequestProcess = {
  params ["_requestId", "_requester", "_vehicle", "_taskType", "_payload", "_requestOwner", "_authorityToken"];
  if (!isServer || {_authorityToken isNotEqualTo (localNamespace getVariable ["YSF_task_authority_token", "missing"])}) exitWith {false};
  private _requesterClaim = _requester;
  _requester = objNull;
  if (_requesterClaim isEqualType 0 && {_requesterClaim isEqualTo _requestOwner} && {_requestOwner > 2}) then {
    private _identityDeadline = diag_tickTime + 3;
    waitUntil {
      {if (isPlayer _x && {owner _x isEqualTo _requestOwner}) exitWith {_requester = _x;};} forEach allPlayers;
      !isNull _requester || {diag_tickTime > _identityDeadline}
    };
  };
  private _finish = {
    params ["_accepted", "_reason", ["_task", objNull]];
    private _taskId = if (typeName _task isEqualTo "HASHMAP") then {_task getOrDefault ["id", ""]} else {""};
    [_requestId, _requestOwner, _taskType, _accepted, _reason, _vehicle, _taskId] call YSF_taskRequestAudit;
    [_requestOwner, _requestId, ["rejected", "accepted"] select _accepted, _accepted, _reason, _taskId] call YSF_taskRequestReply;
    if (!isNull _vehicle && {_taskType in ["transport", "cas"]}) then {
      private _status = if (_accepted) then {"accepted"} else {
        if (_reason in ["asset_busy", "duplicate"]) then {"duplicate_rejected"} else {_reason}
      };
      _vehicle setVariable [format ["YSF_%1_lastRequest", _taskType], _status, true];
    };
    _accepted
  };

  if !(_requestId isEqualType "" && {_requestId isNotEqualTo ""} && {count _requestId <= 128}) exitWith {false};
  if (_requestOwner <= 2
      || {isNull _requester}
      || {!isPlayer _requester}
      || {owner _requester isNotEqualTo _requestOwner}
      || {!(_requesterClaim isEqualType 0)}
      || {_requesterClaim isNotEqualTo _requestOwner}) exitWith {
    [false, "invalid_requester"] call _finish
  };

  private _cache = missionNamespace getVariable ["YSF_task_request_cache", createHashMap];
  private _cacheKey = format ["%1:%2", _requestOwner, _requestId];
  private _now = serverTime;
  {if ((_cache get _x) <= _now) then {_cache deleteAt _x;};} forEach keys _cache;
  if ((_cache getOrDefault [_cacheKey, 0]) > _now) exitWith {[false, "duplicate"] call _finish};
  _cache set [_cacheKey, _now + YSF_REQUEST_REPLAY_TTL];
  missionNamespace setVariable ["YSF_task_request_cache", _cache];

  if !(_taskType isEqualType "" && {_taskType in ["artillery", "transport", "cas"]}) exitWith {
    [false, "unsupported_task_type"] call _finish
  };
  if !(_payload isEqualType []) exitWith {[false, "malformed_payload"] call _finish};
  private _asset = [_requester, _vehicle] call YSF_taskAssetAllowed;
  if !(_asset # 0) exitWith {[false, _asset # 1] call _finish};

  private _existing = (call YSF__mgr) getOrDefault [[_vehicle] call YSF_taskKey, objNull];
  if (typeName _existing isEqualTo "HASHMAP" && {_existing getOrDefault ["enabled", false]}) exitWith {
    [false, "asset_busy"] call _finish
  };

  private _built = [_taskType, _vehicle, _payload] call YSF_taskRequestBuild;
  if !(_built # 0) exitWith {[false, _built # 1] call _finish};
  private _task = _built # 2;
  _task set ["serverBuilt", true];
  _task set ["requestId", _requestId];
  _task set ["requestOwner", _requestOwner];
  private _assigned = [_vehicle, _task, _authorityToken] call YSF_taskAssign;
  if (typeName _assigned isNotEqualTo "HASHMAP") exitWith {[false, "asset_busy"] call _finish};
  [true, "accepted", _task] call _finish
};

YSF_taskRequestRemote = {
  params ["_vehicle", "_taskType", "_payload"];
  if (!hasInterface || {isNull player} || {isNull _vehicle}) exitWith {false};
  private _requestId = format ["YSF_TASK_%1_%2_%3", clientOwner, floor (diag_tickTime * 1000), floor random 1000000];
  [_requestId, clientOwner, _vehicle, _taskType, _payload] remoteExecCall ["YSF_fnc_taskRequestServer", 2];
  _requestId
};

YSF_taskCancel = {
  params ["_veh"];
  private _rec  = (call YSF__mgr) getOrDefault [[_veh] call YSF_taskKey, objNull];
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

  private _requestOwner = _task getOrDefault ["requestOwner", 0];
  private _requestId = _task getOrDefault ["requestId", ""];
  if (_requestOwner > 2 && {_requestId isNotEqualTo ""}) then {
    [_requestOwner, _requestId, "terminal", true, "terminal", _task getOrDefault ["id", ""], _task getOrDefault ["state", "complete"]] call YSF_taskRequestReply;
  };

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

  private _rec  = (call YSF__mgr) getOrDefault [[_veh] call YSF_taskKey, objNull];
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

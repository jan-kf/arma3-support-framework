"""Permanent coverage for Vigil's CAS auto-engage debug-channel policy."""

from tribunal.runner.model import Scenario, ScenarioReview


SERVER_ASSERTIONS = [
    "vigil.aaeDebug.fixture",
    "vigil.aaeDebug.policy",
    "vigil.aaeDebug.cleanup",
]

CLIENT_ASSERTIONS = [
    "vigil.aaeDebug.clientDisabled",
    "vigil.aaeDebug.clientEnabled",
    "vigil.aaeDebug.clientCleanup",
]

EVIDENCE_CONTRACT = {
    "scenario": {
        "id": "vigil-debug-channel",
        "version": 1,
        "feature_family": "pontifex-vigil-cas-auto-engage-debug",
        "name": "Vigil CAS auto-engage debug-channel policy",
        "definition": {
            "kind": "controlled dedicated-multiplayer debug-routing specification",
            "reference": "source/visual-support-tablet/tests/tribunal/vigil_debug_channel.py",
            "applicability": "Arma 3 2.22 dedicated multiplayer with CORDIS, Vigil, one authenticated client, and the globally synchronized YSF_showDebugMessages setting",
            "participants": {
                "server": "invokes the exact CAS auto-engage debug adapter, records server RPT tokens, changes/restores the supported setting, and verifies client receipts",
                "client-a": "delegates the exact CORDIS presentation function while independently recording its line, setting key, and target-local gate value",
            },
        },
    },
    "knowledge_subject": {
        "key": "pontifex:vigil:cas-auto-engage-debug",
        "label": "Vigil CAS auto-engage debug channel",
        "kind": "product_behavior",
        "aliases": ["Vigil AAE debug policy"],
        "biki_context": [],
    },
    "arms": [
        {
            "key": "fixture",
            "role": "baseline",
            "description": "The exact Vigil and CORDIS debug functions exist, client-a has installed a delegating target-local observer, and the obsolete private gate is absent",
            "assertions": [SERVER_ASSERTIONS[0]],
        },
        {
            "key": "supported-setting-disabled",
            "role": "negative_control",
            "description": "The exact AAE token is still routed and logged while client-a receives the registered setting key with a false presentation gate",
            "assertions": [CLIENT_ASSERTIONS[0]],
        },
        {
            "key": "supported-setting-enabled",
            "role": "treatment",
            "description": "The exact AAE token is routed through the same registered setting key with a true target-local presentation gate",
            "assertions": [SERVER_ASSERTIONS[1], CLIENT_ASSERTIONS[1]],
        },
        {
            "key": "cleanup",
            "role": "treatment",
            "description": "The original target-local CORDIS function and initial synchronized setting value are restored",
            "assertions": [SERVER_ASSERTIONS[2], CLIENT_ASSERTIONS[2]],
        },
    ],
    "causal_relationships": [
        {
            "key": "registered-debug-setting-off-v-on",
            "relation": "CAUSAL_PAIR_WITH",
            "source": "supported-setting-enabled",
            "target": "supported-setting-disabled",
            "controlled_dimensions": [
                "same server invocation function",
                "same AAE prefix",
                "same authenticated client",
                "same delegated CORDIS presentation function",
                "same network route",
            ],
        },
    ],
    "propositions": [
        {
            "id": "pontifex:vigil:aae-debug-supported-gate",
            "text": "Vigil CAS auto-engage diagnostics always reach the dedicated-server log path and use the registered YSF_showDebugMessages setting as the sole client presentation gate; the prior always-true private gate is absent.",
            "intended_use": "primary_result",
            "assertions": SERVER_ASSERTIONS + CLIENT_ASSERTIONS,
            "rationale": "Exact unique AAE tokens are preserved in the server artifact and independently received at client-a through the real CORDIS target function. Matched false/true setting arms record the exact registered key and gate value, while cleanup restores both instrumented function and setting.",
        },
    ],
    "unresolved": [
        "Visible systemChat pixels, multiple clients/sides, client-originated AAE calls, network interruption, CBA settings UI interaction, and diagnostic rate/volume remain outside this proof."
    ],
}


SERVER_SQF = r'''
private _initialSetting = missionNamespace getVariable ["YSF_showDebugMessages", false];
missionNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_SETUP", _token, true];

private _readyDeadline = diag_tickTime + 45;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_READY", ""]) isEqualTo _token
        || {diag_tickTime > _readyDeadline}
};
private _clientReady = (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_READY", ""]) isEqualTo _token;
private _fixtureOk = _clientReady
    && {!isNil "YSF_AAE_dbg"}
    && {!isNil "YCD_fnc_debugMsg"}
    && {!isNil "YCD_fnc_showDebugLine"}
    && {isNil "YSF_AAE_DEBUG"};
["vigil.aaeDebug.fixture", _fixtureOk, format ["clientReady=%1|aae=%2|cordis=%3|show=%4|legacy=%5|initial=%6", _clientReady, !isNil "YSF_AAE_dbg", !isNil "YCD_fnc_debugMsg", !isNil "YCD_fnc_showDebugLine", missionNamespace getVariable ["YSF_AAE_DEBUG", "absent"], _initialSetting]] call _assert;

missionNamespace setVariable ["YSF_showDebugMessages", false, true];
private _disabledReadyDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_DISABLED_READY", ""]) isEqualTo _token
        || {diag_tickTime > _disabledReadyDeadline}
};
private _disabledToken = format ["TRIBUNAL_AAE_DISABLED_%1", _token];
[_disabledToken] call YSF_AAE_dbg;
private _disabledDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_DISABLED_ACK", []]) param [0, ""] isEqualTo _token
        || {diag_tickTime > _disabledDeadline}
};
private _disabledAck = missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_DISABLED_ACK", []];

missionNamespace setVariable ["YSF_showDebugMessages", true, true];
private _enabledReadyDeadline = diag_tickTime + 10;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ENABLED_READY", ""]) isEqualTo _token
        || {diag_tickTime > _enabledReadyDeadline}
};
private _enabledToken = format ["TRIBUNAL_AAE_ENABLED_%1", _token];
[_enabledToken] call YSF_AAE_dbg;
private _enabledDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ENABLED_ACK", []]) param [0, ""] isEqualTo _token
        || {diag_tickTime > _enabledDeadline}
};
private _enabledAck = missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ENABLED_ACK", []];

private _policyOk = (_disabledAck param [0, ""]) isEqualTo _token
    && {(_disabledAck param [1, ""]) isEqualTo format ["[YSF_AAE] %1", _disabledToken]}
    && {(_disabledAck param [2, ""]) isEqualTo "YSF_showDebugMessages"}
    && {!(_disabledAck param [3, true])}
    && {(_enabledAck param [0, ""]) isEqualTo _token}
    && {(_enabledAck param [1, ""]) isEqualTo format ["[YSF_AAE] %1", _enabledToken]}
    && {(_enabledAck param [2, ""]) isEqualTo "YSF_showDebugMessages"}
    && {_enabledAck param [3, false]};
["vigil.aaeDebug.policy", _policyOk, format ["disabled=%1|enabled=%2|tokens=%3", _disabledAck, _enabledAck, [_disabledToken, _enabledToken]]] call _assert;

missionNamespace setVariable ["YSF_showDebugMessages", _initialSetting, true];
missionNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_CLEANUP", _token, true];
private _cleanupDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_CLEANED", ""]) isEqualTo _token
        || {diag_tickTime > _cleanupDeadline}
};
private _clientCleaned = (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_CLEANED", ""]) isEqualTo _token;
private _cleanupOk = _clientCleaned
    && {(missionNamespace getVariable ["YSF_showDebugMessages", !_initialSetting]) isEqualTo _initialSetting};
["vigil.aaeDebug.cleanup", _cleanupOk, format ["clientCleaned=%1|setting=%2|initial=%3", _clientCleaned, missionNamespace getVariable ["YSF_showDebugMessages", "missing"], _initialSetting]] call _assert;

{
    missionNamespace setVariable [_x, nil, true];
} forEach [
    "TRIBUNAL_VIGIL_AAE_DEBUG_SETUP",
    "TRIBUNAL_VIGIL_AAE_DEBUG_READY",
    "TRIBUNAL_VIGIL_AAE_DEBUG_DISABLED_READY",
    "TRIBUNAL_VIGIL_AAE_DEBUG_DISABLED_ACK",
    "TRIBUNAL_VIGIL_AAE_DEBUG_ENABLED_READY",
    "TRIBUNAL_VIGIL_AAE_DEBUG_ENABLED_ACK",
    "TRIBUNAL_VIGIL_AAE_DEBUG_CLEANUP",
    "TRIBUNAL_VIGIL_AAE_DEBUG_CLEANED"
];
'''


CLIENT_SQF = r'''
private _setupDeadline = diag_tickTime + 45;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_SETUP", ""]) isEqualTo _token
        || {diag_tickTime > _setupDeadline}
};
private _setup = (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_SETUP", ""]) isEqualTo _token;
localNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ORIGINAL", YCD_fnc_showDebugLine];
localNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_TOKEN", _token];
localNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ROWS", []];
YCD_fnc_showDebugLine = {
    params ["_line", ["_settingName", "YSF_showDebugMessages"]];
    private _gate = missionNamespace getVariable [_settingName, false];
    private _rows = localNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ROWS", []];
    _rows pushBack [_line, _settingName, _gate];
    localNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ROWS", _rows];
    private _scenarioToken = localNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_TOKEN", ""];
    if ((_line find format ["TRIBUNAL_AAE_DISABLED_%1", _scenarioToken]) >= 0) then {
        missionNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_DISABLED_ACK", [_scenarioToken, _line, _settingName, _gate], true];
    };
    if ((_line find format ["TRIBUNAL_AAE_ENABLED_%1", _scenarioToken]) >= 0) then {
        missionNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ENABLED_ACK", [_scenarioToken, _line, _settingName, _gate], true];
    };
    [_line, _settingName] call (localNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ORIGINAL", {}]);
};
missionNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_READY", _token, true];

private _disabledReadyDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    !(missionNamespace getVariable ["YSF_showDebugMessages", true])
        || {diag_tickTime > _disabledReadyDeadline}
};
private _disabledSettingReady = !(missionNamespace getVariable ["YSF_showDebugMessages", true]);
missionNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_DISABLED_READY", _token, true];
private _disabledDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_DISABLED_ACK", []]) param [0, ""] isEqualTo _token
        || {diag_tickTime > _disabledDeadline}
};
private _disabledAck = missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_DISABLED_ACK", []];
private _disabledOk = _setup && {_disabledSettingReady}
    && {(_disabledAck param [0, ""]) isEqualTo _token}
    && {(_disabledAck param [2, ""]) isEqualTo "YSF_showDebugMessages"}
    && {!(_disabledAck param [3, true])};
["vigil.aaeDebug.clientDisabled", _disabledOk, format ["setup=%1|settingReady=%2|ack=%3", _setup, _disabledSettingReady, _disabledAck]] call _assert;

private _enabledReadyDeadline = diag_tickTime + 15;
waitUntil {
    uiSleep 0.05;
    missionNamespace getVariable ["YSF_showDebugMessages", false]
        || {diag_tickTime > _enabledReadyDeadline}
};
private _enabledSettingReady = missionNamespace getVariable ["YSF_showDebugMessages", false];
missionNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ENABLED_READY", _token, true];
private _enabledDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ENABLED_ACK", []]) param [0, ""] isEqualTo _token
        || {diag_tickTime > _enabledDeadline}
};
private _enabledAck = missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ENABLED_ACK", []];
private _enabledOk = _enabledSettingReady
    && {(_enabledAck param [0, ""]) isEqualTo _token}
    && {(_enabledAck param [2, ""]) isEqualTo "YSF_showDebugMessages"}
    && {_enabledAck param [3, false]};
["vigil.aaeDebug.clientEnabled", _enabledOk, format ["settingReady=%1|ack=%2|rows=%3", _enabledSettingReady, _enabledAck, localNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ROWS", []]]] call _assert;

private _cleanupDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_CLEANUP", ""]) isEqualTo _token
        || {diag_tickTime > _cleanupDeadline}
};
YCD_fnc_showDebugLine = localNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ORIGINAL", YCD_fnc_showDebugLine];
localNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ORIGINAL", nil];
localNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_TOKEN", nil];
localNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_ROWS", nil];
missionNamespace setVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_CLEANED", _token, true];
private _cleanupOk = (missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_CLEANUP", ""]) isEqualTo _token
    && {isNil {localNamespace getVariable "TRIBUNAL_VIGIL_AAE_DEBUG_ORIGINAL"}}
    && {isNil {localNamespace getVariable "TRIBUNAL_VIGIL_AAE_DEBUG_TOKEN"}}
    && {isNil {localNamespace getVariable "TRIBUNAL_VIGIL_AAE_DEBUG_ROWS"}};
["vigil.aaeDebug.clientCleanup", _cleanupOk, format ["cleanupSignal=%1", missionNamespace getVariable ["TRIBUNAL_VIGIL_AAE_DEBUG_CLEANUP", ""]]] call _assert;
'''


TRIBUNAL_SCENARIO = Scenario(
    identifier="vigil-debug-channel",
    tier="gameplay",
    server_expected=frozenset(SERVER_ASSERTIONS),
    client_expected=frozenset(CLIENT_ASSERTIONS),
    server_sqf=SERVER_SQF,
    client_sqf=CLIENT_SQF,
    metadata={"product": "visual-support-tablet", "feature": "cas-auto-engage-debug-channel"},
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="CAS auto-engage diagnostics always use CORDIS server logging and use only Vigil's registered YSF_showDebugMessages setting to gate client presentation.",
        outcome="REFINE BEFORE PERMANENT COVERAGE",
        rationale="The former private pre-init variable was hardcoded true and bypassed Vigil's supported debug setting. Matched false/true setting arms now prove the exact registered gate at the target client while unique tokens remain in the server evidence artifact.",
        dependencies=("CORDIS debug adapter", "Vigil synchronized debug setting", "one authenticated client"),
        evidence_types=frozenset({"server-log-token", "target-local-observer", "setting-gate", "causal-pair", "replication", "cleanup"}),
        locality_requirements="The dedicated server invokes and logs the exact AAE adapter. Client-a temporarily delegates the real CORDIS target function and records the exact setting key and local gate before restoring it. Other clients and client-originated calls are unclaimed.",
    ),
    evidence_contract=EVIDENCE_CONTRACT,
)

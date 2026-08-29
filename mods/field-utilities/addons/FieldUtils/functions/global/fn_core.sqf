/*
 I have given you a command. 
 Be strong and brave, 
 do not be afraid nor dismayed. 
 I, the Lord, your God, will be with you wherever you go.
(Joshua 1:9)
*/

YOSHI_callOnce = {
    params ["_params", "_function", "_target", "_key"];
    if (isNil "_target") exitWith {};
    if (isNull _target) exitWith {};
    if !(_key isEqualType "") exitWith {};

    private _isCalled = _target getVariable [_key, false];
    if (!_isCalled) then {
        _params call _function;
        // Keep ACE action dedupe local to each client; making this public causes the
        // first machine that runs it to block every other client from adding the action.
        _target setVariable [_key, true];
    };
};

YOSHI_addActionToObjectForEveryClient = {
    params ["_name", "_obj", "_action", ["_isSelf", 0], ["_path", ["ACE_SelfActions"]]];
    [[[_obj, _isSelf, _path, _action], ace_interact_menu_fnc_addActionToObject, _obj, _name], YOSHI_callOnce] remoteExec ["call", 0];
};

YFU_fnc_debugMsg = {
    params ["_msg"];
    [_msg, "YFU", "YFU_showDebugMessages"] call YCD_fnc_debugMsg;
};

YFU_fnc_emitSideChat = {
    params ["_speaker", "_message", ["_targets", 0], ["_onceKey", ""], ["_ttl", 3]];
    [_speaker, _message, _targets, _onceKey, _ttl, "YFU_playSideMessages"] call YCD_fnc_emitSideChat;
};

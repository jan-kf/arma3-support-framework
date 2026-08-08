YOSHI_numToTextArray = {
    params ["_number"];

    if (_number < 0 || {_number > 199}) exitWith {["error"]};
    if (_number == 0) exitWith {[]};

    private _ones = ["zero", "one", "two", "three", "four", "five", "six", "seven", "eight", "nine"];
    private _teens = ["ten", "eleven", "twelve", "thirteen", "fourteen", "fifteen", "sixteen", "seventeen", "eighteen", "nineteen"];
    private _tens = ["", "", "twenty", "thirty", "forty", "fifty", "sixty", "seventy", "eighty", "ninety"];

    private _twoDigitToText = {
        params ["_n"];

        if (_n < 10) exitWith {[_ones select _n]};
        if (_n < 20) exitWith {[_teens select (_n - 10)]};

        private _t = floor (_n / 10);
        private _o = _n mod 10;

        if (_o == 0) exitWith {[_tens select _t]};

        [_tens select _t, _ones select _o]
    };

    if (_number < 100) exitWith {
        [_number] call _twoDigitToText
    };

    private _remainder = _number - 100;
    private _result = ["one_hundred"];
    if (_remainder > 0) then {
        _result append ([_remainder] call _twoDigitToText);
    };

    _result
};

YAS_fnc_notifyCurator = {
    params ["_msg", ["_title", "AdvSys Notification"], ["_duration", 5], ["_targets", 0], ["_onceKey", ""], ["_ttl", 3]];
    [_msg, _title, _duration, _targets, _onceKey, _ttl] call YCD_fnc_notifyCurator;
};

YAS_fnc_debugMsg = {
    params ["_msg"];
    [_msg, "YAS", "YAS_showDebugMessages"] call YCD_fnc_debugMsg;
};

YAS_fnc_emitSideRadio = {
    params ["_speaker", "_message", ["_targets", 0], ["_onceKey", ""], ["_ttl", 3]];
    [_speaker, _message, _targets, _onceKey, _ttl, "YAS_playRadioMessages"] call YCD_fnc_emitSideRadio;
};

"""Generic mission-local locality evidence helpers."""

from __future__ import annotations


def locality_fixture_sqf() -> str:
    """Return SQF helpers that record and verify object ownership transitions."""

    return r'''
TRIBUNAL_fnc_localityRecord = {
    params ["_object", "_expectedMachine"];
    private _machine = missionNamespace getVariable ["TRIBUNAL_MACHINE_IDENTITY", if (isServer) then {"server"} else {"client-unknown"}];
    private _record = [diag_tickTime, netId _object, _expectedMachine, _machine, owner _object, local _object, isNull _object];
    private _records = missionNamespace getVariable ["TRIBUNAL_LOCALITY_RECORDS", []];
    _records pushBack _record;
    missionNamespace setVariable ["TRIBUNAL_LOCALITY_RECORDS", _records];
    diag_log format ["TRIBUNAL_LOCALITY|RECORD|object=%1|expected=%2|machine=%3|owner=%4|local=%5|null=%6", netId _object, _expectedMachine, _machine, owner _object, local _object, isNull _object];
    _record
};
TRIBUNAL_fnc_waitForLocality = {
    params ["_object", "_expectedOwner", "_expectedLocal", ["_timeout", 10]];
    private _deadline = diag_tickTime + _timeout;
    private _ownerMatches = { _expectedOwner < 0 || {(owner _object) isEqualTo _expectedOwner} };
    waitUntil { uiSleep 0.02; isNull _object || {call _ownerMatches && {(local _object) isEqualTo _expectedLocal}} || {diag_tickTime > _deadline} };
    private _ok = !isNull _object && {call _ownerMatches} && {(local _object) isEqualTo _expectedLocal};
    diag_log format ["TRIBUNAL_LOCALITY|WAIT|object=%1|expectedOwner=%2|observedOwner=%3|expectedLocal=%4|observedLocal=%5|ok=%6", netId _object, _expectedOwner, owner _object, _expectedLocal, local _object, _ok];
    _ok
};
'''

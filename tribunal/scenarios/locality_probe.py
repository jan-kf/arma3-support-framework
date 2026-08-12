"""Runtime proof that declared server/client ownership is actually achieved."""

from tribunal.locality import locality_fixture_sqf
from tribunal.runner.model import Scenario


TRIBUNAL_SCENARIO = Scenario(
    identifier="locality-probe",
    tier="capability",
    server_expected=frozenset({
        "tribunal.locality.serverInitial",
        "tribunal.locality.clientTransfer",
        "tribunal.locality.remoteExactlyOnce",
        "tribunal.locality.serverRestored",
    }),
    client_expected=frozenset({
        "tribunal.locality.clientOwned",
        "tribunal.locality.executionMachine",
    }),
    server_sqf=locality_fixture_sqf() + r'''
missionNamespace setVariable ["TRIBUNAL_LOCALITY_ACKS", []];
TRIBUNAL_fnc_localityClientAck = {
    params ["_receivedToken", "_objectId", "_clientIdentityOwner", "_objectOwnerDiagnostic"];
    private _acks = missionNamespace getVariable ["TRIBUNAL_LOCALITY_ACKS", []];
    _acks pushBack [_receivedToken, _objectId, _clientIdentityOwner, _objectOwnerDiagnostic, remoteExecutedOwner];
    missionNamespace setVariable ["TRIBUNAL_LOCALITY_ACKS", _acks];
};
private _localityObject = "C_Offroad_01_F" createVehicle ((getPosATL _player) vectorAdd [12, 0, 0]);
private _objectId = netId _localityObject;
private _clientOwner = owner _player;
// A freshly created network object briefly reports owner 0 before the
// dedicated server registers it as owner 2.  Transferring during that window
// is ignored by this engine build, so verify the stable source owner first.
private _sourceReady = [_localityObject, 2, true, 10] call TRIBUNAL_fnc_waitForLocality;
private _initial = [_localityObject, "server"] call TRIBUNAL_fnc_localityRecord;
["tribunal.locality.serverInitial", _sourceReady && {!isNull _localityObject} && {_objectId isNotEqualTo ""}, format ["object=%1|owner=%2|local=%3", _objectId, owner _localityObject, local _localityObject]] call _assert;
private _transferRequested = _localityObject setOwner _clientOwner;
private _clientOwned = [_localityObject, _clientOwner, false, 15] call TRIBUNAL_fnc_waitForLocality;
[_localityObject, "client-a"] call TRIBUNAL_fnc_localityRecord;
missionNamespace setVariable ["TRIBUNAL_LOCALITY_OBJECT", [_token, _objectId, _clientOwner], true];
["tribunal.locality.clientTransfer", _transferRequested && {_clientOwned}, format ["object=%1|owner=%2|clientOwner=%3|local=%4", _objectId, owner _localityObject, _clientOwner, local _localityObject]] call _assert;
private _ackDeadline = diag_tickTime + 20;
waitUntil { uiSleep 0.05; count (missionNamespace getVariable ["TRIBUNAL_LOCALITY_ACKS", []]) >= 1 || diag_tickTime > _ackDeadline };
private _acks = missionNamespace getVariable ["TRIBUNAL_LOCALITY_ACKS", []];
private _ack = _acks param [0, []];
["tribunal.locality.remoteExactlyOnce", (count _acks) isEqualTo 1 && {(_ack param [0, ""]) isEqualTo _token} && {(_ack param [1, ""]) isEqualTo _objectId} && {(_ack param [2, -1]) isEqualTo _clientOwner} && {(_ack param [4, -2]) isEqualTo _clientOwner}, format ["acks=%1", _acks]] call _assert;
private _returnRequested = _localityObject setOwner 2;
private _serverRestored = [_localityObject, 2, true, 15] call TRIBUNAL_fnc_waitForLocality;
[_localityObject, "server"] call TRIBUNAL_fnc_localityRecord;
["tribunal.locality.serverRestored", _serverRestored, format ["request=%1|object=%2|owner=%3|local=%4", _returnRequested, _objectId, owner _localityObject, local _localityObject]] call _assert;
deleteVehicle _localityObject;
''',
    client_sqf=locality_fixture_sqf() + r'''
private _localityDeadline = diag_tickTime + 30;
waitUntil { uiSleep 0.05; !isNil {missionNamespace getVariable "TRIBUNAL_LOCALITY_OBJECT"} || diag_tickTime > _localityDeadline };
private _declaration = missionNamespace getVariable ["TRIBUNAL_LOCALITY_OBJECT", []];
private _objectId = _declaration param [1, ""];
private _expectedOwner = _declaration param [2, -1];
private _localityObject = if (_objectId isNotEqualTo "") then {objectFromNetId _objectId} else {objNull};
private _resolveDeadline = diag_tickTime + 15;
waitUntil { uiSleep 0.02; !isNull _localityObject || diag_tickTime > _resolveDeadline };
// Numeric object ownership is authoritative on the server. This dedicated
// build reports owner 0 for a local transferred object on the owning client,
// so client evidence verifies local plus the declared clientOwner identity.
private _owned = [_localityObject, -1, true, 15] call TRIBUNAL_fnc_waitForLocality;
private _record = [_localityObject, "client-a"] call TRIBUNAL_fnc_localityRecord;
["tribunal.locality.clientOwned", (_declaration param [0, ""]) isEqualTo _token && {_owned} && {_expectedOwner isEqualTo clientOwner}, format ["object=%1|owner=%2|clientOwner=%3|local=%4", _objectId, owner _localityObject, clientOwner, local _localityObject]] call _assert;
["tribunal.locality.executionMachine", (missionNamespace getVariable ["TRIBUNAL_MACHINE_IDENTITY", ""]) isEqualTo "client-a" && {(_record param [3, ""]) isEqualTo "client-a"}, format ["record=%1", _record]] call _assert;
[_token, _objectId, clientOwner, owner _localityObject] remoteExecCall ["TRIBUNAL_fnc_localityClientAck", 2];
''',
    requires_project_mods=False,
    metadata={"capability": "locality", "ownership": "server->client-a->server"},
)

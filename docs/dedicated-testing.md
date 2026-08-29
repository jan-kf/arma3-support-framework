# Dedicated-server integration testing

## What the command does

`./pontifex test dedicated` creates a unique `$PONTIFEX_STATE_ROOT/runs/<UTC-time>-<random>/` directory, records Git/Arma/dependency provenance, rebuilds all four Pontifex mods, provisions pinned dependencies, prepares the disposable runtime view, launches Arma on loopback port 2312, waits for an explicit mission completion record, and stops only its own process group.

The controller is `tools/pontifex_server.py`. It holds `$PONTIFEX_STATE_ROOT/server/control.lock` for the complete lifecycle. Persistent/manual server start is deliberately not implemented.

## Runtime ownership

Arma 3 Server 2.20.152984 (Steam build 18981937) is reused from:

```text
/mnt/services/arma3-server/pufferpanel/data/servers/80e9c1f3
```

The executable and base/DLC PBO banks are exposed through symlinks in `$PONTIFEX_STATE_ROOT/server/install`. PufferPanel is never invoked. Pontifex owns the generated Linux-normalized mod deployment, mission, server config, dependency packages, runtime state, per-run profile, and logs. The legacy payload must remain until it is moved or replaced with a project-owned SteamCMD installation.

Linux Arma requires lowercase mod/PBO paths. Build artifacts retain their historical names; `$PONTIFEX_STATE_ROOT/server/mods` contains generated lowercase deployment copies. Dependency releases are hard-linked into `$PONTIFEX_STATE_ROOT/server/dependency-mods` so both host and container lifecycles see a physical game-directory deployment. Installed official DLC PBO banks are wrapped as generated test mods because the legacy server did not activate those banks itself.

## Dependencies

The complete official releases are used instead of maintaining a fragile hand-pruned transitive PBO graph:

| Dependency | Version | Source |
| --- | --- | --- |
| CBA A3 | 3.18.6 | CBATeam GitHub release |
| ACE3 | 3.21.0 | ACE3 GitHub release |
| Zeus Enhanced | 1.15.1 | ZEN GitHub release |

Versions, URLs, archive names, and SHA-256 values are tracked in `server/dependencies.lock.json`. Archives cache under `$PONTIFEX_STATE_ROOT/dependencies/cache`; extracted packages live under `$PONTIFEX_STATE_ROOT/dependencies`. Both are ignored by Git. GitHub downloads need no Steam account or Steam Guard. To update, edit and review the lock entry, then run `./pontifex dependencies provision`.

## Mission and protocol

The source mission is `tests/missions/Pontifex_Integration.Stratis`. It has no playable client and runs `initServer.sqf` inside the real dedicated mission. It asserts:

- SQF execution and dedicated/server locality;
- all four real Pontifex `CfgPatches` classes;
- all four registered production server functions;
- the Core server postInit cache;
- the controlled-failure parameter.

Protocol records are single, pipe-delimited RPT lines:

```text
PONTIFEX_TEST|PASS|server|core.config|
PONTIFEX_TEST|FAIL|server|harness.forcedFailure|enabled=true
PONTIFEX_TEST|COMPLETE|server|status=PASS|assertions=13|failures=0
```

Success requires all expected assertion names, no FAIL records, matching assertion counts, and an explicit PASS completion marker. Process uptime alone never counts as success. `--force-failure` is a harness-validation option and must return nonzero.

Linux dedicated Arma emits its RPT stream to stdout in this installation. The controller captures that stream as both `server-console.log` and the canonical `server.rpt` evidence.

## Evidence and failure behavior

Each run retains:

```text
$PONTIFEX_STATE_ROOT/runs/<run-id>/
├── manifest.json       # Git state, hashes, versions, command, timestamps
├── results.json        # parsed PASS/FAIL and reason
├── server.rpt          # canonical captured Arma RPT stream
├── server-console.log  # raw process output
├── build.log
├── server.cfg
├── basic.cfg
└── profile/            # isolated Arma profile/cache state
```

The runner reports build/provision/start failures, early process exit, timeout, missing/malformed protocol, missing assertions, count mismatch, and assertion failure. Default timeout is 180 seconds; override it with `PONTIFEX_DEDICATED_TIMEOUT`. All outcomes retain evidence and return nonzero on failure.

The state file records PID, `/proc` start ticks, process group, command, and run ID. Stop validates all identity fields and never searches by process name. Cleanup escalates only that process group from SIGINT to SIGTERM to SIGKILL when required.

## Known mods/runtime observations

- Existing HEMTT warnings remain, including two VIGIL `fn_homepage.sqf` type-inference warnings and Field Utilities `CfgPatches` omissions.
- The test proves server-side config/function/postInit loading, not client UI or client locality.
- Steam API may log initialization warnings before connecting; the server-only test does not depend on Workshop or Steam authentication.
- The empty no-client mission logs role/header warnings but starts correctly under `-autoInit`.

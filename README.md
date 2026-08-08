# Pontifex development appliance

Pontifex is a four-mod Arma 3 suite. This directory is the canonical Gustav workspace:

- `source/core` — CORDIS, the shared core (`CORDIS.pbo`)
- `source/field-utilities` — Field Utilities (`FieldUtils.pbo`)
- `source/advanced-systems` — Advanced Systems (`AdvSys.pbo`)
- `source/visual-support-tablet` — VIGIL Visual Support Tablet (`VIGIL.pbo`)

## Normal commands

Run these from `/mnt/services/pontifex`:

```bash
./pontifex check
./pontifex build
./pontifex test
./pontifex test dedicated
./pontifex status
./pontifex server status
./pontifex server stop
```

`check` performs HEMTT config/SQF checks plus harness syntax checks. `build` produces four unsigned development PBOs under `build/current/`. Plain `test` is the fast/static suite. `test dedicated` builds, provisions dependencies, launches a real loopback-only Arma dedicated server, runs the Stratis mission assertions, writes JSON/log evidence, and stops the exact process it launched.

Inspect the latest dedicated result with:

```bash
jq . runs/latest/results.json
less runs/latest/server.rpt
```

Each run is retained under `runs/<run-id>/`. `server status` shows the controlled process, pinned dependencies, and latest result. `server stop` validates the recorded PID, process start time, process group, and command before stopping anything.

HEMTT 1.20.1 is project-bootstrapped on first use and checksum-verified. The repository contains source and tooling configuration; generated `.hemttout`, `build`, `release`, `runs`, and server runtime files are ignored.

## Runtime and results

- Editable source: `source/`
- Current build artifacts: `build/current/`
- Future release artifacts: `release/`
- Future isolated Arma server: `server/runtime/`
- Future server profiles/config: `server/config/`
- Future test missions: `tests/missions/`
- Future per-run logs and machine results: `runs/`
- Preserved original import: `archive/Pontifex-original.zip`

Dependencies are pinned in `server/dependencies.lock.json`, installed outside Git under `server/dependencies/`, and checksum-verified. Provision explicitly with `./pontifex dependencies provision`; dedicated tests provision missing packages automatically. Updates require changing the pinned version, URL, and SHA-256 in the lock file. No Steam credentials are used for CBA, ACE, or Zeus Enhanced.

The Arma 3 2.20.152984 base files are currently shared read-only from the preserved legacy Steam installation through a generated view under `server/runtime/`; test config, dependencies, missions, profiles, deployment copies, state, and logs are Pontifex-owned. The lifecycle does not call PufferPanel. The old panel remains separately managed at `/mnt/services/arma3-server`.

## Unfinished / next step

Phase three should add an automated client/locality test while preserving this server-only smoke test, then add `test --interactive`. Before removing the complete legacy tree, relocate or freshly provision its Steam payload into a Pontifex-owned base-install location. Establish versioning and protected private-key storage before enabling `release`.

See `docs/dedicated-testing.md` for the lifecycle/protocol and `docs/reconnaissance.md` for the original inventory.

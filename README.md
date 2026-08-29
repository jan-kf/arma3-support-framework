# Pontifex development appliance

Pontifex is a four-mod Arma 3 suite. This directory is the canonical Gustav workspace:

- `mods/core` — CORDIS, the shared core (`CORDIS.pbo`)
- `mods/field-utilities` — Field Utilities (`FieldUtils.pbo`)
- `mods/advanced-systems` — Advanced Systems (`AdvSys.pbo`)
- `mods/visual-support-tablet` — VIGIL Visual Support Tablet (`VIGIL.pbo`)

## Normal commands

Run these from `/mnt/services/arma-projects/pontifex`:

```bash
./pontifex check
./pontifex build
./pontifex test
./pontifex test smoke
./pontifex test integration --select config,round-trip
./pontifex test gameplay
./pontifex test live
./pontifex live status
./pontifex test dedicated
./pontifex test multiplayer
./pontifex status
./pontifex server status
./pontifex server stop
./pontifex client status
```

`check` performs HEMTT config/SQF checks plus harness syntax checks. `build` produces four unsigned development PBOs under `$PONTIFEX_STATE_ROOT/builds/current/`. Plain `test` is the fast/static suite. `test smoke`, `test integration`, and `test gameplay` are the fresh real-client tiers; see [multiplayer testing](docs/multiplayer-testing.md#test-tiers). `test dedicated` runs the real server-only test. `test multiplayer` is the one-real-player experiment: it creates an isolated Docker bridge, launches the server and a normal Steam/Proton player client at different virtual addresses, parses both origins, and removes its containers/network.

The generic framework is the independent Tribunal repository resolved by
`TRIBUNAL_ROOT`. Pontifex is its first registered mod suite; feature scenarios
remain beside the feature they validate. Use
`$TRIBUNAL_ROOT/bin/tribunal scenarios tribunal.project.json` to inspect them,
or `tribunal run tribunal.project.json ...` through an installed CLI.

Inspect the latest dedicated result with:

```bash
jq . /mnt/services/arma-state/pontifex/runs/latest/results.json
less /mnt/services/arma-state/pontifex/runs/latest/server.rpt
```

Each run is retained under `$PONTIFEX_STATE_ROOT/runs/<run-id>/`. `server status` shows the controlled process, pinned dependencies, and latest result. `server stop` validates the recorded PID, process start time, process group, and command before stopping anything.

The multiplayer command currently requires one manual, credential-bearing provisioning step. Build and verify the credential-free image with:

```bash
./pontifex client image
./pontifex client preflight
./pontifex client login
```

`client login` exposes Steam VNC only on Gustav `127.0.0.1:5903`. Reach it through an SSH tunnel, sign in directly to Steam, force a Proton tool for Arma 3, and install the Windows client. Then run `./pontifex client stop-login` and `./pontifex client status`. Steam state and the large game installation live outside Git under `$PONTIFEX_STATE_ROOT/client/`; never put a password in a command or repository file.

HEMTT 1.20.1 is project-bootstrapped on first use and checksum-verified. The repository contains source and tooling configuration. Runtime and generated state live under `PONTIFEX_STATE_ROOT`, which defaults to `/mnt/services/arma-state/pontifex` for this checkout and may be overridden explicitly.

## Runtime and results

- Editable source: `mods/`
- Current build artifacts: `$PONTIFEX_STATE_ROOT/builds/current/`
- Future release artifacts: `release/`
- Isolated Arma server: `$PONTIFEX_STATE_ROOT/server/`
- Future server profiles/config: `server/config/`
- Future test missions: `tests/missions/`
- Per-run logs and machine results: `$PONTIFEX_STATE_ROOT/runs/`
- Preserved original import: `archive/Pontifex-original.zip`

Dependencies are pinned in `server/dependencies.lock.json`, installed outside Git under `$PONTIFEX_STATE_ROOT/dependencies/`, and checksum-verified. Provision explicitly with `./pontifex dependencies provision`; dedicated tests provision missing packages automatically. Updates require changing the pinned version, URL, and SHA-256 in the lock file. No Steam credentials are used for CBA, ACE, or Zeus Enhanced.

The Arma 3 2.20.152984 base files are currently shared read-only from the preserved legacy Steam installation through a generated view under `$PONTIFEX_STATE_ROOT/server/`; test config, dependencies, missions, profiles, deployment copies, state, and logs are Pontifex-owned. The lifecycle does not call PufferPanel. The old panel remains separately managed at `/mnt/services/arma3-server`.

## Next step

The single authenticated Steam identity now proves the real-client core. A future two-client/JIP/locality proof requires a second independently authenticated Steam account. Before removing the complete legacy tree, relocate or freshly provision its Steam payload into a Pontifex-owned base-install location. Establish versioning and protected private-key storage before enabling `release`.

See `docs/dedicated-testing.md` for the server lifecycle, `docs/multiplayer-testing.md` for the client experiment and secure provisioning boundary, and `docs/reconnaissance.md` for the original inventory.

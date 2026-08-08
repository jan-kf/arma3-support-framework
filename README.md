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
./pontifex status
./pontifex server status
```

`check` performs HEMTT config/SQF checks. `build` produces four unsigned development PBOs under `build/current/`. `test` currently means the static phase-one checks; it explicitly does not start Arma.

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

No Pontifex server process exists yet, so `server start` and `server stop` deliberately refuse to act. The unrelated legacy PufferPanel installation remains preserved and running from `/mnt/services/arma3-server`; do not use it as the Pontifex test server. Its status/logs are available with `docker compose -f /mnt/services/arma3-server/docker-compose.yml ps` and `docker compose -f /mnt/services/arma3-server/docker-compose.yml logs`; deliberately start or stop it with the corresponding `up -d` or `stop` command.

## Unfinished / next step

Phase two should install a clean Arma 3 dedicated runtime under `server/runtime`, add a minimal test mission and config, deploy the four development builds, run the server with a per-run profile directory, parse its RPT into PASS/FAIL JSON, and then add `test --interactive` behavior. Establish versioning and protected private-key storage before enabling `release`.

See `docs/reconnaissance.md` for the import and legacy-server inventory.


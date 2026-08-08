# Phase-one reconnaissance

## Source import

The supplied `/mnt/services/arma3-dev/pontifex/Pontifex.zip` was 28,416,947 bytes. It contained 381 ZIP entries (295 files, 32,565,439 uncompressed bytes) under four top-level directories. The archive passed a path-traversal-name check. It contained no Git metadata or build automation.

The editable import retains each historical addon prefix and internal path. Distribution folders were separated from editable source. The complete original archive remains at `archive/Pontifex-original.zip`, including old stable/beta packages, art, and notes.

| Component | Imported source | PBO prefix/name | Historical packages |
| --- | --- | --- | --- |
| Core | `CORDIS/CORDIS` | `CORDIS` | stable |
| Field Utilities | `YSF_Field_Utilities/FieldUtils` | `FieldUtils` | stable + beta |
| Advanced Systems | `YSF_Advanced_Systems/AdvSys` | `AdvSys` | stable + beta |
| Visual Support Tablet | `YSF_Tablet/VIGIL` | `VIGIL` | stable + beta |

The archive had 72 SQF files, 17 CPP configs, 13 HPP files, 87 OGG files, 50 PAA files, 24 PNG files, seven PBOs, seven signatures, and seven copies of the same public `Yoshi.bikey`. It also had `YSF_Tablet/VIGIL.zip` and temporary/source artwork. No `.biprivatekey` was present. Old PBO timestamps show manual stable/beta builds through March 2026, but there was no script or metadata identifying the exact prior packer; the conventional `@Mod/Addons` output and BI signatures are consistent with Arma Tools/AddOn Builder or equivalent manual tooling.

## Build decision

HEMTT was selected because it is command-line native on Linux, validates configs and SQF, builds PBOs, supports signing/releases later, and does not require PufferPanel or a Windows P: drive for these script/config-only addons. Four small HEMTT projects preserve the four separately distributed mods. The imported flat `$PBOPREFIX$` values are explicitly retained with per-addon `ignore_pboprefix`; changing runtime paths during bootstrap would be unnecessarily risky.

The bootstrap pins HEMTT 1.20.1 and verifies SHA-256 `4ec152f9174be9745c8ee571df0862246b1beb9819c92d3f8876f1c406faf3ea`. Project version `0.1.0` is scaffolding only; release remains disabled until the real version policy is chosen.

VIGIL includes Arma's loose `\a3\ui_f\hpp\defineDIKCodes.inc`, which is not shipped in a Linux dedicated-server install. Its workspace therefore supplies a minimal HEMTT `include/` shim defining the sole referenced constant, `DIK_HOME` (`0xC7`). The imported SQF remains unchanged and no P: drive is needed.

## Build verification

On Gustav, `./pontifex build` successfully produced and checksum-validated four unsigned development PBOs with embedded prefixes `CORDIS`, `FieldUtils`, `AdvSys`, and `VIGIL`. They are package-ready beneath `build/current`. HEMTT reports imported source-quality warnings (including CfgPatches omissions and SQF type/style findings) and warns that Arma 3 Tools is unavailable for BI-native binarization; no build-stopping error remains. These warnings should be triaged separately from the environment bootstrap.

Runtime dependency inspection found CBA required by all four mods, ACE required by Field Utilities and Advanced Systems, and Zeus Enhanced (`zen_main`) required by Field Utilities. These dependencies are not present in the old server tree and must be pinned/provisioned for phase-two integration tests.

## Legacy Arma/PufferPanel inventory

`/mnt/services/arma3-server` occupies about 5.5 GiB. Its Docker Compose file runs `pufferpanel/pufferpanel:latest`, mounts the Docker socket, and declares UI/SFTP bindings to the historical host address `192.168.1.115`. The container is currently running, but Docker reports no effective published ports. PufferPanel's process and database are operational; the managed Arma server itself is not running.

PufferPanel server `80e9c1f3` contains a real Linux Arma 3 Dedicated Server installation (Steam app 233780), `arma3server_x64`, base-game PBOs, Steam runtime/manifests, a small `config.cfg`, `parameters.txt`, and the stock public `a3.bikey`. It is configured for port 2302, docker/host networking, no autostart/recovery/restart, and a named Steam account. Its current config disables signature verification, allows file patching, and still contains a placeholder admin password, so it is not an acceptable integration-test baseline. Empty top-level `mods`, `missions`, `backups`, and `servers` directories are mounted beside it. No Pontifex mods, custom missions, RPT logs, Arma profiles, BI private signing keys, or unique test harness were found.

Sensitive PufferPanel material is preserved in place: session/token configuration, its SQLite user/session database, SFTP host key, and server record. Values were not copied into the Pontifex repository. The Steam username is present in the PufferPanel server record; no Steam password was found in the inspected file configuration.

Recommendation: reuse the installed Arma server payload only as a download/cache source if useful, but do not retain PufferPanel in the Pontifex architecture. After phase two proves a transparent project-local server runner and any desired PufferPanel credentials are backed up, stop and archive/remove the old panel and its duplicate server tree. Nothing was deleted or stopped in phase one.


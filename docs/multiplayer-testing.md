# Real-client multiplayer testing

## Test tiers

Every real-client tier creates a fresh tokenized mission and deterministic PBO, uses the normal private Docker bridge and Steam/Proton path, and reports machine-readable assertions by origin. Normal tier runs tear down their client, server, and private network after completion.

| Command | Purpose | Session shape |
| --- | --- | --- |
| `./pontifex test smoke` | Fastest real confidence check: build, server, native join, player creation, and both init phases. | One fresh boot. |
| `./pontifex test integration [--select name,...]` | Modular script/config/RPC checks. | One fresh boot, then all selected checks run inside that mission session. |
| `./pontifex test gameplay` | Deterministic setup/action/assert/cleanup scenarios. | One fresh boot per scenario suite. |
| `./pontifex e2e` | Canonical tokenized end-to-end proof. | One fresh boot and authoritative in-game action. |

The current integration demonstrations are `mission-namespace`, `config`, and `round-trip`. They can be independently selected, for example:

```bash
./pontifex test integration --select config,round-trip
```

The gameplay demonstration creates a server-owned Offroad, publishes its netId, moves the real client player into the driver seat, and requires an authoritative server verification. It is a model for scenario setup, action, assertion, and cleanup—not a replacement for the canonical E2E.

The permanent `aps-intercept` scenario additionally runs a real server-owned rocket through the production APS predicate and interceptor. It records the exact vehicle and projectile IDs in the authoritative engagement ledger, requires projectile neutralization and exactly one hard-kill charge consumed, and verifies the replicated ledger from the real client. Its controls prove an APS-disabled vehicle receives the impact without an engagement or charge consumption, while an elevated lateral miss remains a live projectile outside the envelope with no engagement or charge change. Fixture rockets are positioned from the terrain-snapped vehicle's ASL position; this prevents an elevated Stratis terrain surface from turning the test into a ground-collision artifact.

### Developer Live Mode

```bash
./pontifex test live
./pontifex live status
./pontifex live exec server 'diag_log "my server probe";'
./pontifex live exec client 'diag_log "my client probe";'
./pontifex live test config
./pontifex live reset
./pontifex live stop
```

Live Mode first completes the smoke protocol, then deliberately retains its already-running private server/client session. It is a development aid, never proof: permanent tests must be promoted to Tier 2 or Tier 3 and pass from a fresh autonomous run.

The server command channel is intentionally narrow. A runtime-only Arma extension can read exactly one run-scoped, read-only mounted SQF inbox and exposes no networking, process execution, directory traversal, or writes. Client snippets are relayed through the existing authenticated mission RPC channel. Commands are atomically replaced, size-limited, and audited in the run's `live-control/commands.jsonl`. `live stop` is the only command that tears down the retained containers and bridge.

No Git remote is configured. Source commits remain local-only until a remote URL and authentication are supplied.

## Architecture

The controller is `tools/pontifex_multiplayer.py`. Each run creates two unprivileged containers on one run-labeled Docker bridge:

```text
Gustav
└── run-scoped Docker bridge: 10.253.X.0/24
    ├── dedicated server: 10.253.X.10
    └── normal Steam/Proton player client: 10.253.X.20
```

The exact third octet is selected per run and recorded. No Arma or VNC port is published by an automated test. The client receives the server bridge address in `-connect`; it cannot accidentally connect to the server through its own `127.0.0.1`. Docker inspection, container `/proc/net/route`, and interface evidence are retained under `network/`.

The server shares the same read-only Arma base payload as the dedicated test. Config, profiles, normalized mods, logs, and run state remain Pontifex-owned. Dependencies are hard-linked into the disposable runtime so Linux Arma can load them across the container mount boundary.

Every selected mission directory is deterministically staged as an uncompressed banked PBO in the disposable `mpmissions/` view before the server starts. This is intentionally not an optimization: a controlled real-client comparison showed that Arma's dedicated directory-mission path generated a different transient `__cur_mp` transfer and crashed the client during state receipt, while the identical mission served as a PBO transferred byte-for-byte and entered gameplay. The PBO is runtime-local and contains only the already-selected mission files; it does not change mods, Steam authentication, network exposure, or confinement.

SteamCMD's Linux dedicated-server payload omits the base playable-character PBO. The integration mission uses one `B_Soldier_F` player slot, so the controller bind-mounts only the authenticated client's licensed `Addons/characters_f.pbo` as a read-only, server-only test mod. Registering it as a mod is required: placing it in the dedicated payload's base `addons/` directory still leaves it classified as deleted content.

The SteamCMD distribution App ID (`233780`) is used only to install and update the dedicated payload. The running dedicated executable writes `107410` to its disposable `steam_appid.txt`, matching the Arma 3 client's Steamworks ticket context. The bare server image has no OS trust store, so the controller stages the host's public CA bundle into its disposable runtime and bind-mounts that single file read-only at `/etc/ssl/certs/ca-certificates.crt`. This permits Steam's TLS transport to authenticate; it does not expose a host service, add a capability, publish a port, or give the server write access to host configuration.

The client image is built from `client/Dockerfile` using Ubuntu 24.04 packages. It runs as the host UID/GID, drops all Linux capabilities, enables `no-new-privileges`, and receives only NVIDIA GPU 0 through NVIDIA CDI. Steam runs with its browser sandbox enabled. A private session bus is exported only as `DBUS_SYSTEM_BUS_ADDRESS` inside the container and hosts a fixed-value, read-only `org.freedesktop.NetworkManager` manager object. It reports global connectivity but exposes no host socket, device, proxy, or configuration operation. A project-owned AppArmor profile and Moby-derived seccomp allowlist permit bubblewrap to create an unprivileged user/mount namespace and perform mounts only after entering it; kernel capability checks continue to block mounts in the container's initial namespace. Pontifex loads the named AppArmor profile with a short-lived setup container, proves the confined bubblewrap path before every login or automated client run, and never runs the long-lived client privileged. The interactive and automated client paths receive a 1 GiB private `/dev/shm` so CEF can keep its renderer alive. Sound is disabled and no physical display is used.

The display server is Weston 13's unprivileged `headless` backend with its GL renderer, kiosk shell, and Xwayland module. Weston creates one deterministic 1280×720 virtual output and an in-container Wayland socket; it then creates a private Xwayland display for Steam, Proton, DXVK, and Arma. The kiosk shell gives the game the full virtual output without desktop decorations or focus-dependent window management. The entrypoint waits for both the Wayland socket and a responding X11 socket, then exports the discovered `DISPLAY`; Steam and Proton inherit it normally. Weston uses the NVIDIA EGL/GL implementation (recorded in `weston.log`), while DXVK retains the RTX Vulkan device for the game. The only X11 socket directory is the container-local sticky `/tmp/.X11-unix`; neither X11 nor Wayland is mounted from or exposed to the host.

GPU-backed Xorg was deliberately rejected. NVIDIA can start it only in NoScanout mode under this confinement, which leaves Steam with no display information. Asking Xorg for a real output fails with `Failed to acquire modesetting permission`, because the host owns DRM modesetting. Adding only `/dev/dri/card0` and its video group did not change that result. Weston headless avoids DRM/KMS entirely, so no DRM node, modesetting authority, capability, seccomp rule, AppArmor relaxation, host D-Bus socket, privileged container, or external display endpoint is added. Optional x11vnc still exists only inside the client and is published by the controller only to `127.0.0.1` for diagnostics.

The network-state bridge exists solely because Steam's native `client_networkmanager` module declines to export `SteamClient.System.Network.RegisterForDeviceChanges` when no system bus is present; the embedded login page otherwise waits indefinitely even after Steam's separate HTTP connectivity test reports `Connected`. Its manager object implements only `GetDevices`, `GetAllDevices`, `CheckConnectivity`, D-Bus property reads, and object-manager enumeration. All device lists are empty, and all property values are constants. It accepts no mutations and receives no additional Linux capability.

Reconnaissance and validated facts:

- NVIDIA GeForce RTX 3080, 10 GiB VRAM, driver 580.173.02;
- native Vulkan 1.4.312 works;
- NVIDIA CDI exposes the real RTX device inside the unprivileged image;
- `vkcube` presents through Weston headless/Xwayland on the discrete GPU;
- 31 GiB total RAM (28 GiB available during reconnaissance);
- 284 GiB free storage during reconnaissance;
- no Steam player session, Proton, Wine, or App 107410 installation was present;
- the free Linux dedicated-server App 233780 remains separate and unlicensed.

A short 1280×720 `vkcube`/Weston/Xwayland probe confirms that the virtual presentation path uses the discrete GPU. This is rendering-layer evidence only—not an Arma client capacity measurement. A real multiplayer run retains periodic Docker/NVIDIA samples for the meaningful figure.

## One-time secure provisioning

Build and prove the credential-free layer:

```bash
./pontifex client image
./pontifex client preflight
```

Start Steam's graphical login environment:

```bash
./pontifex client login
```

The command first loads `client/security/pontifex-steam.apparmor` and validates `bwrap` under `client/security/pontifex-steam-seccomp.json`. It fails closed if either profile or the user-namespace probe fails.

It publishes only `127.0.0.1:5903` on Gustav. From a trusted laptop, establish a tunnel equivalent to:

```bash
ssh -L 5903:127.0.0.1:5903 <gustav-ssh-target>
```

Connect a VNC viewer to laptop `127.0.0.1:5903`, then:

1. allow Steam to bootstrap;
2. sign in to the account that owns Arma 3 and complete Steam Guard inside Steam;
3. in Arma 3 Compatibility settings, force a current Proton release;
4. install Arma 3 and the selected Proton tool;
5. confirm the Windows `arma3_x64.exe` depot exists;
6. close Steam and run `./pontifex client stop-login`.

Do not type a password into a Pontifex command, configuration, shell history, or Codex conversation. Steam's own session files and game payload persist under mode-0700 `client/runtime/home`, which is ignored by Git. The login container is label-validated before removal.

Check readiness without reading or printing session contents:

```bash
./pontifex client status
```

Readiness requires the image, a Steam login marker, Windows Arma executable, and Proton executable.

## Automated command and protocol

Once provisioned:

```bash
./pontifex test multiplayer
```

The command builds Pontifex, provisions dependencies, creates the bridge, starts the real dedicated server at `.10`, waits for mission initialization, starts Steam App 107410 at `.20`, gathers both RPT streams, evaluates both completion records, records resource samples, and removes only containers/networks bearing its run ID.

Records identify origin:

```text
PONTIFEX_TEST|PASS|server|server.isDedicated|actual=true
PONTIFEX_TEST|PASS|client-a|client.hasInterface|actual=true
PONTIFEX_TEST|COMPLETE|client-a|status=PASS|assertions=9|failures=0
```

The dedicated-only command uses the same origin-aware protocol and remains a 13-assertion regression test.

The multiplayer server adds assertions for exactly one `allPlayers` entry, a nontrivial owner/name identity, a non-`HeadlessClient_F` player unit, and an acknowledged nonce round trip. The client asserts `hasInterface`, non-server/non-dedicated semantics, CORDIS client postInit, all four configs/functions, a present local player, and the nonce response. CORDIS now exposes `YCD_clientInitialized` as a general lifecycle signal; production behavior does not depend on the harness.

## Evidence and cleanup

Multiplayer runs retain:

```text
runs/<run-id>/
├── manifest.json
├── results.json
├── build.log
├── server/
│   ├── server.rpt
│   ├── console.log
│   └── profile/
├── client-a/
│   ├── client.rpt
│   ├── console.log
│   ├── steam.log
│   ├── steam-107410.log
│   ├── weston.log
│   └── weston.stdout.log
│   └── profile/
└── network/
    ├── docker-network.json
    ├── container inspections
    └── route/interface records
```

The manifest records Git/PBO/dependency identities, both Arma builds, Proton path, container IDs and host PIDs, virtual IP/MAC/gateway data, commands, and GPU state. Results group assertions by origin and retain periodic Docker CPU/memory plus GPU utilization/memory/power samples.

State is stored in `server/runtime/multiplayer.json`. Removal validates each run label before touching a container or network. Build, graphics, Steam, launch, mission, protocol, timeout, early-exit, and cleanup failures all return nonzero with retained evidence. `./pontifex server stop` covers both the Phase Two process lifecycle and this container lifecycle.

## Licensing references

Bohemia documents that playable App 107410 branches require an account possessing Arma 3, while dedicated-server App 233780 is separately available without game ownership. See the Bohemia Interactive Community pages for [Steam branches](https://community.bohemia.net/wiki/Arma_3:_Steam_Branches) and [dedicated servers](https://community.bohemia.net/wiki/Arma_3:_Dedicated_Server).

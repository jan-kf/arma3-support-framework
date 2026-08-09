# One-real-player multiplayer experiment

## Current boundary

The credential-free architecture is implemented and its independent layers are proven. Gustav has no existing licensed Arma 3 player installation or reusable Steam login. Therefore `./pontifex test multiplayer` deliberately returns `client_not_provisioned` before creating a network or process until an account that owns Arma 3 completes Steam login/Steam Guard and installs the Windows client plus Proton.

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

The client image is built from `client/Dockerfile` using Ubuntu 24.04 packages. It runs as the host UID/GID, drops all Linux capabilities, enables `no-new-privileges`, and receives only NVIDIA GPU 0 through NVIDIA CDI. Steam runs with its browser sandbox enabled. A private session bus is exported only as `DBUS_SYSTEM_BUS_ADDRESS` inside the container and hosts a fixed-value, read-only `org.freedesktop.NetworkManager` manager object. It reports global connectivity but exposes no host socket, device, proxy, or configuration operation. A project-owned AppArmor profile and Moby-derived seccomp allowlist permit bubblewrap to create an unprivileged user/mount namespace and perform mounts only after entering it; kernel capability checks continue to block mounts in the container's initial namespace. Pontifex loads the named AppArmor profile with a short-lived setup container, proves the confined bubblewrap path before every login or automated client run, and never runs the long-lived client privileged. The interactive and automated client paths receive a 1 GiB private `/dev/shm` so CEF can keep its renderer alive. It contains 64/32-bit Vulkan/GLVND libraries, Steam, Xvfb, and a loopback-provisioning VNC server. The automated framebuffer is 640×480, sound is disabled, and no physical display is used.

The network-state bridge exists solely because Steam's native `client_networkmanager` module declines to export `SteamClient.System.Network.RegisterForDeviceChanges` when no system bus is present; the embedded login page otherwise waits indefinitely even after Steam's separate HTTP connectivity test reports `Connected`. Its manager object implements only `GetDevices`, `GetAllDevices`, `CheckConnectivity`, D-Bus property reads, and object-manager enumeration. All device lists are empty, and all property values are constants. It accepts no mutations and receives no additional Linux capability.

Reconnaissance and validated facts:

- NVIDIA GeForce RTX 3080, 10 GiB VRAM, driver 580.173.02;
- native Vulkan 1.4.312 works;
- NVIDIA CDI exposes the real RTX device inside the unprivileged image;
- `vkcube` renders continuously through Xvfb on the discrete GPU;
- 31 GiB total RAM (28 GiB available during reconnaissance);
- 284 GiB free storage during reconnaissance;
- no Steam player session, Proton, Wine, or App 107410 installation was present;
- the free Linux dedicated-server App 233780 remains separate and unlicensed.

A short 640×480 `vkcube`/Xvfb probe used about 48 MiB container RAM, 28 MiB VRAM, 43% GPU, 126 W GPU power, and 186% CPU at the sampled instant. This is rendering-layer evidence only—not an Arma client capacity measurement. A real multiplayer run will retain periodic Docker/NVIDIA samples for the meaningful figure.

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
│   ├── xvfb.log
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

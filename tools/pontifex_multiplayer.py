#!/usr/bin/env python3
"""One-real-player Pontifex multiplayer experiment and client provisioning."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time
import uuid

import pontifex_server as dedicated


ROOT = dedicated.ROOT
RUNTIME = dedicated.RUNTIME
RUNS = dedicated.RUNS
CLIENT = ROOT / "client"
CLIENT_RUNTIME = CLIENT / "runtime"
CLIENT_HOME = CLIENT_RUNTIME / "home"
CLIENT_SECURITY = CLIENT / "security"
SECCOMP_PROFILE = CLIENT_SECURITY / "pontifex-steam-seccomp.json"
APPARMOR_PROFILE = CLIENT_SECURITY / "pontifex-steam.apparmor"
APPARMOR_NAME = "pontifex-steam"
IMAGE = "pontifex-arma-client:phase3"
LOGIN_CONTAINER = "pontifex-client-login"
MULTIPLAYER_STATE = RUNTIME / "multiplayer.json"
SERVER_IMAGE = "ubuntu:24.04"
SERVER_EXPECTED = dedicated.EXPECTED_ASSERTIONS | {
    "server.clientCount",
    "server.playerIdentity",
    "server.clientNotHeadless",
    "server.roundTrip",
}
CLIENT_EXPECTED = {
    "client.hasInterface",
    "client.notServer",
    "client.notDedicated",
    "client.coreInitialized",
    "client.configs",
    "client.functions",
    "client.playerExists",
    "client.playerLocal",
    "client.roundTrip",
}


def docker(args: list[str], *, check: bool = True, capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["docker", *args],
        check=check,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.PIPE if capture else None,
    )


def image_exists() -> bool:
    return docker(["image", "inspect", IMAGE], check=False).returncode == 0


def driver_branch() -> str:
    output = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=driver_version", "--format=csv,noheader"], text=True
    ).strip()
    return output.split(".", 1)[0]


def build_image() -> int:
    command = [
        "build",
        "--pull",
        "--build-arg",
        f"CLIENT_UID={os.getuid()}",
        "--build-arg",
        f"CLIENT_GID={os.getgid()}",
        "--build-arg",
        f"NVIDIA_DRIVER_BRANCH={driver_branch()}",
        "--tag",
        IMAGE,
        str(CLIENT),
    ]
    print(f"building {IMAGE} for NVIDIA branch {driver_branch()}...")
    return docker(command, check=False, capture=False).returncode


def steam_roots() -> list[Path]:
    return [
        CLIENT_HOME / ".local" / "share" / "Steam",
        CLIENT_HOME / ".steam" / "steam",
        CLIENT_HOME / ".steam" / "debian-installation",
    ]


def find_client_executable() -> Path | None:
    for root in steam_roots():
        candidate = root / "steamapps" / "common" / "Arma 3" / "arma3_x64.exe"
        if candidate.is_file():
            return candidate
    return None


def find_app_manifest() -> Path | None:
    for root in steam_roots():
        candidate = root / "steamapps" / "appmanifest_107410.acf"
        if candidate.is_file():
            return candidate
    return None


def find_login_marker() -> Path | None:
    for root in steam_roots():
        candidate = root / "config" / "loginusers.vdf"
        if candidate.is_file():
            return candidate
    return None


def find_proton() -> Path | None:
    candidates: list[Path] = []
    for root in steam_roots():
        candidates.extend(root.glob("steamapps/common/Proton*/proton"))
        candidates.extend(root.glob("compatibilitytools.d/*/proton"))
    return sorted(candidates)[-1] if candidates else None


def client_install_info() -> dict:
    executable = find_client_executable()
    manifest = find_app_manifest()
    build_id = "unknown"
    if manifest:
        found = re.search(r'"buildid"\s+"(\d+)"', manifest.read_text(errors="replace"))
        if found:
            build_id = found.group(1)
    proton = find_proton()
    image = docker(["image", "inspect", IMAGE], check=False)
    image_id = None
    if image.returncode == 0:
        image_id = json.loads(image.stdout)[0].get("Id")
    return {
        "image": IMAGE,
        "image_id": image_id,
        "image_ready": image_exists(),
        "home": str(CLIENT_HOME),
        "steam_session_present": find_login_marker() is not None,
        "arma_executable": str(executable) if executable else None,
        "arma_installed": executable is not None,
        "steam_build_id": build_id,
        "proton": str(proton) if proton else None,
    }


def ensure_client_dirs() -> None:
    CLIENT_HOME.mkdir(parents=True, exist_ok=True)
    (CLIENT_RUNTIME / "login-logs").mkdir(parents=True, exist_ok=True)
    CLIENT_RUNTIME.chmod(0o700)
    CLIENT_HOME.chmod(0o700)


def client_security_args() -> list[str]:
    return [
        "--cap-drop",
        "ALL",
        "--security-opt",
        "no-new-privileges",
        "--security-opt",
        f"seccomp={SECCOMP_PROFILE}",
        "--security-opt",
        f"apparmor={APPARMOR_NAME}",
    ]


def ensure_client_security() -> tuple[bool, str]:
    """Load and prove the confined profile needed by Steam's own sandbox."""
    missing = [str(path) for path in (SECCOMP_PROFILE, APPARMOR_PROFILE) if not path.is_file()]
    if missing:
        return False, f"missing client security profile: {', '.join(missing)}"
    load = docker(
        [
            "run",
            "--rm",
            "--privileged",
            "--user",
            "0:0",
            "--network",
            "none",
            "--read-only",
            "--security-opt",
            "apparmor=unconfined",
            "--volume",
            "/sys/kernel/security:/sys/kernel/security",
            "--volume",
            f"{APPARMOR_PROFILE}:/opt/pontifex/pontifex-steam.apparmor:ro",
            "--entrypoint",
            "/usr/sbin/apparmor_parser",
            IMAGE,
            "--replace",
            "--skip-cache",
            "/opt/pontifex/pontifex-steam.apparmor",
        ],
        check=False,
    )
    if load.returncode != 0:
        return False, f"failed to load {APPARMOR_NAME} AppArmor profile:\n{load.stderr.strip()}"
    probe = docker(
        [
            "run",
            "--rm",
            "--user",
            "pontifex",
            *client_security_args(),
            IMAGE,
            "bwrap",
            "--ro-bind",
            "/",
            "/",
            "true",
        ],
        check=False,
    )
    output = (probe.stdout or "") + (probe.stderr or "")
    if probe.returncode != 0:
        return False, f"Steam user-namespace sandbox probe failed:\n{output.strip()}"
    return True, f"{APPARMOR_NAME}: loaded; bubblewrap user namespace: PASS"


def wait_for_steam_sandbox(container: str, timeout_seconds: int = 60) -> tuple[bool, str]:
    """Require Steam, pressure-vessel, and at least one sandboxed CEF zygote."""
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        state = container_inspect(container)
        if not state or not state["State"]["Running"]:
            logs = docker(["logs", container], check=False)
            return False, ((logs.stdout or "") + (logs.stderr or "")).strip()
        processes = docker(["top", container, "-eo", "pid,comm,args"], check=False)
        if processes.returncode == 0:
            lines = processes.stdout.splitlines()
            pressure_vessel = any("srt-bwrap" in line for line in lines)
            sandboxed_zygote = any(
                "steamwebhelper" in line
                and "--type=zygote" in line
                and "--no-sandbox" not in line
                and "--no-zygote-sandbox" not in line
                for line in lines
            )
            cef_sentinel = (
                CLIENT_HOME
                / ".steam"
                / "debian-installation"
                / "ubuntu12_64"
                / ".cef-initialize-sentinel"
            )
            if pressure_vessel and sandboxed_zygote and not cef_sentinel.exists():
                return True, "pressure-vessel bubblewrap and CEF namespace sandbox: PASS"
        time.sleep(1)
    return False, "Steam did not establish pressure-vessel and a sandboxed CEF zygote before timeout"


def gpu_preflight() -> tuple[bool, str]:
    if not image_exists():
        return False, f"client image missing; run ./pontifex client image"
    security_ok, security_output = ensure_client_security()
    if not security_ok:
        return False, security_output
    run = docker(
        [
            "run",
            "--rm",
            "--device",
            "nvidia.com/gpu=0",
            *client_security_args(),
            "--env",
            "NVIDIA_DRIVER_CAPABILITIES=graphics,display,utility,compat32",
            IMAGE,
            "preflight",
        ],
        check=False,
    )
    text = security_output + "\n" + (run.stdout or "") + (run.stderr or "")
    return run.returncode == 0 and "NVIDIA GeForce RTX 3080" in text, text


def show_client_status() -> int:
    info = client_install_info()
    for key, value in info.items():
        print(f"{key}: {value}")
    login = container_inspect(LOGIN_CONTAINER)
    print(f"login_container_running: {bool(login and login['State']['Running'])}")
    ready = (
        info["image_ready"]
        and info["steam_session_present"]
        and info["arma_installed"]
        and info["proton"] is not None
    )
    return 0 if ready else 1


def start_login() -> int:
    ensure_client_dirs()
    if not image_exists() and build_image() != 0:
        return 1
    security_ok, security_output = ensure_client_security()
    if not security_ok:
        print(security_output, file=sys.stderr)
        return 1
    print(security_output)
    existing = container_inspect(LOGIN_CONTAINER)
    if existing and existing["State"]["Running"]:
        sandbox_ok, sandbox_output = wait_for_steam_sandbox(LOGIN_CONTAINER)
        print(sandbox_output, file=sys.stdout if sandbox_ok else sys.stderr)
        if sandbox_ok:
            print(f"Steam login container already running: {LOGIN_CONTAINER}")
        return 0 if sandbox_ok else 1
    if existing:
        if existing.get("Config", {}).get("Labels", {}).get("pontifex.role") != "client-login":
            print("refusing to replace container with mismatched ownership label", file=sys.stderr)
            return 1
        if docker(["rm", LOGIN_CONTAINER], check=False).returncode != 0:
            print(f"failed to remove stopped login container: {LOGIN_CONTAINER}", file=sys.stderr)
            return 1
    result = docker(
        [
            "run",
            "--detach",
            "--name",
            LOGIN_CONTAINER,
            "--label",
            "pontifex.role=client-login",
            "--device",
            "nvidia.com/gpu=0",
            *client_security_args(),
            "--env",
            "NVIDIA_DRIVER_CAPABILITIES=graphics,display,utility,compat32",
            "--publish",
            "127.0.0.1:5903:5900",
            "--shm-size",
            "1g",
            "--volume",
            f"{CLIENT_HOME}:/home/pontifex",
            "--volume",
            f"{CLIENT_RUNTIME / 'login-logs'}:/logs",
            "--env",
            "PONTIFEX_LOG_DIR=/logs",
            IMAGE,
            "login",
        ],
        check=False,
    )
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return 1
    sandbox_ok, sandbox_output = wait_for_steam_sandbox(LOGIN_CONTAINER)
    if not sandbox_ok:
        print(sandbox_output, file=sys.stderr)
        return 1
    print(sandbox_output)
    print("Steam launched with its browser and bubblewrap sandboxes enabled.")
    print("Steam is available only on Gustav loopback TCP 5903.")
    print("Use an SSH tunnel and a VNC viewer, sign in, force a Proton tool for Arma 3,")
    print("install the Windows client plus Proton, then run:")
    print("  ./pontifex client stop-login")
    print("Credentials are entered only into Steam and persist in ignored client/runtime/home.")
    return 0


def stop_login() -> int:
    inspect = docker(["inspect", LOGIN_CONTAINER], check=False)
    if inspect.returncode != 0:
        print("Steam login container is not running")
        return 0
    data = json.loads(inspect.stdout)[0]
    if data.get("Config", {}).get("Labels", {}).get("pontifex.role") != "client-login":
        print("refusing to remove container with mismatched ownership label", file=sys.stderr)
        return 1
    return docker(["rm", "--force", LOGIN_CONTAINER], check=False, capture=False).returncode


def container_inspect(container: str) -> dict | None:
    result = docker(["inspect", container], check=False)
    if result.returncode != 0:
        return None
    return json.loads(result.stdout)[0]


def validated_remove_container(container: str, run_id: str) -> bool:
    data = container_inspect(container)
    if data is None:
        return True
    labels = data.get("Config", {}).get("Labels", {})
    if labels.get("pontifex.run_id") != run_id:
        return False
    return docker(["rm", "--force", container], check=False).returncode == 0


def validated_remove_network(network: str, run_id: str) -> bool:
    result = docker(["network", "inspect", network], check=False)
    if result.returncode != 0:
        return True
    data = json.loads(result.stdout)[0]
    if data.get("Labels", {}).get("pontifex.run_id") != run_id:
        return False
    return docker(["network", "rm", network], check=False).returncode == 0


def clean_multiplayer_state() -> dict:
    cleanup = {"client_removed": True, "server_removed": True, "network_removed": True}
    if not MULTIPLAYER_STATE.is_file():
        return cleanup
    try:
        state = json.loads(MULTIPLAYER_STATE.read_text())
        run_id = state["run_id"]
        cleanup["client_removed"] = validated_remove_container(state["client_container"], run_id)
        cleanup["server_removed"] = validated_remove_container(state["server_container"], run_id)
        cleanup["network_removed"] = validated_remove_network(state["network"], run_id)
    except (OSError, KeyError, json.JSONDecodeError):
        cleanup = {key: False for key in cleanup}
    if all(cleanup.values()):
        MULTIPLAYER_STATE.unlink(missing_ok=True)
    return cleanup


def choose_network(run_id: str) -> tuple[str, str, str, str]:
    network = "pontifex-" + run_id.lower().replace("t", "-").replace("z", "-")
    seed = int(run_id[-2:], 16)
    for offset in range(20):
        octet = 40 + ((seed + offset) % 180)
        subnet = f"10.253.{octet}.0/24"
        result = docker(
            [
                "network",
                "create",
                "--driver",
                "bridge",
                "--subnet",
                subnet,
                "--label",
                f"pontifex.run_id={run_id}",
                network,
            ],
            check=False,
        )
        if result.returncode == 0:
            return network, subnet, f"10.253.{octet}.10", f"10.253.{octet}.20"
    raise RuntimeError("could not allocate an isolated Docker bridge subnet")


def container_logs(name: str) -> str:
    result = docker(["logs", name], check=False)
    return (result.stdout or "") + (result.stderr or "")


def container_running(name: str) -> bool:
    data = container_inspect(name)
    return bool(data and data.get("State", {}).get("Running"))


def container_identity(name: str, network: str) -> dict:
    data = container_inspect(name) or {}
    net = data.get("NetworkSettings", {}).get("Networks", {}).get(network, {})
    return {
        "container_id": data.get("Id"),
        "host_pid": data.get("State", {}).get("Pid"),
        "started_at": data.get("State", {}).get("StartedAt"),
        "address": net.get("IPAddress"),
        "gateway": net.get("Gateway"),
        "mac_address": net.get("MacAddress"),
    }


def write_network_evidence(run_dir: Path, network: str, containers: list[str]) -> None:
    evidence = run_dir / "network"
    evidence.mkdir(exist_ok=True)
    inspected = docker(["network", "inspect", network], check=False)
    (evidence / "docker-network.json").write_text(inspected.stdout or "[]\n")
    for container in containers:
        inspected_container = docker(["inspect", container], check=False)
        (evidence / f"{container}.json").write_text(inspected_container.stdout or "[]\n")
        for source, destination in (("/proc/net/route", "route.txt"), ("/proc/net/dev", "interfaces.txt")):
            output = docker(["exec", container, "cat", source], check=False)
            (evidence / f"{container}-{destination}").write_text(output.stdout or "")


def client_version() -> dict:
    info = client_install_info()
    executable = Path(info["arma_executable"]) if info["arma_executable"] else None
    version = "unknown"
    if executable:
        match = re.search(rb"Arma 3 (\d+\.\d+\.\d+)", executable.read_bytes())
        if match:
            version = match.group(1).decode()
    return {
        **info,
        "version": version,
        "executable_sha256": dedicated.sha256(executable) if executable else None,
    }


def gpu_sample() -> dict:
    command = [
        "nvidia-smi",
        "--query-gpu=utilization.gpu,memory.used,power.draw",
        "--format=csv,noheader,nounits",
    ]
    try:
        values = subprocess.check_output(command, text=True).strip().split(", ")
        return {"utilization_percent": float(values[0]), "memory_mib": float(values[1]), "power_w": float(values[2])}
    except (OSError, subprocess.SubprocessError, ValueError, IndexError):
        return {}


def stats_sample(container: str) -> dict:
    result = docker(["stats", "--no-stream", "--format", "{{json .}}", container], check=False)
    try:
        return json.loads(result.stdout)
    except (TypeError, json.JSONDecodeError):
        return {}


def container_processes(container: str) -> str:
    result = docker(["top", container, "-eo", "pid,ppid,lstart,args"], check=False)
    return result.stdout or ""


def combine_rpts(directory: Path, output: Path) -> str:
    reports = sorted(path for path in directory.rglob("*.rpt") if path != output)
    text = "\n".join(path.read_text(errors="replace") for path in reports)
    output.write_text(text, encoding="utf-8")
    return text


def validate_origin(assertions: list[dict], complete: dict | None, expected: set[str]) -> tuple[list[str], str | None]:
    names = {item["name"] for item in assertions}
    missing = sorted(expected - names)
    if missing or not assertions:
        return missing, "malformed_or_incomplete_protocol"
    if complete is None:
        return missing, "missing_complete_marker"
    if complete["assertions"] != len(assertions):
        return missing, "assertion_count_mismatch"
    if any(item["status"] == "FAIL" for item in assertions) or complete["status"] != "PASS" or complete["failures"]:
        return missing, "assertion_failure"
    return missing, None


def write_result(run_dir: Path, result: dict) -> None:
    result["finished_at"] = dedicated.utc_now()
    dedicated.atomic_json(run_dir / "results.json", result)
    print(f"result: {result['status']} ({result['reason']})")
    print(f"evidence: {run_dir}")


def run_multiplayer(force_failure: bool, timeout_seconds: int) -> int:
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{uuid.uuid4().hex[:8]}"
    run_dir = RUNS / run_id
    server_dir = run_dir / "server"
    client_dir = run_dir / "client-a"
    for path in (server_dir / "profile", client_dir / "profile", run_dir / "network"):
        path.mkdir(parents=True, exist_ok=True)
    latest = RUNS / "latest"
    latest.unlink(missing_ok=True)
    latest.symlink_to(run_id)

    manifest = {
        "schema": 2,
        "run_id": run_id,
        "mode": "multiplayer-forced-failure" if force_failure else "multiplayer",
        "started_at": dedicated.utc_now(),
        "timeout_seconds": timeout_seconds,
        "git": dedicated.git_info(),
        "arma_server": dedicated.arma_version(),
        "arma_client": client_version(),
        "dependencies": dedicated.dependency_status(),
        "builds": [],
        "command": ["./pontifex", "test", "multiplayer"] + (["--force-failure"] if force_failure else []),
        "architecture": "two unprivileged Docker containers on one run-scoped bridge; NVIDIA CDI client GPU",
    }
    dedicated.atomic_json(run_dir / "manifest.json", manifest)
    result = {
        "schema": 2,
        "run_id": run_id,
        "status": "FAIL",
        "reason": "runner_error",
        "assertions": [],
        "origins": {},
        "cleanup": {},
    }

    info = client_install_info()
    missing_setup = [
        name
        for name, ready in (
            ("client image", info["image_ready"]),
            ("Steam authenticated session", info["steam_session_present"]),
            ("licensed Arma 3 client", info["arma_installed"]),
            ("Proton compatibility tool", info["proton"] is not None),
        )
        if not ready
    ]
    if missing_setup:
        result["reason"] = "client_not_provisioned"
        result["missing_setup"] = missing_setup
        result["required_action"] = (
            "run ./pontifex client image, then ./pontifex client login"
            if not info["image_ready"]
            else "run ./pontifex client login"
        )
        result["cleanup"] = {"not_started": True}
        write_result(run_dir, result)
        return 1

    gpu_ok, gpu_output = gpu_preflight()
    (client_dir / "gpu-preflight.log").write_text(gpu_output, encoding="utf-8")
    if not gpu_ok:
        result["reason"] = "graphics_vulkan_preflight_failed"
        result["cleanup"] = {"not_started": True}
        write_result(run_dir, result)
        return 1

    server_name = f"pontifex-server-{run_id.lower()}"
    client_name = f"pontifex-client-a-{run_id.lower()}"
    network = ""
    cleanup = {}
    with dedicated.runtime_lock():
        dedicated.stop_server()
        previous = clean_multiplayer_state()
        if not all(previous.values()):
            result["reason"] = "stale_multiplayer_cleanup_failed"
            result["cleanup"] = previous
            write_result(run_dir, result)
            return 1
        try:
            with (run_dir / "build.log").open("w", encoding="utf-8") as build_log:
                built = subprocess.run(
                    [str(ROOT / "pontifex"), "build"],
                    cwd=ROOT,
                    stdout=build_log,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
            if built.returncode != 0:
                result["reason"] = "build_failed"
                return_code = 1
                return return_code
            dependencies = dedicated.provision_dependencies()
            dedicated.prepare_runtime()

            config = (dedicated.SERVER / "config" / "dedicated.cfg.in").read_text()
            config = config.replace("@FORCE_FAILURE@", "1" if force_failure else "0").replace(
                "@REQUIRE_CLIENT@", "1"
            )
            (server_dir / "server.cfg").write_text(config)
            shutil.copy2(dedicated.SERVER / "config" / "basic.cfg", server_dir / "basic.cfg")

            network, subnet, server_ip, client_ip = choose_network(run_id)
            port = int(os.environ.get("PONTIFEX_MULTIPLAYER_PORT", "2322"))
            mod_names = [
                *(f"@pontifex_a3_{name}" for name in dedicated.OFFICIAL_MODS),
                "@cba_a3",
                "@ace",
                "@zen",
                "@cordis",
                "@fieldutils",
                "@advsys",
                "@vigil",
            ]
            server_command = [
                str(dedicated.INSTALL_VIEW / "arma3server_x64"),
                f"-ip={server_ip}",
                f"-port={port}",
                f"-config={server_dir / 'server.cfg'}",
                f"-cfg={server_dir / 'basic.cfg'}",
                f"-profiles={server_dir / 'profile'}",
                "-name=pontifex-multiplayer-server",
                f"-mod={';'.join(mod_names)}",
                "-world=empty",
                "-autoInit",
                "-noSound",
                "-noPause",
                "-noSplash",
            ]
            server_run = docker(
                [
                    "run",
                    "--detach",
                    "--name",
                    server_name,
                    "--label",
                    f"pontifex.run_id={run_id}",
                    "--label",
                    "pontifex.role=server",
                    "--network",
                    network,
                    "--ip",
                    server_ip,
                    "--cap-drop",
                    "ALL",
                    "--user",
                    f"{os.getuid()}:{os.getgid()}",
                    "--security-opt",
                    "no-new-privileges",
                    "--volume",
                    f"{ROOT}:{ROOT}:ro",
                    "--volume",
                    f"{RUNTIME}:{RUNTIME}:rw",
                    "--volume",
                    f"{server_dir}:{server_dir}:rw",
                    "--volume",
                    f"{dedicated.LEGACY_INSTALL}:{dedicated.LEGACY_INSTALL}:ro",
                    "--workdir",
                    str(dedicated.INSTALL_VIEW),
                    "--env",
                    f"LD_LIBRARY_PATH={dedicated.INSTALL_VIEW}:{dedicated.INSTALL_VIEW / 'linux64'}",
                    SERVER_IMAGE,
                    *server_command,
                ],
                check=False,
            )
            if server_run.returncode != 0:
                raise RuntimeError(f"server container launch failed: {server_run.stderr.strip()}")

            state = {
                "run_id": run_id,
                "network": network,
                "server_container": server_name,
                "client_container": client_name,
            }
            dedicated.atomic_json(MULTIPLAYER_STATE, state)

            server_deadline = time.monotonic() + 30
            while time.monotonic() < server_deadline:
                if "PONTIFEX_TEST|PASS|server|sqf.executed" in container_logs(server_name):
                    break
                if not container_running(server_name):
                    raise RuntimeError("server exited before mission initialization")
                time.sleep(1)

            client_mods = [
                r"Z:\pontifex\server\runtime\dependency-mods\@CBA_A3",
                r"Z:\pontifex\server\runtime\dependency-mods\@ace",
                r"Z:\pontifex\server\runtime\dependency-mods\@zen",
                r"Z:\pontifex\server\runtime\mods\@cordis",
                r"Z:\pontifex\server\runtime\mods\@fieldutils",
                r"Z:\pontifex\server\runtime\mods\@advsys",
                r"Z:\pontifex\server\runtime\mods\@vigil",
            ]
            client_args = [
                "-noLauncher",
                "-noSplash",
                "-skipIntro",
                "-noPause",
                "-noSound",
                "-noBattlEye",
                "-window",
                "-x=640",
                "-y=480",
                "-name=PontifexClientA",
                r"-profiles=Z:\run\pontifex\profile",
                f"-connect={server_ip}",
                f"-port={port}",
                f"-mod={';'.join(client_mods)}",
            ]
            client_run = docker(
                [
                    "run",
                    "--detach",
                    "--name",
                    client_name,
                    "--label",
                    f"pontifex.run_id={run_id}",
                    "--label",
                    "pontifex.role=client-a",
                    "--network",
                    network,
                    "--ip",
                    client_ip,
                    "--device",
                    "nvidia.com/gpu=0",
                    *client_security_args(),
                    "--shm-size",
                    "1g",
                    "--env",
                    "NVIDIA_DRIVER_CAPABILITIES=graphics,display,utility,compat32",
                    "--env",
                    "PONTIFEX_LOG_DIR=/run/pontifex",
                    "--volume",
                    f"{CLIENT_HOME}:/home/pontifex",
                    "--volume",
                    f"{ROOT}:/pontifex:ro",
                    "--volume",
                    f"{client_dir}:/run/pontifex:rw",
                    IMAGE,
                    "test",
                    *client_args,
                ],
                check=False,
            )
            if client_run.returncode != 0:
                raise RuntimeError(f"client container launch failed: {client_run.stderr.strip()}")

            write_network_evidence(run_dir, network, [server_name, client_name])
            manifest.update(
                {
                    "dependencies": dependencies,
                    "builds": dedicated.pbo_manifest(),
                    "port": port,
                    "network": {
                        "name": network,
                        "driver": "bridge",
                        "subnet": subnet,
                        "server": container_identity(server_name, network),
                        "client-a": container_identity(client_name, network),
                        "loopback_prevention": "client connects only to the server bridge address; no host ports are published",
                    },
                    "server_command": server_command,
                    "client_command": ["steam", "-applaunch", "107410", *client_args],
                    "gpu_start": gpu_sample(),
                }
            )
            dedicated.atomic_json(run_dir / "manifest.json", manifest)

            deadline = time.monotonic() + timeout_seconds
            server_complete = None
            client_complete = None
            server_assertions: list[dict] = []
            client_assertions: list[dict] = []
            samples = []
            next_sample = 0.0
            reason = "timeout"
            while time.monotonic() < deadline:
                server_text = container_logs(server_name)
                (server_dir / "console.log").write_text(server_text, encoding="utf-8")
                (server_dir / "server.rpt").write_text(server_text, encoding="utf-8")
                server_assertions, server_complete = dedicated.parse_protocol(server_text)
                server_assertions = [item for item in server_assertions if item["origin"] == "server"]
                if client_dir.exists():
                    client_text = combine_rpts(client_dir, client_dir / "client.rpt")
                    client_assertions, client_complete = dedicated.parse_protocol(client_text)
                    client_assertions = [item for item in client_assertions if item["origin"] == "client-a"]
                    if client_assertions and "client_process_table" not in manifest:
                        manifest["client_process_table"] = container_processes(client_name)
                        manifest["server_process_table"] = container_processes(server_name)
                        dedicated.atomic_json(run_dir / "manifest.json", manifest)
                if server_complete and client_complete:
                    reason = "complete"
                    break
                if not container_running(server_name):
                    reason = "server_exited"
                    break
                if not container_running(client_name):
                    reason = "client_exited"
                    break
                if time.monotonic() >= next_sample:
                    samples.append(
                        {
                            "at": dedicated.utc_now(),
                            "server": stats_sample(server_name),
                            "client-a": stats_sample(client_name),
                            "gpu": gpu_sample(),
                        }
                    )
                    next_sample = time.monotonic() + 5
                time.sleep(1)

            (client_dir / "console.log").write_text(container_logs(client_name), encoding="utf-8")
            server_missing, server_error = validate_origin(server_assertions, server_complete, SERVER_EXPECTED)
            client_missing, client_error = validate_origin(client_assertions, client_complete, CLIENT_EXPECTED)
            result.update(
                {
                    "assertions": server_assertions + client_assertions,
                    "origins": {
                        "server": {"complete": server_complete, "missing": server_missing},
                        "client-a": {"complete": client_complete, "missing": client_missing},
                    },
                    "resource_samples": samples,
                }
            )
            if reason != "complete":
                result["reason"] = reason
            elif server_error:
                result["reason"] = server_error
            elif client_error:
                result["reason"] = client_error
            else:
                result["status"] = "PASS"
                result["reason"] = "complete"
        except Exception as exc:
            result["reason"] = "runner_error"
            result["error"] = f"{type(exc).__name__}: {exc}"
        finally:
            if server_name:
                (server_dir / "console.log").write_text(container_logs(server_name), encoding="utf-8")
                shutil.copy2(server_dir / "console.log", server_dir / "server.rpt")
            if client_name:
                (client_dir / "console.log").write_text(container_logs(client_name), encoding="utf-8")
                combine_rpts(client_dir, client_dir / "client.rpt")
            cleanup = {
                "client_removed": validated_remove_container(client_name, run_id),
                "server_removed": validated_remove_container(server_name, run_id),
                "network_removed": validated_remove_network(network, run_id) if network else True,
            }
            cleanup["state_removed"] = all(cleanup.values())
            if cleanup["state_removed"]:
                MULTIPLAYER_STATE.unlink(missing_ok=True)
            result["cleanup"] = cleanup
            manifest["finished_at"] = dedicated.utc_now()
            manifest["gpu_finish"] = gpu_sample()
            dedicated.atomic_json(run_dir / "manifest.json", manifest)
            if not all(cleanup.values()):
                result["status"] = "FAIL"
                result["reason"] = "cleanup_failed"
            write_result(run_dir, result)
    return 0 if result["status"] == "PASS" else 1


def show_runtime_status() -> int:
    if not MULTIPLAYER_STATE.is_file():
        print("Pontifex multiplayer runtime: stopped (no state file)")
        return 0
    try:
        state = json.loads(MULTIPLAYER_STATE.read_text())
    except (OSError, json.JSONDecodeError):
        print("Pontifex multiplayer runtime: malformed state", file=sys.stderr)
        return 1
    server = container_inspect(state.get("server_container", ""))
    client = container_inspect(state.get("client_container", ""))
    print(f"Pontifex multiplayer runtime: run {state.get('run_id')}")
    print(f"server container running: {bool(server and server['State']['Running'])}")
    print(f"client container running: {bool(client and client['State']['Running'])}")
    print(f"network: {state.get('network')}")
    run_dir = RUNS / str(state.get("run_id", ""))
    client_log = run_dir / "client-a" / "console.log"
    process_text = container_processes(state.get("client_container", "")) if client else ""
    phase = "steam_booting"
    if re.search(r"(?:wine|proton|arma3)", process_text, re.IGNORECASE):
        phase = "proton_or_arma_running"
    elif client_log.is_file() and "PONTIFEX_TEST|" in client_log.read_text(errors="replace"):
        phase = "client_assertions_emitting"
    print(f"client phase: {phase}")
    print(f"evidence: {run_dir}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    test = sub.add_parser("test")
    test.add_argument("--force-failure", action="store_true")
    test.add_argument("--timeout", type=int, default=int(os.environ.get("PONTIFEX_MULTIPLAYER_TIMEOUT", "300")))
    client = sub.add_parser("client")
    client.add_argument("action", choices=("status", "image", "preflight", "login", "stop-login"))
    sub.add_parser("status")
    sub.add_parser("stop")
    args = parser.parse_args()
    if args.command == "test":
        return run_multiplayer(args.force_failure, args.timeout)
    if args.command == "client":
        if args.action == "status":
            return show_client_status()
        if args.action == "image":
            return build_image()
        if args.action == "preflight":
            ok, output = gpu_preflight()
            print(output)
            return 0 if ok else 1
        if args.action == "login":
            return start_login()
        if args.action == "stop-login":
            return stop_login()
    if args.command == "status":
        return show_runtime_status()
    if args.command == "stop":
        cleanup = clean_multiplayer_state()
        print(json.dumps(cleanup, sort_keys=True))
        return 0 if all(cleanup.values()) else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

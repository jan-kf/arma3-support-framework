#!/usr/bin/env python3
"""One-real-player Pontifex multiplayer experiment and client provisioning."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import shutil
import socket
import subprocess
import sys
import time
import uuid

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tribunal.assertions.protocol import validate_origin
from tribunal.mission.entities import render_typed_entities
from tribunal.mission.projectiles import direct_fixture_sqf
from tribunal.discovery import discover
from tribunal.reporting.evidence import EvidenceAttachment, attach_evidence
from tribunal.runner.model import ClientIdentity, TierPlan as TestPlan, client_identity_map

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
FEATURE_SCENARIOS = discover([
    ROOT / "source" / "advanced-systems" / "tests" / "tribunal",
    ROOT / "source" / "field-utilities" / "tests" / "tribunal",
    ROOT / "source" / "visual-support-tablet" / "tests" / "tribunal",
])
FRAMEWORK_SCENARIOS = discover([ROOT / "tribunal" / "scenarios"])
ALL_SCENARIOS = {**FRAMEWORK_SCENARIOS, **FEATURE_SCENARIOS}
APS_SCENARIO = FEATURE_SCENARIOS["aps-intercept"]
STEAM_DLC_CATALOG = ROOT / "server" / "steam-arma3-dlc-catalog.json"
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
E2E_SERVER_EXPECTED = {
    "sqf.executed",
    "e2e.token",
    "e2e.playerExists",
    "e2e.playerIdentity",
    "e2e.vehicleExists",
    "e2e.actionVerified",
    "e2e.finalState",
}
E2E_CLIENT_EXPECTED = {
    "e2e.initPlayerLocal",
    "e2e.playerIdentity",
    "e2e.token",
    "e2e.vehicleResolved",
    "e2e.actionExecuted",
    "e2e.finalState",
}


SMOKE_PLAN = TestPlan(
    "smoke",
    frozenset({"smoke.init.sqf", "smoke.token", "smoke.player", "smoke.ack"}),
    frozenset({"smoke.initPlayerLocal", "smoke.identity", "smoke.token", "smoke.ack"}),
)
INTEGRATION_PLAN = TestPlan(
    "integration",
    SMOKE_PLAN.server_expected | frozenset({"integration.missionNamespace", "integration.config", "integration.roundTrip"}),
    SMOKE_PLAN.client_expected | frozenset({"integration.hasInterface", "integration.roundTrip"}),
    selected=frozenset({"mission-namespace", "config", "round-trip"}),
)
GAMEPLAY_PLAN = TestPlan(
    "gameplay",
    SMOKE_PLAN.server_expected | frozenset({"gameplay.vehicleCreated", "gameplay.driverAuthoritative"}) | frozenset().union(*(scenario.server_expected for scenario in FEATURE_SCENARIOS.values())),
    SMOKE_PLAN.client_expected | frozenset({"gameplay.vehicleResolved", "gameplay.enterVehicle"}) | frozenset().union(*(scenario.client_expected for scenario in FEATURE_SCENARIOS.values())),
    gameplay=True,
    selected=frozenset({"vehicle-entry", *FEATURE_SCENARIOS}),
    project_mods=True,
)
CAPABILITY_PLAN = TestPlan(
    "capability",
    SMOKE_PLAN.server_expected | frozenset().union(*(scenario.server_expected for scenario in FRAMEWORK_SCENARIOS.values())),
    SMOKE_PLAN.client_expected | frozenset().union(*(scenario.client_expected for scenario in FRAMEWORK_SCENARIOS.values())),
    gameplay=True,
    selected=frozenset(FRAMEWORK_SCENARIOS),
)
LIVE_PLAN = TestPlan("live", SMOKE_PLAN.server_expected, SMOKE_PLAN.client_expected, selected=frozenset({"lifecycle"}), project_mods=True)
TEST_PLANS = {plan.name: plan for plan in (SMOKE_PLAN, INTEGRATION_PLAN, GAMEPLAY_PLAN, CAPABILITY_PLAN, LIVE_PLAN)}
TIER_TESTS = {
    "smoke": frozenset({"lifecycle"}),
    "integration": frozenset({"mission-namespace", "config", "round-trip"}),
    "gameplay": frozenset({"vehicle-entry", *FEATURE_SCENARIOS}),
    "capability": frozenset(FRAMEWORK_SCENARIOS),
    "live": frozenset({"lifecycle"}),
}


def select_plan(name: str, selected: str | None = None) -> TestPlan:
    """Compose a tier from independently selectable in-mission test IDs."""
    base = TEST_PLANS[name]
    chosen = TIER_TESTS[name] if not selected else frozenset(item.strip() for item in selected.split(",") if item.strip())
    unknown = chosen - TIER_TESTS[name]
    if unknown or not chosen:
        raise ValueError(f"unknown {name} test selection: {', '.join(sorted(unknown)) or '<empty>'}")
    server = set(SMOKE_PLAN.server_expected)
    client = set(SMOKE_PLAN.client_expected)
    if name == "integration":
        if "mission-namespace" in chosen:
            server.add("integration.missionNamespace")
        if "config" in chosen:
            server.add("integration.config")
            client.add("integration.hasInterface")
        if "round-trip" in chosen:
            server.add("integration.roundTrip")
            client.add("integration.roundTrip")
    elif name == "gameplay":
        if "vehicle-entry" in chosen:
            server.update({"gameplay.vehicleCreated", "gameplay.driverAuthoritative"})
            client.update({"gameplay.vehicleResolved", "gameplay.enterVehicle"})
        for identifier in chosen.intersection(FEATURE_SCENARIOS):
            scenario = FEATURE_SCENARIOS[identifier]
            server.update(scenario.server_expected)
            client.update(scenario.expected_for("client-a"))
    elif name == "capability":
        for identifier in chosen:
            scenario = FRAMEWORK_SCENARIOS[identifier]
            server.update(scenario.server_expected)
            client.update(scenario.expected_for("client-a"))
    return TestPlan(
        name, frozenset(server), frozenset(client), gameplay=name in {"gameplay", "capability"}, selected=chosen,
        project_mods=name == "gameplay" and any(
            ALL_SCENARIOS[item].requires_project_mods
            for item in chosen.intersection(FEATURE_SCENARIOS)
        ),
    )


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
    character_payload = executable.parent / "Addons" / "characters_f.pbo" if executable else None
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
        "character_payload": str(character_payload) if character_payload and character_payload.is_file() else None,
        "steam_build_id": build_id,
        "proton": str(proton) if proton else None,
    }


def client_component_policy() -> dict:
    """Map App 233780 official components to the authenticated client's banks.

    Matching is by the installed PBO inventory, which accommodates layout
    differences such as server ``enoch`` versus client ``Contact`` without
    encoding DLC names.  Client-only banks are not auto-loaded: they are
    Creator/community DLC or user-selected content and remain explicit.
    """
    executable = find_client_executable()
    if executable is None:
        raise RuntimeError("licensed Arma 3 client executable not found")
    root = executable.parent
    client_banks = []
    for directory in sorted(root.iterdir(), key=lambda item: item.name.casefold()):
        addons = next((path for path in directory.iterdir() if path.name.casefold() == "addons"), None) if directory.is_dir() else None
        if addons and addons.is_dir() and directory.name.casefold() != "addons":
            pbos = {
                path.name.casefold()
                for pattern in ("*.pbo", "*.ebo")
                for path in addons.glob(pattern)
                if path.is_file()
            }
            if pbos:
                client_banks.append({"path": directory, "addons": addons, "pbos": pbos})
    mapped = []
    used = set()
    for component in dedicated.official_component_policy()["official_components"]:
        expected = {name.casefold() for name in component["pbos"]}
        candidates = [
            bank
            for bank in client_banks
            if bank["path"] not in used and expected.intersection(bank["pbos"])
        ]
        if not candidates:
            raise RuntimeError(f"client is missing official App 233780 component: {component['id']}")
        chosen = max(
            candidates,
            key=lambda bank: (
                len(expected.intersection(bank["pbos"])),
                bank["path"].name.casefold() == component["id"],
            ),
        )
        used.add(chosen["path"])
        mapped.append(
            {
                "id": component["id"],
                "server_path": str(component["path"]),
                "client_path": str(chosen["path"]),
                "client_addons": str(chosen["addons"]),
                "shared_pbos": sorted(expected.intersection(chosen["pbos"])),
            }
        )
    catalog = json.loads(STEAM_DLC_CATALOG.read_text(encoding="utf-8"))["apps"]

    def labels(name: str) -> set[str]:
        words = re.findall(r"[a-z0-9]+", name.casefold())
        words = [word for word in words if word not in {"arma", "3", "creator", "dlc"}]
        return {"".join(words), "".join(word[0] for word in words)}

    account_official = []
    excluded = []
    for bank in client_banks:
        if bank["path"] in used:
            continue
        match = next((item for item in catalog.values() if bank["path"].name.casefold() in labels(item["name"])), None)
        if match and match["developers"] == ["Bohemia Interactive"] and match.get("default_enabled", True):
            account_official.append({"id": bank["path"].name.casefold(), "client_path": str(bank["path"]), "client_addons": str(bank["addons"]), "source": "authenticated App 107410 DLC"})
        else:
            excluded.append(
                {
                    "path": str(bank["path"]),
                    "reason": (
                        "Creator/community DLC"
                        if match and match["developers"] != ["Bohemia Interactive"]
                        else "official DLC excluded from the default policy"
                        if match
                        else "unclassified client-only component"
                    ),
                    **({"steam_name": match["name"], "developers": match["developers"]} if match else {}),
                }
            )
    return {
        "core": str(root / "Addons"),
        "official_components": mapped + account_official,
        "excluded_client_only_components": excluded,
        "workshop_or_user_mods": "explicit-only",
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


def run_join_adapter(
    container: str, output: Path, *, server_ip: str, server_port: int
) -> subprocess.CompletedProcess:
    """Pass the runtime bridge endpoint directly to the internal join adapter."""
    return docker(
        [
            "exec", container, "/opt/pontifex/vnc-join-adapter.py",
            "--output", "/run/pontifex/join-adapter.json",
            "--join", server_ip, str(server_port),
        ],
        check=False,
    )


def write_result(run_dir: Path, result: dict) -> None:
    result["finished_at"] = dedicated.utc_now()
    dedicated.atomic_json(run_dir / "results.json", result)
    print(f"result: {result['status']} ({result['reason']})")
    print(f"evidence: {run_dir}")


def prepare_live_extension(run_dir: Path) -> Path:
    """Build the fixed-path read-only Live Mode extension for this run only."""
    source = ROOT / "tools" / "pontifex_live_extension.c"
    output_dir = run_dir / "live-extension"
    output_dir.mkdir(mode=0o700)
    output = output_dir / "pontifex_live_x64.so"
    build = subprocess.run(
        ["gcc", "-shared", "-fPIC", "-O2", "-o", str(output), str(source)],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    (output_dir / "build.log").write_text(build.stdout or "", encoding="utf-8")
    if build.returncode != 0 or not output.is_file():
        raise RuntimeError("failed to build the Developer Live command extension")
    output.chmod(0o555)
    # Arma 3 builds have used both names while probing Linux extensions.
    # Both files are identical and live only in this disposable run.
    shutil.copy2(output, output_dir / "pontifex_live.so")
    (output_dir / "pontifex_live.so").chmod(0o555)
    return output_dir


def write_tier_mission(destination: Path, token: str, plan: TestPlan, *, live: bool = False) -> dict:
    """Generate a fresh, vanilla mission for one scalable test tier.

    The runner is intentionally mission-local: a test batch starts Arma once,
    then dispatches every selected assertion inside the already-running
    session.  A tier's names are stable machine-readable contracts, while the
    token makes every individual run distinguishable from stale artifacts.
    """
    destination.mkdir(parents=True, exist_ok=False)
    position_x = 4683 + (int(token[-4:], 16) % 30)
    player_position = [position_x, 16, 2778]
    requested_spawns = {
        ALL_SCENARIOS[item].metadata.get("player_spawn")
        for item in plan.selected.intersection(ALL_SCENARIOS)
        if ALL_SCENARIOS[item].metadata.get("player_spawn")
    }
    if len(requested_spawns) > 1:
        raise RuntimeError(f"selected scenarios require incompatible player spawns: {sorted(requested_spawns)}")
    if requested_spawns:
        parts = [float(value) for value in next(iter(requested_spawns)).split(",")]
        if len(parts) != 3:
            raise RuntimeError("scenario player_spawn must contain exactly x,y,z")
        player_position = parts
    player_x, player_y, player_z = player_position
    selected_scenarios = [ALL_SCENARIOS[item] for item in sorted(plan.selected) if item in ALL_SCENARIOS]
    mission_entities = tuple(entity for scenario in selected_scenarios for entity in scenario.mission_entities)
    mission_syncs = tuple(sync for scenario in selected_scenarios for sync in scenario.mission_syncs)
    entity_names = [entity.name for entity in mission_entities]
    if len(set(entity_names)) != len(entity_names):
        raise RuntimeError("selected scenarios contain duplicate mission entity names")
    vehicle_entity = ""
    base_entity_count = 1
    addon_rows = [("A3_Characters_F", "Characters", "Bohemia Interactive")]
    if plan.gameplay:
        addon_rows.append(("A3_Soft_F", "Soft Vehicles", "Bohemia Interactive"))
        base_entity_count = 2
        vehicle_entity = f""" class Item1 {{ dataType="Object"; class PositionInfo {{ position[]={{ {position_x + 8},16,2778 }}; }}; side="Empty"; flags=7; class Attributes {{ name="PONTIFEX_TIER_vehicle"; }}; id=2; type="C_Offroad_01_F"; }};"""
    for entity in mission_entities:
        if entity.addon not in {row[0] for row in addon_rows}:
            addon_rows.append((entity.addon, entity.addon, "Tribunal fixture"))
    addons = ",".join("\"{}\"".format(addon) for addon, _, _ in addon_rows)
    metadata_items = " ".join(
        f"class Item{index} {{ className=\"{addon}\"; name=\"{name}\"; author=\"{author}\"; }};"
        for index, (addon, name, author) in enumerate(addon_rows)
    )
    metadata = f"items={len(addon_rows)}; {metadata_items}"
    fixture_entities, fixture_connections = render_typed_entities(
        mission_entities, mission_syncs, first_item=base_entity_count
    )
    mission_sqm = f'''version=54;
binarizationWanted=0;
sourceName="Pontifex{plan.name.title()}_{token}";
addons[]={{ {addons} }};
class AddonsMetaData {{ class List {{ {metadata} }}; }};
randomSeed={int(token[-8:], 16)};
class Mission {{
 class Intel {{ year=2035; month=7; day=6; hour=12; minute=0; startWeather=0; forecastWeather=0; }};
 class Entities {{ items={base_entity_count + len(mission_entities)};
  class Item0 {{ dataType="Group"; side="West"; class Entities {{ items=1; class Item0 {{ dataType="Object"; class PositionInfo {{ position[]={{ {player_x},{player_y},{player_z} }}; }}; side="West"; flags=7; class Attributes {{ isPlayer=1; }}; id=1; type="B_Soldier_A_F"; }}; }}; class Attributes {{}}; id=0; }};{vehicle_entity}{fixture_entities}
 }};{fixture_connections}
}};
'''
    requested_respawn = {
        ALL_SCENARIOS[item].metadata.get("respawn_on_start")
        for item in plan.selected.intersection(ALL_SCENARIOS)
        if ALL_SCENARIOS[item].metadata.get("respawn_on_start") is not None
    }
    if len(requested_respawn) > 1:
        raise RuntimeError(f"selected scenarios require incompatible respawn policies: {sorted(requested_respawn)}")
    respawn_on_start = next(iter(requested_respawn), "1")
    if respawn_on_start not in {"0", "1"}:
        raise RuntimeError("scenario respawn_on_start must be 0 or 1")
    description = (
        "class Header { gameType = COOP; minPlayers = 1; maxPlayers = 1; };\n"
        f"skipLobby = 1;\nrespawn = 3;\nrespawnOnStart = {respawn_on_start};\ndisabledAI = 1;\n"
    )
    integration_server = ""
    integration_client = ""
    if plan.name == "integration":
        integration_server = ""
        integration_client = ""
        if "mission-namespace" in plan.selected:
            integration_server += '''
 missionNamespace setVariable ["PONTIFEX_TIER_integrationValue", _token];
 ["integration.missionNamespace", (missionNamespace getVariable ["PONTIFEX_TIER_integrationValue", ""]) isEqualTo _token, "round-trip mission namespace"] call _assert;
'''
        if "config" in plan.selected:
            integration_server += '''
 ["integration.config", isClass (configFile >> "CfgVehicles" >> "B_Soldier_A_F"), "CfgVehicles/B_Soldier_A_F"] call _assert;
'''
            integration_client += '''
 ["integration.hasInterface", hasInterface isEqualTo true, "client interface"] call _assert;
'''
        if "round-trip" in plan.selected:
            integration_server += '''
 [_token] remoteExecCall ["PONTIFEX_TIER_fnc_integrationRequest", owner _player];
 private _integrationDeadline = diag_tickTime + 20;
 waitUntil { uiSleep 0.1; (missionNamespace getVariable ["PONTIFEX_TIER_integrationAck", ""]) isEqualTo _token || diag_tickTime > _integrationDeadline };
 ["integration.roundTrip", (missionNamespace getVariable ["PONTIFEX_TIER_integrationAck", ""]) isEqualTo _token, "client-to-server event"] call _assert;
'''
            integration_client += '''
 PONTIFEX_TIER_fnc_integrationRequest = { params ["_requestToken"]; missionNamespace setVariable ["PONTIFEX_TIER_integrationRequest", _requestToken]; };
 private _integrationDeadline = diag_tickTime + 20;
 waitUntil { uiSleep 0.1; (missionNamespace getVariable ["PONTIFEX_TIER_integrationRequest", ""]) isEqualTo _token || diag_tickTime > _integrationDeadline };
 private _integrationOk = (missionNamespace getVariable ["PONTIFEX_TIER_integrationRequest", ""]) isEqualTo _token;
 ["integration.roundTrip", _integrationOk, "server-to-client event"] call _assert;
 if (_integrationOk) then { missionNamespace setVariable ["PONTIFEX_TIER_integrationAck", _token]; [_token] remoteExecCall ["PONTIFEX_TIER_fnc_integrationAck", 2]; };
'''
    gameplay_server = ""
    gameplay_client = ""
    if plan.name == "gameplay" and "vehicle-entry" in plan.selected:
        gameplay_server = '''
 private _vehicleDeadline = diag_tickTime + 20;
 waitUntil { uiSleep 0.1; !isNil "PONTIFEX_TIER_vehicle" || diag_tickTime > _vehicleDeadline };
 private _vehicle = missionNamespace getVariable ["PONTIFEX_TIER_vehicle", objNull];
 ["gameplay.vehicleCreated", !isNull _vehicle && {typeOf _vehicle isEqualTo "C_Offroad_01_F"}, format ["netId=%1", netId _vehicle]] call _assert;
missionNamespace setVariable ["PONTIFEX_TIER_vehicleNetId", netId _vehicle, true];
PONTIFEX_TIER_fnc_gameplayAction = { params ["_receivedToken", "_vehicleId"]; missionNamespace setVariable ["PONTIFEX_TIER_gameplayAction", [_receivedToken, _vehicleId, remoteExecutedOwner]]; };
private _actionDeadline = diag_tickTime + 30;
waitUntil { uiSleep 0.1; !(missionNamespace getVariable ["PONTIFEX_TIER_gameplayAction", []] isEqualTo []) || diag_tickTime > _actionDeadline };
private _action = missionNamespace getVariable ["PONTIFEX_TIER_gameplayAction", []];
private _actionOwner = _action param [2, -1];
private _actionPlayer = (allPlayers select { owner _x isEqualTo _actionOwner }) param [0, objNull];
private _actionOk = !isNull _vehicle && {!isNull _actionPlayer} && {(count _action) isEqualTo 3} && {(_action # 0) isEqualTo _token} && {(_action # 1) isEqualTo netId _vehicle};
if (!isNull _actionPlayer) then { _player = _actionPlayer; };
if (_actionOk) then { _player moveInDriver _vehicle; };
private _playerUid = getPlayerUID _player;
private _driverDeadline = diag_tickTime + 30;
waitUntil { uiSleep 0.1; !isNull _vehicle && {!isNull driver _vehicle} && {_playerUid isNotEqualTo ""} && {(getPlayerUID (driver _vehicle)) isEqualTo _playerUid} || diag_tickTime > _driverDeadline };
private _driverUid = if (isNull _vehicle || {isNull driver _vehicle}) then {""} else {getPlayerUID (driver _vehicle)};
["gameplay.driverAuthoritative", _actionOk && {!isNull _vehicle} && {_playerUid isNotEqualTo ""} && {_driverUid isEqualTo _playerUid}, format ["driver=%1|driverNetId=%2|driverUid=%3|playerNetId=%4|playerUid=%5|owner=%6|vehicle=%7|action=%8", if (isNull _vehicle || {isNull driver _vehicle}) then {"<none>"} else {name (driver _vehicle)}, if (isNull _vehicle || {isNull driver _vehicle}) then {""} else {netId (driver _vehicle)}, _driverUid, netId _player, _playerUid, _actionOwner, netId _vehicle, _action]] call _assert;
'''
        gameplay_client = '''
 private _vehicleDeadline = diag_tickTime + 30;
 waitUntil { uiSleep 0.1; !isNil {missionNamespace getVariable "PONTIFEX_TIER_vehicleNetId"} || diag_tickTime > _vehicleDeadline };
 private _vehicleId = missionNamespace getVariable ["PONTIFEX_TIER_vehicleNetId", ""];
 private _vehicle = if (_vehicleId isEqualType "" && {_vehicleId isNotEqualTo ""}) then {objectFromNetId _vehicleId} else {objNull};
 private _resolveDeadline = diag_tickTime + 30;
 waitUntil { uiSleep 0.1; !isNull _vehicle || diag_tickTime > _resolveDeadline };
 ["gameplay.vehicleResolved", !isNull _vehicle && {(netId _vehicle) isEqualTo _vehicleId}, format ["netId=%1", _vehicleId]] call _assert;
 if (!isNull _vehicle) then { player moveInDriver _vehicle; };
 private _actionDeadline = diag_tickTime + 20;
 waitUntil { uiSleep 0.1; !isNull _vehicle && {driver _vehicle isEqualTo player} || diag_tickTime > _actionDeadline };
 private _actionOk = !isNull _vehicle && {driver _vehicle isEqualTo player} && {vehicle player isEqualTo _vehicle};
 ["gameplay.enterVehicle", _actionOk, format ["vehicle=%1", netId _vehicle]] call _assert;
[_token, netId _vehicle] remoteExecCall ["PONTIFEX_TIER_fnc_gameplayAction", 2];
'''
    aps_server = ""
    aps_client = ""
    if plan.name == "gameplay" and "aps-intercept" in plan.selected:
        # Deterministic direct shotRocket fixture. Direct spawns must be registered
        # explicitly because the production tracker normally learns only Fired events.
        aps_server = (
            r'''
private _newTarget = {
    params ["_position", ["_fuel", 0]];
    private _target = "O_MBT_02_cannon_F" createVehicle _position;
    _target setFuel _fuel; _target engineOn false; _target allowDamage true; _target setDamage 0;
    sleep 3; _target setVelocity [0, 0, 0]; _target
};
'''
            + direct_fixture_sqf()
            + r'''
private _injectThreat = {
    // APS-only wrapper: geometry and explicit APS registration.  Tribunal owns
    // creation, launch-state verification, telemetry, impact evidence, and cleanup.
    params ["_target", "_label", ["_lateral", 0], ["_height", 0], ["_away", false], ["_minimumTerrainClearance", 0], ["_aimHeight", -1e9]];
    if (_aimHeight isEqualTo -1e9) then { _aimHeight = _height; };
    private _targetASL = getPosASL _target;
    private _origin = _targetASL vectorAdd [90, _lateral, _height];
    // Aim from the same terrain-cleared origin Tribunal will launch from.
    // This matters only for the soft-kill descending case (clearance > 0).
    private _originTerrain = getTerrainHeightASL _origin;
    if ((_origin # 2) < (_originTerrain + _minimumTerrainClearance)) then { _origin set [2, _originTerrain + _minimumTerrainClearance]; };
    private _aim = _targetASL vectorAdd [0, _lateral, _aimHeight];
    private _direction = vectorNormalized (_aim vectorDiff _origin);
    if (_away) then { _direction = vectorNormalized (_origin vectorDiff _targetASL); };
    private _launch = ["R_PG32V_F", _origin, _direction, 250, _label, _target, _minimumTerrainClearance] call TRIBUNAL_fnc_directProjectileLaunch;
    private _projectile = _launch # 0;
    private _tracked = !isNull _projectile && {[_projectile] call YOSHI_fnc_apsTrackProjectileLocal};
    [_projectile, _launch # 1, _tracked, _launch # 3, _launch # 2]
};
private _controlsArmDeadline = diag_tickTime + 30;
waitUntil {
    uiSleep 0.05;
    (missionNamespace getVariable ["PONTIFEX_APS_CONTROLS_ARMED", ""]) isEqualTo _token || {diag_tickTime > _controlsArmDeadline}
};
private _apsVehicle = [[3000, 4000, 0], 1] call _newTarget;
private _compositionControlVehicle = [[3000, 4020, 0], 0] call _newTarget;
[_apsVehicle, 2] call YOSHI_fnc_apsEnableVehicle;
[] call YOSHI_fnc_apsEnsureLocalRuntime;
private _chargesBefore = [_apsVehicle] call YOSHI_fnc_apsHardKillChargeCount;
private _hard = [_apsVehicle, "hardkill"] call _injectThreat;
private _rocket = _hard # 0;
private _projectileUid = [_rocket] call YOSHI_fnc_apsProjectileUid;
["aps.positive.projectileSpawned", !isNull _rocket && {_projectileUid isNotEqualTo ""} && {(_hard # 2)} && {(_hard # 4)} && {local _rocket} && {local _apsVehicle}, format ["uid=%1|tracked=%2|vehicleLocal=%3|projectileLocal=%4|initial=%5", _projectileUid, _hard # 2, local _apsVehicle, local _rocket, _hard # 3]] call _assert;
private _deadline = diag_tickTime + 4; private _threat = []; private _hardEvent = false;
waitUntil { uiSleep 0.005; if (!isNull _rocket) then { _threat = [_apsVehicle, _rocket] call YOSHI_fnc_apsEvaluateProjectileThreat; }; _hardEvent = (missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]) findIf {(_x # 0) isEqualTo (netId _apsVehicle) && {(_x # 1) isEqualTo _projectileUid} && {(_x # 2) isEqualTo "hardkill"}} >= 0; _hardEvent || diag_tickTime > _deadline };
["aps.positive.collisionCourse", !(_threat isEqualTo []) || _hardEvent, format ["threat=%1|ledgerProvesPredicate=%2", _threat, _hardEvent]] call _assert;
["aps.positive.engaged", _hardEvent, format ["vehicle=%1|projectile=%2|events=%3", netId _apsVehicle, _projectileUid, missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]]] call _assert;
private _chargesAfter = [_apsVehicle] call YOSHI_fnc_apsHardKillChargeCount;
["aps.positive.neutralized", _hardEvent && {isNull _rocket}, format ["projectile=%1|null=%2", _projectileUid, isNull _rocket]] call _assert;
["aps.positive.chargeConsumed", _chargesAfter isEqualTo (_chargesBefore - 1), format ["before=%1|after=%2", _chargesBefore, _chargesAfter]] call _assert;
["aps.positive.protected", !(missionNamespace getVariable [_hard # 1, false]), format ["impact=%1", missionNamespace getVariable [_hard # 1, false]]] call _assert;
private _controlVehicle = [[3000, 4200, 0], 0] call _newTarget;
private _eventsBeforeControl = +(missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]);
private _control = [_controlVehicle, "disabled"] call _injectThreat;
private _controlRocket = _control # 0; private _controlUid = [_controlRocket] call YOSHI_fnc_apsProjectileUid; private _controlLocal = !isNull _controlRocket && {local _controlRocket};
private _controlDeadline = diag_tickTime + 4;
waitUntil { uiSleep 0.01; (missionNamespace getVariable [_control # 1, false]) || isNull _controlRocket || diag_tickTime > _controlDeadline };
["aps.control.disabledImpact", (missionNamespace getVariable [_control # 1, false]) && {(_control # 2)} && {(_control # 4)} && {_controlLocal} && {local _controlVehicle}, format ["rocket=%1|vehicleLocal=%2|projectileLocal=%3", _controlUid, local _controlVehicle, local _controlRocket]] call _assert;
["aps.control.disabledNoEngagement", (missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]) isEqualTo _eventsBeforeControl, "disabled control"] call _assert;
private _outsideEvents = +(missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]); private _outsideCharges = [_apsVehicle] call YOSHI_fnc_apsHardKillChargeCount;
private _outside = [_apsVehicle, "outside", 35, 20] call _injectThreat; private _outsideRocket = _outside # 0; sleep 0.1;
private _outsideThreat = [_apsVehicle, _outsideRocket] call YOSHI_fnc_apsEvaluateProjectileThreat;
["aps.control.outsideEnvelope", !isNull _outsideRocket && {vectorMagnitude (velocity _outsideRocket) >= 10} && {(_outside # 2)} && {(_outside # 4)} && {local _outsideRocket} && {_outsideThreat isEqualTo []} && {(missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]) isEqualTo _outsideEvents} && {([_apsVehicle] call YOSHI_fnc_apsHardKillChargeCount) isEqualTo _outsideCharges}, format ["threat=%1|speed=%2", _outsideThreat, if (isNull _outsideRocket) then {0} else {vectorMagnitude velocity _outsideRocket}]] call _assert;
if (!isNull _outsideRocket) then {deleteVehicle _outsideRocket};
private _awayEvents = +(missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]); private _awayCharges = [_apsVehicle] call YOSHI_fnc_apsHardKillChargeCount;
private _away = [_apsVehicle, "away", 0, 20, true] call _injectThreat; private _awayRocket = _away # 0; sleep 0.1;
private _awayThreat = [_apsVehicle, _awayRocket] call YOSHI_fnc_apsEvaluateProjectileThreat;
["aps.control.directionAway", !isNull _awayRocket && {(_away # 2)} && {(_away # 4)} && {local _awayRocket} && {_awayThreat isEqualTo []} && {(missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]) isEqualTo _awayEvents} && {([_apsVehicle] call YOSHI_fnc_apsHardKillChargeCount) isEqualTo _awayCharges}, format ["threat=%1|velocity=%2", _awayThreat, if (isNull _awayRocket) then {[]} else {velocity _awayRocket}]] call _assert;
if (!isNull _awayRocket) then {deleteVehicle _awayRocket};
private _softVehicle = [[3000, 4400, 0], 1] call _newTarget;
[_softVehicle, 0] call YOSHI_fnc_apsEnableVehicle; [_softVehicle, false] call YOSHI_fnc_apsSetHardKillState; [_softVehicle, true] call YOSHI_fnc_apsSetSoftKillState;
private _fuelBefore = fuel _softVehicle; private _soft = [_softVehicle, "softkill", 0, 0, false, 8, 0] call _injectThreat; private _softRocket = _soft # 0; private _softUid = [_softRocket] call YOSHI_fnc_apsProjectileUid; private _lastPreEventVelocity = []; private _velocityBefore = []; private _velocityAfter = []; private _softEvent = false; private _eventFrame = -1; private _softDeadline = diag_tickTime + 4;
diag_log format ["PONTIFEX_APS_FIXTURE|softkill|SAMEFRAME|projectile=%1|exists=%2|position=%3|velocity=%4|speed=%5|local=%6|distance=%7|terrain=%8|clearance=%9", _softUid, !isNull _softRocket, if (isNull _softRocket) then {[]} else {getPosASL _softRocket}, if (isNull _softRocket) then {[]} else {velocity _softRocket}, if (isNull _softRocket) then {0} else {vectorMagnitude velocity _softRocket}, !isNull _softRocket && {local _softRocket}, if (isNull _softRocket) then {-1} else {_softRocket distance _softVehicle}, if (isNull _softRocket) then {-1} else {getTerrainHeightASL (getPosASL _softRocket)}, if (isNull _softRocket) then {-1} else {((getPosASL _softRocket) # 2) - getTerrainHeightASL (getPosASL _softRocket)}];
waitUntil { uiSleep 0.005; if (!isNull _softRocket && {!_softEvent}) then { _lastPreEventVelocity = velocity _softRocket; private _candidate = [_softVehicle, _softRocket] call YOSHI_fnc_apsEvaluateProjectileThreat; _softEvent = (missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]) findIf {(_x # 0) isEqualTo (netId _softVehicle) && {(_x # 1) isEqualTo _softUid} && {(_x # 2) isEqualTo "softkill"}} >= 0; if (_softEvent) then { _velocityBefore = _lastPreEventVelocity; _eventFrame = diag_frameNo; diag_log format ["PONTIFEX_APS_FIXTURE|softkill|EVENT|projectile=%1|threat=%2|before=%3|frame=%4", _softUid, _candidate, _velocityBefore, _eventFrame]; }; }; if (_softEvent && {!isNull _softRocket} && {diag_frameNo > _eventFrame} && {_velocityAfter isEqualTo []}) then { _velocityAfter = velocity _softRocket; diag_log format ["PONTIFEX_APS_FIXTURE|softkill|NEXTFRAME|projectile=%1|after=%2|speed=%3|frame=%4", _softUid, _velocityAfter, vectorMagnitude _velocityAfter, diag_frameNo]; }; (_softEvent && {!(_velocityAfter isEqualTo [])}) || diag_tickTime > _softDeadline };
sleep 0.1; private _postDeflectionPosition = if (isNull _softRocket) then {[]} else {getPosASL _softRocket};
["aps.softkill.deflection", _softEvent && {!isNull _softRocket} && {(_soft # 2)} && {(_soft # 4)} && {local _softRocket} && {!(_velocityBefore isEqualTo [])} && {!(_velocityAfter isEqualTo [])} && {(_velocityBefore distance _velocityAfter) > 0.1} && {(fuel _softVehicle) isEqualTo (_fuelBefore - YOSHI_APS_SOFTKILL_FUEL_COST)} && {!(missionNamespace getVariable [_soft # 1, false])}, format ["uid=%1|before=%2|after=%3|fuel=%4:%5|postPosition=%6", _softUid, _velocityBefore, _velocityAfter, _fuelBefore, fuel _softVehicle, _postDeflectionPosition]] call _assert;
if (!isNull _softRocket) then {deleteVehicle _softRocket};
private _controlsStartCharges = [_apsVehicle] call YOSHI_fnc_apsHardKillChargeCount;
missionNamespace setVariable ["PONTIFEX_APS_CONTROLS_FIXTURE", [_token, netId _apsVehicle, _controlsStartCharges, netId _compositionControlVehicle], true];
private _operatorDeadline = diag_tickTime + 20;
waitUntil {
    uiSleep 0.05;
    ((missionNamespace getVariable ["PONTIFEX_APS_CONTROLS_PHASE", ""]) isEqualTo "positioned" && {(_player distance _apsVehicle) <= YOSHI_APS_OPERATOR_RANGE})
        || {diag_tickTime > _operatorDeadline}
};
missionNamespace setVariable ["PONTIFEX_APS_CONTROLS_PHASE", "operator-ready", true];
private _hardOffDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["PONTIFEX_APS_CONTROLS_PHASE", ""]) isEqualTo "hard-off" || {diag_tickTime > _hardOffDeadline}};
private _offEvents = +(missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]);
private _offThreat = [_apsVehicle, "controls-off"] call _injectThreat;
private _offRocket = _offThreat # 0;
private _offUid = [_offRocket] call YOSHI_fnc_apsProjectileUid;
private _offDeadline = diag_tickTime + 4;
waitUntil {uiSleep 0.01; (missionNamespace getVariable [_offThreat # 1, false]) || {isNull _offRocket} || {diag_tickTime > _offDeadline}};
private _offImpact = missionNamespace getVariable [_offThreat # 1, false];
["aps.controls.hardOffImpact", _offImpact && {(_offThreat # 2)} && {(_offThreat # 4)} && {(missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]) isEqualTo _offEvents} && {([_apsVehicle] call YOSHI_fnc_apsHardKillChargeCount) isEqualTo _controlsStartCharges}, format ["projectile=%1|impact=%2|charges=%3|eventsUnchanged=%4", _offUid, _offImpact, [_apsVehicle] call YOSHI_fnc_apsHardKillChargeCount, (missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]) isEqualTo _offEvents]] call _assert;
missionNamespace setVariable ["PONTIFEX_APS_CONTROLS_PHASE", "off-impact", true];

private _rebootDeadline = diag_tickTime + 45;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["PONTIFEX_APS_CONTROLS_PHASE", ""]) isEqualTo "rebooted" || {diag_tickTime > _rebootDeadline}};
private _rebootThreat = [_apsVehicle, "controls-reboot"] call _injectThreat;
private _rebootRocket = _rebootThreat # 0;
private _rebootUid = [_rebootRocket] call YOSHI_fnc_apsProjectileUid;
private _rebootEvent = false;
private _rebootPhysicalDeadline = diag_tickTime + 4;
waitUntil {
    uiSleep 0.005;
    _rebootEvent = (missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]) findIf {(_x # 0) isEqualTo (netId _apsVehicle) && {(_x # 1) isEqualTo _rebootUid} && {(_x # 2) isEqualTo "hardkill"}} >= 0;
    _rebootEvent || {diag_tickTime > _rebootPhysicalDeadline}
};
["aps.controls.rebootIntercept", _rebootEvent && {isNull _rebootRocket} && {!(missionNamespace getVariable [_rebootThreat # 1, false])} && {([_apsVehicle] call YOSHI_fnc_apsHardKillChargeCount) isEqualTo (_controlsStartCharges - 1)}, format ["projectile=%1|event=%2|impact=%3|charges=%4", _rebootUid, _rebootEvent, missionNamespace getVariable [_rebootThreat # 1, false], [_apsVehicle] call YOSHI_fnc_apsHardKillChargeCount]] call _assert;
missionNamespace setVariable ["PONTIFEX_APS_CONTROLS_PHASE", "physical-done", true];
private _controlsDoneDeadline = diag_tickTime + 60;
waitUntil {uiSleep 0.05; (missionNamespace getVariable ["PONTIFEX_APS_CONTROLS_DONE", ""]) isEqualTo _token || {diag_tickTime > _controlsDoneDeadline}};
private _audit = missionNamespace getVariable ["YOSHI_APS_OPERATION_AUDIT", []];
["aps.controls.authoritativeAudit", (missionNamespace getVariable ["PONTIFEX_APS_CONTROLS_DONE", ""]) isEqualTo _token && {(count _audit) >= 8} && {(_audit findIf {(_x # 2) isEqualTo false && {(_x # 3) in ["replay", "operator_ineligible", "unknown_operation"]}}) >= 0}, format ["done=%1|auditCount=%2|audit=%3", missionNamespace getVariable ["PONTIFEX_APS_CONTROLS_DONE", ""], count _audit, _audit]] call _assert;
missionNamespace setVariable ["PONTIFEX_TIER_apsReplication", [_token, netId _apsVehicle, _projectileUid], true];
{if (!isNull _x) then {deleteVehicle _x}} forEach [_apsVehicle, _controlVehicle, _softVehicle, _compositionControlVehicle];
'''
        )
        aps_client = '''
 missionNamespace setVariable ["PONTIFEX_APS_CONTROLS_ARMED", _token, true];
 private _controlsFixture = [];
 private _controlsFixtureDeadline = diag_tickTime + 120;
 waitUntil {
     uiSleep 0.05;
     _controlsFixture = missionNamespace getVariable ["PONTIFEX_APS_CONTROLS_FIXTURE", []];
     (count _controlsFixture) isEqualTo 4 || {diag_tickTime > _controlsFixtureDeadline}
 };
 private _controlsVehicleId = _controlsFixture param [1, ""];
 private _controlsVehicle = if (_controlsVehicleId isEqualTo "") then {objNull} else {objectFromNetId _controlsVehicleId};
 private _compositionControlId = _controlsFixture param [3, ""];
 private _compositionControl = if (_compositionControlId isEqualTo "") then {objNull} else {objectFromNetId _compositionControlId};
 private _controlsResolveDeadline = diag_tickTime + 15;
 waitUntil {uiSleep 0.05; (!isNull _controlsVehicle && {!isNull _compositionControl}) || {diag_tickTime > _controlsResolveDeadline}};
 private _originalPlayerASL = getPosASL player;
 if (!isNull _controlsVehicle) then {player setPosASL ((getPosASL _controlsVehicle) vectorAdd [0, 5, 0]);};
 private _stateDeadline = diag_tickTime + 10;
 waitUntil {uiSleep 0.05; (_controlsVehicle getVariable ["YOSHI_APS_Installed", false]) && {(_controlsVehicle getVariable ["YOSHI_APS_Enabled", false])} || {diag_tickTime > _stateDeadline}};
 missionNamespace setVariable ["PONTIFEX_APS_CONTROLS_PHASE", "positioned", true];
 private _operatorDeadline = diag_tickTime + 20;
 waitUntil {uiSleep 0.05; (missionNamespace getVariable ["PONTIFEX_APS_CONTROLS_PHASE", ""]) isEqualTo "operator-ready" || {diag_tickTime > _operatorDeadline}};
 private _registrationDeadline = diag_tickTime + 15;
 waitUntil {uiSleep 0.05; (count (_controlsVehicle getVariable ["YOSHI_APS_ActionData_Local", []])) isEqualTo 14 || {diag_tickTime > _registrationDeadline}};
 private _actionData = {
     params ["_id"];
     private _record = (_controlsVehicle getVariable ["YOSHI_APS_ActionData_Local", []]) select {(_x param [0, ""]) isEqualTo _id};
     if ((count _record) isEqualTo 1) then {_record # 0} else {[]}
 };
 private _activeActionOn = {
     params ["_target", "_data"];
     if (isNull _target || {_data isEqualTo []}) exitWith {false};
     ace_interact_menu_objectActionList = [];
     private _tree = [_target, [_data, []], [], player distance _target] call ace_interact_menu_fnc_collectActiveActionTree;
     _tree isNotEqualTo []
 };
 private _activeAction = {
     params ["_data"];
     [_controlsVehicle, _data] call _activeActionOn
 };
 private _findAction = {
     params ["_nodes", "_wanted"];
     private _found = [];
     {
         _x params ["_data", "_children"];
         if ((_data param [0, ""]) isEqualTo _wanted) exitWith {_found = _data};
         private _child = [_children, _wanted] call _findAction;
         if (_child isNotEqualTo []) exitWith {_found = _child};
     } forEach _nodes;
     _found
 };
 private _allActionIds = {
     params ["_nodes"];
     private _found = [];
     {
         _x params ["_data", "_children"];
         private _id = _data param [0, ""];
         if (_id isNotEqualTo "") then {_found pushBack _id;};
         _found append ([_children] call _allActionIds);
     } forEach _nodes;
     _found
 };
 private _fieldWanted = ["logiActions", "TowActions", "YOSHI_StowRopes", "UAV_field_task"];
 private _fieldSnapshot = {
     params ["_target"];
     if (isNull _target) exitWith {[[], [], [], []]};
     [_target] call ace_interact_menu_fnc_compileMenu;
     private _class = typeOf _target call ace_common_fnc_getConfigName;
     private _tree = ace_interact_menu_ActNamespace getOrDefault [_class, []];
     private _ids = [_tree] call _allActionIds;
     private _records = _fieldWanted apply {[_tree, _x] call _findAction};
     private _counts = _fieldWanted apply {private _wanted = _x; {_x isEqualTo _wanted} count _ids};
     private _active = [];
     {if ([_target, _x] call _activeActionOn) then {_active pushBack (_x param [0, ""]);};} forEach _records;
     [_counts, _active, [count ropes _target, _target getVariable ["YOSHI_UavHasIED", false], _target getVariable ["YOSHI_UavOrdinanceCount", 0], _target getVariable ["YOSHI_UavGrenadeCount", 0]], _ids]
 };
 private _activeApsLeafIds = {
     private _active = [];
     {
         private _id = _x param [0, ""];
         if !(_id in ["YOSHI_APS_Menu", "YOSHI_APS_AntiDrone_Menu"]) then {
             if ([_x] call _activeAction) then {_active pushBack _id;};
         };
     } forEach (_controlsVehicle getVariable ["YOSHI_APS_ActionData_Local", []]);
     _active
 };
 private _fieldInitial = [_controlsVehicle] call _fieldSnapshot;
 private _fieldUninstalled = [_compositionControl] call _fieldSnapshot;
 private _uninstalledNoAps = !(_compositionControl getVariable ["YOSHI_APS_Installed", false])
     && {(count (_compositionControl getVariable ["YOSHI_APS_ActionData_Local", []])) isEqualTo 0};
 private _apsInitialLeaves = call _activeApsLeafIds;
 private _invokeRegistered = {
     params ["_id"];
     private _data = [_id] call _actionData;
     if !([_data] call _activeAction) exitWith {["", []]};
     [_controlsVehicle, player, []] call (_data # 3);
     private _submitted = uiNamespace getVariable ["YOSHI_APS_LastSubmittedOperation", []];
     private _requestId = _submitted param [0, ""];
     private _ack = [];
     private _ackDeadline = diag_tickTime + 10;
     waitUntil {
         uiSleep 0.05;
         _ack = missionNamespace getVariable [format ["YOSHI_APS_OPERATION_ACK_%1", _requestId], []];
         (count _ack) isEqualTo 8 || {diag_tickTime > _ackDeadline}
     };
     [_requestId, _ack]
 };
 private _sendDirect = {
     params ["_operation", "_requestId"];
     missionNamespace setVariable [format ["YOSHI_APS_OPERATION_ACK_%1", _requestId], nil, false];
     [_controlsVehicle, _operation, _requestId] remoteExecCall ["YOSHI_fnc_apsRequestOperation", 2];
     private _ack = [];
     private _deadline = diag_tickTime + 10;
     waitUntil {uiSleep 0.05; _ack = missionNamespace getVariable [format ["YOSHI_APS_OPERATION_ACK_%1", _requestId], []]; (count _ack) isEqualTo 8 || {diag_tickTime > _deadline}};
     _ack
 };
 private _root = ["YOSHI_APS_Menu"] call _actionData;
 private _hardOffData = ["YOSHI_APS_HardKill_TurnOff"] call _actionData;
 private _suspendData = ["YOSHI_APS_Suspend"] call _actionData;
 private _registeredIds = (_controlsVehicle getVariable ["YOSHI_APS_ActionData_Local", []]) apply {_x param [0, ""]};
 private _hardOffActive = [_hardOffData] call _activeAction;
 private _suspendActive = [_suspendData] call _activeAction;
 ace_interact_menu_objectActionList = [];
 private _rootTree = if (_root isEqualTo [] || {_hardOffData isEqualTo []} || {_suspendData isEqualTo []}) then {[]} else {
     [_controlsVehicle, [_root, [[_hardOffData, []], [_suspendData, []]]], [], player distance _controlsVehicle] call ace_interact_menu_fnc_collectActiveActionTree
 };
 private _rootActive = _rootTree isNotEqualTo [];
 private _menuOk = !isNull _controlsVehicle
     && {_rootActive}
     && {_hardOffActive}
     && {_suspendActive}
     && {({_x isEqualTo "YOSHI_APS_Menu"} count _registeredIds) isEqualTo 1}
     && {({_x isEqualTo "YOSHI_APS_Suspend"} count _registeredIds) isEqualTo 1}
     && {({_x isEqualTo "YOSHI_APS_Resume"} count _registeredIds) isEqualTo 1};
 ["aps.controls.menu", _menuOk, format ["vehicle=%1|distance=%2|ids=%3|records=%4|root=%5|hardOff=%6|suspend=%7|installed=%8|enabled=%9", _controlsVehicleId, player distance _controlsVehicle, _registeredIds, count (_controlsVehicle getVariable ["YOSHI_APS_ActionData_Local", []]), _rootActive, _hardOffActive, _suspendActive, _controlsVehicle getVariable ["YOSHI_APS_Installed", false], _controlsVehicle getVariable ["YOSHI_APS_Enabled", false]]] call _assert;

 private _hardOffResult = ["YOSHI_APS_HardKill_TurnOff"] call _invokeRegistered;
 private _hardOffAck = _hardOffResult # 1;
 private _staleHardOffId = format ["APS_STALE_%1", floor random 1e9];
 private _staleHardOffAck = ["hardkill-off", _staleHardOffId] call _sendDirect;
 private _hardOffOk = (_hardOffAck param [2, false]) && {(_hardOffAck param [3, ""]) isEqualTo "hardkill_off"} && {!((_hardOffAck param [7, []]) param [2, true])}
     && {!(_staleHardOffAck param [2, true])} && {(_staleHardOffAck param [3, ""]) isEqualTo "stale_transition"};
 missionNamespace setVariable ["PONTIFEX_APS_CONTROLS_PHASE", "hard-off", true];
 private _offDeadline = diag_tickTime + 15;
 waitUntil {uiSleep 0.05; (missionNamespace getVariable ["PONTIFEX_APS_CONTROLS_PHASE", ""]) isEqualTo "off-impact" || {diag_tickTime > _offDeadline}};
 private _rebootData = ["YOSHI_APS_HardKill_Reboot"] call _actionData;
 private _rebootWasActive = [_rebootData] call _activeAction;
 private _rebootResult = ["YOSHI_APS_HardKill_Reboot"] call _invokeRegistered;
 private _rebootAck = _rebootResult # 1;
 private _rebootOk = _rebootWasActive && {(_rebootAck param [2, false])} && {(_rebootAck param [3, ""]) isEqualTo "hardkill_rebooted"} && {((_rebootAck param [7, []]) param [2, false])} && {((_rebootAck param [7, []]) param [6, -1]) isEqualTo (_controlsFixture # 2)};
 ["aps.controls.transitions", _hardOffOk && {_rebootOk}, format ["hardOff=%1|stale=%2|rebootActive=%3|reboot=%4", _hardOffAck, _staleHardOffAck, _rebootWasActive, _rebootAck]] call _assert;
 missionNamespace setVariable ["PONTIFEX_APS_CONTROLS_PHASE", "rebooted", true];
 private _physicalDeadline = diag_tickTime + 15;
 waitUntil {uiSleep 0.05; (missionNamespace getVariable ["PONTIFEX_APS_CONTROLS_PHASE", ""]) isEqualTo "physical-done" || {diag_tickTime > _physicalDeadline}};
 private _depletionDeadline = diag_tickTime + 5;
 waitUntil {uiSleep 0.05; ([_controlsVehicle] call YOSHI_fnc_apsHardKillChargeCount) isEqualTo 0 || {diag_tickTime > _depletionDeadline}};

 private _emptyReboot = ["YOSHI_APS_HardKill_Reboot"] call _invokeRegistered;
 private _softOff = ["YOSHI_APS_SoftKill_TurnOff"] call _invokeRegistered;
 private _softOn = ["YOSHI_APS_SoftKill_TurnOn"] call _invokeRegistered;
 private _antiDroneOff = ["YOSHI_APS_AntiDrone_TurnOff"] call _invokeRegistered;
 private _voiceOff = ["YOSHI_APS_Voice_Off"] call _invokeRegistered;
 private _modeControlsOk = !((_emptyReboot # 1) param [2, true])
     && {((_emptyReboot # 1) param [3, ""]) isEqualTo "no_hardkill_charges"}
     && {((_softOff # 1) param [2, false])} && {((_softOff # 1) param [3, ""]) isEqualTo "softkill_off"}
     && {((_softOn # 1) param [2, false])} && {((_softOn # 1) param [3, ""]) isEqualTo "softkill_on"}
     && {((_antiDroneOff # 1) param [2, false])} && {((_antiDroneOff # 1) param [3, ""]) isEqualTo "anti_drone_off"}
     && {((_voiceOff # 1) param [2, false])};
 private _beforeSuspend = [_controlsVehicle] call YOSHI_fnc_apsStateSnapshot;
 private _fieldBeforeSuspend = [_controlsVehicle] call _fieldSnapshot;
 private _apsBeforeSuspendLeaves = call _activeApsLeafIds;
 private _suspend = ["YOSHI_APS_Suspend"] call _invokeRegistered;
 private _suspendState = ((_suspend # 1) param [7, []]);
 private _suspendedReplicationDeadline = diag_tickTime + 5;
 waitUntil {uiSleep 0.05; !(_controlsVehicle getVariable ["YOSHI_APS_Enabled", true]) || {diag_tickTime > _suspendedReplicationDeadline}};
 private _fieldSuspended = [_controlsVehicle] call _fieldSnapshot;
 private _apsSuspendedLeaves = call _activeApsLeafIds;
 private _resumeData = ["YOSHI_APS_Resume"] call _actionData;
 private _resumeWasActive = [_resumeData] call _activeAction;
 private _resume = ["YOSHI_APS_Resume"] call _invokeRegistered;
 private _resumeState = ((_resume # 1) param [7, []]);
 private _resumedReplicationDeadline = diag_tickTime + 5;
 waitUntil {uiSleep 0.05; (_controlsVehicle getVariable ["YOSHI_APS_Enabled", false]) || {diag_tickTime > _resumedReplicationDeadline}};
 private _fieldResumed = [_controlsVehicle] call _fieldSnapshot;
 private _apsResumedLeaves = call _activeApsLeafIds;
 private _preservedIndexes = [2, 3, 4, 5, 6, 7];
 private _preserved = (count _beforeSuspend) isEqualTo 8 && {(count _suspendState) isEqualTo 8} && {(count _resumeState) isEqualTo 8} && {(_preservedIndexes findIf {(_beforeSuspend # _x) isNotEqualTo (_suspendState # _x) || {(_beforeSuspend # _x) isNotEqualTo (_resumeState # _x)}}) < 0};
 private _lifecycleOk = _modeControlsOk
     && {((_suspend # 1) param [2, false])}
     && {!(_suspendState # 1)}
     && {_resumeWasActive}
     && {((_resume # 1) param [2, false])}
     && {_resumeState # 1}
     && {_preserved};
 ["aps.controls.lifecycle", _lifecycleOk, format ["emptyReboot=%1|softOff=%2|softOn=%3|antiOff=%4|voiceOff=%5|before=%6|suspend=%7|resumeActive=%8|resume=%9|preserved=%10", _emptyReboot # 1, _softOff # 1, _softOn # 1, _antiDroneOff # 1, _voiceOff # 1, _beforeSuspend, _suspend # 1, _resumeWasActive, _resume # 1, _preserved]] call _assert;
 private _fieldCountsOk = (_fieldInitial # 0) isEqualTo [1, 1, 1, 1]
     && {(_fieldUninstalled # 0) isEqualTo [1, 1, 1, 1]}
     && {(_fieldBeforeSuspend # 0) isEqualTo [1, 1, 1, 1]}
     && {(_fieldSuspended # 0) isEqualTo [1, 1, 1, 1]}
     && {(_fieldResumed # 0) isEqualTo [1, 1, 1, 1]};
 private _fieldStable = _fieldInitial isEqualTo _fieldBeforeSuspend
     && {_fieldInitial isEqualTo _fieldSuspended}
     && {_fieldInitial isEqualTo _fieldResumed}
     && {(_fieldInitial # 0) isEqualTo (_fieldUninstalled # 0)}
     && {"TowActions" in (_fieldInitial # 1)}
     && {!("YOSHI_StowRopes" in (_fieldInitial # 1))}
     && {!("UAV_field_task" in (_fieldInitial # 1))};
 private _initialApsOk = _apsInitialLeaves isEqualTo ["YOSHI_APS_Suspend", "YOSHI_APS_HardKill_TurnOff", "YOSHI_APS_AntiDrone_TurnOff", "YOSHI_APS_AntiDrone_Status", "YOSHI_APS_Status", "YOSHI_APS_Voice_Off"];
 private _activeModeApsExpected = ["YOSHI_APS_Suspend", "YOSHI_APS_HardKill_Reboot", "YOSHI_APS_SoftKill_TurnOff", "YOSHI_APS_AntiDrone_TurnOn", "YOSHI_APS_AntiDrone_Status", "YOSHI_APS_Status", "YOSHI_APS_Voice_On"];
 private _apsLifecycleCensusOk = _apsBeforeSuspendLeaves isEqualTo _activeModeApsExpected
     && {_apsSuspendedLeaves isEqualTo ["YOSHI_APS_Resume"]}
     && {_apsResumedLeaves isEqualTo _activeModeApsExpected};
 private _compositionOk = _uninstalledNoAps && {_fieldCountsOk} && {_fieldStable} && {_initialApsOk} && {_apsLifecycleCensusOk};
 ["aps.controls.composition", _compositionOk, format ["uninstalledNoAps=%1|fieldInitial=%2|fieldControl=%3|fieldBefore=%4|fieldSuspended=%5|fieldResumed=%6|apsInitial=%7|apsBefore=%8|apsSuspended=%9|apsResumed=%10", _uninstalledNoAps, _fieldInitial, _fieldUninstalled, _fieldBeforeSuspend, _fieldSuspended, _fieldResumed, _apsInitialLeaves, _apsBeforeSuspendLeaves, _apsSuspendedLeaves, _apsResumedLeaves]] call _assert;

 private _repeatId = format ["APS_REPEAT_%1", floor random 1e9];
 private _repeatAck = ["resume", _repeatId] call _sendDirect;
 private _replayAck = ["resume", _repeatId] call _sendDirect;
 private _crewId = format ["APS_CREW_%1", floor random 1e9];
 player moveInDriver _controlsVehicle;
 private _crewDeadline = diag_tickTime + 5;
 waitUntil {uiSleep 0.05; (driver _controlsVehicle) isEqualTo player || {diag_tickTime > _crewDeadline}};
 private _crewEntered = (driver _controlsVehicle) isEqualTo player;
 private _crewAck = ["status", _crewId] call _sendDirect;
 moveOut player;
 player setPosASL ((getPosASL _controlsVehicle) vectorAdd [30, 0, 0]);
 uiSleep 1;
 private _farId = format ["APS_FAR_%1", floor random 1e9];
 private _farAck = ["status", _farId] call _sendDirect;
 player setPosASL ((getPosASL _controlsVehicle) vectorAdd [0, 5, 0]);
 uiSleep 1;
 private _unknownId = format ["APS_UNKNOWN_%1", floor random 1e9];
 private _unknownAck = ["invented-operation", _unknownId] call _sendDirect;
 private _authorityOk = _crewEntered && {(_repeatAck param [2, false]) && {(_repeatAck param [3, ""]) isEqualTo "already_active"}}
     && {!(_replayAck param [2, true])} && {(_replayAck param [3, ""]) isEqualTo "replay"}
     && {(_crewAck param [2, false])} && {(_crewAck param [3, ""]) isEqualTo "status_delivered"}
     && {!(_farAck param [2, true])} && {(_farAck param [3, ""]) isEqualTo "operator_ineligible"}
     && {!(_unknownAck param [2, true])} && {(_unknownAck param [3, ""]) isEqualTo "unknown_operation"};
 ["aps.controls.authority", _authorityOk, format ["repeat=%1|replay=%2|crew=%3|far=%4|unknown=%5", _repeatAck, _replayAck, _crewAck, _farAck, _unknownAck]] call _assert;
 private _replicatedResult = _controlsVehicle getVariable ["YOSHI_APS_LastOperationResult", []];
 ["aps.controls.resultReplication", (_replicatedResult param [0, ""]) isEqualTo _unknownId && {(_replicatedResult param [2, true]) isEqualTo false} && {(_replicatedResult param [4, ""]) isEqualTo netId player} && {(_replicatedResult param [5, -1]) isEqualTo clientOwner}, format ["result=%1|player=%2|owner=%3", _replicatedResult, netId player, clientOwner]] call _assert;
 player setPosASL _originalPlayerASL;
 missionNamespace setVariable ["PONTIFEX_APS_CONTROLS_DONE", _token, true];
 private _apsDeadline = diag_tickTime + 45;
 waitUntil { uiSleep 0.1; !isNil {missionNamespace getVariable "PONTIFEX_TIER_apsReplication"} || diag_tickTime > _apsDeadline };
 private _apsReplication = missionNamespace getVariable ["PONTIFEX_TIER_apsReplication", []];
 private _apsId = _apsReplication param [1, ""];
 private _apsProjectile = _apsReplication param [2, ""];
 private _apsObject = if (_apsId isEqualType "" && {_apsId isNotEqualTo ""}) then {objectFromNetId _apsId} else {objNull};
 private _apsEvent = (missionNamespace getVariable ["YOSHI_APS_EngagementEvents", []]) findIf {
     (_x param [0, ""]) isEqualTo _apsId && {(_x param [1, ""]) isEqualTo _apsProjectile} && {(_x param [2, ""]) isEqualTo "hardkill"}
 } >= 0;
 ["aps.replication", (_apsReplication param [0, ""]) isEqualTo _token && {_apsId isNotEqualTo ""} && {_apsProjectile isNotEqualTo ""} && {_apsEvent}, format ["vehicle=%1|projectile=%2|objectResolved=%3|event=%4", _apsId, _apsProjectile, !isNull _apsObject, _apsEvent]] call _assert;
'''
    framework_server = "\n".join(ALL_SCENARIOS[item].server_sqf for item in sorted(plan.selected) if item in ALL_SCENARIOS)
    framework_client = "\n".join(ALL_SCENARIOS[item].sqf_for("client-a") for item in sorted(plan.selected) if item in ALL_SCENARIOS)
    live_server = ""
    live_client = ""
    if live:
        # This exists only in Developer Live Mode, where the operator has
        # intentionally opted into file patching and a run-scoped writable
        # command inbox.  Normal smoke/integration/gameplay missions have no
        # file-patching flag or command mount.
        live_server = '''
 // This dedicated-server build does not deliver mission EachFrame handlers
 // after mission start: both CBA's PFH dispatcher and a direct EachFrame
 // handler register but never tick. A scheduled mission loop does run here.
 // Vary the extension argument on every poll: the extension ignores the
 // nonce, but Arma then performs a fresh call instead of memoizing the first
 // identical request.
 diag_log "PONTIFEX_LIVE|server|POLLER_REGISTERED";
 while {true} do {
     private _poll = (missionNamespace getVariable ["PONTIFEX_LIVE_poll", 0]) + 1;
     missionNamespace setVariable ["PONTIFEX_LIVE_poll", _poll];
     if ((_poll mod 10) isEqualTo 0) then { diag_log format ["PONTIFEX_LIVE|server|POLL|%1", _poll]; };
     private _payload = "pontifex_live" callExtension (format ["next-%1", _poll]);
     private _last = missionNamespace getVariable ["PONTIFEX_LIVE_last", ""];
     if (_payload isNotEqualTo "" && {_payload isNotEqualTo _last}) then {
         missionNamespace setVariable ["PONTIFEX_LIVE_last", _payload];
         diag_log "PONTIFEX_LIVE|server|EXEC";
         // Run the snippet in its own script. Called inline, a runtime error in
         // an operator snippet terminates this loop for good, and `live reset`
         // cannot recover it because reset arrives through this same inbox.
         [_payload] spawn { call compile (_this select 0); };
     };
     sleep 0.5;
 };
 diag_log "PONTIFEX_LIVE|server|READY";
'''
        live_client = '''
 PONTIFEX_LIVE_fnc_exec = { params ["_source", "_commandId"]; diag_log format ["PONTIFEX_LIVE|client-a|EXEC|%1", _commandId]; call compile _source; };
 diag_log "PONTIFEX_LIVE|client-a|READY";
'''
    init_server = f'''[] spawn {{
 private _token = "{token}";
 missionNamespace setVariable ["TRIBUNAL_MACHINE_IDENTITY", "server"];
 waitUntil {{ time > 0 }};
 missionNamespace setVariable ["PONTIFEX_TIER_serverResults", []];
 private _assert = {{ params ["_name", "_condition", ["_detail", ""]]; private _status = "FAIL"; if (_condition isEqualTo true) then {{ _status = "PASS"; }}; private _results = missionNamespace getVariable ["PONTIFEX_TIER_serverResults", []]; _results pushBack [_name, _status, _detail]; missionNamespace setVariable ["PONTIFEX_TIER_serverResults", _results]; diag_log format ["PONTIFEX_TEST|%1|server|%2|%3", _status, _name, _detail]; }};
 ["smoke.init.sqf", true, "server mission init"] call _assert;
 ["smoke.token", _token isEqualTo "{token}", format ["token=%1", _token]] call _assert;
 PONTIFEX_TIER_fnc_clientReady = {{ params ["_receivedToken"]; missionNamespace setVariable ["PONTIFEX_TIER_clientReady", _receivedToken]; missionNamespace setVariable ["PONTIFEX_LIVE_clientOwner", remoteExecutedOwner]; }};
 PONTIFEX_TIER_fnc_integrationAck = {{ params ["_receivedToken"]; missionNamespace setVariable ["PONTIFEX_TIER_integrationAck", _receivedToken]; }};
 private _deadline = diag_tickTime + 180;
 waitUntil {{ uiSleep 0.1; count allPlayers isEqualTo 1 && {{(missionNamespace getVariable ["PONTIFEX_TIER_clientReady", ""]) isEqualTo _token}} || diag_tickTime > _deadline }};
 private _player = allPlayers param [0, objNull];
 ["smoke.player", !isNull _player && {{name _player isEqualTo "PontifexClientA"}}, format ["name=%1|count=%2", name _player, count allPlayers]] call _assert;
 ["smoke.ack", (missionNamespace getVariable ["PONTIFEX_TIER_clientReady", ""]) isEqualTo _token, "client ready"] call _assert;
 {integration_server}
 {gameplay_server}
 {aps_server}
 {framework_server}
 private _results = missionNamespace getVariable ["PONTIFEX_TIER_serverResults", []];
 private _failures = {{(_x # 1) isEqualTo "FAIL"}} count _results;
 private _status = "FAIL";
 if (_failures isEqualTo 0 && {{(count _results) isEqualTo {len(plan.server_expected)}}}) then {{ _status = "PASS"; [_token, _status] remoteExecCall ["PONTIFEX_TIER_fnc_serverAck", owner _player]; }};
 diag_log format ["PONTIFEX_TEST|COMPLETE|server|status=%1|assertions=%2|failures=%3", _status, count _results, _failures];
 diag_log format ["PONTIFEX_TIER|{plan.name}|%1|%2", _status, _token];
 {live_server}
}};
'''
    init_client = f'''[] spawn {{
 private _token = "{token}";
 missionNamespace setVariable ["TRIBUNAL_MACHINE_IDENTITY", "client-a"];
 private _deadline = diag_tickTime + 150;
 waitUntil {{ uiSleep 0.1; !isNull player && {{hasInterface}} || diag_tickTime > _deadline }};
 missionNamespace setVariable ["PONTIFEX_TIER_clientResults", []];
 private _assert = {{ params ["_name", "_condition", ["_detail", ""]]; private _status = "FAIL"; if (_condition isEqualTo true) then {{ _status = "PASS"; }}; private _results = missionNamespace getVariable ["PONTIFEX_TIER_clientResults", []]; _results pushBack [_name, _status, _detail]; missionNamespace setVariable ["PONTIFEX_TIER_clientResults", _results]; diag_log format ["PONTIFEX_TEST|%1|client-a|%2|%3", _status, _name, _detail]; }};
 ["smoke.initPlayerLocal", hasInterface && {{!isNull player}}, "client mission init"] call _assert;
 ["smoke.identity", name player isEqualTo "PontifexClientA" && {{getPlayerUID player isNotEqualTo ""}}, format ["name=%1|uid=%2", name player, getPlayerUID player]] call _assert;
 ["smoke.token", _token isEqualTo "{token}", format ["token=%1", _token]] call _assert;
 PONTIFEX_TIER_fnc_serverAck = {{ params ["_replyToken", "_status"]; missionNamespace setVariable ["PONTIFEX_TIER_serverAck", [_replyToken, _status]]; }};
 [_token] remoteExecCall ["PONTIFEX_TIER_fnc_clientReady", 2];
 {integration_client}
 {gameplay_client}
 {aps_client}
 {framework_client}
 private _ackDeadline = diag_tickTime + 45;
 waitUntil {{ uiSleep 0.1; ((missionNamespace getVariable ["PONTIFEX_TIER_serverAck", []]) param [0, ""]) isEqualTo _token || diag_tickTime > _ackDeadline }};
 private _ack = missionNamespace getVariable ["PONTIFEX_TIER_serverAck", []];
 ["smoke.ack", (_ack param [0, ""]) isEqualTo _token && {{(_ack param [1, "FAIL"]) isEqualTo "PASS"}}, format ["ack=%1", _ack]] call _assert;
 private _results = missionNamespace getVariable ["PONTIFEX_TIER_clientResults", []];
 private _failures = {{(_x # 1) isEqualTo "FAIL"}} count _results;
 private _status = "FAIL";
 if (_failures isEqualTo 0 && {{(count _results) isEqualTo {len(plan.client_expected)}}}) then {{ _status = "PASS"; }};
 diag_log format ["PONTIFEX_TEST|COMPLETE|client-a|status=%1|assertions=%2|failures=%3", _status, count _results, _failures];
 diag_log format ["PONTIFEX_TIER|{plan.name}|%1|%2", _status, _token];
 {live_client}
}};
'''
    (destination / "mission.sqm").write_text(mission_sqm, encoding="ascii")
    (destination / "description.ext").write_text(description, encoding="ascii")
    (destination / "initServer.sqf").write_text(init_server, encoding="ascii")
    (destination / "initPlayerLocal.sqf").write_text(init_client, encoding="ascii")
    return {"token": token, "source": str(destination), "mission_sha256": dedicated.sha256(destination / "mission.sqm"), "plan": plan.name}


def write_e2e_mission(destination: Path, token: str) -> dict:
    """Create a fresh vanilla mission whose state transition is self-checking."""
    destination.mkdir(parents=True, exist_ok=False)
    position_x = 4683 + (int(token[-4:], 16) % 30)
    mission_sqm = f'''version=54;
binarizationWanted=0;
sourceName="PontifexE2E_{token}";
addons[]={{"A3_Characters_F","A3_Soft_F"}};
class AddonsMetaData {{ class List {{ items=2; class Item0 {{ className="A3_Characters_F"; name="Characters"; author="Bohemia Interactive"; }}; class Item1 {{ className="A3_Soft_F"; name="Soft Vehicles"; author="Bohemia Interactive"; }}; }}; }};
randomSeed={int(token[-8:], 16)};
class Mission {{
 class Intel {{ year=2035; month=7; day=6; hour=12; minute=0; startWeather=0; forecastWeather=0; }};
 class Entities {{ items=2;
  class Item0 {{ dataType="Group"; side="West"; class Entities {{ items=1; class Item0 {{ dataType="Object"; class PositionInfo {{ position[]={{ {position_x},16,2778 }}; }}; side="West"; flags=7; class Attributes {{ isPlayer=1; }}; id=1; type="B_Soldier_A_F"; }}; }}; class Attributes {{}}; id=0; }};
  class Item1 {{ dataType="Object"; class PositionInfo {{ position[]={{ {position_x + 8},16,2778 }}; }}; side="Empty"; flags=7; class Attributes {{ name="PONTIFEX_E2E_vehicle"; }}; id=2; type="C_Offroad_01_F"; }};
 }};
}};
'''
    # This is Arma's native, mission-scoped no-lobby policy.  `skipLobby`
    # itself controls the automatic free-role choice, so do not also set
    # `joinUnassigned`: an explicit conflicting value prevents the engine
    # from applying its skip-lobby role selection.
    description = (
        "class Header { gameType = COOP; minPlayers = 1; maxPlayers = 1; };\n"
        "skipLobby = 1;\nrespawn = 3;\nrespawnOnStart = 1;\ndisabledAI = 1;\n"
    )
    init_server = f'''[] spawn {{
 private _token = "{token}";
 waitUntil {{ time > 0 }};
 missionNamespace setVariable ["PONTIFEX_E2E_serverResults", []];
 private _assert = {{ params ["_name", "_condition", ["_detail", ""]]; private _passed = _condition isEqualTo true; private _status = "FAIL"; if (_passed) then {{ _status = "PASS"; }}; private _results = missionNamespace getVariable ["PONTIFEX_E2E_serverResults", []]; _results pushBack [_name, _status, _detail]; missionNamespace setVariable ["PONTIFEX_E2E_serverResults", _results]; diag_log format ["PONTIFEX_TEST|%1|server|%2|%3", _status, _name, _detail]; }};
 ["sqf.executed", true, "e2e initServer"] call _assert;
 private _expectedToken = "{token}";
 private _tokenMatches = _token isEqualTo _expectedToken;
 private _tokenDetail = format ["actual=%1|expected=%2", _token, _expectedToken];
 ["e2e.token", _tokenMatches, _tokenDetail] call _assert;
 private _vehicleDeadline = diag_tickTime + 30;
 waitUntil {{ uiSleep 0.1; !isNil "PONTIFEX_E2E_vehicle" || diag_tickTime > _vehicleDeadline }};
 private _vehicle = missionNamespace getVariable ["PONTIFEX_E2E_vehicle", objNull];
 ["e2e.vehicleExists", !isNull _vehicle && {{typeOf _vehicle isEqualTo "C_Offroad_01_F"}}, format ["netId=%1", netId _vehicle]] call _assert;
 missionNamespace setVariable ["PONTIFEX_E2E_vehicleNetId", netId _vehicle, true];
 PONTIFEX_E2E_fnc_serverAction = {{ params ["_receivedToken", "_clientSaysDone", "_vehicleId"]; private _owner = remoteExecutedOwner; missionNamespace setVariable ["PONTIFEX_E2E_action", [_receivedToken, _clientSaysDone, _vehicleId, _owner]]; }};
 private _deadline = diag_tickTime + 180;
 waitUntil {{ uiSleep 0.2; (count allPlayers isEqualTo 1 && {{!isNull (allPlayers # 0)}} && {{!(missionNamespace getVariable ["PONTIFEX_E2E_action", []] isEqualTo [])}}) || diag_tickTime > _deadline }};
 private _player = allPlayers param [0, objNull];
 private _action = missionNamespace getVariable ["PONTIFEX_E2E_action", []];
 ["e2e.playerExists", !isNull _player && {{(count allPlayers) isEqualTo 1}}, format ["count=%1", count allPlayers]] call _assert;
 ["e2e.playerIdentity", (!isNull _player && {{name _player isEqualTo "PontifexClientA"}} && {{getPlayerUID _player isNotEqualTo ""}}), format ["name=%1|uid=%2", name _player, getPlayerUID _player]] call _assert;
 private _actionOk = !isNull _vehicle && {{!isNull _player}} && {{(count _action) isEqualTo 4}} && {{(_action # 0) isEqualTo _token}} && {{(_action # 1) isEqualTo true}} && {{(netId _vehicle) isEqualTo (_action # 2)}};
 private _driver = objNull;
 if (_actionOk) then {{ _player moveInDriver _vehicle; private _driverDeadline = diag_tickTime + 30; waitUntil {{ uiSleep 0.2; _driver = driver _vehicle; _driver isEqualTo _player || diag_tickTime > _driverDeadline }}; _actionOk = _driver isEqualTo _player; }};
 ["e2e.actionVerified", _actionOk, format ["driver=%1|vehicle=%2|playerVehicle=%3|player=%4", if (isNull _driver) then {{"<none>"}} else {{name _driver}}, netId _vehicle, netId (vehicle _player), name _player]] call _assert;
 private _finalState = _actionOk && {{vehicle _player isEqualTo _vehicle}};
 ["e2e.finalState", _finalState, format ["playerVehicle=%1", netId (vehicle _player)]] call _assert;
 private _results = missionNamespace getVariable ["PONTIFEX_E2E_serverResults", []];
 private _failures = {{(_x # 1) isEqualTo "FAIL"}} count _results;
 private _overall = "FAIL";
 if (_failures isEqualTo 0 && {{(count _results) isEqualTo 7}} && {{_actionOk}}) then {{ _overall = "PASS"; [_token, _overall] remoteExecCall ["PONTIFEX_E2E_fnc_serverAck", owner _player]; }};
 diag_log format ["PONTIFEX_TEST|COMPLETE|server|status=%1|assertions=%2|failures=%3", _overall, count _results, _failures];
 diag_log format ["PONTIFEX_E2E|%1|%2", _overall, _token];
}};
'''
    init_client = f'''[] spawn {{
 private _token = "{token}";
 private _deadline = diag_tickTime + 120;
 waitUntil {{ uiSleep 0.2; (!isNull player && {{hasInterface}}) || diag_tickTime > _deadline }};
 missionNamespace setVariable ["PONTIFEX_E2E_clientResults", []];
 private _assert = {{ params ["_name", "_condition", ["_detail", ""]]; private _passed = _condition isEqualTo true; private _status = "FAIL"; if (_passed) then {{ _status = "PASS"; }}; private _results = missionNamespace getVariable ["PONTIFEX_E2E_clientResults", []]; _results pushBack [_name, _status, _detail]; missionNamespace setVariable ["PONTIFEX_E2E_clientResults", _results]; diag_log format ["PONTIFEX_TEST|%1|client-a|%2|%3", _status, _name, _detail]; }};
 ["e2e.initPlayerLocal", (hasInterface && {{!isNull player}}), "initPlayerLocal"] call _assert;
 ["e2e.playerIdentity", (name player isEqualTo "PontifexClientA" && {{getPlayerUID player isNotEqualTo ""}}), format ["name=%1|uid=%2", name player, getPlayerUID player]] call _assert;
 private _expectedToken = "{token}";
 private _tokenMatches = _token isEqualTo _expectedToken;
 private _tokenDetail = format ["actual=%1|expected=%2", _token, _expectedToken];
 ["e2e.token", _tokenMatches, _tokenDetail] call _assert;
 private _vehicleDeadline = diag_tickTime + 30;
 waitUntil {{ uiSleep 0.2; !isNil {{missionNamespace getVariable "PONTIFEX_E2E_vehicleNetId"}} || diag_tickTime > _vehicleDeadline }};
 private _vehicleId = missionNamespace getVariable ["PONTIFEX_E2E_vehicleNetId", ""];
 private _vehicle = if (_vehicleId isEqualType "" && {{_vehicleId isNotEqualTo ""}}) then {{objectFromNetId _vehicleId}} else {{objNull}};
 private _resolveDeadline = diag_tickTime + 30;
 waitUntil {{ uiSleep 0.2; !isNull _vehicle || diag_tickTime > _resolveDeadline }};
 ["e2e.vehicleResolved", !isNull _vehicle && {{(netId _vehicle) isEqualTo _vehicleId}}, format ["netId=%1", _vehicleId]] call _assert;
 if (!isNull _vehicle) then {{ player moveInDriver _vehicle; }};
 private _actionDeadline = diag_tickTime + 30;
 waitUntil {{ uiSleep 0.2; (!isNull _vehicle && {{driver _vehicle isEqualTo player}}) || diag_tickTime > _actionDeadline }};
 private _actionOk = !isNull _vehicle && {{driver _vehicle isEqualTo player}} && {{vehicle player isEqualTo _vehicle}};
 ["e2e.actionExecuted", _actionOk, format ["vehicle=%1", netId _vehicle]] call _assert;
 missionNamespace setVariable ["PONTIFEX_E2E_serverAck", []];
 PONTIFEX_E2E_fnc_serverAck = {{ params ["_replyToken", "_status"]; missionNamespace setVariable ["PONTIFEX_E2E_serverAck", [_replyToken, _status]]; }};
 [_token, _actionOk, netId _vehicle] remoteExecCall ["PONTIFEX_E2E_fnc_serverAction", 2];
 private _ackDeadline = diag_tickTime + 30;
 waitUntil {{ uiSleep 0.2; ((missionNamespace getVariable ["PONTIFEX_E2E_serverAck", []]) param [0, ""]) isEqualTo _token || diag_tickTime > _ackDeadline }};
 private _ack = missionNamespace getVariable ["PONTIFEX_E2E_serverAck", []];
 private _finalOk = _actionOk && {{(_ack param [0, ""]) isEqualTo _token}} && {{(_ack param [1, "FAIL"]) isEqualTo "PASS"}};
 ["e2e.finalState", _finalOk, format ["ack=%1", _ack]] call _assert;
 private _results = missionNamespace getVariable ["PONTIFEX_E2E_clientResults", []];
 private _failures = {{(_x # 1) isEqualTo "FAIL"}} count _results;
 private _overall = "FAIL";
 if (_failures isEqualTo 0 && {{(count _results) isEqualTo 6}} && {{_finalOk}}) then {{ _overall = "PASS"; }};
 diag_log format ["PONTIFEX_TEST|COMPLETE|client-a|status=%1|assertions=%2|failures=%3", _overall, count _results, _failures];
 diag_log format ["PONTIFEX_E2E|%1|%2", _overall, _token];
}};
'''
    (destination / "mission.sqm").write_text(mission_sqm, encoding="ascii")
    (destination / "description.ext").write_text(description, encoding="ascii")
    (destination / "initServer.sqf").write_text(init_server, encoding="ascii")
    (destination / "initPlayerLocal.sqf").write_text(init_client, encoding="ascii")
    return {"token": token, "source": str(destination), "mission_sha256": dedicated.sha256(destination / "mission.sqm")}


def manual_ssh_target() -> str:
    """Return the local host name used for a manual-test SSH tunnel.

    A deployment may provide a public/bastion name explicitly, but the
    ordinary case must describe the machine that actually owns the loopback
    VNC listener.  Do not carry aliases from another project into a handoff.
    """
    return os.environ.get("PONTIFEX_SSH_TARGET", socket.gethostname())


def terminal_results_ready(server_complete: dict | None, client_complete: dict | None, *, manual: bool, live: bool, server_text: str = "", client_text: str = "") -> bool:
    """Return whether a non-manual run has reached a terminal protocol state.

    PASS and FAIL are both terminal: validation below determines the final exit
    status.  Only absent/incomplete protocol records consume the safety timeout.
    Live Mode intentionally waits for its explicit READY markers instead.
    """
    if manual or server_complete is None or client_complete is None:
        return False
    if live:
        return "PONTIFEX_LIVE|server|READY" in server_text and "PONTIFEX_LIVE|client-a|READY" in client_text
    return True

def run_multiplayer(
    force_failure: bool,
    timeout_seconds: int,
    manual: bool = False,
    e2e: bool = False,
    plan: TestPlan | None = None,
    live: bool = False,
) -> int:
    # Native Arma startup parameters are the normal autonomous E2E join path.
    # Keep the VNC adapter for diagnostic/manual workflows only; it no longer
    # drives Server Browser / Direct Connect for the production proof.
    native_connect = e2e or plan is not None or os.environ.get("PONTIFEX_NATIVE_CONNECT") == "1"
    visual_required = bool(plan and "visual-framebuffer" in plan.selected)
    ui_scenarios = [
        ALL_SCENARIOS[item]
        for item in sorted(plan.selected if plan else ())
        if item in ALL_SCENARIOS and ALL_SCENARIOS[item].metadata.get("visual_driver")
    ]
    experiment = os.environ.get("PONTIFEX_EXPERIMENT_MISSION")
    experiment_pbo = os.environ.get("PONTIFEX_EXPERIMENT_PBO")
    if (e2e or plan is not None) and (experiment or experiment_pbo):
        raise RuntimeError("fresh autonomous tier commands select their own mission")
    if experiment and experiment_pbo:
        raise RuntimeError("select either PONTIFEX_EXPERIMENT_MISSION or PONTIFEX_EXPERIMENT_PBO")
    if experiment:
        source = ROOT / "tests" / "missions" / experiment
        if not source.is_dir():
            raise RuntimeError(f"unknown experiment mission: {experiment}")
        dedicated.MISSION_SOURCE = source
        dedicated.MISSION_NAME = experiment
    if experiment_pbo:
        source = ROOT / experiment_pbo
        if not source.is_file() or source.suffix.lower() != ".pbo":
            raise RuntimeError(f"unknown experiment mission PBO: {experiment_pbo}")
        dedicated.MISSION_SOURCE = source
        dedicated.MISSION_NAME = source.stem
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{uuid.uuid4().hex[:8]}"
    run_dir = RUNS / run_id
    server_dir = run_dir / "server"
    client_dir = run_dir / "client-a"
    configured_clients = client_identity_map((ClientIdentity("client-a", "PontifexClientA", CLIENT_HOME, 20, 5904),))
    for path in (server_dir / "profile", client_dir / "profile", run_dir / "network"):
        path.mkdir(parents=True, exist_ok=True)
    if live:
        (run_dir / "live-control").mkdir(mode=0o700)
        # A blank inbox is important: the mission poller treats a changed,
        # non-empty file as a command.  It never inherits a previous run.
        for endpoint in ("server.sqf", "client.sqf"):
            (run_dir / "live-control" / endpoint).write_text("", encoding="ascii")
    e2e_mission = None
    if e2e:
        token = f"e2e-{run_id}-{uuid.uuid4().hex[:12]}"
        mission_name = f"PontifexE2E_{run_id.replace('-', '_')}.Stratis"
        e2e_mission = write_e2e_mission(run_dir / "mission" / mission_name, token)
        dedicated.MISSION_SOURCE = Path(e2e_mission["source"])
        dedicated.MISSION_NAME = mission_name
    elif plan is not None:
        token = f"{plan.name}-{run_id}-{uuid.uuid4().hex[:12]}"
        mission_name = f"Pontifex{plan.name.title()}_{run_id.replace('-', '_')}.Stratis"
        e2e_mission = write_tier_mission(run_dir / "mission" / mission_name, token, plan, live=live)
        dedicated.MISSION_SOURCE = Path(e2e_mission["source"])
        dedicated.MISSION_NAME = mission_name
    # A fixture can be self-contained yet still require the real Pontifex
    # addon stack.  Keep the smoke path minimal, but mount dependencies and
    # project mods for plans (such as APS) that explicitly declare them.
    minimal = (e2e or plan is not None or experiment is not None or experiment_pbo is not None) and not (plan is not None and plan.project_mods)
    latest = RUNS / "latest"
    latest.unlink(missing_ok=True)
    latest.symlink_to(run_id)

    manifest = {
        "schema": 2,
        "run_id": run_id,
        "mode": (
            "autonomous-single-client-e2e" if e2e else
            f"tier-{plan.name}" if plan is not None else
            "manual-multiplayer" if manual else
            "multiplayer-forced-failure" if force_failure else "multiplayer"
        ),
        "started_at": dedicated.utc_now(),
        "timeout_seconds": timeout_seconds,
        "git": dedicated.git_info(),
        "arma_server": dedicated.arma_version(),
        "arma_client": client_version(),
        "dependencies": dedicated.dependency_status(),
        "builds": [],
        "command": (
            ["./pontifex", "e2e"] if e2e else
            ["./pontifex", "test", "live"] if live else
            ["./pontifex", "test", plan.name] if plan is not None else
            ["./pontifex", "manual"] if manual else
            ["./pontifex", "test", "multiplayer"] + (["--force-failure"] if force_failure else [])
        ),
        "architecture": "two unprivileged Docker containers on one run-scoped bridge; NVIDIA CDI client GPU",
        "clients": {
            identity: {
                "profile_name": client.profile_name,
                "steam_home": str(client.steam_home),
                "address_offset": client.address_offset,
                "diagnostic_vnc_port": client.diagnostic_vnc_port,
            }
            for identity, client in configured_clients.items()
        },
    }
    if e2e_mission:
        manifest["fresh_mission"] = e2e_mission
    if plan is not None:
        manifest["test_plan"] = {
            "tier": plan.name,
            "server_expected": sorted(plan.server_expected),
            "client_expected": sorted(plan.client_expected),
            "single_boot_batch": plan.name == "integration",
            "live_command_channel": live,
            "project_mods": plan.project_mods,
        }
    if manual:
        manifest["manual_access"] = {
            "ssh_target": manual_ssh_target(),
            "vnc_bind": "127.0.0.1:5904",
            "vnc_tunnel": f"ssh -N -L 5904:127.0.0.1:5904 {manual_ssh_target()}",
        }
    dedicated.atomic_json(run_dir / "manifest.json", manifest)

    def phase(name: str, **details: object) -> None:
        manifest.setdefault("lifecycle", []).append({"at": dedicated.utc_now(), "phase": name, **details})
        dedicated.atomic_json(run_dir / "manifest.json", manifest)

    phase("run_initialized", mode=manifest["mode"], build_log=str(run_dir / "build.log"), mission=str(dedicated.MISSION_SOURCE))
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
            ("licensed Arma 3 character payload", info["character_payload"] is not None),
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
    previous_signal_handlers = {}

    def interrupted(signum: int, _frame: object) -> None:
        phase("external_signal_received", signal=signal.Signals(signum).name)
        raise RuntimeError(f"external termination signal: {signal.Signals(signum).name}")

    with dedicated.runtime_lock():
        phase("runtime_lock_acquired")
        for signum in (signal.SIGTERM, signal.SIGHUP):
            previous_signal_handlers[signum] = signal.signal(signum, interrupted)
        dedicated.stop_server()
        phase("stale_runtime_cleanup_started")
        previous = clean_multiplayer_state()
        if not all(previous.values()):
            result["reason"] = "stale_multiplayer_cleanup_failed"
            result["cleanup"] = previous
            write_result(run_dir, result)
            return 1
        try:
            phase("build_started")
            with (run_dir / "build.log").open("w", encoding="utf-8") as build_log:
                built = subprocess.run(
                    [str(ROOT / "pontifex"), "build"],
                    cwd=ROOT,
                    stdout=build_log,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
            phase("build_finished", returncode=built.returncode)
            if built.returncode != 0:
                result["reason"] = "build_failed"
                return_code = 1
                return return_code
            phase("runtime_setup_entered", minimal=minimal, e2e=e2e, plan=plan.name if plan else None)
            dependencies = {} if minimal else dedicated.provision_dependencies()
            dedicated.prepare_runtime()
            live_extension_dir = None
            if live:
                # The extension is built afresh inside this run directory and
                # reads only the explicitly mounted command inbox.  It is not
                # present in normal test tiers or the production E2E.
                live_extension_dir = prepare_live_extension(run_dir)
            phase("runtime_setup_completed")
            if e2e_mission:
                staged_pbo = dedicated.INSTALL_VIEW / "mpmissions" / f"{dedicated.MISSION_NAME}.pbo"
                if not staged_pbo.is_file():
                    raise RuntimeError("fresh E2E mission PBO was not staged")
                manifest["fresh_mission"].update(
                    {
                        "pbo": str(staged_pbo),
                        "pbo_sha256": dedicated.sha256(staged_pbo),
                        "pbo_size": staged_pbo.stat().st_size,
                        "footer_sha1_valid": staged_pbo.read_bytes()[-20:]
                        == hashlib.sha1(staged_pbo.read_bytes()[:-21]).digest(),
                    }
                )
                if not manifest["fresh_mission"]["footer_sha1_valid"]:
                    raise RuntimeError("fresh E2E mission PBO footer hash is invalid")
            official_server_content = dedicated.official_component_policy()
            official_client_content = client_component_policy()
            client_only_official_ids = []
            for component in official_client_content["official_components"]:
                if "server_path" in component:
                    continue
                name = component["id"]
                deployed = RUNTIME / "official-mods" / f"@pontifex_a3_{name}"
                deployed.mkdir(exist_ok=True)
                (deployed / "addons").symlink_to(Path(component["client_addons"]), target_is_directory=True)
                (dedicated.INSTALL_VIEW / f"@pontifex_a3_{name}").symlink_to(deployed, target_is_directory=True)
                client_only_official_ids.append(name)

            config = (dedicated.SERVER / "config" / "dedicated.cfg.in").read_text()
            config = (
                config.replace("@FORCE_FAILURE@", "1" if force_failure else "0")
                .replace("@REQUIRE_CLIENT@", "0" if minimal else "1")
                .replace("Pontifex_Integration.Stratis", dedicated.MISSION_NAME)
            )
            if e2e or plan is not None:
                # The mission itself owns skipLobby.  The server.cfg setting
                # is deliberately absent: Arma consults it only when no
                # mission/campaign config defines skipLobby.
                pass
            (server_dir / "server.cfg").write_text(config)
            shutil.copy2(dedicated.SERVER / "config" / "basic.cfg", server_dir / "basic.cfg")

            network, subnet, server_ip, client_ip = choose_network(run_id)
            port = int(os.environ.get("PONTIFEX_MULTIPLAYER_PORT", "2322"))
            phase("network_creation_entered", network=network, server_ip=server_ip, server_port=port)
            # The SteamCMD server packages official Curator UI separately.
            # Bootcamp's built-in functions include it during base startup,
            # so this official component is required even for a custom-mod-
            # free mission. It is not a Pontifex or third-party mod.
            mod_names = [
                *(f"@pontifex_a3_{name}" for name in dedicated.official_component_ids()),
                *(f"@pontifex_a3_{name}" for name in client_only_official_ids),
                *([] if minimal else ["@pontifex_test_player_base"]),
                *([] if minimal else [
                "@cba_a3",
                "@ace",
                "@zen",
                "@cordis",
                "@fieldutils",
                "@advsys",
                "@vigil",
                ]),
            ]
            player_base_mod = dedicated.INSTALL_VIEW / "@pontifex_test_player_base" / "addons"
            if not minimal:
                player_base_mod.mkdir(parents=True, exist_ok=True)
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
                    *(["--volume", f"{run_dir / 'live-control'}:/run/pontifex/live-control:ro"] if live else []),
                    *(["--mount", f"type=bind,source={live_extension_dir / 'pontifex_live_x64.so'},target={dedicated.INSTALL_VIEW / 'pontifex_live_x64.so'},readonly"] if live else []),
                    *(["--mount", f"type=bind,source={live_extension_dir / 'pontifex_live.so'},target={dedicated.INSTALL_VIEW / 'pontifex_live.so'},readonly"] if live else []),
                    "--volume",
                    f"{dedicated.LEGACY_INSTALL}:{dedicated.LEGACY_INSTALL}:ro",
                    "--mount",
                    "type=bind,"
                    f"source={dedicated.CA_CERTIFICATE_BUNDLE},"
                    "target=/etc/ssl/certs/ca-certificates.crt,readonly",
                    # SteamCMD's dedicated payload marks its omitted player
                    # content as deleted even when a PBO is placed in the
                    # base addons directory. Register the one licensed PBO
                    # explicitly as a read-only server mod instead.
                    *([] if minimal else ["--volume", f"{info['character_payload']}:{player_base_mod / 'characters_f.pbo'}:ro"]),
                    "--workdir",
                    str(dedicated.INSTALL_VIEW),
                    "--env",
                    f"LD_LIBRARY_PATH={dedicated.INSTALL_VIEW}:{dedicated.INSTALL_VIEW / 'linux64'}",
                    SERVER_IMAGE,
                    *server_command,
                ],
                check=False,
            )
            phase("server_container_launch_returned", returncode=server_run.returncode)
            if server_run.returncode != 0:
                raise RuntimeError(f"server container launch failed: {server_run.stderr.strip()}")

            state = {
                "run_id": run_id,
                "network": network,
                "server_container": server_name,
                "client_container": client_name,
                "live": live,
                "live_control": str(run_dir / "live-control") if live else None,
            }
            dedicated.atomic_json(MULTIPLAYER_STATE, state)

            server_deadline = time.monotonic() + 30
            while time.monotonic() < server_deadline:
                startup_assertion = "sqf.executed" if e2e else ("smoke.init.sqf" if plan else "sqf.executed")
                if f"PONTIFEX_TEST|PASS|server|{startup_assertion}" in container_logs(server_name):
                    break
                if not container_running(server_name):
                    raise RuntimeError("server exited before mission initialization")
                time.sleep(1)

            client_mods = [
                rf"S:\steamapps\common\Arma 3\{Path(item['client_path']).name}"
                for item in official_client_content["official_components"]
            ]
            if not minimal:
                client_mods.extend(
                    [
                        r"S:\steamapps\common\Arma 3\@CBA_A3",
                        r"S:\steamapps\common\Arma 3\@ace",
                        r"S:\steamapps\common\Arma 3\@zen",
                        r"S:\steamapps\common\Arma 3\@cordis",
                        r"S:\steamapps\common\Arma 3\@fieldutils",
                        r"S:\steamapps\common\Arma 3\@advsys",
                        r"S:\steamapps\common\Arma 3\@vigil",
                    ]
                )
            client_args = [
                "-noLauncher",
                "-noSplash",
                "-skipIntro",
                "-noPause",
                "-noSound",
                "-noBattlEye",
                "-x=1280",
                "-y=720",
                "-name=PontifexClientA",
                r"-profiles=Z:\run\pontifex\profile",
                f"-mod={';'.join(client_mods)}",
            ]
            # The native -connect route reaches Steam-valid connection but
            # leaves this Arma build on an uninteractive black pre-role
            # surface.  The proven path is the normal main-menu Direct
            # Connect flow, so the autonomous E2E join adapter must begin
            # there too.
            if not manual and (not e2e or native_connect):
                client_args.extend([f"-connect={server_ip}", f"-port={port}"])
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
                    *(
                        ["--publish", "127.0.0.1:5904:5900", "--env", "PONTIFEX_COMPOSITOR_VNC=1"]
                        if manual
                        else (["--publish", "127.0.0.1:5904:5900", "--env", "PONTIFEX_TEST_VNC=1"]
                              if os.environ.get("PONTIFEX_TEST_VNC") == "1" else [])
                    ),
                    # The VNC/manual runs established that Pixman's software
                    # compositor is stable for Xwayland.  Arma remains a
                    # separate DXVK/Vulkan client on the NVIDIA GPU; this
                    # selects only Weston's presentation renderer.  The
                    # headless GL compositor has an observed Xwayland abort
                    # under this load (signal 6), so apply the known-good
                    # presentation path to the autonomous E2E as well.
                    *( ["--env", "PONTIFEX_COMPOSITOR_RENDERER=pixman"] if (manual or e2e or plan is not None) else [] ),
                    # This is a compositor-local VNC endpoint for the E2E
                    # join adapter.  Unlike manual mode there is no Docker
                    # publish rule, so it is unreachable from the host.
                    # Live UI development uses the same authenticated,
                    # container-private RFB observability backend as
                    # autonomous visual scenarios. No Docker publish rule
                    # is added here; manual mode remains the only path that
                    # explicitly binds a host loopback diagnostic port.
                    *( ["--env", "PONTIFEX_COMPOSITOR_VNC=1"] if (e2e or visual_required or ui_scenarios or live) else [] ),
                    "--env",
                    "NVIDIA_DRIVER_CAPABILITIES=graphics,display,utility,compat32",
                    "--env",
                    "PONTIFEX_LOG_DIR=/run/pontifex",
                    "--env",
                    "PROTON_LOG=1",
                    "--env",
                    "PROTON_LOG_DIR=/run/pontifex",
                    "--volume",
                    f"{CLIENT_HOME}:/home/pontifex",
                    "--volume",
                    f"{RUNTIME / 'dependency-mods' / '@CBA_A3'}:/home/pontifex/.steam/debian-installation/steamapps/common/Arma 3/@CBA_A3:ro",
                    "--volume",
                    f"{RUNTIME / 'dependency-mods' / '@ace'}:/home/pontifex/.steam/debian-installation/steamapps/common/Arma 3/@ace:ro",
                    "--volume",
                    f"{RUNTIME / 'dependency-mods' / '@zen'}:/home/pontifex/.steam/debian-installation/steamapps/common/Arma 3/@zen:ro",
                    "--volume",
                    f"{RUNTIME / 'mods' / '@cordis'}:/home/pontifex/.steam/debian-installation/steamapps/common/Arma 3/@cordis:ro",
                    "--volume",
                    f"{RUNTIME / 'mods' / '@fieldutils'}:/home/pontifex/.steam/debian-installation/steamapps/common/Arma 3/@fieldutils:ro",
                    "--volume",
                    f"{RUNTIME / 'mods' / '@advsys'}:/home/pontifex/.steam/debian-installation/steamapps/common/Arma 3/@advsys:ro",
                    "--volume",
                    f"{RUNTIME / 'mods' / '@vigil'}:/home/pontifex/.steam/debian-installation/steamapps/common/Arma 3/@vigil:ro",
                    "--volume",
                    f"{ROOT}:/pontifex:ro",
                    "--volume",
                    f"{client_dir}:/run/pontifex:rw",
                    IMAGE,
                    "manual" if manual else "test",
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
                    "official_content": {
                        "server": {
                            **official_server_content,
                            "core": str(official_server_content["core"]["path"]),
                            "official_components": [
                                {**item, "path": str(item["path"])}
                                for item in official_server_content["official_components"]
                            ],
                        },
                        "client": official_client_content,
                    },
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

            if manual:
                result.update({"status": "READY", "reason": "awaiting_human", "cleanup": {"deferred": True}})
                dedicated.atomic_json(run_dir / "results.json", result)
                print(f"manual run ready: {run_id}")
                print(f"manual deadline: {timeout_seconds} seconds")
                print(f"manual VNC tunnel: ssh -N -L 5904:127.0.0.1:5904 {manual_ssh_target()}")

            deadline = time.monotonic() + timeout_seconds
            server_complete = None
            client_complete = None
            server_assertions: list[dict] = []
            client_assertions: list[dict] = []
            samples = []
            next_sample = 0.0
            join_adapter_attempted = False
            visual_probe_attempted = False
            visual_probe_report = None
            ui_probes_attempted: set[str] = set()
            ui_probe_reports: dict[str, dict] = {}
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
                if terminal_results_ready(server_complete, client_complete, manual=manual, live=live, server_text=server_text, client_text=client_text):
                    if live:
                        reason = "live_ready"
                        result["status"] = "READY"
                    else:
                        reason = "complete"
                    phase("terminal_results_detected", reason=reason, server_status=server_complete["status"], client_status=client_complete["status"])
                    break
                if visual_required and not visual_probe_attempted and "TRIBUNAL_VISUAL|ARMED" in client_text:
                    visual_probe_attempted = True
                    visual_output = client_dir / "visual-proof.json"
                    visual_probe = docker(
                        ["exec", client_name, "python3", "/pontifex/tools/tribunal_visual_probe.py", "--output", "/run/pontifex/visual-proof.json", "--timeout", "30"],
                        check=False,
                    )
                    (client_dir / "visual-proof-console.log").write_text((visual_probe.stdout or "") + (visual_probe.stderr or ""), encoding="utf-8")
                    if visual_output.is_file():
                        visual_probe_report = json.loads(visual_output.read_text(encoding="utf-8"))
                        attach_evidence(result, EvidenceAttachment("framebuffer-transition", "client-a", "visual-framebuffer", visual_output, visual_probe_report))
                    if visual_probe.returncode != 0 or not visual_probe_report or visual_probe_report.get("status") != "PASS":
                        reason = "visual_probe_failed"
                        break
                ui_scenario = next(
                    (
                        scenario for scenario in ui_scenarios
                        if scenario.identifier not in ui_probes_attempted
                        and str(scenario.metadata["visual_armed_marker"]) in client_text
                    ),
                    None,
                )
                if ui_scenario is not None:
                    ui_probes_attempted.add(ui_scenario.identifier)
                    ui_probe_report = None
                    visual_driver = ui_scenario.metadata.get("visual_driver")
                    ui_output = client_dir / f"{ui_scenario.identifier}-visual.json"
                    if visual_driver == "tabbed-control":
                        probe_args = [
                            "exec", "-e", "DISPLAY=:0", client_name,
                            "python3", "/pontifex/tools/tribunal_ui_probe.py",
                            "--output", f"/run/pontifex/{ui_output.name}",
                            "--regions", json.dumps(ui_scenario.metadata["visual_regions"], separators=(",", ":")),
                            "--initial-index", str(ui_scenario.metadata["visual_initial_index"]),
                            "--target-index", str(ui_scenario.metadata["visual_target_index"]),
                            "--timeout", "45",
                        ]
                        evidence_kind = "interactive-framebuffer-sequence"
                    elif visual_driver == "map-markers":
                        probe_args = [
                            "exec", "-e", "DISPLAY=:0", client_name,
                            "python3", "/pontifex/tools/tribunal_map_probe.py",
                            "--output", f"/run/pontifex/{ui_output.name}",
                            "--regions", json.dumps(ui_scenario.metadata["visual_regions"], separators=(",", ":")),
                            "--initial-index", str(ui_scenario.metadata["visual_initial_index"]),
                            "--target-index", str(ui_scenario.metadata["visual_target_index"]),
                            "--map-region", json.dumps(ui_scenario.metadata["map_region"], separators=(",", ":")),
                            "--expected-anchor", json.dumps(ui_scenario.metadata["map_expected_anchor"], separators=(",", ":")),
                            "--timeout", "55",
                        ]
                        evidence_kind = "interactive-map-marker-sequence"
                    elif visual_driver == "designation-input":
                        probe_args = [
                            "exec", "-e", "DISPLAY=:0", client_name,
                            "python3", "/pontifex/tools/tribunal_designation_probe.py",
                            "--output", f"/run/pontifex/{ui_output.name}",
                            "--timeout", "300",
                        ]
                        evidence_kind = "interactive-designation-sequence"
                    elif visual_driver == "zeus-placement":
                        probe_args = [
                            "exec", "-e", "DISPLAY=:0", client_name,
                            "python3", "/pontifex/tools/tribunal_zeus_probe.py",
                            "--output", f"/run/pontifex/{ui_output.name}",
                            "--placements", str(ui_scenario.metadata.get("zeus_placements", 2)),
                            "--marker-prefix", str(ui_scenario.metadata.get("zeus_marker_prefix", "TRIBUNAL_APS_ZEUS")),
                            "--timeout", "240",
                        ]
                        evidence_kind = "interactive-curator-placement-sequence"
                    elif visual_driver == "ace-interaction":
                        interaction_point = ui_scenario.metadata["interaction_point"]
                        point_marker = ui_scenario.metadata.get("interaction_point_marker")
                        if point_marker:
                            matches = re.findall(
                                re.escape(str(point_marker)) + r"(\[[^\]]+\])",
                                client_text,
                            )
                            if matches:
                                interaction_point = json.loads(matches[-1])
                        probe_args = [
                            "exec", "-e", "DISPLAY=:0", client_name,
                            "python3", "/pontifex/tools/tribunal_ace_probe.py",
                            "--output", f"/run/pontifex/{ui_output.name}",
                            "--interaction-point", json.dumps(
                                interaction_point, separators=(",", ":")
                            ),
                            "--activation-region", json.dumps(
                                ui_scenario.metadata["activation_region"], separators=(",", ":")
                            ),
                            "--minimum-mean-luma", str(
                                ui_scenario.metadata.get("minimum_mean_luma", 0)
                            ),
                            "--maximum-frame-delta", str(
                                ui_scenario.metadata.get("maximum_frame_delta", 0.12)
                            ),
                            "--timeout", "60",
                        ]
                        evidence_kind = "interactive-ace-sequence"
                    else:
                        raise RuntimeError(f"unsupported Tribunal visual driver: {visual_driver}")
                    ui_probe = docker(probe_args, check=False)
                    (client_dir / f"{ui_scenario.identifier}-visual-console.log").write_text(
                        (ui_probe.stdout or "") + (ui_probe.stderr or ""), encoding="utf-8"
                    )
                    if ui_output.is_file():
                        ui_probe_report = json.loads(ui_output.read_text(encoding="utf-8"))
                        ui_probe_reports[ui_scenario.identifier] = ui_probe_report
                        attach_evidence(result, EvidenceAttachment(
                            evidence_kind, "client-a", ui_scenario.identifier,
                            ui_output, ui_probe_report,
                        ))
                    if ui_probe.returncode != 0 or not ui_probe_report or ui_probe_report.get("status") != "PASS":
                        reason = "ui_probe_failed"
                        break
                if not container_running(server_name):
                    reason = "server_exited"
                    break
                if not container_running(client_name):
                    reason = "client_exited"
                    break
                if (
                    e2e
                    and not native_connect
                    and not join_adapter_attempted
                    and (client_dir / "client.rpt").exists()
                    and (client_dir / "client.rpt").stat().st_size > 10_000
                ):
                    adapter = run_join_adapter(
                        client_name,
                        client_dir / "join-adapter.json",
                        server_ip=server_ip,
                        server_port=port,
                    )
                    join_adapter_attempted = True
                    (client_dir / "join-adapter-console.log").write_text(
                        f"returncode={adapter.returncode}\n{adapter.stdout}{adapter.stderr}", encoding="utf-8"
                    )
                    if adapter.returncode != 0:
                        reason = "join_adapter_failed"
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
            server_expected = E2E_SERVER_EXPECTED if e2e else (plan.server_expected if plan else SERVER_EXPECTED)
            client_expected = E2E_CLIENT_EXPECTED if e2e else (plan.client_expected if plan else CLIENT_EXPECTED)
            server_missing, server_error = validate_origin(server_assertions, server_complete, server_expected)
            client_missing, client_error = validate_origin(client_assertions, client_complete, client_expected)
            result.update(
                {
                    "assertions": server_assertions + client_assertions,
                    "origins": {
                        "server": {"complete": server_complete, "missing": server_missing},
                        "client-a": {"complete": client_complete, "missing": client_missing},
                    },
                    "resource_samples": samples,
                    **({"join_adapter_attempted": join_adapter_attempted} if e2e else {}),
                    **({"visual_probe_attempted": visual_probe_attempted, "visual_probe": visual_probe_report} if visual_required else {}),
                    **(
                        {
                            "ui_probes_attempted": sorted(ui_probes_attempted),
                            "ui_probes": ui_probe_reports,
                            **(
                                {
                                    "ui_probe_attempted": bool(ui_probes_attempted),
                                    "ui_probe": ui_probe_reports.get(ui_scenarios[0].identifier),
                                }
                                if len(ui_scenarios) == 1 else {}
                            ),
                        }
                        if ui_scenarios else {}
                    ),
                }
            )
            if live and reason == "live_ready" and not server_error and not client_error:
                result["status"] = "READY"
                result["reason"] = "live_ready"
            elif manual and reason == "timeout":
                result["status"] = "READY"
                result["reason"] = "manual_timeout"
            elif reason != "complete":
                result["reason"] = reason
            elif server_error:
                result["reason"] = server_error
            elif client_error:
                result["reason"] = client_error
            else:
                result["status"] = "PASS"
                result["reason"] = "complete"
        except BaseException as exc:
            phase("exception", error=f"{type(exc).__name__}: {exc}")
            result["reason"] = "runner_error"
            result["error"] = f"{type(exc).__name__}: {exc}"
        finally:
            if server_name:
                (server_dir / "console.log").write_text(container_logs(server_name), encoding="utf-8")
                shutil.copy2(server_dir / "console.log", server_dir / "server.rpt")
            if client_name:
                (client_dir / "console.log").write_text(container_logs(client_name), encoding="utf-8")
                combine_rpts(client_dir, client_dir / "client.rpt")
            if live and result["status"] == "READY":
                cleanup = {"deferred": True, "state_removed": False}
            else:
                cleanup = {
                    "client_removed": validated_remove_container(client_name, run_id),
                    "server_removed": validated_remove_container(server_name, run_id),
                    "network_removed": validated_remove_network(network, run_id) if network else True,
                }
            if "state_removed" not in cleanup:
                cleanup["state_removed"] = all(cleanup.values())
            if cleanup["state_removed"]:
                MULTIPLAYER_STATE.unlink(missing_ok=True)
            result["cleanup"] = cleanup
            manifest["finished_at"] = dedicated.utc_now()
            manifest["gpu_finish"] = gpu_sample()
            dedicated.atomic_json(run_dir / "manifest.json", manifest)
            # A healthy developer session intentionally retains its containers,
            # private network and state file.  It is therefore READY rather
            # than a failed cleanup; `pontifex live stop` owns that teardown.
            if not (live and result["status"] == "READY") and not all(cleanup.values()):
                result["status"] = "FAIL"
                result["reason"] = "cleanup_failed"
            write_result(run_dir, result)
            for signum, handler in previous_signal_handlers.items():
                signal.signal(signum, handler)
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


def live_state() -> dict:
    """Read and validate the sole active developer-live session."""
    if not MULTIPLAYER_STATE.is_file():
        raise RuntimeError("no Pontifex live session is active")
    state = json.loads(MULTIPLAYER_STATE.read_text(encoding="utf-8"))
    if not state.get("live"):
        raise RuntimeError("the active Pontifex runtime is not Developer Live Mode")
    control = Path(str(state.get("live_control", "")))
    if not control.is_dir() or control.parent.parent != RUNS:
        raise RuntimeError("live command directory is invalid")
    return state


# A live snippet is delivered through the extension and executed with `call
# compile`, which performs no preprocessing, and it is returned through Arma's
# fixed callExtension output buffer.  Both limits were measured against the
# running dedicated server: a 20000-byte payload round-trips, 24000 truncates,
# and a `//` comment raises "Invalid number in expression" at the comment.
# Rejecting them here turns two confusing engine syntax errors into one clear
# message.  Mission .sqf files are preprocessed normally and are not affected.
LIVE_COMMAND_MAX_BYTES = 19 * 1024


def strip_sqf_string_literals(source: str) -> str:
    """Blank out SQF string literals so comment detection cannot match inside one.

    SQF quotes with either delimiter and escapes by doubling it, so `"a""b"` and
    `'a''b'` are single strings.  A URL or a quoted `/*` is ordinary data, not a
    comment, and must not be rejected.
    """

    out: list[str] = []
    quote: str | None = None
    index = 0
    while index < len(source):
        char = source[index]
        if quote is None:
            if char in ('"', "'"):
                quote = char
                out.append(" ")
            else:
                out.append(char)
            index += 1
            continue
        # Inside a literal: a doubled delimiter is an escaped quote, not the end.
        if char == quote:
            if index + 1 < len(source) and source[index + 1] == quote:
                out.append("  ")
                index += 2
                continue
            quote = None
        out.append(" ")
        index += 1
    return "".join(out)


def build_live_payload(endpoint: str, source: str, command_id: str) -> str:
    """Return the exact bytes the mission will receive for one live command."""

    if endpoint == "client":
        # The live server is the only endpoint granted file patching.  It
        # relays explicitly requested client snippets over the mission's
        # already-authenticated multiplayer channel, keeping Proton's client
        # launch arguments identical to normal smoke/integration/gameplay.
        escaped = source.rstrip().replace('"', '""')
        source = (
            f'private _owner = missionNamespace getVariable ["PONTIFEX_LIVE_clientOwner", -1]; '
            f'if (_owner > 0) then {{ ["{escaped}", "{command_id}"] remoteExecCall ["PONTIFEX_LIVE_fnc_exec", _owner]; }} '
            f'else {{ diag_log "PONTIFEX_LIVE|client-a|NO_OWNER"; }};'
        )
    return f'diag_log "PONTIFEX_LIVE|{endpoint}|COMMAND|{command_id}";\n{source.rstrip()}\n'


def write_live_command(endpoint: str, source: str) -> Path:
    """Atomically publish one explicit developer command to one mission VM."""
    if endpoint not in {"server", "client"}:
        raise RuntimeError("live endpoint must be server or client")
    if not source.strip():
        raise RuntimeError("live command must be non-empty")
    if "//" in strip_sqf_string_literals(source) or "/*" in strip_sqf_string_literals(source):
        raise RuntimeError(
            "live commands are executed with `call compile`, which does not run the preprocessor, "
            "so // and /* */ comments are syntax errors. Remove the comments."
        )
    state = live_state()
    control = Path(state["live_control"])
    command_id = uuid.uuid4().hex
    # Measure what the mission actually receives.  A client snippet is wrapped in
    # a relay and has every quote doubled, so a source comfortably under the
    # bound can still deliver an oversized, silently truncated payload.
    payload = build_live_payload(endpoint, source, command_id)
    payload_bytes = len(payload.encode("utf-8"))
    if payload_bytes > LIVE_COMMAND_MAX_BYTES:
        raise RuntimeError(
            f"live command delivers a {payload_bytes}-byte payload, over the "
            f"{LIVE_COMMAND_MAX_BYTES}-byte limit; Arma's callExtension output buffer silently "
            "truncates larger payloads. Split it into smaller commands "
            f"(source was {len(source.encode('utf-8'))} bytes before relay wrapping and quote escaping)."
        )
    target_endpoint = "server" if endpoint == "client" else endpoint
    target = control / f"{target_endpoint}.sqf"
    temporary = target.with_suffix(".sqf.new")
    temporary.write_text(payload, encoding="utf-8")
    os.replace(temporary, target)
    record = {"at": dedicated.utc_now(), "id": command_id, "endpoint": endpoint, "source": source}
    with (control / "commands.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    return target


def show_live_status() -> int:
    try:
        state = live_state()
    except (RuntimeError, OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    output = {
        "run_id": state["run_id"],
        "server_running": bool((item := container_inspect(state["server_container"])) and item["State"]["Running"]),
        "client_running": bool((item := container_inspect(state["client_container"])) and item["State"]["Running"]),
        "control": state["live_control"],
    }
    print(json.dumps(output, sort_keys=True))
    return 0 if output["server_running"] and output["client_running"] else 1


def run_live_test(name: str) -> int:
    scripts = {
        "config": (
            'diag_log format ["PONTIFEX_LIVE_TEST|PASS|server|config|B_Soldier_A_F=%1", isClass (configFile >> "CfgVehicles" >> "B_Soldier_A_F")];',
            'diag_log format ["PONTIFEX_LIVE_TEST|PASS|client-a|config|hasInterface=%1", hasInterface];',
        ),
        "namespace": (
            'missionNamespace setVariable ["PONTIFEX_LIVE_namespace", "PASS", true]; diag_log "PONTIFEX_LIVE_TEST|PASS|server|namespace";',
            'diag_log format ["PONTIFEX_LIVE_TEST|PASS|client-a|namespace|value=%1", missionNamespace getVariable ["PONTIFEX_LIVE_namespace", "missing"]];',
        ),
    }
    if name not in scripts:
        print(f"unknown live demonstration test: {name}", file=sys.stderr)
        return 2
    server, client = scripts[name]
    # One inbox update prevents the poller from observing only the latter of
    # two rapid writes.  The server assertion runs first, then relays the
    # client assertion using the same controlled transport as `live exec`.
    command_id = uuid.uuid4().hex
    escaped = client.replace('"', '""')
    combined = (
        f'{server}\nprivate _owner = missionNamespace getVariable ["PONTIFEX_LIVE_clientOwner", -1]; '
        f'if (_owner > 0) then {{ ["{escaped}", "{command_id}"] remoteExecCall ["PONTIFEX_LIVE_fnc_exec", _owner]; }};'
    )
    write_live_command("server", combined)
    print(json.dumps({"status": "queued", "test": name}, sort_keys=True))
    return 0


def reset_live() -> int:
    client = 'diag_log "PONTIFEX_LIVE|client-a|RESET";'.replace('"', '""')
    write_live_command(
        "server",
        '{ if (_x getVariable ["PONTIFEX_LIVE_owned", false]) then { deleteVehicle _x; }; } forEach vehicles; '
        'diag_log "PONTIFEX_LIVE|server|RESET"; '
        'private _owner = missionNamespace getVariable ["PONTIFEX_LIVE_clientOwner", -1]; '
        f'if (_owner > 0) then {{ ["{client}", "reset"] remoteExecCall ["PONTIFEX_LIVE_fnc_exec", _owner]; }};',
    )
    print('{"status":"reset_queued"}')
    return 0


def start_live(timeout_seconds: int) -> int:
    """Start live mode in a user service so terminal closure cannot kill it."""
    unit = "pontifex-live"
    command = [
        "systemd-run", "--user", "--unit", unit, "--collect", "--no-block",
        "--property=KillMode=control-group", "--property=TimeoutStartSec=3h",
        sys.executable, str(Path(__file__).resolve()), "live-worker", "--timeout", str(timeout_seconds),
    ]
    completed = subprocess.run(command, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if completed.returncode != 0:
        print(completed.stderr.strip(), file=sys.stderr)
        return completed.returncode
    print(completed.stdout.strip())
    print("Developer Live Mode is starting; run './pontifex live status' until it reports both endpoints ready.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    test = sub.add_parser("test")
    test.add_argument("--force-failure", action="store_true")
    test.add_argument("--timeout", type=int, default=int(os.environ.get("PONTIFEX_MULTIPLAYER_TIMEOUT", "720")))
    manual = sub.add_parser("manual")
    manual.add_argument("--timeout", type=int, default=int(os.environ.get("PONTIFEX_MANUAL_TIMEOUT", "7200")))
    e2e = sub.add_parser("e2e")
    e2e.add_argument("--timeout", type=int, default=int(os.environ.get("PONTIFEX_E2E_TIMEOUT", "720")))
    tier = sub.add_parser("tier")
    tier.add_argument("name", choices=("smoke", "integration", "gameplay", "capability"))
    tier.add_argument("--select", help="comma-separated test IDs; defaults to the whole tier")
    tier.add_argument("--timeout", type=int, default=int(os.environ.get("PONTIFEX_TIER_TIMEOUT", "360")))
    live_worker = sub.add_parser("live-worker")
    live_worker.add_argument("--timeout", type=int, default=int(os.environ.get("PONTIFEX_LIVE_TIMEOUT", "10800")))
    live_start = sub.add_parser("live-start")
    live_start.add_argument("--timeout", type=int, default=int(os.environ.get("PONTIFEX_LIVE_TIMEOUT", "10800")))
    live = sub.add_parser("live")
    live_sub = live.add_subparsers(dest="live_command", required=True)
    live_sub.add_parser("status")
    live_exec = live_sub.add_parser("exec")
    live_exec.add_argument("endpoint", choices=("server", "client"))
    live_exec.add_argument("source")
    live_test = live_sub.add_parser("test")
    live_test.add_argument("name", choices=("config", "namespace"))
    live_sub.add_parser("reset")
    live_sub.add_parser("stop")
    client = sub.add_parser("client")
    client.add_argument("action", choices=("status", "image", "preflight", "login", "stop-login"))
    sub.add_parser("status")
    sub.add_parser("stop")
    args = parser.parse_args()
    if args.command == "test":
        return run_multiplayer(args.force_failure, args.timeout)
    if args.command == "manual":
        return run_multiplayer(False, args.timeout, manual=True)
    if args.command == "e2e":
        return run_multiplayer(False, args.timeout, e2e=True)
    if args.command == "tier":
        try:
            plan = select_plan(args.name, args.select)
        except ValueError as exc:
            print(str(exc), file=sys.stderr)
            return 2
        return run_multiplayer(False, args.timeout, plan=plan)
    if args.command == "live-worker":
        return run_multiplayer(False, args.timeout, plan=LIVE_PLAN, live=True)
    if args.command == "live-start":
        return start_live(args.timeout)
    if args.command == "live":
        if args.live_command == "status":
            return show_live_status()
        if args.live_command == "exec":
            try:
                path = write_live_command(args.endpoint, args.source)
            except RuntimeError as exc:
                print(str(exc), file=sys.stderr)
                return 1
            print(json.dumps({"status": "queued", "endpoint": args.endpoint, "path": str(path)}, sort_keys=True))
            return 0
        if args.live_command == "test":
            return run_live_test(args.name)
        if args.live_command == "reset":
            return reset_live()
        if args.live_command == "stop":
            cleanup = clean_multiplayer_state()
            print(json.dumps(cleanup, sort_keys=True))
            return 0 if all(cleanup.values()) else 1
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

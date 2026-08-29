#!/usr/bin/env python3
"""Pontifex's small, project-local Arma dedicated-server controller."""

from __future__ import annotations

import argparse
import contextlib
import datetime as dt
import fcntl
import json
import os
from pathlib import Path, PurePosixPath
import re
import shutil
import signal
import subprocess
import sys
import time
import urllib.request
import uuid
import zipfile

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from pontifex_paths import PATHS, TRIBUNAL_ROOT

if str(TRIBUNAL_ROOT) in sys.path:
    sys.path.remove(str(TRIBUNAL_ROOT))
sys.path.insert(0, str(TRIBUNAL_ROOT))

from tribunal.assertions.protocol import parse_protocol as parse_tribunal_protocol
from tribunal.mission.pbo import build_mission_pbo, sha256
from tribunal.reporting.artifacts import atomic_json


ROOT = PROJECT_ROOT
SERVER = ROOT / "server"
RUNTIME = PATHS.server
INSTALL_VIEW = RUNTIME / "install"
CA_CERTIFICATE_BUNDLE = RUNTIME / "ca-certificates.crt"
DEPENDENCIES = PATHS.dependencies
CACHE = PATHS.cache
RUNS = PATHS.runs
BUILD = PATHS.builds
LOCK_FILE = SERVER / "dependencies.lock.json"
STEAM_DLC_CATALOG = SERVER / "steam-arma3-dlc-catalog.json"
STATE_FILE = RUNTIME / "server.json"
LEGACY_INSTALL = Path(
    os.environ.get(
        "PONTIFEX_ARMA_INSTALL",
        "/mnt/services/arma3-server/pufferpanel/data/servers/80e9c1f3",
    )
)
INSTALLER_STEAM_APP_ID = "233780"
RUNTIME_STEAM_APP_ID = "107410"
MISSION_NAME = "Pontifex_Integration.Stratis"
MISSION_SOURCE = ROOT / "tests" / "missions" / MISSION_NAME
EXPECTED_ASSERTIONS = {
    "sqf.executed",
    "server.isDedicated",
    "server.isServer",
    "core.config",
    "field_utilities.config",
    "advanced_systems.config",
    "visual_support_tablet.config",
    "core.function",
    "field_utilities.function",
    "advanced_systems.function",
    "visual_support_tablet.function",
    "core.postInit",
    "harness.forcedFailure",
}
def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def official_component_policy() -> dict:
    """Classify content from the SteamCMD App 233780 layout, not a name list.

    App 233780's root Addons bank is core content.  Its sibling directories
    that contain an Addons bank are official components.  The supported
    ``creatordlc`` branch also supplies Creator DLC banks, so their Steam app
    metadata—not directory naming—keeps those third-party banks explicit-only.
    """
    manifest = LEGACY_INSTALL / "steamapps" / "appmanifest_233780.acf"
    if not manifest.is_file():
        raise RuntimeError(f"SteamCMD App 233780 manifest not found: {manifest}")
    catalog = json.loads(STEAM_DLC_CATALOG.read_text(encoding="utf-8"))["apps"]
    creator_banks = {
        item["component_bank"].casefold(): item
        for item in catalog.values()
        if item.get("component_bank") and item["developers"] != ["Bohemia Interactive"]
    }
    components = []
    excluded_creator = []
    for directory in sorted(LEGACY_INSTALL.iterdir(), key=lambda item: item.name.casefold()):
        addons = directory / "addons"
        if not directory.is_dir() or directory.name.startswith("@") or not addons.is_dir():
            continue
        pbos = sorted(path.name for path in addons.glob("*.pbo") if path.is_file())
        if pbos:
            component_id = directory.name.casefold()
            creator = creator_banks.get(component_id)
            if creator:
                excluded_creator.append(
                    {
                        "id": component_id,
                        "path": str(directory),
                        "steam_name": creator["name"],
                        "developers": creator["developers"],
                    }
                )
            else:
                components.append({"id": component_id, "path": directory, "pbos": pbos})
    return {
        "steam_app": int(INSTALLER_STEAM_APP_ID),
        "core": {"path": LEGACY_INSTALL / "addons"},
        "official_components": components,
        "excluded": {
            "creator_or_community_dlc": excluded_creator,
            "workshop_or_user_mods": "directories prefixed with @ are explicit-only",
        },
    }


def official_component_ids() -> tuple[str, ...]:
    return tuple(item["id"] for item in official_component_policy()["official_components"])


def lock_data() -> dict:
    return json.loads(LOCK_FILE.read_text(encoding="utf-8"))


def dependency_status() -> list[dict]:
    status = []
    for item in lock_data()["dependencies"]:
        marker = DEPENDENCIES / item["directory"] / ".pontifex-dependency.json"
        installed = False
        if marker.is_file():
            try:
                installed_data = json.loads(marker.read_text(encoding="utf-8"))
                installed = installed_data.get("sha256") == item["sha256"]
            except (OSError, json.JSONDecodeError):
                pass
        status.append({**item, "path": str(marker.parent), "installed": installed})
    return status


def safe_extract(archive: Path, destination: Path) -> None:
    with zipfile.ZipFile(archive) as bundle:
        for entry in bundle.infolist():
            parts = PurePosixPath(entry.filename).parts
            if PurePosixPath(entry.filename).is_absolute() or ".." in parts:
                raise RuntimeError(f"unsafe ZIP entry: {entry.filename}")
        bundle.extractall(destination)


def provision_dependencies() -> list[dict]:
    DEPENDENCIES.mkdir(parents=True, exist_ok=True)
    CACHE.mkdir(parents=True, exist_ok=True)
    for item in lock_data()["dependencies"]:
        destination = DEPENDENCIES / item["directory"]
        current = next((x for x in dependency_status() if x["id"] == item["id"]), None)
        if current and current["installed"]:
            print(f"dependency ready: {item['name']} {item['version']}")
            continue

        archive = CACHE / item["archive"]
        if not archive.is_file() or sha256(archive) != item["sha256"]:
            temporary = archive.with_name(f".{archive.name}.{os.getpid()}.tmp")
            print(f"downloading: {item['name']} {item['version']}")
            request = urllib.request.Request(item["url"], headers={"User-Agent": "Pontifex-test-harness/1"})
            try:
                with urllib.request.urlopen(request) as response, temporary.open("wb") as output:
                    shutil.copyfileobj(response, output)
                if sha256(temporary) != item["sha256"]:
                    raise RuntimeError(f"checksum mismatch for {item['name']}")
                temporary.replace(archive)
            finally:
                temporary.unlink(missing_ok=True)

        staging = DEPENDENCIES / f".extract-{item['id']}-{os.getpid()}"
        shutil.rmtree(staging, ignore_errors=True)
        staging.mkdir(parents=True)
        try:
            safe_extract(archive, staging)
            extracted = staging / item["directory"]
            if not (extracted / "addons").is_dir():
                raise RuntimeError(f"{item['name']} archive did not contain {item['directory']}/addons")
            if destination.exists() or destination.is_symlink():
                if destination.is_symlink() or destination.is_file():
                    destination.unlink()
                else:
                    shutil.rmtree(destination)
            extracted.replace(destination)
            atomic_json(
                destination / ".pontifex-dependency.json",
                {
                    "id": item["id"],
                    "name": item["name"],
                    "version": item["version"],
                    "sha256": item["sha256"],
                    "source": item["url"],
                    "installed_at": utc_now(),
                },
            )
        finally:
            shutil.rmtree(staging, ignore_errors=True)
        print(f"installed: {item['name']} {item['version']}")
    return dependency_status()


def arma_version() -> dict:
    binary = LEGACY_INSTALL / "arma3server_x64"
    raw = binary.read_bytes()
    match = re.search(rb"Arma 3 (\d+\.\d+\.\d+)", raw)
    version = match.group(1).decode() if match else "unknown"
    manifest = LEGACY_INSTALL / "steamapps" / "appmanifest_233780.acf"
    build_id = "unknown"
    if manifest.is_file():
        found = re.search(r'"buildid"\s+"(\d+)"', manifest.read_text(errors="replace"))
        if found:
            build_id = found.group(1)
    return {
        "version": version,
        "steam_build_id": build_id,
        "binary": str(binary),
        "binary_sha256": sha256(binary),
    }


def prepare_runtime() -> None:
    binary = LEGACY_INSTALL / "arma3server_x64"
    if not binary.is_file():
        raise RuntimeError(f"Arma server binary not found: {binary}")
    RUNTIME.mkdir(parents=True, exist_ok=True)
    # The bare Ubuntu image used for the confined dedicated process deliberately
    # contains no package-managed trust store.  Steam's OpenSSL transport looks
    # specifically for this standard bundle; stage a copy in the disposable
    # runtime so it can be mounted read-only without granting the process any
    # host configuration or write access.
    host_ca_bundle = Path("/etc/ssl/certs/ca-certificates.crt")
    if not host_ca_bundle.is_file():
        raise RuntimeError(f"host CA certificate bundle not found: {host_ca_bundle}")
    shutil.copy2(host_ca_bundle, CA_CERTIFICATE_BUNDLE)
    CA_CERTIFICATE_BUNDLE.chmod(0o644)
    if INSTALL_VIEW.exists() or INSTALL_VIEW.is_symlink():
        if INSTALL_VIEW.is_symlink() or INSTALL_VIEW.is_file():
            INSTALL_VIEW.unlink()
        else:
            shutil.rmtree(INSTALL_VIEW)
    INSTALL_VIEW.mkdir()
    excluded = {
        "config.cfg",
        "parameters.txt",
        "profiles",
        "mpmissions",
        "server_console.log",
    }
    for source in LEGACY_INSTALL.iterdir():
        if source.name in excluded:
            continue
        (INSTALL_VIEW / source.name).symlink_to(source, target_is_directory=source.is_dir())
    # App 233780 is solely the SteamCMD distribution/update application.  The
    # dedicated executable validates multiplayer tickets in Arma 3's Steamworks
    # application context (107410), so its disposable runtime overlay must use
    # that ID.  The override remains only for explicitly controlled A/B probes.
    runtime_app_id = os.environ.get("PONTIFEX_SERVER_RUNTIME_APPID", RUNTIME_STEAM_APP_ID)
    if runtime_app_id not in {RUNTIME_STEAM_APP_ID, INSTALLER_STEAM_APP_ID}:
        raise RuntimeError(f"unsupported runtime Steam App ID: {runtime_app_id}")
    app_id = INSTALL_VIEW / "steam_appid.txt"
    app_id.unlink(missing_ok=True)
    app_id.write_text(f"{runtime_app_id}\n", encoding="ascii")
    missions = INSTALL_VIEW / "mpmissions"
    missions.mkdir()
    if MISSION_SOURCE.is_file():
        shutil.copy2(MISSION_SOURCE, missions / MISSION_SOURCE.name)
    else:
        # Always use a banked PBO.  See build_mission_pbo() for why a source
        # directory is intentionally not exposed to the dedicated executable.
        build_mission_pbo(MISSION_SOURCE, missions / f"{MISSION_NAME}.pbo")
    runtime_mods = RUNTIME / "mods"
    shutil.rmtree(runtime_mods, ignore_errors=True)
    runtime_mods.mkdir()
    pontifex_mods = {
        "@cordis": (BUILD / "current" / "@CORDIS", "CORDIS.pbo"),
        "@fieldutils": (BUILD / "current" / "@FieldUtils", "FieldUtils.pbo"),
        "@advsys": (BUILD / "current" / "@AdvSys", "AdvSys.pbo"),
        "@vigil": (BUILD / "current" / "@VIGIL_Support_Tablet", "VIGIL.pbo"),
    }
    for alias, (source, pbo_name) in pontifex_mods.items():
        deployed = runtime_mods / alias
        shutil.copytree(source, deployed)
        source_pbo = deployed / "addons" / pbo_name
        source_pbo.replace(deployed / "addons" / pbo_name.lower())
    dependency_mods = RUNTIME / "dependency-mods"
    shutil.rmtree(dependency_mods, ignore_errors=True)
    dependency_mods.mkdir()
    for directory in ("@CBA_A3", "@ace", "@zen"):
        source = DEPENDENCIES / directory
        deployed = dependency_mods / directory

        def link_or_copy(src: str, dst: str) -> str:
            try:
                os.link(src, dst)
                return dst
            except OSError:
                return shutil.copy2(src, dst)

        shutil.copytree(source, deployed, copy_function=link_or_copy)
    official_mods = RUNTIME / "official-mods"
    shutil.rmtree(official_mods, ignore_errors=True)
    official_mods.mkdir()
    for component in official_component_policy()["official_components"]:
        name = component["id"]
        deployed = official_mods / f"@pontifex_a3_{name}"
        deployed.mkdir()
        (deployed / "addons").symlink_to(component["path"] / "addons", target_is_directory=True)
        (deployed / "mod.cpp").write_text(
            f'name = "Arma 3 {name} test bank";\nauthor = "Bohemia Interactive";\n',
            encoding="utf-8",
        )
    mod_aliases = {
        "@cba_a3": dependency_mods / "@CBA_A3",
        "@ace": dependency_mods / "@ace",
        "@zen": dependency_mods / "@zen",
        "@cordis": runtime_mods / "@cordis",
        "@fieldutils": runtime_mods / "@fieldutils",
        "@advsys": runtime_mods / "@advsys",
        "@vigil": runtime_mods / "@vigil",
    }
    mod_aliases.update(
        {f"@pontifex_a3_{name}": official_mods / f"@pontifex_a3_{name}" for name in official_component_ids()}
    )
    for alias, target in mod_aliases.items():
        (INSTALL_VIEW / alias).symlink_to(target, target_is_directory=True)
    atomic_json(
        RUNTIME / "source.json",
        {
            "type": "symlink-view",
            "shared_read_only_source": str(LEGACY_INSTALL),
            "prepared_at": utc_now(),
            "arma": arma_version(),
        },
    )


def git_info() -> dict:
    commit = subprocess.check_output(["git", "-C", str(ROOT), "rev-parse", "HEAD"], text=True).strip()
    dirty_lines = subprocess.check_output(
        ["git", "-C", str(ROOT), "status", "--porcelain=v1"], text=True
    ).splitlines()
    return {"commit": commit, "dirty": bool(dirty_lines), "changes": dirty_lines}


def pbo_manifest() -> list[dict]:
    output = []
    for path in sorted((BUILD / "current").glob("*/addons/*.pbo")):
        # Keep the Evidence Contract's historical project-relative artifact
        # identity even though generated builds now live outside the checkout.
        evidence_path = Path("build") / path.relative_to(BUILD)
        output.append({"path": str(evidence_path), "size": path.stat().st_size, "sha256": sha256(path)})
    return output


def proc_start_ticks(pid: int) -> str | None:
    try:
        content = Path(f"/proc/{pid}/stat").read_text()
        return content[content.rfind(")") + 2 :].split()[19]
    except (OSError, IndexError):
        return None


def validated_state() -> tuple[dict | None, str]:
    if not STATE_FILE.is_file():
        return None, "no state file"
    try:
        state = json.loads(STATE_FILE.read_text(encoding="utf-8"))
        pid = int(state["pid"])
    except (OSError, ValueError, KeyError, json.JSONDecodeError):
        return None, "malformed state file"
    if proc_start_ticks(pid) != str(state.get("proc_start_ticks")):
        return None, "recorded process is not running"
    try:
        if os.getpgid(pid) != pid:
            return None, "recorded process no longer owns its process group"
        cmdline = Path(f"/proc/{pid}/cmdline").read_bytes().replace(b"\0", b" ").decode(errors="replace")
    except OSError:
        return None, "recorded process is not running"
    if "arma3server_x64" not in cmdline or str(INSTALL_VIEW) not in cmdline:
        return None, "recorded PID identity does not match Pontifex Arma"
    return state, "running"


def stop_server(grace: float = 12.0) -> bool:
    state, reason = validated_state()
    if not state:
        STATE_FILE.unlink(missing_ok=True)
        print(f"Pontifex server: stopped ({reason})")
        return True
    pid = int(state["pid"])
    for sig, wait_seconds in ((signal.SIGINT, grace), (signal.SIGTERM, 5.0), (signal.SIGKILL, 2.0)):
        try:
            os.killpg(pid, sig)
        except ProcessLookupError:
            break
        deadline = time.monotonic() + wait_seconds
        while time.monotonic() < deadline and proc_start_ticks(pid) == str(state["proc_start_ticks"]):
            time.sleep(0.2)
        if proc_start_ticks(pid) != str(state["proc_start_ticks"]):
            break
    stopped = proc_start_ticks(pid) != str(state["proc_start_ticks"])
    if stopped:
        STATE_FILE.unlink(missing_ok=True)
        print(f"Pontifex server: stopped (run {state.get('run_id', 'unknown')})")
    else:
        print(f"Pontifex server: failed to stop PID {pid}", file=sys.stderr)
    return stopped


def parse_protocol(text: str) -> tuple[list[dict], dict | None]:
    assertions, complete = parse_tribunal_protocol(text, prefix="PONTIFEX_TEST")
    for assertion in assertions:
        assertion["detail"] = assertion["detail"].strip()
    return assertions, complete


def newest_rpt(profile: Path) -> Path | None:
    reports = list(profile.rglob("*.rpt"))
    return max(reports, key=lambda path: path.stat().st_mtime_ns) if reports else None


def write_result(run_dir: Path, result: dict) -> None:
    result["finished_at"] = utc_now()
    atomic_json(run_dir / "results.json", result)
    print(f"result: {result['status']} ({result['reason']})")
    print(f"evidence: {run_dir}")


@contextlib.contextmanager
def runtime_lock():
    RUNTIME.mkdir(parents=True, exist_ok=True)
    with (RUNTIME / "control.lock").open("w") as handle:
        try:
            fcntl.flock(handle, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc:
            raise RuntimeError("another Pontifex server/test lifecycle owns the runtime lock") from exc
        yield


def run_dedicated(force_failure: bool, timeout_seconds: int) -> int:
    run_id = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%SZ") + f"-{uuid.uuid4().hex[:8]}"
    run_dir = RUNS / run_id
    profile = run_dir / "profile"
    run_dir.mkdir(parents=True)
    profile.mkdir()
    latest = RUNS / "latest"
    if latest.exists() or latest.is_symlink():
        latest.unlink()
    latest.symlink_to(run_id)

    manifest = {
        "schema": 1,
        "run_id": run_id,
        "mode": "dedicated-forced-failure" if force_failure else "dedicated",
        "started_at": utc_now(),
        "timeout_seconds": timeout_seconds,
        "git": git_info(),
        "arma": arma_version(),
        "dependencies": dependency_status(),
        "builds": [],
        "command": ["./pontifex", "test", "dedicated"] + (["--force-failure"] if force_failure else []),
    }
    atomic_json(run_dir / "manifest.json", manifest)
    result = {
        "schema": 1,
        "run_id": run_id,
        "status": "FAIL",
        "reason": "runner_error",
        "complete_seen": False,
        "assertions": [],
        "missing_assertions": sorted(EXPECTED_ASSERTIONS),
        "server_exit_code": None,
    }

    with runtime_lock():
        stop_server()
        try:
            print(f"run: {run_id}")
            print("building Pontifex PBOs...")
            with (run_dir / "build.log").open("w", encoding="utf-8") as build_log:
                build = subprocess.run(
                    [str(ROOT / "pontifex"), "build"],
                    cwd=ROOT,
                    stdout=build_log,
                    stderr=subprocess.STDOUT,
                    text=True,
                )
            if build.returncode != 0:
                result["reason"] = "build_failed"
                write_result(run_dir, result)
                return 1

            dependencies = provision_dependencies()
            if not all(item["installed"] for item in dependencies):
                result["reason"] = "dependency_provision_failed"
                write_result(run_dir, result)
                return 1
            prepare_runtime()

            manifest["dependencies"] = dependencies
            manifest["builds"] = pbo_manifest()
            atomic_json(run_dir / "manifest.json", manifest)

            config_template = (SERVER / "config" / "dedicated.cfg.in").read_text(encoding="utf-8")
            (run_dir / "server.cfg").write_text(
                config_template.replace("@FORCE_FAILURE@", "1" if force_failure else "0").replace(
                    "@REQUIRE_CLIENT@", "0"
                ),
                encoding="utf-8",
            )
            shutil.copy2(SERVER / "config" / "basic.cfg", run_dir / "basic.cfg")

            mod_paths = [
                *(f"@pontifex_a3_{name}" for name in official_component_ids()),
                "@cba_a3",
                "@ace",
                "@zen",
                "@cordis",
                "@fieldutils",
                "@advsys",
                "@vigil",
            ]
            port = int(os.environ.get("PONTIFEX_TEST_PORT", "2312"))
            command = [
                str(INSTALL_VIEW / "arma3server_x64"),
                "-ip=127.0.0.1",
                f"-port={port}",
                f"-config={run_dir / 'server.cfg'}",
                f"-cfg={run_dir / 'basic.cfg'}",
                f"-profiles={profile}",
                "-name=pontifex-test",
                f"-mod={';'.join(mod_paths)}",
                "-world=empty",
                "-autoInit",
                "-noSound",
                "-noPause",
                "-noSplash",
            ]
            manifest["server_command"] = command
            manifest["port"] = port
            atomic_json(run_dir / "manifest.json", manifest)

            console_path = run_dir / "server-console.log"
            console = console_path.open("w", encoding="utf-8")
            environment = os.environ.copy()
            environment["LD_LIBRARY_PATH"] = f"{INSTALL_VIEW}:{INSTALL_VIEW / 'linux64'}"
            process = subprocess.Popen(
                command,
                cwd=INSTALL_VIEW,
                stdout=console,
                stderr=subprocess.STDOUT,
                env=environment,
                start_new_session=True,
                text=True,
            )
            atomic_json(
                STATE_FILE,
                {
                    "pid": process.pid,
                    "proc_start_ticks": proc_start_ticks(process.pid),
                    "run_id": run_id,
                    "started_at": utc_now(),
                    "command": command,
                },
            )

            deadline = time.monotonic() + timeout_seconds
            assertions: list[dict] = []
            complete = None
            reason = "timeout"
            try:
                while time.monotonic() < deadline:
                    if console_path.is_file():
                        assertions, complete = parse_protocol(console_path.read_text(errors="replace"))
                    if complete:
                        reason = "complete"
                        break
                    exit_code = process.poll()
                    if exit_code is not None:
                        reason = "server_exited"
                        result["server_exit_code"] = exit_code
                        break
                    time.sleep(0.5)
            finally:
                stop_server()
                try:
                    result["server_exit_code"] = process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    result["server_exit_code"] = None
                STATE_FILE.unlink(missing_ok=True)
                console.close()

            report = run_dir / "server.rpt"
            shutil.copy2(console_path, report)
            assertions, complete = parse_protocol(report.read_text(errors="replace"))

            names = {item["name"] for item in assertions}
            missing = sorted(EXPECTED_ASSERTIONS - names)
            failures = [item for item in assertions if item["status"] == "FAIL"]
            result.update(
                {
                    "complete_seen": complete is not None,
                    "protocol_complete": complete,
                    "assertions": assertions,
                    "missing_assertions": missing,
                    "log_source": "captured Linux dedicated-server stdout/stderr stream",
                }
            )
            if reason == "timeout":
                result["reason"] = "timeout_waiting_for_complete"
            elif reason == "server_exited" and not complete:
                result["reason"] = "server_exited_before_complete"
            elif not assertions or missing:
                result["reason"] = "malformed_or_incomplete_protocol"
            elif not complete:
                result["reason"] = "missing_complete_marker"
            elif complete["assertions"] != len(assertions):
                result["reason"] = "assertion_count_mismatch"
            elif failures or complete["status"] != "PASS" or complete["failures"] != 0:
                result["reason"] = "assertion_failure"
            else:
                result["status"] = "PASS"
                result["reason"] = "complete"
            write_result(run_dir, result)
            return 0 if result["status"] == "PASS" else 1
        except Exception as exc:
            stop_server()
            result["reason"] = "runner_error"
            result["error"] = f"{type(exc).__name__}: {exc}"
            write_result(run_dir, result)
            return 1


def show_status() -> int:
    state, reason = validated_state()
    if state:
        print(f"Pontifex server: running PID {state['pid']} (run {state['run_id']})")
        print(f"state: {STATE_FILE}")
    else:
        print(f"Pontifex server: stopped ({reason})")
    print(f"Arma: {arma_version()['version']} (Steam build {arma_version()['steam_build_id']})")
    for item in dependency_status():
        status = "ready" if item["installed"] else "missing"
        print(f"dependency: {item['name']} {item['version']} [{status}]")
    if (RUNS / "latest" / "results.json").is_file():
        latest = json.loads((RUNS / "latest" / "results.json").read_text())
        print(f"latest run: {latest['run_id']} {latest['status']} ({latest['reason']})")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)
    test_parser = subparsers.add_parser("test")
    test_parser.add_argument("--force-failure", action="store_true")
    test_parser.add_argument(
        "--timeout",
        type=int,
        default=int(os.environ.get("PONTIFEX_DEDICATED_TIMEOUT", "180")),
    )
    dependency_parser = subparsers.add_parser("dependencies")
    dependency_parser.add_argument("action", choices=("status", "provision"), nargs="?", default="status")
    subparsers.add_parser("status")
    subparsers.add_parser("stop")
    args = parser.parse_args()

    if args.command == "test":
        return run_dedicated(args.force_failure, args.timeout)
    if args.command == "dependencies":
        if args.action == "provision":
            provision_dependencies()
        for item in dependency_status():
            print(f"{item['name']} {item['version']}: {'ready' if item['installed'] else 'missing'} ({item['path']})")
        return 0 if all(item["installed"] for item in dependency_status()) else 1
    if args.command == "status":
        return show_status()
    if args.command == "stop":
        return 0 if stop_server() else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())

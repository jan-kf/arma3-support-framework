"""Single source of truth for Pontifex repository and runtime-state paths."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
from typing import Mapping


@dataclass(frozen=True)
class PontifexPaths:
    project_root: Path
    state_root: Path
    builds: Path
    runs: Path
    client: Path
    server: Path
    dependencies: Path
    cache: Path
    tools: Path
    legacy_layout: bool


def resolve_paths(project_root: Path, environ: Mapping[str, str] | None = None) -> PontifexPaths:
    env = os.environ if environ is None else environ
    project_root = project_root.resolve()
    configured = env.get("PONTIFEX_STATE_ROOT", "").strip()
    if configured:
        state_root = Path(configured).expanduser().resolve()
    elif project_root.parent.name == "arma-projects":
        state_root = (project_root.parent.parent / "arma-state" / project_root.name).resolve()
    else:
        state_root = project_root
    legacy = state_root == project_root
    if legacy:
        return PontifexPaths(
            project_root=project_root,
            state_root=state_root,
            builds=project_root / "build",
            runs=project_root / "runs",
            client=project_root / "client" / "runtime",
            server=project_root / "server" / "runtime",
            dependencies=project_root / "server" / "dependencies",
            cache=project_root / "server" / "cache",
            tools=project_root / ".tools",
            legacy_layout=True,
        )
    dependencies = state_root / "dependencies"
    return PontifexPaths(
        project_root=project_root,
        state_root=state_root,
        builds=state_root / "builds",
        runs=state_root / "runs",
        client=state_root / "client",
        server=state_root / "server",
        dependencies=dependencies,
        cache=dependencies / "cache",
        tools=dependencies / "tools",
        legacy_layout=False,
    )


def resolve_tribunal_root(project_root: Path, environ: Mapping[str, str] | None = None) -> Path:
    """Locate the independent Tribunal checkout without a host-specific path."""

    env = os.environ if environ is None else environ
    configured = env.get("TRIBUNAL_ROOT", "").strip()
    candidates = [Path(configured).expanduser()] if configured else [
        project_root.resolve().parent / "tribunal",
        project_root.resolve().parent.parent / "tribunal",
    ]
    for candidate in candidates:
        resolved = candidate.resolve()
        if (resolved / "tribunal/__init__.py").is_file() and (resolved / "bin/tribunal").is_file():
            return resolved
    raise RuntimeError("independent Tribunal checkout not found; set TRIBUNAL_ROOT")


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PATHS = resolve_paths(PROJECT_ROOT)
TRIBUNAL_ROOT = resolve_tribunal_root(PROJECT_ROOT)

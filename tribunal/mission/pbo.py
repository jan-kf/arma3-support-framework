"""Deterministic, uncompressed Arma mission PBO construction."""

from __future__ import annotations

import hashlib
from pathlib import Path, PurePosixPath
import struct


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_mission_pbo(source: Path, destination: Path) -> dict:
    """Build a reproducible raw PBO and validate all packaged paths first."""
    if not source.is_dir():
        raise RuntimeError(f"mission directory not found: {source}")
    files = sorted(path for path in source.rglob("*") if path.is_file())
    if not files:
        raise RuntimeError(f"mission directory is empty: {source}")
    entries: list[tuple[str, bytes]] = []
    for path in files:
        name = path.relative_to(source).as_posix()
        if not name.isascii() or ".." in PurePosixPath(name).parts:
            raise RuntimeError(f"unsafe mission PBO path: {name}")
        entries.append((name, path.read_bytes()))

    header = bytearray()
    for name, data in entries:
        header.extend(name.encode("ascii"))
        header.append(0)
        header.extend(struct.pack("<IIIII", 0, 0, 0, 0, len(data)))
    header.append(0)
    header.extend(struct.pack("<IIIII", 0, 0, 0, 0, 0))
    body = bytes(header) + b"".join(data for _, data in entries)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(body + b"\0" + hashlib.sha1(body).digest())
    return {"source": str(source), "destination": str(destination), "files": [name for name, _ in entries], "sha256": sha256(destination), "size": destination.stat().st_size}

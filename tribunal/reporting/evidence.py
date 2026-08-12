"""Incremental typed evidence attachments for Tribunal result documents."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class EvidenceAttachment:
    kind: str
    origin: str
    label: str
    path: Path | None = None
    metadata: dict[str, object] = field(default_factory=dict)

    def as_result_record(self) -> dict[str, object]:
        record = asdict(self)
        record["path"] = str(self.path) if self.path is not None else None
        return record


def attach_evidence(result: dict, attachment: EvidenceAttachment) -> None:
    """Extend schema-2 results without changing existing assertion records."""

    result.setdefault("evidence", []).append(attachment.as_result_record())

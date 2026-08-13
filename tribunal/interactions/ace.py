"""Product-neutral contract for future ACE interaction execution.

This module deliberately models the request without reaching into ACE's
private action arrays. Runtime discovery/activation belongs in an ACE-version
adapter and must still prove actor availability before executing an action.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AceInteractionRequest:
    """Describe one actor-visible ACE action without project semantics."""

    actor: str
    target: str
    action_path: tuple[str, ...]
    interaction_type: str = "external"
    expect_available: bool = True
    activate: bool = True

    def __post_init__(self) -> None:
        if not self.actor or not self.target:
            raise ValueError("ACE interaction requests require actor and target identities")
        if not self.action_path or any(not part for part in self.action_path):
            raise ValueError("ACE interaction requests require a non-empty action path")
        if self.interaction_type not in {"external", "self"}:
            raise ValueError("ACE interaction type must be external or self")
        if self.activate and not self.expect_available:
            raise ValueError("an unavailable ACE interaction cannot be activated")

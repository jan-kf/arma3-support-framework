"""Declarative network profiles; application belongs to a scoped helper."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class NetworkProfile:
    name: str
    latency_ms: int
    jitter_ms: int = 0
    loss_percent: float = 0.0

    def tc_netem_arguments(self) -> tuple[str, ...]:
        args = ["delay", f"{self.latency_ms}ms"]
        if self.jitter_ms:
            args.append(f"{self.jitter_ms}ms")
        if self.loss_percent:
            args.extend(("loss", f"{self.loss_percent:g}%"))
        return tuple(args)


NETWORK_PROFILES = {
    "lan": NetworkProfile("lan", 1),
    "normal": NetworkProfile("normal", 25, 5),
    "remote": NetworkProfile("remote", 100, 15),
    "poor": NetworkProfile("poor", 175, 40, 1.0),
}

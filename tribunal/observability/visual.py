"""Tolerant framebuffer metrics for generic rendered-state assertions."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class FrameMetrics:
    mean_luma: float
    dark_fraction: float
    nonblack_fraction: float

    def as_dict(self) -> dict[str, float]:
        return asdict(self)


def frame_metrics(rgb: bytes) -> FrameMetrics:
    if not rgb or len(rgb) % 3:
        raise ValueError("RGB frame must contain complete pixels")
    pixels = len(rgb) // 3
    luma = 0.0
    dark = 0
    nonblack = 0
    for offset in range(0, len(rgb), 3):
        red, green, blue = rgb[offset:offset + 3]
        value = 0.2126 * red + 0.7152 * green + 0.0722 * blue
        luma += value
        dark += value < 12
        nonblack += red > 2 or green > 2 or blue > 2
    return FrameMetrics(luma / pixels, dark / pixels, nonblack / pixels)


def visual_transition(baseline: FrameMetrics, present: FrameMetrics, absent: FrameMetrics) -> tuple[bool, dict[str, object]]:
    """Verify a deliberately dark full-screen element appeared then disappeared.

    This uses structural luminance ratios rather than exact pixels, tolerating
    animation and minor rendering changes in the underlying game scene.
    """

    appeared = present.dark_fraction >= 0.70 and present.mean_luma <= baseline.mean_luma * 0.45
    disappeared = absent.dark_fraction <= present.dark_fraction - 0.25 and absent.mean_luma >= present.mean_luma * 1.8
    return appeared and disappeared, {
        "appeared": appeared,
        "disappeared": disappeared,
        "baseline": baseline.as_dict(),
        "present": present.as_dict(),
        "absent": absent.as_dict(),
    }

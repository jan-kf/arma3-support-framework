"""Generic region and transition evidence for rendered UI controls."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Region:
    x: int
    y: int
    width: int
    height: int

    def center(self) -> tuple[int, int]:
        return self.x + self.width // 2, self.y + self.height // 2


@dataclass(frozen=True)
class RegionMetrics:
    mean_rgb: tuple[float, float, float]
    mean_luma: float

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class RegionDifference:
    changed_pixels: int
    changed_fraction: float
    centroid: tuple[float, float] | None
    bounding_box: tuple[int, int, int, int] | None

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def region_metrics(rgb: bytes, frame_width: int, frame_height: int, region: Region) -> RegionMetrics:
    if len(rgb) != frame_width * frame_height * 3:
        raise ValueError("RGB frame size does not match dimensions")
    if region.width <= 0 or region.height <= 0 or region.x < 0 or region.y < 0:
        raise ValueError("region must have positive dimensions inside the frame")
    if region.x + region.width > frame_width or region.y + region.height > frame_height:
        raise ValueError("region extends outside the frame")
    totals = [0, 0, 0]
    pixels = region.width * region.height
    for y in range(region.y, region.y + region.height):
        start = (y * frame_width + region.x) * 3
        row = rgb[start:start + region.width * 3]
        for offset in range(0, len(row), 3):
            totals[0] += row[offset]
            totals[1] += row[offset + 1]
            totals[2] += row[offset + 2]
    means = tuple(value / pixels for value in totals)
    return RegionMetrics(means, 0.2126 * means[0] + 0.7152 * means[1] + 0.0722 * means[2])


def selected_region_index(
    rgb: bytes,
    frame_width: int,
    frame_height: int,
    regions: tuple[Region, ...],
    *,
    minimum_luma: float = 40.0,
    contrast_ratio: float = 1.45,
) -> tuple[int | None, list[RegionMetrics]]:
    """Identify one highlighted control without exact-pixel matching."""

    if len(regions) < 2:
        raise ValueError("selected-region detection requires at least two regions")
    metrics = [region_metrics(rgb, frame_width, frame_height, region) for region in regions]
    ranked = sorted(enumerate(metrics), key=lambda item: item[1].mean_luma, reverse=True)
    best_index, best = ranked[0]
    runner_up = ranked[1][1]
    selected = best.mean_luma >= minimum_luma and best.mean_luma >= runner_up.mean_luma * contrast_ratio
    return (best_index if selected else None), metrics


def changed_pixel_fraction(before: bytes, after: bytes, *, channel_tolerance: int = 18) -> float:
    if len(before) != len(after) or not before or len(before) % 3:
        raise ValueError("frames must be equal, non-empty RGB buffers")
    changed = 0
    pixels = len(before) // 3
    for offset in range(0, len(before), 3):
        if max(abs(before[offset + channel] - after[offset + channel]) for channel in range(3)) > channel_tolerance:
            changed += 1
    return changed / pixels


def region_difference(
    before: bytes,
    after: bytes,
    frame_width: int,
    frame_height: int,
    region: Region,
    *,
    channel_tolerance: int = 18,
) -> RegionDifference:
    """Summarize meaningful pixel changes inside one bounded UI region.

    Coordinates are returned in full-frame pixel space so callers can compare
    the evidence directly with a map control's projected screen coordinate.
    """

    # Reuse validation shared with all regional observability helpers.
    region_metrics(before, frame_width, frame_height, region)
    region_metrics(after, frame_width, frame_height, region)
    changed: list[tuple[int, int]] = []
    for y in range(region.y, region.y + region.height):
        for x in range(region.x, region.x + region.width):
            offset = (y * frame_width + x) * 3
            if max(
                abs(before[offset + channel] - after[offset + channel])
                for channel in range(3)
            ) > channel_tolerance:
                changed.append((x, y))
    if not changed:
        return RegionDifference(0, 0.0, None, None)
    xs = [point[0] for point in changed]
    ys = [point[1] for point in changed]
    return RegionDifference(
        len(changed),
        len(changed) / (region.width * region.height),
        (sum(xs) / len(xs), sum(ys) / len(ys)),
        (min(xs), min(ys), max(xs), max(ys)),
    )

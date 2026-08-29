"""Render validated typed Eden entities and Sync links for generated missions."""

from __future__ import annotations

from collections.abc import Iterable

from tribunal.runner.model import MissionEntity, MissionSync


def render_typed_entities(
    entities: Iterable[MissionEntity],
    syncs: Iterable[MissionSync],
    *,
    first_item: int,
    first_id: int = 100,
) -> tuple[str, str]:
    """Return mission Entity items and a Connections block.

    Positions use mission.sqm order: X, absolute world altitude, world Y. The API deliberately
    exposes only typed Object/Logic entities and named Sync links, never raw SQM.
    """
    rows = tuple(entities)
    links = tuple(syncs)
    object_fixtures: list[MissionEntity] = []
    for entity in rows:
        if entity.data_type != "Object":
            continue
        for previous in object_fixtures:
            distance_squared = sum(
                (left - right) ** 2
                for left, right in zip(entity.position, previous.position)
            )
            if distance_squared < 100:
                raise ValueError(
                    f"mission objects {previous.name} and {entity.name} overlap fixture footprints "
                    f"at {previous.position} and {entity.position}"
                )
        object_fixtures.append(entity)
    ids = {entity.name: first_id + offset for offset, entity in enumerate(rows)}
    rendered: list[str] = []
    for offset, entity in enumerate(rows):
        x, altitude, world_y = entity.position
        side = " side=\"Empty\"; flags=7;" if entity.data_type == "Object" else ""
        rendered.append(
            f" class Item{first_item + offset} {{ dataType=\"{entity.data_type}\"; "
            f"class PositionInfo {{ position[]={{ {x},{altitude},{world_y} }}; }};"
            f"{side} class Attributes {{ name=\"{entity.name}\"; }}; "
            f"id={ids[entity.name]}; type=\"{entity.class_name}\"; }};"
        )
    if not links:
        return "".join(rendered), ""
    connection_rows = []
    for offset, link in enumerate(links):
        connection_rows.append(
            f" class Item{offset} {{ linkID={offset}; item0={ids[link.source]}; "
            f"item1={ids[link.target]}; class CustomData {{ type=\"Sync\"; }}; }};"
        )
    connections = (
        f" class Connections {{ class LinkIDProvider {{ nextID={len(links)}; }}; "
        f"class Links {{ items={len(links)};"
        + "".join(connection_rows)
        + " }; };"
    )
    return "".join(rendered), connections

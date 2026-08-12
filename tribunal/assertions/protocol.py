"""Generic line-protocol parsing and completion validation for Tribunal."""

from __future__ import annotations

import re


def parse_protocol(text: str, *, prefix: str) -> tuple[list[dict], dict | None]:
    """Parse a project-selected Tribunal assertion prefix from an Arma log.

    The prefix is a compatibility boundary, not a framework brand.  Existing
    projects may retain an established log prefix while adopting Tribunal.
    """
    escaped = re.escape(prefix)
    assertion = re.compile(
        rf"{escaped}\|(PASS|FAIL)\|(server|client-a)\|([^|\r\n\"]+)(?:\|([^\r\n\"]*))?"
    )
    complete = re.compile(
        rf"{escaped}\|COMPLETE\|(server|client-a)\|status=(PASS|FAIL)\|assertions=(\d+)\|failures=(\d+)"
    )
    records = [
        {"status": match.group(1), "origin": match.group(2), "name": match.group(3), "detail": match.group(4) or ""}
        for match in assertion.finditer(text)
    ]
    completions = list(complete.finditer(text))
    final = None
    if completions:
        match = completions[-1]
        final = {
            "origin": match.group(1),
            "status": match.group(2),
            "assertions": int(match.group(3)),
            "failures": int(match.group(4)),
        }
    return records, final


def validate_origin(assertions: list[dict], complete: dict | None, expected: set[str]) -> tuple[list[str], str | None]:
    """Fail closed unless all expected assertions pass and completion agrees."""
    names = {item["name"] for item in assertions}
    missing = sorted(expected - names)
    if missing or not assertions:
        return missing, "malformed_or_incomplete_protocol"
    if complete is None:
        return missing, "missing_complete_marker"
    if complete["assertions"] != len(assertions):
        return missing, "assertion_count_mismatch"
    if any(item["status"] == "FAIL" for item in assertions) or complete["status"] != "PASS" or complete["failures"]:
        return missing, "assertion_failure"
    return missing, None

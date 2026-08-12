"""Pontifex Advanced Systems' permanent Tribunal APS scenario contract.

The SQF fixture remains in the compatibility mission adapter during this first
boundary migration so historical autonomous artifacts remain byte-for-byte
comparable. Its assertions and ownership now live with the APS feature.
"""

from tribunal.runner.model import Scenario


TRIBUNAL_SCENARIO = Scenario(
    identifier="aps-intercept",
    tier="gameplay",
    server_expected=frozenset({
        "aps.positive.projectileSpawned",
        "aps.positive.collisionCourse",
        "aps.positive.engaged",
        "aps.positive.neutralized",
        "aps.positive.chargeConsumed",
        "aps.positive.protected",
        "aps.control.disabledImpact",
        "aps.control.disabledNoEngagement",
        "aps.control.outsideEnvelope",
        "aps.control.directionAway",
        "aps.softkill.deflection",
    }),
    client_expected=frozenset({"aps.replication"}),
    # The existing generated SQF fixture is intentionally retained by the
    # Pontifex compatibility adapter for this migration commit.
    server_sqf="",
    client_sqf="",
    metadata={"product": "advanced-systems", "feature": "active-protection-system"},
)

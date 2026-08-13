"""Pontifex Advanced Systems' permanent Tribunal APS scenario contract.

The SQF fixture remains in the compatibility mission adapter during this first
boundary migration so historical autonomous artifacts remain byte-for-byte
comparable. Its assertions and ownership now live with the APS feature.
"""

from tribunal.runner.model import Scenario, ScenarioReview


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
    review=ScenarioReview(
        test_type="specification",
        behavior_contract="APS intercepts qualifying inbound threats, preserves disabled/outside/away controls, consumes the correct resource, and replicates the authoritative result.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="The matrix asserts causal player-visible protection and resource behavior; ledger and exact projectile identities are supplemental correlation rather than the public contract.",
        dependencies=("Tribunal direct-projectile fixture", "server-authoritative APS", "one authenticated client"),
        evidence_types=frozenset({"trajectory", "impact", "authoritative-state", "replication", "locality"}),
        locality_requirements="APS tracking, threat projectile, and authoritative ledger execute on the server; client-a observes replicated state.",
    ),
)

"""A generic rendered-presence/removal probe for the framebuffer backend."""

from tribunal.runner.model import Scenario, ScenarioReview


TRIBUNAL_SCENARIO = Scenario(
    identifier="visual-framebuffer",
    tier="capability",
    server_expected=frozenset(),
    client_expected=frozenset({"tribunal.visual.lifecycle"}),
    server_sqf="",
    client_sqf=r'''
diag_log "TRIBUNAL_VISUAL|ARMED";
uiSleep 5;
titleText ["TRIBUNAL VISUAL PROBE", "BLACK FADED", 0];
diag_log "TRIBUNAL_VISUAL|PRESENT";
uiSleep 10;
titleText ["", "BLACK IN", 0];
diag_log "TRIBUNAL_VISUAL|REMOVED";
uiSleep 2;
["tribunal.visual.lifecycle", true, "known full-screen element rendered then removed"] call _assert;
''',
    requires_project_mods=False,
    metadata={"capability": "visual", "observability_backend": "authenticated-rfb"},
    review=ScenarioReview(
        test_type="tooling",
        behavior_contract="Tribunal can capture and distinguish the presence and removal of a known rendered element on the live Arma framebuffer.",
        outcome="KEEP AS-IS AND SPEC-TEST",
        rationale="This validates a reusable evidence backend and contains no product-specific meaning.",
        dependencies=("loopback-only authenticated RFB", "live Arma surface"),
        evidence_types=frozenset({"framebuffer", "rendered-transition"}),
        locality_requirements="The rendered probe and captured surface belong to client-a only.",
    ),
)

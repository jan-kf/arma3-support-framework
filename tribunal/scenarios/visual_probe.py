"""A generic rendered-presence/removal probe for the framebuffer backend."""

from tribunal.runner.model import Scenario


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
)

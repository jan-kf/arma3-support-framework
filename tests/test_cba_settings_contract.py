"""Static, product-neutral contract for Pontifex CBA setting declarations."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

SETTING_FILES = {
    "advanced": ROOT / "source/advanced-systems/addons/AdvSys/functions/global/fn_initSettings.sqf",
    "vigil": ROOT / "source/visual-support-tablet/addons/VIGIL/functions/global/fn_initSettings.sqf",
    "field": ROOT / "source/field-utilities/addons/FieldUtils/functions/global/fn_initSettings.sqf",
}

# key: (file, kind, normalized default/bounds fragment, intended scope)
EXPECTED = {
    "YAS_playRadioMessages": ("advanced", "CHECKBOX", "true", "global"),
    "YAS_showDebugMessages": ("advanced", "CHECKBOX", "false", "global"),
    "YAS_ironDomeEngagementRadius": ("advanced", "SLIDER", "[100,5000,1000,0]", "global"),
    "YAS_apsAntiDroneEngagementRadius": ("advanced", "SLIDER", "[5,100,25,0]", "global"),
    "YAS_apsAntiDroneMinimumSpeed": ("advanced", "SLIDER", "[5,100,40,0]", "global"),
    "YSF_enableTablet": ("vigil", "CHECKBOX", "true", "global"),
    "YSF_playRadioMessages": ("vigil", "CHECKBOX", "true", "global"),
    "YSF_playSideMessages": ("vigil", "CHECKBOX", "true", "global"),
    "YSF_showDebugMessages": ("vigil", "CHECKBOX", "false", "global"),
    "YSF_monochromeBaseColor": ("vigil", "COLOR", "[0,1,0,1]", "local"),
    "YSF_laserVizColor": ("vigil", "COLOR", "[0,1,0,1]", "local"),
    "YFU_playSideMessages": ("field", "CHECKBOX", "true", "global"),
    "YFU_showDebugMessages": ("field", "CHECKBOX", "false", "global"),
    "YFU_monochromeBaseColor": ("field", "COLOR", "[0.15,0.95,0.15,1]", "local"),
    "YFU_bridge_perPlankBuildDelay": ("field", "SLIDER", "[0,10,1,2]", "global"),
}

CONSUMERS = {
    "YAS_playRadioMessages": ("source/advanced-systems/addons/AdvSys/functions/global/fn_utils.sqf", '"YAS_playRadioMessages"'),
    "YAS_showDebugMessages": ("source/advanced-systems/addons/AdvSys/functions/global/fn_utils.sqf", '"YAS_showDebugMessages"'),
    "YAS_ironDomeEngagementRadius": ("source/advanced-systems/addons/AdvSys/functions/iron_dome/fn_ironDome.sqf", '["YAS_ironDomeEngagementRadius", 1000]'),
    "YAS_apsAntiDroneEngagementRadius": ("source/advanced-systems/addons/AdvSys/functions/aps/fn_aps.sqf", '["YAS_apsAntiDroneEngagementRadius", 25]'),
    "YAS_apsAntiDroneMinimumSpeed": ("source/advanced-systems/addons/AdvSys/functions/aps/fn_aps.sqf", '["YAS_apsAntiDroneMinimumSpeed", 40]'),
    "YSF_enableTablet": ("source/visual-support-tablet/addons/VIGIL/functions/tablet/fn_ui_utils.sqf", '[\'YSF_enableTablet\', true]'),
    "YSF_playRadioMessages": ("source/visual-support-tablet/addons/VIGIL/functions/global/fn_utils.sqf", '"YSF_playRadioMessages"'),
    "YSF_playSideMessages": ("source/visual-support-tablet/addons/VIGIL/functions/global/fn_utils.sqf", '"YSF_playSideMessages"'),
    "YSF_showDebugMessages": ("source/visual-support-tablet/addons/VIGIL/functions/global/fn_utils.sqf", '"YSF_showDebugMessages"'),
    "YSF_monochromeBaseColor": ("source/visual-support-tablet/addons/VIGIL/functions/global/fn_init.sqf", '"YSF_monochromeBaseColor"'),
    "YSF_laserVizColor": ("source/visual-support-tablet/addons/VIGIL/functions/client/fn_irLaserViz.sqf", '["YSF_laserVizColor", [0,1,0,1]]'),
    "YFU_playSideMessages": ("source/field-utilities/addons/FieldUtils/functions/global/fn_core.sqf", '"YFU_playSideMessages"'),
    "YFU_showDebugMessages": ("source/field-utilities/addons/FieldUtils/functions/global/fn_core.sqf", '"YFU_showDebugMessages"'),
    "YFU_monochromeBaseColor": ("source/field-utilities/addons/FieldUtils/functions/fabricator/fn_assets.sqf", '["YFU_monochromeBaseColor", [0.15, 0.95, 0.15, 1]]'),
    "YFU_bridge_perPlankBuildDelay": ("source/field-utilities/addons/FieldUtils/functions/bridge/fn_bridgeUtils.sqf", '["YFU_bridge_perPlankBuildDelay", 1]'),
}


def normalized_block(source: str, key: str) -> str:
    key_at = source.index(f'"{key}"')
    start = source.rfind("[", 0, key_at)
    end_marker = "] call CBA_fnc_addSetting;"
    end = source.index(end_marker, key_at) + len(end_marker)
    return re.sub(r"\s+", "", source[start:end])


class CbaSettingsContractTests(unittest.TestCase):
    def test_exact_unique_declaration_matrix(self) -> None:
        sources = {name: path.read_text() for name, path in SETTING_FILES.items()}
        discovered: list[str] = []
        for source in sources.values():
            discovered.extend(re.findall(r'\[\s*"([^"]+)"\s*,\s*"(?:CHECKBOX|SLIDER|COLOR)"', source))
        self.assertEqual(len(discovered), 15)
        self.assertEqual(set(discovered), set(EXPECTED))
        self.assertEqual(len(discovered), len(set(discovered)))

        for key, (owner, kind, default, scope) in EXPECTED.items():
            block = normalized_block(sources[owner], key)
            self.assertIn(f'["{key}","{kind}",', block)
            self.assertIn(default, block)
            if scope == "global":
                self.assertTrue(block.endswith(",1]callCBA_fnc_addSetting;"), (key, block))
            else:
                self.assertNotRegex(block, r",1\]callCBA_fnc_addSetting;$")
                self.assertTrue(block.endswith("]callCBA_fnc_addSetting;"), (key, block))

    def test_every_setting_has_an_independent_consumer_and_matching_fallback(self) -> None:
        self.assertEqual(set(CONSUMERS), set(EXPECTED))
        for key, (relative, needle) in CONSUMERS.items():
            path = ROOT / relative
            self.assertNotIn(path, SETTING_FILES.values())
            self.assertIn(needle, path.read_text(), key)

        core = (ROOT / "source/core/addons/CORDIS/functions/global/fn_core.sqf").read_text()
        self.assertIn('missionNamespace getVariable [_settingName, true]', core)
        self.assertIn('missionNamespace getVariable [_settingName, false]', core)

    def test_debug_setting_description_matches_logging_semantics(self) -> None:
        description = "Debug messages are always written to the server log. When enabled, they are also shown in systemChat on clients."
        for owner in ("advanced", "vigil", "field"):
            self.assertIn(description, SETTING_FILES[owner].read_text())
        core = (ROOT / "source/core/addons/CORDIS/functions/global/fn_core.sqf").read_text()
        self.assertLess(core.index("remoteExecCall [\"YCD_fnc_showDebugLine\""), core.index("diag_log _line"))
        self.assertIn("if (missionNamespace getVariable [_settingName, false]) then", core)


if __name__ == "__main__":
    unittest.main()

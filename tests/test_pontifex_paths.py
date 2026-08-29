"""Runtime state follows the split layout and remains explicitly configurable."""

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from pontifex_paths import resolve_paths, resolve_tribunal_root  # noqa: E402


class PontifexPathTests(unittest.TestCase):
    def test_relocated_checkout_defaults_to_sibling_state_root(self) -> None:
        paths = resolve_paths(ROOT, {})
        expected = ROOT.parent.parent / "arma-state" / "pontifex"
        self.assertFalse(paths.legacy_layout)
        self.assertEqual(paths.state_root, expected)
        self.assertEqual(paths.runs, expected / "runs")
        self.assertEqual(paths.builds, expected / "builds")
        self.assertEqual(paths.client, expected / "client")
        self.assertEqual(paths.server, expected / "server")
        self.assertEqual(paths.dependencies, expected / "dependencies")

    def test_unrelocated_checkout_retains_legacy_fallback(self) -> None:
        legacy_root = Path("/srv/pontifex")
        paths = resolve_paths(legacy_root, {})
        self.assertTrue(paths.legacy_layout)
        self.assertEqual(paths.runs, legacy_root / "runs")
        self.assertEqual(paths.builds, legacy_root / "build")

    def test_configured_root_uses_the_split_state_layout(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            paths = resolve_paths(ROOT, {"PONTIFEX_STATE_ROOT": str(root)})
            self.assertFalse(paths.legacy_layout)
            self.assertEqual(paths.runs, root / "runs")
            self.assertEqual(paths.builds, root / "builds")
            self.assertEqual(paths.client, root / "client")
            self.assertEqual(paths.server, root / "server")
            self.assertEqual(paths.dependencies, root / "dependencies")
            self.assertEqual(paths.cache, root / "dependencies/cache")
            self.assertEqual(paths.tools, root / "dependencies/tools")

    def test_tribunal_checkout_resolves_before_and_after_project_relocation(self) -> None:
        expected = Path("/mnt/services/tribunal")
        self.assertEqual(resolve_tribunal_root(ROOT), expected)
        relocated = Path("/mnt/services/arma-projects/pontifex")
        self.assertEqual(resolve_tribunal_root(relocated), expected)


if __name__ == "__main__":
    unittest.main()

"""Runtime state is configurable without changing the legacy checkout layout."""

import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from pontifex_paths import resolve_paths, resolve_tribunal_root  # noqa: E402


class PontifexPathTests(unittest.TestCase):
    def test_unconfigured_paths_preserve_the_current_layout(self) -> None:
        paths = resolve_paths(ROOT, {})
        self.assertTrue(paths.legacy_layout)
        self.assertEqual(paths.runs, ROOT / "runs")
        self.assertEqual(paths.builds, ROOT / "build")
        self.assertEqual(paths.client, ROOT / "client/runtime")
        self.assertEqual(paths.server, ROOT / "server/runtime")
        self.assertEqual(paths.dependencies, ROOT / "server/dependencies")

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

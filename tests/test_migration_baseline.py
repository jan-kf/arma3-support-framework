"""The repository migration must preserve Tribunal's scenario contract."""

import json
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import migration_baseline  # noqa: E402


class MigrationBaselineTests(unittest.TestCase):
    def test_scenario_and_assertion_inventory_is_unchanged(self) -> None:
        expected = json.loads((ROOT / "docs/migration-baseline.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(migration_baseline.inventory(ROOT / "tribunal.project.json"), expected)


if __name__ == "__main__":
    unittest.main()

"""Generated-state relocation preserves stable evidence artifact identities."""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import pontifex_server as dedicated  # noqa: E402


class ArtifactManifestTests(unittest.TestCase):
    def test_external_build_root_keeps_project_relative_evidence_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            build = Path(temporary) / "builds"
            pbo = build / "current" / "@CORDIS" / "addons" / "CORDIS.pbo"
            pbo.parent.mkdir(parents=True)
            pbo.write_bytes(b"pbo")

            with patch.object(dedicated, "BUILD", build):
                artifacts = dedicated.pbo_manifest()

        self.assertEqual(artifacts[0]["path"], "build/current/@CORDIS/addons/CORDIS.pbo")
        self.assertEqual(artifacts[0]["size"], 3)


if __name__ == "__main__":
    unittest.main()

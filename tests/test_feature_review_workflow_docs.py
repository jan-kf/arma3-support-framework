"""Cold-read discoverability guard for the canonical feature-review workflow."""

from pathlib import Path
import re
import sys
import unittest


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from pontifex_paths import TRIBUNAL_ROOT  # noqa: E402

ENTRY = ROOT / "CLAUDE.md"
PROGRAM = TRIBUNAL_ROOT / "docs" / "feature-review-program.md"


class FeatureReviewWorkflowDocsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.entry = ENTRY.read_text(encoding="utf-8")
        cls.program = PROGRAM.read_text(encoding="utf-8")
        cls.program_flat = " ".join(cls.program.split())

    def test_memoryless_agent_discovers_one_canonical_program(self) -> None:
        self.assertIn("$TRIBUNAL_ROOT/docs/feature-review-program.md", self.entry)
        self.assertIn("the canonical 12-question feature-review", self.entry)
        self.assertIn("/mnt/services/arma-knowledge/README.md", self.entry)
        self.assertIn("$TRIBUNAL_ROOT/tribunal/evidence/README.md", self.entry)
        self.assertIn("short prompt quoted in the canonical program is sufficient", self.entry)

    def test_cold_read_covers_selection_review_evidence_and_closeout(self) -> None:
        required = (
            "### Selecting the feature",
            "### Sacred Texts first",
            "### The canonical 12 questions",
            "### False-PASS and evidence rules",
            "Use authentic engine stimulus where practical",
            "### Execution and acceptance program",
            "### Evidence Contract and knowledge closeout",
            "### Progress accounting and final report",
            "highest-value unblocked surface",
            "fresh single-scenario autonomous proof",
            "ingest-evidence-v1 --package-file",
            "distill-tribunal",
            "OUR VERIFIED NOTES",
            "Zero generic findings is a valid result",
            "Feature-review completion",
            "Permanent automated coverage",
            "RETIRE / REMOVE",
            "MUST/SHOULD/DEFERRED/OPTIONAL",
        )
        for text in required:
            with self.subTest(text=text):
                self.assertIn(" ".join(text.split()), self.program_flat)
        questions = re.findall(r"^#### (\d+)\.", self.program, flags=re.MULTILINE)
        self.assertEqual(questions, [str(value) for value in range(1, 13)])

    def test_short_prompt_and_stop_boundary_are_explicit(self) -> None:
        self.assertIn(
            "Look into uncovered features in Pontifex, select and cover the next best",
            self.program,
        )
        self.assertIn("do not begin it unless", self.program)
        self.assertIn("Recommend the next candidate", self.program)


if __name__ == "__main__":
    unittest.main()

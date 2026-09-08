from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
TOOLKIT_SCAN = ROOT / "web" / "toolkit-scan.html"


class ToolkitBenchmarkContractTests(unittest.TestCase):
    def setUp(self):
        self.html = TOOLKIT_SCAN.read_text(encoding="utf-8")
        self.lower = self.html.lower()

    def test_comparison_is_evidence_bounded(self):
        self.assertIn("functional differentiation", self.lower)
        self.assertIn("does not replace", self.lower)
        self.assertIn("not a clinical effectiveness claim", self.lower)
        self.assertNotIn("scored maturity", self.lower)
        self.assertNotIn("this project improves", self.lower)

    def test_authoritative_comparators_are_present(self):
        for expected in (
            "agency for healthcare research and quality",
            "institute for patient- and family-centered care",
            "cms patient safety structural measure",
            "dartmouth mph",
            "rramani dervishi",
            "lewis b",
        ):
            self.assertIn(expected, self.lower)

    def test_unique_value_is_operational_not_outcome_claim(self):
        for expected in (
            "domain 5 traceability",
            "local population context",
            "closed-loop action",
            "evidence limitations",
            "competency traceability",
        ):
            self.assertIn(expected, self.lower)


if __name__ == "__main__":
    unittest.main()

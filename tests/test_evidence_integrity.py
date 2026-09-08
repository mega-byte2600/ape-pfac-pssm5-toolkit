import csv
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"


class EvidenceIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.analysis_html = (WEB / "applied-analysis.html").read_text(encoding="utf-8")
        self.bibliography_html = (WEB / "bibliography.html").read_text(encoding="utf-8")
        with (WEB / "upper-valley-local-analysis.csv").open(encoding="utf-8", newline="") as handle:
            self.rows = list(csv.DictReader(handle))

    def test_service_area_denominator_and_municipality_count(self):
        self.assertEqual(len(self.rows), 19)
        total = sum(int(row["2023 population"]) for row in self.rows)
        self.assertEqual(total, 72736)
        self.assertIn("72,736", self.analysis_html)

    def test_headline_shares_reconcile_to_source_csv(self):
        specs = [
            ("Above service-area poverty average (8%)", 35234, 48.4),
            ("Above service-area disability average (12%)", 43995, 60.5),
            ("Above service-area age 65+ average (22%)", 34875, 47.9),
        ]
        total = sum(int(row["2023 population"]) for row in self.rows)
        for flag, expected_population, expected_pct in specs:
            population = sum(int(row["2023 population"]) for row in self.rows if row[flag] == "Yes")
            self.assertEqual(population, expected_population)
            self.assertAlmostEqual(population / total * 100, expected_pct, places=1)
            self.assertIn(f"{expected_pct:.1f}%", self.analysis_html)

    def test_local_analysis_preserves_methodological_boundary(self):
        required = [
            "Planning analysis, not a risk score",
            "not validated cut points",
            "clinical risk estimates",
            "causal findings",
            "measures of PFAC effectiveness",
        ]
        for phrase in required:
            self.assertIn(phrase, self.analysis_html)

    def test_core_peer_reviewed_dois_are_locked(self):
        dois = [
            "10.1177/23743735251316995",
            "10.1177/23743735261415786",
            "10.1136/bmjoq-2025-004040",
            "10.1177/23743735251376068",
            "10.1007/s11606-018-4565-9",
            "10.1186/s12913-017-2630-4",
            "10.1136/bmjqs-2015-004315",
            "10.1093/intqhc/mzab059",
            "10.2196/43966",
            "10.1097/MLR.0000000000001088",
            "10.1136/bmjopen-2012-001570",
            "10.1377/hlthaff.2012.1133",
        ]
        for doi in dois:
            self.assertIn(doi, self.bibliography_html)

    def test_no_numeric_pfac_maturity_score_is_presented(self):
        benchmark = (WEB / "dh-benchmark.html").read_text(encoding="utf-8")
        lowered = benchmark.lower()
        self.assertNotIn("maturity score", lowered)
        self.assertNotRegex(lowered, r"pfac\s+(?:score|rating)\s*[:=]\s*\d")


if __name__ == "__main__":
    unittest.main()

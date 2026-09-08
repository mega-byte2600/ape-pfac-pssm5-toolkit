from __future__ import annotations

import csv
import unittest
from pathlib import Path

from pssm5_toolkit.server import application


def request(path: str):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(application({"PATH_INFO": path, "REQUEST_METHOD": "GET"}, start_response)).decode("utf-8")
    return captured["status"], captured["headers"], body


class InteractiveAnalysisTests(unittest.TestCase):
    def test_interactive_analysis_assets_are_served(self):
        status, headers, page = request("/applied-analysis.html")
        self.assertEqual(status, "200 OK")
        self.assertIn("text/html", headers["Content-Type"])
        for fragment in (
            'data-local-analysis',
            'id="analysis-metric"',
            'id="analysis-threshold"',
            'id="analysis-sort"',
            'id="analysis-search"',
            'id="analysis-chart"',
            'id="analysis-body"',
            'plotly-2.35.2.min.js',
            '/applied-analysis.js',
        ):
            self.assertIn(fragment, page)

        status, headers, script = request("/applied-analysis.js")
        self.assertEqual(status, "200 OK")
        self.assertIn("javascript", headers["Content-Type"])
        self.assertIn("/upper-valley-local-analysis.csv", script)
        self.assertIn("Poverty percent", script)
        self.assertIn("Disability percent", script)
        self.assertIn("Age 65+ percent", script)
        self.assertIn("Plotly.react", script)

    def test_analysis_is_visual_first_with_supporting_table_drilldown(self):
        _, _, page = request("/applied-analysis.html")
        lowered = page.lower()
        self.assertIn('id="analysis-chart"', lowered)
        self.assertIn("plotly", lowered)
        self.assertIn("view municipality data table", lowered)
        self.assertIn("<details", lowered)
        self.assertIn("<table", lowered)
        self.assertNotIn("<canvas", lowered)
        self.assertNotIn("<svg", lowered)

    def test_headline_results_recompute_from_same_csv_used_by_interaction(self):
        with Path("web/upper-valley-local-analysis.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

        total = sum(int(row["2023 population"]) for row in rows)
        self.assertEqual(len(rows), 19)
        self.assertEqual(total, 72736)

        expected = {
            "Above service-area poverty average (8%)": (6, 48.4),
            "Above service-area disability average (12%)": (10, 60.5),
            "Above service-area age 65+ average (22%)": (11, 47.9),
        }
        for field, (expected_towns, expected_share) in expected.items():
            selected = [row for row in rows if row[field] == "Yes"]
            selected_population = sum(int(row["2023 population"]) for row in selected)
            self.assertEqual(len(selected), expected_towns, field)
            self.assertAlmostEqual(selected_population / total * 100, expected_share, places=1, msg=field)

    def test_public_analysis_has_no_model_prompt_or_tool_spillover(self):
        _, _, page = request("/applied-analysis.html")
        _, _, script = request("/applied-analysis.js")
        public_text = f"{page}\n{script}".casefold()
        forbidden = (
            "system prompt",
            "developer message",
            "tool call",
            "chain of thought",
            "chatgpt",
            "openai",
            "anthropic",
            "claude",
            "codex",
            "large language model",
            "prompt spillover",
            "internal instructions",
        )
        for fragment in forbidden:
            self.assertNotIn(fragment, public_text, fragment)

    def test_analysis_preserves_claim_boundaries(self):
        _, _, page = request("/applied-analysis.html")
        self.assertIn("Planning analysis, not a risk score", page)
        self.assertIn("not a claim that Dartmouth Health has adopted", page)
        self.assertIn("descriptive approximations", page)
        self.assertNotIn("Dartmouth Health implemented", page)
        self.assertNotIn("improved patient outcomes", page.lower())


if __name__ == "__main__":
    unittest.main()

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


class ExecutiveValueContractTests(unittest.TestCase):
    def test_executive_launch_is_real_public_page(self):
        status, headers, body = request("/executive-launch.html")
        self.assertEqual(status, "200 OK")
        self.assertIn("text/html", headers["Content-Type"])
        for fragment in (
            "Executive Launch Brief",
            "Six decisions to make before calling a PFAC operational.",
            "90-day operating plan",
            "Track contribution before claiming impact.",
            "A PFAC should create inspectable decisions, not just meetings.",
            "/pfac-90-day-launch-plan.csv",
        ):
            self.assertIn(fragment, body)

    def test_homepage_routes_leaders_to_executive_brief_without_losing_prior_contracts(self):
        status, _, body = request("/")
        self.assertEqual(status, "200 OK")
        for fragment in (
            "Turn patient voice into better care.",
            "Evidence-Based PFAC Summary",
            "DH benchmark",
            "Applied Analysis",
            "APE deliverables",
            "/executive-launch.html",
            "Start with the executive brief",
        ):
            self.assertIn(fragment, body)

    def test_90_day_plan_is_downloadable_and_operational(self):
        status, headers, body = request("/pfac-90-day-launch-plan.csv")
        self.assertEqual(status, "200 OK")
        self.assertIn("text/csv", headers["Content-Type"])
        for fragment in (
            "Days 0-30",
            "Days 31-60",
            "Days 61-90",
            "Primary owner",
            "Decision or output",
            "Validation note",
            "Do not attribute downstream outcomes to PFAC activity without appropriate evaluation",
        ):
            self.assertIn(fragment, body)

        with Path("web/pfac-90-day-launch-plan.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 7)
        self.assertEqual({row["Status"] for row in rows}, {"Not started"})
        self.assertTrue(all(row["Primary owner"] == "TBD" for row in rows))

    def test_executive_layer_does_not_overclaim_or_expand_scope(self):
        _, _, body = request("/executive-launch.html")
        forbidden = (
            "proves PFAC effectiveness",
            "PFAC improves patient outcomes",
            "Dartmouth Health has adopted",
            "Dartmouth Health implemented",
            "completed organizational change",
            "third deliverable",
            "fourth deliverable",
            "coauthor",
            "manuscript",
            "publication",
        )
        for fragment in forbidden:
            self.assertNotIn(fragment.casefold(), body.casefold())
        self.assertIn("Deliverable 2", body)
        self.assertIn("without claiming outcomes the evidence does not establish", body)

    def test_new_page_has_no_internal_build_or_model_spillover(self):
        _, _, body = request("/executive-launch.html")
        forbidden = (
            "GitHub",
            "pull request",
            "regression",
            "system prompt",
            "developer message",
            "tool call",
            "chain of thought",
            "ChatGPT",
            "OpenAI",
            "Claude",
            "Codex",
            "large language model",
            "coming soon",
            "placeholder",
        )
        for fragment in forbidden:
            self.assertNotIn(fragment.casefold(), body.casefold())


if __name__ == "__main__":
    unittest.main()

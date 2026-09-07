from __future__ import annotations

import unittest
from pathlib import Path

from pssm5_toolkit.hai_dashboard import build_hai_dashboard
from pssm5_toolkit.open_resources import build_open_resources
from pssm5_toolkit.server import application
from pssm5_toolkit.toolkit import build_toolkit


def request(path: str):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(application({"PATH_INFO": path, "REQUEST_METHOD": "GET"}, start_response)).decode("utf-8")
    return captured["status"], captured["headers"], body


def public_html_paths() -> list[str]:
    web_dir = Path("web")
    if not web_dir.is_dir():
        return ["/"]
    paths = ["/"]
    paths.extend(f"/{item.name}" for item in sorted(web_dir.glob("*.html")) if item.name != "index.html")
    return paths


class WebContractTests(unittest.TestCase):
    def assert_page_contains(self, path: str, expected: list[str]) -> str:
        status, headers, body = request(path)
        self.assertEqual(status, "200 OK", path)
        self.assertIn("text/html", headers["Content-Type"], path)
        for fragment in expected:
            self.assertIn(fragment, body, f"{path} missing {fragment!r}")
        return body

    def test_core_public_pages_serve_expected_content(self):
        required_pages = {
            "/": [
                "Turn patient voice into better care.",
                "Evidence-Based PFAC Summary",
                "DH benchmark",
                "APE deliverables",
                "Collaboration",
            ],
            "/evidence.html": [
                "Evidence Launch Page",
                "Evidence-Based PFAC Summary",
                "PubMed search protocol",
                "Evidence matrix",
                "AMA 11 source layer",
            ],
            "/evidence-summary.html": [
                "Evidence-Based PFAC Summary",
                "My APE/ILE project translates",
                "mutually beneficial applied work",
                "culminating high-quality written product",
            ],
            "/research-plan.html": [
                "Inclusion criteria",
                "Exclusion criteria",
                "Search lane 1",
                "Search lane 2",
                "Search lane 3",
                "Screening workflow",
            ],
            "/surveillance-method.html": [
                "Research Surveillance Method",
                "PubMed/MyNCBI",
                "Outlook folders",
                "Zotero collections",
                "Weekly review",
                "Example SQL",
            ],
            "/bibliography.html": [
                "AMA 11",
                "Core research evidence",
                "Implementation toolkits and benchmark resources",
                "Open data and public resource sources",
                "Story and acknowledgement resources",
            ],
            "/hai-alert.html": [
                "HAI",
                "MRSA",
                "PFAC",
                "infection",
                "escalation",
            ],
            "/story.html": [
                "Rosie Bartel",
                "lived-experience anchor",
            ],
            "/about.html": [
                "Michael Bolton",
                "LinkedIn profile",
                "mailto:michael.bolton.ph@dartmouth.edu",
                "Notion workspace",
                "Research surveillance how-to",
            ],
            "/collaboration.html": [
                "Collaboration Layer",
                "Open Notion workspace",
                "Source Intake",
                "Evidence Review",
                "Toolkit Backlog",
            ],
            "/deliverables.html": [
                "Applied Practice Experience Deliverables",
                "Environmental scan",
                "PFAC/PSSM 5 leadership toolkit",
                "Selected competencies",
            ],
            "/mvp-one.html": [
                "Reviewer Readiness",
                "What reviewers can inspect now",
                "Surveillance how-to",
            ],
        }

        for path, expected in required_pages.items():
            with self.subTest(path=path):
                self.assert_page_contains(path, expected)

    def test_every_public_html_page_loads_without_fallback(self):
        for path in public_html_paths():
            with self.subTest(path=path):
                status, headers, body = request(path)
                self.assertEqual(status, "200 OK")
                self.assertIn("text/html", headers["Content-Type"])
                if path != "/":
                    self.assertNotIn("Turn patient voice into better care.", body, f"{path} appears to be falling back to homepage")

    def test_public_pages_do_not_expose_prompt_or_admin_language(self):
        forbidden_fragments = [
            "GitHub",
            "Private</span>",
            "Private repository",
            "repository stays private",
            "private project administration",
            "Code, deployment, drafts, and project administration",
            "Acceptance criteria",
            "What MVP 1 must do well",
            "MVP 1 reviewer portal",
            "Reviewer portal acceptance criteria",
            "No prompt spillover",
            "prompt spillover",
            "internal instructions",
            "code repository",
            "source control",
            "The Agreement defines",
            "CI/CD",
            "regression checks",
        ]

        for path in public_html_paths():
            with self.subTest(path=path):
                status, _, body = request(path)
                self.assertEqual(status, "200 OK")
                for fragment in forbidden_fragments:
                    self.assertNotIn(fragment, body, f"{path} exposes {fragment!r}")

    def test_public_pages_do_not_render_markdown_artifacts(self):
        forbidden_markdown = ["**", "```", "### ", "## "]
        for path in public_html_paths():
            with self.subTest(path=path):
                status, _, body = request(path)
                self.assertEqual(status, "200 OK")
                for fragment in forbidden_markdown:
                    self.assertNotIn(fragment, body, f"{path} contains raw markdown artifact {fragment!r}")

    def test_reviewer_flow_stays_on_public_pages(self):
        body = self.assert_page_contains("/", ["/evidence-summary.html", "/dh-benchmark.html", "/deliverables.html"])
        self.assertIn('/research-plan.html', body)
        self.assertIn('/surveillance-method.html', body)
        self.assertIn('/collaboration.html', body)
        self.assertNotIn("github.com", body.lower())

    def test_story_and_evidence_are_separated(self):
        research_plan = self.assert_page_contains("/research-plan.html", ["Stories are not research evidence"])
        bibliography = self.assert_page_contains("/bibliography.html", ["Rosie Bartel", "not treated as peer-reviewed evidence"])
        self.assertIn("Patient stories can anchor urgency and meaning", research_plan)
        self.assertIn("Core research evidence", bibliography)

    def test_hai_dashboard_endpoint_returns_chart_data(self):
        status, _, body = request("/api/hai-dashboard")
        self.assertEqual(status, "200 OK")
        self.assertIn('"measures"', body)
        self.assertIn('"executive_actions"', body)

    def test_hai_dashboard_exposes_executive_actions(self):
        dashboard = build_hai_dashboard()
        self.assertEqual(dashboard["status"], "ok")
        self.assertGreaterEqual(len(dashboard["measures"]), 7)
        self.assertGreaterEqual(len(dashboard["executive_actions"]), 4)
        self.assertTrue(any(item["measure"] == "SSI hysterectomy" for item in dashboard["measures"]))

    def test_payloads_have_content_for_rendered_sections(self):
        toolkit = build_toolkit()
        resources = build_open_resources()
        self.assertGreaterEqual(len(toolkit["peer_models"]), 5)
        self.assertGreaterEqual(len(resources), 5)


if __name__ == "__main__":
    unittest.main()

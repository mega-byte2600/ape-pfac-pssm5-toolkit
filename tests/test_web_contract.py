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
            "/": ["Turn patient voice into better care.", "Evidence-Based PFAC Summary", "DH benchmark", "APE deliverables", "Collaboration"],
            "/evidence.html": ["Evidence Launch Page", "Evidence-Based PFAC Summary", "PubMed search protocol", "Evidence matrix", "AMA 11 source layer"],
            "/evidence-summary.html": [
                "Evidence-Based PFAC Summary",
                "CMS Patient Safety Structural Measure",
                "Domain 5: Patient and Family Engagement",
                "evidence base remains limited",
                "203 respondents",
            ],
            "/dh-benchmark.html": [
                "Benchmark assessment framework",
                "not a scored evaluation",
                "Evidence-backed preliminary findings",
                "Evidence needed before scoring",
                "Not yet scored",
                "Reusable evidence table",
            ],
            "/research-plan.html": [
                "non-research APE",
                "confirmation bias",
                "Search lane 1",
                "Search lane 2",
                "Search lane 3",
                "Screening workflow",
                "conflicting, null, or negative findings",
            ],
            "/surveillance-method.html": ["Research Surveillance Method", "PubMed/MyNCBI", "Outlook folders", "Zotero collections", "Weekly review", "Example SQL"],
            "/bibliography.html": ["AMA 11", "Core research evidence", "Implementation toolkits and benchmark resources", "Open data and public resource sources", "Story and acknowledgement resources"],
            "/hai-alert.html": ["HAI", "MRSA", "PFAC", "infection", "escalation"],
            "/story.html": ["Rosie Bartel", "lived-experience anchor", "does not imply endorsement", "not representative evidence"],
            "/about.html": ["Michael Bolton", "LinkedIn profile", "mailto:michael.bolton.ph@dartmouth.edu", "Notion workspace", "Research surveillance how-to"],
            "/collaboration.html": ["Collaboration Layer", "Open Notion workspace", "Source Intake", "Evidence Review", "Toolkit Backlog"],
            "/deliverables.html": [
                "Two practical deliverables",
                "Environmental scan and annotated bibliography",
                "Deliverable 2 tools",
                "CEPH 4",
                "CEPH 7",
                "Dartmouth Program-Specific Competency 4",
            ],
            "/toolkit-tools.html": [
                "Tools leaders can use immediately.",
                "PFAC current-state assessment",
                "Closed-loop action tracker",
                "Representation and access check",
                "Measurement plan",
                "Domain 5 traceability",
            ],
            "/mvp-one.html": ["Reviewer Readiness", "What reviewers can inspect now", "Surveillance how-to"],
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

    def test_public_pages_do_not_expose_prompt_admin_or_scope_spillover(self):
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
            "APE/ILE",
            "Integrated Learning Experience",
            "industry-grade",
            "Chick-fil-A",
            "McDonald’s thesis",
            "Patients over payers",
        ]
        for path in public_html_paths():
            with self.subTest(path=path):
                status, _, body = request(path)
                self.assertEqual(status, "200 OK")
                for fragment in forbidden_fragments:
                    self.assertNotIn(fragment.lower(), body.lower(), f"{path} exposes {fragment!r}")

    def test_evidence_matrix_carries_limitations_and_current_evidence(self):
        body = self.assert_page_contains(
            "/evidence-matrix.html",
            [
                "Evidence strength / limitation",
                "Anticipated patient benefit",
                "Lewis et al, 2025",
                "Lewis et al, 2026",
                "Rramani Dervishi et al, 2026",
                "Leia et al, 2025",
                "cross-sectional associations do not establish causality",
            ],
        )
        self.assertNotIn("Patient advisors can influence health care outcomes when linked to action and measurement", body)
        self.assertNotIn("Improves communication, discharge readiness", body)

    def test_toolkit_download_templates_are_real_static_assets(self):
        templates = {
            "/pfac-current-state-assessment.csv": "Executive sponsorship",
            "/pfac-action-tracker.csv": "Leadership disposition",
            "/pfac-representation-access.csv": "Participation barrier",
            "/pfac-measurement-plan.csv": "Interpretation caution",
            "/pssm-domain5-traceability.csv": "Validation source",
        }
        for path, fragment in templates.items():
            with self.subTest(path=path):
                status, headers, body = request(path)
                self.assertEqual(status, "200 OK")
                self.assertIn("text/csv", headers["Content-Type"])
                self.assertIn(fragment, body)
                self.assertNotIn("Turn patient voice into better care.", body)

    def test_dh_benchmark_discloses_evidence_state(self):
        body = self.assert_page_contains(
            "/dh-benchmark.html",
            [
                "The framework is real as a structured assessment method.",
                "It is not yet real as a scored benchmark",
                "Scoring should occur only after reviewing public materials",
                "Publicly supported",
                "Not yet validated",
                "Insufficient evidence",
                "Preliminary finding",
                'id="evidence-status"',
                'class="evidence-status-table"',
                'id="evidence-table"',
                'class="benchmark-evidence-table"',
            ],
        )
        self.assertNotIn("Benchmark maturity model", body)
        self.assertNotIn("View maturity model", body)
        self.assertNotIn("maturity score", body.lower())
        self.assertNotIn("completed scorecard", body.lower())
        self.assertNotIn("completed evaluation", body.lower())

    def test_dh_benchmark_uses_plan_evidence_fields(self):
        body = self.assert_page_contains(
            "/dh-benchmark.html",
            ["Domain", "Evidence item", "Evidence type", "Source title", "Source URL", "Date reviewed", "Current finding", "Limitation", "Confidence", "Gap", "Recommended action", "Public safe", "Include on site"],
        )
        self.assertIn('data-evidence-status="publicly-supported"', body)
        self.assertIn('data-evidence-status="not-yet-validated"', body)
        self.assertIn('data-evidence-status="insufficient-evidence"', body)
        self.assertIn('data-evidence-status="preliminary-finding"', body)

    def test_dh_benchmark_keeps_public_and_unvalidated_findings_separate(self):
        body = self.assert_page_contains("/dh-benchmark.html", ["evidence-status-table"])
        rows = [segment.split("</tr>", 1)[0] for segment in body.split("<tr") if "data-evidence-status" in segment]
        self.assertGreaterEqual(len(rows), 4)
        for row in rows:
            statuses = [status for status in ("publicly-supported", "not-yet-validated", "insufficient-evidence", "preliminary-finding") if f'data-evidence-status="{status}"' in row]
            self.assertEqual(len(statuses), 1, row)

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
        research_plan = self.assert_page_contains("/research-plan.html", ["not an inclusion requirement"])
        bibliography = self.assert_page_contains("/bibliography.html", ["Rosie Bartel", "not treated as peer-reviewed evidence"])
        story = self.assert_page_contains("/story.html", ["not research evidence", "not representative evidence"])
        self.assertIn("Core research evidence", bibliography)
        self.assertIn("does not imply endorsement", story)
        self.assertIn("confirmation bias", research_plan)

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

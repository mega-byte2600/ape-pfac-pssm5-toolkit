from __future__ import annotations

import csv
import re
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
            "/": ["Turn patient voice into accountable action.", "Evidence-Based PFAC Summary", "DH benchmark", "Applied Analysis", "APE deliverables", "/mvp-one.html"],
            "/evidence.html": ["Evidence Launch Page", "Evidence-Based PFAC Summary", "PubMed search protocol", "Evidence matrix", "AMA 11 source layer", "/toolkit-scan.html"],
            "/evidence-summary.html": ["Evidence-Based PFAC Summary", "CMS Patient Safety Structural Measure", "Domain 5: Patient and Family Engagement", "evidence base remains limited", "203 respondents"],
            "/dh-benchmark.html": ["Benchmark assessment framework", "not a scored evaluation", "Evidence-backed preliminary findings", "Evidence needed before scoring", "Not yet scored", "Reusable evidence table"],
            "/applied-analysis.html": ["Original local analysis", "72,736", "48.4%", "60.5%", "47.9%", "Explore the local data", "Implementation demonstration", "Host validation required"],
            "/research-plan.html": ["non-research APE", "confirmation bias", "Search lane 1", "Search lane 2", "Search lane 3", "Screening workflow", "Conflicting, null, or negative findings"],
            "/surveillance-method.html": ["Research Surveillance Method", "PubMed/MyNCBI", "Outlook folders", "Zotero collections", "Weekly review", "Example SQL"],
            "/bibliography.html": ["AMA 11", "Core research evidence", "Federal and implementation guidance", "Open data and public resources", "Story and acknowledgement resources", "Validation note"],
            "/hai-alert.html": ["HAI", "MRSA", "PFAC", "infection", "escalation", "Evidence synthesis summary", "Interactive HAI dashboard"],
            "/story.html": ["Rosie Bartel", "lived-experience anchor", "does not imply endorsement", "not representative evidence"],
            "/about.html": ["Michael Bolton", "LinkedIn profile", "mailto:michael.bolton.ph@dartmouth.edu", "Notion workspace", "Research surveillance how-to"],
            "/collaboration.html": ["Collaboration Layer", "Open Notion workspace", "Source Intake", "Evidence Review", "Toolkit Backlog", "Do not submit"],
            "/deliverables.html": ["Two practical deliverables", "Environmental scan and annotated bibliography", "Deliverable 2 tools", "CEPH 4", "CEPH 7", "Dartmouth Program-Specific Competency 4", "Demonstrated."],
            "/toolkit-tools.html": ["Tools leaders can use immediately.", "PFAC current-state assessment", "Closed-loop action tracker", "Representation and access check", "Measurement plan", "Domain 5 traceability"],
            "/mvp-one.html": ["Reviewer Guide", "Recommended sequence", "local analysis", "Leadership tools"],
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
                    self.assertNotIn("Turn patient voice into accountable action.", body, f"{path} appears to be falling back to homepage")

    def test_public_pages_have_no_internal_or_generation_spillover(self):
        forbidden_fragments = [
            "GitHub",
            "Private repository",
            "repository stays private",
            "Code, deployment, drafts, and project administration",
            "Acceptance criteria",
            "MVP 1",
            "prompt spillover",
            "internal instructions",
            "code repository",
            "source control",
            "CI/CD",
            "regression checks",
            "APE/ILE",
            "Integrated Learning Experience",
            "industry-grade",
            "Chick-fil-A",
            "McDonald’s thesis",
            "Patients over payers",
            "system prompt",
            "developer message",
            "tool call",
            "chain of thought",
            "ChatGPT",
            "OpenAI",
            "Anthropic",
            "Claude",
            "Codex",
            "large language model",
        ]
        for path in public_html_paths():
            with self.subTest(path=path):
                status, _, body = request(path)
                self.assertEqual(status, "200 OK")
                for fragment in forbidden_fragments:
                    self.assertNotIn(fragment.casefold(), body.casefold(), f"{path} exposes {fragment!r}")

    def test_public_source_assets_have_no_generation_or_build_spillover(self):
        public_assets = list(Path("web").glob("*.html")) + list(Path("web").glob("*.js")) + list(Path("web").glob("*.css")) + list(Path("web").glob("*.csv"))
        forbidden_fragments = [
            "ChatGPT",
            "OpenAI",
            "Anthropic",
            "Claude",
            "Codex",
            r"\bLLM\b",
            "large language model",
            "AI generated",
            "system prompt",
            "developer message",
            "tool call",
            "chain of thought",
            "prompt spillover",
            "internal instructions",
            "placeholder",
            "TODO",
            "FIXME",
            "debug",
            "test data",
        ]
        for asset in public_assets:
            text = asset.read_text(encoding="utf-8")
            with self.subTest(asset=str(asset)):
                for fragment in forbidden_fragments:
                    if fragment.startswith(r"\b"):
                        self.assertIsNone(re.search(fragment, text, flags=re.IGNORECASE), f"{asset} exposes {fragment!r}")
                    else:
                        self.assertNotIn(fragment.casefold(), text.casefold(), f"{asset} exposes {fragment!r}")

    def test_approved_pages_are_reachable_from_public_reviewer_path(self):
        from html.parser import HTMLParser
        from urllib.parse import urlparse

        class LinkParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.links = []

            def handle_starttag(self, tag, attrs):
                if tag != "a":
                    return
                for key, value in attrs:
                    if key == "href" and value:
                        self.links.append(value)

        web_dir = Path("web")
        route_to_file = {"/": web_dir / "index.html"}
        route_to_file.update({f"/{item.name}": item for item in sorted(web_dir.glob("*.html")) if item.name != "index.html"})
        graph = {}
        for route, path in route_to_file.items():
            parser = LinkParser()
            parser.feed(path.read_text(encoding="utf-8"))
            links = []
            for href in parser.links:
                parsed = urlparse(href)
                if parsed.scheme or href.startswith("mailto:") or href.startswith("#"):
                    continue
                if parsed.path in route_to_file:
                    links.append(parsed.path)
            graph[route] = links

        reachable = {"/"}
        stack = ["/"]
        while stack:
            route = stack.pop()
            for next_route in graph[route]:
                if next_route not in reachable:
                    reachable.add(next_route)
                    stack.append(next_route)

        required_routes = {
            "/story.html",
            "/about.html",
            "/hai-alert.html",
            "/applied-analysis.html",
            "/evidence-summary.html",
            "/evidence-matrix.html",
            "/bibliography.html",
            "/dh-benchmark.html",
            "/toolkit-tools.html",
            "/research-plan.html",
            "/deliverables.html",
            "/executive-launch.html",
            "/mvp-one.html",
            "/toolkit-scan.html",
            "/charter.html",
        }
        self.assertTrue(required_routes <= reachable, sorted(required_routes - reachable))

    def test_public_pages_have_no_placeholder_or_build_state_language(self):
        forbidden = [
            "Reserved for the synthesis text",
            "Drop the final synthesis here",
            "Loading HAI dashboard",
            "Reviewer Readiness",
            "public release",
            "acceptance criteria",
            "coming soon",
        ]
        for path in public_html_paths():
            with self.subTest(path=path):
                _, _, body = request(path)
                for fragment in forbidden:
                    self.assertNotIn(fragment.casefold(), body.casefold(), f"{path} contains unfinished language {fragment!r}")

    def test_evidence_matrix_carries_limitations_and_current_evidence(self):
        body = self.assert_page_contains(
            "/evidence-matrix.html",
            ["Evidence strength / limitation", "Anticipated patient benefit", "Lewis et al, 2025", "Lewis et al, 2026", "Rramani Dervishi et al, 2026", "Leia et al, 2025", "cross-sectional associations do not establish causality"],
        )
        self.assertNotIn("Patient advisors can influence health care outcomes when linked to action and measurement", body)
        self.assertNotIn("Improves communication, discharge readiness", body)

    def test_bibliography_contains_current_matrix_sources_and_validation_note(self):
        body = self.assert_page_contains(
            "/bibliography.html",
            ["Lewis B, Cochran C, Marquez E", "Lewis B, Cochran C, Shoemaker S", "Rramani Dervishi Q", "Leia MP", "Validation note"],
        )
        self.assertIn("not treated as peer-reviewed evidence", body)

    def test_hai_page_keeps_approved_interactive_dashboard_and_evidence_detail(self):
        body = self.assert_page_contains(
            "/hai-alert.html",
            [
                "Interactive HAI dashboard",
                'id="hai-trend-chart"',
                'id="hai-baseline-chart"',
                'id="hai-action-grid"',
                "plotly-2.35.2.min.js",
                "/app.js",
                "Evidence signal",
                "View evidence detail table",
                "Evidence synthesis summary",
                "Infection prevention is also a communication and escalation problem.",
                "What PFAC should ask locally",
                "Leadership follow-through",
            ],
        )
        lowered = body.casefold()
        self.assertNotIn("loading hai dashboard", lowered)
        self.assertNotIn("reserved for the synthesis text", lowered)
        self.assertNotIn("drop the final synthesis here", lowered)
        self.assertNotIn("<canvas", lowered)

    def test_toolkit_download_templates_are_real_static_assets(self):
        templates = {
            "/pfac-current-state-assessment.csv": "Executive sponsorship",
            "/pfac-action-tracker.csv": "Leadership disposition",
            "/pfac-representation-access.csv": "Participation barrier",
            "/pfac-measurement-plan.csv": "Interpretation caution",
            "/pssm-domain5-traceability.csv": "Validation source",
            "/upper-valley-local-analysis.csv": "Above service-area poverty average",
            "/upper-valley-access-implementation.csv": "Implemented in APE case packet",
        }
        for path, fragment in templates.items():
            with self.subTest(path=path):
                status, headers, body = request(path)
                self.assertEqual(status, "200 OK")
                self.assertIn("text/csv", headers["Content-Type"])
                self.assertIn(fragment, body)
                self.assertNotIn("Turn patient voice into better care.", body)

    def test_local_analysis_recomputes_from_source_table(self):
        with Path("web/upper-valley-local-analysis.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))

        self.assertEqual(len(rows), 19)
        total = sum(int(row["2023 population"]) for row in rows)
        self.assertEqual(total, 72736)

        calculations = {
            "Above service-area poverty average (8%)": 48.4,
            "Above service-area disability average (12%)": 60.5,
            "Above service-area age 65+ average (22%)": 47.9,
        }
        for field, expected in calculations.items():
            population = sum(int(row["2023 population"]) for row in rows if row[field] == "Yes")
            self.assertAlmostEqual(population / total * 100, expected, places=1, msg=field)

    def test_applied_analysis_is_local_visual_interactive_and_not_outcome_claiming(self):
        body = self.assert_page_contains(
            "/applied-analysis.html",
            [
                "Planning analysis, not a risk score",
                "42%",
                "72%",
                "59%",
                "55%",
                "not a claim that Dartmouth Health has adopted",
                "CEPH 4",
                "CEPH 7",
                "descriptive approximations",
                'id="analysis-metric"',
                'id="analysis-threshold"',
                'id="analysis-sort"',
                'id="analysis-search"',
                'id="analysis-chart"',
                "plotly-2.35.2.min.js",
                "View municipality data table",
                "View implementation detail table",
                "/applied-analysis.js",
            ],
        )
        self.assertNotIn("Dartmouth Health implemented", body)
        self.assertNotIn("improved patient outcomes", body.casefold())
        self.assertNotIn("<canvas", body.casefold())
        self.assertNotIn("<svg", body.casefold())

    def test_applied_analysis_script_is_served_and_renders_plotly(self):
        status, headers, body = request("/applied-analysis.js")
        self.assertEqual(status, "200 OK")
        self.assertIn("javascript", headers["Content-Type"])
        self.assertIn("/upper-valley-local-analysis.csv", body)
        self.assertIn("Poverty percent", body)
        self.assertIn("Disability percent", body)
        self.assertIn("Age 65+ percent", body)
        self.assertIn("Plotly.react", body)
        self.assertIn("analysis-chart", body)
        self.assertIn("Service-area average", body)

    def test_applied_implementation_case_is_populated(self):
        status, headers, body = request("/upper-valley-access-implementation.csv")
        self.assertEqual(status, "200 OK")
        self.assertIn("text/csv", headers["Content-Type"])
        self.assertIn("Access and navigation", body)
        self.assertIn("Host validation required", body)
        self.assertIn("Implemented in APE case packet", body)
        self.assertIn("Domain 5 alignment", body)

    def test_dh_benchmark_discloses_evidence_state(self):
        body = self.assert_page_contains(
            "/dh-benchmark.html",
            ["The framework is real as a structured assessment method.", "It is not yet real as a scored benchmark", "Scoring should occur only after reviewing public materials", "Publicly supported", "Not yet validated", "Insufficient evidence", "Preliminary finding", 'id="evidence-status"', 'class="evidence-status-table"', 'id="evidence-table"', 'class="benchmark-evidence-table"'],
        )
        self.assertNotIn("Benchmark maturity model", body)
        self.assertNotIn("View maturity model", body)
        self.assertNotIn("maturity score", body.casefold())
        self.assertNotIn("completed scorecard", body.casefold())
        self.assertNotIn("completed evaluation", body.casefold())

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
        for path in public_html_paths():
            with self.subTest(path=path):
                status, _, body = request(path)
                self.assertEqual(status, "200 OK")
                for fragment in ("**", "```", "### ", "## "):
                    self.assertNotIn(fragment, body, f"{path} contains raw markdown artifact {fragment!r}")

    def test_reviewer_flow_stays_on_public_pages(self):
        body = self.assert_page_contains("/", ["/evidence-summary.html", "/dh-benchmark.html", "/applied-analysis.html", "/deliverables.html"])
        self.assertIn('/research-plan.html', body)
        self.assertIn('/toolkit-tools.html', body)
        self.assertNotIn("github.com", body.casefold())

    def test_story_and_evidence_are_separated(self):
        research_plan = self.assert_page_contains("/research-plan.html", ["not an inclusion requirement"])
        bibliography = self.assert_page_contains("/bibliography.html", ["Rosie Bartel", "not treated as peer-reviewed evidence"])
        story = self.assert_page_contains("/story.html", ["not research evidence", "not representative evidence"])
        self.assertIn("Core research evidence", bibliography)
        self.assertIn("does not imply endorsement", story)
        self.assertIn("confirmation bias", research_plan)

    def test_hai_dashboard_endpoint_still_returns_data_for_reuse(self):
        status, _, body = request("/api/hai-dashboard")
        self.assertEqual(status, "200 OK")
        self.assertIn('"measures"', body)
        self.assertIn('"executive_actions"', body)

    def test_hai_dashboard_payload_remains_valid(self):
        dashboard = build_hai_dashboard()
        self.assertEqual(dashboard["status"], "ok")
        self.assertGreaterEqual(len(dashboard["measures"]), 7)
        self.assertGreaterEqual(len(dashboard["executive_actions"]), 4)
        self.assertTrue(any(item["measure"] == "SSI hysterectomy" for item in dashboard["measures"]))

    def test_approved_visual_contract_cannot_be_silently_removed(self):
        hai = self.assert_page_contains("/hai-alert.html", ["plotly", "/app.js", "hai-trend-chart", "hai-baseline-chart"])
        analysis = self.assert_page_contains("/applied-analysis.html", ["plotly", "analysis-chart", "View municipality data table"])
        script_status, _, script = request("/applied-analysis.js")
        self.assertEqual(script_status, "200 OK")
        self.assertIn("Plotly.react", script)
        self.assertIn("View evidence detail table", hai)
        self.assertIn("View implementation detail table", analysis)

    def test_payloads_have_content_for_rendered_sections(self):
        toolkit = build_toolkit()
        resources = build_open_resources()
        self.assertGreaterEqual(len(toolkit["peer_models"]), 5)
        self.assertGreaterEqual(len(resources), 5)


if __name__ == "__main__":
    unittest.main()

from __future__ import annotations

import csv
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

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
            "/": ["Turn patient voice into accountable action through", "Evidence-Based PFAC Summary", "DH benchmark", "Applied Analysis", "APE deliverables"],
            "/evidence.html": ["Evidence launch page", "Evidence-Based PFAC Summary", "Evidence matrix", "AMA 11 source layer", "/toolkit-scan.html"],
            "/evidence-summary.html": ["Evidence-Based PFAC Summary", "CMS Patient Safety Structural Measure", "Domain 5: Patient and Family Engagement", "evidence base remains limited", "203 respondents"],
            "/dh-benchmark.html": ["Benchmark assessment framework", "not a scored evaluation", "Evidence-backed preliminary findings", "Evidence needed before scoring", "Not yet scored", "Reusable evidence table"],
            "/applied-analysis.html": ["Original local analysis", "72,736", "48.4%", "60.5%", "47.9%", "Explore the local data", "Implementation demonstration", "Host validation required"],
            "/bibliography.html": ["AMA 11", "Core research evidence", "Federal and implementation guidance", "Open data and public resources", "Story and acknowledgement resources"],
            "/hai-alert.html": ["HAI", "MRSA", "PFAC", "Evidence synthesis summary", "Interactive HAI dashboard"],
            "/story.html": ["Rosie Bartel", "lived-experience anchor", "does not imply endorsement", "not representative evidence"],
            "/about.html": ["Michael Bolton", "Silicon Valley engineer", "LinkedIn profile", "Notion workspace"],
            "/deliverables.html": ["Two practical deliverables", "Environmental scan and annotated bibliography", "Deliverable 2 tools", "CEPH 4", "CEPH 7", "Dartmouth Program-Specific Competency 4", "Demonstrated."],
            "/toolkit-tools.html": ["Tools leaders can use immediately.", "PFAC current-state assessment", "Closed-loop action tracker", "Representation and access check", "Measurement plan", "Domain 5 traceability"],
        }
        for path, expected in required_pages.items():
            with self.subTest(path=path):
                self.assert_page_contains(path, expected)

    def test_reviewer_guide_is_retired_and_blocked(self):
        self.assertFalse(Path("web/mvp-one.html").exists())
        self.assertFalse(Path("web/review-flow.js").exists())
        for retired in ("/mvp-one.html", "/review-flow.js"):
            status, _, body = request(retired)
            self.assertEqual(status, "404 Not Found")
            self.assertIn("not_found", body)
        forbidden = ("Reviewer Guide", "/mvp-one.html", "review-flow.js", "Reviewer flow")
        for page in sorted(Path("web").glob("*.html")):
            text = page.read_text(encoding="utf-8")
            for fragment in forbidden:
                self.assertNotIn(fragment.casefold(), text.casefold(), f"{page} reintroduces retired reviewer-guide content {fragment!r}")

    def test_every_public_html_page_loads_without_homepage_fallback(self):
        for path in public_html_paths():
            with self.subTest(path=path):
                status, headers, body = request(path)
                self.assertEqual(status, "200 OK")
                self.assertIn("text/html", headers["Content-Type"])
                if path != "/":
                    self.assertNotIn("Turn patient voice into accountable action.", body, f"{path} appears to fall back to homepage")

    def test_internal_review_method_and_validation_spillover_are_not_public(self):
        self.assertFalse(Path("web/research-plan.html").exists())
        forbidden = (
            "/research-plan.html",
            "Validation note:",
            "prompt spillover",
            "system prompt",
            "developer message",
            "chain of thought",
        )
        for page in sorted(Path("web").glob("*.html")):
            text = page.read_text(encoding="utf-8").casefold()
            for fragment in forbidden:
                self.assertNotIn(fragment.casefold(), text, f"{page} exposes internal content {fragment!r}")

    def test_public_pages_have_no_known_unfinished_or_internal_release_copy(self):
        forbidden = (
            "Reserved for the synthesis text",
            "Drop the final synthesis here",
            "Loading HAI dashboard",
            "Reviewer Readiness",
            "acceptance criteria",
            "coming soon",
            "APE/ILE",
            "Integrated Learning Experience",
            "Patients over payers",
            "Chick-fil-A",
            "McDonald’s thesis",
        )
        for path in public_html_paths():
            with self.subTest(path=path):
                status, _, body = request(path)
                self.assertEqual(status, "200 OK")
                folded = body.casefold()
                for fragment in forbidden:
                    self.assertNotIn(fragment.casefold(), folded, f"{path} exposes {fragment!r}")

    def test_required_public_routes_remain_reachable(self):
        class LinkParser(HTMLParser):
            def __init__(self):
                super().__init__()
                self.links: list[str] = []

            def handle_starttag(self, tag, attrs):
                if tag != "a":
                    return
                for key, value in attrs:
                    if key == "href" and value:
                        self.links.append(value)

        web_dir = Path("web")
        route_to_file = {"/": web_dir / "index.html"}
        route_to_file.update({f"/{item.name}": item for item in sorted(web_dir.glob("*.html")) if item.name != "index.html"})
        graph: dict[str, list[str]] = {}
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
            "/deliverables.html",
            "/executive-launch.html",
            "/toolkit-scan.html",
            "/charter.html",
        }
        self.assertTrue(required_routes <= reachable, sorted(required_routes - reachable))

    def test_dh_benchmark_contextual_navigation_sequence_is_preserved(self):
        body = self.assert_page_contains("/dh-benchmark.html", ['nav aria-label="Primary"'])
        primary_nav = re.search(r'<nav aria-label="Primary">(.*?)</nav>', body, flags=re.DOTALL)
        self.assertIsNotNone(primary_nav)
        links = re.findall(r'<a href="([^"]+)">([^<]+)</a>', primary_nav.group(1))
        self.assertEqual(
            links,
            [
                ("/evidence-summary.html", "Evidence Summary"),
                ("/surveillance-method.html", "Surveillance Method"),
                ("/applied-analysis.html", "Applied Analysis"),
                ("/hai-alert.html", "HAI Alert"),
                ("/about.html", "About"),
            ],
        )

    def test_evidence_matrix_keeps_current_sources_and_claim_limits(self):
        body = self.assert_page_contains(
            "/evidence-matrix.html",
            ["Evidence strength / limitation", "Anticipated patient benefit", "Lewis et al, 2025", "Lewis et al, 2026", "Rramani Dervishi et al, 2026", "Leia et al, 2025", "cross-sectional associations do not establish causality"],
        )
        self.assertNotIn("Patient advisors can influence health care outcomes when linked to action and measurement", body)
        self.assertNotIn("Improves communication, discharge readiness", body)

    def test_bibliography_sources_remain_intact_without_validation_note(self):
        body = self.assert_page_contains(
            "/bibliography.html",
            ["Lewis B, Cochran C, Marquez E", "Lewis B, Cochran C, Shoemaker S", "Rramani Dervishi Q", "Leia MP", "not treated as peer-reviewed evidence"],
        )
        self.assertNotIn("Validation note:", body)

    def test_hai_visual_contract_is_intact(self):
        body = self.assert_page_contains(
            "/hai-alert.html",
            ["Interactive HAI dashboard", 'id="hai-trend-chart"', 'id="hai-baseline-chart"', 'id="hai-action-grid"', "plotly-2.35.2.min.js", "/app.js", "Evidence signal", "View evidence detail table", "Evidence synthesis summary", "Infection prevention is also a communication and escalation problem.", "What PFAC should ask locally", "Leadership follow-through"],
        )
        lowered = body.casefold()
        self.assertNotIn("loading hai dashboard", lowered)
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

    def test_applied_analysis_visual_and_claim_boundaries_are_intact(self):
        body = self.assert_page_contains(
            "/applied-analysis.html",
            ["Planning analysis, not a risk score", "42%", "72%", "59%", "55%", "not a claim that Dartmouth Health has adopted", "CEPH 4", "CEPH 7", "descriptive approximations", 'id="analysis-metric"', 'id="analysis-threshold"', 'id="analysis-sort"', 'id="analysis-search"', 'id="analysis-chart"', "plotly-2.35.2.min.js", "View municipality data table", "View implementation detail table", "/applied-analysis.js"],
        )
        self.assertNotIn("Dartmouth Health implemented", body)
        self.assertNotIn("validated risk score", body.casefold())
        self.assertNotIn("<canvas", body.casefold())
        self.assertNotIn("<svg", body.casefold())

    def test_applied_analysis_script_still_renders_plotly(self):
        status, headers, body = request("/applied-analysis.js")
        self.assertEqual(status, "200 OK")
        self.assertIn("javascript", headers["Content-Type"])
        for fragment in ("/upper-valley-local-analysis.csv", "Poverty percent", "Disability percent", "Age 65+ percent", "Plotly.react", "analysis-chart", "Service-area average"):
            self.assertIn(fragment, body)

    def test_dh_benchmark_preserves_evidence_state_boundaries(self):
        body = self.assert_page_contains(
            "/dh-benchmark.html",
            ["The framework is real as a structured assessment method.", "It is not yet real as a scored benchmark", "Scoring should occur only after reviewing public materials", "Publicly supported", "Not yet validated", "Insufficient evidence", "Preliminary finding", 'id="evidence-status"', 'class="evidence-status-table"', 'id="evidence-table"', 'class="benchmark-evidence-table"'],
        )
        self.assertNotIn("Benchmark maturity model", body)
        self.assertNotIn("maturity score", body.casefold())
        rows = [segment.split("</tr>", 1)[0] for segment in body.split("<tr") if "data-evidence-status" in segment]
        self.assertGreaterEqual(len(rows), 4)
        for row in rows:
            statuses = [status for status in ("publicly-supported", "not-yet-validated", "insufficient-evidence", "preliminary-finding") if f'data-evidence-status="{status}"' in row]
            self.assertEqual(len(statuses), 1, row)

    def test_story_and_evidence_are_separated(self):
        bibliography = self.assert_page_contains("/bibliography.html", ["Rosie Bartel", "not treated as peer-reviewed evidence"])
        story = self.assert_page_contains("/story.html", ["not research evidence", "not representative evidence", "does not imply endorsement"])
        self.assertIn("Core research evidence", bibliography)

    def test_dashboard_and_toolkit_payloads_remain_valid(self):
        dashboard = build_hai_dashboard()
        toolkit = build_toolkit()
        resources = build_open_resources()
        self.assertEqual(dashboard["status"], "ok")
        self.assertGreaterEqual(len(dashboard["measures"]), 7)
        self.assertGreaterEqual(len(dashboard["executive_actions"]), 4)
        self.assertTrue(any(item["measure"] == "SSI hysterectomy" for item in dashboard["measures"]))
        self.assertGreaterEqual(len(toolkit["peer_models"]), 5)
        self.assertGreaterEqual(len(resources), 5)

    def test_public_pages_do_not_render_markdown_artifacts(self):
        for path in public_html_paths():
            with self.subTest(path=path):
                status, _, body = request(path)
                self.assertEqual(status, "200 OK")
                for fragment in ("**", "```", "### ", "## "):
                    self.assertNotIn(fragment, body, f"{path} contains raw markdown artifact {fragment!r}")


if __name__ == "__main__":
    unittest.main()

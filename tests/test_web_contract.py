from __future__ import annotations

import unittest

from pssm5_toolkit.hai_dashboard import build_hai_dashboard
from pssm5_toolkit.open_resources import build_open_resources
from pssm5_toolkit.server import application
from pssm5_toolkit.toolkit import build_toolkit


def request(path: str):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(application({"PATH_INFO": path}, start_response)).decode("utf-8")
    return captured["status"], captured["headers"], body


class WebContractTests(unittest.TestCase):
    def test_homepage_wires_model_and_resources_sections(self):
        status, headers, body = request("/")

        self.assertEqual(status, "200 OK")
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn('id="model-grid"', body)
        self.assertIn('href="/resources.html"', body)

    def test_resources_page_is_a_real_static_page(self):
        status, headers, body = request("/resources.html")

        self.assertEqual(status, "200 OK")
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn('id="open-resources-grid"', body)
        self.assertIn("/api/open-resources", body)

    def test_hai_alert_page_has_dashboard_surface(self):
        status, headers, body = request("/hai-alert.html")

        self.assertEqual(status, "200 OK")
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn('id="hai-trend-chart"', body)
        self.assertIn('id="hai-baseline-chart"', body)
        self.assertIn("plotly", body.lower())

    def test_about_page_has_notion_and_core_reviewer_links(self):
        status, headers, body = request("/about.html")

        self.assertEqual(status, "200 OK")
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn("Notion workspace", body)
        self.assertIn("Evidence-Based PFAC Summary", body)
        self.assertIn("APE deliverables", body)
        self.assertIn("Research surveillance how-to", body)
        self.assertIn('href="/surveillance-method.html"', body)

    def test_evidence_summary_uses_ape_ile_framing(self):
        status, headers, body = request("/evidence-summary.html")

        self.assertEqual(status, "200 OK")
        self.assertIn("text/html", headers["Content-Type"])
        self.assertIn("My APE/ILE project translates", body)
        self.assertIn("mutually beneficial applied work", body)
        self.assertIn("culminating high-quality written product", body)
        self.assertNotIn("The Agreement defines", body)

    def test_public_pages_do_not_expose_internal_admin_language(self):
        public_paths = [
            "/",
            "/about.html",
            "/collaboration.html",
            "/evidence-summary.html",
            "/surveillance-method.html",
            "/deliverables.html",
        ]
        forbidden_fragments = [
            "Private</span><strong>GitHub",
            "Private repository",
            "repository stays private",
            "Code, deployment, drafts, and project administration",
            "private project administration",
        ]

        for path in public_paths:
            with self.subTest(path=path):
                status, _, body = request(path)
                self.assertEqual(status, "200 OK")
                self.assertNotIn("GitHub", body)
                for fragment in forbidden_fragments:
                    self.assertNotIn(fragment, body)

    def test_payloads_have_content_for_rendered_sections(self):
        toolkit = build_toolkit()
        resources = build_open_resources()

        self.assertGreaterEqual(len(toolkit["peer_models"]), 5)
        self.assertGreaterEqual(len(resources), 5)

    def test_hai_dashboard_exposes_executive_actions(self):
        dashboard = build_hai_dashboard()

        self.assertEqual(dashboard["status"], "ok")
        self.assertGreaterEqual(len(dashboard["measures"]), 7)
        self.assertGreaterEqual(len(dashboard["executive_actions"]), 4)
        self.assertTrue(any(item["measure"] == "SSI hysterectomy" for item in dashboard["measures"]))

    def test_hai_dashboard_endpoint_returns_chart_data(self):
        status, _, body = request("/api/hai-dashboard")

        self.assertEqual(status, "200 OK")
        self.assertIn('"measures"', body)
        self.assertIn('"executive_actions"', body)


if __name__ == "__main__":
    unittest.main()

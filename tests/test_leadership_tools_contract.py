from __future__ import annotations

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


class LeadershipToolsContractTests(unittest.TestCase):
    def test_workspace_preserves_six_tools_and_audit_tables(self):
        html = Path("web/toolkit-tools.html").read_text(encoding="utf-8")
        for fragment in (
            'id="leadership-tool-select"',
            'id="leadership-focus-select"',
            'id="leadership-tool-summary"',
            'data-leadership-tool="assessment"',
            'data-leadership-tool="action"',
            'data-leadership-tool="representation"',
            'data-leadership-tool="measurement"',
            'data-leadership-tool="traceability"',
            'data-leadership-tool="launch"',
            "Inspect full working table",
            "/leadership-tools.js",
            "/leadership-tools.css",
        ):
            self.assertIn(fragment, html)
        self.assertGreaterEqual(html.count('<details class="audit-table-details">'), 5)

    def test_core_evidence_and_downloads_remain_present(self):
        html = Path("web/toolkit-tools.html").read_text(encoding="utf-8")
        preserved = (
            "A Dartmouth Health Office of Care Experience onboarding job aid approved March 3, 2026",
            "DH onboarding process documented; implementation across locations not validated by this APE",
            "PREMs, PROMs, Press Ganey measures",
            "Presence does not establish effectiveness.",
            "Do not attribute system-level change to PFAC alone.",
            "/pfac-current-state-assessment.csv",
            "/pfac-action-tracker.csv",
            "/pfac-representation-access.csv",
            "/pfac-measurement-plan.csv",
            "/pssm-domain5-traceability.csv",
            "/pfac-90-day-launch-plan.csv",
        )
        for fragment in preserved:
            self.assertIn(fragment, html)

    def test_workspace_assets_are_served(self):
        for path, content_type, sentinels in (
            ("/leadership-tools.js", "javascript", ("leadership-tool-select", "data-leadership-tool", "history.replaceState")),
            ("/leadership-tools.css", "text/css", (".tool-workspace", ".tool-summary-grid", ".audit-table-details")),
        ):
            with self.subTest(path=path):
                status, headers, body = request(path)
                self.assertEqual(status, "200 OK")
                self.assertIn(content_type, headers["Content-Type"])
                for sentinel in sentinels:
                    self.assertIn(sentinel, body)

    def test_page_specific_assets_do_not_modify_global_stylesheet(self):
        global_css = Path("web/styles.css").read_text(encoding="utf-8")
        for fragment in (".tool-workspace", ".tool-summary-grid", ".audit-table-details"):
            self.assertNotIn(fragment, global_css)

    def test_retired_reviewer_guide_stays_absent(self):
        combined = "\n".join(
            Path(path).read_text(encoding="utf-8")
            for path in ("web/toolkit-tools.html", "web/leadership-tools.js", "web/leadership-tools.css")
        ).casefold()
        for forbidden in ("reviewer guide", "/mvp-one.html", "review-flow.js", "reviewer flow"):
            self.assertNotIn(forbidden, combined)


if __name__ == "__main__":
    unittest.main()

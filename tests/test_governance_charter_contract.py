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


class GovernanceCharterContractTests(unittest.TestCase):
    def test_governance_charter_page_is_public_and_operational(self):
        status, headers, body = request("/pfac-governance-charter.html")
        self.assertEqual(status, "200 OK")
        self.assertIn("text/html", headers["Content-Type"])
        for fragment in (
            "PFAC Governance Charter Starter",
            "Purpose and scope",
            "Decision rights",
            "Agenda intake",
            "Leadership disposition",
            "Escalation",
            "Report-back",
            "Governance design is not evidence of adoption.",
        ):
            self.assertIn(fragment, body)

    def test_governance_charter_download_is_real_and_complete(self):
        status, headers, body = request("/pfac-governance-charter.csv")
        self.assertEqual(status, "200 OK")
        self.assertIn("text/csv", headers["Content-Type"])
        with Path("web/pfac-governance-charter.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(len(rows), 10)
        self.assertEqual({row["Status"] for row in rows}, {"Not assessed"})
        self.assertTrue(all(row["Local decision"] == "" for row in rows))
        self.assertTrue(all(row["Validation source"] == "" for row in rows))

    def test_current_state_tool_links_to_charter_without_expanding_tool_count(self):
        _, _, body = request("/toolkit-tools.html")
        self.assertIn("These six working tools sit inside Deliverable 2.", body)
        self.assertIn("/pfac-governance-charter.html", body)
        self.assertIn("Open governance charter starter", body)

    def test_charter_does_not_claim_local_adoption_or_authority(self):
        _, _, body = request("/pfac-governance-charter.html")
        forbidden = (
            "Dartmouth Health adopted",
            "Dartmouth Health approved",
            "current Dartmouth Health charter",
            "implemented at Dartmouth Health",
            "validated governance structure",
            "completed organizational change",
        )
        for fragment in forbidden:
            self.assertNotIn(fragment.casefold(), body.casefold())
        self.assertIn("must be validated by the host health system before use", body)


if __name__ == "__main__":
    unittest.main()

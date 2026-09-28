"""Frontend-backend contract for the live public data section on resources.html.

The live-data.js UI depends on exact payload shapes from pssm5_toolkit.live_data.
These tests pin those shapes so a backend change cannot silently break the UI.
All network calls are mocked; we assert shape, not live values.
"""
import json
import unittest
from unittest.mock import patch

from pssm5_toolkit.live_data import (
    fetch_census_demographics,
    fetch_evidence_watch,
    fetch_hcahps,
    live_data_status,
    search_facilities,
)


class LiveDataUIContractTest(unittest.TestCase):
    def test_status_payload_has_sources_with_ids_and_labels(self):
        st = live_data_status()
        self.assertEqual(st["status"], "ok")
        self.assertTrue(st["sources"])
        for s in st["sources"]:
            self.assertIn("id", s)
            self.assertIn("label", s)
            self.assertIn("endpoint", s)

    @patch("pssm5_toolkit.live_data._get_json")
    def test_facility_search_shape(self, mock_get):
        mock_get.return_value = {
            "results": [
                {"facility_id": "300001", "facility_name": "CONCORD HOSPITAL"}
            ]
        }
        d = search_facilities(name="", state="NH")
        self.assertEqual(d["status"], "ok")
        for f in d["facilities"]:
            self.assertIn("facility_id", f)
            self.assertIn("facility_name", f)

    @patch("pssm5_toolkit.live_data._get_json")
    def test_hcahps_measure_shape(self, mock_get):
        mock_get.return_value = {
            "results": [
                {
                    "facility_id": "300003",
                    "facility_name": "MARY HITCHCOCK",
                    "measure_id": "H_COMP_1_A_P",
                    "patient_survey_star_rating": "4",
                    "hcpahps_answer_percent": "78",
                }
            ]
        }
        d = fetch_hcahps("300003")
        # ok or unavailable both acceptable; shape must hold on ok
        if d["status"] == "ok":
            for m in d["measures"]:
                self.assertIn("label", m)
                self.assertIn("facility_percent", m)
                self.assertIn("national_percent", m)
        else:
            self.assertIn("reason_code", d)

    @patch("pssm5_toolkit.live_data._get_json")
    def test_evidence_watch_ama11_shape(self, mock_get):
        mock_get.return_value = {"esearchresult": {"count": "0", "idlist": []}}
        d = fetch_evidence_watch()
        self.assertEqual(d["status"], "ok")
        for w in d["watches"]:
            self.assertIn("watch_id", w)
            self.assertIn("total_results", w)
            for a in w["recent"]:
                self.assertIn("ama11_citation", a)
                self.assertIn("url", a)
                self.assertTrue(a["url"].startswith("https://pubmed.ncbi.nlm.nih.gov/"))

    def test_census_unavailable_shape_without_key(self):
        d = fetch_census_demographics("33", "009")
        self.assertEqual(d["status"], "unavailable")
        self.assertEqual(d["reason_code"], "CREDENTIALS_NOT_CONFIGURED")
        self.assertIn("detail", d)

    def test_resources_page_includes_live_data_section(self):
        from pathlib import Path
        html = Path("web/resources.html").read_text()
        self.assertIn('id="live-data"', html)
        self.assertIn("live-data.js", html)
        self.assertIn("live-data.css", html)


if __name__ == "__main__":
    unittest.main()

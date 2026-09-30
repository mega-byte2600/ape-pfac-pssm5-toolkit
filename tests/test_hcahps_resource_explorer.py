"""Regression coverage for the CMS HCAHPS Resources explorer."""

import unittest
from pathlib import Path
from unittest.mock import patch

from pssm5_toolkit import hcahps_data


class HCAHPSResourceExplorerTest(unittest.TestCase):
    def setUp(self):
        hcahps_data._CACHE.clear()

    @patch("pssm5_toolkit.hcahps_data._get_json")
    def test_hospital_state_national_contract_uses_current_cms_fields(self, mock_get):
        hospital = {
            "results": [
                {
                    "facility_id": "300003",
                    "facility_name": "MARY HITCHCOCK MEMORIAL HOSPITAL",
                    "citytown": "LEBANON",
                    "state": "NH",
                    "hcahps_measure_id": "H_COMP_1_A_P",
                    "hcahps_question": 'Patients who reported that their nurses "Always" communicated well',
                    "hcahps_answer_percent": "81",
                    "patient_survey_star_rating": "4",
                    "start_date": "10/01/2024",
                    "end_date": "09/30/2025",
                }
            ]
        }
        state = {
            "results": [
                {
                    "state": "NH",
                    "hcahps_measure_id": "H_COMP_1_A_P",
                    "hcahps_question": 'Patients who reported that their nurses "Always" communicated well',
                    "hcahps_answer_percent": "82",
                    "start_date": "10/01/2024",
                    "end_date": "09/30/2025",
                }
            ]
        }
        national = {
            "results": [
                {
                    "hcahps_measure_id": "H_COMP_1_A_P",
                    "hcahps_question": 'Patients who reported that their nurses "Always" communicated well',
                    "hcahps_answer_percent": "80",
                    "start_date": "10/01/2024",
                    "end_date": "09/30/2025",
                }
            ]
        }
        mock_get.side_effect = [hospital, state, national]

        payload = hcahps_data.fetch_hcahps_comparison("300003")

        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["facility_name"], "MARY HITCHCOCK MEMORIAL HOSPITAL")
        self.assertEqual(payload["state"], "NH")
        self.assertFalse(payload["api_key_required"])
        first = payload["measures"][0]
        self.assertEqual(first["measure_id"], "H_COMP_1_A_P")
        self.assertEqual(first["hospital_percent"], 81.0)
        self.assertEqual(first["state_percent"], 82.0)
        self.assertEqual(first["national_percent"], 80.0)
        self.assertTrue(first["period_alignment"])
        self.assertEqual(first["hospital_period"]["start"], "10/01/2024")

        urls = [call.args[0] for call in mock_get.call_args_list]
        self.assertIn("dgck-syfz", urls[0])
        self.assertIn("84jm-wiui", urls[1])
        self.assertIn("99ue-w85f", urls[2])
        state_params = mock_get.call_args_list[1].args[1]
        self.assertEqual(state_params["conditions[0][property]"], "state")
        self.assertEqual(state_params["conditions[0][value]"], "NH")

    @patch("pssm5_toolkit.hcahps_data._get_json")
    def test_suppressed_or_non_numeric_percentages_render_as_missing(self, mock_get):
        hospital = {
            "results": [
                {
                    "facility_id": "300003",
                    "facility_name": "MARY HITCHCOCK MEMORIAL HOSPITAL",
                    "citytown": "LEBANON",
                    "state": "NH",
                    "hcahps_measure_id": "H_COMP_1_A_P",
                    "hcahps_answer_percent": "Not Available",
                }
            ]
        }
        state = {
            "results": [
                {
                    "state": "NH",
                    "hcahps_measure_id": "H_COMP_1_A_P",
                    "hcahps_answer_percent": "101",
                }
            ]
        }
        national = {
            "results": [
                {
                    "hcahps_measure_id": "H_COMP_1_A_P",
                    "hcahps_answer_percent": "80",
                }
            ]
        }
        mock_get.side_effect = [hospital, state, national]
        payload = hcahps_data.fetch_hcahps_comparison("300003")
        first = payload["measures"][0]
        self.assertIsNone(first["hospital_percent"])
        self.assertIsNone(first["state_percent"])
        self.assertEqual(first["national_percent"], 80.0)

    def test_invalid_facility_id_is_rejected_without_network(self):
        with patch("pssm5_toolkit.hcahps_data._get_json") as mock_get:
            payload = hcahps_data.fetch_hcahps_comparison("abc")
        self.assertEqual(payload["status"], "unavailable")
        self.assertEqual(payload["reason_code"], "INVALID_FACILITY_ID")
        mock_get.assert_not_called()

    def test_resources_page_wires_the_explorer(self):
        html = Path("web/resources.html").read_text()
        js = Path("web/hcahps-explorer.js").read_text()
        server = Path("pssm5_toolkit/server.py").read_text()
        self.assertIn('id="cms-hcahps-explorer"', html)
        self.assertIn('id="hcahps-explorer-form"', html)
        self.assertIn("hcahps-explorer.js", html)
        self.assertIn("/api/live/hcahps-compare", js)
        self.assertIn('path == "/api/live/hcahps-compare"', server)
        self.assertIn("state and the United States", html)
        self.assertIn("No API key or login required", html)


if __name__ == "__main__":
    unittest.main()

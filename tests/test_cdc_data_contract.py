import json
import unittest
from pathlib import Path
from unittest.mock import patch

from pssm5_toolkit.cdc_data import (
    fetch_cdc_candidemia,
    fetch_cdc_hai_isa,
    fetch_cdc_places_county,
    fetch_cdc_svi_county,
)
from pssm5_toolkit.cdc_geography import fetch_cdc_counties
from pssm5_toolkit.server import application


def request(path, query=""):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(
        application(
            {"PATH_INFO": path, "QUERY_STRING": query, "REQUEST_METHOD": "GET"},
            start_response,
        )
    ).decode("utf-8")
    return captured["status"], json.loads(body)


class CDCDataContractTests(unittest.TestCase):
    @patch("pssm5_toolkit.cdc_data._get_json")
    def test_haic_isa_shape(self, mock_get):
        mock_get.return_value = [
            {"yearname": "2024", "topic": "Incidence", "viewby": "Overall", "series": "MRSA", "value": "12.4"}
        ]
        d = fetch_cdc_hai_isa(limit=10)
        self.assertEqual(d["status"], "ok")
        self.assertEqual(d["dataset_id"], "ssz5-s49e")
        self.assertEqual(d["records"][0]["year"], 2024)
        self.assertEqual(d["records"][0]["series"], "MRSA")
        self.assertEqual(d["records"][0]["value"], 12.4)

    @patch("pssm5_toolkit.cdc_data._get_json")
    def test_candidemia_shape(self, mock_get):
        mock_get.return_value = [
            {"yearname": "2023", "topic": "Resistance", "viewby": "Drug", "series": "Fluconazole", "value": "5.0"}
        ]
        d = fetch_cdc_candidemia(limit=10)
        self.assertEqual(d["status"], "ok")
        self.assertEqual(d["dataset_id"], "34p9-h4us")
        self.assertEqual(d["count"], 1)

    @patch("pssm5_toolkit.cdc_data._get_json")
    def test_places_county_shape_and_fips(self, mock_get):
        mock_get.return_value = [
            {
                "year": "2023",
                "stateabbr": "CA",
                "locationname": "San Luis Obispo",
                "locationid": "06079",
                "category": "Health Status",
                "measure": "Frequent mental distress among adults",
                "data_value_type": "Age-adjusted prevalence",
                "data_value_unit": "%",
                "data_value": "12.1",
                "low_confidence_limit": "11.7",
                "high_confidence_limit": "12.5",
            }
        ]
        d = fetch_cdc_places_county("06079")
        self.assertEqual(d["status"], "ok")
        self.assertEqual(d["location_id"], "06079")
        self.assertEqual(d["measures"][0]["value"], 12.1)
        params = mock_get.call_args[0][1]
        self.assertEqual(params["locationid"], "06079")

    def test_places_rejects_bad_fips(self):
        d = fetch_cdc_places_county("6079")
        self.assertEqual(d["status"], "unavailable")
        self.assertEqual(d["reason_code"], "MISSING_PARAMETERS")

    @patch("pssm5_toolkit.cdc_geography._get_json")
    def test_county_selector_returns_valid_fips(self, mock_get):
        mock_get.return_value = [
            {"locationid": "06037", "locationname": "Los Angeles", "stateabbr": "CA"},
            {"locationid": "06079", "locationname": "San Luis Obispo", "stateabbr": "CA"},
        ]
        d = fetch_cdc_counties("ca")
        self.assertEqual(d["status"], "ok")
        self.assertEqual(d["state"], "CA")
        self.assertEqual(d["counties"][1]["fips"], "06079")
        params = mock_get.call_args[0][1]
        self.assertIn("stateabbr='CA'", params["$where"])

    @patch("pssm5_toolkit.cdc_data._get_json")
    def test_svi_shape(self, mock_get):
        mock_get.return_value = {
            "features": [
                {
                    "attributes": {
                        "FIPS": "06079",
                        "LOCATION": "San Luis Obispo County, California",
                        "RPL_THEMES": 0.31,
                        "RPL_THEME1": 0.24,
                        "RPL_THEME2": 0.35,
                        "RPL_THEME3": 0.42,
                        "RPL_THEME4": 0.29,
                    }
                }
            ]
        }
        d = fetch_cdc_svi_county("06079")
        self.assertEqual(d["status"], "ok")
        self.assertEqual(d["overall_percentile"], 0.31)
        self.assertIn("housing_transportation", d["themes"])

    def test_public_pages_surface_cdc_integration_without_internal_copy(self):
        resources = Path("web/resources.html").read_text(encoding="utf-8")
        hai = Path("web/hai-alert.html").read_text(encoding="utf-8")
        js = Path("web/live-data.js").read_text(encoding="utf-8")
        selector = Path("web/cdc-county-selector.js").read_text(encoding="utf-8")
        app = Path("web/app.js").read_text(encoding="utf-8")
        self.assertIn('id="cdc-community-context"', resources)
        self.assertIn('id="cdc-state"', resources)
        self.assertIn('id="cdc-county-fips"', resources)
        self.assertIn('id="cdc-county-submit"', resources)
        self.assertNotIn('type="text" id="cdc-county-fips"', resources)
        self.assertIn("/api/live/cdc/counties", selector)
        self.assertIn("/api/live/cdc/places", js)
        self.assertIn("/api/live/cdc/svi", js)
        self.assertIn('id="cdc-hai-live"', hai)
        self.assertIn("/api/live/cdc/hai-isa", app)
        self.assertIn("/api/live/cdc/candidemia", app)
        for page in Path("web").glob("*.html"):
            self.assertNotIn("Carpe Data", page.read_text(encoding="utf-8"), page.name)

    @patch("pssm5_toolkit.cdc_geography._get_json")
    def test_server_counties_route(self, mock_get):
        mock_get.return_value = [
            {"locationid": "06079", "locationname": "San Luis Obispo", "stateabbr": "CA"}
        ]
        status, d = request("/api/live/cdc/counties", "state=CA")
        self.assertEqual(status, "200 OK")
        self.assertEqual(d["status"], "ok")
        self.assertEqual(d["counties"][0]["fips"], "06079")

    @patch("pssm5_toolkit.cdc_data._get_json")
    def test_server_places_route(self, mock_get):
        mock_get.return_value = []
        status, d = request("/api/live/cdc/places", "location_id=06079&limit=5")
        self.assertEqual(status, "200 OK")
        self.assertEqual(d["status"], "ok")
        self.assertEqual(d["dataset_id"], "swc5-untb")


if __name__ == "__main__":
    unittest.main()

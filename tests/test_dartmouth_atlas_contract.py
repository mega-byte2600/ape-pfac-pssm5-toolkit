"""Contract tests for the Dartmouth Atlas Resources explorer."""
import csv
import io
import zipfile
import unittest
from unittest.mock import patch

from pssm5_toolkit.dartmouth_atlas import atlas_catalog, atlas_options, atlas_value, _load_dataset


def _zip_csv():
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["hrrnum", "hrrname", "year", "primary_visit_rate", "readmit_rate"])
    writer.writeheader()
    writer.writerow({"hrrnum":"101","hrrname":"Lebanon, NH","year":"2018","primary_visit_rate":"74.1","readmit_rate":"12.4"})
    writer.writerow({"hrrnum":"101","hrrname":"Lebanon, NH","year":"2019","primary_visit_rate":"75.2","readmit_rate":"-99999"})
    raw = io.BytesIO()
    with zipfile.ZipFile(raw, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("sample.csv", output.getvalue())
    return raw.getvalue()


class DartmouthAtlasContractTest(unittest.TestCase):
    def setUp(self):
        _load_dataset.cache_clear()

    def tearDown(self):
        _load_dataset.cache_clear()

    def test_catalog_is_small_and_curated(self):
        payload = atlas_catalog()
        self.assertEqual(payload["status"], "ok")
        self.assertEqual([d["id"] for d in payload["datasets"]], ["primary-care", "post-discharge"])

    @patch("pssm5_toolkit.dartmouth_atlas._fetch_bytes", return_value=_zip_csv())
    def test_options_expose_human_area_and_measure(self, _mock):
        payload = atlas_options("primary-care")
        self.assertEqual(payload["status"], "ok")
        self.assertIn("Lebanon, NH", payload["areas"])
        ids = [m["id"] for m in payload["measures"]]
        self.assertIn("primary_visit_rate", ids)

    @patch("pssm5_toolkit.dartmouth_atlas._fetch_bytes", return_value=_zip_csv())
    def test_value_uses_latest_year(self, _mock):
        payload = atlas_value("primary-care", "Lebanon, NH", "primary_visit_rate")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["year"], "2019")
        self.assertEqual(payload["value"], 75.2)

    @patch("pssm5_toolkit.dartmouth_atlas._fetch_bytes", return_value=_zip_csv())
    def test_suppression_sentinel_is_never_rendered_as_value(self, _mock):
        payload = atlas_value("post-discharge", "Lebanon, NH", "readmit_rate")
        self.assertEqual(payload["status"], "ok")
        self.assertTrue(payload["suppressed"])
        self.assertIsNone(payload["value"])
        self.assertIn("privacy", payload["note"].lower())


if __name__ == "__main__":
    unittest.main()

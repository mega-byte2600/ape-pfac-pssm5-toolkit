"""Frontend-backend contract for the live public data section on resources.html.

The live-data.js UI depends on exact payload shapes from pssm5_toolkit.live_data.
These tests pin those shapes so a backend change cannot silently break the UI.
All network calls are mocked; we assert shape, not live values.
"""
import json
import unittest
from unittest.mock import patch

from pssm5_toolkit.live_data import (
    _trial_search_token,
    fetch_census_demographics,
    fetch_evidence_watch,
    fetch_hcahps,
    fetch_trials,
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
        self.assertIn('id="trials-panel"', html)

    @patch("pssm5_toolkit.live_data._get_json")
    def test_facility_search_uses_partial_match_and_ranks(self, mock_get):
        mock_get.return_value = {
            "results": [
                {"facility_id": "1", "facility_name": "EAST HITCHCOCK CLINIC",
                 "citytown": "A", "state": "NH", "countyparish": "X"},
                {"facility_id": "2", "facility_name": "HITCHCOCK MEMORIAL",
                 "citytown": "B", "state": "NH", "countyparish": "Y"},
                {"facility_id": "3", "facility_name": "MARY HITCHCOCK MEMORIAL HOSPITAL",
                 "citytown": "C", "state": "NH", "countyparish": "Z"},
                # duplicate row for facility 3 (one row per measure upstream)
                {"facility_id": "3", "facility_name": "MARY HITCHCOCK MEMORIAL HOSPITAL",
                 "citytown": "C", "state": "NH", "countyparish": "Z"},
            ]
        }
        d = search_facilities(name="Hitchcock", state="NH")
        self.assertEqual(d["status"], "ok")
        # like operator with wildcards, not exact match
        _, kwargs = mock_get.call_args
        params = kwargs.get("params") or mock_get.call_args[0][1]
        values = list(params.values())
        self.assertTrue(any(v == "like" for v in values))
        self.assertTrue(any("%Hitchcock%" in str(v) for v in values))
        # deduped by facility_id, best match first
        ids = [f["facility_id"] for f in d["facilities"]]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(ids[0], "2")  # starts-with beats contains
        self.assertEqual(d["count"], 3)

    def test_trial_search_token_picks_distinctive_word(self):
        self.assertEqual(
            _trial_search_token("MARY HITCHCOCK MEMORIAL HOSPITAL"), "HITCHCOCK"
        )
        self.assertEqual(_trial_search_token(""), "")
        self.assertEqual(_trial_search_token("St "), "")

    @patch("pssm5_toolkit.live_data._get_json")
    def test_trials_shape_filters_to_matching_locations(self, mock_get):
        mock_get.return_value = {
            "studies": [
                {
                    "protocolSection": {
                        "identificationModule": {
                            "nctId": "NCT0001",
                            "briefTitle": "Advisor input study",
                        },
                        "statusModule": {"overallStatus": "RECRUITING"},
                        "designModule": {"phases": ["Phase 2"], "studyType": "Interventional"},
                        "conditionsModule": {"keywords": ["Diabetes"]},
                        "contactsLocationsModule": {
                            "locations": [
                                {"facility": "Mary Hitchcock Memorial Hospital",
                                 "city": "Lebanon", "state": "New Hampshire"},
                                {"facility": "Unrelated Clinic",
                                 "city": "Boston", "state": "Massachusetts"},
                            ]
                        },
                    }
                },
                {
                    # no matching location: filtered out
                    "protocolSection": {
                        "identificationModule": {"nctId": "NCT0002", "briefTitle": "Other"},
                        "statusModule": {"overallStatus": "COMPLETED"},
                        "contactsLocationsModule": {
                            "locations": [{"facility": "Far Away Hospital",
                                           "city": "Reno", "state": "Nevada"}]
                        },
                    }
                },
            ]
        }
        d = fetch_trials("Mary Hitchcock Memorial Hospital", state="NH")
        self.assertEqual(d["status"], "ok")
        self.assertEqual(d["count"], 1)
        s = d["studies"][0]
        self.assertEqual(s["nct_id"], "NCT0001")
        self.assertTrue(s["url"].endswith("/NCT0001"))
        self.assertEqual(s["status"], "RECRUITING")
        # only the matching location survives; NH filter applied
        self.assertEqual(len(s["locations"]), 1)
        self.assertIn("Hitchcock", s["locations"][0]["facility"])
        self.assertIn("clinicaltrials.gov", d["source"].lower())

    def test_trials_missing_name_is_unavailable(self):
        d = fetch_trials("", "")
        self.assertEqual(d["status"], "unavailable")
        self.assertEqual(d["reason_code"], "MISSING_PARAMETERS")

    def test_get_json_retries_transient_then_succeeds(self):
        import urllib.error
        from pssm5_toolkit import live_data

        calls = []

        class FakeResponse:
            def __enter__(self):
                return self

            def __exit__(self, *a):
                return False

            def read(self):
                return b'{"ok": true}'

        def fake_urlopen(request, timeout=None):
            calls.append(1)
            if len(calls) == 1:
                raise urllib.error.HTTPError(
                    request.full_url, 503, "Service Unavailable", {}, None
                )
            return FakeResponse()

        with patch.object(live_data.urllib.request, "urlopen", fake_urlopen):
            with patch.object(live_data.time, "sleep", lambda s: None):
                result = live_data._get_json("https://example.invalid/x")
        self.assertEqual(result, {"ok": True})
        self.assertEqual(len(calls), 2)

    def test_get_json_does_not_retry_client_errors(self):
        import urllib.error
        from pssm5_toolkit import live_data

        calls = []

        def fake_urlopen(request, timeout=None):
            calls.append(1)
            raise urllib.error.HTTPError(
                request.full_url, 400, "Bad Request", {}, None
            )

        with patch.object(live_data.urllib.request, "urlopen", fake_urlopen):
            with self.assertRaises(urllib.error.HTTPError):
                live_data._get_json("https://example.invalid/x")
        self.assertEqual(len(calls), 1)

    @patch("pssm5_toolkit.live_data._probe_source")
    def test_status_reports_state_per_source(self, mock_probe):
        from pssm5_toolkit import live_data

        live_data._CACHE.clear()
        mock_probe.return_value = {"state": "live", "reason": ""}
        st = live_data_status()
        self.assertEqual(st["status"], "ok")
        ids = {s["id"] for s in st["sources"]}
        self.assertIn("trials", ids)
        for s in st["sources"]:
            self.assertIn("id", s)
            self.assertIn("label", s)
            self.assertIn("endpoint", s)
            self.assertIn("state", s)
            self.assertIn(s["state"], {"live", "degraded", "unavailable", "needs_key"})


if __name__ == "__main__":
    unittest.main()

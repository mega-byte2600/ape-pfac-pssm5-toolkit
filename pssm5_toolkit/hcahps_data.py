"""CMS HCAHPS comparison adapter for the Resources explorer.

Public aggregate data only. No API key is required for the CMS Provider Data
Catalog Open Data API. The adapter returns one stable payload comparing a
selected hospital with its state and U.S. HCAHPS benchmarks.
"""

from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

_TIMEOUT_SECONDS = 12
_USER_AGENT = "ape-pfac-pssm5-toolkit/0.1 (MPH Applied Practice Experience)"
_CMS_BASE = "https://data.cms.gov/provider-data/api/1/datastore/query"
_CMS_HOSPITAL_DATASET = "dgck-syfz"
_CMS_STATE_DATASET = "84jm-wiui"
_CMS_NATIONAL_DATASET = "99ue-w85f"
_CACHE: Dict[str, Any] = {}

HCAHPS_FOCUS_MEASURES = {
    "H_COMP_1_A_P": "Nurses always communicated well",
    "H_COMP_2_A_P": "Doctors always communicated well",
    "H_COMP_3_A_P": "Always received help when wanted",
    "H_COMP_5_A_P": "Staff always explained medicines",
    "H_COMP_6_Y_P": "Always quiet at night",
    "H_CLEAN_HSP_A_P": "Room and bathroom always clean",
    "H_HSP_RATING_9_10": "Rated hospital 9 or 10",
    "H_RECMND_DY": "Would definitely recommend",
}


def _cache_get(key: str) -> Optional[Dict[str, Any]]:
    entry = _CACHE.get(key)
    if entry and entry[0] > time.time():
        return entry[1]
    _CACHE.pop(key, None)
    return None


def _cache_set(key: str, value: Dict[str, Any], ttl_seconds: int) -> None:
    _CACHE[key] = (time.time() + ttl_seconds, value)


def _get_json(url: str, params: Optional[Dict[str, str]] = None) -> Any:
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
        return json.loads(response.read().decode("utf-8"))


def _unavailable(reason_code: str, detail: str = "") -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "status": "unavailable",
        "source": "CMS Provider Data Catalog: HCAHPS (data.cms.gov)",
        "reason_code": reason_code,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if detail:
        payload["detail"] = detail
    return payload


def _rows(payload: Any) -> List[Dict[str, Any]]:
    results = (payload or {}).get("results", []) if isinstance(payload, dict) else []
    return [row for row in results if isinstance(row, dict)]


def _index(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    result: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        measure_id = row.get("hcahps_measure_id")
        if measure_id in HCAHPS_FOCUS_MEASURES:
            result[measure_id] = row
    return result


def _percent(value: Any) -> Optional[float]:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text.lower() in {"not available", "n/a", "na", "null"}:
        return None
    try:
        number = float(text)
    except (TypeError, ValueError):
        return None
    if number < 0 or number > 100:
        return None
    return round(number, 1)


def _period(row: Dict[str, Any]) -> Dict[str, Optional[str]]:
    return {
        "start": row.get("start_date") or None,
        "end": row.get("end_date") or None,
    }


def fetch_hcahps_comparison(facility_id: str) -> Dict[str, Any]:
    """Return hospital, state, and national HCAHPS benchmarks for one CCN."""
    facility_id = (facility_id or "").strip()
    if not re.fullmatch(r"\d{6}", facility_id):
        return _unavailable(
            "INVALID_FACILITY_ID",
            "facility_id must be a six-digit CMS Certification Number.",
        )

    cache_key = f"hcahps_compare:{facility_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        hospital_payload = _get_json(
            f"{_CMS_BASE}/{_CMS_HOSPITAL_DATASET}/0",
            {
                "limit": "500",
                "conditions[0][property]": "facility_id",
                "conditions[0][value]": facility_id,
                "conditions[0][operator]": "=",
            },
        )
        hospital_rows = _rows(hospital_payload)
        if not hospital_rows:
            payload = _unavailable(
                "NO_PUBLISHED_DATA",
                "CMS has no published HCAHPS rows for this facility in the current dataset.",
            )
            _cache_set(cache_key, payload, 3600)
            return payload

        identity_row = hospital_rows[0]
        facility_name = identity_row.get("facility_name") or f"CMS facility {facility_id}"
        state = (identity_row.get("state") or "").strip().upper()
        city = identity_row.get("citytown") or ""
        if not re.fullmatch(r"[A-Z]{2}", state):
            payload = _unavailable(
                "MISSING_STATE",
                "CMS hospital rows did not include a usable two-letter state code.",
            )
            _cache_set(cache_key, payload, 3600)
            return payload

        state_payload = _get_json(
            f"{_CMS_BASE}/{_CMS_STATE_DATASET}/0",
            {
                "limit": "500",
                "conditions[0][property]": "state",
                "conditions[0][value]": state,
                "conditions[0][operator]": "=",
            },
        )
        national_payload = _get_json(
            f"{_CMS_BASE}/{_CMS_NATIONAL_DATASET}/0",
            {"limit": "500"},
        )
    except Exception as exc:  # upstream failure is surfaced, never fabricated
        payload = _unavailable("UPSTREAM_FAILURE", type(exc).__name__)
        _cache_set(cache_key, payload, 300)
        return payload

    hospital_index = _index(hospital_rows)
    state_index = _index(_rows(state_payload))
    national_index = _index(_rows(national_payload))

    measures: List[Dict[str, Any]] = []
    for measure_id, label in HCAHPS_FOCUS_MEASURES.items():
        hospital = hospital_index.get(measure_id, {})
        state_row = state_index.get(measure_id, {})
        national = national_index.get(measure_id, {})
        hospital_period = _period(hospital)
        state_period = _period(state_row)
        national_period = _period(national)
        periods = [hospital_period, state_period, national_period]
        comparable_periods = [p for p in periods if p["start"] or p["end"]]
        period_alignment = bool(comparable_periods) and all(
            p == comparable_periods[0] for p in comparable_periods
        )
        measures.append(
            {
                "measure_id": measure_id,
                "label": label,
                "question": (
                    hospital.get("hcahps_question")
                    or state_row.get("hcahps_question")
                    or national.get("hcahps_question")
                    or ""
                ),
                "hospital_percent": _percent(hospital.get("hcahps_answer_percent")),
                "state_percent": _percent(state_row.get("hcahps_answer_percent")),
                "national_percent": _percent(national.get("hcahps_answer_percent")),
                "hospital_star_rating": hospital.get("patient_survey_star_rating"),
                "hospital_period": hospital_period,
                "state_period": state_period,
                "national_period": national_period,
                "period_alignment": period_alignment,
            }
        )

    payload = {
        "status": "ok",
        "source": "CMS Provider Data Catalog: HCAHPS (data.cms.gov)",
        "api_key_required": False,
        "facility_id": facility_id,
        "facility_name": facility_name,
        "city": city,
        "state": state,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "cache_ttl_seconds": 86400,
        "source_urls": {
            "hospital": f"https://data.cms.gov/provider-data/dataset/{_CMS_HOSPITAL_DATASET}",
            "state": f"https://data.cms.gov/provider-data/dataset/{_CMS_STATE_DATASET}",
            "national": f"https://data.cms.gov/provider-data/dataset/{_CMS_NATIONAL_DATASET}",
        },
        "note": (
            "Public CMS-published HCAHPS aggregates for patient-experience context and benchmarking. "
            "These data do not establish that PFAC activity caused any observed score."
        ),
        "measures": measures,
    }
    _cache_set(cache_key, payload, 24 * 3600)
    return payload

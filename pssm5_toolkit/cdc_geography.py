"""Mistake-proof CDC county lookup for the public APE interface."""

from __future__ import annotations

import re
import time
from typing import Any, Dict

from .live_data import _cache_get, _cache_set, _get_json, _unavailable

_CDC_PLACES_URL = "https://data.cdc.gov/resource/swc5-untb.json"
_SOURCE = "CDC PLACES: Local Data for Better Health, County Data, 2025 release"


def fetch_cdc_counties(state: str = "") -> Dict[str, Any]:
    """Return valid county names and five-digit FIPS codes for one state."""
    state_abbr = (state or "").strip().upper()
    if not re.fullmatch(r"[A-Z]{2}", state_abbr):
        return _unavailable(
            _SOURCE,
            "MISSING_PARAMETERS",
            "Choose a two-letter U.S. state abbreviation.",
        )

    cache_key = f"cdc_counties:{state_abbr}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        rows = _get_json(
            _CDC_PLACES_URL,
            {
                "$select": "locationid,locationname,stateabbr",
                "$where": f"stateabbr='{state_abbr}'",
                "$group": "locationid,locationname,stateabbr",
                "$order": "locationname ASC",
                "$limit": "500",
            },
        )
    except Exception as exc:  # noqa: BLE001
        payload = _unavailable(_SOURCE, "UPSTREAM_FAILURE", type(exc).__name__)
        _cache_set(cache_key, payload, 300)
        return payload

    counties = []
    seen = set()
    for row in rows if isinstance(rows, list) else []:
        fips = str(row.get("locationid") or "").strip()
        name = str(row.get("locationname") or "").strip()
        if len(fips) != 5 or not fips.isdigit() or not name or fips in seen:
            continue
        seen.add(fips)
        counties.append({"fips": fips, "name": name})

    if not counties:
        payload = _unavailable(
            _SOURCE,
            "NOT_FOUND",
            f"No CDC PLACES counties were returned for {state_abbr}.",
        )
        _cache_set(cache_key, payload, 300)
        return payload

    payload = {
        "status": "ok",
        "source": _SOURCE,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "state": state_abbr,
        "count": len(counties),
        "counties": counties,
    }
    _cache_set(cache_key, payload, 24 * 3600)
    return payload

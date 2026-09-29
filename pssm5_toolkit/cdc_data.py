"""CDC public-data adapters for the APE PFAC leadership toolkit.

Public aggregate CDC data only. These feeds provide patient-safety and
population context; they do not measure PFAC effectiveness and are not local
organizational performance unless the returned geography matches the user.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List, Optional

from .live_data import _cache_get, _cache_set, _get_json, _unavailable

_CDC_SOCRATA = "https://data.cdc.gov/resource"
_CDC_ISA_DATASET = "ssz5-s49e"
_CDC_CANDIDEMIA_DATASET = "34p9-h4us"
_CDC_PLACES_COUNTY_DATASET = "swc5-untb"
_CDC_SVI_COUNTY = (
    "https://services3.arcgis.com/ZvidGQkLaDJxRSJ2/ArcGIS/rest/services/"
    "CDC_ATSDR_Social_Vulnerability_Index_2022_USA/FeatureServer/1/query"
)


def _now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _bounded_limit(value: int, maximum: int = 250) -> int:
    return min(max(int(value), 1), maximum)


def _probe(url: str, params: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    started = time.time()
    try:
        _get_json(url, params, timeout=6)
    except Exception as exc:  # noqa: BLE001
        return {"state": "unavailable", "reason": type(exc).__name__}
    elapsed = time.time() - started
    if elapsed > 4:
        return {"state": "degraded", "reason": f"slow response ({elapsed:.1f}s)"}
    return {"state": "live", "reason": ""}


def _normalize_haic_rows(rows: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for row in rows or []:
        value = row.get("value")
        try:
            value = float(value) if value not in (None, "") else None
        except (TypeError, ValueError):
            value = None
        year = row.get("yearname")
        try:
            year = int(float(year)) if year not in (None, "") else None
        except (TypeError, ValueError):
            year = None
        normalized.append(
            {
                "year": year,
                "topic": row.get("topic"),
                "view_by": row.get("viewby"),
                "series": row.get("series"),
                "value": value,
            }
        )
    return normalized


def _fetch_haic_dataset(
    dataset_id: str,
    source_label: str,
    source_url: str,
    *,
    topic: str = "",
    view_by: str = "",
    series: str = "",
    limit: int = 100,
) -> Dict[str, Any]:
    limit = _bounded_limit(limit)
    cache_key = f"cdc_haic:{dataset_id}:{topic}:{view_by}:{series}:{limit}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    params: Dict[str, str] = {"$limit": str(limit), "$order": "yearname DESC"}
    if topic:
        params["topic"] = topic
    if view_by:
        params["viewby"] = view_by
    if series:
        params["series"] = series

    try:
        rows = _get_json(f"{_CDC_SOCRATA}/{dataset_id}.json", params)
    except Exception as exc:  # noqa: BLE001
        payload = _unavailable(source_label, "UPSTREAM_FAILURE", type(exc).__name__)
        _cache_set(cache_key, payload, 300)
        return payload

    records = _normalize_haic_rows(rows if isinstance(rows, list) else [])
    payload = {
        "status": "ok",
        "source": source_label,
        "source_url": source_url,
        "dataset_id": dataset_id,
        "fetched_at": _now(),
        "count": len(records),
        "note": (
            "CDC HAIC surveillance context. Small counts and differing methods can "
            "limit year-to-year interpretation; this is not a local PFAC outcome measure."
        ),
        "records": records,
    }
    _cache_set(cache_key, payload, 6 * 3600)
    return payload


def fetch_cdc_hai_isa(
    topic: str = "", view_by: str = "", series: str = "", limit: int = 100
) -> Dict[str, Any]:
    """CDC HAICViz invasive Staphylococcus aureus (MRSA/MSSA) surveillance."""
    return _fetch_haic_dataset(
        _CDC_ISA_DATASET,
        "CDC HAICViz: Invasive Staphylococcus aureus",
        "https://data.cdc.gov/Public-Health-Surveillance/HAICViz-iSA/ssz5-s49e",
        topic=topic,
        view_by=view_by,
        series=series,
        limit=limit,
    )


def fetch_cdc_candidemia(
    topic: str = "", view_by: str = "", series: str = "", limit: int = 100
) -> Dict[str, Any]:
    """CDC HAICViz candidemia surveillance, including resistance views."""
    return _fetch_haic_dataset(
        _CDC_CANDIDEMIA_DATASET,
        "CDC HAICViz: Candidemia",
        "https://data.cdc.gov/d/34p9-h4us",
        topic=topic,
        view_by=view_by,
        series=series,
        limit=limit,
    )


def fetch_cdc_places_county(location_id: str = "", limit: int = 100) -> Dict[str, Any]:
    """CDC PLACES county measures for a five-digit county FIPS code."""
    fips = (location_id or "").strip()
    source = "CDC PLACES: Local Data for Better Health, County Data, 2025 release"
    if not (fips.isdigit() and len(fips) == 5):
        return _unavailable(
            source,
            "MISSING_PARAMETERS",
            "Pass location_id as a five-digit county FIPS code, e.g. 33009.",
        )

    limit = _bounded_limit(limit, 200)
    cache_key = f"cdc_places:{fips}:{limit}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        rows = _get_json(
            f"{_CDC_SOCRATA}/{_CDC_PLACES_COUNTY_DATASET}.json",
            {"locationid": fips, "$limit": str(limit), "$order": "category, measure, data_value_type"},
        )
    except Exception as exc:  # noqa: BLE001
        payload = _unavailable(source, "UPSTREAM_FAILURE", type(exc).__name__)
        _cache_set(cache_key, payload, 300)
        return payload

    measures = []
    for row in rows if isinstance(rows, list) else []:
        try:
            value = float(row["data_value"]) if row.get("data_value") not in (None, "") else None
        except (TypeError, ValueError):
            value = None
        measures.append(
            {
                "year": row.get("year"),
                "state": row.get("stateabbr"),
                "location_name": row.get("locationname"),
                "location_id": row.get("locationid"),
                "category": row.get("category"),
                "measure": row.get("measure"),
                "value_type": row.get("data_value_type"),
                "unit": row.get("data_value_unit"),
                "value": value,
                "low_confidence_limit": row.get("low_confidence_limit"),
                "high_confidence_limit": row.get("high_confidence_limit"),
            }
        )

    payload = {
        "status": "ok",
        "source": source,
        "source_url": "https://data.cdc.gov/d/swc5-untb",
        "dataset_id": _CDC_PLACES_COUNTY_DATASET,
        "fetched_at": _now(),
        "location_id": fips,
        "count": len(measures),
        "note": (
            "PLACES provides model-based population estimates for public-health planning. "
            "CDC cautions against using the estimates to evaluate local program effects."
        ),
        "measures": measures,
    }
    _cache_set(cache_key, payload, 24 * 3600)
    return payload


def fetch_cdc_svi_county(fips: str = "") -> Dict[str, Any]:
    """CDC/ATSDR 2022 Social Vulnerability Index for one U.S. county."""
    county_fips = (fips or "").strip()
    source = "CDC/ATSDR Social Vulnerability Index 2022, U.S. county"
    if not (county_fips.isdigit() and len(county_fips) == 5):
        return _unavailable(
            source,
            "MISSING_PARAMETERS",
            "Pass fips as a five-digit county FIPS code, e.g. 33009.",
        )

    cache_key = f"cdc_svi:{county_fips}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    fields = "FIPS,LOCATION,RPL_THEMES,RPL_THEME1,RPL_THEME2,RPL_THEME3,RPL_THEME4"
    try:
        data = _get_json(
            _CDC_SVI_COUNTY,
            {
                "where": f"FIPS='{county_fips}'",
                "outFields": fields,
                "returnGeometry": "false",
                "f": "json",
            },
        )
        features = (data or {}).get("features") or []
        if not features:
            raise ValueError("county not found")
        attrs = features[0].get("attributes") or {}
    except Exception as exc:  # noqa: BLE001
        payload = _unavailable(source, "UPSTREAM_FAILURE", type(exc).__name__)
        _cache_set(cache_key, payload, 300)
        return payload

    def num(name: str):
        try:
            return float(attrs.get(name)) if attrs.get(name) not in (None, "") else None
        except (TypeError, ValueError):
            return None

    payload = {
        "status": "ok",
        "source": source,
        "source_url": "https://www.atsdr.cdc.gov/place-health/php/svi/",
        "fetched_at": _now(),
        "fips": county_fips,
        "location": attrs.get("LOCATION"),
        "overall_percentile": num("RPL_THEMES"),
        "themes": {
            "socioeconomic_status": num("RPL_THEME1"),
            "household_characteristics": num("RPL_THEME2"),
            "racial_ethnic_minority_status": num("RPL_THEME3"),
            "housing_transportation": num("RPL_THEME4"),
        },
        "note": (
            "SVI is a relative vulnerability index for public-health planning. "
            "Use it to inform representation and access questions, not individual risk scoring."
        ),
    }
    _cache_set(cache_key, payload, 24 * 3600)
    return payload


def cdc_data_status() -> Dict[str, Any]:
    """Availability of configured CDC feeds, cached for five minutes."""
    cache_key = "cdc_source_health"
    health = _cache_get(cache_key)
    if health is None:
        health = {
            "hai_isa": _probe(f"{_CDC_SOCRATA}/{_CDC_ISA_DATASET}.json", {"$limit": "1"}),
            "candidemia": _probe(f"{_CDC_SOCRATA}/{_CDC_CANDIDEMIA_DATASET}.json", {"$limit": "1"}),
            "places_county": _probe(f"{_CDC_SOCRATA}/{_CDC_PLACES_COUNTY_DATASET}.json", {"$limit": "1"}),
            "svi_county": _probe(
                _CDC_SVI_COUNTY,
                {"where": "1=1", "outFields": "FIPS", "resultRecordCount": "1", "returnGeometry": "false", "f": "json"},
            ),
        }
        _cache_set(cache_key, health, 300)

    definitions = [
        ("hai_isa", "CDC HAICViz invasive Staphylococcus aureus (MRSA/MSSA)", _CDC_ISA_DATASET, "/api/live/cdc/hai-isa"),
        ("candidemia", "CDC HAICViz candidemia and drug resistance", _CDC_CANDIDEMIA_DATASET, "/api/live/cdc/candidemia"),
        ("places_county", "CDC PLACES county public-health measures", _CDC_PLACES_COUNTY_DATASET, "/api/live/cdc/places?location_id="),
        ("svi_county", "CDC/ATSDR Social Vulnerability Index 2022", "CDC_ATSDR_SVI_2022_USA", "/api/live/cdc/svi?fips="),
    ]
    sources = []
    for source_id, label, dataset_id, endpoint in definitions:
        probe = health[source_id]
        sources.append(
            {
                "id": source_id,
                "label": label,
                "credential_required": False,
                "dataset_id": dataset_id,
                "endpoint": endpoint,
                "state": probe["state"],
                "reason": probe["reason"],
                "checked_at": _now(),
            }
        )
    return {"status": "ok", "fetched_at": _now(), "sources": sources}

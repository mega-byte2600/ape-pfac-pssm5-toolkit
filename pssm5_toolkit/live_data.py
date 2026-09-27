"""Live public-data fetchers for the APE PFAC leadership toolkit.

All sources are free, public, aggregate data with no PHI. Every fetcher:
- uses only the Python standard library,
- enforces a short timeout,
- caches successful responses in memory with a TTL,
- never raises to the caller: on failure it returns a structured
  ``status: "unavailable"`` payload with a reason code.

Source attribution is included in every payload so any visual built on
this data can state its source.
"""

from __future__ import annotations

import json
import os
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

_TIMEOUT_SECONDS = 12
_USER_AGENT = "ape-pfac-pssm5-toolkit/0.1 (MPH Applied Practice Experience)"

# facility_id -> display name for hospitals tracked by the toolkit
TRACKED_FACILITIES = {
    "300003": "Mary Hitchcock Memorial Hospital (Dartmouth Health)",
}

# In-memory TTL cache: key -> (expires_at, payload)
_CACHE: Dict[str, Any] = {}


def _cache_get(key: str) -> Optional[Dict[str, Any]]:
    entry = _CACHE.get(key)
    if entry and entry[0] > time.time():
        return entry[1]
    _CACHE.pop(key, None)
    return None


def _cache_set(key: str, payload: Dict[str, Any], ttl_seconds: int) -> None:
    _CACHE[key] = (time.time() + ttl_seconds, payload)


def _get_json(url: str, params: Optional[Dict[str, str]] = None) -> Any:
    """GET a URL and parse JSON. Raises on any failure."""
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
    with urllib.request.urlopen(request, timeout=_TIMEOUT_SECONDS) as response:
        raw = response.read()
    return json.loads(raw.decode("utf-8"))


def _unavailable(source: str, reason_code: str, detail: str = "") -> Dict[str, Any]:
    payload: Dict[str, Any] = {
        "status": "unavailable",
        "source": source,
        "reason_code": reason_code,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    if detail:
        payload["detail"] = detail
    return payload


# ---------------------------------------------------------------------------
# CMS HCAHPS: hospital patient-experience scores + national benchmarks
# ---------------------------------------------------------------------------

_CMS_HOSPITAL_DATASET = "dgck-syfz"
_CMS_NATIONAL_DATASET = "99ue-w85f"
_CMS_BASE = "https://data.cms.gov/provider-data/api/1/datastore/query"

# HCAHPS composite / global measures most relevant to PFAC work, with the
# "top-box" answer variant (patients answering "Always" / 9-10).
HCAHPS_FOCUS_MEASURES = {
    "H_COMP_1_A_P": "Nurses always communicated well",
    "H_COMP_2_A_P": "Doctors always communicated well",
    "H_COMP_3_A_P": "Always received help when wanted",
    "H_COMP_5_A_P": "Staff always explained medicines",
    "H_COMP_6_Y_P": "Always quiet at night",
    "H_CLEAN_HSP_A_P": "Room/bathroom always clean",
    "H_HSP_RATING_9_10": "Rated hospital 9 or 10",
    "H_RECMND_DY": "Would definitely recommend",
}


def fetch_hcahps(facility_id: str = "300003") -> Dict[str, Any]:
    """Live HCAHPS scores for a tracked facility vs national benchmarks.

    Source: CMS Provider Data Catalog (Socrata API, no key required).
    All values are public CMS-published aggregates, not project findings.
    """
    cache_key = f"hcahps:{facility_id}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    source = "CMS Provider Data Catalog: HCAHPS (data.cms.gov)"
    try:
        facility_rows = _get_json(
            f"{_CMS_BASE}/{_CMS_HOSPITAL_DATASET}/0",
            {
                "limit": "500",
                "conditions[0][property]": "facility_id",
                "conditions[0][value]": facility_id,
                "conditions[0][operator]": "=",
            },
        )
        national_rows = _get_json(
            f"{_CMS_BASE}/{_CMS_NATIONAL_DATASET}/0",
            {"limit": "500"},
        )
    except Exception as exc:
        payload = _unavailable(source, "UPSTREAM_OR_AUTH_FAILURE", type(exc).__name__)
        _cache_set(cache_key, payload, 300)
        return payload

    def _index(rows: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
        index: Dict[str, Dict[str, Any]] = {}
        for row in rows or []:
            mid = row.get("hcahps_measure_id")
            if mid in HCAHPS_FOCUS_MEASURES:
                index[mid] = row
        return index

    facility = _index((facility_rows or {}).get("results", []))
    national = _index((national_rows or {}).get("results", []))

    measures = []
    for measure_id, label in HCAHPS_FOCUS_MEASURES.items():
        f = facility.get(measure_id, {})
        n = national.get(measure_id, {})
        measures.append(
            {
                "measure_id": measure_id,
                "label": label,
                "question": f.get("hcahps_question") or n.get("hcahps_question") or "",
                "facility_percent": f.get("hcahps_answer_percent"),
                "national_percent": n.get("hcahps_answer_percent"),
                "facility_star_rating": f.get("patient_survey_star_rating"),
                "period_start": f.get("start_date") or n.get("start_date"),
                "period_end": f.get("end_date") or n.get("end_date"),
            }
        )

    facility_name = TRACKED_FACILITIES.get(facility_id, facility_id)
    payload = {
        "status": "ok",
        "source": source,
        "source_urls": [
            f"https://data.cms.gov/provider-data/dataset/{_CMS_HOSPITAL_DATASET}",
            f"https://data.cms.gov/provider-data/dataset/{_CMS_NATIONAL_DATASET}",
        ],
        "facility_id": facility_id,
        "facility_name": facility_name,
        "note": (
            "Public CMS-published HCAHPS aggregates for context and benchmarking. "
            "Not a project finding and not a claim about PFAC effectiveness."
        ),
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "measures": measures,
    }
    _cache_set(cache_key, payload, 6 * 3600)
    return payload


# ---------------------------------------------------------------------------
# PubMed: new PFAC / patient-engagement evidence surveillance
# ---------------------------------------------------------------------------

_PUBMED_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
_PUBMED_ESUMMARY = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"

EVIDENCE_WATCH_QUERIES = {
    "pfac_systematic_reviews": (
        "(patient family advisory council[All Fields] OR patient advisor[All Fields]) "
        "AND (systematic review[Publication Type] OR meta-analysis[Publication Type])"
    ),
    "engagement_outcomes": (
        "(patient engagement[MeSH Terms] OR patient participation[MeSH Terms]) "
        "AND (patient safety[MeSH Terms] OR quality improvement[MeSH Terms]) "
        "AND (2024:3000[Date - Publication])"
    ),
}


def fetch_evidence_watch() -> Dict[str, Any]:
    """Recent PubMed-indexed PFAC / engagement evidence.

    Returns titles, journals, dates, and PubMed links for candidate
    bibliography refresh. Does not assess quality: inclusion in results
    is not an endorsement of findings.
    """
    cache_key = "evidence_watch"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    source = "PubMed / NCBI E-utilities (pubmed.ncbi.nlm.nih.gov)"
    watches = []
    try:
        for watch_id, term in EVIDENCE_WATCH_QUERIES.items():
            search = _get_json(
                _PUBMED_ESEARCH,
                {
                    "db": "pubmed",
                    "term": term,
                    "retmode": "json",
                    "retmax": "10",
                    "sort": "date",
                },
            )
            result = (search or {}).get("esearchresult", {})
            id_list = result.get("idlist", [])
            total = result.get("count", "0")
            articles = []
            if id_list:
                summary = _get_json(
                    _PUBMED_ESUMMARY,
                    {
                        "db": "pubmed",
                        "id": ",".join(id_list),
                        "retmode": "json",
                    },
                )
                docs = (summary or {}).get("result", {})
                for pmid in id_list:
                    doc = docs.get(pmid, {})
                    if not doc or pmid == "uids":
                        continue
                    articles.append(
                        {
                            "pmid": pmid,
                            "title": doc.get("title"),
                            "journal": doc.get("source"),
                            "pubdate": doc.get("pubdate"),
                            "authors": [
                                a.get("name") for a in (doc.get("authors") or [])[:5]
                            ],
                            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                        }
                    )
            watches.append(
                {
                    "watch_id": watch_id,
                    "query": term,
                    "total_results": total,
                    "recent": articles,
                }
            )
    except Exception as exc:
        payload = _unavailable(source, "UPSTREAM_OR_AUTH_FAILURE", type(exc).__name__)
        _cache_set(cache_key, payload, 300)
        return payload

    payload = {
        "status": "ok",
        "source": source,
        "note": (
            "Candidate literature for bibliography review. Search hits are not "
            "quality-appraised and are not project findings."
        ),
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "watches": watches,
    }
    _cache_set(cache_key, payload, 24 * 3600)
    return payload


# ---------------------------------------------------------------------------
# Census ACS: Upper Valley municipality refresh (requires free API key)
# ---------------------------------------------------------------------------

# 19 municipalities from web/upper-valley-local-analysis.csv with
# (state FIPS, county FIPS, place description) for ACS county-subdivision lookup.
UPPER_VALLEY_PLACES = [
    ("Canaan", "33", "009"), ("Dorchester", "33", "009"), ("Enfield", "33", "009"),
    ("Grafton", "33", "009"), ("Grantham", "33", "009"), ("Hanover", "33", "009"),
    ("Lebanon", "33", "009"), ("Lyme", "33", "009"), ("Orange", "33", "009"),
    ("Orford", "33", "009"), ("Piermont", "33", "009"), ("Plainfield", "33", "009"),
    ("Fairlee", "50", "017"), ("Hartford", "50", "027"), ("Hartland", "50", "027"),
    ("Norwich", "50", "027"), ("Sharon", "50", "027"), ("Thetford", "50", "017"),
    ("Woodstock", "50", "027"),
]


def fetch_census_upper_valley() -> Dict[str, Any]:
    """ACS 5-year demographics for the 19 Upper Valley municipalities.

    Requires the free Census API key (CENSUS_API_KEY env var). Without it,
    returns status "unavailable" with reason CREDENTIALS_NOT_CONFIGURED and
    the project keeps serving its static CHNA-derived CSV.
    """
    cache_key = "census_upper_valley"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    source = "U.S. Census Bureau American Community Survey 5-year (api.census.gov)"
    api_key = os.environ.get("CENSUS_API_KEY", "").strip()
    if not api_key:
        payload = _unavailable(
            source,
            "CREDENTIALS_NOT_CONFIGURED",
            "Set CENSUS_API_KEY (free at api.census.gov/data/key_signup.html) to enable live refresh.",
        )
        _cache_set(cache_key, payload, 3600)
        return payload

    try:
        collected: Dict[str, Dict[str, Any]] = {}
        # Group places by (state, county) to minimize requests.
        groups: Dict[tuple, List[str]] = {}
        for name, state, county in UPPER_VALLEY_PLACES:
            groups.setdefault((state, county), []).append(name)
        for (state, county), _names in groups.items():
            data = _get_json(
                "https://api.census.gov/data/2023/acs/acs5",
                {
                    "get": "NAME,B17001_001E,B17001_002E,B01003_001E",
                    "for": "county subdivision:*",
                    "in": f"state:{state} county:{county}",
                    "key": api_key,
                },
            )
            header, rows = data[0], data[1:]
            idx = {col: i for i, col in enumerate(header)}
            for row in rows:
                name_full = row[idx["NAME"]]
                town = name_full.split(",")[0].replace(" town", "").replace(" city", "")
                collected[town] = {
                    "census_name": name_full,
                    "poverty_universe": row[idx["B17001_001E"]],
                    "poverty_count": row[idx["B17001_002E"]],
                    "population": row[idx["B01003_001E"]],
                }
        municipalities = []
        for name, _s, _c in UPPER_VALLEY_PLACES:
            municipalities.append({"municipality": name, **collected.get(name, {})})
    except Exception as exc:
        payload = _unavailable(source, "UPSTREAM_OR_AUTH_FAILURE", type(exc).__name__)
        _cache_set(cache_key, payload, 300)
        return payload

    payload = {
        "status": "ok",
        "source": source,
        "note": (
            "Live ACS 5-year estimates for context. Poverty/disability/age "
            "band calculations remain the project's own reproducible method "
            "in web/upper-valley-local-analysis.csv."
        ),
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "municipalities": municipalities,
    }
    _cache_set(cache_key, payload, 24 * 3600)
    return payload


def live_data_status() -> Dict[str, Any]:
    """Summary of live-data source availability (no fetches)."""
    census_key = bool(os.environ.get("CENSUS_API_KEY", "").strip())
    return {
        "status": "ok",
        "sources": [
            {
                "id": "hcahps",
                "label": "CMS HCAHPS hospital patient-experience scores",
                "credential_required": False,
                "endpoint": "/api/live/hcahps",
            },
            {
                "id": "evidence_watch",
                "label": "PubMed PFAC evidence surveillance",
                "credential_required": False,
                "endpoint": "/api/live/evidence-watch",
            },
            {
                "id": "census_upper_valley",
                "label": "Census ACS Upper Valley demographics",
                "credential_required": True,
                "configured": census_key,
                "endpoint": "/api/live/census-upper-valley",
            },
        ],
    }

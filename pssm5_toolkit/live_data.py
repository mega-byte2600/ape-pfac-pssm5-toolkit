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

# facility_id -> display name, seeded with one example. Leaders can query
# any CMS-tracked facility by passing facility_id to /api/live/hcahps
# or using /api/live/facility-search to find theirs.
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


def search_facilities(name: str = "", state: str = "", limit: int = 20) -> Dict[str, Any]:
    """Find CMS-tracked facilities by name and/or state.

    Leaders use this to find their hospital's facility_id, then pass it to
    /api/live/hcahps for their own patient-experience benchmark.
    """
    cache_key = f"facility_search:{name}:{state}:{limit}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    source = "CMS Provider Data Catalog: HCAHPS (data.cms.gov)"
    try:
        params: Dict[str, str] = {"limit": str(min(max(limit, 1), 50))}
        idx = 0
        if name:
            params[f"conditions[{idx}][property]"] = "facility_name"
            params[f"conditions[{idx}][value]"] = name
            params[f"conditions[{idx}][operator]"] = "="
            idx += 1
        if state:
            params[f"conditions[{idx}][property]"] = "state"
            params[f"conditions[{idx}][value]"] = state.upper()
            params[f"conditions[{idx}][operator]"] = "="
            idx += 1
        data = _get_json(f"{_CMS_BASE}/{_CMS_HOSPITAL_DATASET}/0", params)
    except Exception as exc:
        payload = _unavailable(source, "UPSTREAM_OR_AUTH_FAILURE", type(exc).__name__)
        _cache_set(cache_key, payload, 300)
        return payload

    seen: Dict[str, Dict[str, Any]] = {}
    for row in (data or {}).get("results", []):
        fid = row.get("facility_id")
        if fid and fid not in seen:
            seen[fid] = {
                "facility_id": fid,
                "facility_name": row.get("facility_name"),
                "city": row.get("citytown"),
                "state": row.get("state"),
                "county": row.get("countyparish"),
            }

    payload = {
        "status": "ok",
        "source": source,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(seen),
        "facilities": sorted(seen.values(), key=lambda f: f["facility_name"] or ""),
    }
    _cache_set(cache_key, payload, 24 * 3600)
    return payload


def fetch_hcahps(facility_id: str = "300003") -> Dict[str, Any]:
    """Live HCAHPS scores for any CMS-tracked facility vs national benchmarks.

    Leaders pass their own facility_id (found via /api/live/facility-search)
    to benchmark their hospital's patient-experience scores against national
    averages — the "measure what matters" input for PFAC effectiveness work.

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


def format_ama11(doc: Dict[str, Any]) -> str:
    """Format a PubMed esummary doc as an AMA 11th-edition journal citation.

    Pattern: Authors. Title. Journal. Year;Volume(Issue):pages. doi:xx
    Lists the first 3 authors then et al. when more than 6 are present,
    per AMA 11. Uses the journal name as returned by PubMed.
    """
    authors = [a.get("name", "") for a in (doc.get("authors") or []) if a.get("name")]
    if len(authors) > 6:
        author_str = ", ".join(authors[:3]) + ", et al"
    elif authors:
        author_str = ", ".join(authors)
    else:
        author_str = ""

    title = (doc.get("title") or "").rstrip(".")
    journal = doc.get("source") or ""
    pubdate = doc.get("pubdate") or ""
    year = pubdate.split()[0] if pubdate else ""
    volume = doc.get("volume") or ""
    issue = doc.get("issue") or ""
    pages = doc.get("pages") or ""
    doi = ""
    for aid in doc.get("articleids") or []:
        if aid.get("idtype") == "doi":
            doi = aid.get("value", "")
            break

    parts = []
    if author_str:
        parts.append(author_str + ".")
    if title:
        parts.append(title + ".")
    if journal:
        parts.append(journal + ".")
    vol_issue = volume
    if issue:
        vol_issue += f"({issue})"
    tail = ";".join(p for p in [year, vol_issue] if p)
    if pages:
        tail += f":{pages}" if tail else pages
    if tail:
        parts.append(tail + ".")
    if doi:
        parts.append(f"doi:{doi}")
    return " ".join(parts)

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
                            "volume": doc.get("volume"),
                            "issue": doc.get("issue"),
                            "pages": doc.get("pages"),
                            "authors": [
                                a.get("name") for a in (doc.get("authors") or [])[:6]
                            ],
                            "author_count": len(doc.get("authors") or []),
                            "ama11_citation": format_ama11(doc),
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
# Census ACS: service-area demographics for any county (requires free key)
# ---------------------------------------------------------------------------

# Example: the 19 Upper Valley municipalities from the one-time environmental
# scan (web/upper-valley-local-analysis.csv), kept as a usage example.
# Leaders pass their own state/county FIPS to /api/live/census-demographics.
UPPER_VALLEY_EXAMPLE = {"state_fips": "33", "county_fips": "009", "label": "Grafton County, NH"}


def fetch_census_demographics(
    state_fips: str = "", county_fips: str = ""
) -> Dict[str, Any]:
    """ACS 5-year demographics (population, poverty, disability proxy) for all
    county subdivisions in a given county.

    Leaders use this for the population-context input to PFAC recruitment and
    representation design in their own service area.

    Requires the free Census API key (CENSUS_API_KEY env var). Without it,
    returns status "unavailable" with reason CREDENTIALS_NOT_CONFIGURED.
    """
    cache_key = f"census_demographics:{state_fips}:{county_fips}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    source = "U.S. Census Bureau American Community Survey 5-year (api.census.gov)"
    api_key = os.environ.get("CENSUS_API_KEY", "").strip()
    if not api_key:
        payload = _unavailable(
            source,
            "CREDENTIALS_NOT_CONFIGURED",
            "Set CENSUS_API_KEY (free at api.census.gov/data/key_signup.html) to enable.",
        )
        _cache_set(cache_key, payload, 3600)
        return payload
    if not state_fips or not county_fips:
        payload = _unavailable(
            source,
            "MISSING_PARAMETERS",
            "Pass state_fips and county_fips query parameters (e.g. state_fips=33&county_fips=009).",
        )
        _cache_set(cache_key, payload, 3600)
        return payload

    try:
        data = _get_json(
            "https://api.census.gov/data/2023/acs/acs5",
            {
                "get": "NAME,B17001_001E,B17001_002E,B01003_001E",
                "for": "county subdivision:*",
                "in": f"state:{state_fips} county:{county_fips}",
                "key": api_key,
            },
        )
        header, rows = data[0], data[1:]
        idx = {col: i for i, col in enumerate(header)}
        subdivisions = []
        for row in rows:
            universe = row[idx["B17001_001E"]]
            poor = row[idx["B17001_002E"]]
            try:
                poverty_pct = round(100 * int(poor) / int(universe), 1) if int(universe) else None
            except (ValueError, TypeError):
                poverty_pct = None
            subdivisions.append(
                {
                    "name": row[idx["NAME"]].split(",")[0],
                    "population": row[idx["B01003_001E"]],
                    "poverty_percent": poverty_pct,
                }
            )
        subdivisions.sort(key=lambda r: r["name"] or "")
    except Exception as exc:
        payload = _unavailable(source, "UPSTREAM_OR_AUTH_FAILURE", type(exc).__name__)
        _cache_set(cache_key, payload, 300)
        return payload

    payload = {
        "status": "ok",
        "source": source,
        "note": (
            "Live ACS 5-year estimates for local population context. "
            "Interpretation and PFAC design decisions remain the leader's own work."
        ),
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "state_fips": state_fips,
        "county_fips": county_fips,
        "subdivisions": subdivisions,
    }
    _cache_set(cache_key, payload, 24 * 3600)
    return payload


def fetch_census_upper_valley() -> Dict[str, Any]:
    """Backwards-compatible alias: Upper Valley example from the one-time scan."""
    return fetch_census_demographics(
        UPPER_VALLEY_EXAMPLE["state_fips"], UPPER_VALLEY_EXAMPLE["county_fips"]
    )


def live_data_status() -> Dict[str, Any]:
    """Summary of live-data source availability (no fetches)."""
    census_key = bool(os.environ.get("CENSUS_API_KEY", "").strip())
    return {
        "status": "ok",
        "sources": [
            {
                "id": "facility_search",
                "label": "CMS facility lookup by name/state",
                "credential_required": False,
                "endpoint": "/api/live/facility-search?name=&state=",
            },
            {
                "id": "hcahps",
                "label": "CMS HCAHPS patient-experience scores for any facility vs national benchmarks",
                "credential_required": False,
                "endpoint": "/api/live/hcahps?facility_id=",
            },
            {
                "id": "evidence_watch",
                "label": "PubMed PFAC evidence surveillance",
                "credential_required": False,
                "endpoint": "/api/live/evidence-watch",
            },
            {
                "id": "census_demographics",
                "label": "Census ACS demographics for any county's subdivisions",
                "credential_required": True,
                "configured": census_key,
                "endpoint": "/api/live/census-demographics?state_fips=&county_fips=",
            },
        ],
    }

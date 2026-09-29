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

import http.client
import json
import os
import random
import re
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional

_TIMEOUT_SECONDS = 12
_USER_AGENT = "ape-pfac-pssm5-toolkit/0.1 (MPH Applied Practice Experience)"

# Retry policy for transient upstream failures (timeouts, 429, 5xx).
# 4xx other than 429 is not retried: the request itself is wrong.
_MAX_RETRIES = 2

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


def _is_transient(exc: BaseException) -> bool:
    """True for failures worth retrying: timeouts, disconnects, 429, 5xx."""
    if isinstance(exc, urllib.error.HTTPError):
        return exc.code == 429 or exc.code >= 500
    return isinstance(
        exc,
        (
            urllib.error.URLError,
            TimeoutError,
            ConnectionError,
            http.client.HTTPException,
        ),
    )


def _get_json(
    url: str, params: Optional[Dict[str, str]] = None, timeout: int = _TIMEOUT_SECONDS
) -> Any:
    """GET a URL and parse JSON, with backoff on transient failures.

    Raises on any failure after retries are exhausted.
    """
    if params:
        url = url + "?" + urllib.parse.urlencode(params)
    last_exc: Optional[BaseException] = None
    for attempt in range(_MAX_RETRIES + 1):
        try:
            request = urllib.request.Request(url, headers={"User-Agent": _USER_AGENT})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                raw = response.read()
            return json.loads(raw.decode("utf-8"))
        except Exception as exc:  # noqa: BLE001 - classified below
            if not _is_transient(exc):
                raise
            last_exc = exc
        if attempt < _MAX_RETRIES:
            time.sleep(2**attempt + random.uniform(0, 0.5))
    assert last_exc is not None
    raise last_exc


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


def _rank_facilities(
    facilities: List[Dict[str, Any]], name_query: str
) -> List[Dict[str, Any]]:
    """Best matches first: exact, then starts-with, then contains, then name."""
    query = (name_query or "").strip().casefold()

    def sort_key(facility: Dict[str, Any]):
        name = (facility.get("facility_name") or "").casefold()
        if query and name == query:
            rank = 0
        elif query and name.startswith(query):
            rank = 1
        elif query and name:
            rank = 2
        else:
            rank = 3
        return (rank, name)

    return sorted(facilities, key=sort_key)


def search_facilities(name: str = "", state: str = "", limit: int = 20) -> Dict[str, Any]:
    """Find CMS-tracked facilities by name and/or state.

    Leaders use this to find their hospital's facility_id, then pass it to
    /api/live/hcahps for their own patient-experience benchmark.

    Name matching is partial and case-insensitive ("Hitchcock" finds
    "MARY HITCHCOCK MEMORIAL HOSPITAL"); results are ranked exact first,
    then starts-with, then contains. CMS returns one row per measure, so
    rows are de-duplicated by facility_id before ranking.
    """
    cache_key = f"facility_search:{name}:{state}:{limit}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    source = "CMS Provider Data Catalog: HCAHPS (data.cms.gov)"
    limit = min(max(limit, 1), 50)
    try:
        params: Dict[str, str] = {}
        idx = 0
        if name:
            # Escape LIKE wildcards in user input, then match any substring.
            safe = re.sub(r"[%_]", "", name.strip())
            params[f"conditions[{idx}][property]"] = "facility_name"
            params[f"conditions[{idx}][value]"] = f"%{safe}%"
            params[f"conditions[{idx}][operator]"] = "like"
            idx += 1
        if state:
            params[f"conditions[{idx}][property]"] = "state"
            params[f"conditions[{idx}][value]"] = state.upper()
            params[f"conditions[{idx}][operator]"] = "="
            idx += 1
        # One row per measure per facility: over-fetch rows, dedup to facilities.
        params["limit"] = str(min(limit * 12, 600))
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

    facilities = _rank_facilities(list(seen.values()), name)[:limit]
    payload = {
        "status": "ok",
        "source": source,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "count": len(facilities),
        "facilities": facilities,
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
# ClinicalTrials.gov: research engagement opportunities at the leader's facility
# ---------------------------------------------------------------------------

_CTG_BASE = "https://clinicaltrials.gov/api/v2/studies"
_CTG_SOURCE = "ClinicalTrials.gov (U.S. National Library of Medicine)"

# Generic words in hospital names that make poor search tokens.
_TRIAL_NAME_STOPWORDS = frozenset(
    {
        "hospital", "medical", "center", "centre", "memorial", "health",
        "healthcare", "system", "clinic", "regional", "general", "community",
        "university", "saint", "st", "the", "of", "and",
    }
)

# Two-letter code -> full name, to match ClinicalTrials.gov location states
# against the CMS two-letter state codes the UI already carries.
_US_STATE_NAMES = {
    "AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas",
    "CA": "California", "CO": "Colorado", "CT": "Connecticut",
    "DE": "Delaware", "DC": "District of Columbia", "FL": "Florida",
    "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho", "IL": "Illinois",
    "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky",
    "LA": "Louisiana", "ME": "Maine", "MD": "Maryland",
    "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
    "MS": "Mississippi", "MO": "Missouri", "MT": "Montana",
    "NE": "Nebraska", "NV": "Nevada", "NH": "New Hampshire",
    "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York",
    "NC": "North Carolina", "ND": "North Dakota", "OH": "Ohio",
    "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
    "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota",
    "TN": "Tennessee", "TX": "Texas", "UT": "Utah", "VT": "Vermont",
    "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
    "WI": "Wisconsin", "WY": "Wyoming",
    "PR": "Puerto Rico", "GU": "Guam", "VI": "Virgin Islands",
}


def _normalize_state(state: str) -> str:
    """Two-letter code or full name -> full name, for location matching."""
    s = (state or "").strip()
    if len(s) == 2:
        return _US_STATE_NAMES.get(s.upper(), s)
    return s


# Trial statuses where advisor input matters most, in display order.
_TRIAL_STATUS_RANK = {
    "RECRUITING": 0,
    "NOT_YET_RECRUITING": 1,
    "ACTIVE_NOT_RECRUITING": 2,
    "ENROLLING_BY_INVITATION": 2,
}


def _trial_search_token(facility_name: str) -> str:
    """Pick the most distinctive word of a facility name for trial search."""
    words = re.findall(r"[A-Za-z0-9]+", facility_name or "")
    candidates = [
        w for w in words if len(w) >= 4 and w.lower() not in _TRIAL_NAME_STOPWORDS
    ]
    if not candidates:
        candidates = [w for w in words if len(w) >= 3]
    if not candidates:
        return ""
    return max(candidates, key=len)


def fetch_trials(
    facility_name: str = "", state: str = "", limit: int = 10
) -> Dict[str, Any]:
    """Active clinical trials listing the leader's facility as a location.

    PFACs commonly advise on research: recruiting studies are where advisor
    input on recruitment materials and participant experience counts most.
    This gives leaders their institution's research footprint as an input to
    feedback-to-action planning and new-leader onboarding — informational
    only; whether advisors engage with any study is the leader's decision.

    Source: ClinicalTrials.gov API v2 (no key required). Only studies with a
    location whose facility name matches the search are returned; the API's
    own area search is broad, so locations are filtered client-side.
    """
    cache_key = f"trials:{facility_name}:{state}:{limit}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    token = _trial_search_token(facility_name)
    if not token:
        payload = _unavailable(
            _CTG_SOURCE,
            "MISSING_PARAMETERS",
            "Pass a facility_name (e.g. from /api/live/facility-search).",
        )
        _cache_set(cache_key, payload, 3600)
        return payload
    limit = min(max(limit, 1), 25)
    want_state = _normalize_state(state).lower()

    try:
        data = _get_json(
            _CTG_BASE,
            {
                "query.term": f"AREA[LocationFacility]{token}",
                "pageSize": "25",
                "fields": ",".join(
                    [
                        "NCTId",
                        "BriefTitle",
                        "OverallStatus",
                        "StartDate",
                        "Phase",
                        "StudyType",
                        "Condition",
                        "LocationFacility",
                        "LocationCity",
                        "LocationState",
                    ]
                ),
            },
        )
    except Exception as exc:
        payload = _unavailable(_CTG_SOURCE, "UPSTREAM_OR_AUTH_FAILURE", type(exc).__name__)
        _cache_set(cache_key, payload, 300)
        return payload

    token_lower = token.lower()
    studies = []
    for entry in (data or {}).get("studies", []):
        ps = entry.get("protocolSection") or {}
        ident = ps.get("identificationModule") or {}
        status_mod = ps.get("statusModule") or {}
        locations = (ps.get("contactsLocationsModule") or {}).get("locations") or []
        matching = [
            {
                "facility": loc.get("facility"),
                "city": loc.get("city"),
                "state": loc.get("state"),
            }
            for loc in locations
            if token_lower in (loc.get("facility") or "").lower()
            and (not want_state or (loc.get("state") or "").lower() == want_state)
        ]
        if not matching:
            continue
        nct_id = ident.get("nctId") or ""
        status = status_mod.get("overallStatus") or ""
        conditions = ps.get("conditionsModule") or {}
        studies.append(
            {
                "nct_id": nct_id,
                "title": ident.get("briefTitle"),
                "status": status,
                "start_date": (status_mod.get("startDateStruct") or {}).get("date"),
                "phase": ", ".join((ps.get("designModule") or {}).get("phases") or []),
                "study_type": (ps.get("designModule") or {}).get("studyType"),
                "conditions": conditions.get("keywords") or [],
                "locations": matching,
                "url": f"https://clinicaltrials.gov/study/{nct_id}" if nct_id else "",
            }
        )

    studies.sort(
        key=lambda s: (
            _TRIAL_STATUS_RANK.get(s["status"], 3),
            s["title"] or "",
        )
    )
    studies = studies[:limit]

    payload = {
        "status": "ok",
        "source": _CTG_SOURCE,
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "facility_name": facility_name,
        "search_token": token,
        "count": len(studies),
        "note": (
            "Trial listings are informational context for PFAC research-engagement "
            "planning. Inclusion is not an endorsement of any study."
        ),
        "studies": studies,
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


def _probe_source(name: str, url: str, params: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
    """Cheap liveness check for one source: live, degraded (slow), or unavailable."""
    started = time.time()
    try:
        _get_json(url, params, timeout=6)
    except Exception as exc:  # noqa: BLE001 - surfaced as the reason
        return {"state": "unavailable", "reason": type(exc).__name__}
    elapsed = time.time() - started
    if elapsed > 4:
        return {"state": "degraded", "reason": f"slow response ({elapsed:.1f}s)"}
    return {"state": "live", "reason": ""}


def live_data_status() -> Dict[str, Any]:
    """Per-source availability: live, degraded, unavailable (with reason),
    or needs_key. Keyless sources get a cheap live probe, cached 5 minutes;
    nothing here fetches full datasets."""
    cached = _cache_get("source_health")
    if cached is not None:
        health = cached
    else:
        health = {
            "facility_search": _probe_source(
                "cms", f"{_CMS_BASE}/{_CMS_HOSPITAL_DATASET}/0", {"limit": "1"}
            ),
            "hcahps": _probe_source(
                "cms", f"{_CMS_BASE}/{_CMS_NATIONAL_DATASET}/0", {"limit": "1"}
            ),
            "evidence_watch": _probe_source(
                "pubmed",
                _PUBMED_ESEARCH,
                {"db": "pubmed", "term": "patient engagement", "retmode": "json", "retmax": "0"},
            ),
            "trials": _probe_source(
                "clinicaltrials",
                _CTG_BASE,
                {"query.term": "AREA[LocationFacility]hospital", "pageSize": "1",
                 "fields": "NCTId"},
            ),
        }
        _cache_set("source_health", health, 300)

    census_key = bool(os.environ.get("CENSUS_API_KEY", "").strip())
    census_health = (
        {"state": "live", "reason": ""}
        if census_key
        else {"state": "needs_key", "reason": "Set CENSUS_API_KEY to enable"}
    )
    checked_at = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    sources = [
        {
            "id": "facility_search",
            "label": "CMS facility lookup by name/state",
            "credential_required": False,
            "endpoint": "/api/live/facility-search?name=&state=",
            "state": health["facility_search"]["state"],
            "reason": health["facility_search"]["reason"],
            "checked_at": checked_at,
        },
        {
            "id": "hcahps",
            "label": "CMS HCAHPS patient-experience scores for any facility vs national benchmarks",
            "credential_required": False,
            "endpoint": "/api/live/hcahps?facility_id=",
            "state": health["hcahps"]["state"],
            "reason": health["hcahps"]["reason"],
            "checked_at": checked_at,
        },
        {
            "id": "evidence_watch",
            "label": "PubMed PFAC evidence surveillance",
            "credential_required": False,
            "endpoint": "/api/live/evidence-watch",
            "state": health["evidence_watch"]["state"],
            "reason": health["evidence_watch"]["reason"],
            "checked_at": checked_at,
        },
        {
            "id": "trials",
            "label": "ClinicalTrials.gov research engagement at your facility",
            "credential_required": False,
            "endpoint": "/api/live/trials?facility_name=&state=",
            "state": health["trials"]["state"],
            "reason": health["trials"]["reason"],
            "checked_at": checked_at,
        },
        {
            "id": "census_demographics",
            "label": "Census ACS demographics for any county's subdivisions",
            "credential_required": True,
            "configured": census_key,
            "endpoint": "/api/live/census-demographics?state_fips=&county_fips=",
            "state": census_health["state"],
            "reason": census_health["reason"],
            "checked_at": checked_at,
        },
    ]
    return {"status": "ok", "sources": sources}

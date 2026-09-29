"""Ad-hoc PubMed evidence search for the APE PFAC leadership toolkit.

Uses the same PubMed E-utilities client and AMA 11 formatter as the preset
evidence watch. Public, keyless, aggregate literature metadata only.
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

from .live_data import (
    _PUBMED_ESEARCH,
    _PUBMED_ESUMMARY,
    _cache_get,
    _cache_set,
    _get_json,
    _unavailable,
    format_ama11,
)

_SOURCE = "PubMed / NCBI E-utilities (pubmed.ncbi.nlm.nih.gov)"


def _articles_for_term(term: str, limit: int) -> Dict[str, Any]:
    search = _get_json(
        _PUBMED_ESEARCH,
        {
            "db": "pubmed",
            "term": term,
            "retmode": "json",
            "retmax": str(limit),
            "sort": "date",
        },
    )
    result = (search or {}).get("esearchresult", {})
    id_list: List[str] = result.get("idlist", []) or []
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
                    "authors": [a.get("name") for a in (doc.get("authors") or [])[:6]],
                    "author_count": len(doc.get("authors") or []),
                    "ama11_citation": format_ama11(doc),
                    "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
                }
            )
    return {"total_results": total, "recent": articles}


def fetch_evidence_search(term: str, limit: int = 10) -> Dict[str, Any]:
    """Search PubMed for a leader-supplied topic; never raises to callers."""
    clean = " ".join((term or "").strip().split())[:200]
    if not clean:
        return _unavailable(_SOURCE, "MISSING_PARAMETERS", "Enter a PubMed search term.")

    limit = min(max(int(limit or 10), 1), 20)
    cache_key = f"evidence_search:{clean.casefold()}:{limit}"
    cached = _cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        result = _articles_for_term(clean, limit)
    except Exception as exc:  # live-data contract: structured failure, never raise
        payload = _unavailable(_SOURCE, "UPSTREAM_OR_AUTH_FAILURE", type(exc).__name__)
        _cache_set(cache_key, payload, 300)
        return payload

    payload = {
        "status": "ok",
        "source": _SOURCE,
        "query": clean,
        "total_results": result["total_results"],
        "recent": result["recent"],
        "note": "Search results are candidate literature, not quality-appraised project findings.",
        "fetched_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    _cache_set(cache_key, payload, 6 * 3600)
    return payload

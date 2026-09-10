#!/usr/bin/env python3

import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data" / "raw" / "BOLTON_TDI_APE_27_ALL_ITEMS.json"
OUTPUT = ROOT / "analysis" / "corpus_profile.json"


def first_year(value):
    match = re.search(r"\b(?:19|20)\d{2}\b", str(value or ""))
    return int(match.group()) if match else None


def build_profile(items, raw_bytes):
    item_types = Counter(item.get("data", {}).get("itemType", "unknown") for item in items)

    years = [first_year(item.get("data", {}).get("date")) for item in items]
    dated_years = [year for year in years if year is not None]

    doi_groups = defaultdict(list)
    for item in items:
        doi = (item.get("data", {}).get("DOI") or "").strip().lower()
        if doi:
            doi_groups[doi].append(item)

    duplicate_groups = []
    for doi, records in doi_groups.items():
        if len(records) > 1:
            duplicate_groups.append(
                {
                    "doi": doi,
                    "keys": [record["key"] for record in records],
                    "title": records[0].get("data", {}).get("title", ""),
                }
            )

    retracted_records = [
        {
            "key": item["key"],
            "title": item.get("data", {}).get("title", ""),
        }
        for item in items
        if "retracted" in item.get("data", {}).get("title", "").lower()
    ]

    return {
        "project": "ILE_Paper",
        "source_of_truth": {
            "file": "data/raw/BOLTON_TDI_APE_27_ALL_ITEMS.json",
            "export_n": len(items),
            "append_policy": "Do not add external evidence unless explicitly instructed to append.",
        },
        "source_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "item_types": dict(sorted(item_types.items())),
        "metadata_completeness": {
            "abstract": sum(
                bool((item.get("data", {}).get("abstractNote") or "").strip())
                for item in items
            ),
            "doi": sum(
                bool((item.get("data", {}).get("DOI") or "").strip())
                for item in items
            ),
            "url": sum(
                bool((item.get("data", {}).get("url") or "").strip())
                for item in items
            ),
            "pmid": sum(
                bool((item.get("data", {}).get("PMID") or "").strip())
                for item in items
            ),
        },
        "date_coverage": {
            "dated_items": len(dated_years),
            "undated_items": len(items) - len(dated_years),
            "earliest_year": min(dated_years) if dated_years else None,
            "latest_year": max(dated_years) if dated_years else None,
        },
        "quality_accounting": {
            "duplicate_groups": duplicate_groups,
            "retracted_records": retracted_records,
            "unique_after_deduplication": len(items)
            - sum(len(group["keys"]) - 1 for group in duplicate_groups),
            "unique_after_deduplication_and_retraction_exclusion": len(items)
            - sum(len(group["keys"]) - 1 for group in duplicate_groups)
            - len(retracted_records),
        },
    }


def main():
    raw_bytes = SOURCE.read_bytes()
    items = json.loads(raw_bytes)
    profile = build_profile(items, raw_bytes)
    OUTPUT.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(profile, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

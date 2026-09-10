#!/usr/bin/env python3

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "evidence" / "canonical_sources.json"
DIFF = REPO / "evidence" / "source_diff.json"
OUTPUT = Path(__file__).resolve().parent / "corpus_profile.json"


def first_year(value):
    match = re.search(r"\b(?:19|20)\d{2}\b", str(value or ""))
    return int(match.group()) if match else None


def main():
    canonical = json.loads(SOURCE.read_text())
    records = canonical["records"]
    diff = json.loads(DIFF.read_text())

    item_types = Counter(record.get("item_type", "unknown") for record in records)
    years = [first_year(record.get("date")) for record in records]
    dated_years = [year for year in years if year is not None]

    doi_groups = defaultdict(list)
    for record in records:
        doi = (record.get("doi") or "").strip().lower()
        if doi:
            doi_groups[doi].append(record)

    duplicate_groups = [
        {
            "doi": doi,
            "zotero_keys": [record["zotero_key"] for record in group],
            "title": group[0]["title"],
        }
        for doi, group in doi_groups.items()
        if len(group) > 1
    ]

    retracted = [
        {"zotero_key": record["zotero_key"], "title": record["title"]}
        for record in records
        if "retracted" in record.get("title", "").lower()
    ]

    profile = {
        "project": "ILE_Paper",
        "shared_source_of_truth": "evidence/canonical_sources.json",
        "export_n": len(records),
        "item_types": dict(sorted(item_types.items())),
        "date_coverage": {
            "dated_items": len(dated_years),
            "undated_items": len(records) - len(dated_years),
            "earliest_year": min(dated_years) if dated_years else None,
            "latest_year": max(dated_years) if dated_years else None,
        },
        "quality_accounting": {
            "duplicate_groups": duplicate_groups,
            "retracted_records": retracted,
            "unique_after_deduplication": len(records) - sum(len(group["zotero_keys"]) - 1 for group in duplicate_groups),
            "unique_after_deduplication_and_retraction_exclusion": len(records) - sum(len(group["zotero_keys"]) - 1 for group in duplicate_groups) - len(retracted),
        },
        "site_reconciliation": diff["summary"],
        "append_registry": "evidence/append_registry.json",
    }

    OUTPUT.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(profile, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

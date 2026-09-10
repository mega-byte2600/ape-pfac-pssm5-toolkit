#!/usr/bin/env python3

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SOURCE = REPO / "evidence" / "canonical_sources.json"
DIFF = REPO / "evidence" / "source_diff.json"
OUTPUT = Path(__file__).resolve().parent / "corpus_profile.json"

RAW_EXPORT_FILE = "BOLTON_TDI_APE_27_ALL_ITEMS.json"
RAW_EXPORT_SHA256 = "510f3d91d256081749a5b52f496bef87d2a3605a4d92b154c7d416137bad014a"
PROJECTION_FIELDS = ["zotero_key", "item_type", "title", "date", "doi", "url"]


def first_year(value):
    match = re.search(r"\b(?:19|20)\d{2}\b", str(value or ""))
    return int(match.group()) if match else None


def main():
    canonical = json.loads(SOURCE.read_text())
    records = canonical["records"]
    diff = json.loads(DIFF.read_text())

    if canonical["source_export_n"] != len(records):
        raise ValueError("Canonical source count does not match source_export_n.")

    zotero_keys = [record["zotero_key"] for record in records]
    if len(zotero_keys) != len(set(zotero_keys)):
        raise ValueError("Duplicate Zotero keys found in canonical registry.")

    if diff["summary"]["zotero_export_records"] != len(records):
        raise ValueError("Diff baseline count does not match canonical registry.")

    if diff["summary"]["matched_site_sources"] + diff["summary"]["site_only_sources"] != diff["summary"]["site_bibliography_sources"]:
        raise ValueError("Site reconciliation counts do not balance.")

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

    unique_after_deduplication = len(records) - sum(
        len(group["zotero_keys"]) - 1 for group in duplicate_groups
    )

    if diff["summary"]["zotero_unique_sources"] != unique_after_deduplication:
        raise ValueError("Diff unique-source count does not match canonical deduplication.")

    if diff["summary"]["matched_site_sources"] + diff["summary"]["zotero_only_unique_sources"] != unique_after_deduplication:
        raise ValueError("Zotero reconciliation counts do not balance.")

    profile = {
        "project": "ILE_Paper",
        "shared_source_of_truth": "evidence/canonical_sources.json",
        "source_export_file": RAW_EXPORT_FILE,
        "source_export_sha256": RAW_EXPORT_SHA256,
        "projection_fields": PROJECTION_FIELDS,
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
            "unique_after_deduplication": unique_after_deduplication,
            "unique_after_deduplication_and_retraction_exclusion": unique_after_deduplication - len(retracted),
        },
        "site_reconciliation": diff["summary"],
        "append_registry": "evidence/append_registry.json",
        "integrity_checks": {
            "canonical_count_matches_export_n": True,
            "zotero_keys_unique": True,
            "diff_baseline_matches_canonical": True,
            "site_counts_balance": True,
            "zotero_unique_counts_balance": True,
        },
    }

    OUTPUT.write_text(json.dumps(profile, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(profile, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

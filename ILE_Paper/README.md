# ILE Paper

This directory isolates the scholarly ILE paper work from the applied APE leadership toolkit while using the same evidence source of truth.

## Shared evidence source of truth

Both the APE and ILE use `../evidence/canonical_sources.json` as the canonical source registry. It contains the 51 Zotero records from `Bolton TDI APE 27` and preserves Zotero keys for traceability.

Accounting always starts at **N = 51 exported Zotero records**. The duplicate record and retracted record remain visible in the baseline for auditability; deduplication and exclusion occur only in derived analysis.

Existing public-site sources that are not identical to a canonical Zotero record are preserved in `../evidence/source_diff.json`. They are not deleted or silently merged.

Any source intentionally added beyond the 51-record baseline belongs in `../evidence/append_registry.json`, with an explicit source class. An append does not change the historical N = 51 denominator.

## Project boundary

The APE remains the applied leadership toolkit and implementation work. The ILE is the scholarly paper that analyzes and synthesizes the evidence underpinning that work. The projects can produce different analyses and products while reading from the same evidence layer.

## Analysis rule

Cleaning, title normalization, DOI reconciliation, deduplication, retraction handling, relevance screening, thematic coding, evidence grading, and other wrangling are derived transformations. They must never overwrite the canonical registry or erase the original source identity.

## Current accounting

Exported Zotero records: 51

Unique sources after DOI deduplication: 50

Unique sources after deduplication and exclusion of the explicitly retracted record: 49

Current site bibliography sources: 32

Site bibliography sources with a strict Zotero identity match: 5

Site-only sources preserved for classification or append review: 27

Canonical Zotero unique sources not currently listed in the site bibliography: 45

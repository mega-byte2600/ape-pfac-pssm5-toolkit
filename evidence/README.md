# Shared Evidence Store

This directory is the single source-control evidence layer for both the APE and ILE.

## Canonical baseline

`canonical_sources.json` is the shared 51-record Zotero source registry derived from the `Bolton TDI APE 27` export. Both APE and ILE analyses must use this same baseline unless an append is explicitly approved.

## Append layer

`append_registry.json` holds sources that are intentionally added beyond the 51-record baseline. Appends are classified by source type so the original Zotero denominator remains unchanged.

## Reconciliation layer

`source_diff.json` contains only records that differ between the canonical Zotero registry and the current public-site bibliography. Existing site sources are preserved. A site-only record is not deleted simply because it is absent from Zotero; it remains visible for later classification as an approved append, contextual source, public data source, guidance source, or lived-experience source.

## Data handling rule

Raw evidence is never overwritten by cleaning or deduplication. Cleaning, deduplication, retraction handling, relevance screening, and source classification occur only in derived analysis outputs and remain auditable back to Zotero keys, DOI, or title.

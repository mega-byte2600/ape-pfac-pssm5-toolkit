# ILE Paper

This directory isolates the scholarly ILE paper work from the applied APE leadership toolkit while preserving a shared evidence lineage.

## Evidence source of truth

The canonical evidence input is `data/raw/BOLTON_TDI_APE_27_ALL_ITEMS.json`, exported from the Zotero group library `Bolton TDI APE 27`.

Accounting starts at **N = 51 exported Zotero items**. Unless explicitly instructed to **append**, analyses for the APE and ILE use this export as the evidence source of truth rather than adding new literature.

The file `data/raw/BOLTON_TDI_APE_27_ZB5C7RQK.json` is retained only as provenance from the earlier collection scoped API pull. It contains an empty JSON array and is not an evidence corpus.

## Project boundaries

The APE remains the applied leadership toolkit and implementation work. The ILE is the scholarly paper that analyzes and synthesizes the evidence underpinning that work. Files under `ILE_Paper/` should not be mixed into the public toolkit, web application, Supabase data, or reviewer facing APE content unless that integration is explicitly requested.

## Structure

`data/raw/` contains immutable Zotero exports.

`analysis/` contains deterministic corpus accounting and analysis utilities plus derived outputs.

## Current corpus accounting

Exported items: 51

Journal articles: 32

Webpages: 14

Attachments: 2

Book: 1

Book section: 1

Video recording: 1

Unique records after DOI deduplication: 50

Unique records after deduplication and exclusion of the explicitly retracted record: 49

The raw export remains the denominator. Deduplication, retraction exclusion, relevance screening, and evidence quality decisions must be reported transparently rather than silently changing N.

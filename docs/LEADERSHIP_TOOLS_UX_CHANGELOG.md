# Leadership Tools UX Closeout

Baseline: `069af6a413c0627efc5692e23dd9533d8ae45519`

Scope: presentation and interaction only for `web/toolkit-tools.html`.

## Preserved invariants

- Existing contextual site navigation.
- Rosie lived-experience page and framing.
- About page.
- HAI Plotly dashboard.
- Applied Analysis Plotly explorer and local calculations.
- Evidence Summary, Evidence Matrix, Bibliography, Dartmouth Health Benchmark, Executive Brief, and Deliverables.
- All six Leadership Tools and their source content.
- Dartmouth Health onboarding evidence and implementation limitation.
- PREM, PROM, Press Ganey, access, safety, and causal-attribution cautions.
- Existing CSV templates and public URLs.
- Retired Reviewer Guide routes remain absent and 404.

## UX changes

- Added a compact working-tool selector for Tools 1 through 6.
- Added a context-sensitive focus selector for row-based tools.
- Shows one leadership tool at a time when JavaScript is available.
- Preserves full tables under an `Inspect full working table` disclosure.
- Keeps all content visible as a no-JavaScript fallback.
- Uses a page-specific stylesheet instead of modifying global site styling.
- Preserves the existing three-card 90-day operating plan.

## QA additions

- Static contract tests for selectors, tool count, evidence language, downloads, assets, and retired Reviewer Guide content.
- Production smoke checks for the new page markers, JavaScript, and CSS.
- Browser smoke checks tool selection, focus selection, measurement caution rendering, 90-day plan activation, preserved audit tables, and desktop/tablet/mobile horizontal overflow.

# APE Navigation Refactor Handoff

## Purpose

This document is the source of truth for a focused information architecture and navigation cleanup of the Dartmouth APE PFAC/PSSM toolkit. The site has strong content and working features, but discoverability has drifted over time and the user experience can feel like a maze. The task is to simplify how people move through the existing site without deleting, rewriting, flattening, or weakening the work already present.

## Non-negotiable constraints

1. Rosie is untouchable. Do not edit `web/story.html` content, structure, or meaning.
2. Preserve the current Applied Analysis page and Plotly functionality.
3. Preserve the compact Leadership Tools workspace and all downloadable CSVs.
4. Preserve HAI/MRSA Plotly content and supporting routes/assets.
5. Preserve evidence claims, local calculations, benchmark evidence states, APE/ILE separation, and causal guardrails.
6. Do not reintroduce Reviewer Guide, reviewer-flow navigation, or any equivalent faculty-tour layer.
7. Do not normalize one global seven-item navigation across every page. That approach was tried and reverted.
8. Do not perform a framework migration. Keep the current small HTML/CSS/vanilla-JS architecture unless a concrete defect requires otherwise.
9. Do not delete or merge pages simply to reduce page count. Solve discoverability through information architecture first.
10. Changes must be incremental, branch-isolated, testable, and reversible.

## Known navigation history

### Bad pattern: global navigation normalization

Commit `859dd41a491e811456433c6ad1f8f1dbd5216ef1` attempted to use one consistent seven-item primary navigation across every public HTML page. This flattened page context and made the site feel less intentional.

Commit `ebfbde91a6b4c12a0b9580bc3168b6234de6ce81` explicitly reverted that navigation over-refactor and restored the known-good public tree based on `472e498` while preserving Plotly, evidence, tools, calculations, backend, and visual regression protections.

### Bad pattern: reviewer-flow layer

Commit `019623ce5570fb83dde3c1c9751dc9981ce3a76a` added reviewer-flow navigation and a Reviewer Guide. This was a showstopper because it inserted an artificial review path into the public product.

Commit `069af6a413c0627efc5692e23dd9533d8ae45519` removed the Reviewer Guide and injected reviewer flow, retired those public routes, and added regression/smoke protection so they cannot return.

### Current corrective direction

Commit `470576bee3df5f8ec558a75fb5f89835b6a226d2` restored one-click homepage discoverability for signature supporting pages by adding a compact Project Library rather than flattening navigation across the site.

This is the current design principle to preserve: contextual navigation plus intentional discovery hubs.

## Current core journeys

The site should support three simple mental models without forcing users through every page.

### Leadership journey

Home → Executive Brief → DH Benchmark / Applied Analysis → Leadership Tools → APE Deliverables

This is the shortest operational route for a health-system leader.

### Evidence journey

Home → Evidence Summary → Evidence Matrix → Bibliography → Surveillance Method

This is the traceability route for faculty, researchers, or anyone validating the evidence backbone.

### Human-centered journey

Home → Rosie lived-experience anchor → HAI/MRSA safety context → Applied Analysis → Leadership Tools

Rosie is a lived-experience anchor, not representative empirical evidence and not an endorsement.

## Signature pages that must stay discoverable

- `web/story.html` — Rosie lived-experience anchor
- `web/hai-alert.html` — HAI/MRSA Plotly safety content
- `web/applied-analysis.html` — local population/access analysis
- `web/executive-launch.html` — executive brief
- `web/evidence-summary.html` — evidence synthesis
- `web/evidence-matrix.html` — source-to-claim traceability
- `web/bibliography.html` — bibliography
- `web/dh-benchmark.html` — Dartmouth Health benchmark framework
- `web/toolkit-tools.html` — compact Leadership Tools workspace
- `web/surveillance-method.html` — reproducible PubMed/My NCBI/Outlook/Zotero how-to
- `web/deliverables.html` — APE deliverables and competency proof
- `web/about.html` — project context and author information
- `web/collaboration.html` — collaboration/shared-learning model

Other pages may exist and should be inventoried before any navigation change. Do not assume they are obsolete based only on low visibility.

## Required full-stack team task

### Phase 1: inventory and graph

Produce a route inventory for every public HTML page and significant downloadable asset. For each route record:

- page title
- purpose
- primary audience
- inbound links
- outbound links
- whether it belongs to leadership, evidence, human-centered, or supporting journey
- whether it is a canonical destination, supporting page, or downloadable artifact
- whether it is currently orphaned or weakly discoverable

Then generate a directed link graph and identify:

- orphan pages
- dead ends
- duplicate routes or duplicate-purpose pages
- pages with too many outbound choices
- pages with no obvious next action
- navigation loops
- links that jump users into unrelated context

### Phase 2: propose IA before coding

Do not change code yet. Provide one recommended information architecture based on the current content. The proposal should favor:

- a small stable primary navigation for canonical destinations
- contextual secondary links on individual pages
- the homepage Project Library as a discovery hub for signature supporting work
- explicit next-step links at the bottom of major pages
- breadcrumbs only if they materially improve orientation
- no Reviewer Guide or faculty-specific tour layer
- no global mega-menu that exposes every page at once

The proposal must show the exact before/after user journeys and explain what becomes easier.

### Phase 3: smallest viable navigation refactor

Implement the minimum changes needed to make the approved IA real. Prefer link and labeling changes over page rewrites. Do not change page bodies unless a navigation label or next-action sentence is required.

### Phase 4: regression and smoke testing

Before merge, prove that:

- Rosie file is byte/content unchanged unless explicitly authorized otherwise
- Applied Analysis Plotly still renders
- HAI/MRSA Plotly still renders
- Leadership Tools selectors and CSV downloads still work
- all canonical pages return 200
- Reviewer Guide retired routes remain 404
- no public page has horizontal overflow at desktop/tablet/mobile breakpoints
- no orphan page is introduced
- all Project Library links work
- no evidence or calculation content changed unintentionally

Run Faculty Review, Site Regression, Browser Smoke, and Production Smoke on the exact merged SHA.

## Current technical architecture

Keep the current architecture simple:

- static HTML
- shared CSS plus page-scoped CSS where appropriate
- vanilla JavaScript
- Plotly where already used
- small Python server/runtime layer
- Render deployment

Do not introduce React, Next.js, a component framework, or another backend just to solve navigation.

## Team roles for Hermes orchestration

Hermes should coordinate the work but each role should have one bounded responsibility.

### Information architect

Own route inventory, audience mapping, journey design, and IA proposal. No code changes.

### Front-end engineer

Implement only the approved navigation/link changes using existing HTML/CSS/JS patterns.

### QA engineer

Build or extend automated route/link/browser checks, test all viewports, and verify invariant pages/assets.

### Evidence/content reviewer

Confirm navigation labels accurately describe page purpose and that no change alters evidence meaning, APE/ILE boundaries, or Rosie framing.

### Release engineer

Verify exact main SHA, Render deployment SHA, post-merge CI, and Production Smoke before declaring the release complete.

## Hermes execution prompt

Use this repo as the only codebase: `mega-byte2600/ape-pfac-pssm5-toolkit`.

Goal: simplify the site's information architecture and link flow because the current experience can feel like a maze, while preserving every approved content and functional asset.

Start by reading `docs/NAVIGATION_HANDOFF.md`. Do not code immediately. First inventory every public route and produce a link graph plus one recommended IA. Protect Rosie, Applied Analysis, HAI/MRSA Plotly, Leadership Tools, evidence claims, local calculations, APE/ILE separation, the surveillance how-to, and the existing visual language. Never reintroduce Reviewer Guide or normalize the same large navigation across every page. Prefer contextual navigation, discovery hubs, and explicit next actions. After the IA is approved, implement incrementally on a branch, with small commits and Faculty Review, Site Regression, Browser Smoke, and Production Smoke against the exact release SHA.

## Definition of done

A new visitor should be able to answer three questions within seconds:

1. Where do I start if I am a health-system leader?
2. Where do I verify the evidence and method?
3. Where do I see the human story and local applied analysis?

A returning user should be able to reach any signature page in one or two intentional clicks without facing a wall of links.

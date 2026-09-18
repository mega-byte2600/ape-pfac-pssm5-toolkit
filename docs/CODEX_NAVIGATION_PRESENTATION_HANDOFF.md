# Codex Technical Handoff: Elegant Navigation and Presentation Flow

## Mission

Fix the public APE site's navigation so it is elegant, predictable, and easy to present live without breaking or redesigning the working site.

Repository: `mega-byte2600/ape-pfac-pssm5-toolkit`

Baseline: current `main` at handoff creation.

This is an information architecture and navigation correction, not a visual redesign and not a content rewrite.

## User experience requirement

A presenter starting on the homepage must be able to walk faculty, students, and visitors through the APE without memorizing the site's 19-page structure, guessing which link comes next, using the browser Back button to recover, or wondering where a click will lead.

The site must have one obvious presentation spine:

`Home → Executive Brief → Evidence Summary → Applied Analysis → Leadership Tools → APE Deliverables`

Every core page must make the next destination explicit by name. Example: `Next: Applied Analysis`, not `Continue` or `Learn more`.

Supporting pages remain available and directly shareable but must not compete with the core presentation path.

## Current-state diagnosis

The existing navigation consistency refactor solved several mechanical inconsistencies but did not solve information architecture.

Current public surface contains 19 HTML pages under `web/`.

The homepage currently exposes:
1. Six primary navigation choices.
2. Three hero actions.
3. Six Leadership Path cards.
4. Eleven Project Library cards.

The result is multiple overlapping ways to reach content and excessive peer-level choice. Technically valid links can still produce a maze.

The existing root `handoff.md` documents an earlier navigation-normalization problem and must NOT be treated as the implementation specification for this issue.

## Architecture

### Tier 1: presentation spine

These are the six core destinations and their required order:

1. Home: `/`
2. Executive Brief: `/executive-launch.html`
3. Evidence Summary: `/evidence-summary.html`
4. Applied Analysis: `/applied-analysis.html`
5. Leadership Tools: `/toolkit-tools.html`
6. APE Deliverables: `/deliverables.html`

Do not create another competing top-level route.

### Tier 2: supporting evidence and methods

Keep these pages intact and discoverable from the most relevant Tier 1 parent:

Evidence Summary:
`/evidence.html`
`/evidence-matrix.html`
`/bibliography.html`
`/surveillance-method.html`
`/toolkit-scan.html`

Applied Analysis:
`/dh-benchmark.html`
`/hai-alert.html`

Leadership Tools:
`/charter.html`
`/pfac-governance-charter.html`
working CSV/tool downloads already exposed by the toolkit

Project context / lived experience:
`/story.html`
`/resources.html`
`/collaboration.html`
`/about.html`

These are not deleted. They are demoted from competing navigation choices into contextual supporting destinations.

## Required interaction model

### Primary navigation

Create one small, stable primary navigation model across core pages. It must reinforce the presentation spine rather than expose the entire repository.

Do not use the header as a sitemap.

Codex may determine the cleanest responsive implementation using the existing HTML/CSS/JS architecture, but it must preserve semantic `nav aria-label="Primary"` behavior and accessibility.

### Previous and Next

On each Tier 1 page except Home, provide explicit presentation controls near the end of the principal content:

Executive Brief:
Previous: Home
Next: Evidence Summary

Evidence Summary:
Previous: Executive Brief
Next: Applied Analysis

Applied Analysis:
Previous: Evidence Summary
Next: Leadership Tools

Leadership Tools:
Previous: Applied Analysis
Next: APE Deliverables

APE Deliverables:
Previous: Leadership Tools
Next: Home, labeled clearly as return to project home rather than implying another presentation section.

Destination names must be visible in the link text.

### Supporting-page orientation

Every Tier 2 page must have an obvious route back to its Tier 1 parent and must not become a dead end.

Examples:
HAI Alert → Back to Applied Analysis
Evidence Matrix → Back to Evidence Summary
Governance Charter → Back to Leadership Tools

Do not add arbitrary cross-links merely to increase connectivity.

## Homepage simplification

The homepage must communicate the presentation sequence clearly.

Reduce redundant calls to the same destinations. The header, hero actions, Leadership Path, and Project Library currently compete with one another.

Preserve substantive APE content, but simplify the navigation surface so the six-step core journey is visually and semantically dominant.

The Project Library may remain as a secondary resource area, but it must read as supporting material, not another primary route through the project.

Do not delete a page solely to simplify navigation.

## HAI Alert requirement

`web/hai-alert.html` and `pssm5_toolkit/hai_dashboard.py` are existing project assets.

The project owner has established the conceptual mapping:

`HAI Alert → Pay for Performance Incentives`

Treat this as a required information-architecture/content relationship to surface appropriately within the Applied Analysis context.

Important evidence constraint: do not invent a causal claim, financial result, incentive amount, reimbursement effect, or evidence citation. First inspect the project's validated evidence/source material. If the repository does not support a stronger claim, implement only a clearly bounded conceptual connection and flag the evidence limitation in the change report.

## Non-negotiable preservation constraints

1. No wholesale redesign.
2. No backend, Supabase, API, or data-model changes for this navigation task.
3. No deletion or rewriting of validated APE evidence merely to make navigation simpler.
4. Do not mix ILE content into the public APE.
5. Do not expose internal reviewer guides, prompts, grading language, AI reasoning, QA commentary, or development notes on public pages.
6. Preserve the existing PFAC Leadership Toolkit identity.
7. Preserve working direct URLs to all legitimate public pages.
8. Preserve retired-route behavior.
9. Preserve accessibility, responsive behavior, and semantic navigation.
10. No unsupported factual, causal, outcome, or performance claims.

## Implementation discipline

### Phase 1: audit before edit

Before modifying files, inspect all `web/*.html`, navigation-related CSS/JS, and navigation assertions in tests.

Produce a concise implementation map containing:
1. Current Tier 1 navigation on each page.
2. Duplicate/redundant entry points.
3. Tier 2 parent assignment.
4. Exact files proposed for modification.
5. Tests that must change.
6. Any conflict between this handoff and existing contract tests.

Do not code until this map is internally coherent.

### Phase 2: minimal implementation

Prefer the smallest reusable implementation that produces the required UX.

Avoid large mechanical rewrites of 19 pages when a safer shared CSS/JS or narrowly scoped HTML pattern is available.

Do not introduce a framework migration.

Keep diffs reviewable.

### Phase 3: regression

Run the repository's existing gates, including as applicable:

```bash
python3 scripts/extended_public_smoke.py
python3 scripts/faculty_review.py
PYTHONPYCACHEPREFIX=/private/tmp/ape-pycache python3 -m compileall pssm5_toolkit
PYTHONPYCACHEPREFIX=/private/tmp/ape-pycache python3 -m unittest discover -s tests -p 'test_*.py' -v
python3 scripts/browser_smoke.py
```

Also validate manually or through browser automation:

1. Desktop navigation.
2. Mobile-width navigation.
3. Keyboard navigation and focus visibility.
4. Every Tier 1 Previous/Next destination.
5. Every Tier 2 return-to-parent destination.
6. No dead links.
7. No unexpected homepage fallback from subpages.
8. Direct loading of all 19 public pages.
9. Presentation flow from Home through APE Deliverables without Back-button recovery.

Do not weaken a valid test merely to make the new implementation pass. Update tests only where the intended navigation contract has legitimately changed.

## Acceptance tests

The work is complete only when all are true:

1. A first-time visitor can identify the primary path from the homepage.
2. A presenter can traverse the complete APE in the defined order without guessing.
3. Each Next link names its destination.
4. Each supporting page has a clear parent and return path.
5. Supporting resources remain directly addressable and shareable.
6. The header no longer behaves like a 19-page sitemap.
7. The homepage no longer presents multiple competing primary architectures.
8. HAI Alert is contextually mapped to Applied Analysis and the Pay for Performance Incentives concept without unsupported claims.
9. Existing substantive content and functionality remain intact.
10. All appropriate automated regression gates pass.

## Definition of done / developer report

Do not merge automatically.

Return:
1. Before/after navigation map.
2. Files changed.
3. Exact behavior changed.
4. Tests changed and why.
5. Full test results.
6. Any evidence limitation encountered for HAI Alert / Pay for Performance Incentives.
7. Screenshots or concise browser-validation observations for desktop and mobile.
8. Commit SHA and PR link if a PR is created.

## North Star

The site should feel like a guided professional presentation with a deeper reference library behind it.

A user should always know:

Where am I?
What is this page for?
Where do I go next?
How do I return to the main flow?

If navigation makes the presenter think about the navigation instead of the APE, the implementation has failed.

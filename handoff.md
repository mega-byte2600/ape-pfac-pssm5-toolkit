# Evidence-Based Approach to Improve Outcomes for Patient-Care Experience — Navigation Consistency Refactor Handoff

**Branch:** `refactor/nav-consistency-handoff`
**Date:** 2026-09-10
**Scope:** Public-facing navigation consistency across `web/*.html`. No backend, API, or data-layer changes.

---

## 1. Purpose

Navigation is orientation. When header style, brand, link labels, and nav width change from page to page, the user subconsciously asks "where am I?" — that question is friction, and friction erodes trust. For a faculty-facing evidence product, trust is survival.

The goal: **consistent, predictable navigation that preserves the project's intentional contextual-nav model** while eliminating the micro-inconsistencies that make the site feel unfinished.

This is not about adding a global nav. The QA playbook explicitly states: *"Navigation improvements should add orientation without flattening contextual page navigation."* Contextual nav stays. We make it consistent.

---

## 2. Current State (measured, not assumed)

### 2.1 Header brand inconsistency

Every page has a different brand mark and name in the header. The homepage shows "PFAC Leadership Toolkit" with mark "PF". Other pages show:

| Page | Mark | Brand text |
|------|------|------------|
| `index.html` | PF | PFAC Leadership Toolkit |
| `evidence.html` | EV | Evidence Launch Page |
| `evidence-summary.html` | — | Evidence-Based PFAC Summary |
| `evidence-matrix.html` | — | Evidence Matrix |
| `bibliography.html` | — | Bibliography |
| `charter.html` | LC | Launch Charter |
| `story.html` | — | Rosie Bartel Story Anchor |
| `hai-alert.html` | — | HAI Risk Alert |
| `applied-analysis.html` | — | Applied Analysis |
| `dh-benchmark.html` | — | Dartmouth Health Benchmark |
| `executive-launch.html` | — | Executive Launch Brief |
| `toolkit-tools.html` | LT | Leadership Tools |
| `deliverables.html` | — | APE Deliverables |
| `collaboration.html` | — | Collaboration Layer |
| `surveillance-method.html` | — | Research Surveillance Method |
| `resources.html` | — | Open Resources |
| `about.html` | — | About the Project Lead |
| `toolkit-scan.html` | — | Toolkit Scan |
| `pfac-governance-charter.html` | — | PFAC Governance Charter Starter |

**Problem:** The user lands on a page and the header tells them they're on a different product. There is no single identity anchor.

### 2.2 Header style inconsistency

Two header classes are used: `site-header enterprise-header` and `site-header` (no enterprise-header). The `enterprise-header` class adds `box-shadow`. Usage is random — no correlation with page type, importance, or section.

### 2.3 Link label inconsistency

The same target page has different labels depending on which page the user is coming from:

| Target | Labels used |
|--------|-------------|
| `/applied-analysis.html` | "Analysis", "Applied Analysis" |
| `/deliverables.html` | "Deliverables", "APE Deliverables" |
| `/evidence-matrix.html` | "Evidence", "Matrix", "Evidence Matrix" |
| `/evidence-summary.html` | "Evidence", "Summary" |
| `/toolkit-tools.html` | "Leadership Tools", "Tools" |

**Problem:** Users don't build a stable mental model. "Evidence" on one page points to a different destination than "Evidence" on another.

### 2.4 Nav width inconsistency

- `index.html`: 6 links
- `toolkit-tools.html`: 6 links
- Most other pages: 4–5 links

No clear information-architecture reason for the variance.

### 2.5 Orphan pages

These pages are never linked from any page's primary nav:
- `charter.html`
- `pfac-governance-charter.html`
- `toolkit-scan.html`

(Note: `index.html` is the homepage — reachable via `/` and the "Toolkit"/"Overview" labels, so it's not truly orphaned, but it's not linked by name.)

### 2.6 What is working

- All pages serve 200 OK (verified by test suite)
- No homepage fallback on subpages (verified)
- Retired routes (`/mvp-one.html`, `/review-flow.js`) remain 404
- Contextual nav model is preserved
- No dead nav links (all targets exist)
- Footer, skip link, and semantic structure are consistent

---

## 3. What must NOT break

These are hard constraints. Violating any of them means the refactor failed.

1. **Contextual navigation model** — Each page still links to its related pages. We do not replace contextual nav with a single global nav.
2. **Retired routes stay retired** — `/mvp-one.html`, `/review-flow.js` remain 404 and unlinked.
3. **Evidence boundaries** — No conflation of story with evidence, no unsupported claims.
4. **Existing contract tests** — `test_dh_benchmark_contextual_navigation_sequence_is_preserved` hardcodes the dh-benchmark nav. If you change dh-benchmark's nav, you MUST update this test.
5. **Homepage fallback guard** — Subpages must not serve homepage content.
6. **No spillover** — No internal/prompt/build language leaks into public pages.
7. **Existing content** — All page content, copy, and data stay unchanged. This is nav-only.
8. **Header HTML structure** — `browser_smoke.py` asserts `nav[aria-label="Primary"]` count == 1 per page. Don't remove or duplicate the primary nav.

---

## 4. Recommended Approach

### 4.1 Single site identity (fix brand inconsistency)

**Decision:** All pages share one brand in the header.

```html
<header class="site-header enterprise-header">
  <div class="brand">
    <span class="mark">PF</span>
    <div>
      <strong>PFAC Leadership Toolkit</strong>
      <small>Evidence. Local analysis. Decisions. Accountability.</small>
    </div>
  </div>
  <nav aria-label="Primary">...</nav>
</header>
```

The brand block is identical on every page. The nav block is contextual (different links per page).

**Rationale:** The user always knows what product they're in. The homepage and subpages are the same product. This is standard for single-product sites and matches the project's "enterprise" positioning.

**Risk:** Some pages (evidence.html) have their own hero with a page-specific title and eyebrow. The header brand does not conflict with that — the hero still says "Evidence Launch Page", the header says "PFAC Leadership Toolkit". This is normal: site identity ≠ page title.

### 4.2 One header class (fix style inconsistency)

**Decision:** Every page uses `class="site-header enterprise-header"`.

The bare `site-header` class is removed from all pages. The `enterprise-header` box-shadow is a subtle professional touch and should be uniform.

### 4.3 Canonical link labels (fix label inconsistency)

Pick one label per target. Apply it everywhere that target is linked.

| Target | Canonical label | Rationale |
|--------|-----------------|-----------|
| `/` | Toolkit | Short, matches homepage brand |
| `/executive-launch.html` | Executive Brief | Full name, matches h1 |
| `/evidence-summary.html` | Evidence Summary | Full name |
| `/evidence-matrix.html` | Evidence Matrix | Full name |
| `/bibliography.html` | Bibliography | Full name |
| `/story.html` | Rosie Bartel | Full name |
| `/hai-alert.html` | HAI Alert | Full name |
| `/applied-analysis.html` | Applied Analysis | Full name |
| `/dh-benchmark.html` | DH Benchmark | Short, matches existing convention |
| `/toolkit-tools.html` | Leadership Tools | Full name |
| `/deliverables.html` | APE Deliverables | Full name |
| `/collaboration.html` | Collaboration | Short, clean |
| `/surveillance-method.html` | Surveillance Method | Full name |
| `/resources.html` | Resources | Short, clean |
| `/about.html` | About | Standard |
| `/toolkit-scan.html` | Toolkit Scan | Full name |
| `/charter.html` | Launch Charter | Full name |
| `/pfac-governance-charter.html` | Governance Charter | Short, distinct from charter.html |

### 4.4 Consistent nav width (fix width inconsistency)

**Decision:** Most pages get 5 links. The homepage stays at 6 (it's the hub). Pages with a natural 4-link context stay at 4 — but only if the 4 links are truly the most relevant, not just arbitrary.

Proposed nav for each page (see §5 for full file-by-file spec).

### 4.5 Integrate orphans

`charter.html`, `toolkit-scan.html`, and `pfac-governance-charter.html` need to be reachable. Options:
- Add them to relevant pages' contextual nav
- Add them to the homepage card grid (which already links to many pages)
- Both

---

## 5. File-by-File Change Spec

This is the execution plan. Each file's nav is listed with the exact links in order.

### 5.1 `index.html` (homepage — hub)

**Header:** PFAC Leadership Toolkit (as today — already correct)
**Nav (6 links):**
1. Executive Brief → `/executive-launch.html`
2. Evidence Summary → `/evidence-summary.html`
3. DH Benchmark → `/dh-benchmark.html`
4. Applied Analysis → `/applied-analysis.html`
5. Leadership Tools → `/toolkit-tools.html`
6. APE Deliverables → `/deliverables.html`

No change to nav. Already consistent.

### 5.2 `evidence.html` (evidence launch)

**Header:** PFAC Leadership Toolkit (was: "Evidence Launch Page" / mark "EV")
**Nav (5 links):**
1. Toolkit → `/`
2. Evidence Summary → `/evidence-summary.html`
3. Evidence Matrix → `/evidence-matrix.html`
4. Bibliography → `/bibliography.html`
5. Leadership Tools → `/toolkit-tools.html`

No change to nav links. Only header brand changes.

### 5.3 `evidence-summary.html`

**Header:** PFAC Leadership Toolkit (was: "Evidence-Based PFAC Summary" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. Evidence Matrix → `/evidence-matrix.html`
3. Bibliography → `/bibliography.html`
4. DH Benchmark → `/dh-benchmark.html`
5. About → `/about.html`

Change: Add canonical label consistency. Current nav is already reasonable. Consider adding a 6th link to `/evidence.html` (the launch page) for users who want the entry point.

### 5.4 `evidence-matrix.html`

**Header:** PFAC Leadership Toolkit (was: "Evidence Matrix" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. Evidence Summary → `/evidence-summary.html`
3. Bibliography → `/bibliography.html`
4. Surveillance Method → `/surveillance-method.html`
5. About → `/about.html`

### 5.5 `bibliography.html`

**Header:** PFAC Leadership Toolkit (was: "Bibliography" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. Evidence Summary → `/evidence-summary.html`
3. Evidence Matrix → `/evidence-matrix.html`
4. Rosie Bartel → `/story.html`
5. Surveillance Method → `/surveillance-method.html`

### 5.6 `story.html`

**Header:** PFAC Leadership Toolkit (was: "Rosie Bartel Story Anchor" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. Evidence Summary → `/evidence-summary.html`
3. Bibliography → `/bibliography.html`
4. HAI Alert → `/hai-alert.html`
5. About → `/about.html`

### 5.7 `hai-alert.html`

**Header:** PFAC Leadership Toolkit (was: "HAI Risk Alert" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. Applied Analysis → `/applied-analysis.html`
3. Rosie Bartel → `/story.html`
4. Deliverables → `/deliverables.html`
5. About → `/about.html`

### 5.8 `applied-analysis.html`

**Header:** PFAC Leadership Toolkit (was: "Applied Analysis" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. Deliverables → `/deliverables.html`
3. DH Benchmark → `/dh-benchmark.html`
4. Leadership Tools → `/toolkit-tools.html`
5. Evidence Summary → `/evidence-summary.html`

### 5.9 `dh-benchmark.html`

**Header:** PFAC Leadership Toolkit (was: "Dartmouth Health Benchmark" / no mark)
**Nav (5 links):**
1. Evidence Summary → `/evidence-summary.html`
2. Surveillance Method → `/surveillance-method.html`
3. Applied Analysis → `/applied-analysis.html`
4. HAI Alert → `/hai-alert.html`
5. About → `/about.html`

**TEST WARNING:** `test_dh_benchmark_contextual_navigation_sequence_is_preserved` hardcodes the current nav for this page. If you change the nav, you MUST update this test with the new link sequence. The test is in `tests/test_web_contract.py`.

### 5.10 `executive-launch.html`

**Header:** PFAC Leadership Toolkit (was: "Executive Launch Brief" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. APE Deliverables → `/deliverables.html`
3. Applied Analysis → `/applied-analysis.html`
4. Leadership Tools → `/toolkit-tools.html`
5. DH Benchmark → `/dh-benchmark.html`

### 5.11 `toolkit-tools.html`

**Header:** PFAC Leadership Toolkit (was: "Leadership Tools" / mark "LT")
**Nav (6 links — this page has a lot of peer pages):**
1. Toolkit → `/`
2. Executive Brief → `/executive-launch.html`
3. APE Deliverables → `/deliverables.html`
4. DH Benchmark → `/dh-benchmark.html`
5. Evidence Matrix → `/evidence-matrix.html`
6. About → `/about.html`

No change to nav links. Only header brand changes.

### 5.12 `deliverables.html`

**Header:** PFAC Leadership Toolkit (was: "APE Deliverables" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. Evidence Summary → `/evidence-summary.html`
3. DH Benchmark → `/dh-benchmark.html`
4. Applied Analysis → `/applied-analysis.html`
5. Leadership Tools → `/toolkit-tools.html`

### 5.13 `collaboration.html`

**Header:** PFAC Leadership Toolkit (was: "Collaboration Layer" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. Evidence Summary → `/evidence-summary.html`
3. Surveillance Method → `/surveillance-method.html`
4. About → `/about.html`
5. Deliverables → `/deliverables.html`

### 5.14 `surveillance-method.html`

**Header:** PFAC Leadership Toolkit (was: "Research Surveillance Method" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. Evidence Summary → `/evidence-summary.html`
3. DH Benchmark → `/dh-benchmark.html`
4. Evidence Matrix → `/evidence-matrix.html`
5. Bibliography → `/bibliography.html`

### 5.15 `resources.html`

**Header:** PFAC Leadership Toolkit (was: "Open Resources" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. Evidence Summary → `/evidence-summary.html`
3. Bibliography → `/bibliography.html`
4. Rosie Bartel → `/story.html`
5. Surveillance Method → `/surveillance-method.html`

### 5.16 `about.html`

**Header:** PFAC Leadership Toolkit (was: "About the Project Lead" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. Evidence Summary → `/evidence-summary.html`
3. Applied Analysis → `/applied-analysis.html`
4. Deliverables → `/deliverables.html`
5. Collaboration → `/collaboration.html`

### 5.17 `toolkit-scan.html`

**Header:** PFAC Leadership Toolkit (was: "Toolkit Scan" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. Evidence Summary → `/evidence-summary.html`
3. Bibliography → `/bibliography.html`
4. Leadership Tools → `/toolkit-tools.html`
5. DH Benchmark → `/dh-benchmark.html`

### 5.18 `charter.html`

**Header:** PFAC Leadership Toolkit (was: "Launch Charter" / mark "LC")
**Nav (5 links):**
1. Toolkit → `/`
2. Executive Brief → `/executive-launch.html`
3. APE Deliverables → `/deliverables.html`
4. Governance Charter → `/pfac-governance-charter.html`
5. About → `/about.html`

### 5.19 `pfac-governance-charter.html`

**Header:** PFAC Leadership Toolkit (was: "PFAC Governance Charter Starter" / no mark)
**Nav (5 links):**
1. Toolkit → `/`
2. Executive Brief → `/executive-launch.html`
3. Leadership Tools → `/toolkit-tools.html`
4. DH Benchmark → `/dh-benchmark.html`
5. APE Deliverables → `/deliverables.html`

---

## 6. What else to update

### 6.1 Tests

- `tests/test_web_contract.py` — `test_dh_benchmark_contextual_navigation_sequence_is_preserved` must be updated if dh-benchmark nav changes.
- `tests/test_web_contract.py` — `test_core_public_pages_serve_expected_content` checks for content fragments, not nav. Should still pass.
- `scripts/browser_smoke.py` — checks nav count == 1 per page. Should still pass.
- `scripts/extended_public_smoke.py` — checks nav labels. Should still pass since we're standardizing labels.

### 6.2 Docs

- `docs/LEADERSHIP_TOOLS_UX_CHANGELOG.md` — only if toolkit-tools.html nav changes (it doesn't in this plan).
- `docs/QA_REGRESSION_PLAYBOOK.md` — no changes needed.

### 6.3 CI/CD

- `.github/workflows/site-regression.yml` — no changes needed.
- `.github/workflows/browser-smoke.yml` — no changes needed.

---

## 7. Risks

### 7.1 Test breakage (HIGH)

The dh-benchmark nav contract test will break if that page's nav changes. Update the test in the same commit. Do not leave main with a broken test.

### 7.2 Browser smoke flakiness (LOW)

The browser smoke checks for `nav[aria-label="Primary"]` count. We're not removing or duplicating nav, so this is safe.

### 7.3 Loss of page identity (LOW)

Pages like `evidence.html` have a unique hero and eyebrow. The header brand change does not touch the hero. The page still feels like "the evidence page" because the hero and content are unchanged. Only the site identity strip at the top becomes uniform.

### 7.4 Over-navigating (LOW)

Adding links to orphan pages could make some navs feel arbitrary. Mitigation: only add an orphan link if there's a genuine contextual reason (e.g., charter.html is linked from toolkit-tools.html already via resource-links; adding it to the executive-launch nav is a stretch — prefer adding it to the homepage card grid instead).

---

## 8. Execution Order

1. Create the branch (done: `refactor/nav-consistency-handoff`).
2. Update the homepage card grid to include links to `charter.html`, `toolkit-scan.html`, and `pfac-governance-charter.html` (if not already present — check index.html's project library section).
3. Apply the header brand change to all 19 pages (mechanical, search-and-replace).
4. Apply the nav label canonicalization to all pages.
5. Update `tests/test_web_contract.py` for the dh-benchmark nav change.
6. Run the full PR gate locally:
   ```
   python3 scripts/extended_public_smoke.py
   python3 scripts/faculty_review.py
   PYTHONPYCACHEPREFIX=/private/tmp/ape-pycache python3 -m compileall pssm5_toolkit
   PYTHONPYCACHEPREFIX=/private/tmp/ape-pycache python3 -m unittest discover -s tests -p 'test_*.py' -v
   ```
7. If Playwright is installed, run `python3 scripts/browser_smoke.py`.
8. Commit, push, open PR.

---

## 9. Out of Scope

- Backend/API changes
- Content/copy changes
- CSS visual redesign (beyond the header class normalization)
- New pages
- Removing pages
- Supabase changes
- Render deployment config changes

---

## 10. Success Criteria

After the refactor:
- Every page has the same header brand: "PFAC Leadership Toolkit" with mark "PF".
- Every page uses `class="site-header enterprise-header"`.
- Every link to a given target uses the same label, everywhere.
- Every page has 4–6 nav links (5 is the norm; 4 or 6 only with justification).
- All orphan pages are reachable from at least one other page's nav or the homepage card grid.
- All existing tests pass.
- No retired routes are exposed.
- No content is lost.
- The contextual nav model is preserved.

---

## 11. Why This Approach

The project's README says: *"The project distinguishes among federal requirements and guidance, empirical findings, conceptual frameworks, implementation recommendations, local descriptive analysis, proposed leadership actions, and lived-experience material."*

Navigation is the same discipline applied to site structure: distinguish clearly, label consistently, don't conflate one thing with another. A user should never wonder "is this the same site?" or "does 'Evidence' mean the same thing here as it did on the last page?"

Consistency is not rigidity. Contextual nav stays. We just make the context readable.

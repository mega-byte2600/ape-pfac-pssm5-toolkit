# Development Schedule: MVP → Golden Master

**Branch:** `refactor/nav-consistency-handoff`
**Deadline:** 2026-09-11 16:00hrs PDT (firm)
**Budget:** ~12 effective hours
**Ratio:** 80% Development / 20% QA

---

## Timeline

| Time | Phase | Activity | Type | Owner |
|------|-------|----------|------|-------|
| 08:00–09:30 | **1. Nav Refactor** | Apply header brand consistency across all 19 pages (`site-header enterprise-header` + PF brand) | Dev | Agent |
| 09:30–11:00 | **1. Nav Refactor** | Apply canonical link labels + consistent nav widths (5 links standard) | Dev | Agent |
| 11:00–12:00 | **2. Integration** | Integrate orphan pages (`charter.html`, `toolkit-scan.html`, `pfac-governance-charter.html`) into nav + homepage grid | Dev | Agent |
| 12:00–13:00 | **3. Content Polish** | Hero section consistency, mobile viewport audit, command-strip alignment | Dev | Agent |
| 13:00–14:00 | **4. QA Gate 1** | Update `test_web_contract.py` for dh-benchmark nav; run full test suite (`compileall`, `unittest discover`) | QA | Agent |
| 14:00–14:30 | **4. QA Gate 1** | Run `extended_public_smoke.py` + `faculty_review.py` | QA | Agent |
| 14:30–15:00 | **5. Merge & Deploy** | Merge to `main`, push to GitHub, verify Render auto-deploy | Dev | Agent |
| 15:00–15:30 | **5. Merge & Deploy** | Deploy Supabase functions (`toolkit-data`, `demo-intake`), verify edge function responses | Dev | Agent |
| 15:30–16:00 | **6. Final QA** | Verify deployed URL across desktop/tablet/mobile; browser smoke if Playwright available; present demo URL | QA | Agent |

---

## Phase Details

### Phase 1: Nav Refactor (Dev — 3h)

**Goal:** Eliminate the 5 inconsistency classes identified in `handoff.md`.

**Tasks:**
1. Replace per-page brand blocks with unified brand:
   ```html
   <div class="brand">
     <span class="mark">PF</span>
     <div>
       <strong>PFAC Leadership Toolkit</strong>
       <small>Evidence. Local analysis. Decisions. Accountability.</small>
     </div>
   </div>
   ```
2. Standardize all headers to `class="site-header enterprise-header"`.
3. Apply canonical labels from §4.3 of `handoff.md`.
4. Set nav width to 5 links for all pages (6 for homepage, 4 only with justification).

**Pages affected:** All 19 `web/*.html` files.

**Validation:** `grep -c 'PFAC Leadership Toolkit' web/*.html` should return 19.

---

### Phase 2: Orphan Integration (Dev — 1h)

**Goal:** No page is unreachable.

**Tasks:**
1. Add `charter.html` to toolkit-tools nav + homepage card grid.
2. Add `toolkit-scan.html` to evidence nav + homepage card grid.
3. Add `pfac-governance-charter.html` to deliverables nav + homepage card grid.

**Validation:** `grep -r 'charter.html\|toolkit-scan.html\|pfac-governance-charter.html' web/*.html` returns nav links.

---

### Phase 3: Content Polish (Dev — 1h)

**Goal:** Consistent hero sections, responsive behavior.

**Tasks:**
1. Ensure every hero has an eyebrow, h1, and lead paragraph.
2. Verify mobile viewport meta tags present.
3. Check horizontal overflow on key pages (applied-analysis, toolkit-tools, dh-benchmark).
4. Verify all Plotly containers present on `applied-analysis.html` and `hai-alert.html`.

---

### Phase 4: QA Gate 1 (QA — 1.5h)

**Goal:** All tests green before deploy.

**Tasks:**
1. Update `tests/test_web_contract.py::test_dh_benchmark_contextual_navigation_sequence_is_preserved` with new nav sequence.
2. Run `PYTHONPYCACHEPREFIX=/private/tmp/ape-pycache python3 -m compileall pssm5_toolkit`.
3. Run `PYTHONPYCACHEPREFIX=/private/tmp/ape-pycache python3 -m unittest discover -s tests -p 'test_*.py' -v`.
4. Run `python3 scripts/extended_public_smoke.py`.
5. Run `python3 scripts/faculty_review.py`.

**Exit criteria:** 0 test failures, 0 smoke errors.

---

### Phase 5: Merge & Deploy (Dev — 1h)

**Goal:** Live URL serving golden master.

**Tasks:**
1. `git add -A && git commit -m "refactor: nav consistency + brand unity across public pages"`.
2. `git checkout main && git merge refactor/nav-consistency-handoff --no-ff`.
3. `git push origin main`.
4. Verify Render auto-deploys (check dashboard or `render.yaml` service `ape-pfac-pssm5-toolkit`).
5. Deploy Supabase functions: `supabase functions deploy toolkit-data && supabase functions deploy demo-intake`.
6. Verify edge functions respond: `curl https://vgquagonefygzgebgzyx.supabase.co/functions/v1/toolkit-data`.

**Expected URL:** `https://ape-pfac-pssm5-toolkit.onrender.com`

---

### Phase 6: Final QA (QA — 0.5h)

**Goal:** Verify deployed artifact works end-to-end.

**Tasks:**
1. Open deployed URL on desktop (1440×1000).
2. Verify primary nav present and consistent across `/`, `/evidence-summary.html`, `/dh-benchmark.html`, `/toolkit-tools.html`.
3. Open on tablet (900×1100) and mobile (390×844) viewports.
4. Verify Plotly charts render on `/applied-analysis.html` and `/hai-alert.html`.
5. Verify Supabase data loads on `/` (toolkit homepage fetches live data).
6. Run `python3 scripts/browser_smoke.py` if Playwright installed.
7. Run `python3 scripts/production_smoke.py --expected-sha $(git rev-parse HEAD)`.

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Render auto-deploy fails | Manually trigger deploy via Render dashboard; verify build logs |
| Supabase function deploy fails | Functions are additive; existing functions continue working. Deploy with `--no-verify-jwt` if needed |
| Test contract break (dh-benchmark) | Update test in same commit; never leave main red |
| Merge conflict on main | Branch is isolated; rebase if needed before merge |
| Playwright not installed | Browser smoke is optional; contract tests are sufficient |

---

## Success Criteria (16:00hrs)

- [ ] All 19 pages share unified brand and header style
- [ ] Canonical labels applied everywhere
- [ ] All orphan pages reachable
- [ ] Full test suite green
- [ ] Smoke tests pass
- [ ] Deployed URL live and verified
- [ ] Demo URL ready to present

---

## Notes

- All changes are nav-only; no content, data, or backend logic is altered.
- The retired Reviewer Guide routes remain 404 and unlinked.
- Evidence boundaries and spillover guards remain intact.
- No API credentials are modified.

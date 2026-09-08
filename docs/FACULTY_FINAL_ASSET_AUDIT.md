# Faculty Final Asset Audit

## A. Executive assessment

The current APE site is a strong, faculty-facing Applied Practice Experience asset. It reads as a public-health and health-system improvement product rather than a software demo. The evidence summary, matrix, DH benchmark framework, HAI alert, local applied analysis, leadership tools, deliverables page, Rosie Bartel lived-experience anchor, and About page are preserved.

The audit found no BLOCKER issues. HIGH issues were limited to discoverability of valid supporting pages and one homepage phrase that could be read as overclaiming care improvement. One source-level search placeholder also appeared in the public HTML scan; it was not narrative copy, but removing it strengthens the zero-spillover standard.

## B. Page-by-page faculty review

| Page | Severity | Finding |
|---|---:|---|
| Home | HIGH | Clear APE entry point, but the headline "Turn patient voice into better care" could be read as an unsupported improvement claim. |
| Evidence Summary | LOW | Strong synthesis and visible limitations. Current wording separates PFAC structure from outcome attribution. |
| Evidence Launch Page | MEDIUM | Strong evidence pathway. Comparative toolkit scan existed but was not reachable from the main reviewer path. |
| Evidence Matrix | LOW | Evidence type, limitations, leadership action, anticipated benefit, and measurement connection are clearly separated. |
| Dartmouth Health Benchmark | LOW | Correctly presents a benchmark assessment framework, not a completed scorecard or numeric maturity score. |
| HAI Risk Alert | LOW | Plotly dashboard, evidence detail table, and HAI synthesis are intact and appropriately bounded to national signal plus local questions. |
| Applied Analysis | MEDIUM | Plotly local analysis is intact. One HTML search placeholder appeared in public source scan. |
| Leadership Tools | MEDIUM | Tools are usable and health-system oriented. Launch charter existed but was not reachable from the main reviewer graph. |
| Rosie Bartel Story | LOW | Lived-experience framing is explicit and non-representative evidence boundary is preserved. |
| About / Project Lead | LOW | Contact and collaboration pathways are clear. |
| Deliverables | LOW | The two APE deliverables and competency traceability are explicit. |
| Reviewer Guide | HIGH | Useful page, but it was orphaned from the homepage reviewer path. |
| Toolkit Scan | HIGH | Useful comparative page, but it was orphaned from the homepage reviewer path. |
| Launch Charter | HIGH | Useful governance page, but it was orphaned from the homepage reviewer path. |

## C. Information architecture / navigation map

The site uses contextual navigation rather than a single repeated global menu. The main reviewer path now starts at the homepage and reaches: Executive Brief, Evidence Summary, DH Benchmark, Applied Analysis, Leadership Tools, Method, APE Deliverables, Rosie Bartel Story, Reviewer Guide, Toolkit Scan, Launch Charter, Evidence Matrix, Bibliography, HAI Alert, About, Collaboration, Resources, Surveillance Method, and Governance Charter Starter.

## D. Orphaned or hard-to-discover pages

HIGH: `/mvp-one.html`, `/toolkit-scan.html`, and `/charter.html` were valid pages but were not reachable from the homepage navigation graph. The fix adds contextual links from the homepage, Evidence page, and Leadership Tools page.

## E. Broken or misleading links

No broken internal route was found during local route validation. The server returns 200 for public HTML, CSV, JS, and API routes used by the test suite.

## F. Duplicated or AI-sounding copy

No obvious generated filler or repetitive consulting prose was found on the core public pages. The strongest wording concern was the homepage headline, which was tightened to avoid implying proven care improvement.

## G. Inconsistent terminology

No HIGH terminology issue was found. The site consistently uses "CMS Patient Safety Structural Measure" and "Domain 5: Patient and Family Engagement" on core evidence and toolkit pages.

## H. Evidence / claim-boundary concerns

HIGH: The homepage headline could imply an outcome claim. The revised wording emphasizes accountable action rather than improved care outcomes. Evidence pages continue to distinguish research evidence, lived experience, public Dartmouth Health evidence, local descriptive analysis, and unvalidated local findings.

## I. Mobile/responsive issues

No BLOCKER or HIGH mobile issue was found from source inspection. Existing CSS includes responsive layout adjustments for navigation, analysis controls, chart height, grids, and tables.

## J. Accessibility issues

MEDIUM: The applied-analysis search control used placeholder text for its example. It now has an explicit accessible label and no placeholder attribute in public source.

## K. Visual hierarchy / polish issues

No BLOCKER visual hierarchy issue was found. The strongest polish improvement was to clarify the homepage claim boundary and make hidden reviewer resources easier to discover without replacing page-specific navigation.

## L. Spillover scan findings

Public web source scan found one instance of the term `placeholder` in an HTML input attribute on `/applied-analysis.html`. It was not public narrative copy, but it was removed to satisfy the strict source-level scan. No public web source exposed ChatGPT, OpenAI, Anthropic, Claude, Codex, LLM, system prompt, developer message, tool call, chain of thought, prompt spillover, internal instructions, TODO, FIXME, debug, or test data language.

## M. Exact proposed changes

| Severity | Change |
|---|---|
| HIGH | Revise the homepage headline from outcome-improvement wording to accountable-action wording. |
| HIGH | Add a contextual homepage link to the Reviewer Guide. |
| HIGH | Add a contextual Evidence page link to the Comparative Toolkit Scan. |
| HIGH | Add a contextual Leadership Tools link to the Launch Charter. |
| MEDIUM | Remove the search placeholder attribute from Applied Analysis and keep an accessible label. |
| HIGH | Add regression tests for public source spillover and reviewer-path reachability. |

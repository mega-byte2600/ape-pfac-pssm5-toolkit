# Navigation and Presentation Implementation

## Result

The public toolkit now behaves as one lightweight professional presentation with a reference library behind it. The implementation uses existing HTML and the shared stylesheet only. It adds no framework, package, client-side navigation system, or backend dependency.

## Presentation path

`Home → Executive Brief → Evidence Summary → Applied Analysis → Leadership Tools → APE Deliverables → Home`

All 19 public pages use the same primary links in the same order. The six core pages provide destination-labelled Previous and Next controls. Supporting pages retain direct URLs and provide a named return to Evidence Summary, Applied Analysis, Leadership Tools, or Home.

## Critical resources

Rosie Bartel, HAI Alert, Resources, and About remain available in a slim shortcut row directly below the header and in the same footer location on every page. The homepage also gives those four resources visual priority. The remaining supporting content stays intact in a native, collapsed reference library.

## HAI and payment context

Applied Analysis now identifies the supported national connection between HAI measures and CMS value-based payment programs. The language does not infer Dartmouth Health scores, eligibility, payment adjustments, incentive amounts, or causal effects. The HAI page links to the CMS Hospital Value-Based Purchasing and Hospital-Acquired Condition Reduction Program sources.

## Engineering choices

- Semantic HTML landmarks and native links and disclosure controls
- One shared stylesheet with visible focus, reduced-motion support, and responsive layouts
- No new JavaScript, framework, dependency, route, API, or data change
- Existing charts, downloads, tools, evidence, and claim boundaries preserved
- Two-column mobile primary navigation so every destination remains visible without horizontal clipping

## Verification

- 54 unit and contract tests pass; one optional Playwright test is skipped because Playwright is not installed
- Extended smoke passes across 19 public HTML routes, assets, internal links, navigation, retired routes, and spillover guards
- Faculty review passes
- Production-style smoke passes against the local server
- Python compilation passes
- Desktop rendering verified at 1440 × 1100 in installed Chrome
- Mobile rendering verified in the in-app browser at 319 px wide

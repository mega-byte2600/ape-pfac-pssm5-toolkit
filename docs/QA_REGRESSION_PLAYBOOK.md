# APE QA Regression Playbook

This project uses a best-fit QA ladder for a small agile team preparing a public health-system leadership demo. The goal is fast feedback with enough coverage to protect evidence discipline, navigation, data calculations, browser behavior, architecture boundaries, prompt spillover prevention, and production readiness.

## Architecture Guardrails

The site should stay simple, inspectable, and elegant:

- Static public pages remain the faculty-facing product surface.
- The lightweight Python server handles routing, API payloads, and security headers.
- Evidence, calculations, and public copy stay testable as plain files.
- Supabase integration stays behind the backend interface and must degrade cleanly for demo use.
- Contextual page navigation should remain intact and important assets must stay discoverable.
- Internal review, source-control, build, and prompt language must remain outside the public site.
- The retired `mvp-one.html` and `review-flow.js` assets must remain absent and their routes must return 404.

## Pull Request Gate

Run these checks before opening or updating a PR:

```bash
python3 scripts/extended_public_smoke.py
python3 scripts/faculty_review.py
PYTHONPYCACHEPREFIX=/private/tmp/ape-pycache python3 -m compileall pssm5_toolkit
PYTHONPYCACHEPREFIX=/private/tmp/ape-pycache python3 -m unittest discover -s tests -p 'test_*.py' -v
```

The PR gate must protect:

- Public routes load without homepage fallback.
- Public links resolve to existing routes or static assets.
- Contextual page navigation is preserved.
- Retired routes stay retired and are not linked from public pages.
- Dartmouth Health benchmark language remains a framework until scoring evidence exists.
- Prompt, build, repository, or internal administration language does not leak into the public site.
- CSV-backed calculations reconcile to the source data.
- HAI and applied-analysis Plotly containers remain present.

## White-Box Regression

White-box tests inspect implementation details that are easy to break during development:

- Route handling and fallback behavior.
- Explicit 404 handling for retired public routes.
- Security headers and health payloads.
- CSV-backed calculations and source-data reconciliation.
- Evidence status boundaries and no premature benchmark scoring.
- Public asset serving for CSS, JavaScript, CSV, and API responses.
- Contextual navigation integrity without injected global navigation.

## Black-Box Smoke

Black-box smoke treats the site like a faculty or health-system user would:

- Open the core public pages.
- Follow visible contextual navigation across evidence, benchmark, analysis, tools, story, and about pages.
- Confirm that charts, tables, calls to action, and footer content are visible.
- Confirm that no retired reviewer-guide copy or route is exposed.
- Check desktop, tablet, and mobile viewport behavior when browser tooling is available.
- Confirm the deployed Render revision and public health endpoint after merge.

## Browser And Mobile Smoke

When Playwright is installed, run:

```bash
python3 scripts/browser_smoke.py
```

This checks the highest-value public route set across desktop, tablet, and mobile viewports. It verifies visible page structure, primary navigation, chart containers, footer visibility, horizontal overflow, and absence of retired reviewer-guide content. If Playwright is not installed, the script exits with a clear skip message so CI can distinguish missing browser tooling from a product failure.

## Production Smoke

After Render deploys a merged commit, run:

```bash
python3 scripts/production_smoke.py --expected-sha <commit-sha>
```

Use production smoke to confirm the deployed site is serving the intended revision, core public pages, key JavaScript assets, CSV data, health endpoint, and 404 responses for retired routes.

## Agile Working Agreement

- Keep tests close to the risk being changed.
- Add regression coverage when a faculty-facing route, claim boundary, data calculation, public navigation path, or deployed asset changes.
- Treat failing evidence-boundary tests as product failures, not cosmetic failures.
- Keep retired public routes retired unless the user explicitly re-approves them.
- Do not merge a demo-facing change when extended public smoke fails.
- Prefer clear, small tests over broad brittle snapshots.

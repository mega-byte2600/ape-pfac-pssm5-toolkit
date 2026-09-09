from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "web/evidence-summary.html": [
        "CMS Patient Safety Structural Measure",
        "Domain 5: Patient and Family Engagement",
        "evidence base remains limited",
        "203 respondents",
    ],
    "web/evidence-matrix.html": [
        "Evidence strength / limitation",
        "Anticipated patient benefit",
        "Lewis et al, 2025",
        "Lewis et al, 2026",
        "Rramani Dervishi et al, 2026",
    ],
    "web/story.html": [
        "lived-experience anchor",
        "does not imply endorsement",
        "not research evidence",
        "not representative evidence",
    ],
    "web/deliverables.html": [
        "Two practical deliverables",
        "Environmental scan and annotated bibliography",
        "Deliverable 2 tools",
        "CEPH 4",
        "CEPH 7",
        "Dartmouth Program-Specific Competency 4",
    ],
    "web/hai-alert.html": [
        "Interactive HAI dashboard",
        "hai-trend-chart",
        "hai-baseline-chart",
        "plotly-2.35.2.min.js",
        "Evidence synthesis summary",
    ],
    "web/applied-analysis.html": [
        "Original local analysis",
        "72,736",
        "48.4%",
        "60.5%",
        "47.9%",
        'id="analysis-chart"',
        "plotly-2.35.2.min.js",
        "Implementation demonstration",
        "Host validation required",
        "Planning analysis, not a risk score",
        "not a claim that Dartmouth Health has adopted",
    ],
}

PUBLIC_SPILLOVER = (
    "/research-plan.html",
    "Validation note:",
    "prompt spillover",
    "system prompt",
    "developer message",
    "chain of thought",
    "Reviewer Guide",
    "/mvp-one.html",
    "review-flow.js",
    "Reviewer flow",
)

CLAIM_GUARDRAILS = {
    "web/evidence-matrix.html": [
        "Patient advisors can influence health care outcomes when linked to action and measurement",
        "Improves communication, discharge readiness",
    ],
    "web/hai-alert.html": [
        "Loading HAI dashboard",
        "Reserved for the synthesis text",
        "Drop the final synthesis here",
    ],
    "web/applied-analysis.html": [
        "Dartmouth Health implemented",
        "validated risk score",
        "<canvas",
        "<svg",
    ],
}

RETIRED_PUBLIC_ASSETS = (
    ROOT / "web/research-plan.html",
    ROOT / "web/mvp-one.html",
    ROOT / "web/review-flow.js",
)


def main() -> int:
    failures: list[str] = []

    for retired in RETIRED_PUBLIC_ASSETS:
        if retired.exists():
            failures.append(f"{retired.relative_to(ROOT)}: retired public asset must not be published")

    for path, fragments in REQUIRED.items():
        text = (ROOT / path).read_text(encoding="utf-8")
        folded = text.casefold()
        for fragment in fragments:
            if fragment.casefold() not in folded:
                failures.append(f"{path}: missing faculty contract {fragment!r}")

    for path, fragments in CLAIM_GUARDRAILS.items():
        folded = (ROOT / path).read_text(encoding="utf-8").casefold()
        for fragment in fragments:
            if fragment.casefold() in folded:
                failures.append(f"{path}: prohibited claim or unfinished content {fragment!r}")

    for page in sorted((ROOT / "web").glob("*.html")):
        folded = page.read_text(encoding="utf-8").casefold()
        for fragment in PUBLIC_SPILLOVER:
            if fragment.casefold() in folded:
                failures.append(f"{page.relative_to(ROOT)}: public spillover {fragment!r}")

    if failures:
        print("FACULTY REVIEW: FAIL")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("FACULTY REVIEW: PASS")
    print("Core APE evidence, scope, claim-boundary, visual, local-analysis, retired-route, and public-content contracts are intact.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

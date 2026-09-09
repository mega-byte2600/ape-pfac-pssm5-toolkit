from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "web/evidence-summary.html": [
        "CMS Patient Safety Structural Measure",
        "Domain 5: Patient and Family Engagement",
        "evidence base remains limited",
        "leadership support",
    ],
    "web/evidence-matrix.html": [
        "Domain 5: Patient and Family Engagement",
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
        "two practical deliverables",
        "CEPH 4",
        "CEPH 7",
        "Dartmouth Program-Specific Competency 4",
        "Deliverable 2 tools",
        "Demonstrated.",
    ],
    "web/hai-alert.html": [
        "Interactive HAI dashboard",
        "hai-trend-chart",
        "hai-baseline-chart",
        "plotly-2.35.2.min.js",
        "/app.js",
        "Evidence signal",
        "Evidence synthesis summary",
        "View evidence detail table",
    ],
    "web/applied-analysis.html": [
        "Original local analysis",
        "72,736",
        "48.4%",
        "60.5%",
        "47.9%",
        "Explore the local data",
        'id="analysis-metric"',
        'id="analysis-threshold"',
        'id="analysis-sort"',
        'id="analysis-search"',
        'id="analysis-chart"',
        "plotly-2.35.2.min.js",
        "View municipality data table",
        "/applied-analysis.js",
        "Implementation demonstration",
        "Host validation required",
        "Planning analysis, not a risk score",
        "not a claim that Dartmouth Health has adopted",
    ],
    "web/applied-analysis.js": [
        "/upper-valley-local-analysis.csv",
        "Poverty percent",
        "Disability percent",
        "Age 65+ percent",
        "2023 population",
        "Above service-area average",
        "Plotly.react",
        "Service-area average",
    ],
}

FORBIDDEN = {
    "web/evidence-summary.html": [
        "Chick-fil-A",
        "McDonald",
        "Patients over payers",
        "industry-grade",
        "APE/ILE",
        "Integrated Learning Experience",
    ],
    "web/story.html": [
        "Patients over payers",
        "patient-safety source",
    ],
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
        "improved patient outcomes",
        "validated risk score",
        "<canvas",
        "<svg",
    ],
}

# These are specifically internal/generation artifacts that should never be
# visible on a public APE page. Keep this list narrow so the gate does not
# reject legitimate academic, implementation, or technical terminology.
PUBLIC_SPILLOVER = [
    "/research-plan.html",
    "Validation note:",
    "prompt spillover",
    "system prompt",
    "developer message",
    "chain of thought",
]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []

    if (ROOT / "web/research-plan.html").exists():
        failures.append("web/research-plan.html: internal review-method page must not be published")

    for path, fragments in REQUIRED.items():
        text = read(path)
        folded = text.casefold()
        for fragment in fragments:
            if fragment.casefold() not in folded:
                failures.append(f"{path}: missing faculty gate {fragment!r}")

    for path, fragments in FORBIDDEN.items():
        text = read(path).casefold()
        for fragment in fragments:
            if fragment.casefold() in text:
                failures.append(f"{path}: prohibited faculty-facing phrasing {fragment!r}")

    for page in sorted((ROOT / "web").glob("*.html")):
        text = page.read_text(encoding="utf-8").casefold()
        for fragment in PUBLIC_SPILLOVER:
            if fragment.casefold() in text:
                failures.append(f"{page.relative_to(ROOT)}: public spillover {fragment!r}")

    if failures:
        print("FACULTY REVIEW: FAIL")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("FACULTY REVIEW: PASS")
    print("Core APE pages meet evidence, local-analysis, implementation, approved-visual, scope, and public-spillover gates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

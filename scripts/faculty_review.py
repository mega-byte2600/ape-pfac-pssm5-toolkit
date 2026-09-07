from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = {
    "web/evidence-summary.html": [
        "PSSM Domain 5",
        "evidence remains limited",
        "separate ILE",
    ],
    "web/research-plan.html": [
        "non-research APE",
        "Search lane 1",
        "Screening workflow",
        "confirmation bias",
    ],
    "web/evidence-matrix.html": [
        "PSSM Domain 5",
        "Evidence strength / limitation",
        "Anticipated patient benefit",
        "Rramani Dervishi",
    ],
    "web/story.html": [
        "lived-experience anchor",
        "does not imply endorsement",
        "not research evidence",
    ],
    "web/deliverables.html": [
        "two practical deliverables",
        "CEPH 4",
        "CEPH 7",
        "Dartmouth Program-Specific Competency 4",
    ],
}

FORBIDDEN = {
    "web/evidence-summary.html": [
        "Chick-fil-A",
        "McDonald",
        "Patients over payers",
        "industry-grade",
    ],
    "web/story.html": [
        "Patients over payers",
    ],
    "web/evidence-matrix.html": [
        "Patient advisors can influence health care outcomes when linked to action and measurement",
        "Improves communication, discharge readiness",
    ],
}


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def main() -> int:
    failures: list[str] = []

    for path, fragments in REQUIRED.items():
        text = read(path)
        for fragment in fragments:
            if fragment not in text:
                failures.append(f"{path}: missing faculty gate {fragment!r}")

    for path, fragments in FORBIDDEN.items():
        text = read(path)
        for fragment in fragments:
            if fragment.lower() in text.lower():
                failures.append(f"{path}: prohibited faculty-facing phrasing {fragment!r}")

    if failures:
        print("FACULTY REVIEW: FAIL")
        for failure in failures:
            print(f" - {failure}")
        return 1

    print("FACULTY REVIEW: PASS")
    print("Core APE pages meet the automated faculty-content gates.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

from __future__ import annotations

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web"

NAV_ITEMS = [
    ("Executive Brief", "/executive-launch.html"),
    ("Evidence", "/evidence-summary.html"),
    ("DH Benchmark", "/dh-benchmark.html"),
    ("Applied Analysis", "/applied-analysis.html"),
    ("Tools", "/toolkit-tools.html"),
    ("Method", "/research-plan.html"),
    ("APE Deliverables", "/deliverables.html"),
]

ACTIVE_PAGE = {
    "executive-launch.html": "/executive-launch.html",
    "evidence-summary.html": "/evidence-summary.html",
    "dh-benchmark.html": "/dh-benchmark.html",
    "applied-analysis.html": "/applied-analysis.html",
    "toolkit-tools.html": "/toolkit-tools.html",
    "research-plan.html": "/research-plan.html",
    "deliverables.html": "/deliverables.html",
}

NAV_RE = re.compile(r'<nav\s+aria-label="Primary"[^>]*>.*?</nav>', re.DOTALL)
CSS_MARKER = "/* Global navigation current-page state */"


def canonical_nav(filename: str) -> str:
    active_href = ACTIVE_PAGE.get(filename)
    links = []
    for label, href in NAV_ITEMS:
        current = ' aria-current="page"' if href == active_href else ""
        links.append(f'<a href="{href}"{current}>{label}</a>')
    return '<nav aria-label="Primary" data-global-nav="true">' + "".join(links) + "</nav>"


def normalize_html() -> list[str]:
    changed: list[str] = []
    failures: list[str] = []

    for page in sorted(WEB.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        matches = list(NAV_RE.finditer(text))
        if len(matches) != 1:
            failures.append(f"{page.name}: expected exactly one Primary nav, found {len(matches)}")
            continue

        updated = NAV_RE.sub(canonical_nav(page.name), text, count=1)
        if updated != text:
            page.write_text(updated, encoding="utf-8")
            changed.append(str(page.relative_to(ROOT)))

    if failures:
        raise SystemExit("Navigation normalization stopped:\n" + "\n".join(failures))
    return changed


def normalize_css() -> bool:
    css_path = WEB / "styles.css"
    css = css_path.read_text(encoding="utf-8")
    if CSS_MARKER in css:
        return False

    addition = """

/* Global navigation current-page state */
nav[data-global-nav="true"] a[aria-current="page"] {
  color: var(--dartmouth-green);
  background: rgba(0, 105, 62, .10);
  box-shadow: inset 0 0 0 1px rgba(0, 105, 62, .14);
}
"""
    css_path.write_text(css.rstrip() + addition + "\n", encoding="utf-8")
    return True


def main() -> int:
    changed = normalize_html()
    if normalize_css():
        changed.append("web/styles.css")

    print(f"Normalized global navigation on {len(changed)} files.")
    for path in changed:
        print(f" - {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

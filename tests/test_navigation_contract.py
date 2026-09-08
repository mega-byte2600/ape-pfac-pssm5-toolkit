from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
import unittest

from pssm5_toolkit.server import application


EXPECTED_NAV = [
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


class PrimaryNavParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.in_primary = False
        self.primary_count = 0
        self.global_marker_count = 0
        self.links: list[dict[str, str]] = []
        self._current: dict[str, str] | None = None

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = {key: value or "" for key, value in attrs}
        if tag == "nav" and attributes.get("aria-label") == "Primary":
            self.in_primary = True
            self.primary_count += 1
            if attributes.get("data-global-nav") == "true":
                self.global_marker_count += 1
            return

        if self.in_primary and tag == "a":
            self._current = {
                "href": attributes.get("href", ""),
                "aria-current": attributes.get("aria-current", ""),
                "text": "",
            }

    def handle_data(self, data: str) -> None:
        if self._current is not None:
            self._current["text"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "a" and self._current is not None:
            self._current["text"] = " ".join(self._current["text"].split())
            self.links.append(self._current)
            self._current = None
        elif tag == "nav" and self.in_primary:
            self.in_primary = False


def request(path: str):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    body = b"".join(application({"PATH_INFO": path, "REQUEST_METHOD": "GET"}, start_response)).decode("utf-8")
    return captured["status"], captured["headers"], body


class NavigationContractTests(unittest.TestCase):
    def test_every_public_html_page_uses_same_global_navigation(self):
        expected_pairs = EXPECTED_NAV
        for page in sorted(Path("web").glob("*.html")):
            with self.subTest(page=page.name):
                parser = PrimaryNavParser()
                parser.feed(page.read_text(encoding="utf-8"))
                self.assertEqual(parser.primary_count, 1, f"{page.name} must have exactly one Primary nav")
                self.assertEqual(parser.global_marker_count, 1, f"{page.name} must use the canonical global nav")
                observed = [(item["text"], item["href"]) for item in parser.links]
                self.assertEqual(observed, expected_pairs, f"{page.name} changed global nav labels, destinations, or order")

    def test_canonical_destination_pages_mark_only_the_current_page(self):
        for page in sorted(Path("web").glob("*.html")):
            with self.subTest(page=page.name):
                parser = PrimaryNavParser()
                parser.feed(page.read_text(encoding="utf-8"))
                marked = [item for item in parser.links if item["aria-current"]]
                expected_href = ACTIVE_PAGE.get(page.name)
                if expected_href:
                    self.assertEqual(len(marked), 1, f"{page.name} must mark exactly one current page")
                    self.assertEqual(marked[0]["href"], expected_href)
                    self.assertEqual(marked[0]["aria-current"], "page")
                else:
                    self.assertEqual(marked, [], f"{page.name} must not mark a parent section as the current page")

    def test_all_global_navigation_destinations_resolve(self):
        for label, href in EXPECTED_NAV:
            with self.subTest(label=label, href=href):
                status, headers, _ = request(href)
                self.assertEqual(status, "200 OK")
                self.assertIn("text/html", headers["Content-Type"])

    def test_global_navigation_active_style_exists(self):
        css = Path("web/styles.css").read_text(encoding="utf-8")
        self.assertIn('nav[data-global-nav="true"] a[aria-current="page"]', css)


if __name__ == "__main__":
    unittest.main()

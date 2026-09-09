"""Extended public smoke and spillover checks for the APE toolkit."""

from __future__ import annotations

import re
import sys
from html.parser import HTMLParser
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from pssm5_toolkit.server import application


WEB = Path("web")
PUBLIC_SPILLOVER = (
    "system prompt",
    "developer message",
    "tool call",
    "chain of thought",
    "prompt spillover",
    "internal instructions",
    "acceptance criteria",
    "raw prompt",
    "ChatGPT",
    "OpenAI",
    "Anthropic",
    "Claude",
    "Codex",
    "large language model",
    "GitHub",
    "source control",
    "CI/CD",
    "repository",
    "MVP 1",
    "APE/ILE",
    "Integrated Learning Experience",
)
UNFINISHED_COPY = (
    "Reserved for the synthesis text",
    "Drop the final synthesis here",
    "Loading HAI dashboard",
    "coming soon",
    "TODO",
    "FIXME",
    "debug",
)
RAW_MARKDOWN = ("**", "```", "### ", "## ")


class LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []
        self.nav_labels: list[str] = []
        self.main_count = 0
        self.footer_count = 0

    def handle_starttag(self, tag: str, attrs) -> None:
        attrs_dict = dict(attrs)
        if tag == "a" and attrs_dict.get("href"):
            self.links.append(attrs_dict["href"])
        if tag == "nav":
            self.nav_labels.append(attrs_dict.get("aria-label", ""))
        if tag == "main":
            self.main_count += 1
        if tag == "footer":
            self.footer_count += 1


def request(path: str) -> tuple[str, dict[str, str], str]:
    captured: dict[str, object] = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    environ = {
        "PATH_INFO": path,
        "REQUEST_METHOD": "GET",
        "CONTENT_LENGTH": "0",
        "wsgi.input": BytesIO(b""),
    }
    body = b"".join(application(environ, start_response)).decode("utf-8")
    return str(captured["status"]), captured["headers"], body  # type: ignore[return-value]


def public_routes() -> dict[str, Path]:
    routes = {"/": WEB / "index.html"}
    routes.update({f"/{path.name}": path for path in sorted(WEB.glob("*.html")) if path.name != "index.html"})
    return routes


def assert_public_smoke() -> list[str]:
    failures: list[str] = []
    routes = public_routes()

    if (WEB / "research-plan.html").exists():
        failures.append("Retired public research-plan.html is present")

    for route, path in routes.items():
        status, headers, body = request(route)
        if status != "200 OK":
            failures.append(f"{route} returned {status}")
            continue
        if "text/html" not in headers.get("Content-Type", ""):
            failures.append(f"{route} did not return HTML")
        if route != "/" and "Turn patient voice into accountable action." in body:
            failures.append(f"{route} appears to fall back to the homepage")
        if '<script defer src="/review-flow.js"></script>' not in body:
            failures.append(f"{route} is missing reviewer-flow script")

        parser = LinkParser()
        parser.feed(body)
        if parser.nav_labels.count("Primary") != 1:
            failures.append(f"{route} should keep exactly one Primary navigation")
        if parser.main_count != 1:
            failures.append(f"{route} should have exactly one main element")
        if parser.footer_count != 1:
            failures.append(f"{route} should have exactly one footer")

        lowered = body.casefold()
        for fragment in PUBLIC_SPILLOVER + UNFINISHED_COPY:
            if fragment.casefold() in lowered:
                failures.append(f"{route} exposes {fragment!r}")
        for fragment in RAW_MARKDOWN:
            if fragment in body:
                failures.append(f"{route} exposes raw markdown artifact {fragment!r}")

        for href in parser.links:
            parsed = urlparse(href)
            if parsed.scheme or href.startswith("mailto:") or href.startswith("#"):
                continue
            if parsed.path not in routes and not (WEB / parsed.path.lstrip("/")).is_file():
                failures.append(f"{route} links to missing internal target {href}")

    for asset in ("/styles.css", "/app.js", "/applied-analysis.js", "/review-flow.js"):
        status, headers, body = request(asset)
        if status != "200 OK":
            failures.append(f"{asset} returned {status}")
        if asset.endswith(".js") and "javascript" not in headers.get("Content-Type", ""):
            failures.append(f"{asset} did not return JavaScript")
        if asset == "/review-flow.js":
            for href in re.findall(r'href: "([^"]+)"', body):
                if href not in routes:
                    failures.append(f"review-flow.js links to missing public route {href}")
            if "github.com" in body.casefold():
                failures.append("review-flow.js exposes a GitHub link")

    dh_body = request("/dh-benchmark.html")[2]
    for phrase in ("Benchmark maturity model", "maturity score", "completed scorecard"):
        if phrase.casefold() in dh_body.casefold():
            failures.append(f"DH benchmark overclaims with {phrase!r}")
    rows = [segment.split("</tr>", 1)[0] for segment in dh_body.split("<tr") if "data-evidence-status" in segment]
    for row in rows:
        statuses = [
            status
            for status in ("publicly-supported", "not-yet-validated", "insufficient-evidence", "preliminary-finding")
            if f'data-evidence-status="{status}"' in row
        ]
        if len(statuses) != 1:
            failures.append("DH benchmark mixes public and unvalidated evidence statuses")

    return failures


def main() -> int:
    failures = assert_public_smoke()
    if failures:
        print("EXTENDED PUBLIC SMOKE: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("EXTENDED PUBLIC SMOKE: PASS")
    print(f"Checked {len(public_routes())} public HTML routes, core assets, links, navigation shape, and spillover terms.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

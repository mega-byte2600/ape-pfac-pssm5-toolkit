"""Optional Playwright browser smoke checks for desktop and mobile layouts."""

from __future__ import annotations

import argparse
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.request import urlopen


ROOT = Path(__file__).resolve().parents[1]
ROUTES = (
    "/",
    "/evidence-summary.html",
    "/dh-benchmark.html",
    "/applied-analysis.html",
    "/hai-alert.html",
    "/toolkit-tools.html",
    "/about.html",
)
VIEWPORTS = (
    ("desktop", 1440, 1000),
    ("tablet", 900, 1100),
    ("mobile", 390, 844),
)
FORBIDDEN_COPY = ("Reviewer Guide", "/mvp-one.html", "Reviewer flow")


def find_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


def wait_for_server(base_url: str) -> None:
    deadline = time.time() + 12
    while time.time() < deadline:
        try:
            with urlopen(f"{base_url}/api/health", timeout=1) as response:
                if response.status == 200:
                    return
        except OSError:
            time.sleep(0.25)
    raise RuntimeError("local server did not become ready")


def run_browser_smoke(screenshots_dir: Path | None = None) -> list[str]:
    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError:
        return ["SKIP: Playwright is not installed in this environment"]

    port = find_port()
    base_url = f"http://127.0.0.1:{port}"
    proc = subprocess.Popen(
        [sys.executable, "-m", "pssm5_toolkit.server"],
        cwd=ROOT,
        env={**os.environ, "PORT": str(port)},
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    failures: list[str] = []
    try:
        wait_for_server(base_url)
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            try:
                for label, width, height in VIEWPORTS:
                    context = browser.new_context(viewport={"width": width, "height": height})
                    page = context.new_page()
                    for route in ROUTES:
                        page.goto(f"{base_url}{route}", wait_until="domcontentloaded")
                        if page.locator('nav[aria-label="Primary"]').count() != 1:
                            failures.append(f"{label} {route}: primary navigation count changed")
                        if not page.locator("main").first.is_visible():
                            failures.append(f"{label} {route}: main content is not visible")
                        if not page.locator("footer").first.is_visible():
                            failures.append(f"{label} {route}: footer is not visible")
                        body_text = page.locator("body").inner_text()
                        body_html = page.content()
                        for forbidden in FORBIDDEN_COPY:
                            if forbidden.casefold() in body_text.casefold() or forbidden.casefold() in body_html.casefold():
                                failures.append(f"{label} {route}: retired reviewer-guide content is visible: {forbidden}")

                        if route == "/toolkit-tools.html":
                            if page.locator("#leadership-tool-select").count() != 1:
                                failures.append(f"{label} {route}: working-tool selector is missing")
                            if page.locator("#leadership-focus-select").count() != 1:
                                failures.append(f"{label} {route}: focus selector is missing")
                            if page.locator("details.audit-table-details").count() < 5:
                                failures.append(f"{label} {route}: full audit tables are not preserved")
                            if not page.locator("#assessment").is_visible():
                                failures.append(f"{label} {route}: default assessment tool is not visible")

                            page.select_option("#leadership-tool-select", "measurement")
                            if not page.locator("#measurement").is_visible():
                                failures.append(f"{label} {route}: measurement tool did not activate")
                            if page.locator("#assessment").is_visible():
                                failures.append(f"{label} {route}: inactive assessment tool remained visible")
                            page.select_option("#leadership-focus-select", "2")
                            summary_text = page.locator("#leadership-tool-summary").inner_text()
                            if "Association does not establish downstream clinical effect." not in summary_text:
                                failures.append(f"{label} {route}: measurement caution did not render in focused summary")

                            page.select_option("#leadership-tool-select", "launch")
                            if not page.locator("#launch").is_visible():
                                failures.append(f"{label} {route}: 90-day plan did not activate")
                            if page.locator("#leadership-focus-wrap").is_visible():
                                failures.append(f"{label} {route}: focus selector should hide for the 90-day plan")

                        overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth + 2")
                        if overflow:
                            failures.append(f"{label} {route}: page has horizontal viewport overflow")
                        if route in ("/applied-analysis.html", "/hai-alert.html"):
                            if page.locator("[id$='chart']").count() < 1:
                                failures.append(f"{label} {route}: chart containers are missing")
                    if screenshots_dir:
                        screenshots_dir.mkdir(parents=True, exist_ok=True)
                        page.goto(f"{base_url}/", wait_until="domcontentloaded")
                        page.screenshot(path=screenshots_dir / f"{label}-home.png", full_page=True)
                    context.close()
            finally:
                browser.close()
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=4)
        except subprocess.TimeoutExpired:
            proc.kill()
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--screenshots-dir", type=Path)
    args = parser.parse_args()
    failures = run_browser_smoke(args.screenshots_dir)
    if failures and failures[0].startswith("SKIP:"):
        print(failures[0])
        return 77
    if failures:
        print("BROWSER SMOKE: FAIL")
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("BROWSER SMOKE: PASS")
    print(f"Checked {len(ROUTES)} routes across {len(VIEWPORTS)} desktop/tablet/mobile viewports.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

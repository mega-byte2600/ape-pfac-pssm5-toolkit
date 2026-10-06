"""Systemic frontend integration invariants.

Prevents shipping a browser controller that is never loaded and prevents
interactive pages from existing outside the Playwright smoke matrix.
"""
from __future__ import annotations

import re
import unittest
from pathlib import Path

from scripts.browser_smoke import ROUTES

WEB = Path("web")
SCRIPT_RE = re.compile(r'<script[^>]+src=["\'](/[^"\']+\.js(?:\?[^"\']*)?)["\']', re.IGNORECASE)
GLOBAL_SCRIPTS = {"/app.js"}


def _local_scripts(html: str) -> set[str]:
    return {src.split("?", 1)[0] for src in SCRIPT_RE.findall(html)}


class FrontendIntegrationContractTest(unittest.TestCase):
    def test_every_local_browser_script_is_loaded_by_public_html(self):
        html_text = "\n".join(path.read_text(encoding="utf-8") for path in WEB.glob("*.html"))
        referenced = set()
        for src in SCRIPT_RE.findall(html_text):
            referenced.add(src.split("?", 1)[0])

        local_scripts = {"/" + path.name for path in WEB.glob("*.js")}
        orphaned = sorted(local_scripts - referenced)
        self.assertEqual(
            orphaned,
            [],
            "Local browser JavaScript exists but is not loaded by any HTML page: "
            + ", ".join(orphaned),
        )

    def test_every_interactive_page_is_in_browser_smoke_matrix(self):
        interactive_routes = set()
        for path in WEB.glob("*.html"):
            scripts = _local_scripts(path.read_text(encoding="utf-8")) - GLOBAL_SCRIPTS
            if not scripts:
                continue
            route = "/" if path.name == "index.html" else "/" + path.name
            interactive_routes.add(route)

        missing = sorted(interactive_routes - set(ROUTES))
        self.assertEqual(
            missing,
            [],
            "Interactive public pages missing from Browser Smoke ROUTES: "
            + ", ".join(missing),
        )


if __name__ == "__main__":
    unittest.main()

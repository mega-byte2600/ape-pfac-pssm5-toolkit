from __future__ import annotations

import importlib.util
import unittest

from scripts.browser_smoke import run_browser_smoke


class BrowserSmokeTests(unittest.TestCase):
    def test_playwright_desktop_and_mobile_smoke(self):
        if importlib.util.find_spec("playwright") is None:
            self.skipTest("Playwright is not installed in this environment")
        self.assertEqual(run_browser_smoke(), [])


if __name__ == "__main__":
    unittest.main()

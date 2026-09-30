"""Presentation-only regression guard for the featured HCAHPS Resources panel."""

from pathlib import Path
import unittest


class HCAHPSFeaturedPresentationTest(unittest.TestCase):
    def test_hcahps_is_featured_without_new_runtime_dependencies(self):
        html = Path("web/resources.html").read_text(encoding="utf-8")
        section_start = html.index('id="cms-hcahps-explorer"')
        section = html[max(0, section_start - 120):section_start + 1400]

        self.assertIn("highlight-panel", section)
        self.assertIn("Featured live resource", section)
        self.assertIn("CMS Open Data API", section)
        self.assertIn('id="hcahps-explorer-form"', section)

        # Internal project shorthand must never become public copy.
        self.assertNotIn("Carpe Data", html)
        self.assertNotIn("CARPE DATA", html)

    def test_feature_change_does_not_touch_hai_or_add_scripts(self):
        html = Path("web/resources.html").read_text(encoding="utf-8")
        self.assertIn('<a href="/hai-alert.html">HAI Alert</a>', html)
        self.assertEqual(html.count('src="/hcahps-explorer.js"'), 1)
        self.assertEqual(html.count('src="/live-data.js"'), 1)


if __name__ == "__main__":
    unittest.main()

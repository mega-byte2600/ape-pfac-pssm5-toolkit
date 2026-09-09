from __future__ import annotations

import unittest

from scripts.extended_public_smoke import assert_public_smoke


class ExtendedPublicSmokeTests(unittest.TestCase):
    def test_extended_public_smoke_and_spillover_scan_passes(self):
        self.assertEqual(assert_public_smoke(), [])


if __name__ == "__main__":
    unittest.main()

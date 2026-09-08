from __future__ import annotations

import json
import os
import unittest
from io import BytesIO
from unittest.mock import patch

from pssm5_toolkit.server import application


def request(path: str):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    environ = {
        "PATH_INFO": path,
        "REQUEST_METHOD": "GET",
        "CONTENT_LENGTH": "0",
        "wsgi.input": BytesIO(b""),
    }
    body = b"".join(application(environ, start_response))
    return captured["status"], captured["headers"], body


class PlatformHardeningTests(unittest.TestCase):
    def test_health_reports_deployed_revision(self):
        with patch.dict(os.environ, {"RENDER_GIT_COMMIT": "abc123release"}, clear=False):
            status, headers, body = request("/api/health")
        payload = json.loads(body)
        self.assertEqual(status, "200 OK")
        self.assertEqual(payload["status"], "ok")
        self.assertEqual(payload["service"], "ape-pfac-pssm5-toolkit")
        self.assertEqual(payload["release"], "abc123release")
        self.assertEqual(headers["Cache-Control"], "no-store")

    def test_security_headers_cover_html_and_json(self):
        for path in ("/", "/api/health"):
            with self.subTest(path=path):
                status, headers, _ = request(path)
                self.assertEqual(status, "200 OK")
                self.assertEqual(headers["X-Content-Type-Options"], "nosniff")
                self.assertEqual(headers["Referrer-Policy"], "strict-origin-when-cross-origin")


if __name__ == "__main__":
    unittest.main()

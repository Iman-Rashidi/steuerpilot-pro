from __future__ import annotations

import io
import unittest
from unittest.mock import patch

import crypto_super_radar_portal as portal


class _FakeResponse:
    status = 200
    reason = "OK"

    def __init__(self, payload: bytes, content_type: str = "text/html; charset=utf-8"):
        self.payload = payload
        self.content_type = content_type

    def read(self):
        return self.payload

    def getheader(self, name, default=None):
        return self.content_type if name.lower() == "content-type" else default


class _FakeConnection:
    last_request = None

    def __init__(self, host, port, timeout):
        self.host = host
        self.port = port
        self.timeout = timeout

    def request(self, method, target, body=None, headers=None):
        type(self).last_request = (method, target, body, headers)

    def getresponse(self):
        return _FakeResponse(
            b'<!doctype html><html><head><style>main{max-width:980px;margin:auto}</style>'
            b'</head><body><main><form method="post" action="/scan">'
            b'<script>fetch(\'/jobs/abc\')</script></main></body></html>'
        )

    def close(self):
        pass


class CryptoPortalProxyTests(unittest.TestCase):
    def test_dashboard_rewrites_paths_and_adds_wide_portal_navigation(self):
        source = (
            b'<html><head><style>main{max-width:980px;margin:auto}</style></head>'
            b'<body><main><form method="post" action="/scan">'
            b'<script>fetch(\'/jobs/abc\')</script></main></body></html>'
        )
        rendered = portal._rewrite_dashboard(source).decode("utf-8")
        self.assertIn('action="/crypto-radar/scan"', rendered)
        self.assertIn("fetch('/crypto-radar/jobs/", rendered)
        self.assertIn("max-width:1680px", rendered)
        self.assertIn('href="/invoice"', rendered)
        self.assertIn('href="/reinigungsradar"', rendered)
        self.assertIn('href="/crypto-radar"', rendered)

    def test_proxy_strips_mount_prefix_and_does_not_forward_origin(self):
        environ = {
            "PATH_INFO": "/crypto-radar/scan",
            "QUERY_STRING": "",
            "REQUEST_METHOD": "POST",
            "CONTENT_LENGTH": "19",
            "CONTENT_TYPE": "application/x-www-form-urlencoded",
            "HTTP_ORIGIN": "https://steuerpilot-pro-v2.onrender.com",
            "HTTP_HOST": "steuerpilot-pro-v2.onrender.com",
            "wsgi.url_scheme": "https",
            "wsgi.input": io.BytesIO(b"asset=cex%3ABTCUSDT"),
        }
        captured = {}

        def start_response(status, headers):
            captured["status"] = status
            captured["headers"] = dict(headers)

        with patch.object(portal, "_upstream_port", return_value=12345), patch.object(
            portal.http.client, "HTTPConnection", _FakeConnection
        ):
            response = b"".join(portal.proxy_crypto_request(environ, start_response))

        method, target, body, headers = _FakeConnection.last_request
        self.assertEqual(method, "POST")
        self.assertEqual(target, "/scan")
        self.assertEqual(body, b"asset=cex%3ABTCUSDT")
        self.assertEqual(headers.get("Content-Type"), "application/x-www-form-urlencoded")
        self.assertNotIn("Origin", headers)
        self.assertEqual(captured["status"], "200 OK")
        self.assertIn(b"/crypto-radar/jobs/", response)

    def test_unmounted_path_is_not_proxied(self):
        captured = {}
        response = portal.proxy_crypto_request(
            {"PATH_INFO": "/invoice"}, lambda status, headers: captured.update(status=status)
        )
        self.assertEqual(captured["status"], "404 Not Found")
        self.assertEqual(b"".join(response), b"Not found")


if __name__ == "__main__":
    unittest.main()

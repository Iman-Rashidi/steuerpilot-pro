import unittest
from urllib.parse import parse_qs, urlsplit

from steuerpilot.radar_sso import (
    build_radar_embed_url,
    create_portal_session,
    verify_portal_password,
    verify_portal_session,
)


SECRET = "test-only-secret-material-with-at-least-32-characters"
RADAR_URL = "https://reinigungsai-pr7-staging.onrender.com"


class RadarSSOTests(unittest.TestCase):
    def test_embed_url_contains_short_lived_signed_token(self):
        url = build_radar_embed_url(RADAR_URL, SECRET, now=1_800_000_000)
        parts = urlsplit(url)
        params = parse_qs(parts.query)
        self.assertEqual(parts.hostname, "reinigungsai-pr7-staging.onrender.com")
        self.assertEqual(params["embed"], ["true"])
        self.assertEqual(len(params["sso"][0].split(".")), 2)

    def test_rejects_non_staging_hosts(self):
        with self.assertRaises(ValueError):
            build_radar_embed_url("https://reinigungsai.onrender.com", SECRET)

    def test_rejects_plain_http(self):
        with self.assertRaises(ValueError):
            build_radar_embed_url("http://reinigungsai-pr7-staging.onrender.com", SECRET)

    def test_portal_password_requires_long_configured_value(self):
        self.assertTrue(verify_portal_password("pilot-password-123456", "pilot-password-123456"))
        self.assertFalse(verify_portal_password("short", "short"))

    def test_signed_portal_session_expires(self):
        token = create_portal_session(SECRET, now=1_800_000_000)
        self.assertTrue(verify_portal_session(token, SECRET, now=1_800_000_100))
        self.assertFalse(verify_portal_session(token, SECRET, now=1_800_028_801))


if __name__ == "__main__":
    unittest.main()

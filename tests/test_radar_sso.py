import base64
import json
import unittest
from urllib.parse import parse_qs, urlsplit

from steuerpilot.radar_sso import (
    TOKEN_TTL_SECONDS,
    build_radar_embed_url,
    get_radar_sso_secret,
)


SECRET = "test-only-secret-material-with-at-least-32-characters"
RADAR_URL = "https://reinigungsai-pr7-staging.onrender.com"


class RadarSSOTests(unittest.TestCase):
    def test_embed_url_contains_short_lived_signed_token(self):
        url = build_radar_embed_url(RADAR_URL, SECRET, now=1_800_000_000)
        parts = urlsplit(url)
        params = parse_qs(parts.query)
        self.assertEqual(parts.scheme, "https")
        self.assertEqual(parts.hostname, "reinigungsai-pr7-staging.onrender.com")
        self.assertEqual(params["embed"], ["true"])
        token = params["sso"][0]
        self.assertEqual(len(token.split(".")), 2)
        payload = token.split(".")[0]
        claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
        self.assertEqual(claims["iss"], "steuerpilot-pro")
        self.assertEqual(claims["aud"], "reinigungsradar")
        self.assertEqual(claims["sub"], "demo-admin")
        self.assertEqual(claims["exp"] - claims["iat"], TOKEN_TTL_SECONDS)

    def test_rejects_non_staging_hosts(self):
        with self.assertRaises(ValueError):
            build_radar_embed_url("https://reinigungsai.onrender.com", SECRET)

    def test_rejects_plain_http(self):
        with self.assertRaises(ValueError):
            build_radar_embed_url("http://reinigungsai-pr7-staging.onrender.com", SECRET)

    def test_rejects_url_with_existing_query_or_userinfo(self):
        with self.assertRaises(ValueError):
            build_radar_embed_url(RADAR_URL + "/?sso=anything", SECRET)
        with self.assertRaises(ValueError):
            build_radar_embed_url("https://user:pass@reinigungsai-pr7-staging.onrender.com", SECRET)

    def test_rejects_short_secret(self):
        with self.assertRaises(ValueError):
            build_radar_embed_url(RADAR_URL, "too-short")

    def test_reads_canonical_secret_name(self):
        self.assertEqual(
            get_radar_sso_secret({"STEUERPILOT_RADAR_SSO_SECRET": "  " + SECRET + "  "}),
            SECRET,
        )

    def test_supports_existing_legacy_secret_name(self):
        self.assertEqual(
            get_radar_sso_secret({"STEUEERPILOT_RADAR_SSO_SECRET": SECRET}),
            SECRET,
        )

    def test_canonical_secret_takes_precedence(self):
        other = SECRET + "-canonical"
        self.assertEqual(
            get_radar_sso_secret({
                "STEUERPILOT_RADAR_SSO_SECRET": other,
                "STEUEERPILOT_RADAR_SSO_SECRET": SECRET,
            }),
            other,
        )


if __name__ == "__main__":
    unittest.main()

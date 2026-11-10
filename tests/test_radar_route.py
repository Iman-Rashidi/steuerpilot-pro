import unittest
from io import BytesIO

from demo_app import application


def request(path, method="GET"):
    captured = {}

    def start_response(status, headers):
        captured["status"] = status
        captured["headers"] = dict(headers)

    environ = {
        "REQUEST_METHOD": method,
        "PATH_INFO": path,
        "QUERY_STRING": "",
        "CONTENT_LENGTH": "0",
        "wsgi.input": BytesIO(b""),
        "HTTP_COOKIE": "",
    }
    body = b"".join(application(environ, start_response)).decode("utf-8")
    return captured["status"], captured["headers"], body


class RadarRouteTests(unittest.TestCase):
    def test_radar_route_embeds_passwordless_staging_app_without_sso(self):
        status, headers, body = request("/reinigungsradar")

        self.assertEqual(status, "200 OK")
        self.assertIn("text/html", headers.get("Content-Type", ""))
        self.assertIn("<iframe", body)
        self.assertIn('src="https://reinigungsai-pr7-staging.onrender.com/"', body)
        self.assertNotIn("sso=", body)
        self.assertNotIn("embed=true", body)
        self.assertNotIn("type=\"password\"", body)
        self.assertNotIn("/radar-login", body)

    def test_radar_route_does_not_depend_on_sso_environment_variables(self):
        status, _, body = request("/reinigungsradar")
        self.assertEqual(status, "200 OK")
        self.assertIn("ReinigungsRadar NRW", body)
        self.assertNotIn("ورود یکپارچه هنوز آماده نیست", body)

    def test_legacy_password_route_is_removed(self):
        status, _, _ = request("/radar-login")
        self.assertEqual(status, "404 Not Found")


if __name__ == "__main__":
    unittest.main()


class CryptoDashboardCardTests(unittest.TestCase):
    def test_crypto_card_is_visible_but_not_linked_before_validation(self):
        status, _, body = request("/")
        self.assertEqual(status, "200 OK")
        self.assertIn("Crypto Super Radar", body)
        self.assertIn("در حال اعتبارسنجی منابع داده", body)
        self.assertIn("دسترسی پس از تأیید فنی", body)
        self.assertNotIn('href="/crypto-radar"', body)


class ExchangeCenterTests(unittest.TestCase):
    def test_exchange_center_contains_primary_exchanges_and_wallets(self):
        status, _, body = request("/")
        self.assertEqual(status, "200 OK")
        for name in ("Binance", "Bybit", "OKX", "KuCoin", "Kraken", "Coinbase", "Bitget", "Gate.io", "MEXC", "Trust Wallet", "MetaMask"):
            self.assertIn(name, body)
        self.assertIn('id="exchange-center"', body)
        self.assertIn('id="exchange-grid"', body)

    def test_custom_exchange_controls_and_persistence_are_present(self):
        status, _, body = request("/")
        self.assertEqual(status, "200 OK")
        self.assertIn('id="exchange-form"', body)
        self.assertIn("localStorage", body)
        self.assertIn("EXCHANGE_STORAGE_KEY", body)
        self.assertIn("editExchange", body)
        self.assertIn("deleteExchange", body)

    def test_custom_exchange_links_are_restricted_to_https_and_open_safely(self):
        status, _, body = request("/")
        self.assertEqual(status, "200 OK")
        self.assertIn("u.protocol==='https:'", body)
        self.assertIn("open.target='_blank'", body)
        self.assertIn("open.rel='noopener noreferrer'", body)
        self.assertIn("!u.username&&!u.password", body)


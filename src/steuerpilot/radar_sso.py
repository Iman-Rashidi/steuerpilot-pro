"""Short-lived staging SSO and signed browser-session helpers."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from urllib.parse import urlencode, urlsplit, urlunsplit


RADAR_ISSUER = "steuerpilot-pro"
RADAR_AUDIENCE = "reinigungsradar"
PORTAL_AUDIENCE = "steuerpilot-radar-portal"
TOKEN_TTL_SECONDS = 120
SESSION_TTL_SECONDS = 8 * 60 * 60
ALLOWED_RADAR_HOST = "reinigungsai-pr7-staging.onrender.com"


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def _sign_claims(claims: dict, secret: str) -> str:
    encoded = _encode(json.dumps(claims, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(secret.encode("utf-8"), encoded.encode("ascii"), hashlib.sha256).digest()
    return f"{encoded}.{_encode(signature)}"


def _verify_claims(token: str, secret: str, audience: str, now: int | None = None) -> dict | None:
    if not isinstance(token, str) or len(token) > 2048 or not isinstance(secret, str) or len(secret) < 32:
        return None
    try:
        encoded, signature = token.split(".", 1)
        if not encoded or not signature or "." in signature:
            return None
        expected = hmac.new(secret.encode("utf-8"), encoded.encode("ascii"), hashlib.sha256).digest()
        if not hmac.compare_digest(_decode(signature), expected):
            return None
        claims = json.loads(_decode(encoded).decode("utf-8"))
        current = int(time.time() if now is None else now)
        issued = claims.get("iat") if isinstance(claims, dict) else None
        expires = claims.get("exp") if isinstance(claims, dict) else None
        if (
            not isinstance(claims, dict)
            or claims.get("iss") != RADAR_ISSUER
            or claims.get("aud") != audience
            or isinstance(issued, bool) or not isinstance(issued, int)
            or isinstance(expires, bool) or not isinstance(expires, int)
            or issued > current + 15
            or expires <= current
            or expires <= issued
        ):
            return None
        return claims
    except (ValueError, TypeError, UnicodeError, json.JSONDecodeError, base64.binascii.Error):
        return None


def verify_portal_password(candidate: str, configured_password: str) -> bool:
    if not configured_password or len(configured_password) < 20:
        return False
    return hmac.compare_digest(str(candidate), str(configured_password))


def create_portal_session(secret: str, *, now: int | None = None) -> str:
    if not isinstance(secret, str) or len(secret) < 32:
        raise ValueError("SSO secret must contain at least 32 characters")
    issued = int(time.time() if now is None else now)
    return _sign_claims(
        {"iss": RADAR_ISSUER, "aud": PORTAL_AUDIENCE, "iat": issued, "exp": issued + SESSION_TTL_SECONDS},
        secret,
    )


def verify_portal_session(token: str, secret: str, *, now: int | None = None) -> bool:
    claims = _verify_claims(token, secret, PORTAL_AUDIENCE, now=now)
    return bool(claims and claims.get("exp", 0) - claims.get("iat", 0) <= SESSION_TTL_SECONDS)


def build_radar_embed_url(base_url: str, secret: str, *, now: int | None = None) -> str:
    """Build an embed URL only for the known experimental Render staging host."""
    if not isinstance(secret, str) or len(secret) < 32:
        raise ValueError("SSO secret must contain at least 32 characters")
    parts = urlsplit(str(base_url or "").strip())
    if (
        parts.scheme != "https"
        or parts.hostname != ALLOWED_RADAR_HOST
        or parts.username or parts.password
        or parts.port
        or parts.query or parts.fragment
    ):
        raise ValueError("Only the configured ReinigungsRadar staging host is allowed")
    issued = int(time.time() if now is None else now)
    token = _sign_claims(
        {
            "iss": RADAR_ISSUER,
            "aud": RADAR_AUDIENCE,
            "sub": "demo-admin",
            "iat": issued,
            "exp": issued + TOKEN_TTL_SECONDS,
        },
        secret,
    )
    path = parts.path.rstrip("/") + "/"
    query = urlencode({"embed": "true", "sso": token})
    return urlunsplit(("https", ALLOWED_RADAR_HOST, path, query, ""))

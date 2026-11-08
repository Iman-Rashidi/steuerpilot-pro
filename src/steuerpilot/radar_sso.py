"""Short-lived HMAC SSO links for the experimental SteuerPilot Pro shell."""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from urllib.parse import urlencode, urlsplit, urlunsplit


RADAR_ISSUER = "steuerpilot-pro"
RADAR_AUDIENCE = "reinigungsradar"
TOKEN_TTL_SECONDS = 180
ALLOWED_RADAR_HOST = "reinigungsai-pr7-staging.onrender.com"

# The correctly-spelled name is preferred. The misspelled name remains as a
# temporary compatibility alias because it may already exist in Render.
SSO_SECRET_ENV = "STEUERPILOT_RADAR_SSO_SECRET"
LEGACY_SSO_SECRET_ENV = "STEUEERPILOT_RADAR_SSO_SECRET"


def get_radar_sso_secret(environ=None) -> str:
    """Read the shared staging secret without ever logging or exposing it."""
    source = os.environ if environ is None else environ
    value = source.get(SSO_SECRET_ENV) or source.get(LEGACY_SSO_SECRET_ENV) or ""
    return str(value).strip()


def _encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")


def _sign_claims(claims: dict, secret: str) -> str:
    encoded = _encode(json.dumps(claims, sort_keys=True, separators=(",", ":")).encode("utf-8"))
    signature = hmac.new(secret.encode("utf-8"), encoded.encode("ascii"), hashlib.sha256).digest()
    return f"{encoded}.{_encode(signature)}"


def build_radar_embed_url(base_url: str, secret: str, *, now: int | None = None) -> str:
    """Build an HTTPS embed URL only for the known experimental Render staging host."""
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

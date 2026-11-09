"""Same-origin mount for the read-only Crypto Super Radar HTTP dashboard.

The upstream dashboard keeps its own HTTP handler and in-memory scan jobs. This
adapter runs that handler on an ephemeral loopback-only port and exposes it
under /crypto-radar without publishing a second app URL.
"""
from __future__ import annotations

import http.client
import threading
from urllib.parse import urlsplit
from http.server import ThreadingHTTPServer

_PREFIX = "/crypto-radar"
_LOCK = threading.Lock()
_SERVER: ThreadingHTTPServer | None = None
_PORT: int | None = None


def _upstream_port() -> int:
    global _SERVER, _PORT
    if _PORT is not None:
        return _PORT
    with _LOCK:
        if _PORT is not None:
            return _PORT
        # Import only when the integrated route is first requested.
        from crypto_super_radar.web_app import Handler

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        server.daemon_threads = True
        thread = threading.Thread(
            target=server.serve_forever,
            name="crypto-radar-loopback",
            daemon=True,
        )
        thread.start()
        _SERVER = server
        _PORT = int(server.server_address[1])
        return _PORT


def _rewrite_dashboard(payload: bytes) -> bytes:
    """Expand the existing dashboard and keep its internal requests same-origin."""
    page = payload.decode("utf-8")
    page = page.replace('action="/scan"', 'action="/crypto-radar/scan"')
    page = page.replace("fetch('/jobs/", "fetch('/crypto-radar/jobs/")
    page = page.replace('fetch("/jobs/', 'fetch("/crypto-radar/jobs/')
    page = page.replace(
        "main{max-width:980px;margin:auto}",
        "main{width:min(100%,1680px);max-width:1680px;margin:0 auto}",
    )
    page = page.replace(
        "</style>",
        """
.portal-nav{display:flex;gap:10px;flex-wrap:wrap;align-items:center;
  max-width:1680px;margin:0 auto 18px;padding:12px 16px;
  border:1px solid #26364d;border-radius:14px;background:#111c2f}
.portal-nav a{color:#dbeafe;text-decoration:none;font-weight:700;padding:6px 10px;
  border-radius:8px}.portal-nav a:hover{background:#243b59}
.portal-nav .brand{margin-left:auto;color:#fff;font-size:16px}
body{padding:18px clamp(12px,2vw,32px)}
@media(max-width:640px){.portal-nav{gap:4px}.portal-nav a{font-size:12px;padding:6px}}
</style>""",
        1,
    )
    nav = (
        '<nav class="portal-nav" aria-label="SteuerPilot navigation">'
        '<a class="brand" href="/">SteuerPilot Pro</a>'
        '<a href="/">داشبورد اصلی</a>'
        '<a href="/invoice">Rechnung</a>'
        '<a href="/reinigungsradar">Reinigung Radar</a>'
        '<a href="/crypto-radar" aria-current="page">Crypto Super Radar</a>'
        '</nav>'
    )
    page = page.replace("<body><main>", "<body>" + nav + "<main>", 1)
    return page.encode("utf-8")


def proxy_crypto_request(environ, start_response):
    """Serve /crypto-radar and its scan/job endpoints from the loopback handler."""
    path = environ.get("PATH_INFO", "")
    if path != _PREFIX and not path.startswith(_PREFIX + "/"):
        start_response("404 Not Found", [("Content-Type", "text/plain; charset=utf-8")])
        return [b"Not found"]

    upstream_path = path[len(_PREFIX):] or "/"
    if not upstream_path.startswith("/"):
        upstream_path = "/" + upstream_path
    query = environ.get("QUERY_STRING", "")
    target = upstream_path + (("?" + query) if query else "")
    method = environ.get("REQUEST_METHOD", "GET").upper()
    origin = environ.get("HTTP_ORIGIN")
    if origin:
        parsed_origin = urlsplit(origin)
        request_host = environ.get("HTTP_HOST", "").lower()
        # Render terminates public HTTPS before the internal WSGI hop; compare
        # the browser Origin authority with the preserved public Host header.
        if parsed_origin.netloc.lower() != request_host:
            start_response("403 Forbidden", [("Content-Type", "text/plain; charset=utf-8")])
            return [b"Cross-origin Crypto Radar requests are not allowed"]
    if method not in {"GET", "POST", "HEAD"}:
        start_response("405 Method Not Allowed", [("Allow", "GET, POST, HEAD")])
        return [b"Method not allowed"]

    try:
        length = int(environ.get("CONTENT_LENGTH") or "0")
        if length < 0 or length > 16_384:
            start_response("413 Payload Too Large", [("Content-Type", "text/plain; charset=utf-8")])
            return [b"Invalid request size"]
        body = environ["wsgi.input"].read(length) if length else None
        headers = {}
        content_type = environ.get("CONTENT_TYPE")
        if content_type:
            headers["Content-Type"] = content_type
        # Deliberately do not forward Origin, Host, cookies, or authorization.
        connection = http.client.HTTPConnection("127.0.0.1", _upstream_port(), timeout=180)
        connection.request(method, target, body=body, headers=headers)
        response = connection.getresponse()
        payload = response.read()
        status = response.status
        reason = response.reason
        response_type = response.getheader("Content-Type", "text/plain; charset=utf-8")
        connection.close()
        if response_type.startswith("text/html"):
            payload = _rewrite_dashboard(payload)
        start_response(
            f"{status} {reason}",
            [
                ("Content-Type", response_type),
                ("Content-Length", str(len(payload))),
                ("Cache-Control", "no-store"),
                ("X-Content-Type-Options", "nosniff"),
            ],
        )
        return [payload]
    except (OSError, http.client.HTTPException, ValueError) as exc:
        message = f"Crypto Radar is temporarily unavailable: {type(exc).__name__}"
        start_response(
            "502 Bad Gateway",
            [("Content-Type", "text/plain; charset=utf-8"), ("Cache-Control", "no-store")],
        )
        return [message.encode("utf-8")]

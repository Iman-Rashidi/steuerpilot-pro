"""Stateless staging demo for SteuerPilot Pro. Synthetic data only."""
from __future__ import annotations

import json
import os
from decimal import Decimal, InvalidOperation
from wsgiref.simple_server import make_server

from steuerpilot.vat import VatRate, vat_from_net, vat_from_gross
from datetime import date

PAGE = """<!doctype html>
<html lang="de"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SteuerPilot Pro · Testumgebung</title>
<style>
:root{font-family:system-ui,sans-serif;color:#172033;background:#f3f5f8}
body{max-width:760px;margin:40px auto;padding:0 18px}
header,.panel{background:white;border:1px solid #dce2ea;border-radius:14px;padding:22px;margin:16px 0}
h1{margin:0 0 8px}.tag{display:inline-block;background:#fff1cc;color:#765300;padding:5px 9px;border-radius:20px;font-size:13px;font-weight:700}
label{display:block;margin:14px 0 6px;font-weight:600}input,select,button{font:inherit;padding:11px;border:1px solid #bbc5d2;border-radius:8px}
input{width:100%;box-sizing:border-box}button{margin-top:16px;background:#203b63;color:white;border:0;cursor:pointer}
#result{white-space:pre-wrap;background:#eef4fb;padding:14px;border-radius:8px;margin-top:16px;display:none}
.warning{border-left:4px solid #c58a00;padding:10px 14px;background:#fff8e6}
small{color:#536174}
</style></head><body>
<header><span class="tag">STAGING · TEST ONLY</span><h1>SteuerPilot Pro</h1>
<p>آزمایش محاسبهٔ سادهٔ VAT با داده‌های ساختگی</p>
<small>این محیط آزمایشی است؛ هیچ داده‌ای ذخیره نمی‌شود.</small></header>
<section class="panel">
<h2>محاسبه‌گر مالیات نمونه</h2>
<form id="vat">
<label for="amount">مبلغ (€)</label><input id="amount" type="number" min="0" max="100000000" step="0.01" value="100.00" required>
<label for="rate">درصد واردشده برای آزمایش</label><input id="rate" type="number" min="0" max="100" step="0.01" value="19" required>
<label for="mode">مبنای مبلغ</label><select id="mode"><option value="net">مبلغ خالص (Netto)</option><option value="gross">مبلغ ناخالص (Brutto)</option></select>
<button type="submit">محاسبه</button></form><div id="result"></div></section>
<section class="panel warning"><strong>محدودیت مهم</strong><p>درصد مالیات را کاربر وارد می‌کند و این ابزار تشخیص نمی‌دهد کدام نرخ از نظر قانون آلمان برای معامله مناسب است. برای اظهارنامه، فاکتور واقعی، حقوق یا اطلاعات اشخاص استفاده نکنید.</p></section>
<script>
document.getElementById('vat').addEventListener('submit',async e=>{
 e.preventDefault();const box=document.getElementById('result');box.style.display='block';box.textContent='در حال محاسبه…';
 try{const r=await fetch('/api/vat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({amount:document.getElementById('amount').value,rate:document.getElementById('rate').value,mode:document.getElementById('mode').value})});
 const d=await r.json();if(!r.ok)throw new Error(d.error||'خطا');
 box.textContent='خالص: €'+d.net+'\\nمالیات: €'+d.tax+'\\nناخالص: €'+d.gross+'\\n\\nاین فقط محاسبهٔ ریاضی بر اساس نرخ واردشده است.';
 }catch(err){box.textContent='خطا: '+err.message;}
});
</script></body></html>"""


def _response(start_response, status, payload, content_type="application/json; charset=utf-8"):
    body = payload.encode("utf-8")
    start_response(status, [("Content-Type", content_type), ("Content-Length", str(len(body))),
                            ("Cache-Control", "no-store"), ("X-Content-Type-Options", "nosniff")])
    return [body]


def application(environ, start_response):
    method, path = environ.get("REQUEST_METHOD"), environ.get("PATH_INFO")
    if method == "GET" and path == "/":
        return _response(start_response, "200 OK", PAGE, "text/html; charset=utf-8")
    if method == "GET" and path == "/health":
        return _response(start_response, "200 OK", json.dumps({"status": "ok", "environment": "staging", "persistence": False}))
    if method == "POST" and path == "/api/vat":
        try:
            length = int(environ.get("CONTENT_LENGTH") or "0")
            if length <= 0 or length > 8192:
                raise ValueError("درخواست خالی یا بیش از حد بزرگ است")
            raw = environ["wsgi.input"].read(length)
            data = json.loads(raw.decode("utf-8"))
            amount = Decimal(str(data["amount"]))
            percent = Decimal(str(data["rate"]))
            mode = data.get("mode", "net")
            if not amount.is_finite() or amount < 0 or amount > Decimal("100000000"):
                raise ValueError("مبلغ باید بین صفر تا ۱۰۰ میلیون باشد")
            if not percent.is_finite() or percent < 0 or percent > 100:
                raise ValueError("درصد باید بین صفر تا ۱۰۰ باشد")
            if mode not in ("net", "gross"):
                raise ValueError("حالت محاسبه نامعتبر است")
            rate = VatRate("USER-ENTERED-DEMO", percent, date.today())
            result = vat_from_net(amount, rate) if mode == "net" else vat_from_gross(amount, rate)
            out = {"net": str(result.net), "tax": str(result.tax), "gross": str(result.gross),
                   "rate_percent": str(result.rate_percent), "mode": mode}
            return _response(start_response, "200 OK", json.dumps(out))
        except (ValueError, KeyError, TypeError, InvalidOperation, json.JSONDecodeError) as exc:
            return _response(start_response, "400 Bad Request", json.dumps({"error": str(exc)}, ensure_ascii=False))
    return _response(start_response, "404 Not Found", json.dumps({"error": "not found"}))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "10000"))
    with make_server("0.0.0.0", port, application) as server:
        print(f"SteuerPilot staging demo listening on {port}")
        server.serve_forever()

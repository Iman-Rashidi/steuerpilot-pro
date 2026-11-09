"""Dependency-light Persian web dashboard for on-demand research scans."""
from __future__ import annotations

import html
import json
import os
import threading
import time
import uuid
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from .integrated_engine import WhaleAwareConfirmationEngine
from .indicators import observed_price_ranges
from .models import AssetSpec

ENGINE = WhaleAwareConfirmationEngine()
STORE = ENGINE.whale_store
JOBS: dict[str, dict] = {}
LAST_SCAN: dict[str, float] = {}
LOCK = threading.RLock()
SCAN_RUNNING = False


def _page(body: str, title: str = "CRYPTO SUPER RADAR") -> bytes:
    return f"""<!doctype html>
<html lang="fa" dir="rtl"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(title)}</title>
<style>
:root{{color-scheme:dark}}
*{{box-sizing:border-box}}
body{{font-family:Inter,Arial,sans-serif;background:radial-gradient(circle at 85% 0%,#152c49 0,#0b1220 42%,#070d17 100%);color:#e5edf7;margin:0;padding:clamp(12px,2vw,30px);line-height:1.65}}
main{{width:min(100%,1680px);max-width:1680px;margin:0 auto}}
h1{{font-size:clamp(28px,3vw,42px);line-height:1.2;margin:4px 0 10px}}h2{{font-size:clamp(20px,2vw,28px)}}h3{{font-size:18px;margin:0 0 14px}}
.card{{background:linear-gradient(145deg,#111e32,#0c1728);border:1px solid #293d58;border-radius:20px;padding:clamp(18px,2vw,30px);margin:18px 0;box-shadow:0 14px 34px #0003}}
input,button{{font:inherit;padding:12px 14px;border-radius:10px;border:1px solid #40536e;background:#091526;color:#fff;width:100%;box-sizing:border-box}}
input:focus{{outline:2px solid #4d9aff;border-color:#4d9aff}}button{{background:linear-gradient(120deg,#2563eb,#3478e5);border:0;margin-top:12px;cursor:pointer;font-weight:800}}button:hover{{filter:brightness(1.12)}}
table{{width:100%;border-collapse:collapse;font-size:14px}}td,th{{padding:11px;border-bottom:1px solid #2a3a50;text-align:right;vertical-align:top}}th{{color:#a9c3e3;font-weight:700}}
small,.muted{{color:#9fb0c5}}.status{{font-weight:bold}}code{{direction:ltr;display:inline-block}}
pre{{white-space:pre-wrap;overflow-wrap:anywhere;background:#08101d;padding:16px;border-radius:12px;direction:ltr;text-align:left;border:1px solid #25364c}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px}}
.metric{{background:#0b1729;border:1px solid #30445f;border-radius:14px;padding:15px;min-height:92px}}
.metric span{{display:block;color:#a8bad0;font-size:13px}}.metric strong{{display:block;font-size:clamp(17px,1.5vw,23px);margin-top:7px;direction:ltr;text-align:right;overflow-wrap:anywhere}}
canvas{{display:block;width:100%;height:420px;background:linear-gradient(180deg,#081522,#0a1727);border:1px solid #263b55;border-radius:14px}}
label{{display:block;margin-top:10px;color:#c7d5e6;font-weight:700}}.calc-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}}
.status-pass{{color:#4ade80}}.status-unknown{{color:#fbbf24}}.status-fail{{color:#fb7185}}
.scan-hero{{display:flex;justify-content:space-between;gap:24px;align-items:center;flex-wrap:wrap;padding:24px;border:1px solid #304866;border-radius:20px;background:linear-gradient(120deg,#142b48,#101c31);margin-bottom:18px}}
.scan-hero .muted{{max-width:760px}}.scan-status{{padding:8px 13px;border-radius:999px;background:#1b3554;color:#c6e2ff;font-weight:800}}
.dashboard-grid{{display:grid;grid-template-columns:minmax(0,1.65fr) minmax(300px,1fr);gap:18px;align-items:start}}
.dashboard-grid .card{{margin:0}}.wide-card{{grid-column:1/-1}}
.signal-pill{{display:inline-flex;align-items:center;justify-content:center;padding:8px 18px;border-radius:999px;font-size:18px;font-weight:900;background:#27364b;color:#dbeafe}}
.signal-pill.long{{background:#123d31;color:#86efac}}.signal-pill.short{{background:#4a1e2a;color:#fda4af}}.signal-pill.no-trade{{background:#49351b;color:#fcd34d}}
.gate-grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}}
.gate-item{{background:#0b1729;border:1px solid #2a3d57;border-radius:14px;padding:14px;min-width:0}}
.gate-item .gate-head{{display:flex;justify-content:space-between;gap:12px;align-items:start;margin-bottom:8px}}
.gate-item .gate-name{{font-weight:800}}.gate-item .gate-status{{font-size:12px;font-weight:900;letter-spacing:.04em}}
.gate-item p{{color:#aebed1;font-size:13px;margin:8px 0 0;overflow-wrap:anywhere}}
.gate-item.pass{{border-color:#27634f}}.gate-item.fail{{border-color:#784052}}.gate-item.unknown{{border-color:#6b552b}}
.section-kicker{{font-size:12px;text-transform:uppercase;letter-spacing:.12em;color:#83a9d3;font-weight:800}}
.result-note{{padding:14px 16px;border-radius:12px;background:#0b1729;border:1px solid #2d425e;color:#c8d7e8;margin-top:12px}}
details{{background:#0b1729;border:1px solid #2d425e;border-radius:14px;padding:14px;margin:18px 0}}summary{{cursor:pointer;font-weight:800;color:#c8d7e8}}
@media(max-width:900px){{.dashboard-grid{{grid-template-columns:1fr}}.wide-card{{grid-column:auto}}canvas{{height:320px}}}}
@media(max-width:560px){{body{{padding:10px}}.scan-hero{{padding:18px}}.card{{padding:16px}}table{{font-size:12px}}td,th{{padding:8px}}canvas{{height:260px}}}}
</style></head><body><main>{body}</main></body></html>""".encode("utf-8")


def _run_scan(job_id: str, asset: AssetSpec, headline: str, social_post: str) -> None:
    global SCAN_RUNNING
    try:
        result = ENGINE.analyze(
            asset,
            headlines=[headline] if headline else [],
            social_posts=[social_post] if social_post else [],
        )
        candle_frame = getattr(ENGINE.data, "candle_frames", {}).get(asset.raw)
        range_evidence = observed_price_ranges(candle_frame)
        trend_gate = next((gate for gate in result.gates if gate.gate_id == 3), None)
        regime_gate = next((gate for gate in result.gates if gate.gate_id == 2), None)
        candle_records = []
        if candle_frame is not None and not candle_frame.empty:
            required_ohlc = {"open", "high", "low", "close"}
            if required_ohlc.issubset(candle_frame.columns):
                for timestamp, row in candle_frame.tail(120).iterrows():
                    values = [float(row[key]) for key in ("open", "high", "low", "close")]
                    if all(value > 0 for value in values):
                        candle_records.append({
                            "timestamp": timestamp.isoformat() if hasattr(timestamp, "isoformat") else str(timestamp),
                            "open": values[0], "high": values[1], "low": values[2], "close": values[3],
                        })
        payload = {
            "asset": asset.raw,
            "market_overview": {
                "status": range_evidence.get("status", "UNKNOWN"),
                "reason": range_evidence.get("reason"),
                "current_price": range_evidence.get("current_price"),
                "candle_age_hours": range_evidence.get("candle_age_hours"),
                "ranges": range_evidence.get("windows", {}),
                "candles": candle_records,
                "asset_regime": (trend_gate.evidence or {}).get("asset_regime") if trend_gate else None,
                "benchmark_regime": (regime_gate.evidence or {}).get("regime") if regime_gate else None,
            },
            "signal": result.signal.value,
            "confirmation_score": result.confirmation_score,
            "estimated_risk_score": result.estimated_risk_score,
            "risk_score": result.metrics.get("risk_score"),
            "opportunity_rank": result.opportunity_rank,
            "confidence_level_pct": result.metrics.get("confidence_level_pct"),
            "evidence_confidence_pct": result.metrics.get("evidence_confidence_pct"),
            "summary_fa": result.summary_fa,
            "gates": [
                {"id": gate.gate_id, "name": gate.name_fa, "name_en": gate.name_en,
                 "status": gate.status.value, "reason": gate.reason_fa,
                 "reason_en": gate.reason_en, "evidence": gate.evidence}
                for gate in result.gates
            ],
            "metrics": {
                key: result.metrics.get(key) for key in (
                    "whale_status", "whale_bias", "whale_history_count",
                    "whale_recent_history_bias", "whale_alignment", "sentiment_alignment",
                    "market_sentiment_score", "fear_greed_value", "fear_greed_attribution",
                    "walk_forward_status", "walk_forward_fold_count", "risk_score",
                    "opportunity_rank", "confidence_level_pct", "evidence_confidence_pct",
                )
            },
        }
        with LOCK:
            JOBS[job_id] = {"status": "completed", "result": payload}
    except Exception as exc:
        with LOCK:
            JOBS[job_id] = {"status": "failed", "error": f"{type(exc).__name__}: {exc}"}
    finally:
        with LOCK:
            SCAN_RUNNING = False


class Handler(BaseHTTPRequestHandler):
    server_version = "CryptoSuperRadar/0.2"

    def _send(self, status: int, content: bytes, content_type: str = "text/html; charset=utf-8"):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path == "/health":
            return self._send(200, b'{"status":"ok"}', "application/json")
        if parsed.path.startswith("/jobs/"):
            job_id = parsed.path.rsplit("/", 1)[-1]
            with LOCK:
                job = JOBS.get(job_id)
            if job is None:
                return self._send(404, b'{"error":"job not found"}', "application/json")
            return self._send(200, json.dumps(job, ensure_ascii=False, default=str).encode(),
                              "application/json; charset=utf-8")
        if parsed.path == "/history":
            asset = parse_qs(parsed.query).get("asset", [""])[0]
            try:
                AssetSpec.parse(asset)
                data = STORE.summary(asset)
                return self._send(200, json.dumps(data, ensure_ascii=False, default=str).encode(),
                                  "application/json; charset=utf-8")
            except Exception:
                return self._send(400, b'{"error":"invalid asset"}', "application/json")
        if parsed.path != "/":
            return self._send(404, b"Not found", "text/plain; charset=utf-8")
        body = """
        <h1>🐋 CRYPTO SUPER RADAR</h1>
        <p class="muted">Quantitative Crypto Intelligence · فقط تحلیل و Paper Research، بدون اجرای سفارش</p>
        <section class="card">
          <h2>اسکن دارایی</h2>
          <form method="post" action="/scan">
            <label>بازار و نماد / آدرس</label>
            <input name="asset" required value="cex:BTCUSDT" placeholder="cex:BTCUSDT یا base:0x...">
            <p class="muted">نمونه‌ها: cex:BTCUSDT · perp:BTCUSDT · base:0x... · eth:0x... · solana:MINT</p>
            <label>تیتر خبری تکمیلی (اختیاری)</label>
            <input name="headline" placeholder="تیتر خبر">
            <label>متن اجتماعی تکمیلی (اختیاری)</label>
            <input name="social_post" placeholder="متن عمومی شبکه اجتماعی">
            <button type="submit">اجرای اسکن پژوهشی</button>
          </form>
        </section>
        <section class="card" id="market-tools">
          <h2>ماشین‌حساب حرفه‌ای سناریوی Spot</h2>
          <p class="muted">محاسبهٔ سود/زیان فرضی Long بدون اهرم؛ زمان انتخابی فقط افق سناریو است، نه پیش‌بینی زمان سود.</p>
          <div class="calc-grid">
            <div><label for="calc-amount">سرمایه (EUR)</label><input id="calc-amount" type="number" min="0.01" step="0.01" value="10"></div>
            <div><label for="calc-move">تغییر فرضی قیمت (%)</label><input id="calc-move" type="number" min="-99.9" step="0.1" value="10"></div>
            <div><label for="calc-days">افق سناریو (روز)</label><input id="calc-days" type="number" min="1" max="3650" value="14"></div>
            <div><label for="calc-buy-fee">کارمزد خرید (%)</label><input id="calc-buy-fee" type="number" min="0" max="20" step="0.01" value="0.1"></div>
            <div><label for="calc-sell-fee">کارمزد فروش (%)</label><input id="calc-sell-fee" type="number" min="0" max="20" step="0.01" value="0.1"></div>
            <div><label for="calc-buy-slip">لغزش خرید (%)</label><input id="calc-buy-slip" type="number" min="0" max="20" step="0.01" value="0.2"></div>
            <div><label for="calc-sell-slip">لغزش فروش (%)</label><input id="calc-sell-slip" type="number" min="0" max="20" step="0.01" value="0.2"></div>
          </div>
          <div class="grid" style="margin-top:12px">
            <div class="metric">سود/زیان خالص<strong id="calc-pnl">—</strong></div>
            <div class="metric">ارزش نهایی<strong id="calc-value">—</strong></div>
            <div class="metric">بازده خالص<strong id="calc-return">—</strong></div>
            <div class="metric">رشد سربه‌سر<strong id="calc-break-even">—</strong></div>
          </div>
          <h3>مقایسهٔ سناریوهای قیمت</h3><div id="calc-scenarios"></div>
          <p class="muted">فرمول: Vnet = I(1−fb)(1−sb)(1+r)(1−ss)(1−fs). مالیات، تغییر EUR/USD، هزینه برداشت/شبکه و اثر اندازه سفارش خارج از محاسبه‌اند.</p>
          <p class="muted">این ابزار پیش‌بینی، توصیه سرمایه‌گذاری یا سفارش معاملاتی نیست.</p>
        </section>
        <script>
        (function(){
          const ids=['calc-amount','calc-move','calc-days','calc-buy-fee','calc-sell-fee','calc-buy-slip','calc-sell-slip'];
          const el=id=>document.getElementById(id);
          function calc(move){
            const amount=Number(el('calc-amount').value), change=Number(move);
            const bf=Number(el('calc-buy-fee').value)/100, sf=Number(el('calc-sell-fee').value)/100;
            const bs=Number(el('calc-buy-slip').value)/100, ss=Number(el('calc-sell-slip').value)/100;
            const factor=(1-bf)*(1-bs)*(1+change/100)*(1-ss)*(1-sf);
            const net=amount*factor, pnl=net-amount;
            const base=(1-bf)*(1-bs)*(1-ss)*(1-sf);
            return {net,pnl,ret:pnl/amount*100,be:(1/base-1)*100};
          }
          function update(){
            const amount=Number(el('calc-amount').value),move=Number(el('calc-move').value);
            const days=Number(el('calc-days').value);
            const rates=ids.slice(3).map(id=>Number(el(id).value));
            if(!Number.isFinite(amount)||amount<=0||!Number.isFinite(move)||move<=-100||!Number.isFinite(days)||days<1||rates.some(x=>!Number.isFinite(x)||x<0||x>=100)){
              el('calc-pnl').textContent='ورودی نامعتبر';return;
            }
            const out=calc(move),eur=x=>x.toFixed(4)+' €';
            el('calc-pnl').textContent=(out.pnl>=0?'+':'')+eur(out.pnl);
            el('calc-value').textContent=eur(out.net);
            el('calc-return').textContent=(out.ret>=0?'+':'')+out.ret.toFixed(3)+'%';
            el('calc-break-even').textContent=out.be.toFixed(3)+'%';
            const rows=[-20,-10,0,5,10,20].map(v=>{const x=calc(v);return '<tr><td>'+v.toFixed(1)+'%</td><td>'+eur(x.pnl)+'</td><td>'+x.ret.toFixed(3)+'%</td><td>'+days+' روز</td></tr>';}).join('');
            el('calc-scenarios').innerHTML='<table><thead><tr><th>تغییر قیمت</th><th>سود/زیان خالص</th><th>بازده خالص</th><th>افق</th></tr></thead><tbody>'+rows+'</tbody></table>';
          }
          ids.forEach(id=>el(id).addEventListener('input',update));update();
        })();
        </script>
        <section class="card">
          <h3>۱۲ فیلتر اجباری</h3>
          <p>داده بازار · رژیم · روند · مومنتوم · جریان سرمایه · امنیت · احساسات · بک‌تست · ریسک · نهنگ‌ها · پوشش احساسات · Walk-forward</p>
          <p class="muted">هر فیلتر FAIL یا UNKNOWN باشد، خروجی NO TRADE است. سولانا در نسخه فعلی فقط نمونه‌برداری محدود از تراکنش‌های اخیر دارد.</p>
        </section>
        <p class="muted">تاریخچه: <code>/history?asset=cex:BTCUSDT</code></p>
        """
        return self._send(200, _page(body))

    def do_POST(self):
        global SCAN_RUNNING
        if urlparse(self.path).path != "/scan":
            return self._send(404, b"Not found", "text/plain; charset=utf-8")
        origin = self.headers.get("Origin")
        request_host = self.headers.get("Host", "")
        if origin and urlparse(origin).netloc.lower() != request_host.lower():
            return self._send(403, b"Cross-origin scan requests are not allowed", "text/plain; charset=utf-8")
        try:
            length = int(self.headers.get("Content-Length", "0"))
        except (TypeError, ValueError):
            return self._send(400, b"Invalid Content-Length", "text/plain; charset=utf-8")
        if length <= 0 or length > 16_384:
            return self._send(413, b"Invalid request size", "text/plain; charset=utf-8")
        client = self.client_address[0]
        now = time.time()
        with LOCK:
            previous = LAST_SCAN.get(client, 0.0)
            if now - previous < 60:
                return self._send(429, _page("<h2>محدودیت اسکن</h2><p>برای جلوگیری از مصرف بیش از حد APIهای عمومی، هر IP هر ۶۰ ثانیه یک اسکن می‌تواند اجرا کند.</p><a href='/'>بازگشت</a>"))
            if SCAN_RUNNING:
                return self._send(429, _page("<h2>اسکن در حال اجراست</h2><p>لطفاً تا پایان اسکن فعلی صبر کنید.</p><a href='/'>بازگشت</a>"))
            LAST_SCAN[client] = now
            SCAN_RUNNING = True
        try:
            form = parse_qs(self.rfile.read(length).decode("utf-8", errors="replace"))
            asset = AssetSpec.parse(form.get("asset", [""])[0].strip())
            headline = form.get("headline", [""])[0].strip()
            social_post = form.get("social_post", [""])[0].strip()
            job_id = uuid.uuid4().hex
            with LOCK:
                JOBS[job_id] = {"status": "queued"}
                while len(JOBS) > 100:
                    JOBS.pop(next(iter(JOBS)))
            worker = threading.Thread(
                target=_run_scan, args=(job_id, asset, headline, social_post), daemon=True
            )
            worker.start()
            body = """
            <section class="scan-hero">
              <div><div class="section-kicker">Crypto Super Radar · Research workspace</div>
                <h1>داشبورد تحلیل بازار</h1>
                <p class="muted">نمای عریض بازار، نمودار OHLC، تصمیم موتور تأیید، ریسک و وضعیت هر ۱۲ فیلتر. فقط شواهد دریافت‌شده نمایش داده می‌شود؛ دادهٔ ناموجود با UNKNOWN مشخص خواهد شد.</p>
              </div>
              <div><div id="state" class="scan-status">در حال جمع‌آوری داده‌های عمومی...</div>
                <p class="muted">شناسه اسکن: <code>__JOB_ID__</code></p></div>
            </section>
            <section class="dashboard-grid">
              <section class="card">
                <div class="section-kicker">Market overview</div><h3>نمای بازار و نمودار قیمت</h3>
                <div id="market-summary" class="grid"></div>
                <canvas id="candles" width="1400" height="440" aria-label="نمودار OHLC"></canvas>
                <p class="muted">نمودار فقط از کندل‌های OHLC موجود در نتیجه ساخته می‌شود؛ حجم معاملات یا تایم‌فریمِ تأییدنشده نمایش داده نمی‌شود.</p>
                <div id="range-table"></div>
              </section>
              <section class="card">
                <div class="section-kicker">Decision & risk</div><h3>خروجی موتور تصمیم</h3>
                <div id="signal" class="signal-pill no-trade">در انتظار نتیجه</div>
                <div id="decision-kpis" class="grid" style="margin-top:14px"></div>
                <div id="decision-summary" class="result-note">نتیجه پس از تکمیل اسکن نمایش داده می‌شود.</div>
              </section>
              <section class="card wide-card">
                <div class="section-kicker">Confirmation engine</div><h3>۱۲ فیلتر اجباری</h3>
                <div id="gate-grid" class="gate-grid"></div>
              </section>
              <section class="card">
                <div class="section-kicker">Whale & sentiment</div><h3>نهنگ‌ها و احساسات بازار</h3>
                <div id="insights-grid" class="grid"></div>
              </section>
              <section class="card">
                <div class="section-kicker">Validation & stability</div><h3>اعتبارسنجی و پایداری</h3>
                <div id="validation-grid" class="grid"></div>
              </section>
            </section>
            <details><summary>مشاهدهٔ شواهد خام (JSON)</summary><pre id="result">در انتظار نتیجه...</pre></details>
            <p><a href="/">بازگشت به پورتال SteuerPilot</a></p>
            <script>
            const job = "__JOB_ID__";
            const unknown = "UNKNOWN";
            const fmt = value => value === null || value === undefined || value === "" ? unknown :
              (typeof value === "number" ? new Intl.NumberFormat("en-US",{maximumFractionDigits:6}).format(value) : String(value));
            function addMetrics(id, entries) {
              const box = document.getElementById(id); box.replaceChildren();
              entries.forEach(([label,value]) => {
                const card = document.createElement("div"); card.className = "metric";
                const name = document.createElement("span"); name.textContent = label;
                const strong = document.createElement("strong"); strong.textContent = fmt(value);
                card.append(name,strong); box.appendChild(card);
              });
            }
            function renderMarket(m) {
              addMetrics("market-summary", [
                ["قیمت آخر",m.current_price],["رژیم دارایی",m.asset_regime],
                ["رژیم معیار",m.benchmark_regime],["سن آخرین کندل (ساعت)",m.candle_age_hours],
                ["اعتبار دادهٔ بازار",m.status]
              ]);
              const labels={"7":"۷ روز","30":"۳۰ روز","90":"۹۰ روز","365":"۳۶۵ روز"};
              const table=document.createElement("table"), head=document.createElement("thead"), row=document.createElement("tr");
              ["بازه","وضعیت","کف","سقف","تعداد کندل","پوشش %"].forEach(x=>{const th=document.createElement("th");th.textContent=x;row.appendChild(th);});
              head.appendChild(row);table.appendChild(head);
              const body=document.createElement("tbody");
              Object.entries(m.ranges||{}).forEach(([key,value])=>{
                const tr=document.createElement("tr");
                [labels[key]||key,value.status,value.low,value.high,value.candle_count,value.coverage_pct].forEach(x=>{
                  const td=document.createElement("td");td.textContent=fmt(x);tr.appendChild(td);
                });body.appendChild(tr);
              });
              table.appendChild(body);document.getElementById("range-table").replaceChildren(table);
              const canvas=document.getElementById("candles"),ctx=canvas.getContext("2d"),bars=m.candles||[];
              ctx.clearRect(0,0,canvas.width,canvas.height);
              if(!bars.length){ctx.fillStyle="#fbbf24";ctx.font="20px Arial";ctx.fillText("دادهٔ OHLC کافی برای نمودار موجود نیست",28,42);return;}
              const lo=Math.min(...bars.map(x=>x.low)),hi=Math.max(...bars.map(x=>x.high));
              const span=Math.max(hi-lo,1e-12),pad=28,w=(canvas.width-2*pad)/bars.length;
              bars.forEach((x,i)=>{
                const cx=pad+i*w+w/2,y=v=>canvas.height-pad-(v-lo)/span*(canvas.height-2*pad);
                const rising=x.close>=x.open;ctx.strokeStyle=rising?"#34d399":"#fb7185";ctx.fillStyle=ctx.strokeStyle;
                ctx.beginPath();ctx.moveTo(cx,y(x.high));ctx.lineTo(cx,y(x.low));ctx.stroke();
                const top=y(Math.max(x.open,x.close)),bottom=y(Math.min(x.open,x.close));
                ctx.fillRect(cx-w*.32,top,Math.max(1,w*.64),Math.max(1,bottom-top));
              });
            }
            function renderGates(gates) {
              const box=document.getElementById("gate-grid");box.replaceChildren();
              (gates||[]).forEach(g=>{
                const item=document.createElement("article"),head=document.createElement("div");
                const name=document.createElement("span"),status=document.createElement("span"),reason=document.createElement("p");
                const state=String(g.status||unknown).toLowerCase();
                item.className="gate-item "+(state==="pass"?"pass":state==="fail"?"fail":"unknown");
                head.className="gate-head";name.className="gate-name";name.textContent=(g.id??"—")+". "+(g.name||g.name_en||"فیلتر");
                status.className="gate-status status-"+state;status.textContent=g.status||unknown;
                reason.textContent=g.reason||g.reason_en||"برای این فیلتر توضیح قابل‌تأیید موجود نیست.";
                head.append(name,status);item.append(head,reason);box.appendChild(item);
              });
            }
            function renderResult(r) {
              const signal=String(r.signal||"NO TRADE").toUpperCase(),pill=document.getElementById("signal");
              pill.textContent=signal;pill.className="signal-pill "+(signal==="LONG"?"long":signal==="SHORT"?"short":"no-trade");
              addMetrics("decision-kpis",[
                ["امتیاز تأیید",r.confirmation_score],["ریسک تخمینی",r.estimated_risk_score],
                ["ریسک",r.risk_score],["اعتماد شواهد %",r.evidence_confidence_pct],
                ["سطح اطمینان %",r.confidence_level_pct],["رتبه فرصت",r.opportunity_rank]
              ]);
              document.getElementById("decision-summary").textContent=r.summary_fa||"خلاصهٔ توضیحی برای این نتیجه موجود نیست.";
              renderMarket(r.market_overview||{});renderGates(r.gates||[]);
              const m=r.metrics||{};
              addMetrics("insights-grid",[
                ["وضعیت نهنگ‌ها",m.whale_status],["جهت نهنگ‌ها",m.whale_bias],
                ["تعداد مشاهدات",m.whale_history_count],["هم‌راستایی نهنگ‌ها",m.whale_alignment],
                ["هم‌راستایی احساسات",m.sentiment_alignment],["امتیاز احساسات",m.market_sentiment_score],
                ["Fear & Greed",m.fear_greed_value],["توضیح Fear & Greed",m.fear_greed_attribution]
              ]);
              addMetrics("validation-grid",[
                ["وضعیت Walk-forward",m.walk_forward_status],["تعداد Fold",m.walk_forward_fold_count],
                ["امتیاز ریسک",m.risk_score],["رتبه فرصت",m.opportunity_rank],
                ["اطمینان مدل %",m.confidence_level_pct],["پوشش شواهد %",m.evidence_confidence_pct]
              ]);
              document.getElementById("result").textContent=JSON.stringify(r,null,2);
            }
            async function poll() {
              try {
                const response=await fetch("/jobs/"+job),jobData=await response.json();
                document.getElementById("state").textContent="وضعیت اسکن: "+jobData.status;
                if(jobData.status==="completed"){renderResult(jobData.result);document.getElementById("state").textContent="اسکن تکمیل شد · فقط داده‌های عمومی";return;}
                if(jobData.status==="failed"){document.getElementById("state").textContent="اسکن ناموفق";document.getElementById("result").textContent=jobData.error||"خطای نامشخص";return;}
              } catch(error) {
                document.getElementById("state").textContent="ارتباط موقتاً قطع شد؛ صفحه را تازه‌سازی کنید.";
                return;
              }
              setTimeout(poll,2500);
            }
            poll();
            </script>
            """.replace("__JOB_ID__", job_id)
            return self._send(202, _page(body, "Scan Running"))
        except Exception as exc:
            with LOCK:
                SCAN_RUNNING = False
            message = html.escape(f"{type(exc).__name__}: {exc}")
            return self._send(400, _page(f"<h2>خطا در ورودی</h2><p>{message}</p><a href='/'>بازگشت</a>"))

    def log_message(self, fmt, *args):
        super().log_message(fmt, *args)


def main():
    port = int(os.getenv("PORT", "10000"))
    host = os.getenv("HOST", "0.0.0.0")
    server = ThreadingHTTPServer((host, port), Handler)
    print(f"CRYPTO SUPER RADAR listening on {host}:{port}")
    server.serve_forever()


if __name__ == "__main__":
    main()

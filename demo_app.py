"""Stateless staging demo for SteuerPilot Pro. Synthetic data only."""
from __future__ import annotations

import json
import os
from decimal import Decimal, InvalidOperation
from wsgiref.simple_server import make_server

from datetime import date

from steuerpilot.vat import VatRate, vat_from_net, vat_from_gross

PAGE = """<!doctype html>
<html lang="fa"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
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
small{color:#536174}.academy-link{display:inline-block;margin-top:14px;padding:10px 13px;background:#e7f0ff;border-radius:9px;color:#163b6b;text-decoration:none;font-weight:700}
</style></head><body>
<header><span class="tag">STAGING · TEST ONLY</span><h1>SteuerPilot Pro</h1>
<p>آزمایش محاسبهٔ سادهٔ VAT با داده‌های ساختگی</p>
<small>این محیط آزمایشی است؛ هیچ داده‌ای ذخیره نمی‌شود.</small>
<br><a class="academy-link" href="/academy">🎓 ورود به آکادمی مدیرعامل و دستیار اجرایی</a></header>
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

ACADEMY_PAGE = """<!doctype html>
<html lang="fa"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SteuerPilot Pro · آکادمی مدیرعامل</title>
<style>
:root{font-family:system-ui,sans-serif;color:#172033;background:#f3f5f8;line-height:1.65}
body{max-width:900px;margin:28px auto;padding:0 16px}
header,.panel,.lesson{background:#fff;border:1px solid #dce2ea;border-radius:14px;padding:20px;margin:14px 0}
.tag{display:inline-block;background:#fff1cc;color:#765300;padding:4px 9px;border-radius:20px;font-size:12px;font-weight:700}
h1{margin:8px 0}.muted{color:#536174;font-size:14px}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:12px}
.lesson h3{margin:4px 0}.lesson p{margin:8px 0}.de{color:#315b88;font-weight:600}
details{border-top:1px solid #e5eaf0;margin-top:12px;padding-top:10px}
summary{cursor:pointer;font-weight:700;color:#203b63}
button,a.button{display:inline-block;margin-top:12px;background:#203b63;color:white;border:0;border-radius:8px;padding:10px 14px;font:inherit;text-decoration:none;cursor:pointer}
.note{background:#fff8e6;border-left:4px solid #c58a00;padding:12px;border-radius:8px}
.good{background:#eaf7ef;border-left:4px solid #27834a;padding:12px;border-radius:8px}
ol,ul{padding-inline-start:24px}
#practice-result{display:none;margin-top:12px;padding:12px;background:#eef4fb;border-radius:8px}
footer{padding:20px 4px;color:#536174;font-size:13px}
</style></head><body>
<header>
<span class="tag">STAGING · TRAINING ONLY</span>
<h1>🎓 آکادمی مدیرعامل | Geschäftsführer-Akademie</h1>
<p>آموزش ساده، اجرای تمرینی و کنترل مرحله‌به‌مرحله برای مدیرانی که از حسابداری شروع می‌کنند.</p>
<p class="de">Lernen · Verstehen · Ausführen · Kontrollieren</p>
<a class="button" href="/">بازگشت به صفحه اصلی و VAT آزمایشی</a>
</header>

<section class="panel">
<h2>روش کار دستیار</h2>
<div class="good"><b>هر کار در ۶ مرحله:</b> آموزش → آماده‌سازی → پرسش از مدیر → پیش‌نویس → کنترل → تأیید مسئول</div>
<p class="muted">این صفحه یک نمونه قابل‌تعامل است. پاسخ‌ها در سرور ذخیره نمی‌شوند و برای داده واقعی شرکت یا کارکنان طراحی نشده‌اند.</p>
</section>

<section class="panel">
<h2>مسیر یادگیری مدیرعامل</h2>
<div class="grid">
<article class="lesson"><h3>📚 ۱. حسابداری از صفر</h3><p class="de">Buchhaltung Grundlagen</p><p>درآمد، هزینه، دریافت وجه، بدهی، طلب، سود و نقدینگی را از هم تشخیص بده.</p>
<details><summary>درس و تمرین</summary><ol><li>هر رویداد مالی را با یک جمله توضیح بده.</li><li>تاریخ، مبلغ و مدرک آن را مشخص کن.</li><li>به خاطر بسپار: درآمد و دریافت پول همیشه یکی نیستند.</li></ol></details></article>

<article class="lesson"><h3>🧾 ۲. فاکتور و رسید</h3><p class="de">Rechnungen und Belege</p><p>فاکتور فروش، فاکتور خرید و مدرک پرداخت را مرتب ثبت کن.</p>
<details><summary>درس و تمرین</summary><ol><li>فروشنده یا مشتری را مشخص کن.</li><li>تاریخ، شرح و مبلغ را بخوان.</li><li>فایل رسید را به عملیات مرتبط کن.</li><li>اگر داده ناقص است، پیش‌نویس را نهایی نکن.</li></ol></details></article>

<article class="lesson"><h3>👥 ۳. شروع همکاری</h3><p class="de">Mitarbeiter-Onboarding</p><p>مراحل برنامه‌ریزی، قرارداد، ثبت‌های اداری و آماده‌سازی حقوق را بشناس.</p>
<details><summary>درس و تمرین</summary><ol><li>نوع اشتغال را مشخص کن.</li><li>تاریخ شروع و ساعات کاری را ثبت کن.</li><li>چک‌لیست قرارداد و ثبت بیمه را آماده کن.</li><li>ثبت رسمی فقط با رسید واقعی تأیید می‌شود.</li></ol></details></article>

<article class="lesson"><h3>📋 ۴. پایان همکاری</h3><p class="de">Mitarbeiter-Offboarding</p><p>مدارک، تسویه، دسترسی‌ها و موارد نیازمند بررسی حقوقی را شناسایی کن.</p>
<details><summary>درس و تمرین</summary><ol><li>نوع پایان همکاری را مشخص کن.</li><li>قرارداد و تاریخ‌های مربوط را جمع کن.</li><li>حمایت‌های ویژه و مهلت‌ها را برای بررسی متخصص علامت بزن.</li><li>سیستم به‌تنهایی قانونی‌بودن اخراج را تأیید نمی‌کند.</li></ol></details></article>

<article class="lesson"><h3>🏛️ ۵. مالیات شرکت</h3><p class="de">Steuern und Finanzamt</p><p>با انواع مالیات و آماده‌سازی پیش‌نویس گزارش آشنا شو.</p>
<details><summary>درس و تمرین</summary><ol><li>نوع حقوقی شرکت را انتخاب کن.</li><li>دوره گزارش را مشخص کن.</li><li>اسناد درآمد و هزینه را فهرست کن.</li><li>پیش‌نویس برای بررسی آماده می‌شود؛ ارسال رسمی در این صفحه انجام نمی‌شود.</li></ol></details></article>

<article class="lesson"><h3>📊 ۶. بازبینی ماهانه</h3><p class="de">Monatlicher CEO-Check</p><p>نقدینگی، فاکتورهای باز، اسناد ناقص و موعدهای نزدیک را مرور کن.</p>
<details><summary>درس و تمرین</summary><ol><li>مانده بانکی را بررسی کن.</li><li>مطالبات و بدهی‌ها را مرور کن.</li><li>مدارک ناقص را پیگیری کن.</li><li>کارهای باز را به مسئول مشخص ارجاع بده.</li></ol></details></article>
</div>
</section>

<section class="panel">
<h2>تمرین کوتاه مدیرعامل</h2>
<p>کدام گزینه تفاوت «درآمد» و «دریافت پول» را بهتر نشان می‌دهد؟</p>
<form id="quiz">
<label><input type="radio" name="q1" value="a"> هر دو همیشه دقیقاً یک معنی دارند.</label>
<label><input type="radio" name="q1" value="b"> ممکن است فاکتور صادر شده باشد اما مشتری هنوز پول را پرداخت نکرده باشد.</label>
<label><input type="radio" name="q1" value="c"> هر هزینه‌ای به‌صورت خودکار قابل کسر مالیاتی است.</label>
<button type="submit">بررسی پاسخ</button>
</form>
<div id="practice-result" role="status"></div>
</section>

<section class="panel note">
<h2>مرزهای مهم این نسخه</h2>
<ul>
<li>فقط برای یادگیری و آزمایش با اطلاعات ساختگی است.</li>
<li>هیچ اطلاعاتی ذخیره یا برای مرجع دولتی ارسال نمی‌شود.</li>
<li>محاسبه ریاضی جایگزین تشخیص قانونی نرخ، هزینه قابل‌کسر یا مالیات نمی‌شود.</li>
<li>اخراج، حقوق و دستمزد و اظهارنامه‌های مالیاتی باید در مسیر واقعی توسط افراد واجد صلاحیت بررسی شوند.</li>
<li>برای آزمایش از Steuer-ID، شماره بیمه، IBAN، اطلاعات سلامت، فیش حقوقی یا مدارک واقعی استفاده نکن.</li>
</ul>
</section>
<footer>SteuerPilot Pro · Prototyp · Keine produktive Steuerberatung, Payroll oder Behördenübermittlung.</footer>
<script>
document.getElementById('quiz').addEventListener('submit',function(event){
 event.preventDefault();
 const answer=document.querySelector('input[name="q1"]:checked');
 const box=document.getElementById('practice-result');
 box.style.display='block';
 if(!answer){box.textContent='ابتدا یک گزینه را انتخاب کن.';return;}
 if(answer.value==='b'){
   box.textContent='درست است. فاکتور می‌تواند به یک طلب تبدیل شود؛ دریافت بانکی ممکن است بعداً اتفاق بیفتد.';
 }else{
   box.textContent='این پاسخ درست نیست. دوباره درس «فاکتور و رسید» را مرور کن. درآمد، طلب و دریافت پول مفاهیم متفاوتی هستند.';
 }
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
    if method == "GET" and path in ("/academy", "/academy/"):
        return _response(start_response, "200 OK", ACADEMY_PAGE, "text/html; charset=utf-8")
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

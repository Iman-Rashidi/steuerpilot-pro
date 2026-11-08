"""Stateless staging demo for SteuerPilot Pro. Synthetic data only."""
from __future__ import annotations

import json
import os
from pathlib import Path
from decimal import Decimal, InvalidOperation
from wsgiref.simple_server import make_server

from datetime import date

from steuerpilot.vat import VatRate, vat_from_net, vat_from_gross
from payroll_demo import PAYROLL_PAGE
from steuerpilot.radar_sso import build_radar_embed_url, get_radar_sso_secret

PAGE = """<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SteuerPilot Pro · مرکز مدیریت کسب‌وکار</title><style>
:root{font-family:Tahoma,Arial,sans-serif;color:#18253b;background:#f2f5fa;line-height:1.7}*{box-sizing:border-box}body{max-width:1120px;margin:26px auto;padding:0 18px}
.hero{background:linear-gradient(125deg,#122846,#244f79);color:#fff;border-radius:22px;padding:28px;display:grid;grid-template-columns:1.5fr .8fr;gap:20px;align-items:center}
.hero h1{font-size:34px;margin:5px 0}.hero p{color:#e0eaf6;margin:7px 0}.pilot{display:inline-block;background:#f8d986;color:#543b08;padding:4px 11px;border-radius:24px;font-weight:800;font-size:12px}
.hero-side{background:#ffffff18;border:1px solid #ffffff30;border-radius:14px;padding:16px}.stats,.cards{display:grid;gap:12px;margin:16px 0}.stats{grid-template-columns:repeat(3,1fr)}.stats div,.card,.feature{background:#fff;border:1px solid #dfe6ef;border-radius:15px;padding:16px}.stats strong{display:block;color:#1d426c}.stats small,.card p,.muted{color:#66758a;font-size:13px}
h2{font-size:21px;margin:26px 0 10px}.cards{grid-template-columns:repeat(auto-fit,minmax(215px,1fr))}
.card{display:block;color:#18253b;text-decoration:none;min-height:130px}.card:hover{border-color:#86a4c8}.card h3{font-size:17px;margin:4px 0}.card .ico{font-size:24px}.card p{margin:0}
.feature-grid{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:center}.warning{background:#fff8e7;border:1px solid #f0dca9;border-radius:12px;padding:13px;color:#6e5313}
input,select,button{font:inherit;padding:10px;border:1px solid #c8d3e0;border-radius:9px}input{width:100%;margin:5px 0 10px}button{background:#244f79;color:white;border:0;cursor:pointer;padding:11px 16px}#result{white-space:pre-wrap;background:#edf4fb;padding:12px;border-radius:10px;margin-top:12px;display:none}
@media(max-width:700px){.hero,.feature-grid,.stats{grid-template-columns:1fr}.cards{grid-template-columns:1fr}}
</style></head><body>
<section class="hero"><div><span class="pilot">نسخهٔ آزمایشی · Pilot</span><h1>SteuerPilot Pro</h1><p>یک فضای کاری واحد برای امور مالی، مدیریت شرکت، آموزش و فرصت‌های تجاری خدمات نظافت در NRW.</p><p class="muted" style="color:#d4e0ef">داده‌ها در این نسخه ذخیره نمی‌شوند و همهٔ بخش‌ها فقط برای آزمایش هستند.</p></div>
<div class="hero-side"><strong>مرکز مدیریت کسب‌وکار</strong><p>مالی · کارکنان · مدیریت · رشد شرکت</p><a href="/reinigungsradar" style="color:white;font-weight:700">ورود به ReinigungsRadar ←</a></div></section>
<div class="stats"><div><strong>مالی و حسابداری</strong><small>VAT · Rechnung · Payroll</small></div><div><strong>مدیریت شرکت</strong><small>پروفایل شرکت · مدیرعامل · آکادمی</small></div><div><strong>فرصت‌های رشد</strong><small>شرکت‌ها · پیمانکاران · مناقصه‌ها</small></div></div>
<h2>مالی و امور اداری</h2><div class="cards">
<a class="card" href="/"><span class="ico">🧮</span><h3>محاسبه‌گر VAT</h3><p>محاسبهٔ نمونهٔ Netto، Steuer و Brutto.</p></a>
<a class="card" href="/invoice"><span class="ico">🧾</span><h3>Rechnung · فاکتور</h3><p>ساخت و پیش‌نمایش فاکتور در محیط آزمایشی.</p></a>
<a class="card" href="/reinigungsradar"><span class="ico">📡</span><h3>ReinigungsRadar</h3><p>جست‌وجوی مشتریان، شرکت‌ها و مناقصه‌های نظافت در همان داشبورد.</p></a>
<a class="card" href="/payroll"><span class="ico">👥</span><h3>Lohnabrechnung · فیش حقوقی</h3><p>ساخت و پیش‌نمایش فیش حقوقی در محیط آزمایشی.</p></a>
<a class="card" href="/academy"><span class="ico">🎓</span><h3>آکادمی مدیرعامل</h3><p>حسابداری، کارکنان، مالیات و بررسی ماهانه.</p></a></div>
<h2>پروفایل و مدیریت</h2><div class="cards">
<a class="card" href="/company-profile"><span class="ico">🏢</span><h3>پروفایل شرکت</h3><p>ساختار حقوقی، حوزهٔ فعالیت و اطلاعات پایه.</p></a>
<a class="card" href="/ceo-profile"><span class="ico">🧑‍💼</span><h3>پروفایل مدیرعامل</h3><p>نقش مدیریتی و تنظیمات نمایشی.</p></a></div>
<h2>فرصت‌های تجاری و بازار</h2><div class="feature"><div class="feature-grid"><div><span class="pilot">ماژول یکپارچه</span><h3>📡 ReinigungsRadar NRW</h3><p>جست‌وجوی شرکت‌ها، مشتریان بالقوه، پیمانکاران و مناقصه‌های TED در NRW.</p><p class="muted">نتایج نیازمند بررسی دستی هستند؛ هیچ تماس خودکار یا ارسال پیشنهاد انجام نمی‌شود.</p><a href="/reinigungsradar">بازکردن Radar در همین صفحه ←</a></div><div class="warning"><strong>نسخهٔ آزمایشی</strong><p>از اطلاعات واقعی کارکنان، مشتریان، حساب بانکی یا شماره مالیاتی استفاده نکنید. داده‌ها ذخیره یا برای مرجع دولتی ارسال نمی‌شوند.</p></div></div></div>
<h2>محاسبهٔ سریع VAT</h2><div class="feature"><form id="vat"><label for="amount">مبلغ (€)</label><input id="amount" type="number" min="0" max="100000000" step="0.01" value="100" required>
<label for="rate">درصد آزمایشی</label><input id="rate" type="number" min="0" max="100" step="0.01" value="19" required>
<label for="mode">مبنای مبلغ</label><select id="mode"><option value="net">Netto</option><option value="gross">Brutto</option></select><button type="submit">محاسبه</button></form><div id="result"></div></div>
<p class="muted">SteuerPilot Pro · Pilot · keine produktive Steuerberatung, Payroll oder Behördenübermittlung.</p>
<script>document.getElementById('vat').addEventListener('submit',async e=>{e.preventDefault();const b=document.getElementById('result');b.style.display='block';b.textContent='در حال محاسبه…';try{const r=await fetch('/api/vat',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({amount:document.getElementById('amount').value,rate:document.getElementById('rate').value,mode:document.getElementById('mode').value})});const d=await r.json();if(!r.ok)throw new Error(d.error||'خطا');b.textContent='خالص: €'+d.net+'\\nمالیات: €'+d.tax+'\\nناخالص: €'+d.gross;}catch(e){b.textContent='خطا: '+e.message;}});</script></body></html>"""

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
<h1>🎓 آکادمی مدیرعامل | Geschäftsführer-Akademie</h1>
<p>آموزش ساده، اجرای تمرینی و کنترل مرحله‌به‌مرحله برای مدیرانی که از حسابداری شروع می‌کنند.</p>
<p class="de">Lernen · Verstehen · Ausführen · Kontrollieren</p>
<a class="button" href="/">بازگشت به صفحه اصلی</a> <a class="button" href="/payroll">ساخت فیش حقوقی و PDF</a> <a class="button" href="/invoice">صدور Rechnung و PDF</a>
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



def _sample_payroll_page() -> str:
    """Return the existing payroll form prefilled with synthetic demonstration data."""
    page = PAYROLL_PAGE

    def set_input(input_id: str, value: str) -> None:
        nonlocal page
        marker = f'id="{input_id}"'
        start = page.index(marker)
        end = page.index(">", start)
        tag = page[start:end]
        if " value=" in tag:
            raise ValueError(f"Sample input {input_id} already has a value attribute")
        page = page[:end] + f' value="{value}"' + page[end:]

    def select_option(select_id: str, option_html: str) -> None:
        nonlocal page
        start = page.index(f'<select id="{select_id}">')
        end = page.index("</select>", start) + len("</select>")
        block = page[start:end]
        if option_html not in block:
            raise ValueError(f"Sample option not found for {select_id}")
        block = block.replace(option_html, option_html.replace("<option", "<option selected", 1), 1)
        page = page[:start] + block + page[end:]

    for input_id, value in {
        "company": "Muster GmbH",
        "company_address": "Musterstrasse 12, 40210 Duesseldorf",
        "employee": "Max Mustermann",
        "employee_no": "TEST-001",
        "employee_address": "Beispielweg 4, 40211 Duesseldorf",
        "birth_date": "1990-01-01",
        "start_date": "2024-05-01",
        "pay_date": "2026-11-30",
    }.items():
        set_input(input_id, value)

    select_option("tax_class", "<option>I</option>")
    select_option("religion", '<option value="Keine">Keine</option>')
    select_option("state", '<option value="NW">Nordrhein-Westfalen</option>')

    page = page.replace(
        "<header>\n  <h1>Lohnabrechnung erstellen</h1>",
        "<header>\n  <div class=\"note\" style=\"background:#fff;border:1px solid #888;color:#111\"><strong>MUSTERDATEN · NICHT ZUR AUSZAHLUNG</strong><br>Diese Vorschau verwendet ausschließlich erfundene Beispieldaten.</div>\n  <h1>Lohnabrechnung erstellen</h1>",
        1,
    )
    page = page.replace(
        "keine zertifizierte Entgeltabrechnung.",
        "MUSTER - keine Auszahlung; ausschliesslich erfundene Testdaten.",
        1,
    )
    return page



def _with_navigation(page: str, active: str = "home") -> str:
    if active == "payroll":
        # Keep the German payroll workflow fully LTR and free of mixed-language labels.
        links = [
            ("home", "/", "Home"),
            ("company", "/company-profile", "Company"),
            ("ceo", "/ceo-profile", "CEO"),
            ("academy", "/academy", "Academy"),
            ("invoice", "/invoice", "Invoice"),
            ("radar", "/reinigungsradar", "ReinigungsRadar"),
            ("payroll", "/payroll", "Lohnabrechnung"),
        ]
    else:
        links = [("home","/","مرکز اصلی"),("company","/company-profile","پروفایل شرکت"),
            ("ceo","/ceo-profile","مدیرعامل"),("academy","/academy","آکادمی"),
            ("invoice","/invoice","فاکتور"),("radar","/reinigungsradar","ReinigungsRadar"),
            ("payroll","/payroll","حقوق")]
    items = []
    for key, href, label in links:
        current = ' aria-current="page"' if key == active else ""
        items.append(f'<a href="{href}"{current}>{label}</a>')
    nav = '<nav class="sp-nav"><a class="sp-brand" href="/">SteuerPilot Pro</a>' + "".join(items) + "</nav>"
    css = """<style>.sp-nav{max-width:1120px;margin:0 auto 18px;padding:10px;display:flex;gap:6px;flex-wrap:wrap;background:white;border:1px solid #dce4ee;border-radius:14px;direction:rtl}
.sp-nav a{padding:7px 9px;text-decoration:none;color:#29415f;border-radius:9px;font-size:13px;font-weight:700}.sp-nav a[aria-current="page"],.sp-nav a:hover{background:#e9f1fa;color:#173d67}
.sp-nav .sp-brand{margin-left:auto;color:#173d67;font-size:15px}@media(max-width:640px){.sp-nav{overflow-x:auto;flex-wrap:nowrap;white-space:nowrap}}</style>"""
    if active == "payroll":
        css = css.replace("direction:rtl", "direction:ltr")
    if "</head>" in page:
        page = page.replace("</head>", css + "</head>", 1)
    i = page.lower().find("<body")
    if i >= 0:
        j = page.find(">", i)
        if j >= 0:
            page = page[:j+1] + nav + page[j+1:]
    return page


def _profile_page(title: str, description: str, fields: list[tuple[str, str, str]]) -> str:
    rows = "".join(f'<label for="{i}">{label}</label><input id="{i}" name="{i}" placeholder="{ph}" autocomplete="off">' for i,label,ph in fields)
    return f"""<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{title}</title>
<style>:root{{font-family:Tahoma,Arial,sans-serif;color:#17243a;background:#f3f6fa;line-height:1.7}}body{{max-width:900px;margin:28px auto;padding:0 18px}}header,.panel{{background:#fff;border:1px solid #dce4ee;border-radius:16px;padding:22px;margin:14px 0}}label{{display:block;font-weight:700;margin:10px 0 3px}}input{{width:100%;padding:11px;border:1px solid #c8d3e0;border-radius:9px;font:inherit}}button{{margin-top:16px;padding:11px 16px;background:#244f79;color:white;border:0;border-radius:9px;font:inherit}}.note{{background:#fff8e7;border:1px solid #f0dca9;border-radius:12px;padding:13px;color:#6e5313}}#profile-result{{display:none;background:#edf4fb;padding:12px;border-radius:9px;margin-top:12px}}</style></head><body>
<header><h1>{title}</h1><p>{description}</p></header><section class="panel"><form id="profile-form">{rows}<button type="submit">بررسی نمایشی فرم</button></form><div id="profile-result" role="status"></div></section>
<section class="note"><b>فقط نمایشی</b><p>این فرم در مرورگر اجرا می‌شود، به سرور ارسال نمی‌شود و هیچ داده‌ای ذخیره نمی‌کند. اطلاعات واقعی وارد نکنید.</p></section>
<script>document.getElementById('profile-form').addEventListener('submit',e=>{{e.preventDefault();const b=document.getElementById('profile-result');b.style.display='block';b.textContent='فرم در مرورگر بررسی شد؛ ذخیره‌سازی در این نسخه فعال نیست.';}});</script></body></html>"""


def _radar_page(environ) -> tuple[str, str]:
    """Render Radar directly through a short-lived SteuerPilot-issued SSO token."""
    secret = get_radar_sso_secret()
    if len(secret) < 32:
        return (
            "503 Service Unavailable",
            '<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><body>'
            '<h1>ورود یکپارچه هنوز آماده نیست</h1>'
            '<p>تنظیم امن اتصال بین دو سرویس آزمایشی کامل نیست.</p></body></html>',
        )
    try:
        iframe_url = build_radar_embed_url(
            "https://reinigungsai-pr7-staging.onrender.com",
            secret,
        )
    except ValueError:
        return (
            "503 Service Unavailable",
            '<!doctype html><html lang="fa" dir="rtl"><meta charset="utf-8"><body>'
            '<h1>اتصال آزمایشی قابل استفاده نیست</h1>'
            '<p>نشانی سرویس مقصد یا تنظیمات SSO معتبر نیست.</p></body></html>',
        )

    # Keep the short-lived token out of the parent page's markup except for the
    # iframe destination, and prevent it being sent as a Referer header.
    iframe_url = iframe_url.replace("&", "&amp;").replace('"', "&quot;")
    page = f"""<!doctype html><html lang="fa" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SteuerPilot Pro · ReinigungsRadar</title>
<style>:root{{font-family:Tahoma,Arial,sans-serif;background:#f2f5fa;color:#17243a}}body{{margin:20px auto;padding:0 14px;max-width:1500px}}.radar-head{{background:#fff;border:1px solid #dce4ee;border-radius:14px;padding:14px 18px;margin-bottom:12px}}.radar-frame{{width:100%;height:calc(100vh - 180px);min-height:950px;border:1px solid #dce4ee;border-radius:14px;background:#fff}}.muted{{color:#66758a;font-size:13px}}</style></head><body>
<section class="radar-head"><h1>📡 ReinigungsRadar NRW</h1><p>ماژول فرصت‌های تجاری داخل SteuerPilot Pro: شرکت‌ها، مشتریان بالقوه، پیمانکاران و مناقصه‌های TED.</p>
<p class="muted">ورود شما از داشبورد مرکزی SteuerPilot انجام شده است؛ نیازی به رمز عبور آزمایشی جداگانه نیست.</p></section>
<iframe class="radar-frame" src="{iframe_url}" title="ReinigungsRadar NRW" loading="eager" referrerpolicy="no-referrer"></iframe></body></html>"""
    return "200 OK", _with_navigation(page, "radar")


def application(environ, start_response):
    method, path = environ.get("REQUEST_METHOD"), environ.get("PATH_INFO")
    if method == "GET" and path.startswith("/static/"):
        asset_name = path.removeprefix("/static/")
        assets = {
            "steuerpilot_payroll_wasm.js": ("text/javascript; charset=utf-8",),
            "steuerpilot_payroll_wasm_bg.wasm": ("application/wasm",),
            "Lohnsteuer2026.xml": ("application/xml; charset=utf-8",),
        }
        asset = assets.get(asset_name)
        if asset is None:
            return _response(start_response, "404 Not Found", json.dumps({"error": "not found"}))
        asset_path = Path(__file__).with_name("static") / asset_name
        if not asset_path.is_file():
            return _response(start_response, "503 Service Unavailable", json.dumps({"error": "payroll tax assets are not built"}))
        body = asset_path.read_bytes()
        start_response("200 OK", [
            ("Content-Type", asset[0]),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
            ("X-Content-Type-Options", "nosniff"),
        ])
        return [body]
    if method == "GET" and path == "/":
        return _response(start_response, "200 OK", _with_navigation(PAGE, "home"), "text/html; charset=utf-8")
    if method == "GET" and path in ("/academy", "/academy/"):
        return _response(start_response, "200 OK", _with_navigation(ACADEMY_PAGE, "academy"), "text/html; charset=utf-8")
    if method == "GET" and path in ("/payroll/sample", "/payroll/sample/"):
        return _response(start_response, "200 OK", _with_navigation(_sample_payroll_page(), "payroll"), "text/html; charset=utf-8")
    if method == "GET" and path in ("/payroll", "/payroll/"):
        return _response(start_response, "200 OK", _with_navigation(PAYROLL_PAGE, "payroll"), "text/html; charset=utf-8")
    if method == "GET" and path in ("/invoice", "/invoice/"):
        invoice_page = Path(__file__).with_name("invoice_demo.html").read_text(encoding="utf-8")
        return _response(start_response, "200 OK", _with_navigation(invoice_page, "invoice"), "text/html; charset=utf-8")
    if method == "GET" and path in ("/company-profile", "/company-profile/"):
        page = _profile_page("پروفایل شرکت", "مشخصات پایهٔ کسب‌وکار در نمایهٔ آزمایشی.", [
            ("company_name", "نام شرکت", "Muster GmbH"),
            ("legal_form", "ساختار حقوقی", "GmbH / UG / Einzelunternehmen"),
            ("sector", "حوزهٔ فعالیت", "Gebäudereinigung / Facility Management"),
            ("city", "شهر اصلی فعالیت", "Düsseldorf"),
            ("website", "وب‌سایت شرکت", "https://example.de"),
        ])
        return _response(start_response, "200 OK", _with_navigation(page, "company"), "text/html; charset=utf-8")
    if method == "GET" and path in ("/ceo-profile", "/ceo-profile/"):
        page = _profile_page("پروفایل مدیرعامل", "نمایهٔ نمایشی مدیر مسئول شرکت و تنظیمات پایه.", [
            ("ceo_name", "نام نمایشی مدیرعامل", "Max Mustermann"),
            ("ceo_role", "سمت", "Geschäftsführer"),
            ("work_email", "ایمیل کاری نمونه", "ceo@example.de"),
            ("language", "زبان رابط کاربری", "Deutsch / فارسی"),
            ("business_focus", "اولویت مدیریتی", "Finanzen, Personal, Wachstum"),
        ])
        return _response(start_response, "200 OK", _with_navigation(page, "ceo"), "text/html; charset=utf-8")
    if method == "GET" and path in ("/reinigungsradar", "/reinigungsradar/"):
        status, page = _radar_page(environ)
        return _response(start_response, status, page, "text/html; charset=utf-8")
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

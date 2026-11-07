"""Browser-only payroll statement preview for the SteuerPilot staging demo."""

PAYROLL_PAGE = r"""<!doctype html>
<html lang="fa" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SteuerPilot Pro · فیش حقوقی</title>
<style>
:root{font-family:system-ui,sans-serif;color:#172033;background:#f3f5f8;line-height:1.55}
*{box-sizing:border-box}
body{max-width:1180px;margin:24px auto;padding:0 16px}
header,.panel{background:#fff;border:1px solid #dce2ea;border-radius:14px;padding:18px;margin:14px 0}
h1,h2,h3{margin-top:0}
header h1{margin-bottom:4px}
.muted{color:#5c6878;font-size:13px}
.layout{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px;align-items:start}
.editor{display:grid;gap:14px}
.group{border:1px solid #e0e6ee;border-radius:10px;padding:14px}
.group h3{margin:0 0 10px;font-size:16px}
.fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.field{min-width:0}
.field.full{grid-column:1/-1}
label{display:block;margin:0 0 5px;font-weight:650;font-size:13px}
input{width:100%;min-width:0;padding:10px;border:1px solid #bbc5d2;border-radius:8px;font:inherit;background:#fff}
input[type=file]{padding:7px}
.actions{display:flex;gap:10px;flex-wrap:wrap}
button,.button{display:inline-block;border:0;border-radius:9px;padding:11px 16px;font:inherit;text-decoration:none;cursor:pointer}
.primary{background:#203b63;color:white}
.secondary{background:#e8eef6;color:#203b63}
.note{background:#fff8e8;border-right:4px solid #c58a00;padding:12px;border-radius:8px;font-size:13px}
.preview{background:#fff;border:1px solid #cfd7e2;border-radius:12px;padding:22px;box-shadow:0 4px 18px #10243a0b;direction:ltr;text-align:left}
.preview-top{display:flex;gap:16px;align-items:flex-start;justify-content:space-between;border-bottom:2px solid #203b63;padding-bottom:15px}
.logo-area{width:150px;height:82px;border:1px dashed #91a0b3;border-radius:8px;display:flex;align-items:center;justify-content:center;overflow:hidden;color:#66758a;font-size:12px;text-align:center;padding:6px;flex-shrink:0}
.logo-area img{max-width:100%;max-height:100%;object-fit:contain}
.company-block{flex:1;text-align:right;direction:rtl}
.company-block strong{font-size:17px}
.pay-title{margin:18px 0 12px;font-size:21px}
.meta{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px}
.meta div,.party{background:#f5f7fa;border-radius:7px;padding:9px}
.meta small,.party small{display:block;color:#596779;font-size:11px}
.parties{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px}
.party b{display:block;min-height:22px}
table{width:100%;border-collapse:collapse;font-size:12px;margin:8px 0 14px}
th,td{padding:7px 6px;border-bottom:1px solid #e2e7ed;text-align:left}
th{background:#f1f4f8;font-weight:700}
.amount{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
.section-title{margin:14px 0 4px;font-size:14px}
.total-row{font-weight:700;background:#f4f7fb}
.net-box{border:2px solid #203b63;border-radius:9px;padding:13px;margin-top:14px;display:flex;justify-content:space-between;align-items:center;font-size:16px;font-weight:750}
.preview-foot{margin-top:18px;padding-top:10px;border-top:1px solid #dce2ea;color:#596779;font-size:10px}
a.back{color:#203b63;text-decoration:none;font-weight:650}
@media(max-width:850px){.layout{grid-template-columns:1fr}.preview{padding:15px}}
@media(max-width:520px){.fields,.meta,.parties{grid-template-columns:1fr}.preview-top{gap:8px}.logo-area{width:105px;height:68px}.preview{padding:11px}table{font-size:11px}}
@page{size:A4;margin:12mm}
@media print{
  html,body{background:white!important;margin:0!important;padding:0!important;max-width:none!important}
  header,.editor,.actions,.note,.screen-only{display:none!important}
  .layout{display:block!important}
  .preview{display:block!important;border:0!important;border-radius:0!important;box-shadow:none!important;padding:0!important;width:100%!important}
  .preview table{page-break-inside:avoid}
  .preview-top,.parties,.net-box{page-break-inside:avoid}
  .preview-foot{position:static}
}
</style>
</head>
<body>
<header>
  <h1>ساخت فیش حقوقی | Lohnabrechnung</h1>
  <p class="muted">اطلاعات را وارد کن، پیش‌نمایش را بررسی کن و برای ساخت PDF از گزینه چاپ مرورگر استفاده کن.</p>
  <p><a class="back" href="/">← بازگشت به SteuerPilot Pro</a></p>
</header>

<div class="layout">
  <main class="editor">
    <section class="panel">
      <div class="note">این فرم در مرورگر اجرا می‌شود. اطلاعات فیش و تصویر لوگو به سرور ارسال یا در برنامه ذخیره نمی‌شوند. فقط برای داده‌های ساختگی استفاده کن؛ شناسه مالیاتی، شماره بیمه اجتماعی، IBAN یا اطلاعات واقعی کارکنان را وارد نکن.</div>
    </section>

    <section class="panel group">
      <h3>مشخصات شرکت</h3>
      <div class="fields">
        <div class="field full"><label for="company">نام شرکت / Arbeitgeber</label><input id="company" data-bind="company" placeholder="Muster GmbH"></div>
        <div class="field full"><label for="company_address">نشانی شرکت</label><input id="company_address" data-bind="company_address" placeholder="Musterstraße 1, 00000 Musterstadt"></div>
        <div class="field full"><label for="logo_file">لوگوی شرکت</label><input id="logo_file" type="file" accept="image/png,image/jpeg,image/webp"></div>
      </div>
    </section>

    <section class="panel group">
      <h3>مشخصات کارمند و دوره</h3>
      <div class="fields">
        <div class="field"><label for="employee">نام کارمند / Arbeitnehmer</label><input id="employee" data-bind="employee" placeholder="Max Mustermann"></div>
        <div class="field"><label for="employee_no">شماره داخلی کارمند</label><input id="employee_no" data-bind="employee_no" placeholder="M-001"></div>
        <div class="field"><label for="start_date">تاریخ شروع همکاری</label><input id="start_date" type="date" data-bind="start_date"></div>
        <div class="field"><label for="period">دوره حقوق</label><input id="period" data-bind="period" placeholder="November 2026"></div>
        <div class="field"><label for="pay_date">تاریخ پرداخت</label><input id="pay_date" type="date" data-bind="pay_date"></div>
      </div>
    </section>

    <section class="panel group">
      <h3>دریافتی‌ها</h3>
      <p class="muted">مبالغ زیر را طبق محاسبه حقوق معتبر وارد کن؛ این فرم نرخ قانونی را محاسبه نمی‌کند.</p>
      <div class="fields">
        <div class="field"><label for="base_pay">حقوق پایه ناخالص (€)</label><input id="base_pay" type="number" min="0" step="0.01" value="3000" data-money="earning"></div>
        <div class="field"><label for="overtime">اضافه‌کاری و Zuschläge (€)</label><input id="overtime" type="number" min="0" step="0.01" value="0" data-money="earning"></div>
        <div class="field"><label for="bonus">پاداش و پرداخت یک‌باره (€)</label><input id="bonus" type="number" min="0" step="0.01" value="0" data-money="earning"></div>
        <div class="field"><label for="allowance">مزایا و فوق‌العاده‌ها (€)</label><input id="allowance" type="number" min="0" step="0.01" value="0" data-money="earning"></div>
      </div>
    </section>

    <section class="panel group">
      <h3>کسورات کارمند</h3>
      <p class="muted">مبالغ را از محاسبه حقوق معتبر وارد کن؛ مبلغ کسورات این فرم به‌صورت خودکار تعیین نمی‌شود.</p>
      <div class="fields">
        <div class="field"><label for="tax">Lohnsteuer (€)</label><input id="tax" type="number" min="0" step="0.01" value="0" data-money="deduction"></div>
        <div class="field"><label for="soli">Solidaritätszuschlag (€)</label><input id="soli" type="number" min="0" step="0.01" value="0" data-money="deduction"></div>
        <div class="field"><label for="church">Kirchensteuer (€)</label><input id="church" type="number" min="0" step="0.01" value="0" data-money="deduction"></div>
        <div class="field"><label for="health">Krankenversicherung - Arbeitnehmer (€)</label><input id="health" type="number" min="0" step="0.01" value="0" data-money="deduction"></div>
        <div class="field"><label for="care">Pflegeversicherung - Arbeitnehmer (€)</label><input id="care" type="number" min="0" step="0.01" value="0" data-money="deduction"></div>
        <div class="field"><label for="pension">Rentenversicherung - Arbeitnehmer (€)</label><input id="pension" type="number" min="0" step="0.01" value="0" data-money="deduction"></div>
        <div class="field"><label for="unemployment">Arbeitslosenversicherung - Arbeitnehmer (€)</label><input id="unemployment" type="number" min="0" step="0.01" value="0" data-money="deduction"></div>
        <div class="field"><label for="other">سایر کسورات (€)</label><input id="other" type="number" min="0" step="0.01" value="0" data-money="deduction"></div>
        <div class="field"><label for="advance">پیش‌پرداخت قبلی / Vorschuss (€)</label><input id="advance" type="number" min="0" step="0.01" value="0" data-money="deduction"></div>
      </div>
    </section>

    <section class="panel group">
      <h3>سهم کارفرما (اطلاعاتی)</h3>
      <p class="muted">این مبالغ از خالص دریافتی کارمند کم نمی‌شوند.</p>
      <div class="fields">
        <div class="field"><label for="employer_health">Krankenversicherung Arbeitgeber (€)</label><input id="employer_health" type="number" min="0" step="0.01" value="0" data-money="employer"></div>
        <div class="field"><label for="employer_care">Pflegeversicherung Arbeitgeber (€)</label><input id="employer_care" type="number" min="0" step="0.01" value="0" data-money="employer"></div>
        <div class="field"><label for="employer_pension">Rentenversicherung Arbeitgeber (€)</label><input id="employer_pension" type="number" min="0" step="0.01" value="0" data-money="employer"></div>
        <div class="field"><label for="employer_unemployment">Arbeitslosenversicherung Arbeitgeber (€)</label><input id="employer_unemployment" type="number" min="0" step="0.01" value="0" data-money="employer"></div>
      </div>
    </section>

    <div class="actions screen-only">
      <button class="primary" id="pdf_button" type="button">ساخت PDF / Drucken</button>
      <button class="secondary" id="reset_button" type="button">پاک‌کردن فرم</button>
    </div>
  </main>

  <section class="preview" id="payroll_preview" aria-live="polite">
    <div class="preview-top">
      <div class="logo-area" id="logo_area">LOGO<br>Unternehmen</div>
      <div class="company-block">
        <strong id="p_company">نام شرکت</strong>
        <div id="p_company_address">نشانی شرکت</div>
      </div>
    </div>
    <h2 class="pay-title">Entgeltabrechnung</h2>
    <div class="meta">
      <div><small>Abrechnungszeitraum</small><b id="p_period">-</b></div>
      <div><small>Auszahlungsdatum</small><b id="p_pay_date">-</b></div>
    </div>
    <div class="parties">
      <div class="party"><small>Arbeitnehmer</small><b id="p_employee">-</b><span><small>Personalnummer</small><span id="p_employee_no">-</span></span></div>
      <div class="party"><small>Arbeitgeber</small><b id="p_company_short">-</b><span><small>Beschäftigungsbeginn</small><span id="p_start_date">-</span></span></div>
    </div>

    <h3 class="section-title">Bruttoentgelt / Bezüge</h3>
    <table><thead><tr><th>Bezeichnung</th><th class="amount">Betrag (EUR)</th></tr></thead>
      <tbody>
        <tr><td>Grundgehalt</td><td class="amount" id="p_base_pay">0,00</td></tr>
        <tr><td>Überstunden / Zuschläge</td><td class="amount" id="p_overtime">0,00</td></tr>
        <tr><td>Bonus / Einmalzahlungen</td><td class="amount" id="p_bonus">0,00</td></tr>
        <tr><td>Zulagen / Sonstige Bezüge</td><td class="amount" id="p_allowance">0,00</td></tr>
        <tr class="total-row"><td>Gesamtbrutto (manuell erfasst)</td><td class="amount" id="p_gross">0,00</td></tr>
      </tbody>
    </table>

    <h3 class="section-title">Abzüge Arbeitnehmer</h3>
    <table><thead><tr><th>Bezeichnung</th><th class="amount">Betrag (EUR)</th></tr></thead>
      <tbody>
        <tr><td>Lohnsteuer</td><td class="amount" id="p_tax">0,00</td></tr>
        <tr><td>Solidaritätszuschlag</td><td class="amount" id="p_soli">0,00</td></tr>
        <tr><td>Kirchensteuer</td><td class="amount" id="p_church">0,00</td></tr>
        <tr><td>Krankenversicherung</td><td class="amount" id="p_health">0,00</td></tr>
        <tr><td>Pflegeversicherung</td><td class="amount" id="p_care">0,00</td></tr>
        <tr><td>Rentenversicherung</td><td class="amount" id="p_pension">0,00</td></tr>
        <tr><td>Arbeitslosenversicherung</td><td class="amount" id="p_unemployment">0,00</td></tr>
        <tr><td>Sonstige Abzüge</td><td class="amount" id="p_other">0,00</td></tr>
        <tr><td>Vorschuss / Abschlag</td><td class="amount" id="p_advance">0,00</td></tr>
        <tr class="total-row"><td>Gesamtabzüge</td><td class="amount" id="p_deductions">0,00</td></tr>
      </tbody>
    </table>

    <h3 class="section-title">Arbeitgeberanteile (nicht vom Nettolohn abgezogen)</h3>
    <table><thead><tr><th>Bezeichnung</th><th class="amount">Betrag (EUR)</th></tr></thead>
      <tbody>
        <tr><td>Krankenversicherung Arbeitgeber</td><td class="amount" id="p_employer_health">0,00</td></tr>
        <tr><td>Pflegeversicherung Arbeitgeber</td><td class="amount" id="p_employer_care">0,00</td></tr>
        <tr><td>Rentenversicherung Arbeitgeber</td><td class="amount" id="p_employer_pension">0,00</td></tr>
        <tr><td>Arbeitslosenversicherung Arbeitgeber</td><td class="amount" id="p_employer_unemployment">0,00</td></tr>
      </tbody>
    </table>
    <div class="net-box"><span>Auszahlungsbetrag / خالص قابل پرداخت</span><strong id="p_net">0,00 €</strong></div>
    <div class="preview-foot">Erstellt mit manuell eingegebenen Beträgen. Diese Vorschau berechnet keine Lohnsteuer oder Sozialversicherungsbeiträge und ersetzt keine vollständige Entgeltbescheinigung oder geprüfte Lohnabrechnung.</div>
  </section>
</div>

<script>
(function(){
  const moneyIds = ["base_pay","overtime","bonus","allowance","tax","soli","church","health","care","pension","unemployment","other","advance","employer_health","employer_care","employer_pension","employer_unemployment"];
  const toCents = id => {
    const raw = document.getElementById(id).value;
    const parsed = Number(String(raw).replace(",", "."));
    return Number.isFinite(parsed) ? Math.round(parsed * 100) : 0;
  };
  const euro = cents => (cents / 100).toLocaleString("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2});
  const text = (id, value) => { document.getElementById(id).textContent = value || "-"; };
  const update = () => {
    ["company","company_address","employee","employee_no","period"].forEach(id => {
      const input=document.getElementById(id);
      const target={"company":"p_company","company_address":"p_company_address","employee":"p_employee","employee_no":"p_employee_no","period":"p_period"}[id];
      text(target,input.value.trim());
    });
    text("p_company_short",document.getElementById("company").value.trim());
    text("p_start_date",document.getElementById("start_date").value);
    text("p_pay_date",document.getElementById("pay_date").value);
    moneyIds.forEach(id => {
      const target=document.getElementById("p_"+id);
      if(target) target.textContent=euro(toCents(id));
    });
    const gross=["base_pay","overtime","bonus","allowance"].reduce((sum,id)=>sum+toCents(id),0);
    const deduction=["tax","soli","church","health","care","pension","unemployment","other","advance"].reduce((sum,id)=>sum+toCents(id),0);
    document.getElementById("p_gross").textContent=euro(gross);
    document.getElementById("p_deductions").textContent=euro(deduction);
    document.getElementById("p_net").textContent=euro(gross-deduction)+" €";
  };
  document.querySelectorAll("[data-bind],[data-money]").forEach(el=>el.addEventListener("input",update));
  document.getElementById("pdf_button").addEventListener("click",()=>window.print());
  document.getElementById("reset_button").addEventListener("click",()=>{
    document.querySelectorAll(".editor input").forEach(el=>{
      if(el.type==="file"){el.value="";return;}
      if(el.type==="number"){el.value="0";return;}
      el.value="";
    });
    document.getElementById("logo_area").innerHTML="LOGO<br>Unternehmen";
    update();
  });
  document.getElementById("logo_file").addEventListener("change",event=>{
    const file=event.target.files && event.target.files[0];
    const area=document.getElementById("logo_area");
    if(!file){area.innerHTML="LOGO<br>Unternehmen";return;}
    if(!["image/png","image/jpeg","image/webp"].includes(file.type) || file.size>2*1024*1024){
      event.target.value="";
      area.textContent="فقط PNG، JPG یا WebP تا ۲ مگابایت";
      return;
    }
    const reader=new FileReader();
    reader.onload=()=>{area.innerHTML="";const img=document.createElement("img");img.alt="Company logo";img.src=reader.result;area.appendChild(img);};
    reader.readAsDataURL(file);
  });
  update();
})();
</script>
</body></html>"""

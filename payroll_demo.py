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
      <div class="note">این فرم فقط در مرورگر اجرا می‌شود و اطلاعات یا لوگو به سرور ارسال نمی‌شوند. فقط با داده ساختگی آزمایش کن. محاسبات بیمه برای سناریوی استاندارد سال ۲۰۲۶ است و جایگزین سیستم حقوق و دستمزد معتبر نیست.</div>
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
      <h3>اطلاعات حقوق و بیمه</h3>
      <div class="fields">
        <div class="field"><label for="base_pay">حقوق پایه ماهانه ناخالص (€)</label><input id="base_pay" type="number" min="0" step="0.01" value="3000"></div>
        <div class="field"><label for="monthly_hours">ساعات قراردادی ماهانه</label><input id="monthly_hours" type="number" min="1" step="0.5" value="173.33"></div>
        <div class="field"><label for="bonus">پاداش/پرداخت یک‌باره ناخالص (€)</label><input id="bonus" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="allowance">سایر مزایای ناخالص (€)</label><input id="allowance" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="kasse">Krankenkasse</label><input id="kasse" placeholder="نام صندوق بیمه"></div>
        <div class="field"><label for="kv_extra">Zusatzbeitrag صندوق (%)</label><input id="kv_extra" type="number" min="0" max="10" step="0.01" value="2.9"></div>
        <div class="field"><label for="state">محل کار / Bundesland</label><select id="state"><option value="">انتخاب ایالت محل کار</option><option value="BW">Baden-Württemberg</option><option value="BY">Bayern</option><option value="BE">Berlin</option><option value="BB">Brandenburg</option><option value="HB">Bremen</option><option value="HH">Hamburg</option><option value="HE">Hessen</option><option value="MV">Mecklenburg-Vorpommern</option><option value="NI">Niedersachsen</option><option value="NW">Nordrhein-Westfalen</option><option value="RP">Rheinland-Pfalz</option><option value="SL">Saarland</option><option value="SN">Sachsen</option><option value="ST">Sachsen-Anhalt</option><option value="SH">Schleswig-Holstein</option><option value="TH">Thüringen</option></select></div>
        <div class="field"><label for="children">تعداد فرزندان زیر ۲۵ سال</label><select id="children"><option value="0">۰</option><option value="1">۱</option><option value="2">۲</option><option value="3">۳</option><option value="4">۴</option><option value="5">۵ یا بیشتر</option></select></div>
        <div class="field"><label><input id="under23" type="checkbox" style="width:auto"> کارمند هنوز ۲۳ ساله نشده است</label></div>
        <div class="field"><label for="health_rate">نرخ پایه Krankenversicherung (%)</label><input id="health_rate" type="number" min="0" max="30" step="0.01" value="14.6"></div>
      </div>
      <p class="muted">مبنای نسخه آزمایشی: کارمند عادیِ مشمول بیمه قانونی، حقوق ماهانه کامل و یک کارفرما. نرخ Zusatzbeitrag را مطابق صندوق واقعی انتخابی وارد کن. مواردی مانند Minijob، بیمه خصوصی، چند کارفرما، Kurzarbeit و شروع/پایان وسط ماه در این محاسبه‌گر پوشش داده نمی‌شوند.</p>
    </section>

    <section class="panel group">
      <h3>ساعات شیفت و Zuschläge</h3>
      <p class="muted">برای هر شیفت تاریخ، ساعت شروع و پایان و بازه استراحت را وارد کن. عبور از نیمه‌شب پشتیبانی می‌شود. تعطیلات عمومی آلمان و تعطیلات ایالت انتخابی به‌صورت خودکار از تقویم ۲۰۲۶ تشخیص داده می‌شوند؛ تاریخ‌های محلی/خاص را نیز می‌توانی اضافه کنی.</p>
      <div class="fields">
        <div class="field"><label for="night_rate">Zuschlag شب طبق قرارداد (%)</label><input id="night_rate" type="number" min="0" max="300" step="0.5" value="0"></div>
        <div class="field"><label for="sunday_rate">Zuschlag یکشنبه طبق قرارداد (%)</label><input id="sunday_rate" type="number" min="0" max="300" step="0.5" value="0"></div>
        <div class="field"><label for="holiday_rate">Zuschlag تعطیل رسمی طبق قرارداد (%)</label><input id="holiday_rate" type="number" min="0" max="300" step="0.5" value="0"></div>
        <div class="field full"><label for="holidays">تعطیلات محلی اضافه (اختیاری)</label><textarea id="holidays" rows="3" style="width:100%;padding:10px;border:1px solid #bbc5d2;border-radius:8px;font:inherit" placeholder="2026-08-08"></textarea></div>
      </div>
      <div style="overflow-x:auto;margin-top:12px">
        <table id="shift_table"><thead><tr><th>تاریخ</th><th>شروع</th><th>پایان</th><th>استراحت از</th><th>استراحت تا</th><th></th></tr></thead><tbody id="shift_rows"></tbody></table>
      </div>
      <div class="actions"><button class="secondary" id="add_shift" type="button">افزودن شیفت</button></div>
      <p id="shift_summary" class="muted">ساعات شب، یکشنبه و تعطیل پس از ورود شیفت محاسبه می‌شوند.</p>
    </section>

    <section class="panel group">
      <h3>مالیات و سایر کسورات دستی</h3>
      <p class="muted">مالیات حقوق در این نسخه از کلاس مالیاتی و مشخصات فردی محاسبه نمی‌شود. ارقام مالیاتی را فقط در صورت داشتن محاسبه معتبر وارد کن.</p>
      <div class="fields">
        <div class="field"><label for="tax">Lohnsteuer (€)</label><input id="tax" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="soli">Solidaritätszuschlag (€)</label><input id="soli" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="church">Kirchensteuer (€)</label><input id="church" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="other">سایر کسورات (€)</label><input id="other" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="advance">پیش‌پرداخت قبلی / Vorschuss (€)</label><input id="advance" type="number" min="0" step="0.01" value="0"></div>
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
        <tr><td>Nachtzuschläge</td><td class="amount" id="p_night_pay">0,00</td></tr><tr><td>Sonntagszuschläge</td><td class="amount" id="p_sunday_pay">0,00</td></tr><tr><td>Feiertagszuschläge</td><td class="amount" id="p_holiday_pay">0,00</td></tr>
        <tr><td>Bonus / Einmalzahlungen</td><td class="amount" id="p_bonus">0,00</td></tr>
        <tr><td>Zulagen / Sonstige Bezüge</td><td class="amount" id="p_allowance">0,00</td></tr>
        <tr class="total-row"><td>Gesamtbrutto (manuell erfasst)</td><td class="amount" id="p_gross">0,00</td></tr>
      </tbody>
    </table>

    <h3 class="section-title">Steuer- und Sozialversicherungsbasis der Zuschläge</h3><table><tbody><tr><td>Steuerfrei geschätzter Zuschlagsanteil</td><td class="amount" id="p_tax_free">0,00</td></tr><tr><td>Sozialversicherungsfrei geschätzter Zuschlagsanteil</td><td class="amount" id="p_sv_free">0,00</td></tr><tr><td>SV-pflichtiges Brutto</td><td class="amount" id="p_sv_gross">0,00</td></tr></tbody></table>
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
    <div class="preview-foot">Automatische Beispielrechnung mit 2026-Rechengrößen für den Standardfall. Zuschlagssätze richten sich nach Vertrag oder Tarif. Die ausgewiesenen Steuer-/SV-Freibeträge sind Näherungen nach den eingegebenen Schichtdaten. Lohnsteuer wird nicht berechnet. Sonderfälle, Nachweise und vollständige Abrechnung müssen durch ein geeignetes Lohnabrechnungssystem geprüft werden.</div>
  </section>
</div>

<script>
(function(){
  const $ = id => document.getElementById(id);
  const cents = value => Math.round((Number(String(value || "0").replace(",",".")) || 0) * 100);
  const val = id => Number($(id).value || 0);
  const money = n => (n/100).toLocaleString("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2});
  const set = (id,n) => { if($(id)) $(id).textContent=money(n); };
  const rate = id => Math.max(0,Math.min(300,val(id)))/100;
  const shiftRows = $("shift_rows");

  function addShift(date="",start="20:00",end="06:00",breakStart="",breakEnd=""){
    const tr=document.createElement("tr");
    [["date","date",date],["start","time",start],["end","time",end],["break_start","time",breakStart],["break_end","time",breakEnd]].forEach(([name,type,value])=>{
      const td=document.createElement("td"),input=document.createElement("input");
      input.type=type;input.dataset.shift=name;input.value=value;input.style.minWidth=type==="date"?"135px":"105px";
      input.addEventListener("input",update);td.appendChild(input);tr.appendChild(td);
    });
    const td=document.createElement("td"),remove=document.createElement("button");
    remove.type="button";remove.className="secondary";remove.textContent="حذف";
    remove.addEventListener("click",()=>{tr.remove();update();});
    td.appendChild(remove);tr.appendChild(td);shiftRows.appendChild(tr);update();
  }
  function parseClock(s){
    if(!/^([01]\d|2[0-3]):[0-5]\d$/.test(s||"")) return null;
    const [h,m]=s.split(":").map(Number);return h*60+m;
  }
  function isoDate(d){return d.toISOString().slice(0,10);}
  function easterSunday(year){
    const a=year%19,b=Math.floor(year/100),c=year%100,d=Math.floor(b/4),e=b%4,f=Math.floor((b+8)/25),g=Math.floor((b-f+1)/3);
    const h=(19*a+b-d-g+15)%30,i=Math.floor(c/4),k=c%4,l=(32+2*e+2*i-h-k)%7,m=Math.floor((a+11*h+22*l)/451);
    const month=Math.floor((h+l-7*m+114)/31),day=((h+l-7*m+114)%31)+1;
    return new Date(Date.UTC(year,month-1,day));
  }
  function plusDays(date,days){const d=new Date(date);d.setUTCDate(d.getUTCDate()+days);return isoDate(d);}
  function holidaysFor(year,state){
    const easter=easterSunday(year),goodFriday=plusDays(easter,-2),easterMonday=plusDays(easter,1);
    const ascension=plusDays(easter,39),whitMonday=plusDays(easter,50),corpus=plusDays(easter,60);
    const set=new Set([year+"-01-01",goodFriday,plusDays(easter,0),easterMonday,ascension,plusDays(easter,49),whitMonday,year+"-05-01",year+"-10-03",year+"-12-25",year+"-12-26"]);
    const add=(...dates)=>dates.forEach(d=>set.add(d));
    if(state==="BB"){add(plusDays(easter,0),plusDays(easter,49));}
    if(["BW","BY","ST"].includes(state))add(year+"-01-06");
    if(["BE","MV"].includes(state))add(year+"-03-08");
    if(["BW","BY","HE","NW","RP","SL"].includes(state))add(corpus);
    if(["BW","BY","NW","RP","SL"].includes(state))add(year+"-11-01");
    if(["BB","HB","HH","MV","NI","SN","ST","SH","TH"].includes(state))add(year+"-10-31");
    if(state==="SL")add(year+"-08-15");
    if(state==="TH")add(year+"-09-20");
    if(state==="SN"){
      const nov23=new Date(Date.UTC(year,10,23)),delta=(nov23.getUTCDay()+4)%7;
      add(plusDays(nov23,-delta));
    }
    return set;
  }
  function getShifts(){
    const holidays=new Set();[...shiftRows.querySelectorAll('input[data-shift="date"]')].forEach(el=>{if(/^\d{4}-\d{2}-\d{2}$/.test(el.value)) holidaysFor(Number(el.value.slice(0,4)),$("state").value).forEach(d=>holidays.add(d));});$("holidays").value.split(/[\s,;]+/).map(x=>x.trim()).filter(x=>/^\d{4}-\d{2}-\d{2}$/.test(x)).forEach(d=>holidays.add(d));
    let night=0,sunday=0,holiday=0,nightTaxFree=0,sundayTaxFree=0,holidayTaxFree=0,errors=[];
    [...shiftRows.querySelectorAll("tr")].forEach((tr,index)=>{
      const get=name=>tr.querySelector('[data-shift="'+name+'"]').value;
      const date=get("date"),start=parseClock(get("start")),end=parseClock(get("end"));
      const bs=get("break_start")?parseClock(get("break_start")):null,be=get("break_end")?parseClock(get("break_end")):null;
      if(!date||start===null||end===null){errors.push("شیفت "+(index+1)+": تاریخ و ساعت شروع/پایان را کامل کن.");return;}
      if((get("break_start")&&!get("break_end"))||(!get("break_start")&&get("break_end"))||((bs===null)!==(be===null))){errors.push("شیفت "+(index+1)+": هر دو ساعت استراحت را وارد کن یا هر دو را خالی بگذار.");return;}
      const [y,m,d]=date.split("-").map(Number);
      let cursor=Date.UTC(y,m-1,d,Math.floor(start/60),start%60),finish=Date.UTC(y,m-1,d,Math.floor(end/60),end%60);
      if(finish<=cursor) finish+=86400000;
      let breakFrom=null,breakTo=null;
      if(bs!==null&&be!==null){
        breakFrom=Date.UTC(y,m-1,d,Math.floor(bs/60),bs%60);breakTo=Date.UTC(y,m-1,d,Math.floor(be/60),be%60);
        if(breakFrom<cursor)breakFrom+=86400000;
        if(breakTo<=breakFrom)breakTo+=86400000;
        if(breakFrom<cursor||breakTo>finish){errors.push("شیفت "+(index+1)+": بازه استراحت باید داخل شیفت باشد.");return;}
      }
      const startedBeforeMidnight=start>=12*60;
      for(let t=cursor;t<finish;t+=60000){
        if(breakFrom!==null&&t>=breakFrom&&t<breakTo)continue;
        const dt=new Date(t),day=dt.getUTCDay(),mins=dt.getUTCHours()*60+dt.getUTCMinutes();
        const dateIso=isoDate(new Date(Date.UTC(dt.getUTCFullYear(),dt.getUTCMonth(),dt.getUTCDate())));
        const isNight=mins>=1200||mins<360,isSunday=day===0;
        const isHoliday=holidays.has(dateIso);
        if(isNight)night++;if(isSunday)sunday++;if(isHoliday)holiday++;
        if(isNight)nightTaxFree+=(startedBeforeMidnight&&mins<240?0.40:0.25)/60;
        if(isSunday&&!isHoliday)sundayTaxFree+=0.50/60;
        if(isHoliday){
          const special150=dateIso.endsWith("-05-01")||dateIso.endsWith("-12-25")||dateIso.endsWith("-12-26");
          holidayTaxFree+=(special150?1.50:1.25)/60;
        }
      }
    });
    return {night,sunday,holiday,nightTaxFree,sundayTaxFree,holidayTaxFree,errors};
  }
  function calc(){
    const base=cents($("base_pay").value),hours=val("monthly_hours"),bonus=cents($("bonus").value),allowance=cents($("allowance").value);
    const hourly=hours>0?(base/100)/hours:0,shifts=getShifts();
    const nightHours=shifts.night/60,sundayHours=shifts.sunday/60,holidayHours=shifts.holiday/60;
    const nightPay=Math.round(hourly*nightHours*rate("night_rate")*100);
    const sundayPay=Math.round(hourly*sundayHours*rate("sunday_rate")*100);
    const holidayPay=Math.round(hourly*holidayHours*rate("holiday_rate")*100);
    const premium=nightPay+sundayPay+holidayPay,gross=base+bonus+allowance+premium;
    const taxHourly=Math.min(hourly,50),svHourly=Math.min(hourly,25);
    const taxFree=Math.min(nightPay,Math.round(taxHourly*100*shifts.nightTaxFree))+Math.min(sundayPay,Math.round(taxHourly*100*shifts.sundayTaxFree))+Math.min(holidayPay,Math.round(taxHourly*100*shifts.holidayTaxFree));
    const svFree=Math.min(nightPay,Math.round(svHourly*100*shifts.nightTaxFree))+Math.min(sundayPay,Math.round(svHourly*100*shifts.sundayTaxFree))+Math.min(holidayPay,Math.round(svHourly*100*shifts.holidayTaxFree));
    const svGross=Math.max(0,gross-svFree);
    const kvBase=Math.min(svGross,581250),rvBase=Math.min(svGross,845000);
    const kvRate=(val("health_rate")+val("kv_extra"))/100;
    const kvEmployee=Math.round(kvBase*kvRate/2),kvEmployer=kvEmployee;
    const rvEmployee=Math.round(rvBase*0.093),rvEmployer=rvEmployee;
    const avEmployee=Math.round(rvBase*0.013),avEmployer=avEmployee;
    const selectedState=$("state").value,saxony=selectedState==="SN",stateSelected=Boolean(selectedState),childCount=Number($("children").value||0),under23=$("under23").checked;
    let pvEmployeeRate=childCount>=2?1.8-(Math.min(childCount,5)-1)*0.25:(childCount===1||under23?1.8:2.4);
    if(saxony)pvEmployeeRate+=0.5;
    const pvEmployerRate=saxony?1.3:1.8;
    const pvBase=Math.min(svGross,581250);
    const pvEmployee=stateSelected?Math.round(pvBase*pvEmployeeRate/100):0,pvEmployer=stateSelected?Math.round(pvBase*pvEmployerRate/100):0;
    const employeeSocial=kvEmployee+pvEmployee+rvEmployee+avEmployee,employerSocial=kvEmployer+pvEmployer+rvEmployer+avEmployer;
    const manualTax=cents($("tax").value)+cents($("soli").value)+cents($("church").value),other=cents($("other").value)+cents($("advance").value);
    const deductions=employeeSocial+manualTax+other,net=gross-deductions;
    return {base,bonus,allowance,hourly,shifts,nightHours,sundayHours,holidayHours,nightPay,sundayPay,holidayPay,premium,gross,taxFree,svFree,svGross,kvBase,rvBase,kvEmployee,kvEmployer,pvEmployee,pvEmployer,rvEmployee,rvEmployer,avEmployee,avEmployer,employeeSocial,employerSocial,manualTax,other,deductions,net,stateSelected};
  }
  function update(){
    const r=calc();
    set("p_base_pay",r.base);set("p_bonus",r.bonus);set("p_allowance",r.allowance);set("p_night_pay",r.nightPay);set("p_sunday_pay",r.sundayPay);set("p_holiday_pay",r.holidayPay);set("p_tax_free",r.taxFree);set("p_sv_free",r.svFree);set("p_sv_gross",r.svGross);
    set("p_gross",r.gross);set("p_tax",r.manualTax);set("p_health",r.kvEmployee);set("p_care",r.pvEmployee);
    set("p_pension",r.rvEmployee);set("p_unemployment",r.avEmployee);set("p_other",r.other);$("p_care").textContent=r.stateSelected?money(r.pvEmployee):"—";$("p_employer_care").textContent=r.stateSelected?money(r.pvEmployer):"—";
    set("p_deductions",r.deductions);set("p_net",r.net);
    set("p_employer_health",r.kvEmployer);set("p_employer_care",r.pvEmployer);set("p_employer_pension",r.rvEmployer);set("p_employer_unemployment",r.avEmployer);
    $("p_company").textContent=$("company").value||"-";$("p_company_address").textContent=$("company_address").value||"-";
    $("p_employee").textContent=$("employee").value||"-";$("p_employee_no").textContent=$("employee_no").value||"-";
    $("p_company_short").textContent=$("company").value||"-";$("p_period").textContent=$("period").value||"-";
    $("p_start_date").textContent=$("start_date").value||"-";$("p_pay_date").textContent=$("pay_date").value||"-";
    $("shift_summary").textContent="شب: "+r.nightHours.toFixed(2)+" ساعت | یکشنبه: "+r.sundayHours.toFixed(2)+" ساعت | تعطیل رسمی: "+r.holidayHours.toFixed(2)+" ساعت | Zuschläge: "+money(r.premium)+" € | معاف از بیمه (برآورد): "+money(r.svFree)+" € | مبنای بیمه: "+money(r.svGross)+" €"+(!r.stateSelected?" | برای محاسبه خالص، ایالت محل کار را انتخاب کن.":"")+(r.shifts.errors.length?" | "+r.shifts.errors.join(" "):"");
    $("p_gross").parentElement.cells[0].textContent="Gesamtbrutto einschließlich Zuschläge";
    $("p_tax").parentElement.cells[0].textContent="Lohnsteuer / Soli / Kirchensteuer (manuell zusammengefasst)";
    $("p_other").parentElement.cells[0].textContent="Sonstige Abzüge und Vorschuss";
    $("p_advance").parentElement.style.display="none";$("p_soli").parentElement.style.display="none";$("p_church").parentElement.style.display="none";
    $("p_tax").parentElement.cells[1].textContent=money(r.manualTax);$("p_other").parentElement.cells[1].textContent=money(r.other);
    $("p_gross").parentElement.cells[1].textContent=money(r.gross);
    $("p_deductions").parentElement.cells[1].textContent=money(r.deductions);$("p_net").textContent=r.stateSelected?money(r.net)+" €":"ایالت محل کار را انتخاب کن";
    $("shift_summary").style.color=r.shifts.errors.length?"#9b2c2c":"";
  }
  $("add_shift").addEventListener("click",()=>addShift());
  $("pdf_button").addEventListener("click",()=>{const r=calc();if(!r.stateSelected){window.alert("ابتدا ایالت محل کار را انتخاب کن.");return;}if(r.shifts.errors.length){window.alert(r.shifts.errors.join(String.fromCharCode(10)));return;}window.print();});
  $("reset_button").addEventListener("click",()=>{
    document.querySelectorAll(".editor input").forEach(el=>{
      if(el.type==="file"){el.value="";return;}if(el.type==="checkbox"){el.checked=false;return;}
      if(el.type==="number"){el.value=el.id==="base_pay"?"3000":el.id==="monthly_hours"?"173.33":el.id==="kv_extra"?"2.9":el.id==="health_rate"?"14.6":"0";return;}el.value="";
    });
    $("state").value="";$("children").value="0";$("holidays").value="";shiftRows.innerHTML="";
    $("logo_area").innerHTML="LOGO<br>Unternehmen";update();
  });
  $("logo_file").addEventListener("change",event=>{
    const file=event.target.files&&event.target.files[0],area=$("logo_area");
    if(!file){area.innerHTML="LOGO<br>Unternehmen";return;}
    if(!["image/png","image/jpeg","image/webp"].includes(file.type)||file.size>2*1024*1024){event.target.value="";area.textContent="فقط PNG، JPG یا WebP تا ۲ مگابایت";return;}
    const reader=new FileReader();reader.onload=()=>{area.innerHTML="";const img=document.createElement("img");img.alt="Company logo";img.src=reader.result;area.appendChild(img);};reader.readAsDataURL(file);
  });
  document.querySelectorAll(".editor input,.editor select,.editor textarea").forEach(el=>el.addEventListener("input",update));
  addShift();
})();
</script>
</body></html>"""

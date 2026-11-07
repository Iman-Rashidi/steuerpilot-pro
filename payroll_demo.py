"""Browser-only 2026 German payroll demonstration."""

from pathlib import Path

_ENGINE_JS = Path(__file__).with_name("payroll_engine.js").read_text(encoding="utf-8")

_PAGE = r"""<!doctype html>
<html lang="fa" dir="rtl"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>SteuerPilot Pro · فیش حقوقی</title>
<style>
:root{font-family:system-ui,sans-serif;color:#172033;background:#f3f5f8;line-height:1.5}*{box-sizing:border-box}
body{max-width:1250px;margin:20px auto;padding:0 14px}header,.panel{background:white;border:1px solid #dce2ea;border-radius:12px;padding:15px;margin:12px 0}
.layout{display:grid;grid-template-columns:1fr 1fr;gap:14px;align-items:start}.editor{display:grid;gap:12px}.group{border:1px solid #e1e6ec;border-radius:9px;padding:12px}
h1,h2,h3{margin-top:0}.muted{color:#5b6675;font-size:13px}.fields{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:9px}.full{grid-column:1/-1}
label{display:block;font-size:13px;font-weight:650;margin-bottom:4px}input,select{width:100%;padding:9px;border:1px solid #bac5d3;border-radius:8px;font:inherit;background:white}
input[type=checkbox]{width:auto}.check{display:flex;align-items:center;gap:8px;margin:8px 0}.note{background:#f4f6f8;padding:10px;border-radius:8px;font-size:13px;border-right:4px solid #7a8796}
.legal{background:#fff8e8;padding:10px;border-radius:8px;font-size:13px;border-right:4px solid #c58a00}
button{border:0;border-radius:8px;padding:9px 13px;font:inherit;cursor:pointer}.primary{background:#203b63;color:white}.secondary{background:#e8eef6;color:#203b63}
.shift{border:1px solid #e0e5eb;border-radius:8px;padding:9px;margin:8px 0;background:#fbfcfd}.shift-grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:7px}.shift label{font-size:12px}.remove{background:#f1f2f4;color:#444;padding:6px 9px;margin-top:5px}
.calc-error{display:none;background:#fff0f0;color:#8c1d18;padding:9px;border-radius:8px}
.preview{direction:ltr;text-align:left;background:white;border:1px solid #cfd7e2;border-radius:12px;padding:17px}
.top{display:flex;justify-content:space-between;gap:12px;border-bottom:2px solid #203b63;padding-bottom:10px}.logo{width:130px;height:70px;border:1px dashed #9aa7b7;border-radius:8px;display:flex;align-items:center;justify-content:center;overflow:hidden;color:#66758a;font-size:12px}
.logo img{max-width:100%;max-height:100%;object-fit:contain}.co{text-align:right;direction:rtl;flex:1}.meta,.parties{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin:10px 0}.meta div,.party{background:#f4f6f8;border-radius:7px;padding:7px}.meta small,.party small{display:block;color:#596779;font-size:10px}
table{width:100%;border-collapse:collapse;font-size:11px;margin:6px 0 10px}th,td{padding:5px;border-bottom:1px solid #e2e7ed;text-align:left}th{background:#f0f3f6}.amount{text-align:right;white-space:nowrap}.section{font-size:13px;margin:9px 0 2px}.total{font-weight:700;background:#f4f7fb}
.net{border:2px solid #203b63;border-radius:8px;padding:10px;display:flex;justify-content:space-between;font-weight:750;margin-top:10px}.tiny{font-size:9px;color:#596779;margin-top:12px}
.actions{display:flex;gap:8px;flex-wrap:wrap}
@media(max-width:920px){.layout{grid-template-columns:1fr}}@media(max-width:520px){.fields,.meta,.parties{grid-template-columns:1fr}.shift-grid{grid-template-columns:1fr 1fr}.preview{padding:9px}}
@page{size:A4;margin:10mm}@media print{body{margin:0;padding:0;max-width:none;background:white}header,.editor,.actions{display:none!important}.layout{display:block}.preview{border:0;padding:0}}
</style></head>
<body>
<header><h1>محاسبه حقوق و فیش حقوقی | Lohnabrechnung</h1><p class="muted">محاسبه زنده حقوق پایه، بیمه‌های اجتماعی و اضافه‌حقوق شیفت‌ها با خروجی PDF.</p><a href="/">بازگشت به صفحه اصلی</a></header>
<div class="layout">
<main class="editor">
<section class="panel"><div class="note">اطلاعات فقط در مرورگر محاسبه می‌شوند و به سرور ارسال یا ذخیره نمی‌شوند. فقط داده ساختگی وارد کن. نرخ‌های بیمه این نسخه برای سال ۲۰۲۶ و استخدام معمولیِ مشمول بیمه قانونی است؛ Minijob، Midijob، دانشجو، کارآموز، بیمه خصوصی و وضعیت‌های خاص در آن پوشش داده نشده‌اند.</div></section>
<section class="panel group"><h3>شرکت و لوگو</h3><div class="fields">
<div class="full"><label>نام شرکت</label><input id="company" placeholder="Muster GmbH"></div>
<div class="full"><label>نشانی شرکت</label><input id="company_address" placeholder="Musterstraße 1, 00000 Musterstadt"></div>
<div class="full"><label>لوگو</label><input id="logo_file" type="file" accept="image/png,image/jpeg,image/webp"></div>
</div></section>
<section class="panel group"><h3>کارمند، دوره و ایالت</h3><div class="fields">
<div><label>نام کارمند</label><input id="employee" placeholder="Max Mustermann"></div>
<div><label>شماره کارمند</label><input id="employee_no" placeholder="M-001"></div>
<div><label>شروع همکاری</label><input id="start_date" type="date"></div>
<div><label>ماه حقوق</label><input id="period" type="month" value="2026-11"></div>
<div><label>تاریخ پرداخت</label><input id="pay_date" type="date"></div>
<div><label>ایالت محل کار</label><select id="state">
<option value="NW">Nordrhein-Westfalen</option><option value="BW">Baden-Württemberg</option><option value="BY">Bayern</option><option value="BE">Berlin</option><option value="BB">Brandenburg</option><option value="HB">Bremen</option><option value="HH">Hamburg</option><option value="HE">Hessen</option><option value="MV">Mecklenburg-Vorpommern</option><option value="NI">Niedersachsen</option><option value="RP">Rheinland-Pfalz</option><option value="SL">Saarland</option><option value="SN">Sachsen</option><option value="ST">Sachsen-Anhalt</option><option value="SH">Schleswig-Holstein</option><option value="TH">Thüringen</option></select></div>
</div></section>
<section class="panel group"><h3>حقوق ناخالص و Krankenkasse</h3><div class="fields">
<div><label>حقوق پایه ماهانه (€)</label><input id="monthly_gross" type="number" min="0" step=".01" value="3000"></div>
<div><label>ساعات قرارداد در هفته</label><input id="weekly_hours" type="number" min="1" max="60" step=".25" value="40"></div>
<div><label>نام Krankenkasse</label><input id="krankenkasse" placeholder="نام صندوق"></div>
<div><label>Zusatzbeitrag صندوق (%)</label><input id="gkv_additional" type="number" min="0" max="10" step=".01" value="2.9"></div>
<div><label>فرزندان زیر ۲۵ سال (۰ تا ۵)</label><input id="children_under25" type="number" min="0" max="5" step="1" value="0"></div>
</div>
<label class="check"><input id="childless23" type="checkbox" checked> بدون فرزند و حداقل ۲۳ ساله</label>
<p class="muted">میانگین Zusatzbeitrag در ۲۰۲۶ برابر ۲٫۹٪ است، اما نرخ هر صندوق فرق می‌کند. <a href="https://www.gkv-spitzenverband.de/krankenversicherung/kv_grundprinzipien/finanzierung/zusatzbeitragssatz/zusatzbeitragssatz.jsp" target="_blank" rel="noopener">فهرست نرخ‌های GKV</a></p>
</section>
<section class="panel group"><h3>درصدهای اضافه‌حقوق طبق قرارداد</h3><p class="muted">درصد واقعی پرداخت را از قرارداد یا Tarifvertrag وارد کن؛ برای یکشنبه و تعطیلات نرخ پرداخت اجباری یکسانی برای همه شرکت‌ها وجود ندارد.</p><div class="fields">
<div><label>شب‌کاری Nacht (%)</label><input id="night_rate" type="number" min="0" max="300" step=".1" value="0"></div>
<div><label>یکشنبه Sonntag (%)</label><input id="sunday_rate" type="number" min="0" max="300" step=".1" value="0"></div>
<div><label>تعطیل رسمی Feiertag (%)</label><input id="holiday_rate" type="number" min="0" max="300" step=".1" value="0"></div>
<div><label>تعطیلات خاص (%)</label><input id="special_holiday_rate" type="number" min="0" max="300" step=".1" value="0"></div>
</div><p class="muted">سقف معافیت مالیاتی §3b EStG: شب ۲۵٪، ساعت ۰۰ تا ۰۴ در ادامه شیفت شبِ شروع‌شده قبل از نیمه‌شب ۴۰٪، یکشنبه ۵۰٪، تعطیل رسمی ۱۲۵٪ و برخی روزهای خاص ۱۵۰٪ از Grundlohn تا سقف ۵۰ یورو در ساعت. این‌ها سقف معافیت‌اند، نه نرخ اجباری پرداخت.</p></section>
<section class="panel group"><h3>ثبت ساعات شیفت</h3><p class="muted">تاریخ، شروع، پایان و در صورت وجود بازه استراحت را وارد کن. عبور شیفت از نیمه‌شب محاسبه می‌شود.</p><div id="shifts"></div><button class="secondary" id="add_shift" type="button">افزودن شیفت</button>
<div class="full" style="margin-top:10px"><label>تعطیلات رسمی محلی اضافی، تاریخ‌ها با کاما</label><input id="extra_holidays" placeholder="2026-08-08, 2026-08-15"><p class="muted">برای تعطیلات محلی شهرداری، تاریخ را اینجا اضافه کن.</p></div></section>
<section class="panel group"><h3>مالیات حقوق و سایر کسورات</h3><p class="muted">بیمه‌های اجتماعی خودکار محاسبه می‌شوند. Lohnsteuer، Solidaritätszuschlag و Kirchensteuer به ELStAM و شرایط شخصی وابسته‌اند و در این نسخه خودکار نیستند؛ مبلغ معتبر را وارد کن.</p><div class="fields">
<div><label>Lohnsteuer (€)</label><input id="wage_tax" type="number" min="0" step=".01" value="0"></div>
<div><label>Solidaritätszuschlag (€)</label><input id="solidarity_tax" type="number" min="0" step=".01" value="0"></div>
<div><label>Kirchensteuer (€)</label><input id="church_tax" type="number" min="0" step=".01" value="0"></div>
<div><label>Vorschuss (€)</label><input id="advance" type="number" min="0" step=".01" value="0"></div>
</div></section>
<div class="calc-error" id="calc_error" role="alert"></div>
<div class="actions"><button class="primary" id="pdf_button" type="button">ساخت PDF / Drucken</button><button class="secondary" id="reset_button" type="button">پاک‌کردن</button></div>
</main>

<section class="preview">
<div class="top"><div class="logo" id="logo_area">LOGO<br>Unternehmen</div><div class="co"><strong id="p_company">نام شرکت</strong><div id="p_company_address">نشانی شرکت</div></div></div>
<h2>Entgeltabrechnung</h2><div class="meta"><div><small>Abrechnungszeitraum</small><b id="p_period">2026-11</b></div><div><small>Auszahlungsdatum</small><b id="p_pay_date">-</b></div></div>
<div class="parties"><div class="party"><small>Arbeitnehmer</small><b id="p_employee">-</b><small>Personalnummer</small><span id="p_employee_no">-</span></div><div class="party"><small>Arbeitgeber</small><b id="p_company_short">-</b><small>Eintritt</small><span id="p_start_date">-</span></div></div>
<h3 class="section">Bruttoentgelt</h3><table><tbody>
<tr><td>Grundgehalt</td><td class="amount" id="p_monthly_gross">0,00</td></tr><tr><td>Nachtzuschläge</td><td class="amount" id="p_night">0,00</td></tr><tr><td>Sonntagszuschläge</td><td class="amount" id="p_sunday">0,00</td></tr><tr><td>Feiertagszuschläge</td><td class="amount" id="p_holiday">0,00</td></tr><tr><td>Besondere Feiertage</td><td class="amount" id="p_special_holiday">0,00</td></tr>
<tr class="total"><td>Gesamtbrutto</td><td class="amount" id="p_gross">0,00</td></tr><tr><td>SFN steuerfrei</td><td class="amount" id="p_taxfree_sfn">0,00</td></tr><tr><td>SFN steuerpflichtig</td><td class="amount" id="p_taxable_sfn">0,00</td></tr>
</tbody></table>
<h3 class="section">Arbeitszeit (Stunden)</h3><table><tbody>
<tr><td>Gesamt</td><td class="amount" id="p_hours_worked">0,00</td></tr><tr><td>Nacht</td><td class="amount" id="p_hours_night">0,00</td></tr><tr><td>Sonntag</td><td class="amount" id="p_hours_sunday">0,00</td></tr><tr><td>Feiertag</td><td class="amount" id="p_hours_holiday">0,00</td></tr><tr><td>Besondere Feiertage</td><td class="amount" id="p_hours_special">0,00</td></tr>
</tbody></table>
<h3 class="section">Sozialversicherung Arbeitnehmer</h3><table><tbody>
<tr><td>Krankenversicherung</td><td class="amount" id="p_health">0,00</td></tr><tr><td>Pflegeversicherung</td><td class="amount" id="p_care">0,00</td></tr><tr><td>Rentenversicherung</td><td class="amount" id="p_pension">0,00</td></tr><tr><td>Arbeitslosenversicherung</td><td class="amount" id="p_unemployment">0,00</td></tr><tr class="total"><td>Summe Sozialversicherung</td><td class="amount" id="p_employee_social">0,00</td></tr>
</tbody></table>
<h3 class="section">Steuern und sonstige Abzüge</h3><table><tbody>
<tr><td>Lohnsteuer</td><td class="amount" id="p_wage_tax">0,00</td></tr><tr><td>Solidaritätszuschlag</td><td class="amount" id="p_solidarity_tax">0,00</td></tr><tr><td>Kirchensteuer</td><td class="amount" id="p_church_tax">0,00</td></tr><tr><td>Vorschuss</td><td class="amount" id="p_advance">0,00</td></tr></tbody></table>
<h3 class="section">Arbeitgeberanteile</h3><table><tbody>
<tr><td>Krankenversicherung</td><td class="amount" id="p_employer_health">0,00</td></tr><tr><td>Pflegeversicherung</td><td class="amount" id="p_employer_care">0,00</td></tr><tr><td>Rentenversicherung</td><td class="amount" id="p_employer_pension">0,00</td></tr><tr><td>Arbeitslosenversicherung</td><td class="amount" id="p_employer_unemployment">0,00</td></tr><tr class="total"><td>Summe Arbeitgeberanteile</td><td class="amount" id="p_employer_social">0,00</td></tr>
</tbody></table>
<p class="tiny">Krankenkasse: <span id="p_krankenkasse">-</span> · Zusatzbeitrag: <span id="p_additional_rate">2,90%</span><br>SV-Brutto: <span id="p_sv_base">0,00 €</span> · KV/PV-Grundlage: <span id="p_health_base">0,00 €</span> · RV/AV-Grundlage: <span id="p_pension_base">0,00 €</span></p>
<div class="net"><span>Auszahlungsbetrag / Nettolohn</span><strong id="p_net">0,00 €</strong></div>
<div class="tiny">Rechenmodell 2026 für reguläre Beschäftigung mit gesetzlicher Krankenversicherung. Lohnsteuer/ELStAM, Minijob, Midijob, private Versicherung, Mehrfachbeschäftigung, Einmalzahlungen und Teilmonate sind nicht vollständig berechnet. Keine vollständige gesetzliche Entgeltbescheinigung oder produktive Lohnabrechnung.</div>
</section></div>

<script>/*ENGINE_JS*/</script>
<script>
(function(){
const $=id=>document.getElementById(id), euro=n=>Number(n||0).toLocaleString("de-DE",{minimumFractionDigits:2,maximumFractionDigits:2});
const put=(id,v)=>{$(id).textContent=(v===undefined||v===null||v==="")?"-":v;};
function addShift(){
const row=document.createElement("div");row.className="shift";row.innerHTML='<div class="shift-grid">'+
'<div><label>تاریخ</label><input type="date" data-shift="date"></div><div><label>شروع</label><input type="time" data-shift="start"></div>'+
'<div><label>پایان</label><input type="time" data-shift="end"></div><div><label>شروع استراحت</label><input type="time" data-shift="breakStart"></div>'+
'<div><label>پایان استراحت</label><input type="time" data-shift="breakEnd"></div></div><button type="button" class="remove">حذف شیفت</button>';
$("shifts").appendChild(row);
}
function collectShifts(){
const out=[];document.querySelectorAll(".shift").forEach(row=>{const v=k=>row.querySelector('[data-shift="'+k+'"]').value;
const s={date:v("date"),start:v("start"),end:v("end"),breakStart:v("breakStart"),breakEnd:v("breakEnd")};
if(s.date||s.start||s.end||s.breakStart||s.breakEnd)out.push(s);});return out;
}
function n(id){const v=Number($(id).value);if(!Number.isFinite(v))throw new Error("یک فیلد عددی معتبر نیست.");return v;}
function input(){
const period=$("period").value,shifts=collectShifts();
if(!period||!period.startsWith("2026-"))throw new Error("نرخ‌های بیمه این نسخه برای سال ۲۰۲۶ هستند.");
if(shifts.some(s=>!s.date.startsWith("2026-")))throw new Error("تاریخ تمام شیفت‌ها باید در سال ۲۰۲۶ باشد.");
const children=n("children_under25");
return {monthlyGross:n("monthly_gross"),weeklyHours:n("weekly_hours"),state:$("state").value,gkvAdditionalRate:n("gkv_additional"),
childrenUnder25:children,childless23:$("childless23").checked&&children===0,
premiumRates:{night:n("night_rate"),sunday:n("sunday_rate"),holiday:n("holiday_rate"),specialHoliday:n("special_holiday_rate")},
shifts,extraHolidayDates:$("extra_holidays").value.split(",").map(s=>s.trim()).filter(Boolean),
wageTax:n("wage_tax"),solidarityTax:n("solidarity_tax"),churchTax:n("church_tax"),advance:n("advance")};
}
function update(){
try{
const r=window.SteuerPilotPayroll.calculatePayroll(input());$("calc_error").style.display="none";
["company","company_address","employee","employee_no","period","pay_date","start_date"].forEach(id=>{
const target={company:"p_company",company_address:"p_company_address",employee:"p_employee",employee_no:"p_employee_no",period:"p_period",pay_date:"p_pay_date",start_date:"p_start_date"}[id];put(target,$(id).value.trim());});
put("p_company_short",$("company").value.trim());
const vals={p_monthly_gross:r.monthlyGross,p_night:r.shifts.amount.night,p_sunday:r.shifts.amount.sunday,p_holiday:r.shifts.amount.holiday,
p_special_holiday:r.shifts.amount.specialHoliday,p_gross:r.gross,p_taxfree_sfn:r.shifts.taxFree,p_taxable_sfn:r.shifts.taxable,
p_health:r.employee.health,p_care:r.employee.care,p_pension:r.employee.pension,p_unemployment:r.employee.unemployment,p_employee_social:r.employee.socialTotal,
p_wage_tax:r.employee.wageTax,p_solidarity_tax:r.employee.solidarityTax,p_church_tax:r.employee.churchTax,p_advance:r.employee.advance,
p_employer_health:r.employer.health,p_employer_care:r.employer.care,p_employer_pension:r.employer.pension,p_employer_unemployment:r.employer.unemployment,p_employer_social:r.employer.socialTotal};
Object.entries(vals).forEach(([id,v])=>put(id,euro(v)));
const hrs={p_hours_worked:r.shifts.hours.worked,p_hours_night:r.shifts.hours.night,p_hours_sunday:r.shifts.hours.sunday,p_hours_holiday:r.shifts.hours.holiday,p_hours_special:r.shifts.hours.specialHoliday};
Object.entries(hrs).forEach(([id,v])=>put(id,euro(v)));
put("p_krankenkasse",$("krankenkasse").value.trim());put("p_additional_rate",euro(r.rates.healthTotal-14.6)+"%");
put("p_sv_base",euro(r.socialInsuranceBase)+" €");put("p_health_base",euro(r.healthBase)+" €");put("p_pension_base",euro(r.pensionBase)+" €");put("p_net",euro(r.net)+" €");
}catch(e){$("calc_error").style.display="block";$("calc_error").textContent=e.message||"اطلاعات معتبر نیست.";}
}
document.querySelectorAll("input,select").forEach(el=>{if(el.id!=="logo_file")el.addEventListener("input",update);});
$("shifts").addEventListener("input",update);$("shifts").addEventListener("click",e=>{if(e.target.classList.contains("remove")){e.target.closest(".shift").remove();update();}});
$("add_shift").addEventListener("click",()=>{addShift();update();});
$("pdf_button").addEventListener("click",()=>{update();if($("calc_error").style.display==="none")window.print();});
$("reset_button").addEventListener("click",()=>window.location.reload());
$("logo_file").addEventListener("change",e=>{const file=e.target.files&&e.target.files[0],area=$("logo_area");if(!file){area.innerHTML="LOGO<br>Unternehmen";return;}
if(!["image/png","image/jpeg","image/webp"].includes(file.type)||file.size>2097152){e.target.value="";area.textContent="فقط PNG، JPG یا WebP تا ۲ مگابایت";return;}
const reader=new FileReader();reader.onload=()=>{area.innerHTML="";const img=document.createElement("img");img.alt="Company logo";img.src=reader.result;area.appendChild(img);};reader.readAsDataURL(file);});
addShift();update();
})();
</script></body></html>"""

PAYROLL_PAGE = _PAGE.replace("/*ENGINE_JS*/", _ENGINE_JS)

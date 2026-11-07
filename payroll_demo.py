"""Browser-only payroll statement preview for the SteuerPilot staging demo."""

PAYROLL_PAGE = r"""<!doctype html>
<html lang="de" dir="ltr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Entgeltabrechnung</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jspdf/2.5.1/jspdf.umd.min.js"></script>
<style>
:root{font-family:system-ui,sans-serif;color:#172033;background:#f3f5f8;line-height:1.55}
*{box-sizing:border-box}
body{max-width:1180px;margin:24px auto;padding:0 16px}
header,.panel{background:#fff;border:1px solid #dce2ea;border-radius:14px;padding:18px;margin:14px 0}
h1,h2,h3{margin-top:0}
header h1{margin-bottom:4px}
.output-actions{display:grid;grid-template-columns:1fr;gap:9px;margin-top:12px}
.output-actions button{width:100%;text-align:center}
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
select,textarea{width:100%;min-width:0;padding:10px;border:1px solid #bbc5d2;border-radius:8px;font:inherit;background:#fff}
.entry-table{min-width:860px;font-size:11px}.entry-table input,.entry-table select{min-width:68px;padding:6px;font-size:11px}.entry-table input[type=checkbox]{width:auto;min-width:0}.form-table-wrap{overflow-x:auto;margin-top:8px}.entry-table th,.entry-table td{vertical-align:middle}.entry-table .remove-cell{min-width:74px}.visibility-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.visibility-option{display:flex;align-items:flex-start;gap:8px;padding:9px;border:1px solid #dce2ea;border-radius:8px;font-size:13px}.visibility-option input{width:auto;min-width:0;margin:3px 0 0}.visibility-grid .locked{color:#526174;background:#f5f7fa}.summary-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}.summary-grid div{padding:7px;background:#f5f7fa;border-radius:4px}.summary-grid small{display:block;color:#596779}.preview-meta{font-size:10px}.preview-meta td:first-child{font-weight:600;width:28%}.preview-meta td:nth-child(3){font-weight:600;width:28%}
@media print{.form-table-wrap{overflow:visible}.preview{font-size:8pt!important}}
input[type=file]{padding:7px}
.actions{display:flex;gap:10px;flex-wrap:wrap}
button,.button{display:inline-block;border:0;border-radius:9px;padding:11px 16px;font:inherit;text-decoration:none;cursor:pointer}
.primary{background:#203b63;color:white}
.secondary{background:#e8eef6;color:#203b63}
.note{background:#fff8e8;border-right:4px solid #c58a00;padding:12px;border-radius:8px;font-size:13px}
.preview{background:#fff;border:1px solid #cfd7e2;border-radius:4px;padding:15px;box-shadow:0 4px 18px #10243a0b;direction:ltr;text-align:left;font-family:Arial,Helvetica,sans-serif;color:#111;font-size:11px}
.preview-top{display:flex;gap:12px;align-items:flex-start;justify-content:space-between;border-bottom:2px solid #333;padding-bottom:8px}
.logo-area{width:118px;height:58px;border:1px dashed #91a0b3;border-radius:8px;display:flex;align-items:center;justify-content:center;overflow:hidden;color:#66758a;font-size:12px;text-align:center;padding:6px;flex-shrink:0}
.logo-area img{max-width:100%;max-height:100%;object-fit:contain}
.company-block{flex:1;text-align:right;direction:ltr}
.company-block strong{font-size:17px}
.pay-title{margin:10px 0 7px;font-size:18px}
.meta{display:grid;grid-template-columns:1fr 1fr;gap:6px;margin-bottom:7px}
.meta div,.party{background:#f5f7fa;border-radius:2px;padding:6px}
.meta small,.party small{display:block;color:#596779;font-size:11px}
.parties{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-bottom:7px}
.party b{display:block;min-height:22px}
table{width:100%;border-collapse:collapse;font-size:10px;margin:4px 0 7px}
th,td{padding:4px 5px;border-bottom:1px solid #e2e7ed;text-align:left}
th{background:#f1f4f8;font-weight:700}
.amount{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
.section-title{margin:7px 0 3px;font-size:11px;text-transform:uppercase;border-bottom:1px solid #888;padding-bottom:2px}
.total-row{font-weight:700;background:#f4f7fb}
.net-box{border:2px solid #222;border-radius:2px;padding:9px;margin-top:8px;display:flex;justify-content:space-between;align-items:center;font-size:15px;font-weight:750}
.preview-foot{margin-top:8px;padding-top:5px;border-top:1px solid #dce2ea;color:#596779;font-size:10px}
a.back{color:#203b63;text-decoration:none;font-weight:650}

/* SteuerPilot Pro payslip refresh: clean navy/blue payroll document */
.preview{background:#fff;border:1px solid #d7e0ec;border-radius:12px;padding:24px;box-shadow:0 14px 38px rgba(24,49,82,.10);direction:ltr;text-align:left;font-family:Arial,Helvetica,sans-serif;color:#1b2b42;font-size:11px}
.preview-top{display:flex;gap:16px;align-items:center;justify-content:space-between;border-bottom:3px solid #1d426f;padding:0 0 16px;margin-bottom:14px}
.logo-area{width:116px;height:62px;border:1px solid #d9e3ef;border-radius:9px;background:#f5f8fc;display:flex;align-items:center;justify-content:center;overflow:hidden;color:#64758c;font-size:11px;text-align:center;padding:6px;flex-shrink:0}
.company-block{flex:1;text-align:right;direction:ltr;color:#53647b;font-size:10px;line-height:1.5}
.company-block strong{font-size:18px;letter-spacing:.1px;color:#173b67}
.pay-title{margin:13px 0 10px;font-size:19px;line-height:1.25;color:#173b67;font-weight:750}
.meta{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-bottom:10px}
.meta div,.party{background:#f3f7fc;border:1px solid #e0e8f2;border-radius:8px;padding:10px}
.meta small,.party small{display:block;color:#6a7b91;font-size:9px;margin-bottom:3px}
.meta b,.party b{color:#1d3555}
.parties{display:grid;grid-template-columns:1fr 1fr;gap:9px;margin-bottom:13px}
.party b{display:block;min-height:22px;font-size:12px}
.party span{display:block;margin-top:4px;color:#34465e;font-size:10px}
table{width:100%;border-collapse:collapse;font-size:10px;margin:5px 0 9px}
th,td{padding:6px 8px;border-bottom:1px solid #e7edf4;text-align:left}
th{background:#eaf1f9;color:#24466f;font-weight:700}
tbody tr:nth-child(even):not(.total-row){background:#fbfcfe}
.amount{text-align:right;white-space:nowrap;font-variant-numeric:tabular-nums}
.section-title{margin:14px 0 5px;font-size:10px;letter-spacing:.55px;text-transform:uppercase;color:#1d4778;border-bottom:1px solid #d5e0ed;border-left:3px solid #2f6da8;padding:4px 0 5px 8px}
.preview-meta td:first-child,.preview-meta td:nth-child(3){color:#61738a;font-weight:650}
.preview-meta td:nth-child(2),.preview-meta td:nth-child(4){color:#263c59}
.total-row{font-weight:750;background:#edf3fa;color:#183b66}
.summary-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;margin-top:10px}
.summary-grid div{padding:9px;background:#f3f7fc;border:1px solid #e1e9f3;border-radius:7px}
.summary-grid small{display:block;color:#687b92;margin-bottom:3px}
.net-box{background:#173b67;color:#fff;border:0;border-radius:9px;padding:14px 16px;margin-top:13px;display:flex;justify-content:space-between;align-items:center;font-size:13px;font-weight:750;box-shadow:0 5px 12px rgba(23,59,103,.14)}
.net-box strong{font-size:21px;letter-spacing:.2px}
.preview-foot{margin-top:12px;padding:9px 10px;border:1px solid #e0e8f2;border-radius:7px;background:#f8fafc;color:#617188;font-size:9px;line-height:1.45}
@media print{.preview{border:0;border-radius:0;box-shadow:none;padding:0}.net-box{print-color-adjust:exact;-webkit-print-color-adjust:exact}}

/* Clean administrative payslip: white paper, neutral typography, no decorative color */
.preview{background:#fff!important;color:#111!important;border:1px solid #999!important;border-radius:0!important;box-shadow:none!important;padding:18px!important}
.preview-top{border-bottom:1px solid #222!important}
.logo-area{background:#fff!important;border:1px solid #aaa!important;border-radius:0!important;color:#555!important}
.company-block,.company-block strong,.pay-title,.meta small,.party small,.meta b,.party b,.party span,.section-title,.preview-meta td:first-child,.preview-meta td:nth-child(3),.preview-meta td:nth-child(2),.preview-meta td:nth-child(4){color:#111!important}
.meta div,.party,.summary-grid div{background:#fff!important;border:1px solid #bbb!important;border-radius:0!important}
.preview th{background:#fff!important;color:#111!important;border-bottom:1px solid #222!important}
.preview td,.preview th{border-bottom:1px solid #bbb!important}
.preview .total-row{background:#fff!important;color:#111!important;font-weight:700!important}
.preview .section-title{border-left:0!important;border-bottom:1px solid #555!important;padding-left:0!important;letter-spacing:0!important}
.preview .net-box{background:#fff!important;color:#111!important;border:1.5px solid #111!important;border-radius:0!important;box-shadow:none!important}
.preview .net-box strong{color:#111!important}
.preview .preview-foot{background:#fff!important;border:0!important;border-top:1px solid #aaa!important;border-radius:0!important;color:#333!important}
@media print{.preview{background:#fff!important;color:#111!important}.preview *{print-color-adjust:economy!important;-webkit-print-color-adjust:economy!important}}

@media(max-width:850px){.layout{grid-template-columns:1fr}.preview{padding:15px}}
@media(max-width:520px){.fields,.meta,.parties{grid-template-columns:1fr}.preview-top{gap:8px}.logo-area{width:105px;height:68px}.preview{padding:11px}table{font-size:11px}}
@page{size:A4;margin:9mm}
@media print{
  html,body{background:white!important;margin:0!important;padding:0!important;max-width:none!important}
  header,.editor,.actions,.note,.screen-only{display:none!important}
  .layout{display:block!important}
  .preview{display:block!important;border:0!important;border-radius:0!important;box-shadow:none!important;padding:0!important;width:100%!important;font-size:9pt!important}
  .preview table{page-break-inside:avoid;font-size:8pt!important;margin:3px 0 5px!important}\n  .preview th,.preview td{padding:3px 4px!important}\n  .preview .section-title{margin:5px 0 2px!important;font-size:9pt!important}
  .preview-top,.parties,.net-box{page-break-inside:avoid}
  .preview-foot{position:static}
}
</style>
</head>
<body>
<header>
  <h1>Lohnabrechnung erstellen</h1>
  <p class="muted">Geben Sie die Angaben ein, prüfen Sie die Vorschau und laden Sie die Abrechnung als PDF herunter oder drucken Sie sie aus.</p>
  <p><a class="back" href="/">← Zurück zu SteuerPilot Pro</a></p>
</header>

<div class="layout">
  <main class="editor">
    <section class="panel">
      <div class="note">Dieses Formular wird ausschließlich im Browser ausgeführt. Angaben und Logo werden nicht an den Server übertragen. Verwenden Sie ausschließlich synthetische Testdaten. Keine echten Steuer- oder Sozialversicherungsnummern und keine IBAN eingeben. Die Angaben werden nicht gespeichert. Die Sozialversicherungsberechnung gilt für einen Standardfall 2026 und ersetzt keine zertifizierte Lohnabrechnung.</div>
    </section>

    <section class="panel group">
      <h3>Abrechnungsumfang</h3>
      <p class="muted">Wählen Sie aus, welche Zusatzbereiche auf der Entgeltabrechnung erscheinen. Die Berechnung und die erfassten Werte bleiben davon unberührt. Kernbereiche mit Bruttoentgelt und Arbeitnehmerabzügen bleiben sichtbar.</p>
      <div id="section_visibility_controls" class="visibility-grid"></div>
    </section>

    <section class="panel group">
      <h3>Angaben zum Arbeitgeber</h3>
      <div class="fields">
        <div class="field full"><label for="company">Firmenname / Arbeitgeber</label><input id="company" data-bind="company" placeholder="Muster GmbH"></div>
        <div class="field full"><label for="company_address">Anschrift des Arbeitgebers</label><input id="company_address" data-bind="company_address" placeholder="Musterstraße 1, 00000 Musterstadt"></div>
        <div class="field full"><label for="logo_file">Firmenlogo</label><input id="logo_file" type="file" accept="image/png,image/jpeg,image/webp"></div>
      </div>
    </section>

    <section class="panel group">
      <h3>Angaben zum Arbeitnehmer und Abrechnungszeitraum</h3>
      <div class="fields">
        <div class="field"><label for="employee">Name des Arbeitnehmers</label><input id="employee" data-bind="employee" placeholder="Max Mustermann"></div>
        <div class="field"><label for="employee_no">Personalnummer</label><input id="employee_no" data-bind="employee_no" placeholder="TEST-001"></div>
        <div class="field"><label for="employee_address">Anschrift des Arbeitnehmers</label><input id="employee_address" placeholder="Beispielstraße 1, 00000 Musterstadt"></div>
        <div class="field"><label for="birth_date">Geburtsdatum</label><input id="birth_date" type="date"></div>
        <div class="field"><label for="start_date">Eintrittsdatum</label><input id="start_date" type="date" data-bind="start_date"></div>
        <div class="field"><label for="period">Abrechnungsmonat</label><input id="period" type="month" value="2026-11" data-bind="period"></div>
        <div class="field"><label for="pay_date">Auszahlungsdatum</label><input id="pay_date" type="date" data-bind="pay_date"></div>
        <div class="field"><label for="steuer_id_test">Steuer-ID (nur synthetischer Testwert)</label><input id="steuer_id_test" autocomplete="off" placeholder="Nur Testwert eingeben"></div>
        <div class="field"><label for="sv_number_test">SV-Nummer (nur synthetischer Testwert)</label><input id="sv_number_test" autocomplete="off" placeholder="Nur Testwert eingeben"></div>
      </div>
    </section>

    <section class="panel group">
      <h3>Steuermerkmale</h3>
      <div class="fields">
        <div class="field"><label for="tax_class">Steuerklasse</label><select id="tax_class"><option value="">Bitte auswählen</option><option>I</option><option>II</option><option>III</option><option>IV</option><option>IV mit Faktor</option><option>V</option><option>VI</option></select></div>
        <div class="field"><label for="tax_factor">Faktor (Steuerklasse IV)</label><input id="tax_factor" type="number" min="0" step="0.001" placeholder="z. B. 0,984"></div>
        <div class="field"><label for="child_allowance">Kinderfreibetrag</label><input id="child_allowance" type="number" min="0" max="10" step="0.5" placeholder="z. B. 0,5"></div>
        <div class="field"><label for="religion">Konfession</label><select id="religion"><option value="">Bitte auswählen</option><option value="Keine">Keine</option><option value="ev">Evangelisch (ev)</option><option value="rk">Römisch-katholisch (rk)</option><option value="Andere">Andere</option></select></div>
        <div class="field"><label for="church_tax_state">Bundesland des steuerlichen Wohnsitzes (Kirchensteuer)</label><select id="church_tax_state"><option value="">Bitte auswählen</option><option value="BW">Baden-Württemberg</option><option value="BY">Bayern</option><option value="BE">Berlin</option><option value="BB">Brandenburg</option><option value="HB">Bremen</option><option value="HH">Hamburg</option><option value="HE">Hessen</option><option value="MV">Mecklenburg-Vorpommern</option><option value="NI">Niedersachsen</option><option value="NW">Nordrhein-Westfalen</option><option value="RP">Rheinland-Pfalz</option><option value="SL">Saarland</option><option value="SN">Sachsen</option><option value="ST">Sachsen-Anhalt</option><option value="SH">Schleswig-Holstein</option><option value="TH">Thüringen</option></select></div>
        <div class="field"><label for="annual_allowance">Freibetrag jährlich (EUR)</label><input id="annual_allowance" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="monthly_allowance">Freibetrag monatlich (EUR)</label><input id="monthly_allowance" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="dba_country">DBA-Staat (falls zutreffend)</label><input id="dba_country" placeholder="Optional"></div>
        <div class="field"><label><input id="midijob" type="checkbox" style="width:auto"> Beschäftigung im Übergangsbereich (Midijob)</label></div>
      </div>
      <p class="muted">Steuerklasse, Faktor, Kinderfreibetrag, Konfession und Freibeträge werden in dieser Demo angezeigt, aber nicht zur automatischen Lohnsteuerberechnung verwendet.</p>
    </section>

    <section class="panel group">
      <h3>Entgelt und Sozialversicherung</h3>
      <div class="fields">
        <div class="field"><label for="base_pay">Monatliches Grundgehalt brutto (EUR)</label><input id="base_pay" type="number" min="0" step="0.01" value="3000"></div>
        <div class="field"><label for="monthly_hours">Vertragliche Monatsarbeitszeit (Stunden)</label><input id="monthly_hours" type="number" min="1" step="0.5" value="173.33"></div>
        <div class="field"><label for="bonus">Bonus / Einmalzahlung brutto (EUR)</label><input id="bonus" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="allowance">Sonstige Bruttobezüge (EUR)</label><input id="allowance" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="kasse">Krankenkasse</label><input id="kasse" placeholder="Name der Krankenkasse"></div>
        <div class="field"><label for="kv_extra">Zusatzbeitrag der Krankenkasse (%)</label><input id="kv_extra" type="number" min="0" max="10" step="0.01" value="2.9"></div>
        <div class="field"><label for="state">Bundesland des Arbeitsortes</label><select id="state"><option value="">Bundesland auswählen</option><option value="BW">Baden-Württemberg</option><option value="BY">Bayern</option><option value="BE">Berlin</option><option value="BB">Brandenburg</option><option value="HB">Bremen</option><option value="HH">Hamburg</option><option value="HE">Hessen</option><option value="MV">Mecklenburg-Vorpommern</option><option value="NI">Niedersachsen</option><option value="NW">Nordrhein-Westfalen</option><option value="RP">Rheinland-Pfalz</option><option value="SL">Saarland</option><option value="SN">Sachsen</option><option value="ST">Sachsen-Anhalt</option><option value="SH">Schleswig-Holstein</option><option value="TH">Thüringen</option></select></div>
        <div class="field"><label for="children">Anzahl der Kinder unter 25 Jahren</label><select id="children"><option value="0">0</option><option value="1">1</option><option value="2">2</option><option value="3">3</option><option value="4">4</option><option value="5">5 oder mehr</option></select></div>
        <div class="field"><label><input id="under23" type="checkbox" style="width:auto"> Arbeitnehmer ist noch keine 23 Jahre alt</label></div>
        <div class="field"><label for="health_rate">Allgemeiner Beitragssatz der Krankenversicherung (%)</label><input id="health_rate" type="number" min="0" max="30" step="0.01" value="14.6"></div>
        <div class="field"><label for="pgrs">Personengruppenschlüssel (PGRS)</label><input id="pgrs" inputmode="numeric" placeholder="z. B. 101"></div>
        <div class="field"><label for="bgrs">Beitragsgruppenschlüssel (BGRS)</label><input id="bgrs" inputmode="numeric" placeholder="z. B. 1111"></div>
        <div class="field"><label for="sv_days">SV-Tage im Abrechnungsmonat</label><input id="sv_days" type="number" min="0" max="31" step="1" placeholder="Kalendertage"></div>
        <div class="field"><label for="uv_code_test">UV-/Gefahrtarif-Kennzeichen (Testwert)</label><input id="uv_code_test" placeholder="Optionaler Testwert"></div>
        <div class="field"><label for="uv_days">UV-Tage im Abrechnungsmonat</label><input id="uv_days" type="number" min="0" max="31" step="1"></div>
        <div class="field"><label for="kv_type">Krankenversicherungsart</label><select id="kv_type"><option value="Gesetzlich">Gesetzlich</option><option value="Privat (nur Anzeige)">Privat (nur Anzeige)</option></select></div>
      </div>
      <p class="muted">Annahmen: regulär beschäftigter Arbeitnehmer in der gesetzlichen Krankenversicherung, voller Abrechnungsmonat und ein Arbeitgeber. Tragen Sie den Zusatzbeitrag der gewählten Krankenkasse ein. Minijobs, private Krankenversicherung, mehrere Arbeitgeber, Kurzarbeit sowie Ein- oder Austritte während des Monats sind nicht abgedeckt.</p>
    </section>

    <section class="panel group">
      <h3>Arbeitszeiten und Zuschläge</h3>
      <p class="muted">Geben Sie für jede Schicht Datum, Beginn, Ende und Pausenzeitraum ein. Schichten über Mitternacht werden unterstützt. Gesetzliche Feiertage werden anhand des ausgewählten Bundeslands für 2026 erkannt. Zusätzliche lokale Feiertage können ergänzt werden.</p>
      <div class="fields">
        <div class="field"><label for="night_rate">Nachtzuschlag laut Vertrag (%)</label><input id="night_rate" type="number" min="0" max="300" step="0.5" value="0"></div>
        <div class="field"><label for="sunday_rate">Sonntagszuschlag laut Vertrag (%)</label><input id="sunday_rate" type="number" min="0" max="300" step="0.5" value="0"></div>
        <div class="field"><label for="holiday_rate">Feiertagszuschlag laut Vertrag (%)</label><input id="holiday_rate" type="number" min="0" max="300" step="0.5" value="0"></div>
        <div class="field full"><label for="holidays">Zusätzliche lokale Feiertage (optional)</label><textarea id="holidays" rows="3" style="width:100%;padding:10px;border:1px solid #bbc5d2;border-radius:8px;font:inherit" placeholder="2026-08-08"></textarea></div>
      </div>
      <div style="overflow-x:auto;margin-top:12px">
        <table id="shift_table"><thead><tr><th>Datum</th><th>Beginn</th><th>Ende</th><th>Pause von</th><th>Pause bis</th><th></th></tr></thead><tbody id="shift_rows"></tbody></table>
      </div>
      <div class="actions"><button class="secondary" id="add_shift" type="button">Schicht hinzufügen</button></div>
      <p id="shift_summary" class="muted">Nacht-, Sonntags- und Feiertagsstunden werden nach Eingabe der Schichten berechnet.</p>
    </section>

    <section class="panel group">
      <h3>Arbeitszeit und Fehlzeiten</h3>
      <div class="fields">
        <div class="field"><label for="scheduled_hours">Soll-Arbeitsstunden</label><input id="scheduled_hours" type="number" min="0" step="0.25"></div>
        <div class="field"><label for="actual_hours">Ist-Arbeitsstunden</label><input id="actual_hours" type="number" min="0" step="0.25"></div>
        <div class="field"><label for="attendance_days">Anwesenheitstage</label><input id="attendance_days" type="number" min="0" max="31" step="0.5"></div>
        <div class="field"><label for="vacation_entitlement">Urlaubsanspruch laufendes Jahr (Tage)</label><input id="vacation_entitlement" type="number" min="0" step="0.5"></div>
        <div class="field"><label for="vacation_carryover">Resturlaub aus Vorjahr (Tage)</label><input id="vacation_carryover" type="number" min="0" step="0.5"></div>
        <div class="field"><label for="vacation_taken">Genommene Urlaubstage</label><input id="vacation_taken" type="number" min="0" step="0.5"></div>
        <div class="field"><label for="sick_days">Krankheitstage</label><input id="sick_days" type="number" min="0" max="31" step="0.5"></div>
        <div class="field"><label for="absence_days">Sonstige Fehltage</label><input id="absence_days" type="number" min="0" max="31" step="0.5"></div>
        <div class="field"><label for="holiday_days">Feiertage im Abrechnungsmonat</label><input id="holiday_days" type="number" min="0" max="31" step="0.5"></div>
      </div>
      <p class="muted">Der Resturlaub wird als Urlaubsanspruch plus Übertrag aus dem Vorjahr abzüglich genommener Urlaubstage angezeigt.</p>
    </section>

    <section class="panel group">
      <h3>Brutto-Bezüge und Lohnarten</h3>
      <p class="muted">Zusätzliche Lohnarten können mit Menge, Faktor und Prozentsatz erfasst werden. Die Steuer- und SV-Kennzeichen dienen hier der Anzeige und der vereinfachten Basis-Summenbildung, nicht einer zertifizierten Lohnartenprüfung.</p>
      <div class="form-table-wrap">
        <table class="entry-table"><thead><tr><th>Lohnart</th><th>Bezeichnung</th><th>Einheit</th><th>Menge</th><th>Faktor (EUR)</th><th>Prozentsatz</th><th>Steuer</th><th>SV</th><th>GB</th><th>Betrag (EUR)</th><th></th></tr></thead><tbody id="earnings_rows"></tbody></table>
      </div>
      <div class="actions"><button class="secondary" id="add_earning" type="button">Brutto-Lohnart hinzufügen</button></div>
    </section>

    <section class="panel group">
      <h3>Netto-Bezüge</h3>
      <div class="fields">
        <div class="field"><label for="kug_payout">Kug-Auszahlung / Netto-Zuschuss (EUR)</label><input id="kug_payout" type="number" min="0" step="0.01" value="0"></div>
      </div>
      <div class="form-table-wrap">
        <table class="entry-table"><thead><tr><th>Lohnart</th><th>Bezeichnung</th><th>Einheit</th><th>Menge</th><th>Faktor (EUR)</th><th>Prozentsatz</th><th>Betrag (EUR)</th><th></th></tr></thead><tbody id="net_benefit_rows"></tbody></table>
      </div>
      <div class="actions"><button class="secondary" id="add_net_benefit" type="button">Netto-Bezug hinzufügen</button></div>
    </section>

    <section class="panel group">
      <h3>Netto-Abzüge und Auszahlungsweg</h3>
      <div class="fields">
        <div class="field"><label for="vwl_deduction">VWL / vermögenswirksame Leistungen (EUR)</label><input id="vwl_deduction" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="garnishment">Pfändung (EUR)</label><input id="garnishment" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="loan_repayment">Darlehensrückzahlung (EUR)</label><input id="loan_repayment" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="rest_garnishment">Restpfändung (nur Anzeige, EUR)</label><input id="rest_garnishment" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="rest_loan">Darlehen Rest (nur Anzeige, EUR)</label><input id="rest_loan" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="payment_method">Auszahlungsweg</label><select id="payment_method"><option>Überweisung</option><option>Barzahlung</option><option>Sonstiger Zahlungsweg</option></select></div>
        <div class="field"><label for="bank_name_test">Bankbezeichnung (nur Testwert)</label><input id="bank_name_test" placeholder="Keine Kontonummer oder IBAN eingeben"></div>
      </div>
      <div class="form-table-wrap">
        <table class="entry-table"><thead><tr><th>Lohnart</th><th>Bezeichnung</th><th>Einheit</th><th>Menge</th><th>Faktor (EUR)</th><th>Prozentsatz</th><th>Betrag (EUR)</th><th></th></tr></thead><tbody id="net_deduction_rows"></tbody></table>
      </div>
      <div class="actions"><button class="secondary" id="add_net_deduction" type="button">Netto-Abzug hinzufügen</button></div>
    </section>

    <section class="panel group">
      <h3>Steuern und sonstige manuelle Abzüge</h3>
      <p class="muted">Die laufende Lohnsteuer und der Solidaritätszuschlag werden mit dem BMF-Programmablaufplan 2026 direkt in diesem Browser berechnet. Nicht unterstützte Sonderfälle werden blockiert, statt mit Schätzwerten abgerechnet.</p>
      <div class="note" id="tax_engine_status" role="status">BMF-Steuerrechner wird geladen ...</div>
      <div class="fields">
        <div class="field"><label for="tax">Lohnsteuer (€)</label><input id="tax" type="number" min="0" step="0.01" value="0" readonly></div>
        <div class="field"><label for="soli">Solidaritätszuschlag (€)</label><input id="soli" type="number" min="0" step="0.01" value="0" readonly></div>
        <div class="field"><label for="church">Kirchensteuer (€)</label><input id="church" type="number" min="0" step="0.01" value="0" readonly></div>
        <div class="field"><label for="other">Sonstige Abzüge (EUR)</label><input id="other" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="advance">Vorschuss / Abschlag (EUR)</label><input id="advance" type="number" min="0" step="0.01" value="0"></div>
      </div>
    </section>

    <section class="panel group">
      <h3>Verdienstbescheinigung (Jahreswerte bis einschließlich Abrechnungsmonat)</h3>
      <p class="muted">Die kumulierten Jahreswerte werden manuell als Testwerte erfasst und unverändert in der Verdienstbescheinigung ausgegeben.</p>
      <div class="fields">
        <div class="field"><label for="ytd_gross">Gesamt-Brutto (Jahr, EUR)</label><input id="ytd_gross" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="ytd_tax_gross">Steuer-Brutto (Jahr, EUR)</label><input id="ytd_tax_gross" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="ytd_kv_gross">KV-Brutto (Jahr, EUR)</label><input id="ytd_kv_gross" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="ytd_rv_gross">RV-Brutto (Jahr, EUR)</label><input id="ytd_rv_gross" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="ytd_av_gross">AV-Brutto (Jahr, EUR)</label><input id="ytd_av_gross" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="ytd_pv_gross">PV-Brutto (Jahr, EUR)</label><input id="ytd_pv_gross" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="ytd_tax">Lohnsteuer (Jahr, EUR)</label><input id="ytd_tax" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="ytd_church">Kirchensteuer (Jahr, EUR)</label><input id="ytd_church" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="ytd_soli">Solidaritätszuschlag (Jahr, EUR)</label><input id="ytd_soli" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="ytd_kv">KV-Beitrag (Jahr, EUR)</label><input id="ytd_kv" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="ytd_rv">RV-Beitrag (Jahr, EUR)</label><input id="ytd_rv" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="ytd_av">AV-Beitrag (Jahr, EUR)</label><input id="ytd_av" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="ytd_pv">PV-Beitrag (Jahr, EUR)</label><input id="ytd_pv" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="ytd_vwl">VWL gesamt (Jahr, EUR)</label><input id="ytd_vwl" type="number" min="0" step="0.01" value="0"></div>
      </div>
    </section>

    <section class="panel group">
      <h3>Zusätzliche Arbeitgeberkosten</h3>
      <div class="fields">
        <div class="field"><label for="u1_cost">Umlage U1 (EUR)</label><input id="u1_cost" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="u2_cost">Umlage U2 (EUR)</label><input id="u2_cost" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="insolvency_cost">Insolvenzgeldumlage (EUR)</label><input id="insolvency_cost" type="number" min="0" step="0.01" value="0"></div>
        <div class="field"><label for="accident_cost">Unfallversicherung / BG (EUR)</label><input id="accident_cost" type="number" min="0" step="0.01" value="0"></div>
      </div>
    </section>

    <div class="actions screen-only">    <div class="actions screen-only">
      <div class="output-actions"><button class="primary" id="pdf_button" type="button">PDF herunterladen · PDF herunterladen</button><button class="secondary" id="print_button" type="button">Drucken · Drucken</button><button class="secondary" id="reset_button" type="button">Formular zurücksetzen</button></div>
    </div>
  </main>

  <section class="preview" id="payroll_preview" aria-live="polite">
    <div class="preview-top">
      <div class="logo-area" id="logo_area">LOGO<br>Unternehmen</div>
      <div class="company-block">
        <strong id="p_company">Firmenname</strong>
        <div id="p_company_address">Unternehmensanschrift</div>
      </div>
    </div>
    <h2 class="pay-title">Abrechnung der Brutto/Netto-Bezüge</h2>
    <div class="meta">
      <div><small>Abrechnungszeitraum</small><b id="p_period">-</b></div>
      <div><small>Auszahlungsdatum</small><b id="p_pay_date">-</b></div>
    </div>
    <div class="parties">
      <div class="party"><small>Arbeitnehmer</small><b id="p_employee">-</b><span><small>Personalnummer</small><span id="p_employee_no">-</span></span><span><small>Anschrift</small><span id="p_employee_address">-</span></span></div>
      <div class="party"><small>Arbeitgeber</small><b id="p_company_short">-</b><span><small>Eintrittsdatum</small><span id="p_start_date">-</span></span></div>
    </div>
    <h3 class="section-title">Steuermerkmale</h3>
    <table class="preview-meta"><tbody>
      <tr><td>Geburtsdatum</td><td id="p_birth_date">-</td><td>Steuerklasse / Faktor</td><td id="p_tax_class">-</td></tr>
      <tr><td>Kinderfreibetrag</td><td id="p_child_allowance">-</td><td>Konfession</td><td id="p_religion">-</td></tr>
      <tr><td>Freibetrag jährlich</td><td id="p_annual_allowance">0,00 EUR</td><td>Freibetrag monatlich</td><td id="p_monthly_allowance">0,00 EUR</td></tr>
      <tr><td>DBA-Staat</td><td id="p_dba_country">-</td><td>Midijob</td><td id="p_midijob">Nein</td></tr>
      <tr><td>Steuer-ID</td><td id="p_steuer_id_test">-</td><td>SV-Nummer</td><td id="p_sv_number_test">-</td></tr>
    </tbody></table>
    <h3 class="section-title">Sozialversicherung</h3>
    <table class="preview-meta"><tbody>
      <tr><td>Krankenkasse</td><td id="p_kasse">-</td><td>KV-Zusatzbeitrag</td><td id="p_kv_extra">-</td></tr>
      <tr><td>KV-Grundbeitrag</td><td id="p_health_rate">-</td><td>Versicherungsart</td><td id="p_kv_type">-</td></tr>
      <tr><td>PGRS</td><td id="p_pgrs">-</td><td>BGRS</td><td id="p_bgrs">-</td></tr>
      <tr><td>SV-Tage</td><td id="p_sv_days">-</td><td>UV-Tage</td><td id="p_uv_days">-</td></tr>
      <tr><td>Bundesland</td><td id="p_state">-</td><td>UV-Kennzeichen</td><td id="p_uv_code_test">-</td></tr>
      <tr><td>UV-Kennzeichen</td><td id="p_uv_code_test">-</td><td>Kinder unter 25</td><td id="p_children">-</td></tr>
      <tr><td>Unter 23 Jahre</td><td id="p_under23">-</td><td>Beitragsart</td><td id="p_kv_type">-</td></tr>
    </tbody></table>
    <h3 class="section-title">Arbeitszeit und Fehlzeiten</h3>
    <table class="preview-meta"><tbody>
      <tr><td>Soll-/Iststunden</td><td id="p_hours">-</td><td>Anwesenheitstage</td><td id="p_attendance_days">-</td></tr>
      <tr><td>Urlaubsanspruch</td><td id="p_vacation_entitlement">-</td><td>Übertrag Vorjahr</td><td id="p_vacation_carryover">-</td></tr>
      <tr><td>Genommene Urlaubstage</td><td id="p_vacation_taken">-</td><td>Resturlaub</td><td id="p_vacation_balance">-</td></tr>
      <tr><td>Krankheitstage</td><td id="p_sick_days">-</td><td>Sonstige Fehltage</td><td id="p_absence_days">-</td></tr>
      <tr><td>Feiertage</td><td id="p_holiday_days">-</td><td>Abrechnungsmonat</td><td id="p_period_days">-</td></tr>
    </tbody></table>

    <h3 class="section-title">Bruttoentgelt / Bezüge</h3>
    <table><thead><tr><th>Bezeichnung</th><th class="amount">Betrag (EUR)</th></tr></thead>
      <tbody>
        <tr><td>Grundgehalt</td><td class="amount" id="p_base_pay">0,00</td></tr>
        <tr><td>Nachtzuschläge</td><td class="amount" id="p_night_pay">0,00</td></tr><tr><td>Sonntagszuschläge</td><td class="amount" id="p_sunday_pay">0,00</td></tr><tr><td>Feiertagszuschläge</td><td class="amount" id="p_holiday_pay">0,00</td></tr>
        <tr><td>Bonus / Einmalzahlungen</td><td class="amount" id="p_bonus">0,00</td></tr>
        <tr><td>Zulagen / Sonstige Bezüge</td><td class="amount" id="p_allowance">0,00</td></tr>
        
      </tbody>
    </table>
    <table><tbody id="p_earnings_rows"></tbody></table>
    <table><tbody><tr class="total-row"><td>Gesamtbrutto einschließlich Lohnarten</td><td class="amount" id="p_gross">0,00</td></tr></tbody></table>

    <h3 class="section-title">Steuer- und Sozialversicherungsbasis</h3><table><tbody><tr><td>Steuer-Brutto</td><td class="amount" id="p_tax_gross">0,00</td></tr><tr><td>KV-Brutto</td><td class="amount" id="p_kv_gross">0,00</td></tr><tr><td>RV-/AV-Brutto</td><td class="amount" id="p_rv_gross">0,00</td></tr><tr><td>Steuerfrei geschätzter Zuschlagsanteil</td><td class="amount" id="p_tax_free">0,00</td></tr><tr><td>SV-freier geschätzter Zuschlagsanteil</td><td class="amount" id="p_sv_free">0,00</td></tr><tr><td>SV-pflichtiges Brutto</td><td class="amount" id="p_sv_gross">0,00</td></tr></tbody></table>
    <h3 class="section-title">Netto-Bezüge</h3>
    <table><tbody><tr><td>Kug-Auszahlung / Netto-Zuschuss</td><td class="amount" id="p_kug_payout">0,00</td></tr></tbody><tbody id="p_net_benefit_rows"></tbody></table>
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
        <tr><td>VWL</td><td class="amount" id="p_vwl">0,00</td></tr>
        <tr><td>Pfändung</td><td class="amount" id="p_garnishment">0,00</td></tr>
        <tr><td>Darlehensrückzahlung</td><td class="amount" id="p_loan_repayment">0,00</td></tr>
        
        </tbody>
    </table>
    <table><tbody id="p_net_deduction_rows"></tbody></table>
    <table><tbody><tr class="total-row"><td>Gesamtabzüge</td><td class="amount" id="p_deductions">0,00</td></tr></tbody></table>

    <h3 class="section-title">Verdienstbescheinigung</h3>
    <table class="preview-meta"><tbody>
      <tr><td>Gesamt-Brutto</td><td id="p_ytd_gross">0,00 EUR</td><td>Steuer-Brutto</td><td id="p_ytd_tax_gross">0,00 EUR</td></tr>
      <tr><td>KV-Brutto</td><td id="p_ytd_kv_gross">0,00 EUR</td><td>RV-Brutto</td><td id="p_ytd_rv_gross">0,00 EUR</td></tr>
      <tr><td>AV-Brutto</td><td id="p_ytd_av_gross">0,00 EUR</td><td>PV-Brutto</td><td id="p_ytd_pv_gross">0,00 EUR</td></tr>
      <tr><td>Lohnsteuer</td><td id="p_ytd_tax">0,00 EUR</td><td>Kirchensteuer</td><td id="p_ytd_church">0,00 EUR</td></tr>
      <tr><td>Solidaritätszuschlag</td><td id="p_ytd_soli">0,00 EUR</td><td>VWL gesamt</td><td id="p_ytd_vwl">0,00 EUR</td></tr>
      <tr><td>KV-Beitrag</td><td id="p_ytd_kv">0,00 EUR</td><td>RV-Beitrag</td><td id="p_ytd_rv">0,00 EUR</td></tr>
      <tr><td>AV-Beitrag</td><td id="p_ytd_av">0,00 EUR</td><td>PV-Beitrag</td><td id="p_ytd_pv">0,00 EUR</td></tr>
    </tbody></table>

    <h3 class="section-title">Arbeitgeberanteile und zusätzliche Arbeitgeberkosten</h3>
    <table><thead><tr><th>Bezeichnung</th><th class="amount">Betrag (EUR)</th></tr></thead>
      <tbody>
        <tr><td>Krankenversicherung Arbeitgeber</td><td class="amount" id="p_employer_health">0,00</td></tr>
        <tr><td>Pflegeversicherung Arbeitgeber</td><td class="amount" id="p_employer_care">0,00</td></tr>
        <tr><td>Rentenversicherung Arbeitgeber</td><td class="amount" id="p_employer_pension">0,00</td></tr>
        <tr><td>Arbeitslosenversicherung Arbeitgeber</td><td class="amount" id="p_employer_unemployment">0,00</td></tr>
        <tr><td>Umlage U1</td><td class="amount" id="p_u1_cost">0,00</td></tr>
        <tr><td>Umlage U2</td><td class="amount" id="p_u2_cost">0,00</td></tr>
        <tr><td>Insolvenzgeldumlage</td><td class="amount" id="p_insolvency_cost">0,00</td></tr>
        <tr><td>Unfallversicherung / BG</td><td class="amount" id="p_accident_cost">0,00</td></tr>
        <tr class="total-row"><td>Gesamtkosten Arbeitgeber</td><td class="amount" id="p_employer_total">0,00</td></tr>
      </tbody>
    </table>
    <div class="summary-grid preview-meta"><div><small>Auszahlungsweg</small><b id="p_payment_method">Überweisung</b></div><div><small>Bankbezeichnung (Testwert)</small><b id="p_bank_name_test">-</b></div><div><small>Restpfändung</small><b id="p_rest_garnishment">0,00 EUR</b></div><div><small>Darlehen Rest</small><b id="p_rest_loan">0,00 EUR</b></div></div>
    <div class="net-box"><span>Auszahlungsbetrag</span><strong id="p_net">0,00 €</strong></div>
    <div class="preview-foot">Automatische Beispielrechnung mit 2026-Rechengrößen für den Standardfall. Zuschlagssätze richten sich nach Vertrag oder Tarif. Die ausgewiesenen Steuer-/SV-Freibeträge sind Näherungen nach den eingegebenen Schichtdaten. Die automatische Steuerberechnung nutzt den BMF-PAP 2026. Sonderfälle und nicht abgedeckte Beitragskonstellationen werden vor der Ausgabe gestoppt.</div>
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

  let payrollTaxEngine = null;
  let payrollTaxLoading = true;
  let payrollTaxLoadError = "";
  (async function loadBmfTaxEngine(){
    try{
      const module = await import("/static/steuerpilot_payroll_wasm.js");
      await module.default();
      const response = await fetch("/static/Lohnsteuer2026.xml",{cache:"no-store"});
      if(!response.ok) throw new Error("BMF-PAP konnte nicht geladen werden ("+response.status+").");
      const source = await response.text();
      payrollTaxEngine = new module.PayrollTaxEngine(source);
    }catch(error){
      payrollTaxLoadError = error && error.message ? error.message : String(error);
    }finally{
      payrollTaxLoading = false;
      if(typeof update === "function") update();
    }
  })();

  function calculateBmfTax(ctx){
    if(!payrollTaxEngine){
      return {ready:!payrollTaxLoading,supported:false,tax:0,soli:0,church:0,
        reason:payrollTaxLoading?"BMF-Steuerrechner wird geladen ...":
          "Automatische Steuerberechnung nicht verfügbar: "+(payrollTaxLoadError||"PAP-Engine fehlt.")};
    }
    const reasons=[];
    const period=$("period").value||"";
    if(!/^2026-\d{2}$/.test(period)) reasons.push("Nur Abrechnungsmonate des Jahres 2026 sind in dieser PAP-Version enthalten.");
    if(!$("state").value) reasons.push("Bundesland des Arbeitsortes fehlt.");
    const classValue=$("tax_class").value;
    const classMap={"I":"1","II":"2","III":"3","IV":"4","IV mit Faktor":"4","V":"5","VI":"6"};
    if(!classMap[classValue]) reasons.push("Steuerklasse fehlt oder ist nicht unterstützt.");
    if(classValue==="VI") reasons.push("Steuerklasse VI wird bis zur Prüfung der Mehrarbeitgeber-Sozialversicherung nicht als vollständiger Nettofall ausgegeben.");
    if($("midijob").checked) reasons.push("Midijob/Übergangsbereich ist noch nicht in der vollständigen Sozialversicherungsberechnung aktiviert.");
    if($("kv_type").value!=="Gesetzlich") reasons.push("Private Krankenversicherung ist noch nicht vollständig integriert.");
    if(Math.abs(val("health_rate")-14.6)>0.001) reasons.push("Der geprüfte PAP-Pfad setzt den allgemeinen GKV-Beitragssatz von 14,6 % voraus.");
    if($("dba_country").value.trim()) reasons.push("DBA- und grenzüberschreitende Fälle benötigen eine gesonderte Berechnung.");
    if(!["Keine","ev","rk"].includes($("religion").value)) reasons.push("Diese Religionsangabe benötigt eine gesonderte ELStAM-/Kirchensteuer-Zuordnung.");
    if(["ev","rk"].includes($("religion").value)&&!$("church_tax_state").value) reasons.push("Bundesland des steuerlichen Wohnsitzes für die Kirchensteuer fehlt.");
    if(ctx.bonus!==0||ctx.allowance!==0||ctx.premium!==0||ctx.taxableItems!==0||ctx.earnings.some(item=>item.amount!==0)){
      reasons.push("Einmalzahlungen, Zuschläge und zusätzliche Brutto-Lohnarten sind noch nicht in den passenden PAP-Sonderverfahren abgebildet.");
    }
    if($("pgrs").value.trim()&&$("pgrs").value.trim()!=="101") reasons.push("Es wird vorerst nur die Personengruppe 101 unterstützt.");
    if($("bgrs").value.trim()&&$("bgrs").value.trim()!=="1111") reasons.push("Es wird vorerst nur die Beitragsgruppe 1111 unterstützt.");
    const birth=$("birth_date").value;
    if(!/^\d{4}-\d{2}-\d{2}$/.test(birth)) reasons.push("Geburtsdatum fehlt; es wird zur Prüfung des Pflegeversicherungszuschlags benötigt.");
    let age=null;
    if(birth&&/^\d{4}-\d{2}$/.test(period)){
      const [py,pm]=period.split("-").map(Number);
      const end=new Date(Date.UTC(py,pm,0));
      const dob=new Date(birth+"T00:00:00Z");
      age=end.getUTCFullYear()-dob.getUTCFullYear();
      if(end.getUTCMonth()<dob.getUTCMonth()||(end.getUTCMonth()===dob.getUTCMonth()&&end.getUTCDate()<dob.getUTCDate())) age--;
      if(age<0||age>120) reasons.push("Geburtsdatum ist ungültig.");
      if((age<23)!=$("under23").checked) reasons.push("Angabe „unter 23 Jahre“ stimmt nicht mit dem Geburtsdatum überein.");
    }
    const start=$("start_date").value;
    if(start&&period&&start.slice(0,7)===period&&start.slice(8,10)!=="01") reasons.push("Beschäftigungsbeginn mitten im Abrechnungsmonat benötigt eine Teilmonatsberechnung.");
    const daysInMonth=period?new Date(Number(period.slice(0,4)),Number(period.slice(5,7)),0).getDate():0;
    if($("sv_days").value.trim()&&Number($("sv_days").value)!==daysInMonth) reasons.push("Teilmonat mit abweichenden SV-Tagen wird noch nicht unterstützt.");
    if(!Number.isFinite(ctx.base)||ctx.base<=0) reasons.push("Monatliches Grundgehalt muss größer als null sein.");
    if(reasons.length) return {ready:true,supported:false,tax:0,soli:0,church:0,reason:reasons.join(" ")};

    const factorMode=classValue==="IV mit Faktor";
    const factor=factorMode?Number(String($("tax_factor").value).replace(",",".")):1;
    if(factorMode&&(!Number.isFinite(factor)||factor<=0||factor>1)){
      return {ready:true,supported:false,tax:0,soli:0,church:0,reason:"Für Steuerklasse IV mit Faktor muss ein gültiger Faktor zwischen 0 und 1 eingetragen werden."};
    }
    const annualAllowance=Math.round(cents($("annual_allowance").value)/12);
    const monthlyAllowance=cents($("monthly_allowance").value);
    const childCount=Number($("children").value||0);
    const names=["LZZ","STKL","RE4","KVZ","PVZ","PVA","PVS","KRV","ALV","PKV","R","ZKF","LZZFREIB","LZZHINZU","af","f"];
    const values=[
      "2",classMap[classValue],String(ctx.taxGross),val("kv_extra").toFixed(2),
      String(childCount===0&&age>=23?1:0),String(Math.max(0,Math.min(childCount,5)-1)),
      $("state").value==="SN"?"1":"0","0","0","0",
      $("religion").value==="Keine"?"0":"1",
      String(Number(String($("child_allowance").value||"0").replace(",","."))||0),
      String(annualAllowance+monthlyAllowance),"0",factorMode?"1":"0",
      factorMode?factor.toFixed(3):"1.000"
    ];
    try{
      const output=JSON.parse(payrollTaxEngine.run(names,values));
      const readCents=name=>{
        const n=Number(output[name]);
        if(!Number.isSafeInteger(n)||n<0) throw new Error("Ungültiger BMF-Ausgabewert: "+name);
        return n;
      };
      const tax=readCents("LSTLZZ");
      const soli=readCents("SOLZLZZ");
      const churchBase=$("religion").value==="Keine"?0:readCents("BK");
      const churchRate=["BW","BY"].includes($("church_tax_state").value)?8:9;
      const church=Math.round(churchBase*churchRate/100);
      return {ready:true,supported:true,tax,soli,church,churchBase,reason:"BMF-PAP 2026 erfolgreich im Browser ausgeführt."};
    }catch(error){
      return {ready:true,supported:false,tax:0,soli:0,church:0,reason:"BMF-Steuerberechnung fehlgeschlagen: "+(error&&error.message?error.message:String(error))};
    }
  }
  const shiftRows = $("shift_rows");
  const wageBodyIds = {earnings:"earnings_rows",netPlus:"net_benefit_rows",netMinus:"net_deduction_rows"};
  const wagePreviewIds = {earnings:"p_earnings_rows",netPlus:"p_net_benefit_rows",netMinus:"p_net_deduction_rows"};
  const ytdFields = ["gross","tax_gross","kv_gross","rv_gross","av_gross","pv_gross","tax","church","soli","kv","rv","av","pv","vwl"];
  const sectionDefinitions = [
    ["tax","Steuermerkmale",true],
    ["social","Sozialversicherung",true],
    ["time","Arbeitszeit und Fehlzeiten",true],
    ["gross","Bruttoentgelt / Bezüge",false],
    ["basis","Steuer- und Sozialversicherungsbasis",true],
    ["netplus","Netto-Bezüge",true],
    ["deductions","Abzüge Arbeitnehmer",false],
    ["ytd","Verdienstbescheinigung",true],
    ["employer","Arbeitgeberanteile und zusätzliche Arbeitgeberkosten",true]
  ];
  const sectionVisibility = Object.fromEntries(sectionDefinitions.map(([key,label,optional])=>[key,true]));
  let activePdfSection = "";
  function sectionEnabled(key){return !sectionDefinitions.some(item=>item[0]===key&&item[2]) || sectionVisibility[key]!==false;}
  function applySectionVisibility(){
    const headings=[...$("payroll_preview").querySelectorAll("h3.section-title")];
    headings.forEach((heading,index)=>{
      const definition=sectionDefinitions[index];if(!definition)return;
      heading.dataset.sectionKey=definition[0];
      const visible=sectionEnabled(definition[0]);
      heading.hidden=!visible;
      let node=heading.nextElementSibling;
      while(node&&!(node.matches&&node.matches("h3.section-title"))){
        if(node.matches&&node.matches(".net-box,.preview-foot"))break;
        node.hidden=!visible;node=node.nextElementSibling;
      }
    });
  }
  function applyEmptyPreviewVisibility(){
    const root=$("payroll_preview");if(!root)return;
    const empty=value=>{const v=String(value??"").trim();return !v||v==="-"||v==="—";};
    root.querySelectorAll(".preview-meta tr").forEach(tr=>{
      const cells=[...tr.children];let visiblePairs=0;
      for(let i=0;i<cells.length;i+=2){
        const label=cells[i],value=cells[i+1];if(!label||!value)continue;
        const show=!empty(value.textContent);
        label.hidden=!show;value.hidden=!show;if(show)visiblePairs++;
      }
      tr.hidden=visiblePairs===0;
    });
    root.querySelectorAll("table").forEach(table=>{
      if(table.classList.contains("preview-meta"))return;
      const rows=[...table.querySelectorAll("tbody tr")];
      rows.forEach(tr=>{
        if(tr.classList.contains("total-row"))return;
        const amount=tr.querySelector(".amount");
        if(amount)tr.hidden=/^(?:0+(?:[,.]0+)?)(?:\s*EUR)?$/i.test(amount.textContent.trim());
      });
      const hasVisible=[...table.querySelectorAll("tbody tr")].some(tr=>!tr.hidden);
      if(table.closest(".preview")&&table.querySelector("tbody")&&!hasVisible)table.hidden=true;
      else if(hasVisible)table.hidden=false;
    });
    root.querySelectorAll(".section-title").forEach(heading=>{
      if(!sectionEnabled(heading.dataset.sectionKey))return;
      let node=heading.nextElementSibling,hasContent=false;
      while(node&&!(node.matches&&node.matches(".section-title"))){
        if(!node.hidden&&node.matches&&node.matches("table,.summary-grid"))hasContent=true;
        node=node.nextElementSibling;
      }
      heading.hidden=!hasContent;
    });
  }
  function buildSectionControls(){
    const host=$("section_visibility_controls");if(!host)return;
    sectionDefinitions.forEach(([key,label,optional])=>{
      const wrapper=document.createElement("label");wrapper.className="visibility-option"+(optional?"":" locked");
      const checkbox=document.createElement("input");checkbox.type="checkbox";checkbox.checked=true;checkbox.disabled=!optional;
      checkbox.setAttribute("aria-label",label+" auf der Abrechnung anzeigen");
      checkbox.addEventListener("change",()=>{sectionVisibility[key]=checkbox.checked;applySectionVisibility();});
      const text=document.createElement("span");text.textContent=label+(optional?"":" · Kernbereich");
      wrapper.append(checkbox,text);host.appendChild(wrapper);
    });
  }
  function addWageRow(kind,preset={}){
    const body=$(wageBodyIds[kind]);if(!body)return;
    const tr=document.createElement("tr");tr.className="wage-row";tr.dataset.kind=kind;
    const makeInput=(field,type,value,min)=>{const input=document.createElement("input");input.type=type;input.dataset.wage=field;input.value=value??"";if(type==="number"){input.min=min??"0";input.step=field==="qty"?"0.01":"0.01";}input.addEventListener("input",update);input.addEventListener("change",update);return input;};
    const makeCell=node=>{const td=document.createElement("td");td.appendChild(node);tr.appendChild(td);};
    makeCell(makeInput("code","text",preset.code||"",null));
    makeCell(makeInput("description","text",preset.description||"",null));
    const unit=document.createElement("select");unit.dataset.wage="unit";["EUR","Std","Tag","Stück"].forEach(v=>{const o=document.createElement("option");o.value=v;o.textContent=v;unit.appendChild(o);});unit.value=preset.unit||"EUR";unit.addEventListener("change",update);makeCell(unit);
    makeCell(makeInput("qty","number",preset.qty??"1"));
    makeCell(makeInput("factor","number",preset.factor??"0"));
    makeCell(makeInput("percent","number",preset.percent??"100"));
    if(kind==="earnings"){
      ["taxable","sv","gb"].forEach(field=>{const td=document.createElement("td"),input=document.createElement("input");input.type="checkbox";input.dataset.wage=field;input.checked=preset[field]!==false;input.addEventListener("change",update);td.appendChild(input);tr.appendChild(td);});
    }
    const amountCell=document.createElement("td"),amount=document.createElement("span");amount.dataset.wageAmount="";amount.textContent="0,00";amountCell.appendChild(amount);tr.appendChild(amountCell);
    const action=document.createElement("td"),remove=document.createElement("button");remove.type="button";remove.className="secondary";remove.textContent="Entfernen";remove.addEventListener("click",()=>{tr.remove();update();});action.appendChild(remove);tr.appendChild(action);
    body.appendChild(tr);update();
  }
  function readWageRows(kind){
    return [...$(wageBodyIds[kind]).querySelectorAll(".wage-row")].map(tr=>{
      const get=name=>tr.querySelector('[data-wage="'+name+'"]');
      const qty=Number(get("qty").value||0),factor=Number(get("factor").value||0),percent=Number(get("percent").value||100);
      const amount=Math.max(0,Math.round(qty*factor*percent));
      return {code:get("code").value.trim(),description:get("description").value.trim(),unit:get("unit").value,qty,factor,percent,amount,taxable:kind!=="earnings"||get("taxable").checked,sv:kind!=="earnings"||get("sv").checked,gb:kind!=="earnings"||get("gb").checked};
    }).filter(item=>item.amount!==0||item.code||item.description);
  }
  function renderWageRows(kind,items){
    const body=$(wagePreviewIds[kind]);body.textContent="";
    items.forEach(item=>{const tr=document.createElement("tr"),label=document.createElement("td"),amount=document.createElement("td");label.textContent=(item.code?item.code+" ":"")+item.description+" · "+item.qty+" "+item.unit+" × "+item.factor.toLocaleString("de-DE")+" EUR × "+item.percent.toLocaleString("de-DE")+" %";amount.className="amount";amount.textContent=money(item.amount);tr.appendChild(label);tr.appendChild(amount);body.appendChild(tr);});
    const formRows=$(wageBodyIds[kind]).querySelectorAll(".wage-row");
    formRows.forEach(tr=>{const get=name=>tr.querySelector('[data-wage="'+name+'"]');const q=Number(get("qty").value||0),factor=Number(get("factor").value||0),percent=Number(get("percent").value||100);tr.querySelector("[data-wage-amount]").textContent=money(Math.max(0,Math.round(q*factor*percent)));});
  }
  function formatPeriod(value){if(!/^\d{4}-\d{2}$/.test(value||""))return value||"-";const [year,month]=value.split("-").map(Number);return new Date(year,month-1,1).toLocaleDateString("de-DE",{month:"long",year:"numeric"});}
  function previewValue(inputId,outputId,formatter=value=>value||"-"){const input=$(inputId),output=$(outputId);if(input&&output)output.textContent=formatter(input.type==="checkbox"?input.checked:input.value);}
  function ytdValue(id){return cents($(id).value);}

  function addShift(date="",start="20:00",end="06:00",breakStart="",breakEnd=""){
    const tr=document.createElement("tr");
    [["date","date",date],["start","time",start],["end","time",end],["break_start","time",breakStart],["break_end","time",breakEnd]].forEach(([name,type,value])=>{
      const td=document.createElement("td"),input=document.createElement("input");
      input.type=type;input.dataset.shift=name;input.value=value;input.style.minWidth=type==="date"?"135px":"105px";
      input.addEventListener("input",update);td.appendChild(input);tr.appendChild(td);
    });
    const td=document.createElement("td"),remove=document.createElement("button");
    remove.type="button";remove.className="secondary";remove.textContent="Entfernen";
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
      if(!date||start===null||end===null){errors.push("Schicht "+(index+1)+": Bitte Datum sowie Beginn und Ende vollständig eingeben.");return;}
      if((get("break_start")&&!get("break_end"))||(!get("break_start")&&get("break_end"))||((bs===null)!==(be===null))){errors.push("Schicht "+(index+1)+": Bitte beide Pausenzeiten eingeben oder beide Felder leer lassen.");return;}
      const [y,m,d]=date.split("-").map(Number);
      let cursor=Date.UTC(y,m-1,d,Math.floor(start/60),start%60),finish=Date.UTC(y,m-1,d,Math.floor(end/60),end%60);
      if(finish<=cursor) finish+=86400000;
      let breakFrom=null,breakTo=null;
      if(bs!==null&&be!==null){
        breakFrom=Date.UTC(y,m-1,d,Math.floor(bs/60),bs%60);breakTo=Date.UTC(y,m-1,d,Math.floor(be/60),be%60);
        if(breakFrom<cursor)breakFrom+=86400000;
        if(breakTo<=breakFrom)breakTo+=86400000;
        if(breakFrom<cursor||breakTo>finish){errors.push("Schicht "+(index+1)+": Die Pause muss innerhalb der Schicht liegen.");return;}
      }
      const startedBeforeMidnight=finish>Date.UTC(y,m-1,d,24,0);
      for(let t=cursor;t<finish;t+=60000){
        if(breakFrom!==null&&t>=breakFrom&&t<breakTo)continue;
        const dt=new Date(t),day=dt.getUTCDay(),mins=dt.getUTCHours()*60+dt.getUTCMinutes();
        const dateIso=isoDate(new Date(Date.UTC(dt.getUTCFullYear(),dt.getUTCMonth(),dt.getUTCDate())));
        const isNight=mins>=1200||mins<360;
        const previousIso=isoDate(new Date(Date.UTC(dt.getUTCFullYear(),dt.getUTCMonth(),dt.getUTCDate()-1)));
        const afterMidnightCarry=startedBeforeMidnight&&mins<240;
        const previousDay=new Date(Date.UTC(dt.getUTCFullYear(),dt.getUTCMonth(),dt.getUTCDate()-1)).getUTCDay();
        const isSunday=day===0||(afterMidnightCarry&&previousDay===0);
        const isHoliday=holidays.has(dateIso)||(afterMidnightCarry&&holidays.has(previousIso));
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
    const earnings=readWageRows("earnings"),netBenefits=readWageRows("netPlus"),netDeductions=readWageRows("netMinus");
    const earningsTotal=earnings.filter(item=>item.gb).reduce((sum,item)=>sum+item.amount,0),taxableItems=earnings.filter(item=>item.taxable).reduce((sum,item)=>sum+item.amount,0),svItems=earnings.filter(item=>item.sv).reduce((sum,item)=>sum+item.amount,0);
    const netBenefitsTotal=netBenefits.reduce((sum,item)=>sum+item.amount,0),netDeductionsTotal=netDeductions.reduce((sum,item)=>sum+item.amount,0);
    const hourly=hours>0?(base/100)/hours:0,shifts=getShifts();
    const nightHours=shifts.night/60,sundayHours=shifts.sunday/60,holidayHours=shifts.holiday/60;
    const nightPay=Math.round(hourly*nightHours*rate("night_rate")*100);
    const sundayPay=Math.round(hourly*sundayHours*rate("sunday_rate")*100);
    const holidayPay=Math.round(hourly*holidayHours*rate("holiday_rate")*100);
    const premium=nightPay+sundayPay+holidayPay,gross=base+bonus+allowance+premium+earningsTotal;
    const taxHourly=Math.min(hourly,50),svHourly=Math.min(hourly,25);
    const taxFree=Math.min(nightPay,Math.round(taxHourly*100*shifts.nightTaxFree))+Math.min(sundayPay,Math.round(taxHourly*100*shifts.sundayTaxFree))+Math.min(holidayPay,Math.round(taxHourly*100*shifts.holidayTaxFree));
    const svFree=Math.min(nightPay,Math.round(svHourly*100*shifts.nightTaxFree))+Math.min(sundayPay,Math.round(svHourly*100*shifts.sundayTaxFree))+Math.min(holidayPay,Math.round(svHourly*100*shifts.holidayTaxFree));
    const taxGross=Math.max(0,base+bonus+allowance+premium-taxFree+taxableItems),svGross=Math.max(0,base+bonus+allowance+premium-svFree+svItems);
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
    const taxResult=calculateBmfTax({base,bonus,allowance,premium,taxableItems,earnings,taxGross,svGross});
    const tax=taxResult.supported?taxResult.tax:0,soli=taxResult.supported?taxResult.soli:0,church=taxResult.supported?taxResult.church:0,manualTax=tax+soli+church,other=cents($("other").value),advance=cents($("advance").value);
    const vwl=cents($("vwl_deduction").value),garnishment=cents($("garnishment").value),loanRepayment=cents($("loan_repayment").value),kugPayout=cents($("kug_payout").value);
    const netFixedDeductions=vwl+garnishment+loanRepayment,employerExtra=cents($("u1_cost").value)+cents($("u2_cost").value)+cents($("insolvency_cost").value)+cents($("accident_cost").value);
    const deductions=employeeSocial+manualTax+other+advance+netFixedDeductions+netDeductionsTotal,net=gross-deductions+netBenefitsTotal+kugPayout;
    return {base,bonus,allowance,hourly,shifts,nightHours,sundayHours,holidayHours,nightPay,sundayPay,holidayPay,premium,gross,earnings,netBenefits,netDeductions,netBenefitsTotal,netDeductionsTotal,taxFree,svFree,taxGross,svGross,kvBase,rvBase,kvEmployee,kvEmployer,pvEmployee,pvEmployer,rvEmployee,rvEmployer,avEmployee,avEmployer,employeeSocial,employerSocial,manualTax,tax,soli,church,taxReady:taxResult.ready,taxSupported:taxResult.supported,taxReason:taxResult.reason,other,advance,vwl,garnishment,loanRepayment,kugPayout,employerExtra,deductions,net,stateSelected};
  }
  function update(){
    const r=calc();
    set("p_base_pay",r.base);set("p_bonus",r.bonus);set("p_allowance",r.allowance);set("p_night_pay",r.nightPay);set("p_sunday_pay",r.sundayPay);set("p_holiday_pay",r.holidayPay);set("p_tax_free",r.taxFree);set("p_sv_free",r.svFree);set("p_sv_gross",r.svGross);
    set("p_gross",r.gross);set("p_tax_gross",r.taxGross);set("p_kv_gross",r.kvBase);set("p_rv_gross",r.rvBase);
    if($("tax").value!==(r.taxSupported?(r.tax/100).toFixed(2):"")) $("tax").value=r.taxSupported?(r.tax/100).toFixed(2):"";
    if($("soli").value!==(r.taxSupported?(r.soli/100).toFixed(2):"")) $("soli").value=r.taxSupported?(r.soli/100).toFixed(2):"";
    if($("church").value!==(r.taxSupported?(r.church/100).toFixed(2):"")) $("church").value=r.taxSupported?(r.church/100).toFixed(2):"";
    $("tax_engine_status").textContent=r.taxReason||"";
    $("tax_engine_status").style.borderColor=r.taxSupported?"#27834a":"#c58a00";
    set("p_tax",r.tax);set("p_health",r.kvEmployee);set("p_care",r.pvEmployee);
    set("p_pension",r.rvEmployee);set("p_unemployment",r.avEmployee);set("p_other",r.other);$("p_care").textContent=r.stateSelected?money(r.pvEmployee):"—";$("p_employer_care").textContent=r.stateSelected?money(r.pvEmployer):"—";
    set("p_deductions",r.deductions);set("p_net",r.net);
    set("p_employer_health",r.kvEmployer);set("p_employer_care",r.pvEmployer);set("p_employer_pension",r.rvEmployer);set("p_employer_unemployment",r.avEmployer);
    $("p_company").textContent=$("company").value||"-";$("p_company_address").textContent=$("company_address").value||"-";
    $("p_employee").textContent=$("employee").value||"-";$("p_employee_no").textContent=$("employee_no").value||"-";
    $("p_company_short").textContent=$("company").value||"-";$("p_period").textContent=$("period").value||"-";
    $("p_start_date").textContent=$("start_date").value||"-";$("p_pay_date").textContent=$("pay_date").value||"-";
    $("shift_summary").textContent="Nacht: "+r.nightHours.toFixed(2)+" Std. | Sonntag: "+r.sundayHours.toFixed(2)+" Std. | Feiertag: "+r.holidayHours.toFixed(2)+" Std. | Zuschläge: "+money(r.premium)+" € | Geschätzter SV-freier Anteil: "+money(r.svFree)+" € | SV-pflichtiges Entgelt: "+money(r.svGross)+" €"+(!r.stateSelected?" | Bitte wählen Sie das Bundesland des Arbeitsortes aus, um das Nettoentgelt zu berechnen.":"")+(r.shifts.errors.length?" | "+r.shifts.errors.join(" "):"");
    $("p_gross").parentElement.cells[0].textContent="Gesamtbrutto einschließlich Zuschläge";
    $("p_other").parentElement.cells[0].textContent="Sonstige Abzüge";
    $("p_gross").parentElement.cells[1].textContent=money(r.gross);
    $("p_deductions").parentElement.cells[1].textContent=money(r.deductions);$("p_net").textContent=!r.taxSupported?"Nicht berechnet":(r.stateSelected?money(r.net)+" €":"Bundesland auswählen");
    $("shift_summary").style.color=r.shifts.errors.length?"#9b2c2c":"";
    set("p_tax",r.tax);set("p_soli",r.soli);set("p_church",r.church);set("p_advance",r.advance);set("p_vwl",r.vwl);set("p_garnishment",r.garnishment);set("p_loan_repayment",r.loanRepayment);set("p_kug_payout",r.kugPayout);
    $("p_tax").parentElement.style.display=r.taxSupported?"table-row":"none";$("p_soli").parentElement.style.display=r.taxSupported?"table-row":"none";$("p_church").parentElement.style.display=r.taxSupported?"table-row":"none";$("p_advance").parentElement.style.display="table-row";
    $("p_tax").parentElement.cells[1].textContent=money(r.tax);$("p_soli").parentElement.cells[1].textContent=money(r.soli);$("p_church").parentElement.cells[1].textContent=money(r.church);$("p_other").parentElement.cells[1].textContent=money(r.other);$("p_advance").parentElement.cells[1].textContent=money(r.advance);
    renderWageRows("earnings",r.earnings);renderWageRows("netPlus",r.netBenefits);renderWageRows("netMinus",r.netDeductions);
    set("p_u1_cost",cents($("u1_cost").value));set("p_u2_cost",cents($("u2_cost").value));set("p_insolvency_cost",cents($("insolvency_cost").value));set("p_accident_cost",cents($("accident_cost").value));set("p_employer_total",r.gross+r.employerSocial+r.employerExtra);
    const previewPairs=[["employee_address","p_employee_address"],["birth_date","p_birth_date"],["child_allowance","p_child_allowance"],["religion","p_religion"],["dba_country","p_dba_country"],["uv_code_test","p_uv_code_test"],["uv_days","p_uv_days"],["steuer_id_test","p_steuer_id_test"],["sv_number_test","p_sv_number_test"],["kasse","p_kasse"],["pgrs","p_pgrs"],["bgrs","p_bgrs"],["sv_days","p_sv_days"],["attendance_days","p_attendance_days"],["vacation_entitlement","p_vacation_entitlement"],["vacation_carryover","p_vacation_carryover"],["vacation_taken","p_vacation_taken"],["sick_days","p_sick_days"],["absence_days","p_absence_days"],["holiday_days","p_holiday_days"],["rest_garnishment","p_rest_garnishment"],["rest_loan","p_rest_loan"],["bank_name_test","p_bank_name_test"]];
    previewPairs.forEach(([inputId,outputId])=>previewValue(inputId,outputId));
    previewValue("tax_class","p_tax_class",v=>v? v+($("tax_factor").value?" / Faktor "+$("tax_factor").value:""):"-");
    previewValue("midijob","p_midijob",v=>v?"Ja":"Nein");
    previewValue("kv_extra","p_kv_extra",v=>v+" %");
    previewValue("health_rate","p_health_rate",v=>v+" %");
    previewValue("kv_type","p_kv_type");
    previewValue("children","p_children");
    previewValue("under23","p_under23",v=>v?"Ja":"Nein");
    previewValue("state","p_state",v=>$("state").selectedOptions[0]?.textContent||"-");
    previewValue("payment_method","p_payment_method");
    ["annual_allowance","monthly_allowance"].forEach(id=>previewValue(id,id==="annual_allowance"?"p_annual_allowance":"p_monthly_allowance",v=>money(cents(v))+" EUR"));
    previewValue("scheduled_hours","p_hours",v=>v+" / "+$("actual_hours").value+" Std.");
    const leaveBalance=Math.max(0,val("vacation_entitlement")+val("vacation_carryover")-val("vacation_taken"));
    $("p_vacation_balance").textContent=leaveBalance.toLocaleString("de-DE")+" Tage";
    $("p_period_days").textContent=$("period").value?new Date(Number($("period").value.slice(0,4)),Number($("period").value.slice(5,7)),0).getDate()+" Kalendertage":"-";
    $("p_period").textContent=formatPeriod($("period").value);$("p_pay_date").textContent=$("pay_date").value||"-";
    ytdFields.forEach(id=>{const out=$("p_ytd_"+id);if(out)out.textContent=money(ytdValue("ytd_"+id))+" EUR";});
    applySectionVisibility();
    applyEmptyPreviewVisibility();
  }
  $("add_shift").addEventListener("click",()=>addShift());
  $("add_earning").addEventListener("click",()=>addWageRow("earnings"));
  $("add_net_benefit").addEventListener("click",()=>addWageRow("netPlus"));
  $("add_net_deduction").addEventListener("click",()=>addWageRow("netMinus"));
  function validateForOutput(){
    const r=calc();
    if(!r.stateSelected){window.alert("Bitte zuerst das Bundesland des Arbeitsortes auswählen.");return null;}
    if(!r.taxReady||!r.taxSupported){window.alert(r.taxReason||"Die Steuerberechnung ist noch nicht verfügbar. Es wird keine unvollständige Abrechnung ausgegeben.");return null;}
    if(r.shifts.errors.length){window.alert(r.shifts.errors.join(String.fromCharCode(10)));return null;}
    return r;
  }
  $("print_button").addEventListener("click",()=>{if(validateForOutput())window.print();});
  $("pdf_button").addEventListener("click",()=>{
    const r=validateForOutput();if(!r)return;
    if(!window.jspdf||!window.jspdf.jsPDF){window.alert("PDF-Modul konnte nicht geladen werden. Bitte Internetverbindung prüfen oder die Druckfunktion verwenden.");return;}
    const {jsPDF}=window.jspdf,doc=new jsPDF({orientation:"portrait",unit:"mm",format:"a4"});
    const left=15,right=195,width=180;let y=15;
    const ensureSpace=(space=8)=>{if(y+space>280){doc.addPage();y=15;};};
    const line=(yy)=>{doc.setDrawColor(205,218,234);doc.setLineWidth(0.35);doc.line(left,yy,right,yy);};
    const txt=(s,x,yy,size=9,bold=false,options={})=>{if(s===null||s===undefined||String(s).trim()==="")return;doc.setFont("helvetica",bold?"bold":"normal");doc.setFontSize(size);doc.text(String(s),x,yy,options);};
    const euro=(n)=>money(n)+" EUR";
    const company=$("company").value.trim(),address=$("company_address").value.trim();
    const employee=$("employee").value.trim(),employeeNo=$("employee_no").value.trim();
    const logo=$("logo_area").querySelector("img");
    if(logo&&logo.complete&&logo.naturalWidth>0){try{const canvas=document.createElement("canvas");canvas.width=logo.naturalWidth;canvas.height=logo.naturalHeight;canvas.getContext("2d").drawImage(logo,0,0);doc.addImage(canvas.toDataURL("image/png"),"PNG",left,y,28,15,undefined,"FAST");}catch(e){}}
    txt(company,right,y+3,12,true);txt(address,right,y+8,8);y+=21;line(y);y+=8;
    txt("ABRECHNUNG DER BRUTTO/NETTO-BEZÜGE",left,y,12,true);txt($("period").value?"Für: "+formatPeriod($("period").value):"",right,y,9,true);y+=7;
    txt(employee?"Arbeitnehmer: "+employee:"",left,y,9,true);txt(employeeNo?"Personalnummer: "+employeeNo: "",105,y,9);y+=6;
    txt(company?"Arbeitgeber: "+company:"",left,y,9);txt($("pay_date").value?"Auszahlungsdatum: "+$("pay_date").value:"",105,y,9);y+=6;
    txt($("start_date").value?"Beschäftigungsbeginn: "+$("start_date").value:"",left,y,9);y+=5;line(y);y+=6;
    let pdfSectionStarted=false;const startPdfSection=()=>{if(pdfSectionStarted)return;ensureSpace(15);y+=2;doc.setDrawColor(80,80,80);doc.setLineWidth(0.35);doc.line(left,y+3,right,y+3);doc.setTextColor(20,20,20);txt(activePdfTitle.toUpperCase(),left,y,8,true);y+=7;pdfSectionStarted=true;};let activePdfTitle="";const hasPdfValue=value=>{const v=String(value??"").trim();return v!==""&&v!=="-"&&v!=="—"&&!/^(?:0+(?:[,.]0+)?(?:\s*EUR)?)$/i.test(v);};const row=(label,value,bold=false)=>{if(!sectionEnabled(activePdfSection)||!Number.isFinite(Number(value))||Number(value)===0)return;startPdfSection();ensureSpace(8);if(bold){doc.setDrawColor(120,120,120);doc.line(left,y+2,right,y+2);}doc.setTextColor(20,20,20);txt(label,left+1,y,8,bold);doc.setTextColor(20,20,20);txt(euro(value),right-1,y,8,bold,{align:"right"});y+=6;};
    const section=(title)=>{const normalized=title.toLowerCase();const alias=normalized.includes("steuerrechtliche abzüge")||normalized.includes("sozialversicherungsabzüge")||normalized==="netto-abzüge";const match=alias?sectionDefinitions.find(item=>item[0]==="deductions"):sectionDefinitions.find(item=>normalized.startsWith(item[1].toLowerCase().slice(0,Math.min(12,item[1].length))));activePdfSection=match?match[0]:"";activePdfTitle=title;pdfSectionStarted=false;};
    section("Steuermerkmale");
    const pair=(label,value,label2="",value2="")=>{if(!sectionEnabled(activePdfSection))return;const first=hasPdfValue(value),second=Boolean(label2)&&hasPdfValue(value2);if(!first&&!second)return;startPdfSection();ensureSpace(7);if(first)txt(label+": "+value,left,y,8);if(second)txt(label2+": "+value2,first?105:left,y,8);y+=5;};
    pair("Anschrift", $("employee_address").value,"Geburtsdatum",$("birth_date").value);
    pair("Geburtsdatum", $("birth_date").value,"Steuerklasse",$("tax_class").value);
    pair("Faktor",$("tax_factor").value,"Kinderfreibetrag",$("child_allowance").value);
    pair("Konfession",$("religion").value,"Freibetrag jährlich",money(cents($("annual_allowance").value))+" EUR");
    pair("Freibetrag monatlich",money(cents($("monthly_allowance").value))+" EUR","DBA-Staat",$("dba_country").value);
    pair("Midijob",$("midijob").checked?"Ja":"","Steuer-ID (Testwert)",$("steuer_id_test").value);
    section("Sozialversicherung");
    pair("SV-Nummer (Testwert)",$("sv_number_test").value,"Krankenkasse",$("kasse").value);
    pair("PGRS",$("pgrs").value,"BGRS",$("bgrs").value);
    pair("SV-Tage",$("sv_days").value,"UV-Tage",$("uv_days").value);
    pair("UV-Kennzeichen",$("uv_code_test").value,"Bundesland",$("state").selectedOptions[0]?.textContent||"");
    pair("Kinder unter 25",Number($("children").value)>0?$("children").value:"","Unter 23 Jahre",$("under23").checked?"Ja":"");
    section("Arbeitszeit und Fehlzeiten");
    pair("Soll-/Iststunden",$("scheduled_hours").value+" / "+$("actual_hours").value,"Anwesenheitstage",$("attendance_days").value);
    pair("Urlaubsanspruch",$("vacation_entitlement").value,"Übertrag Vorjahr",$("vacation_carryover").value);
    pair("Genommene Urlaubstage",$("vacation_taken").value,"Resturlaub",String(Math.max(0,val("vacation_entitlement")+val("vacation_carryover")-val("vacation_taken"))));
    pair("Krankheitstage",$("sick_days").value,"Sonstige Fehltage",$("absence_days").value);
    section("Bruttoentgelt / Bezüge");
    row("Grundgehalt",r.base);row("Nachtzuschläge",r.nightPay);row("Sonntagszuschläge",r.sundayPay);row("Feiertagszuschläge",r.holidayPay);row("Bonus / Einmalzahlungen",r.bonus);row("Zulagen / Sonstige Bezüge",r.allowance);
    r.earnings.forEach(item=>row((item.code?item.code+" ":"")+item.description+" · "+item.qty+" "+item.unit+" × "+item.factor+" EUR × "+item.percent+" %",item.amount));
    row("Gesamtbrutto",r.gross,true);
    section("Steuer- und Sozialversicherungsbasis");
    row("Steuer-Brutto",r.taxGross,true);row("KV-Brutto",r.kvBase);row("RV-/AV-Brutto",r.rvBase);row("Steuerfrei geschätzter Zuschlagsanteil",r.taxFree);row("SV-freier geschätzter Zuschlagsanteil",r.svFree);row("SV-pflichtiges Brutto",r.svGross,true);
    section("Steuerrechtliche Abzüge");
    row("Lohnsteuer",r.tax);row("Kirchensteuer",r.church);row("Solidaritätszuschlag",r.soli);
    section("Sozialversicherungsabzüge Arbeitnehmer");
    row("Krankenversicherung",r.kvEmployee);row("Pflegeversicherung",r.pvEmployee);row("Rentenversicherung",r.rvEmployee);row("Arbeitslosenversicherung",r.avEmployee);
    section("Netto-Bezüge");
    row("Kug-Auszahlung / Netto-Zuschuss",r.kugPayout);
    r.netBenefits.forEach(item=>row((item.code?item.code+" ":"")+item.description+" · "+item.qty+" "+item.unit+" × "+item.factor+" EUR × "+item.percent+" %",item.amount));
    section("Netto-Abzüge");
    row("Sonstige Abzüge",r.other);row("Vorschuss / Abschlag",r.advance);row("VWL",r.vwl);row("Pfändung",r.garnishment);row("Darlehensrückzahlung",r.loanRepayment);
    r.netDeductions.forEach(item=>row((item.code?item.code+" ":"")+item.description+" · "+item.qty+" "+item.unit+" × "+item.factor+" EUR × "+item.percent+" %",item.amount));
    row("Gesamtabzüge",r.deductions,true);
    section("Verdienstbescheinigung (Jahreswerte)");
    const ytdLabels={gross:"Gesamt-Brutto",tax_gross:"Steuer-Brutto",kv_gross:"KV-Brutto",rv_gross:"RV-Brutto",av_gross:"AV-Brutto",pv_gross:"PV-Brutto",tax:"Lohnsteuer",church:"Kirchensteuer",soli:"Solidaritätszuschlag",kv:"KV-Beitrag",rv:"RV-Beitrag",av:"AV-Beitrag",pv:"PV-Beitrag",vwl:"VWL gesamt"};
    ytdFields.forEach(id=>pair(ytdLabels[id],money(ytdValue("ytd_"+id))+" EUR"));
    section("Arbeitgeberanteile und zusätzliche Kosten");
    row("Krankenversicherung Arbeitgeber",r.kvEmployer);row("Pflegeversicherung Arbeitgeber",r.pvEmployer);row("Rentenversicherung Arbeitgeber",r.rvEmployer);row("Arbeitslosenversicherung Arbeitgeber",r.avEmployer);
    row("Umlage U1",cents($("u1_cost").value));row("Umlage U2",cents($("u2_cost").value));row("Insolvenzgeldumlage",cents($("insolvency_cost").value));row("Unfallversicherung / BG",cents($("accident_cost").value));row("Gesamtkosten Arbeitgeber",r.gross+r.employerSocial+r.employerExtra,true);
    pair("Auszahlungsweg",$("payment_method").value,"Bank (Testwert)",$("bank_name_test").value);
    pair("Restpfändung",money(cents($("rest_garnishment").value))+" EUR","Darlehen Rest",money(cents($("rest_loan").value))+" EUR");
    ensureSpace(27);y+=3;doc.setDrawColor(20,20,20);doc.setLineWidth(0.8);doc.rect(left,y,width,17);doc.setTextColor(20,20,20);txt("NETTO-AUSZAHLUNG",left+5,y+10.5,10,true);doc.setFont("helvetica","bold");doc.setFontSize(15);doc.setTextColor(20,20,20);doc.text(euro(r.net),right-5,y+11,{align:"right"});y+=24;
    doc.setFont("helvetica","normal");doc.setFontSize(7);doc.text("Berechnung auf Basis der eingegebenen Angaben. Lohnsteuer nicht automatisch berechnet. Bitte Angaben und gesetzliche Abrechnungsvorgaben prüfen.",left,y,{maxWidth:width});
    doc.save("Entgeltabrechnung-"+(($("period").value||"Zeitraum").replace(/[^a-zA-Z0-9_-]/g,"_"))+".pdf");
  });
  $("reset_button").addEventListener("click",()=>{
    document.querySelectorAll(".editor input").forEach(el=>{
      if(el.type==="file"){el.value="";return;}if(el.type==="checkbox"){el.checked=false;return;}
      if(el.type==="number"){el.value=el.id==="base_pay"?"3000":el.id==="monthly_hours"?"173.33":el.id==="kv_extra"?"2.9":el.id==="health_rate"?"14.6":"0";return;}el.value="";
    });
    document.querySelectorAll(".editor select").forEach(el=>el.selectedIndex=0);
    $("state").value="";$("children").value="0";$("holidays").value="";shiftRows.innerHTML="";
    Object.values(wageBodyIds).forEach(id=>$(id).textContent="");
    $("logo_area").innerHTML="LOGO<br>Unternehmen";addWageRow("earnings");update();
  });
  $("logo_file").addEventListener("change",event=>{
    const file=event.target.files&&event.target.files[0],area=$("logo_area");
    if(!file){area.innerHTML="LOGO<br>Unternehmen";return;}
    if(!["image/png","image/jpeg","image/webp"].includes(file.type)||file.size>2*1024*1024){event.target.value="";area.textContent="Nur PNG, JPG oder WebP bis 2 MB";return;}
    const reader=new FileReader();reader.onload=()=>{area.innerHTML="";const img=document.createElement("img");img.alt="Company logo";img.src=reader.result;area.appendChild(img);};reader.readAsDataURL(file);
  });
  document.querySelectorAll(".editor input,.editor select,.editor textarea").forEach(el=>{el.addEventListener("input",update);el.addEventListener("change",update);});
  buildSectionControls();
  addShift();
  addWageRow("earnings");
  addWageRow("netPlus");
  addWageRow("netMinus");
})();
</script>
</body></html>"""

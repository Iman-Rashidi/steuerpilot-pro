"use strict";

const RULES_2026 = Object.freeze({
  year: 2026,
  gkvGeneralRate: 14.6,
  gkvAssessmentCeilingMonthly: 5812.50,
  pensionRate: 18.6,
  unemploymentRate: 2.6,
  pensionAssessmentCeilingMonthly: 8450,
  careRate: 3.6,
  averageGkvAdditionalRate: 2.9
});

function roundMoney(value) {
  return Math.round((Number(value) + Number.EPSILON) * 100) / 100;
}

function finiteNumber(value, label, min = 0, max = 100000000) {
  const n = Number(value);
  if (!Number.isFinite(n) || n < min || n > max) {
    throw new Error(label + " مقدار معتبر ندارد.");
  }
  return n;
}

function addDays(date, days) {
  const next = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  next.setDate(next.getDate() + days);
  return next;
}

function dateKey(date) {
  return [
    date.getFullYear(),
    String(date.getMonth() + 1).padStart(2, "0"),
    String(date.getDate()).padStart(2, "0")
  ].join("-");
}

function parseDateTime(dateText, timeText) {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(String(dateText || "")) ||
      !/^(?:[01]\d|2[0-3]):[0-5]\d$/.test(String(timeText || ""))) {
    throw new Error("تاریخ یا ساعت شیفت معتبر نیست.");
  }
  const [year, month, day] = dateText.split("-").map(Number);
  const [hour, minute] = timeText.split(":").map(Number);
  const date = new Date(year, month - 1, day, hour, minute, 0, 0);
  if (date.getFullYear() !== year || date.getMonth() !== month - 1 ||
      date.getDate() !== day) {
    throw new Error("تاریخ شیفت معتبر نیست.");
  }
  return date;
}

function easterSunday(year) {
  const a = year % 19;
  const b = Math.floor(year / 100);
  const c = year % 100;
  const d = Math.floor(b / 4);
  const e = b % 4;
  const f = Math.floor((b + 8) / 25);
  const g = Math.floor((b - f + 1) / 3);
  const h = (19 * a + b - d - g + 15) % 30;
  const i = Math.floor(c / 4);
  const k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7;
  const m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31);
  const day = ((h + l - 7 * m + 114) % 31) + 1;
  return new Date(year, month - 1, day);
}

function holidayName(date, state, extraHolidayDates = []) {
  const y = date.getFullYear();
  const m = date.getMonth() + 1;
  const d = date.getDate();
  const key = dateKey(date);
  const extra = new Set(extraHolidayDates);
  if (extra.has(key)) return "Lokaler gesetzlicher Feiertag";

  const easter = easterSunday(y);
  const fixed = new Map([
    ["1-1", "Neujahr"],
    ["5-1", "Tag der Arbeit"],
    ["10-3", "Tag der Deutschen Einheit"],
    ["12-25", "1. Weihnachtstag"],
    ["12-26", "2. Weihnachtstag"]
  ]);
  const base = fixed.get(m + "-" + d);
  if (base) return base;

  if (key === dateKey(addDays(easter, -2))) return "Karfreitag";
  if (key === dateKey(addDays(easter, 1))) return "Ostermontag";
  if (key === dateKey(addDays(easter, 39))) return "Christi Himmelfahrt";
  if (key === dateKey(addDays(easter, 50))) return "Pfingstmontag";
  if (state === "BB" && key === dateKey(easter)) return "Ostersonntag";
  if (state === "BB" && key === dateKey(addDays(easter, 49))) return "Pfingstsonntag";

  if (m === 1 && d === 6 && ["BW", "BY", "ST"].includes(state)) return "Heilige Drei Könige";
  if (m === 3 && d === 8 && ["BE", "MV"].includes(state)) return "Internationaler Frauentag";
  if (key === dateKey(addDays(easter, 60)) && ["BW", "BY", "HE", "NW", "RP", "SL"].includes(state)) {
    return "Fronleichnam";
  }
  if (m === 8 && d === 15 && state === "SL") return "Mariä Himmelfahrt";
  if (m === 9 && d === 20 && state === "TH") return "Weltkindertag";
  if (m === 10 && d === 31 && ["BB", "HB", "HH", "MV", "NI", "SN", "ST", "SH", "TH"].includes(state)) {
    return "Reformationstag";
  }
  if (m === 11 && d === 1 && ["BW", "BY", "NW", "RP", "SL"].includes(state)) return "Allerheiligen";
  if (state === "SN" && m === 11) {
    const nov22 = new Date(y, 10, 22);
    let repentance = nov22;
    while (repentance.getDay() !== 3) repentance = addDays(repentance, -1);
    if (key === dateKey(repentance)) return "Buß- und Bettag";
  }
  return null;
}

function holidayPremiumKind(date, minuteOfDay, state, extraHolidayDates) {
  const month = date.getMonth() + 1;
  const day = date.getDate();
  if (month === 12 && day === 24 && minuteOfDay >= 14 * 60) {
    return { kind: "specialHoliday", cap: 150, name: "Heiligabend ab 14 Uhr" };
  }
  if (month === 12 && day === 31 && minuteOfDay >= 14 * 60) {
    return { kind: "holiday", cap: 125, name: "Silvester ab 14 Uhr" };
  }
  const name = holidayName(date, state, extraHolidayDates);
  if (!name) return null;
  const special = (month === 5 && day === 1) ||
    (month === 12 && (day === 25 || day === 26));
  return {
    kind: special ? "specialHoliday" : "holiday",
    cap: special ? 150 : 125,
    name
  };
}

function readShift(shift) {
  const start = parseDateTime(shift.date, shift.start);
  let end = parseDateTime(shift.date, shift.end);
  if (end <= start) end = new Date(end.getTime() + 24 * 60 * 60 * 1000);
  const durationMinutes = (end.getTime() - start.getTime()) / 60000;
  if (durationMinutes <= 0 || durationMinutes > 16 * 60) {
    throw new Error("هر شیفت باید بیشتر از صفر و حداکثر ۱۶ ساعت باشد.");
  }
  let breakStart = null;
  let breakEnd = null;
  const hasBreakStart = Boolean(shift.breakStart);
  const hasBreakEnd = Boolean(shift.breakEnd);
  if (hasBreakStart !== hasBreakEnd) {
    throw new Error("برای استراحت، ساعت شروع و پایان را هر دو وارد کن.");
  }
  if (hasBreakStart) {
    breakStart = parseDateTime(shift.date, shift.breakStart);
    breakEnd = parseDateTime(shift.date, shift.breakEnd);
    if (breakStart < start) breakStart = new Date(breakStart.getTime() + 24 * 60 * 60 * 1000);
    if (breakEnd <= breakStart) breakEnd = new Date(breakEnd.getTime() + 24 * 60 * 60 * 1000);
    if (breakStart < start || breakEnd > end || breakEnd <= breakStart) {
      throw new Error("زمان استراحت باید داخل همان شیفت باشد.");
    }
  }
  return { start, end, breakStart, breakEnd, durationMinutes };
}

function calculateShiftPremiums({ shifts, hourlyWage, state, premiumRates, extraHolidayDates = [] }) {
  const hourly = finiteNumber(hourlyWage, "دستمزد ساعتی", 0, 100000);
  const rates = {
    night: finiteNumber(premiumRates.night, "درصد شب‌کاری", 0, 300),
    sunday: finiteNumber(premiumRates.sunday, "درصد یکشنبه", 0, 300),
    holiday: finiteNumber(premiumRates.holiday, "درصد تعطیل رسمی", 0, 300),
    specialHoliday: finiteNumber(premiumRates.specialHoliday, "درصد تعطیل خاص", 0, 300)
  };
  const extraDates = Array.isArray(extraHolidayDates) ? extraHolidayDates : [];
  const amount = { night: 0, sunday: 0, holiday: 0, specialHoliday: 0 };
  const taxFree = { night: 0, sunday: 0, holiday: 0, specialHoliday: 0 };
  const svFree = { night: 0, sunday: 0, holiday: 0, specialHoliday: 0 };
  const hours = { worked: 0, night: 0, sunday: 0, holiday: 0, specialHoliday: 0 };
  let shiftCount = 0;

  for (const rawShift of (shifts || [])) {
    const shift = readShift(rawShift);
    shiftCount += 1;
    const dayWork = new Map();
    for (let cursor = new Date(shift.start); cursor < shift.end; cursor = new Date(cursor.getTime() + 60000)) {
      if (shift.breakStart && cursor >= shift.breakStart && cursor < shift.breakEnd) continue;
      const date = new Date(cursor.getFullYear(), cursor.getMonth(), cursor.getDate());
      const key = dateKey(date);
      const hour = cursor.getHours();
      const minuteOfDay = hour * 60 + cursor.getMinutes();
      const previousDate = addDays(date, -1);
      const previousKey = dateKey(previousDate);
      const previousWork = dayWork.get(previousKey);
      const carryNight = hour < 4 && Boolean(previousWork && previousWork.nightWorked);
      const currentHoliday = holidayPremiumKind(date, minuteOfDay, state, extraDates);
      const previousHoliday = carryNight
        ? holidayPremiumKind(previousDate, 23 * 60 + 59, state, extraDates)
        : null;
      const holiday = currentHoliday || (hour < 4 ? previousHoliday : null);

      let day = dayWork.get(key);
      if (!day) {
        day = { worked: false, nightWorked: false };
        dayWork.set(key, day);
      }
      day.worked = true;
      if (hour >= 20 && hour < 24) day.nightWorked = true;

      hours.worked += 1 / 60;
      const isNight = hour >= 20 || hour < 6;
      const isSunday = date.getDay() === 0 || (hour < 4 && carryNight && previousDate.getDay() === 0);
      if (isNight) hours.night += 1 / 60;

      const minuteBase = hourly / 60;
      const addComponent = (name, actualRate, exemptCap) => {
        const paid = minuteBase * actualRate / 100;
        if (paid <= 0) return;
        const taxLimit = minuteBase * Math.min(hourly, 50) * exemptCap / 100 / Math.max(hourly, 1e-12);
        const svLimit = minuteBase * Math.min(hourly, 25) * exemptCap / 100 / Math.max(hourly, 1e-12);
        amount[name] += paid;
        taxFree[name] += Math.min(paid, hourly > 0 ? taxLimit : 0);
        svFree[name] += Math.min(paid, hourly > 0 ? svLimit : 0);
      };

      if (isNight) {
        const nightCap = hour < 4 && carryNight ? 40 : 25;
        addComponent("night", rates.night, nightCap);
      }
      if (holiday) {
        if (holiday.kind === "specialHoliday") {
          hours.specialHoliday += 1 / 60;
          addComponent("specialHoliday", rates.specialHoliday, holiday.cap);
        } else {
          hours.holiday += 1 / 60;
          addComponent("holiday", rates.holiday, holiday.cap);
        }
      } else if (isSunday) {
        hours.sunday += 1 / 60;
        addComponent("sunday", rates.sunday, 50);
      }
    }
  }

  const total = keys => keys.reduce((sum, key) => sum + amount[key], 0);
  const totalTaxFree = Object.values(taxFree).reduce((sum, n) => sum + n, 0);
  const totalSvFree = Object.values(svFree).reduce((sum, n) => sum + n, 0);
  const totalPremium = Object.values(amount).reduce((sum, n) => sum + n, 0);
  const roundObject = obj => Object.fromEntries(Object.entries(obj).map(([k, v]) => [k, roundMoney(v)]));
  return {
    shiftCount,
    hours: roundObject(hours),
    amount: roundObject(amount),
    taxFree: roundMoney(totalTaxFree),
    svFree: roundMoney(totalSvFree),
    total: roundMoney(totalPremium),
    taxable: roundMoney(Math.max(0, totalPremium - totalTaxFree)),
    socialInsuranceBaseAddition: roundMoney(Math.max(0, totalPremium - totalSvFree))
  };
}

function calculatePayroll(input) {
  const monthlyGross = finiteNumber(input.monthlyGross, "حقوق ناخالص ماهانه", 0, 100000000);
  const weeklyHours = finiteNumber(input.weeklyHours, "ساعات هفتگی", 1, 60);
  const additionalRate = finiteNumber(input.gkvAdditionalRate, "Zusatzbeitrag Krankenkasse", 0, 10);
  const childrenUnder25 = Math.floor(finiteNumber(input.childrenUnder25 || 0, "تعداد فرزندان زیر ۲۵ سال", 0, 5));
  const childless23 = Boolean(input.childless23) && childrenUnder25 === 0;
  const state = String(input.state || "NW");
  const monthlyHours = weeklyHours * 52 / 12;
  const hourlyWage = monthlyGross / monthlyHours;

  const shifts = calculateShiftPremiums({
    shifts: input.shifts || [],
    hourlyWage,
    state,
    premiumRates: input.premiumRates || { night: 0, sunday: 0, holiday: 0, specialHoliday: 0 },
    extraHolidayDates: input.extraHolidayDates || []
  });

  const gross = roundMoney(monthlyGross + shifts.total);
  const socialInsuranceBase = roundMoney(Math.max(0, gross - shifts.svFree));
  const healthBase = Math.min(socialInsuranceBase, RULES_2026.gkvAssessmentCeilingMonthly);
  const careBase = healthBase;
  const pensionBase = Math.min(socialInsuranceBase, RULES_2026.pensionAssessmentCeilingMonthly);
  const unemploymentBase = pensionBase;

  const healthTotalRate = RULES_2026.gkvGeneralRate + additionalRate;
  const healthEmployee = roundMoney(healthBase * healthTotalRate / 200);
  const healthEmployer = roundMoney(healthBase * healthTotalRate / 200);

  const saxony = state === "SN";
  const careEmployeeBaseRate = saxony ? 2.3 : 1.8;
  const careEmployeeRate = Math.max(
    0,
    careEmployeeBaseRate + (childless23 ? 0.6 : 0) - Math.max(0, childrenUnder25 - 1) * 0.25
  );
  const careEmployerRate = saxony ? 1.3 : 1.8;
  const careEmployee = roundMoney(careBase * careEmployeeRate / 100);
  const careEmployer = roundMoney(careBase * careEmployerRate / 100);

  const pensionEmployee = roundMoney(pensionBase * 9.3 / 100);
  const pensionEmployer = roundMoney(pensionBase * 9.3 / 100);
  const unemploymentEmployee = roundMoney(unemploymentBase * 1.3 / 100);
  const unemploymentEmployer = roundMoney(unemploymentBase * 1.3 / 100);

  const employeeSocial = roundMoney(healthEmployee + careEmployee + pensionEmployee + unemploymentEmployee);
  const employerSocial = roundMoney(healthEmployer + careEmployer + pensionEmployer + unemploymentEmployer);
  const wageTax = roundMoney(finiteNumber(input.wageTax || 0, "Lohnsteuer", 0, 100000000));
  const solidarityTax = roundMoney(finiteNumber(input.solidarityTax || 0, "Solidaritätszuschlag", 0, 100000000));
  const churchTax = roundMoney(finiteNumber(input.churchTax || 0, "Kirchensteuer", 0, 100000000));
  const advance = roundMoney(finiteNumber(input.advance || 0, "پیش‌پرداخت", 0, 100000000));
  const deductions = roundMoney(employeeSocial + wageTax + solidarityTax + churchTax + advance);
  const net = roundMoney(gross - deductions);

  return {
    year: RULES_2026.year,
    monthlyGross: roundMoney(monthlyGross),
    weeklyHours: roundMoney(weeklyHours),
    hourlyWage: roundMoney(hourlyWage),
    shifts,
    gross,
    socialInsuranceBase,
    healthBase: roundMoney(healthBase),
    pensionBase: roundMoney(pensionBase),
    rates: {
      healthTotal: healthTotalRate,
      healthEmployee: healthTotalRate / 2,
      careEmployee: careEmployeeRate,
      careEmployer: careEmployerRate,
      pension: 18.6,
      unemployment: 2.6
    },
    employee: {
      health: healthEmployee,
      care: careEmployee,
      pension: pensionEmployee,
      unemployment: unemploymentEmployee,
      socialTotal: employeeSocial,
      wageTax,
      solidarityTax,
      churchTax,
      advance
    },
    employer: {
      health: healthEmployer,
      care: careEmployer,
      pension: pensionEmployer,
      unemployment: unemploymentEmployer,
      socialTotal: employerSocial
    },
    deductions,
    net
  };
}

const api = {
  RULES_2026,
  roundMoney,
  easterSunday,
  holidayName,
  calculateShiftPremiums,
  calculatePayroll
};

if (typeof module !== "undefined" && module.exports) module.exports = api;
if (typeof globalThis !== "undefined") globalThis.SteuerPilotPayroll = api;

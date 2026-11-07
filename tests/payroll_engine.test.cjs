"use strict";

const test = require("node:test");
const assert = require("node:assert/strict");
const payroll = require("../payroll_engine.js");

function base(overrides = {}) {
  return {
    monthlyGross: 3000,
    weeklyHours: 40,
    state: "NW",
    gkvAdditionalRate: 2.9,
    childrenUnder25: 0,
    childless23: true,
    premiumRates: { night: 0, sunday: 0, holiday: 0, specialHoliday: 0 },
    shifts: [],
    wageTax: 0,
    solidarityTax: 0,
    churchTax: 0,
    advance: 0,
    ...overrides
  };
}

test("2026 standard statutory insurance splits health and pension contributions", () => {
  const result = payroll.calculatePayroll(base());
  assert.equal(result.employee.health, 262.5);
  assert.equal(result.employer.health, 262.5);
  assert.equal(result.employee.pension, 279);
  assert.equal(result.employer.pension, 279);
  assert.equal(result.employee.unemployment, 39);
  assert.equal(result.employer.unemployment, 39);
  assert.equal(result.employee.care, 72);
  assert.equal(result.employer.care, 54);
});

test("care insurance child reduction applies from the second child under 25", () => {
  const result = payroll.calculatePayroll(base({ childrenUnder25: 2, childless23: false }));
  assert.equal(result.employee.care, 46.5);
  assert.equal(result.employer.care, 54);
});

test("Saxony applies the different employee and employer care shares", () => {
  const result = payroll.calculatePayroll(base({ state: "SN", childrenUnder25: 0, childless23: true }));
  assert.equal(result.employee.care, 87);
  assert.equal(result.employer.care, 39);
});

test("monthly contribution assessment ceilings are applied", () => {
  const result = payroll.calculatePayroll(base({ monthlyGross: 10000, childless23: false }));
  assert.equal(result.healthBase, 5812.5);
  assert.equal(result.pensionBase, 8450);
  assert.equal(result.employee.health, 508.59);
  assert.equal(result.employee.pension, 785.85);
});

test("overnight Sunday shift counts Sunday carry-over hours and calculates both premiums", () => {
  const result = payroll.calculatePayroll(base({
    monthlyGross: 3466.6667,
    premiumRates: { night: 25, sunday: 50, holiday: 125, specialHoliday: 150 },
    shifts: [{ date: "2026-11-08", start: "22:00", end: "04:00" }]
  }));
  assert.equal(result.shifts.hours.worked, 6);
  assert.equal(result.shifts.hours.night, 6);
  assert.equal(result.shifts.hours.sunday, 6);
  assert.equal(result.shifts.amount.night, 30);
  assert.equal(result.shifts.amount.sunday, 60);
  assert.equal(result.shifts.total, 90);
  assert.equal(result.shifts.taxFree, 90);
  assert.equal(result.shifts.svFree, 90);
});

test("special public holiday and night premiums are calculated separately", () => {
  const result = payroll.calculatePayroll(base({
    monthlyGross: 3466.6667,
    premiumRates: { night: 25, sunday: 50, holiday: 125, specialHoliday: 150 },
    shifts: [{ date: "2026-05-01", start: "22:00", end: "23:00" }]
  }));
  assert.equal(result.shifts.amount.night, 5);
  assert.equal(result.shifts.amount.specialHoliday, 30);
  assert.equal(result.shifts.total, 35);
});

test("holiday calendar uses the selected federal state", () => {
  assert.equal(payroll.holidayName(new Date(2026, 5, 4), "NW"), "Fronleichnam");
  assert.equal(payroll.holidayName(new Date(2026, 5, 4), "BE"), null);
  assert.equal(payroll.holidayName(new Date(2026, 2, 8), "BE"), "Internationaler Frauentag");
  assert.equal(payroll.holidayName(new Date(2026, 10, 18), "SN"), "Buß- und Bettag");
});

test("local holiday dates can be added for municipality-specific holidays", () => {
  assert.equal(payroll.holidayName(new Date(2026, 7, 8), "BY", ["2026-08-08"]), "Lokaler gesetzlicher Feiertag");
});

test("only the premium part based on a 25 euro hourly base is social-insurance-free", () => {
  const result = payroll.calculatePayroll(base({
    monthlyGross: 6933.333333,
    premiumRates: { night: 25, sunday: 0, holiday: 0, specialHoliday: 0 },
    shifts: [{ date: "2026-11-02", start: "21:00", end: "22:00" }]
  }));
  assert.equal(result.shifts.total, 10);
  assert.equal(result.shifts.taxFree, 10);
  assert.equal(result.shifts.svFree, 6.25);
  assert.equal(result.socialInsuranceBase, 6937.08);
});

test("break time is excluded from paid shift hours", () => {
  const result = payroll.calculatePayroll(base({
    monthlyGross: 3466.6667,
    premiumRates: { night: 25, sunday: 0, holiday: 0, specialHoliday: 0 },
    shifts: [{ date: "2026-11-02", start: "20:00", end: "23:00", breakStart: "21:00", breakEnd: "22:00" }]
  }));
  assert.equal(result.shifts.hours.worked, 2);
  assert.equal(result.shifts.hours.night, 2);
  assert.equal(result.shifts.amount.night, 10);
});

test("invalid or overlong shifts are rejected", () => {
  assert.throws(() => payroll.calculateShiftPremiums({
    shifts: [{ date: "2026-11-02", start: "06:00", end: "23:00" }],
    hourlyWage: 20, state: "NW",
    premiumRates: { night: 0, sunday: 0, holiday: 0, specialHoliday: 0 }
  }), /۱۶ ساعت/);
});

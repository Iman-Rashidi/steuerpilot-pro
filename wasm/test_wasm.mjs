import assert from "node:assert/strict";
import { copyFile, readFile, rm } from "node:fs/promises";
import { fileURLToPath } from "node:url";
import path from "node:path";

const here = path.dirname(fileURLToPath(import.meta.url));
const staticDir = path.join(here, "..", "static");
const jsPath = path.join(staticDir, "steuerpilot_payroll_wasm.js");
const mjsPath = path.join(staticDir, "steuerpilot_payroll_wasm.test.mjs");
const wasmPath = path.join(staticDir, "steuerpilot_payroll_wasm_bg.wasm");
const xmlPath = path.join(here, "..", "data", "bmf", "Lohnsteuer2026.xml");

await copyFile(jsPath, mjsPath);
try {
  const wasmModule = await import(mjsPath);
  const bytes = await readFile(wasmPath);
  const xml = await readFile(xmlPath, "utf8");
  await wasmModule.default(bytes);
  const engine = new wasmModule.PayrollTaxEngine(xml);
  assert.equal(engine.name, "Lohnsteuer2026");

  const yearlyNames = ["LZZ", "STKL", "RE4", "KVZ", "PVZ", "PVS", "PVA", "KRV", "ALV", "PKV", "R"];
  for (const [taxClass, expected] of [["1", "681900"], ["3", "283400"], ["5", "1205200"]]) {
    const yearlyValues = ["1", taxClass, "5000000", "2.5", "1", "0", "0", "0", "0", "0", "0"];
    const result = JSON.parse(engine.run(yearlyNames, yearlyValues));
    assert.equal(result.LSTLZZ, expected, `2026 annual tax class ${taxClass}`);
    assert.ok(Number.isInteger(Number(result.SOLZLZZ)), "Soli output must be integer cents");
  }

  const monthlyNames = [...yearlyNames, "ZKF", "LZZFREIB", "LZZHINZU", "af", "f"];
  const monthlyValues = ["2", "1", "300000", "2.9", "1", "0", "0", "0", "0", "0", "0", "0", "0", "0", "0", "1.000"];
  const monthly = JSON.parse(engine.run(monthlyNames, monthlyValues));
  for (const key of ["LSTLZZ", "SOLZLZZ", "BK"]) {
    assert.ok(Number.isSafeInteger(Number(monthly[key])), `monthly ${key} must be integer cents`);
    assert.ok(Number(monthly[key]) >= 0, `monthly ${key} must not be negative`);
  }
  assert.ok(Number(monthly.LSTLZZ) > 0, "monthly 3,000 EUR reference case must withhold wage tax");
  console.log("BMF 2026 WASM runtime checks passed: classes I/III/V and monthly class I.");
} finally {
  await rm(mjsPath, { force: true });
}

// SPDX-License-Identifier: LicenseRef-RIGGED-NC-Research-1.0
import { describe, expect, it } from "vitest";
import { readFileSync } from "node:fs";
import { ResultsError, validateResults } from "./results";

const good = () => JSON.parse(readFileSync("public/data/results.json", "utf8"));

describe("validateResults", () => {
  it("accepts the exported results file", () => {
    expect(validateResults(good()).experiments.length).toBeGreaterThan(0);
  });
  it("rejects a wrong schema name", () => {
    expect(() => validateResults({ ...good(), schema: "other" })).toThrow(ResultsError);
  });
  it("rejects an unsupported major version", () => {
    expect(() => validateResults({ ...good(), schema_version: "2.0.0" })).toThrow(ResultsError);
  });
  it("rejects a missing estimate", () => {
    const r = good();
    delete r.experiments[0].estimates?.[0]?.estimate;
    if (r.experiments[0].estimates.length === 0) r.experiments[0].title = 7;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a non-finite number", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: "NaN", ci_low: null, ci_high: null, ci_level: null, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a half-open interval", () => {
    const r = good();
    r.experiments[0].estimates = [{ label: "x", estimate: 1, ci_low: 0, ci_high: null, ci_level: 0.95, unit: "" }];
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects a malformed source hash", () => {
    expect(() => validateResults({ ...good(), sources: [{ path: "a", sha256: "zz" }] })).toThrow(ResultsError);
  });
  it("rejects a missing explorer", () => {
    const r = good();
    delete r.explorer;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an explorer with a missing cell", () => {
    const r = good();
    r.explorer.cells.pop();
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an explorer value outside its interval", () => {
    const r = good();
    r.explorer.cells[0].policies[0].gaps.eog.estimate = 99;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects policies out of order", () => {
    const r = good();
    r.real_score.cells[0].policies.reverse();
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("rejects an estimate without the manuscript text", () => {
    const r = good();
    r.experiments[0].estimates[0].display = null;
    expect(() => validateResults(r)).toThrow(ResultsError);
  });
  it("carries every registered experiment and the exploratory checks", () => {
    const ids = validateResults(good()).experiments.map((e) => e.id);
    expect(ids).toEqual(["EXP-001", "EXP-002", "EXP-003", "EXP-004", "JRN-0014", "JRN-0015", "JRN-0016"]);
  });
});

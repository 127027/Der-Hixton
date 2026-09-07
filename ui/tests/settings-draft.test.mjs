import assert from "node:assert/strict";
import { test } from "node:test";
import { readFileSync } from "node:fs";
import ts from "typescript";

// Compile just the dependency-free model in memory; no test build directory or new starter.
const source = readFileSync(new URL("../src/settings-draft.ts", import.meta.url), "utf8");
const compiled = ts.transpileModule(source, { compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 } }).outputText;
const { SettingsDraft } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString("base64")}`);

test("Binance key fields stay discoverable while locked and trial controls are explicit", () => {
  const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
  const live = readFileSync(new URL("../src/live-preparation.ts", import.meta.url), "utf8");
  assert.match(html, /<fieldset id="live-protected" class="live-controls" disabled>/);
  assert.doesNotMatch(html, /id="live-protected" class="hidden/);
  for (const id of ["live-api-key", "live-api-secret", "live-trial-start", "live-trial-off", "live-plan"])
    assert.ok(html.includes(`id="${id}"`));
  assert.match(live, /\.disabled = !status\.authenticated/);
  assert.match(live, /notional_usdt: "50\.00"/);
  assert.doesNotMatch(live, /(?:localStorage|sessionStorage)\s*[.(]/);
});

test("polling cannot overwrite an edited form even after blur or cancelled save", () => {
  const draft = new SettingsDraft();
  assert.equal(draft.acceptsPolling, true);
  draft.edit();
  for (let poll = 0; poll < 10; poll++) assert.equal(draft.acceptsPolling, false);
  assert.equal(draft.beginSave(), true);
  assert.equal(draft.beginSave(), false);
  draft.finishSave(false);
  assert.equal(draft.dirty, true);
  assert.equal(draft.acceptsPolling, false);
});

test("save blocks polling and discard until response is confirmed", () => {
  const draft = new SettingsDraft();
  draft.edit(); draft.beginSave(); draft.discard();
  assert.equal(draft.dirty, true);
  assert.equal(draft.acceptsPolling, false);
  draft.finishSave(true);
  assert.equal(draft.acceptsPolling, true);
  draft.edit(); draft.discard();
  assert.equal(draft.acceptsPolling, true);
});

test("confirmations work without native browser prompt/confirm support", () => {
  for (const file of ["main.ts", "live-preparation.ts"]) {
    const source = readFileSync(new URL(`../src/${file}`, import.meta.url), "utf8");
    assert.doesNotMatch(source, /window\.(prompt|confirm|alert)\s*\(/);
  }
  const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
  assert.match(html, /id="settings-confirmation"/);
  assert.match(html, /id="live-confirmation"/);
});

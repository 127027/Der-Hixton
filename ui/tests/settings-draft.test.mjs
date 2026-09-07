import assert from "node:assert/strict";
import { test } from "node:test";
import { readFileSync } from "node:fs";
import ts from "typescript";

// Compile just the dependency-free model in memory; no test build directory or new starter.
const source = readFileSync(new URL("../src/settings-draft.ts", import.meta.url), "utf8");
const compiled = ts.transpileModule(source, { compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 } }).outputText;
const { SettingsDraft, describeLivePlan, settingsProblem } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString("base64")}`);

test("Binance key fields stay discoverable while locked and trial controls are explicit", () => {
  const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
  const live = readFileSync(new URL("../src/live-preparation.ts", import.meta.url), "utf8");
  assert.match(html, /<fieldset id="live-protected" class="live-controls" disabled>/);
  assert.doesNotMatch(html, /id="live-protected" class="hidden/);
  for (const id of ["live-api-key", "live-api-secret", "live-trial-start", "live-off", "live-plan"])
    assert.ok(html.includes(`id="${id}"`));
  assert.match(live, /\.disabled = !status\.authenticated/);
  assert.match(live, /notional_usdt: "50\.00"/);
  assert.doesNotMatch(live, /(?:localStorage|sessionStorage)\s*[.(]/);
});

const limits = {max_slots: 3, max_position_budget_usdt: "240.00"};
const saved = {slot_count: 3, target_notional_usdt: "80.00", emergency_stop: false};
const edited = {slot_count: 1, target_notional_usdt: "50.00", emergency_stop: false};

test("one shared preview distinguishes an unsaved draft from active saved values", () => {
  const preview = describeLivePlan(saved, edited, true, false, limits);
  assert.match(preview, /Gemeinsam gespeichert: 3 × 80,00 USDT/);
  assert.match(preview, /Ungespeicherter Entwurf: 1 × 50,00 USDT/);
  assert.match(preview, /Live an ist mit ungespeicherten Änderungen blockiert/);
  assert.match(describeLivePlan(saved, edited, true, true, limits), /Wird gespeichert: 1 × 50,00/);
  const applied = describeLivePlan(edited, edited, false, false, limits);
  assert.match(applied, /Gemeinsam gespeichert: 1 × 50,00 USDT/);
  assert.doesNotMatch(applied, /3 × 80|Ungespeicherter/);
  const discarded = describeLivePlan(saved, saved, false, false, limits);
  assert.match(discarded, /Gemeinsam gespeichert: 3 × 80,00/);
  assert.match(describeLivePlan(null, edited, true, false, null), /Keine Live-Freigabe/);
});

test("server supplied limits explain invalid drafts without pretending they were saved", () => {
  for (const slot_count of [4, 5, 0, 1.5]) {
    const draft = {...saved, slot_count};
    assert.match(settingsProblem(draft, limits), /1 bis 3 Slots/);
    assert.match(describeLivePlan(saved, draft, true, false, limits), /Entwurf kann nicht übernommen/);
  }
  assert.match(settingsProblem({...saved, target_notional_usdt:"100"}, limits), /240,00 USDT/);
  for (const target_notional_usdt of ["NaN", "Infinity", "-5", ""])
    assert.match(settingsProblem({...saved, target_notional_usdt}, limits), /positive, endliche/);
  assert.equal(settingsProblem(edited, limits), null);
  assert.equal(settingsProblem({...saved, slot_count: 5}, {max_slots:5, max_position_budget_usdt:"400"}), null);
});

test("settings have one UI writer, one save route and one real-entry off button", () => {
  const html = readFileSync(new URL("../index.html", import.meta.url), "utf8");
  const main = readFileSync(new URL("../src/main.ts", import.meta.url), "utf8");
  const live = readFileSync(new URL("../src/live-preparation.ts", import.meta.url), "utf8");
  assert.equal((html.match(/id="slot-input"/g) ?? []).length, 1);
  assert.equal((html.match(/id="live-plan"/g) ?? []).length, 1);
  assert.doesNotMatch(html, /Paper-Einstellungen|id="live-trial-off"|Not-Aus:|3×80 und später 750/);
  assert.match(main, /"\/api\/trading\/settings"/);
  assert.doesNotMatch(live, /element\("live-plan"\)/);
  assert.equal((live.match(/const blocker = sharedSettingsBlocker\(\)/g) ?? []).length, 2);
  assert.match(html, /echten Marktdaten in Echtzeit/);
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

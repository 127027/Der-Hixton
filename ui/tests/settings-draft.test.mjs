import assert from "node:assert/strict";
import { test } from "node:test";
import { readFileSync } from "node:fs";
import ts from "typescript";

// Compile just the dependency-free model in memory; no test build directory or new starter.
const source = readFileSync(new URL("../src/settings-draft.ts", import.meta.url), "utf8");
const compiled = ts.transpileModule(source, { compilerOptions: { target: ts.ScriptTarget.ES2022, module: ts.ModuleKind.ES2022 } }).outputText;
const { SettingsDraft } = await import(`data:text/javascript;base64,${Buffer.from(compiled).toString("base64")}`);

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

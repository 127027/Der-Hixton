# Hixton Codex Supervisor Rules

This repository contains a cryptocurrency trading bot. Treat correctness, reproducibility, and live-trading safety as release blockers.

## Mission

Repair the current branch until the deterministic quality gates pass without weakening tests or safety controls.

## Mandatory workflow

1. Read `.agent/qa-summary.txt` and only the failing logs under `.agent/qa-logs/` first.
2. Reproduce each failure before changing code when practical.
3. Inspect only the files relevant to the failure; do not load the whole repository unless necessary.
4. Make the smallest correct fix.
5. Re-run the narrowest relevant test/check immediately.
6. Continue fixing and retesting in the same run while failures remain.
7. Before finishing, run `bash scripts/qa_gate.sh` once more.
8. Do not claim readiness unless `QUALITY_GATE=PASS`.

## Forbidden shortcuts

Do not:
- delete, skip, xfail, quarantine, or loosen tests merely to obtain green CI;
- reduce ruff/mypy/pytest coverage or disable checks;
- modify `.github/workflows/codex-supervisor.yml`, `scripts/qa_gate.sh`, or this file to evade a failure;
- introduce broad exception swallowing, fake return values, hard-coded test fixtures in production code, or other test-specific bypasses;
- expose API keys, credentials, account data, or secrets;
- send live Binance orders or enable live trading as part of QA;
- change trading strategy semantics unless a failing test/specification requires it and the change is narrowly justified.

## Trading safety

All automated validation must remain offline, mocked, paper, replay, or testnet-safe. Never perform an Echtgeld order. Existing deterministic risk and execution guards remain authoritative.

## Scope discipline

Prefer source fixes under `src/` and UI fixes under `ui/src/`. Tests may be added when they reproduce a real defect, but existing tests must not be weakened. Preserve DMS requirements unless resolving a proven documentation/code inconsistency requires an explicit follow-up rather than silently changing the specification.

## Completion report

At the end, summarize:
- root cause(s),
- files changed,
- tests/checks run,
- remaining blockers,
- final `QUALITY_GATE` state.

---
name: mcare-auto-test
description: Use when a tester asks Copilot to run test scenarios or testcases written in natural language (English or Vietnamese) against the MCare21 DEV or SIT environment — e.g. "run the scenarios in this file", "run these test cases on SIT", "chạy kịch bản", "chạy test case trên DEV", "auto test", "mở màn SIT check...", "vào DEV bấm thử...", "test giao diện trên SIT/DEV". Drives the browser through the Playwright MCP server (tool calls, not scripts); assumes the MCP server is NOT configured yet and walks through setup from scratch. Also explains how a non-technical tester should write the scenario file. Only DEV and SIT — refuses any other environment.
---

# MCare21 — Auto Test for Testers (DEV / SIT)

Who uses this: **testers, not developers**. They write a scenario file in plain English or
Vietnamese — no code, no selectors — and ask Copilot to run it on DEV or SIT. Everything you
say back to them should be understandable without technical background, and in the language
they wrote in.

How it runs: through the **Playwright MCP server** — you call tools like `browser_navigate`,
`browser_click`, `browser_snapshot` directly. No scripts to write, no browser lifecycle to
manage; the same live browser stays open for the whole conversation.

Scope: **DEV and SIT only.** Any other environment is refused (`references/safety-rules.md`).

---

## 0. One-time setup (skip if already done)

Look at the tools available to you right now. If any `browser_navigate` / `browser_snapshot`
style tool is already listed (with or without a prefix such as `mcp_playwright_`), a Playwright
MCP server is already wired up — possibly at VS Code user level, not in this workspace — and
setup is done; don't add a second one. Only if no browser tools exist, follow
`references/mcp-setup.md` end to end: it runs a preflight (VS Code and Copilot versions, Node,
npm registry reachability, which browser is installed) with a concrete fix for each failure,
writes or merges `.vscode/mcp.json` yourself, has the tester do the one click Copilot can't
(start the server), and ends with a smoke test that the browser can actually reach MCare21
(VPN). Do the checks in its order and stop at the first failure — report each one in words a
non-technical tester can act on.

If MCP tools aren't available at all in this Copilot install (older VS Code / Copilot Chat
version), say so — don't fall back to writing raw Playwright scripts instead. Ask the tester
to update Copilot Chat, since a hand-rolled fallback defeats the purpose of this skill.

---

## 1. Running a scenario file (the normal path)

The tester points at a Markdown file of testcases ("run the scenarios in X.md", "chạy kịch bản
trong file X"). Read `references/scenario-format.md` first — it's what the tester was told the
format means — then `references/batch-testcases.md` for how to parse it, run it, and report.

The non-negotiables, in order:

1. **Confirm environments before touching anything.** Read back what you parsed per testcase
   ("TC01 → SIT, TC02 → DEV, TC03 → not stated") and wait for the tester to confirm or correct
   — one confirmation for the whole file, even when every testcase already states one. Testers
   verify real environments; a run that quietly used the wrong one produces a report that looks
   fine but checked nothing.
2. **Detect the login state, don't assume it.** The MCP browser has its own profile — it doesn't
   see the tester's everyday browser, and on a fresh machine it starts logged out. Follow
   `references/login-flow.md`: navigate, snapshot, act on what you see. MSAL sign-in itself is
   done by the tester in the MCP browser window (once per machine); you never type credentials
   or pick an account for them.
3. **Run each testcase as its own unit**, translating steps with
   `references/actions-cheatsheet.md` and screens with `references/routes-selectors.md`. Use
   `browser_snapshot` whenever you're not sure an action landed.
4. **Verdicts are PASS / FAIL / BLOCKED / EXECUTED** as defined in `batch-testcases.md`. A
   blocked step is not a failed app; a testcase with no Expected line is EXECUTED, never PASS.
5. **Report** the table in chat (with counts) and write it to `.outputs/playwright-artifacts/`,
   with a screenshot per testcase as evidence.

---

## 2. A single ad-hoc request

Sometimes the tester just types one thing ("check the Stock Master screen on SIT opens", "vào
DEV mở màn Braden xem có data không"). Treat it as a one-testcase scenario: confirm the
environment, detect login state, run the steps, and report what was actually observed (a count,
a text, a URL — not "looks fine") with a verdict if the request contained an expectation.

---

## 3. Safety

Every run follows `references/safety-rules.md`: DEV/SIT only; write data only when a step says
so and only on records the run created; capture evidence before cleanup; leave the screen clean;
screenshots and reports in `.outputs/playwright-artifacts/`.

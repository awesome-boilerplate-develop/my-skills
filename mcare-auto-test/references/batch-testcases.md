# Running a batch of testcases from a file

When the user points to a file of natural-language testcases instead of describing one action
inline (e.g. "chạy hết testcase trong file này", "run these test cases on SIT"), treat the file
as the input and produce one report at the end.

## Reading the file

The tester writes the file following `scenario-format.md` (that file is written for them —
read it too, so you know what they were told the format means). Parsing rules:

- Each `##` heading is one testcase; its id is whatever short token comes before the colon
  (`TC01`, `TC02`, ...) — if the tester didn't include one, number them in file order.
- A bullet starting with `Kỳ vọng:` / `Expected:` is the pass criterion. A testcase without
  one has nothing to verify against, so it can only be reported as EXECUTED, never PASS (see
  "Verdicts"). If a step reads like a check ("kiểm tra xem ... không") but no expectation line
  exists, treat the check itself as the expectation and say so in the report.
- A bullet starting with `Dọn dẹp:` / `Cleanup:` runs last, after evidence is captured
  (`safety-rules.md` rule 3). If it's missing but the steps wrote data, warn the tester in the
  report — don't invent a cleanup.
- Pull the environment (DEV/SIT) from the heading (usually in parentheses at the end) or the
  first bullet, for **each** testcase individually — testcases in the same file may target
  different environments. Any other environment name → refuse that testcase
  (`safety-rules.md` rule 1).
- **Environment is a required parameter — always confirm with the user before running
  anything, even if every testcase already states one.** This file is written by testers, and
  silently running against whatever the file says (correct or not) risks verifying the wrong
  environment without anyone noticing. Read back what you parsed per testcase (e.g. "TC01→SIT,
  TC02→DEV, TC03→ (not stated)") as a single summary and have the user confirm or correct it —
  one confirmation for the whole batch, not one question per testcase.
- The bullets under each heading are free text — read them the same way you'd read one inline
  request, translating each line via `actions-cheatsheet.md`.

## Execution strategy

Work through testcases one at a time in the same MCP browser session — no script, no relaunching
the browser per case. SIT and DEV are different domains with separate sessions, so when a
testcase switches environment, run the state detection in `login-flow.md` again for that
domain — the profile may already hold a valid session there, or may need the tester to sign in
once more.

To keep a failure in one testcase from corrupting the next:

- Treat each testcase's steps as its own unit — if a tool call fails or a `browser_snapshot`
  shows something unexpected partway through a testcase, stop that testcase, record what went
  wrong, and move to the next one. Don't let one bad case abort the whole run.
- Before starting each testcase, `browser_navigate` to a known-good starting route (e.g.
  `#/MYS/dashboard`) rather than assuming the previous testcase left the UI in a clean state.
- Reset any state a testcase might leave behind that could bleed into the next one — clear search
  chips, close dialogs — same as `safety-rules.md`, just applied after every testcase instead of
  only at the very end.

## Verdicts

A business result and an execution problem are different things — a report that says FAIL
when the session merely expired sends a tester chasing a bug that doesn't exist. Four primary
verdicts, plus SKIPPED for the one situation described after the table:

| Verdict | Use when |
|---|---|
| **PASS** | The testcase has an expectation, every step ran, and the observed result matches it. |
| **FAIL** | Every step ran and the observed result contradicts the expectation. This is the only verdict that means "the app may have a bug". |
| **BLOCKED** | The steps could not be completed for a reason outside the testcase — session expired, Welcome Submit stuck (see `login-flow.md`), screen not reachable, MCP tool error. Say which. |
| **EXECUTED** | All steps ran but the testcase had no expectation to verify against (e.g. "open screen, take screenshot"). Not a pass — just a record that it was done, with evidence. |

Use **SKIPPED** only when the tester asks to skip a case or an earlier BLOCKED case makes it
impossible to reach (say which one). Never invent an expectation to turn EXECUTED into PASS.

Every row also carries **Expected** (verbatim from the file, or "—"), **Actual** (what the
snapshot/evaluate actually showed — a count, a text, a URL, not "looks fine"), and **Evidence**
(the screenshot path). Anything done under a workaround — Welcome bypass, a hospital/department
the tester substituted — goes in Actual, so nobody reads a green row without the caveat.

## Report

After working through every testcase, write a Markdown report to
`.outputs/playwright-artifacts/report-<timestamp>.md`:

```markdown
# Auto-test run — 2026-09-11 15:30 — environments confirmed by tester: SIT, DEV

| ID | Env | Verdict | Expected | Actual | Evidence |
|---|---|---|---|---|---|
| TC01 | SIT | EXECUTED | — | Screen opened, header "Shift Code" visible, search "ABC" returned 3 rows | .outputs/playwright-artifacts/TC01.png |
| TC02 | DEV | PASS | "No Record Found", no data rows | `.table-no-data-row` present, 0 `tr.table-col-row` | .outputs/playwright-artifacts/TC02.png |
| TC03 | DEV | BLOCKED | Add dialog shows required-field errors | Session expired at step 1 — tester re-login needed | .outputs/playwright-artifacts/TC03-login.png |
```

Summarize the same table in the chat reply — don't make the user open the file to see whether
anything failed — and end with the counts (PASS / FAIL / BLOCKED / EXECUTED / SKIPPED) so the
tester can tell at a glance whether any row deserves a bug ticket.

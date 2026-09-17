# Login flow (via MCP tool calls)

MCare21 login goes through MSAL SSO (Microsoft login). Two facts shape everything below:

- **Playwright MCP runs its own browser profile**, not the tester's everyday Chrome/Edge. It
  does not see any session the tester already has open elsewhere. The profile *is* persistent
  on disk, so a login completed once in the MCP browser survives later runs on the same machine
  — but a fresh machine, or a cleared profile, starts logged out.
- **Never type a password yourself and never assume which account is logged in.** The tester
  owns the account; you only detect state and drive the app's own UI.

## 1. Detect the actual state first

`browser_navigate` straight to the **target route** (`${BASE_URL}/#/MYS/...` from
`routes-selectors.md`) — not to `#/login` — then `browser_snapshot`. A valid session lands on
the screen you asked for; an invalid one gets redirected, and the redirect tells you what's
missing:

| Snapshot shows | Meaning | Do |
|---|---|---|
| The target screen (its column headers / title) | Session valid | Skip login entirely. |
| `#/MYS/welcome` | Authenticated, hospital/department not chosen yet | Go to step 3. |
| `-- Select Country --` on `#/login` | No session | Go to step 2. |
| `login.microsoftonline.com` | Mid-SSO | Go to step 2b. |

Repeat this detection whenever a later `browser_snapshot` unexpectedly shows `#/login` —
that's the only reliable signal the session expired. Don't re-run the flow on a hunch.

## 2. First-time login — the tester completes MSAL, you drive the rest

2a. `browser_click` `-- Select Country --` → `browser_click` `Malaysia` → `browser_click`
    **Login**. (SSO redirect can be fast — if the Login button is already gone by the next
    snapshot, you're past this step.)

2b. On `login.microsoftonline.com`: **stop and hand over to the tester.** The MCP browser is a
    visible window — tell them: "Please sign in with your MCare21 account in the browser window
    that just opened (account, password, MFA if prompted; choose **Yes** on 'Stay signed in?'
    so you won't have to repeat this). Tell me when you see the welcome or dashboard screen."
    Then wait. Do not try to pick an account, fill a password, or answer an MFA prompt on
    their behalf. Once done, the persistent profile keeps this session for future runs, so
    this handover normally happens once per machine.

## 3. Welcome screen (`#/MYS/welcome`)

Hospital / Department are usually pre-selected and the agreement checkbox ticked. Ask the tester
which hospital/department the run should use **if the testcase or request names one**; otherwise
`browser_click` **Submit** with the defaults, and record what was selected in the report — the
choice changes which data every later step sees.

### ⚠️ If Submit does nothing

Wait ~5 s and `browser_snapshot` again. If you're still on `#/MYS/welcome`:

1. `browser_take_screenshot` into `.outputs/playwright-artifacts/` as evidence.
2. Mark the login step **BLOCKED** ("Welcome Submit did not navigate") and stop the flow.
   Do **not** conclude login PASSED.
3. Tell the tester a known workaround exists — writing the `welcome-page` entry into
   `sessionStorage` via `browser_evaluate` and setting `location.hash` to the target route —
   and ask whether to apply it. Only apply it on an explicit yes, with the hospital/department
   the tester names (never a silently substituted default), and flag every subsequent result
   in the report as "ran after Welcome bypass". The bypass exists to keep testing other screens
   when Welcome itself is broken; it must never hide that Welcome is broken.

```js
// Only with the tester's explicit go-ahead; substitute their hospital/department.
() => {
  sessionStorage.setItem('welcome-page', JSON.stringify({
    department: '<DEPARTMENT>',
    hospital: '<HOSPITAL NAME>',
    facilityTinNo: null,
  }));
  window.location.hash = '<TARGET_ROUTE>';
}
```

(If it redirects to `antenatal-care-master` on the first try, run the hash assignment a second
time with the real target route.)

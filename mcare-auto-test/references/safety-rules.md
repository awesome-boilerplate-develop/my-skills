# Safety rules

These exist because DEV and SIT are shared by the whole team — other testers, BA, and devs
verify on the same data. A run that leaves junk behind, or touches someone else's records, costs
other people time even when the testcase itself passed.

1. **Only DEV and SIT.** The two domains in `routes-selectors.md` are the only ones this skill
   may drive. If a scenario or request names any other host (production, UAT, a URL you don't
   recognise), stop and say so — don't navigate there at all. Testers own these two
   environments; nothing else is in scope.

2. **Write data only when the scenario says so — and only what it says.** Testers do create,
   edit and delete records; that's normal. What's not allowed is doing it on your own
   initiative:
   - Click Save / Submit / Delete only when a step in the scenario says to. Never "helpfully"
     confirm a dialog the scenario didn't mention.
   - Touch only records the run itself created (the `AT_` prefix in `scenario-format.md`
     marks them). A step that edits or deletes a pre-existing record is a red flag — read it
     back to the tester and confirm before doing it.
   - No bulk actions (select-all + delete, import, reset) unless the scenario spells them out
     and the tester confirms.
   - Validation checks (empty required field, invalid format) are done by entering the bad
     value, blurring, reading the `mat-error`, then **Cancel / X** — never by submitting.

3. **Evidence before cleanup.** Take the screenshot and read the actual result *before* running
   the scenario's `Dọn dẹp:` step, otherwise the evidence shows the cleaned-up state, not the
   thing being tested.

4. **Leave the screen as you found it** at the end of each testcase: search chips cleared,
   dialogs closed, filters reset. The next testcase (or the next person) starts clean.

5. **Screenshots and reports go to `.outputs/playwright-artifacts/`**, never the workspace root.
   Pass the absolute path as `filename` to `browser_take_screenshot`, built from the workspace
   folder's real location — `C:\Users\...\A1H\.outputs\playwright-artifacts\TC01.png` on
   Windows, `/Users/.../A1H/.outputs/playwright-artifacts/TC01.png` on macOS. Don't hand-write
   a path in the other OS's style, and don't pass a bare filename. Name files by testcase id
   (`TC01.png`, `TC03-login.png`) so the report's Evidence column links back unambiguously.

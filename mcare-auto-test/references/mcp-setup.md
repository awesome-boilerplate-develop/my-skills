# Setting up the Playwright MCP server for Copilot

One-time setup per machine/workspace. It wires Copilot Chat to a real browser via the Model
Context Protocol, so you call browser tools instead of writing scripts.

Run the preflight checks **in this order** and stop at the first one that fails — later checks
depend on earlier ones, and each failure has a specific fix the tester can do. Report the
result of each check in plain language; the tester isn't expected to know what any of these
tools are.

**Which OS are you on?** Testers run Windows, macOS, and occasionally Linux, and several
commands below differ. Determine it before the first command — the VS Code terminal's shell is
the quickest tell (PowerShell or cmd prompt means Windows), or run `node -p "process.platform"`
once Node is confirmed (`win32` / `darwin` / `linux`). Then use that column throughout; guessing
wrong makes a working machine look broken.

## 1. Preflight — is anything already working?

Look at your own tools list. If any `browser_navigate` / `browser_snapshot` style tool is there
(with or without a prefix like `mcp_playwright_`), a Playwright MCP server is already configured
— at workspace level or in the tester's VS Code user profile — and running. **Setup is done;
skip to Section 5 (smoke test).** Don't add a second server: two would launch two browsers
fighting over the same tools.

## 2. Preflight — can this machine run the server?

| Check | Windows (PowerShell) | macOS / Linux | Pass when | If it fails |
|---|---|---|---|---|
| VS Code supports MCP | `code --version` | `code --version` | First line is **1.99** or newer | Tester updates VS Code (Help → Check for Updates). MCP tools don't exist in older builds — nothing below will help. |
| Copilot Chat installed | `code --list-extensions \| Select-String copilot` | `code --list-extensions \| grep -i copilot` | Both `github.copilot` and `github.copilot-chat` listed | Tester installs/updates the GitHub Copilot Chat extension from the Extensions view, then reloads VS Code. |
| Node.js present, new enough | `node -v` | `node -v` | **v18** or newer | Tester installs the **LTS** build from <https://nodejs.org> (default options), then **fully restarts VS Code** — on Windows a new terminal alone won't pick up the PATH change. Don't install it for them; it needs their admin rights. |
| npx works | `npx -v` | `npx -v` | Prints a version | Comes with Node. If Node passed but this didn't, the PATH is stale: restart VS Code, and on Windows sign out/in if that isn't enough. |
| npm registry reachable | `npx -y @playwright/mcp@latest --version` | same | Prints a version within ~1 min | Network/proxy problem. Ask whether the company requires a proxy; if so `npm config set proxy <url>` and `npm config set https-proxy <url>` per IT. On VPN-only networks, connect the VPN first. |
| A browser to drive | `Test-Path "$env:ProgramFiles\Google\Chrome\Application\chrome.exe"`, then `Test-Path "${env:ProgramFiles(x86)}\Microsoft\Edge\Application\msedge.exe"` | `ls /Applications \| grep -iE "chrome\|edge"` | Google Chrome **or** Microsoft Edge found | See "Choosing the browser" below. |

### Choosing the browser

Playwright MCP drives the machine's installed **Chrome** by default. What to do with the result
of the last check:

- **Chrome found** → nothing to add; the default works.
- **Only Edge** → add `"--browser", "msedge"` to the args in Section 3. On Windows this is the
  common case, since Edge ships with the OS and Chrome may not be installed.
- **Neither** → run `npx -y playwright install chromium` (downloads ~150 MB, needs the same
  network as the registry check) and add `"--browser", "chromium"`.

Chrome can also be installed per-user on Windows at
`%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe` — check there too before concluding it's
missing.

## 3. Add the workspace config yourself

No tester involvement needed — read and write the file directly:

1. Check whether `.vscode/mcp.json` exists at the workspace root (VS Code's MCP config file; a
   `.mcp.json` at the root, if present, belongs to a different tool — leave it alone).
2. **If it doesn't exist**, create it with:

   ```json
   {
     "servers": {
       "playwright": {
         "command": "npx",
         "args": [
           "-y",
           "@playwright/mcp@latest",
           "--output-dir",
           ".outputs/playwright-artifacts",
           "--output-max-size",
           "268435456"
         ]
       }
     }
   }
   ```

   **On Windows, use `"command": "npx.cmd"` instead of `"npx"`** — VS Code spawns the command
   without a shell, and the bare name resolves only to the `npx` shell script, which Windows
   can't execute directly ("spawn npx ENOENT"). macOS/Linux keep `"npx"`.

   Append `"--browser", "msedge"` or `"--browser", "chromium"` to `args` if the browser check
   in Section 2 said so.

   `--output-dir` matters: the server writes its own artefacts (snapshots, traces, screenshots
   you didn't name) somewhere, and without this flag that somewhere is the workspace root —
   on this project that once silently grew to 63 MB / 1174 files before anyone noticed.
   `--output-max-size` caps it at 256 MB.

3. **If it already exists**, read it first and merge the `playwright` entry under `servers`
   without touching any other server configured there — don't overwrite the whole file.
4. If a `playwright` entry is already there, leave it as is — don't duplicate or reset it.

Keep the `--output-dir` value as the forward-slash relative path shown above on every OS —
VS Code resolves it against the workspace folder, and forward slashes work on Windows too.
Don't rewrite it as a backslash or absolute path.

## 4. Start the server (needs the tester, once)

Copilot can write the config but cannot click VS Code's UI to start the server — ask the tester
to do this one-time step:

- Open the Copilot Chat panel, open the **Tools** picker (the wrench/tools icon), and confirm
  `playwright` shows up as an MCP server.
- If it isn't running, VS Code prompts to start it the first time a tool is used, or they can
  start it from the Command Palette (**Ctrl+Shift+P** on Windows/Linux, **Cmd+Shift+P** on
  macOS) → **MCP: List Servers** → `playwright` → Start.

Once started, browser tools appear in your tools list — names like `browser_navigate`,
`browser_click`, `browser_type`, `browser_snapshot`, `browser_take_screenshot`,
`browser_select_option`, `browser_press_key`, `browser_evaluate`, `browser_wait_for` (some
Copilot versions prefix them; use whatever name actually appears). If nothing appears after the
tester says it started, ask them to open **Output → MCP: playwright** in VS Code and paste the
last lines — the error there says which Section 2 check was wrong. A `spawn npx ENOENT` line on
Windows means the config still says `"npx"` where it needs `"npx.cmd"` (Section 3).

## 5. Smoke test — can the browser actually reach MCare21?

Before running any scenario, `browser_navigate` to `https://sitmcare21.columbiaasia.com` (or
the DEV domain if that's what the tester confirmed) and `browser_snapshot`.

- Country selector or a `#/MYS/...` screen visible → everything works; proceed to
  `login-flow.md`.
- Timeout / "site can't be reached" → the browser launched fine but the machine can't see the
  MCare21 network. Ask the tester to connect the company VPN and retry. This is a network
  problem, not a setup problem — don't reinstall anything.
- No browser window ever opened → the `--browser` choice in Section 3 doesn't match what's
  installed. Re-run the browser check in Section 2.

After the smoke test passes, treat setup as done for the rest of the session — don't re-check.

## Why MCP instead of a hand-written script

- Copilot calls existing tools instead of generating Playwright code from scratch each time —
  no script to get the syntax wrong on.
- The browser session stays open across the whole conversation, so logging in once (see
  `login-flow.md`) carries through every subsequent request without re-authenticating.
- `browser_snapshot` returns the page's accessibility tree, which is usually a more reliable way
  to find an element than guessing a CSS selector cold.

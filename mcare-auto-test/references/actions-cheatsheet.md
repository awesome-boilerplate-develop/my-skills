# Natural language → MCP tool call cheat-sheet

Tool names below are the common Playwright MCP names (`browser_navigate`, `browser_click`, ...).
If this Copilot version prefixes them differently, use whatever actually appears in the tools
list (see `mcp-setup.md`) — same tools, just a different name.

| Natural language (VN / EN) | Action / Strategy | Notes & traps |
|---|---|---|
| "Vào màn / Mở màn [X]"<br>"Open / Navigate to screen [X]" | Resolve route from `routes-selectors.md` → `browser_navigate` to it → `browser_snapshot` and wait for a column header text to appear. | Wait for a specific header (e.g. "Shift Code"), not a generic `table` element. |
| "Bấm nút / Click [Tên nút]"<br>"Click button [Name]" | `browser_snapshot` to find the element ref, then `browser_click` on it. | If a Material ripple animation blocks the click, retry once — MCP clicks usually wait for actionability automatically. |
| "Nhập [Text] vào ô [Label]"<br>"Type [Text] into [Field]" | `browser_snapshot` to find the input, then `browser_type` with the text. | For time-pickers, type slowly / character by character if the field has an input mask (check `browser_snapshot` after typing to confirm it took). |
| "Tìm kiếm / Search [Từ khoá]"<br>"Filter by [Keyword]" | `browser_click` the search/chip input, `browser_type` the keyword, `browser_press_key` `Enter`. | ⚠️ Chip filters silently ignore strings shorter than 3 characters — keyword must be ≥ 3 chars. |
| "Chọn [Option] trong dropdown [Field]"<br>"Select [Option] in [Field]" | `browser_click` the dropdown trigger → `browser_snapshot` to see the opened overlay → `browser_click` the matching option (or `browser_select_option` if it's a native `<select>`). | Click elsewhere on the page if the overlay doesn't auto-close. |
| "Blur ô [Field] / Bấm ra ngoài"<br>"Blur input / trigger validation" | `browser_click` the field, then `browser_click` an adjacent label/heading. | Needed to surface `mat-error` on touched-but-unfocused fields. |
| "Kiểm tra xem có hiển thị [Text] không"<br>"Check if [Text] is visible" | `browser_snapshot` and read the accessibility tree for the text; or `browser_evaluate` to read `innerText` of a specific container. | Also check for `.mat-error` / `.toast-message` text in the snapshot for validation/notification content. |
| "Đếm số dòng / Xem bảng có data không"<br>"Count table rows / check empty" | `browser_evaluate` to count `tr.table-col-row` vs check for `.table-no-data-row`. | An empty table on SIT is common after test-data cleanup — not necessarily a bug. |
| "Chụp ảnh màn hình / Chụp popup"<br>"Take screenshot" | `browser_take_screenshot` with an absolute `filename` path into `.outputs/` (see `safety-rules.md`). | Never pass a bare filename — it may land outside `.outputs/`. Pass the full path explicitly. |
| "Đóng dialog / Huỷ bỏ"<br>"Close dialog / Cancel" | `browser_click` the dialog's `X` close icon; if an "unsaved changes" confirm appears, `browser_click` its **Yes** button. | Use `browser_snapshot` to disambiguate — don't click the first element matching text "Yes" if a table row also contains that word. |

## General tips

- **Prefer `browser_snapshot` over guessing.** It's cheap and returns the actual accessibility
  tree with element refs — use it before any click/type you're not already confident about, and
  after any action whose result you need to verify.
- **`browser_wait_for`** is useful after navigation or a search/filter action, waiting for
  specific text to appear rather than a fixed sleep.
- **`browser_evaluate`** is the escape hatch for anything not covered by a dedicated tool (e.g.
  reading `sessionStorage`, counting rows by class, or the welcome-page bypass in
  `login-flow.md`).

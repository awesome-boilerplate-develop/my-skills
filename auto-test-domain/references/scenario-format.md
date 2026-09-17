# How to write a scenario file (for testers) / Cách viết kịch bản (dành cho tester)

A scenario is a Markdown file written in plain language — **English or Vietnamese, either is
fine, and you can mix them**. No code, no selectors, no technical terms needed. Copilot reads
each line and turns it into browser actions, and replies in whichever language you wrote.

Kịch bản là file Markdown viết bằng lời thường — **tiếng Anh hoặc tiếng Việt đều được, trộn
cũng được**. Không cần code, không cần biết kỹ thuật. Copilot đọc từng dòng, tự thao tác trên
trình duyệt và trả lời bằng ngôn ngữ bạn viết.

## Template / Mẫu

```markdown
## TC01: Fluid Balance Shift — search (SIT)
- Open the Fluid Balance Shift screen
- Search "MORNING" in the table
- Expected: only rows whose Shift Code contains "MORNING" remain

## TC02: Blood Group Master — thêm mới (DEV)
- Mở màn Blood Group Master
- Bấm nút Add
- Nhập "AT_BG_TEST01" vào ô Code
- Nhập "Auto test blood group" vào ô Description
- Bấm Save
- Kỳ vọng: toast báo thành công, bảng có dòng "AT_BG_TEST01"
- Dọn dẹp: xoá dòng "AT_BG_TEST01"

## TC03: Blood Group Master — Code is required (DEV)
- Open the Blood Group Master screen
- Click the Add button
- Click into the Code field, then click outside it
- Expected: the error "Code is required" appears under the Code field
- Close the dialog
```

## Rules / Quy tắc

| Part / Phần | Required? | Notes / Ghi chú |
|---|---|---|
| `## TCxx: <name> (SIT)` or `(DEV)` | Yes | One `##` = one testcase. Put the environment in parentheses at the end of the title. Copilot will still read it back and ask you to confirm before running anything. |
| `- ...` lines | Yes | One action per line, in the order you want it done. |
| `- Expected:` / `- Kỳ vọng:` | Strongly recommended | What you expect to see after the steps. **Without this line the testcase can only be reported as "executed", never PASS** — there is nothing to compare against. |
| `- Cleanup:` / `- Dọn dẹp:` | When the steps write data | How to remove or restore the data the testcase created. Runs after evidence is captured. |

## Phrases Copilot understands / Những câu Copilot hiểu

Write naturally — these are just the patterns that are guaranteed to be recognised, in either
language:

| You write (EN) | Bạn viết (VN) | Copilot does |
|---|---|---|
| Open the X screen / Go to X | Mở màn X / Vào màn X | Navigates to that screen (known screens are listed in `routes-selectors.md`; unknown ones are found through the app menu). |
| Click X / Click the X button | Bấm nút X / Click X | Clicks the button labelled X. |
| Type "abc" into X / Enter "abc" in X | Nhập "abc" vào ô X | Types into the field labelled X. |
| Search "abc" | Tìm kiếm "abc" | Types into the search box and presses Enter. Keyword must be **at least 3 characters** — shorter ones are ignored by the table. |
| Select "X" in the Y dropdown | Chọn "X" trong dropdown Y | Opens dropdown Y and picks X. |
| Click into X, then click outside | Bấm vào ô X rồi bấm ra ngoài | Triggers the field's validation (to see its error message). |
| Check that "abc" is shown | Kiểm tra có hiện "abc" không | Checks whether the text "abc" is on screen. |
| Count the rows in the table | Đếm số dòng trong bảng | Reports the number of data rows. |
| Take a screenshot / Screenshot the popup | Chụp ảnh / Chụp popup | Saves an image as evidence. |
| Close the dialog / Cancel | Đóng dialog / Huỷ | Closes the open dialog. |

## Test data / Dữ liệu test

- Prefix anything you create with **`AT_`** (e.g. `AT_BG_TEST01`) so anyone can tell it is
  auto-test data and clean it up.
  Đặt tiền tố **`AT_`** cho dữ liệu bạn tạo để ai cũng nhận ra và dọn được.
- If a testcase creates, edits or deletes data, always add a `Cleanup:` / `Dọn dẹp:` line.
  Copilot will **not** delete or change anything beyond the steps you wrote.
  Có ghi dữ liệu thì luôn kèm dòng dọn dẹp. Copilot **không** tự xoá/sửa gì ngoài các bước bạn viết.
- Only use data your own scenario created. Don't write steps that edit or delete someone
  else's existing records on DEV/SIT — the environments are shared.
  Chỉ dùng dữ liệu bạn tự tạo; đừng sửa/xoá bản ghi có sẵn của người khác.

## Running / Chạy

In Copilot Chat:

```text
#auto-test-domain run the scenarios in <path-to-file>.md
#auto-test-domain chạy kịch bản trong file <đường-dẫn-file>.md
```

Copilot reads back the environment of each testcase for you to confirm, runs them one by one,
and returns a results table with screenshots. Result meanings (details in "Verdicts",
`batch-testcases.md`): **PASS / FAIL** = compared against your Expected line; **BLOCKED** = the
steps couldn't be completed (login expired, screen unreachable...) — not an application bug;
**EXECUTED** = all steps done but there was no Expected line to compare with.

Copilot đọc lại môi trường từng testcase để bạn xác nhận, chạy lần lượt, rồi trả về bảng kết quả
kèm ảnh. **PASS / FAIL** = so được với Kỳ vọng; **BLOCKED** = không chạy tới nơi (hết phiên đăng
nhập, màn không mở được...) — không phải lỗi ứng dụng; **EXECUTED** = đã làm hết các bước nhưng
không có Kỳ vọng để so.

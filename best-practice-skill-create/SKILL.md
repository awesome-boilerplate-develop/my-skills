---
name: best-practice-skill-create
description: >
  Chuẩn nội bộ để tạo, review và sửa Agent Skill trong bộ plugin — cấu trúc thư mục,
  frontmatter, văn phong, ngưỡng validate và quy trình eval. Dùng khi cần tạo skill mới,
  sửa SKILL.md, review skill người khác viết, hoặc quyết định một quy trình lặp lại có
  nên đóng thành skill hay không.
  Triggers: "tạo skill", "viết skill mới", "review skill", "cấu trúc skill", "frontmatter skill".
metadata:
  status: draft
  version: 0.4.1
  scope: internal
---

# Chuẩn viết skill

Quy định cấu trúc, frontmatter và văn phong cho mọi skill trong bộ plugin. Áp dụng khi tạo mới, khi sửa, và khi review.

Ngưỡng số, lỗi cứng và quy trình chấm điểm nằm ở `references/validation.md`. Chi tiết frontmatter và biến thay thế nằm ở `references/frontmatter-full.md`.

## Bước 0 — Quyết định có cần skill không

| Nhu cầu | Dùng |
|---|---|
| Việc đơn giản, làm trực tiếp được | Agent hiện tại |
| Cần tách nhiệm vụ/context hoặc chạy độc lập | Subagent |
| Quy trình lặp lại, Claude tự chọn bước | **Skill** |
| Nhiều agent theo topology cố định, chạy lại được | Workflow (`workflows/*.js`, cấp plugin) |
| Quy tắc ngắn, áp dụng xuyên suốt dự án | CLAUDE.md / AGENTS.md |
| Kiến thức chuyên biệt, chỉ cần ở một số task | Skill + references |

Phân biệt theo phạm vi và thời điểm cần nạp; cả kiến thức lẫn quy trình đều có thể thuộc skill.

Đã chắc là skill thì xác định **type** trước khi chọn cấu trúc — artifact, workflow, router, knowledge, taste, domain-variant hay automation. Mỗi type có cấu trúc và cách test khác nhau; xem `references/skill-types.md`.

Kiểm tra tiếp: nội dung này Claude đã biết sẵn chưa? Ưu tiên API nội bộ, quy ước riêng và workflow cụ thể. Kiến thức phổ thông vẫn hữu ích nếu giúp thực thi nhất quán; đo bằng eval có/không có skill thay vì loại chỉ vì không mới.

## Cấu trúc thư mục

★ = file bắt buộc hoặc thư mục được spec khuyến nghị · ○ = tài nguyên tùy chọn

Phân loại rule: F2/F4 và giới hạn field portable theo spec; tính năng có tiền tố Claude thuộc runtime Claude Code. Cách đặt thư mục, văn phong và ngưỡng review là quy ước nội bộ/heuristic.

```
<skill-name>/
├── SKILL.md                       ★ BẮT BUỘC
├── references/                    ★ Claude ĐỌC → tốn context
├── REFERENCE.md                   ○ biến thể khi chỉ 1–2 file
├── scripts/                       ★ Claude CHẠY → thường không cần nạp mã nguồn
│   └── requirements.txt           ○
├── <package>/                     ○ khi code lớn: __init__.py + modules
├── assets/                        ★ Claude COPY vào output
├── templates/ | themes/ | fonts/  ○ assets đổi tên theo nội dung
├── examples/                      ○ mẫu hoàn chỉnh để copy & sửa
├── agents/                        ○ prompt subagent nội bộ skill
└── evals/                         ○ test case cho chính skill
```

### S1 — Mặc định là không có thư mục con

Đa số skill chỉ cần `SKILL.md`. Tạo thư mục khi có nhu cầu thật. Xóa mọi thư mục rỗng trước khi commit.

### S2 — Phân loại theo cơ chế nạp, không theo loại file

| Câu hỏi | Đích |
|---|---|
| Claude cần **đọc hiểu** nó? | `references/` |
| Claude chỉ cần **chạy** nó? | `scripts/` |
| File đi thẳng vào **output**, Claude không đọc? | `assets/` |
| Là mẫu hoàn chỉnh để **tham chiếu**? | `examples/` |

### S3 — Ít file thì để phẳng

Dưới 3 file tham chiếu: đặt `REFERENCE.md` ngay cạnh `SKILL.md`. Từ 3 trở lên: gom vào `references/`.

### S4 — Ưu tiên 3 tên thư mục theo quy ước

Spec khuyến nghị `references/`, `scripts/`, `assets/` và cho phép file/thư mục khác. Ưu tiên ba tên này theo quy ước team; `examples/`, `evals/`, `agents/` cũng hợp lệ. Cảnh báo từ một linter không chứng minh giới hạn của nền tảng.

### S5 — Chỉ giữ tài liệu phục vụ phân phối và sử dụng

Ưu tiên đặt README/CHANGELOG ở cấp repo khi chỉ phục vụ người dùng. Giữ `LICENSE`/`LICENSE.txt` trong gói khi cần phân phối giấy phép; spec cho phép `license` trỏ tới file này. Việc file tồn tại không tự làm nội dung của nó được nạp vào context.

### S6 — Tài nguyên cần có nơi sử dụng rõ ràng

File trong `scripts/` `references/` `assets/` chỉ được nạp khi agent gặp một tham chiếu tới nó. Tài liệu cần có đường dẫn truy cập rõ; module được import hoặc asset được script sử dụng không cần liệt kê riêng trong SKILL.md.

Quan hệ tham chiếu có tính bắc cầu: SKILL.md → `references/<guide>.md` → `scripts/extract.py` thì script vẫn với tới được. Nhưng **luôn ghi đủ đuôi mở rộng** — `scripts/check.py`, không phải `scripts/check`.

## Frontmatter

### F1 — Chọn profile trước khi viết

| Đích phân phối | Field được phép |
|---|---|
| Chỉ Claude Code (kể cả plugin) | Tất cả |
| claude.ai / Skills API / `package_skill.py` | Đúng 6: `name` `description` `license` `compatibility` `metadata` `allowed-tools` |

Field ngoài spec làm upload **fail cứng**. Skill nào có thể dùng qua Cowork/claude.ai thì giới hạn ở 6 field ngay từ đầu.

### F2 — Field tự chế phải nằm trong `metadata`

```yaml
# SAI
category: business
keywords: [idea, validation]

# ĐÚNG
metadata:
  category: business
  keywords: "idea, validation"
```

### F3 — Không khai field trùng giá trị mặc định

`user-invocable: true` và `disable-model-invocation: false` là mặc định.

### F4 — Quy tắc đặt tên

- Chữ thường, số, gạch ngang. Tối đa 64 ký tự; không bắt đầu/kết thúc bằng `-`, không có `--`.
- **Phải khớp tên thư mục.**
- Profile Claude Code áp dụng thêm quy tắc tên riêng của Claude; checker nội bộ chặn `anthropic` và `claude` ở profile này.
- Ưu tiên dạng gerund: `processing-pdfs`, `analyzing-spreadsheets`. Chấp nhận cụm danh từ: `pdf-processing`.
- Tránh tên mơ hồ: `helper`, `utils`, `tools`, `data`.

### F5 — Description: văn xuôi trước, trigger sau

Tối đa 1.024 ký tự, ngôi thứ ba, nói cả *cái gì* lẫn *khi nào*.

Có hai áp lực ngược nhau. Claude có xu hướng **undertrigger** — không dùng skill khi lẽ ra nên dùng — nên cần trigger phrase cụ thể. Nhưng nhồi quá thì bị coi là keyword stuffing: từ 5 chuỗi trích dẫn trở lên mà văn xuôi xung quanh ít từ hơn số chuỗi, hoặc 8+ đoạn ngắn ngăn bằng phẩy.

Cách thoát: **một câu văn xuôi thật, rồi mới tới danh sách trigger**.

Công thức đầy đủ, rút từ `docx` và `file-reading` thật:

`<làm gì> + <trigger cụ thể: đuôi file, cụm từ, tình huống> + <phản-trigger: khi nào KHÔNG dùng>`

Phần phản-trigger cắt các near-miss — câu trùng từ khóa nhưng thật ra cần thứ khác. `docx` ghi "Do NOT use for PDFs, spreadsheets, Google Docs"; `file-reading` ghi "không dùng khi nội dung file đã có sẵn trong context". Không có nó, skill nhảy vào cả những câu hỏi bình thường.

**Toàn bộ thông tin "khi nào dùng" nằm ở description**, không để trong body. Body chỉ được nạp sau khi đã trigger — hướng dẫn trigger đặt ở đó thì quá muộn.

```yaml
description: >
  Đánh giá ý tưởng có đáng thử không, dựa trên bằng chứng và nguồn lực thực tế.
  Dùng khi người dùng mô tả một ý tưởng và muốn nhận xét thẳng thắn, hoặc cần
  so sánh nhiều hướng trước khi đầu tư.
  Triggers: "validate ý tưởng", "có nên làm không", "so sánh mấy ý tưởng này".
```

`description` + `when_to_use` chung cap 1.536 ký tự trong listing. Đặt use case chính lên đầu.

### F6 — `context: fork` chỉ dùng cho skill có nhiệm vụ rõ ràng

Skill dạng "đây là quy ước của dự án" mà fork thì subagent nhận hướng dẫn nhưng không có việc để làm, trả về rỗng.

## Body

### B1 — Ngôi thứ ba ở description, mệnh lệnh ở body

```markdown
Đọc file cấu hình trước.        ← đúng
Bạn nên đọc file cấu hình.      ← sai
```

### B2 — Giữ body mỏng

Dưới 500 dòng và dưới 5.000 token. Nội dung được nạp vào hội thoại khi gọi; việc giữ lại qua compaction phụ thuộc runtime. Viết rõ phạm vi và thời điểm áp dụng, tránh làm hướng dẫn cho một task trở thành ràng buộc cho mọi task sau.

### B3 — Chỉ viết cái Claude chưa biết

Với mỗi đoạn, tự hỏi: Claude có thực sự cần giải thích này không? Đoạn này có xứng với chi phí token không?

````markdown
## Trích text từ PDF                    ← ví dụ
Dùng pdfplumber:
```python
import pdfplumber
with pdfplumber.open("f.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

Bản dài dòng giải thích PDF là gì, thư viện là gì, vì sao chọn pdfplumber — tốn gấp ba, giá trị bằng không.

### B4 — Không trùng lặp giữa SKILL.md và references

Một thông tin nằm ở một chỗ. Ưu tiên references trừ khi thực sự cốt lõi.

### B5 — Reference chỉ một tầng

Khi gặp reference lồng nhau, Claude có thể chỉ đọc một phần (dùng `head -100` để xem trước) thay vì đọc trọn file. Mọi file phải link **trực tiếp** từ SKILL.md.

```
SKILL.md → advanced.md → details.md    ← SAI
SKILL.md → advanced.md, reference.md   ← ĐÚNG
```

### B6 — File tham chiếu trên 100 dòng cần mục lục

Để Claude thấy toàn bộ phạm vi ngay cả khi chỉ đọc một phần. File trên ~10k token thì ghi thêm mẫu grep trong SKILL.md.

### B7 — Liệt kê tài nguyên phụ khi có

Có thể đặt tham chiếu ngay ở bước sử dụng hoặc gom vào mục này. Skill một file không cần mục rỗng.

```markdown
## Tài liệu liên quan
- `references/<topic>.md` — <nội dung> · tra bằng `grep -n "<pattern>"`
- `scripts/<action>.py` — <chức năng> · **chạy**: `python scripts/<action>.py <args>`
```

Nêu rõ **chạy** hay **đọc**: "Chạy `analyze.py` để trích field" khác hẳn "Xem `analyze.py` để hiểu thuật toán".

Mỗi tham chiếu phải kèm **điều kiện đọc**, không chỉ liệt kê tên. "`references/<topic>.md` — khi phát hiện code và tài liệu mâu thuẫn" cho Claude biết lúc nào mở; "`references/<topic>.md` — luật xử lý mâu thuẫn" thì không. Tách hẳn nhóm *luôn đọc* khỏi *đọc khi cần* nếu có cả hai.

### B8 — Khớp mức tự do với độ mong manh của việc

| Mức | Dùng khi | Hình thức |
|---|---|---|
| Cao | Nhiều cách đều đúng, phụ thuộc ngữ cảnh | Hướng dẫn bằng văn |
| Trung bình | Có pattern ưa thích, chấp nhận biến thể | Pseudocode / script có tham số |
| Thấp | Thao tác mong manh, cần đúng thứ tự | Script cụ thể + "không được sửa lệnh" |

Cầu hẹp hai bên vực thì cần lan can. Đồng trống thì chỉ cần chỉ hướng.

### B9 — Một mặc định, không liệt kê nhiều lựa chọn

"Dùng pdfplumber. Với PDF scan cần OCR thì dùng pdf2image + pytesseract" — tốt.
"Bạn có thể dùng pypdf, hoặc pdfplumber, hoặc PyMuPDF, hoặc..." — gây nhiễu.

### B10 — Thuật ngữ nhất quán, không thông tin gắn mốc thời gian

Chọn một từ và dùng xuyên suốt: luôn "API endpoint", đừng trộn "URL"/"API route"/"path".

Đừng viết "trước tháng 8/2025 thì dùng API cũ". Dồn nội dung cũ vào mục "Old patterns" trong thẻ `<details>`.

### B11 — Quy trình dài thì kèm checklist

Với quy trình nhiều bước, cho sẵn checklist để Claude copy vào câu trả lời và tick dần. Kèm vòng phản hồi: chạy validator → sửa lỗi → lặp → chỉ đi tiếp khi pass.

### B12 — Trỏ script bằng `${CLAUDE_SKILL_DIR}`

Biến này được thay thế ở **cả body lẫn Bash rule trong `allowed-tools`**, nên script bundled chạy không cần hỏi quyền:

```yaml
---
name: extract-docs
allowed-tools: Bash(${CLAUDE_SKILL_DIR}/scripts/extract.py *)
---
Chạy `${CLAUDE_SKILL_DIR}/scripts/extract.py <file>`.
```

### B13 — Inject context động bằng `` !`lệnh` ``

Chạy trước khi Claude thấy nội dung. Lệnh fail **hủy toàn bộ lượt gọi skill** — nối `|| true` cho lệnh dự kiến exit non-zero.

### B14 — Lý do thay vì mệnh lệnh cứng dày đặc

Thấy mình viết ALWAYS / NEVER in hoa liên tục là cờ vàng. Claude đủ khả năng suy luận; đưa lý do thì tổng quát hóa sang tình huống chưa lường được, ra lệnh cứng thì làm máy móc và không thích ứng.

```markdown
KHÔNG BAO GIỜ đọc trọn glossary.                          ← cứng, không lý do
Grep glossary theo từ khóa thay vì đọc trọn — file 12k từ,   ← có lý do
đọc hết sẽ đẩy phần còn lại của SRS ra khỏi context.
```

Ngoại lệ chính đáng, và ở đó cứng là đúng: format output mà tool khác phụ thuộc (tên field JSON, khung báo cáo), thao tác mong manh cần đúng thứ tự (B8 mức thấp). Nói cách khác: cứng ở *hợp đồng*, mềm ở *cách làm*.

Lưu ý với chỉ số instruction specificity trong `references/validation.md`: nó đếm must/never so với may/consider. Đó là tín hiệu, không phải điểm cần tối đa — skill toàn "có thể cân nhắc" thì yếu, nhưng skill toàn NEVER cũng không phải mục tiêu.

## Script

### C1 — Tự xử lý lỗi, không đẩy cho Claude

Script bắt `FileNotFoundError`, `PermissionError` và có hành vi dự phòng rõ ràng. Đừng để `open(path).read()` trần rồi để Claude tự xoay.

### C2 — Không có hằng số bí ẩn

```python
# HTTP request thường xong trong 30 giây; timeout dài hơn để chịu mạng chậm
REQUEST_TIMEOUT = 30
```

`TIMEOUT = 47` — tại sao 47? Nếu bạn không biết giá trị đúng, Claude cũng không.

### C3 — Luôn dùng dấu gạch chéo xuôi

`scripts/helper.py`, không phải `scripts\helper.py`.

### C4 — Khai dependency rõ ràng

Liệt kê package cần thiết trong SKILL.md. Claude API **không có mạng và không cài được package lúc chạy**; claude.ai thì cài được từ npm/PyPI.

### C5 — Tool MCP phải gọi đủ tên

`BigQuery:bigquery_schema`, không phải `bigquery_schema`. Thiếu prefix server thì Claude không tìm ra tool.

## Eval

### E1 — Viết eval trước, viết tài liệu sau

Chạy Claude **không có skill** trên task thật → ghi lại chỗ hỏng cụ thể → dựng 3 kịch bản test → đo baseline → viết vừa đủ để pass → lặp.

Làm ngược lại sẽ ra skill giải quyết vấn đề tưởng tượng.

### E2 — Format `evals/evals.json`

```json
{
  "skill_name": "srs-lookup",
  "evals": [
    {
      "id": 1,
      "prompt": "Màn hình đăng ký khách hàng có ràng buộc gì về mã số thuế?",
      "expected_output": "Trả lời từ code, đối chiếu SRS, nêu rõ version tài liệu đã dùng",
      "files": [],
      "assertions": [
        "Đọc đúng module liên quan trước khi trả lời",
        "Nêu rõ version tài liệu đã tra",
        "Khi code và tài liệu mâu thuẫn thì lấy code và ghi chú discrepancy"
      ]
    }
  ]
}
```

Assertion phải kiểm chứng được khách quan. Skill có output chủ quan (văn phong, thiết kế) thì đánh giá định tính, đừng ép assertion.

### E3 — Vòng lặp Claude A / Claude B

Làm việc với một instance (**A**) để viết skill, rồi test bằng instance khác (**B**) đã nạp skill trên task thật. Quan sát B chệch ở đâu, mang quan sát cụ thể về cho A: "Khi B dùng skill này, nó quên lọc tài khoản test dù skill có nhắc — có phải chỗ đó chưa đủ nổi bật?"

Test trên cả Haiku, Sonnet và Opus nếu bộ sẽ chạy đa model. Cái vừa đủ cho Opus có thể quá ít cho Haiku.

### E4 — Prompt test phải đủ nặng

Claude chỉ tra skill với task nó **không tự làm gọn được**. Câu một bước đơn giản ("đọc file PDF này") có thể không trigger dù description khớp hoàn hảo. Prompt test phải giống người dùng thật: có đường dẫn file, tên cột, tên module, viết tắt nội bộ, typo, giọng nói chuyện.

Khi tối ưu description: khoảng 20 câu, nửa nên-trigger nửa không. Câu không-nên-trigger giá trị nhất là **near-miss** — trùng từ khóa nhưng cần thứ khác. Câu hiển nhiên vô quan ("viết hàm fibonacci" để test skill PDF) không kiểm được gì. Chọn description theo điểm trên tập held-out, không phải tập đã dùng để sửa.

### E5 — Đọc transcript, tổng quát hóa, không vá

Đọc **cả transcript**, không chỉ output cuối. Skill làm Claude đi vòng vèo — mở file không cần, viết lại helper đã có — là dấu hiệu cần cắt, dù output cuối đúng.

Sửa skill vừa khít 3 test case là overfit. Skill sẽ chạy hàng nghìn lần với prompt khác; khi feedback chỉ ra một lỗi, hỏi *vì sao* Claude làm thế rồi sửa ở mức nguyên tắc, không thêm một dòng "trường hợp X thì làm Y". Mỗi vòng lưu vào thư mục `iteration-N/` riêng để so được.

## Scaffold

```bash
SKILL=<skill-name>
mkdir -p "$SKILL"
cat > "$SKILL/SKILL.md" <<'EOF'
---
name: <skill-name>
description: <Một câu nói skill làm gì và khi nào dùng.> Triggers: "<a>", "<b>".
---

# <Tên skill>

## Mục đích

## Quy trình
1.

## Định dạng output

## Giới hạn
-
EOF
```

Thêm `references/ scripts/ assets/ examples/` **khi cần**, không trước.

## Tài liệu liên quan

### Script — chạy, không đọc

Dùng Python 3.10+. Scaffold chỉ cần thư viện chuẩn; checker cần PyYAML.
Cài dependency bằng `python3 -m pip install -r "${CLAUDE_SKILL_DIR}/scripts/requirements.txt"`.
Chạy test hồi quy khi sửa script: `python3 -m unittest discover -s "${CLAUDE_SKILL_DIR}/tests" -v`.

- `scripts/scaffold_skill.py` — dựng khung skill mới.
  **Chạy**: `python3 ${CLAUDE_SKILL_DIR}/scripts/scaffold_skill.py <tên> [--with=references,scripts]`
  Mặc định chỉ tạo SKILL.md, đúng theo S1.
- `scripts/check_skill.py` — kiểm tra skill theo chuẩn này.
  **Chạy**: `python3 ${CLAUDE_SKILL_DIR}/scripts/check_skill.py <đường-dẫn> [--strict] [--profile=portable|claude-code] [--allow-dirs=tên-thư-mục]`
  Kiểm: frontmatter, keyword stuffing, thư mục lạ, file cho người đọc, code fence,
  Markdown link nội bộ, tài liệu chưa được tham chiếu, ngưỡng token ước lượng,
  mục lục, độ sâu reference. Inline path chỉ dùng để theo file đã tồn tại;
  muốn phát hiện file đích bị thiếu thì dùng Markdown link. Không phân tích Python import. Exit 0 sạch / 1 error / 2 warning / 3 lỗi dùng.

Sau khi sửa skill, chạy `check_skill.py` rồi sửa tiếp đến khi sạch — đây là vòng
phản hồi bắt buộc theo B11.

### Tài liệu tra cứu — đọc khi cần

- `references/validation.md` — ngưỡng token, bốn lỗi cứng, cơ chế reachability,
  luật keyword stuffing, 6 chiều chấm điểm LLM, checklist review đầy đủ, tích hợp CI
- `references/skill-types.md` — bảy type skill rút từ skill thật, mỗi type: cấu trúc,
  trọng tâm, cách test, bẫy hay gặp. Đọc ở Bước 0 khi chọn cấu trúc
- `references/structure-catalog.md` — catalog thư mục bốn tầng, khảo sát repo thật,
  số dòng thực tế của skill Anthropic, ba mức độ phức tạp, ranh giới `agents/`
- `references/frontmatter-full.md` — bảng field đầy đủ, biến thay thế, đối số,
  `skillOverrides`, ranh giới spec vs Claude Code, ví dụ sai/đúng

### Khung output — copy, không đọc

- `assets/SKILL.md.template` — khung SKILL.md rỗng
- `assets/evals.json.template` — khung eval rỗng

### Ví dụ

- `examples/minimal-skill.md` — skill một file, có inject động và `allowed-tools`
- `examples/complete-skill.md` — skill đủ references/scripts/assets/evals, cách tổ chức
  mục "Tài liệu liên quan" tách luôn-đọc khỏi đọc-khi-cần

### Test case của chính skill này

- `evals/evals.json` — bốn eval, dùng khi sửa chuẩn này và cần kiểm tra không vỡ
- `evals/trigger-cases.json` — 20 prompt nên/không nên trigger; giữ held-out khỏi vòng sửa description. Chưa có kết quả chạy model.

Nguồn chuẩn: [Agent Skills specification](https://agentskills.io/specification) và [Claude Code skills](https://code.claude.com/docs/en/skills).
Các ngưỡng và quy ước team không phải yêu cầu chung của spec.

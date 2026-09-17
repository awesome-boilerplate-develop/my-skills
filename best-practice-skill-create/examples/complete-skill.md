# Ví dụ: skill mức Complete

Domain phức tạp, có tài liệu tra cứu và script kiểm chứng.

```
srs-lookup/
├── SKILL.md
├── references/
│   ├── doc-map.md          map module ↔ tài liệu ↔ version
│   ├── glossary-jp-en.md   thuật ngữ; file lớn, grep thay vì đọc hết
│   └── conflict-rules.md   luật ưu tiên khi code và tài liệu mâu thuẫn
├── scripts/
│   ├── extract_docs.py     trích text từ .docx/.xlsx/.pdf
│   └── validate_report.py  kiểm định dạng báo cáo
├── assets/
│   └── qa-report.md        khung báo cáo
└── evals/
    └── evals.json
```

Mục "Tài liệu liên quan" trong SKILL.md:

```markdown
## Tài liệu liên quan

### Luôn đọc
- `references/doc-map.md` — map module ↔ tài liệu ↔ version

### Đọc khi cần
- `references/conflict-rules.md` — khi phát hiện code và tài liệu mâu thuẫn
- `references/glossary-jp-en.md` — thuật ngữ JP/EN. File lớn: `grep -n "<từ khóa>"`, đừng đọc trọn

### Script
- `scripts/extract_docs.py` — **chạy**: `python3 ${CLAUDE_SKILL_DIR}/scripts/extract_docs.py <file>`
- `scripts/validate_report.py` — **chạy** sau khi dựng báo cáo, sửa lỗi rồi chạy lại đến khi pass

### Khung output
- `assets/qa-report.md` — copy và điền
```

Ba điểm đáng học:

1. Tách **luôn đọc** khỏi **đọc khi cần** — Claude không nạp thừa.
2. File lớn được kèm cách grep ngay tại chỗ trỏ tới nó.
3. `validate_report.py` tạo vòng phản hồi: dựng → kiểm → sửa → kiểm lại.

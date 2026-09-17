# Bảy type skill

Không có phân loại chính thức trong tài liệu Anthropic. Bảng này rút ra từ đọc ngược các skill thật trong runtime; dùng ở Bước 0 để chọn cấu trúc thư mục và cách test trước khi viết.

## Mục lục

- [Bảng tóm tắt](#bảng-tóm-tắt)
- [A — Artifact / Output-format](#a--artifact--output-format)
- [B — Workflow / Procedure](#b--workflow--procedure)
- [C — Router / Dispatcher](#c--router--dispatcher)
- [D — Knowledge / Guardrail](#d--knowledge--guardrail)
- [E — Taste / Style](#e--taste--style)
- [F — Domain-variant](#f--domain-variant)
- [G — Automation / Scheduled](#g--automation--scheduled)
- [Ánh xạ sang bộ plugin](#ánh-xạ-sang-bộ-plugin)

## Bảng tóm tắt

| Type | Ví dụ thật | Cấu trúc | Evals |
|---|---|---|---|
| A Artifact | `docx` `pptx` `xlsx` `pdf` | SKILL.md + `scripts/` bắt buộc + `assets/` nếu có mẫu | Rất nên — output khách quan |
| B Workflow | `skill-creator` `import-memory` | SKILL.md + `references/` + `agents/` + `scripts/` | Chấm theo bước hoàn thành |
| C Router | `file-reading` | Chỉ SKILL.md, thường dài | Nhẹ — test trigger |
| D Knowledge | `product-self-knowledge` | SKILL.md ngắn + `references/` | Kiểm tính đúng |
| E Taste | `frontend-design` | Chỉ SKILL.md, ngắn | **Không ép assertion** |
| F Domain-variant | `cloud-deploy` (docs) | SKILL.md + một file/biến thể trong `references/` | Mỗi biến thể ≥1 case |
| G Automation | `morning` | SKILL.md + `assets/` | Kiểm format |

## A — Artifact / Output-format

Sinh hoặc chỉnh một định dạng file cụ thể.

- **Trọng tâm**: script làm sẵn để mọi lần gọi không phải viết lại; quirks của thư viện; đường dẫn output.
- **Tín hiệu cần script**: chạy test thấy Claude tự viết lại cùng một helper (`create_docx.py`, `build_chart.py`) nhiều lần. Viết một lần, bundle vào.
- **Bẫy**: nhét cả tài liệu API thư viện vào SKILL.md. `pdf` tách sang `REFERENCE.md` và `FORMS.md` — 314 dòng SKILL.md mà vẫn không đủ chỗ.

## B — Workflow / Procedure

Quy trình nhiều bước có thứ tự, có điểm dừng để hỏi người dùng.

- **Trọng tâm**: nêu vòng lặp ở đầu và nhắc lại ở cuối; nói rõ chỗ nào linh hoạt được, chỗ nào không được bỏ qua.
- **Bẫy**: quy trình cứng khiến Claude không thích ứng khi người dùng nhảy vào giữa chừng. `skill-creator` xử lý bằng một câu đáng copy: *xác định người dùng đang ở đâu trong quy trình rồi nhảy vào đúng chỗ*.
- **Evals**: chấm theo bước đã hoàn thành đúng thứ tự, hơn là so khớp output cuối.

## C — Router / Dispatcher

Không tự làm việc; đọc tình huống rồi chỉ sang tool hoặc skill đúng.

- **Trọng tâm**: bảng ánh xạ điều kiện → hành động, phủ hết nhánh. `file-reading` dài 372 dòng vì bản chất là bảng tra.
- **Bẫy**: chồng lấn với skill đích. Phải ghi ranh giới ngay trong description — `file-reading` ghi "không dùng khi nội dung file đã có trong context".

## D — Knowledge / Guardrail

Chặn Claude trả lời từ trí nhớ khi trí nhớ có thể sai hoặc cũ.

- **Trọng tâm**: description phải bắt cả trường hợp gián tiếp. `product-self-knowledge` ghi "kể cả task code có dùng SDK" — không thì Claude chỉ tra khi được hỏi thẳng.
- **Bẫy**: nội dung hết hạn. Ghi ngày cập nhật và nguồn ngay trong file reference.
- **Evals**: kiểm tính đúng của sự thật, không kiểm văn phong.

## E — Taste / Style

Định hướng thẩm mỹ, giọng văn, chuẩn thiết kế.

- **Trọng tâm**: nguyên tắc + ví dụ đối chiếu (cái này tốt, cái này tệ, vì sao). `frontend-design` 71 dòng, không bundle gì.
- **Bẫy**: viết thành checklist máy móc thì mọi output ra giống hệt nhau — trái mục đích của skill.
- **Evals**: output chủ quan thì đánh giá định tính do người xem. Ép assertion sẽ chấm sai trọng tâm.

## F — Domain-variant

Một workflow, nhiều biến thể nền tảng hoặc framework.

- **Cấu trúc**: SKILL.md giữ workflow chung + logic *chọn* biến thể; mỗi biến thể một file trong `references/` (`aws.md`, `gcp.md`, `azure.md`).
- **Trọng tâm**: Claude chỉ đọc đúng một file biến thể — đây là chỗ tiết kiệm context lớn nhất của type này.
- **Bẫy**: rò rỉ chi tiết riêng của một biến thể lên SKILL.md.

## G — Automation / Scheduled

Chạy theo lệnh gọi tên hoặc theo lịch, output cố định.

- **Trọng tâm**: điều kiện trigger phải **hẹp**. Description của `morning` nói thẳng: hỏi về lịch không đồng nghĩa với gọi skill.
- **Thường đi với**: `disable-model-invocation: true` — chỉ người dùng gọi.
- **Bẫy**: trigger rộng thì skill nhảy vào những câu hỏi bình thường.

## Ánh xạ sang bộ plugin

| Skill dự kiến | Type | Hệ quả cấu trúc |
|---|---|---|
| `srs-lookup` | D + F | `references/` chứa map tài liệu và glossary; nếu nhiều hệ thống thì một file/hệ thống |
| `test-case-writer` | A | `scripts/` sinh/validate file test case; `assets/` template Excel |
| Quy ước commit, review, báo cáo | E hoặc G | Ngắn, chỉ SKILL.md; G thì thêm `disable-model-invocation` |
| Orchestrator dev ↔ test | B | Vòng lặp rõ, `agents/` chứa prompt hai vai, câu "nhảy vào đúng chỗ" |

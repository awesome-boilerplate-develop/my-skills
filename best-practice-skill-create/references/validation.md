# Validate & chấm điểm skill

Đọc file này khi review skill hoặc dựng CI. Phân biệt checker Python nội bộ với công cụ `agent-ecosystem/skill-validator` bên ngoài. Quy tắc normative theo [Agent Skills specification](https://agentskills.io/specification); ngưỡng token và các chỉ số nội dung là heuristic.

## Mục lục

- [Ngưỡng token](#ngưỡng-token)
- [Lỗi cứng](#lỗi-cứng)
- [Cảnh báo](#cảnh-báo)
- [Keyword stuffing](#keyword-stuffing)
- [Chỉ số chất lượng nội dung](#chỉ-số-chất-lượng-nội-dung)
- [Contamination](#contamination)
- [Chấm điểm LLM-as-judge](#chấm-điểm-llm-as-judge)
- [Checklist review](#checklist-review)
- [Chạy validator](#chạy-validator)
- [Tích hợp CI](#tích-hợp-ci)
- [Anti-pattern hay gặp khi review](#anti-pattern-hay-gặp-khi-review)
- [Ba chỗ chuẩn nội bộ lệch với validator](#ba-chỗ-chuẩn-nội-bộ-lệch-với-validator)

## Ngưỡng token

Bảng dưới là ngưỡng nội bộ tham khảo. Checker Python ước lượng bằng số ký tự / 4, không phải tokenizer; tiếng Việt có thể lệch đáng kể. Không dùng số ước lượng để kết luận chính xác chi phí context.

| Phạm vi | Warning | Error |
|---|---|---|
| SKILL.md body | 5.000 token **hoặc** 500 dòng | — |
| Mỗi file trong `references/` | 10.000 | 25.000 |
| Tổng `references/` | 25.000 | 50.000 |
| File ngoài cấu trúc chuẩn | 25.000 | 100.000 |

File text trong `assets/` (`.md .tex .py .yaml .yml .tsx .ts .jsx .sty .mplstyle .ipynb`) được đếm riêng vì LLM có thể nạp chúng vào context. Ảnh và binary bỏ qua.

**Check tổng thể**: nếu nội dung ngoài chuẩn vượt **10 lần** nội dung chuẩn và trên 25.000 token, đây không phải skill — đó là một repo có file SKILL.md trong đó.

## Lỗi cứng

Bốn thứ này là error, không phải warning:

1. **Code fence chưa đóng** (` ``` ` hoặc `~~~`) trong SKILL.md hoặc file reference. Agent sẽ hiểu nhầm mọi thứ sau đó là code — hỏng hoàn toàn.
2. **Internal link gãy**. Link tương đối trong SKILL.md được resolve theo thư mục skill và kiểm tra tồn tại. Đây là vấn đề cấu trúc, không phải vấn đề mạng.
3. **Thiếu `name` hoặc `description`**, hoặc `name` sai định dạng (chữ thường + số + gạch ngang, 1–64 ký tự).
4. **`name` không khớp tên thư mục.**

## Cảnh báo

**Tên thư mục ngoài quy ước nội bộ** — checker chấp nhận `scripts/`, `references/`, `assets/`, `examples/`, `evals/`, `agents/`, `tests/`. Tên khác chỉ là cảnh báo để review; spec vẫn cho phép.

**Tài liệu ở skill root** — checker gợi ý xem lại `README.md`, `CHANGELOG.md`; giữ giấy phép trong gói khi cần. `AGENTS.md` có cảnh báo riêng: nó là cấu hình agent cấp repo, không phải nội dung skill.

**Phạm vi checker Python nội bộ**

- Parse YAML bằng PyYAML, từ chối key trùng và kiểm kiểu dữ liệu.
- `--profile=portable` mặc định: kiểm 6 field spec; `--profile=claude-code` cho field mở rộng và thêm quy ước tên Claude.
- Kiểm Markdown link tới file nội bộ (bỏ qua anchor khi kiểm file tồn tại). Inline path chỉ theo file đã tồn tại để tránh nhận nhầm tên minh họa là link gãy.
- Theo reference Markdown bắc cầu; cảnh báo tài liệu chưa được trỏ tới và reference gián tiếp. Không đi vào ví dụ/template như tài liệu chỉ dẫn.
- Không phân tích Python import, dependency asset, hoặc xác minh anchor. Kiểm các phần này bằng test script và review.
- Chấp nhận `examples/`, `evals/`, `agents/`, `tests/`. `--allow-dirs` chỉ tắt cảnh báo tên thư mục, không bỏ check link/tài liệu mồ côi.
- Kiểm fence backtick và tilde theo loại và độ dài. Dùng bốn backtick để bao ví dụ có ba backtick bên trong.

```bash
python3 -m pip install -r best-practice-skill-create/scripts/requirements.txt
python3 best-practice-skill-create/scripts/check_skill.py best-practice-skill-create --strict
python3 -m unittest discover -s best-practice-skill-create/tests -v
```

Các tính năng phân tích nội dung, tokenizer, Python import và LLM scoring bên dưới thuộc công cụ bên ngoài; checker Python không triển khai chúng.

## Keyword stuffing

Hai luật:

1. Description có **≥5 chuỗi trích dẫn** bị flag khi văn xuôi xung quanh có **ít từ hơn số chuỗi**.
2. Description có **≥8 đoạn ngắn ngăn bằng dấu phẩy** (sau khi loại chuỗi trích dẫn) bị coi là danh sách keyword.

Pattern được chấp nhận: một câu văn xuôi thật, **rồi** mới tới danh sách trigger bổ sung dạng `Triggers: "a", "b"`.

Đây là chỗ căng với lời khuyên "viết description pushy" của skill-creator. Giải pháp là đặt trigger **sau** văn xuôi, không phải bỏ trigger.

## Chỉ số chất lượng nội dung

Tính cho SKILL.md và các file markdown trong `references/`:

| Chỉ số | Ý nghĩa |
|---|---|
| Word count | Tổng số từ |
| Code block ratio | Tỉ lệ block code |
| Imperative ratio | Tỉ lệ câu bắt đầu bằng động từ mệnh lệnh (use, run, create, configure…) |
| Strong markers | Đếm từ chỉ thị: must, always, never, required, ensure |
| Weak markers | Đếm từ khuyến nghị: may, consider, could, optional, suggested |
| **Instruction specificity** | `strong / (strong + weak)` — mức chỉ thị so với khuyến nghị |
| **Information density** | `code_block_ratio × 0.5 + imperative_ratio × 0.5` |
| Section count | Header H2 trở lên |

Không có ngưỡng pass/fail cho nhóm này — chúng là tín hiệu. Instruction specificity thấp nghĩa là skill toàn "có thể", "nên cân nhắc" — Claude sẽ không coi là ràng buộc.

Nhưng **đừng tối đa hóa nó**. Tài liệu skill-creator nói ngược lại: thấy mình viết ALWAYS/NEVER dày đặc là cờ vàng, vì Claude tổng quát hóa từ lý do tốt hơn từ mệnh lệnh. Hai nguồn hòa được: cứng ở *hợp đồng* (format output, thứ tự thao tác mong manh), mềm ở *cách làm*. Xem rule B14.

## Contamination

Phát hiện skill có ví dụ code ở nhiều ngôn ngữ, gây sinh code sai ngữ cảnh.

Công thức 3 yếu tố, cap ở 1.0:

- Multi-interface tool (0.3): công cụ có nhiều binding ngôn ngữ — MongoDB, AWS, Docker, Kubernetes, Redis
- Language mismatch (0.4): code block thuộc các nhóm ngôn ngữ ứng dụng khác nhau. Nhóm phụ trợ (shell, config, query, markup) được loại vì không gây nhầm cú pháp
- Scope breadth (0.3): số nhóm công nghệ khác nhau được nhắc

Mức: high ≥0.5 · medium ≥0.2 · low <0.2.

Với bộ nội bộ có codebase một ngôn ngữ thì chỉ số này ít quan trọng. Nó đáng chú ý nếu skill nói về công cụ đa binding.

## Chấm điểm LLM-as-judge

**SKILL.md — 6 chiều, mỗi chiều 1–5:**

| Chiều | Câu hỏi |
|---|---|
| Clarity | Hướng dẫn có rõ và không mơ hồ không? |
| Actionability | Agent có làm theo từng bước được không? |
| Token Efficiency | Mỗi token có xứng chỗ trong context không? |
| Scope Discipline | Có bám đúng mục đích đã nêu không? |
| Directive Precision | Dùng chỉ thị chính xác (must/always/never) hay gợi ý mơ hồ? |
| **Novelty** | Bao nhiêu phần vượt ra ngoài cái LLM đã biết từ training? |

**File reference — 5 chiều:** Clarity, Token Efficiency, Novelty, **Instructional Value** (có ví dụ cụ thể áp dụng được ngay không), **Skill Relevance** (mọi mục có phục vụ mục đích của skill cha không).

### Cách dùng novelty

Novelty là tín hiệu để ưu tiên thông tin hữu ích, không chứng minh hiệu quả. Đo giá trị bằng baseline và kết quả task; kiến thức quen thuộc vẫn có thể giúp thực thi nhất quán.

Khi novelty ≥3, validator gọi thêm một lượt để chỉ ra chi tiết nào là mới — API nội bộ, quy ước riêng, workflow chưa công bố — cho người review fact-check có trọng điểm.

Áp dụng cho bộ plugin: skill chứa map tài liệu nội bộ, glossary riêng, quy ước nghiệp vụ của hệ thống → novelty cao, giữ. Skill kiểu "cách viết unit test tốt" → novelty thấp, cân nhắc bỏ.

## Checklist review

**Cấu trúc**
- [ ] SKILL.md tồn tại, frontmatter YAML hợp lệ
- [ ] `name` khớp tên thư mục, đúng quy tắc dấu gạch ngang; áp thêm quy tắc tên của runtime đích
- [ ] Không có thư mục rỗng hoặc tài nguyên không dùng; tên thư mục ngoài quy ước không phải lỗi spec
- [ ] Tài liệu và giấy phép được giữ theo nhu cầu phân phối; không xóa chỉ để hết cảnh báo
- [ ] Tài liệu được tham chiếu rõ; script/asset có caller hoặc mục đích cụ thể
- [ ] Không có code fence chưa đóng
- [ ] Không có internal link gãy

**Frontmatter**
- [ ] Đã chọn profile (Claude Code-only hay 6 field spec)
- [ ] Field tự chế nằm trong `metadata`; profile portable dùng giá trị string
- [ ] Không khai field trùng mặc định
- [ ] Description: văn xuôi trước, trigger sau; không keyword stuffing
- [ ] Description + when_to_use dưới 1.536 ký tự, use case chính lên đầu

**Body**
- [ ] Dưới 500 dòng và 5.000 token
- [ ] Thể mệnh lệnh, không ngôi thứ hai
- [ ] Reference chỉ một tầng từ SKILL.md
- [ ] File reference trên 100 dòng có mục lục
- [ ] Không trùng lặp giữa SKILL.md và references
- [ ] Không có thông tin gắn mốc thời gian ngoài mục "old patterns"
- [ ] Thuật ngữ nhất quán
- [ ] Nêu rõ script nào để **chạy**, file nào để **đọc**

**Script**
- [ ] Tự xử lý lỗi, không đẩy cho Claude
- [ ] Không có hằng số bí ẩn
- [ ] Đường dẫn dùng gạch chéo xuôi
- [ ] Dependency được liệt kê và có sẵn trong môi trường đích
- [ ] Tool MCP gọi đủ tên `Server:tool`

**Test**
- [ ] Có ít nhất 3 eval
- [ ] Đã đo baseline không có skill
- [ ] Gõ câu KHÔNG nên trigger → skill không load
- [ ] Đã test trên các model sẽ dùng
- [ ] Chạy `/doctor` xem chi phí listing

## Chạy validator

Cài (một trong hai):

```bash
brew tap agent-ecosystem/tap && brew install skill-validator
# hoặc
go install github.com/agent-ecosystem/skill-validator/cmd/skill-validator@latest
```

Lệnh theo giai đoạn phát triển:

| Giai đoạn | Lệnh | Trả lời câu hỏi |
|---|---|---|
| Dựng khung | `validate structure` | Có đúng spec và agent dùng được không? |
| Viết nội dung | `analyze content` | Chất lượng chỉ dẫn thế nào? |
| Thêm ví dụ | `analyze contamination` | Có gây nhiễu chéo ngôn ngữ không? |
| Review | `validate links` | Link ngoài còn sống không? |
| Chấm điểm | `score evaluate` | LLM đánh giá skill này ra sao? |
| Trước khi publish | `check` | Chạy tất cả trừ chấm điểm LLM |

Exit code: `0` sạch · `1` có error · `2` có warning · `3` lỗi CLI.

Cờ hay dùng cho bộ nội bộ:

```bash
skill-validator check --allow-dirs=evals,agents --strict skills/
```

`--strict` biến warning thành error. `--allow-dirs` chấp nhận thư mục ngoài chuẩn. `--allow-flat-layouts` cho phép để file ngay ở skill root. `--skip-orphans` tắt cảnh báo file mồ côi.

Nếu đường dẫn không chứa SKILL.md nhưng thư mục con có, validator tự phát hiện và kiểm tra từng skill riêng.

Chấm điểm LLM không cần API key nếu đã đăng nhập Claude CLI:

```bash
skill-validator score evaluate --provider claude-cli skills/srs-lookup/
```

Kết quả cache trong `.score_cache/` bên trong thư mục skill. Xem lại không tốn API: `score report --compare`.

## Tích hợp CI

```yaml
name: Validate Skills
on:
  pull_request:
    paths: ["skills/**"]
jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: brew install agent-ecosystem/tap/skill-validator
      - run: |
          skill-validator check --strict --emit-annotations skills/
          skill-validator check --strict -o markdown skills/ >> "$GITHUB_STEP_SUMMARY"
```

`--emit-annotations` gắn error/warning vào đúng dòng trong PR diff. Tách skill đã publish (dùng `--strict`) khỏi skill nháp (không `--strict`, warning không chặn merge).

Có sẵn pre-commit hook:

```yaml
repos:
  - repo: https://github.com/agent-ecosystem/skill-validator
    rev: v0.5.0
    hooks:
      - id: skill-validator-claude
```

Repo cũng có `examples/review-skill` — một Agent Skill hướng dẫn agent chạy trọn quy trình review. Copy vào thư mục skill để dev tự review trước khi mở PR.

## Anti-pattern hay gặp khi review

| Anti-pattern | Vì sao hỏng | Thay bằng |
|---|---|---|
| Description chỉ mô tả chức năng | Không trigger được | Thêm ngữ cảnh, cụm từ, đuôi file, phản-trigger |
| Hướng dẫn "khi nào dùng" nằm trong body | Body nạp sau khi trigger — quá muộn | Dời hết lên description |
| Nhét toàn bộ tài liệu vào SKILL.md | Đốt context mọi lần trigger | Đẩy xuống `references/`, kèm điều kiện đọc |
| MUST/NEVER dày đặc | Claude làm máy móc, không thích ứng | Giải thích lý do; cứng chỉ ở hợp đồng |
| Skill mô tả từng bước một việc xác định | Chậm, dễ sai, Claude tự viết lại helper | Bundle script |
| Sửa skill vừa khít 3 test case | Không tổng quát | Sửa ở mức nguyên tắc |
| Ép assertion lên skill chủ quan | Chấm sai trọng tâm | Đánh giá định tính |
| Bỏ baseline | Không biết skill có ích hay chỉ tốn context | Luôn chạy cặp có/không |
| Trigger quá rộng | Nhảy vào cả câu hỏi thường | Thêm phản-trigger, hoặc `disable-model-invocation` |
| Test bằng prompt quá nhẹ | Claude tự làm được, không tra skill | Prompt nặng, giống người dùng thật |

## Ba chỗ chuẩn nội bộ lệch với validator

1. **Giấy phép:** giữ `LICENSE.txt` khi cần phân phối; spec cho phép. Không sửa giấy phép để thỏa cảnh báo của linter.
2. **Thư mục tùy chọn:** spec cho phép thư mục khác; `--allow-dirs` là cấu hình linter, không quyết định khả năng nạp của runtime.
3. **Mục lục:** team lấy 100 dòng làm ngưỡng gợi ý; không phải điều kiện hợp lệ của spec.

# Catalog cấu trúc thư mục

Tổng hợp từ khảo sát skill thật: bộ Anthropic ship trong runtime (`/mnt/skills/`), `anthropics/skills`, `anthropics/claude-plugins-official`, `obra/superpowers`, `warpdotdev/common-skills`. Đọc file này khi phân vân một thư mục hoặc file nên đặt ở đâu, hoặc khi review skill lấy từ nguồn ngoài.

## Mục lục

- [Tầng A — spec công nhận](#tầng-a--spec-công-nhận)
- [Tầng B — quy ước phổ biến](#tầng-b--quy-ước-phổ-biến)
- [Tầng C — xuất hiện thực tế ở repo lớn](#tầng-c--xuất-hiện-thực-tế-ở-repo-lớn)
- [Tầng D — không thuộc skill](#tầng-d--không-thuộc-skill)
- [Ba mức độ phức tạp](#ba-mức-độ-phức-tạp)
- [Bằng chứng từ repo thật](#bằng-chứng-từ-repo-thật) — ba tầng nạp, số dòng thực tế
- [agents/ trong skill vs agents/ cấp plugin](#agents-trong-skill-vs-agents-cấp-plugin)

## Tầng A — spec công nhận

Ba thư mục duy nhất được Agent Skills spec công nhận. Validator chỉ chấp nhận ba tên này mà không cảnh báo.

| Thư mục | Cơ chế | Nội dung |
|---|---|---|
| `references/` | Claude **đọc** → tốn context | Schema, API docs, domain knowledge, policy, workflow chi tiết |
| `scripts/` | Claude **chạy** → không tốn context | Code deterministic, tiện ích lặp lại |
| `assets/` | Claude **copy** → không đọc | Template, font, logo, boilerplate |

## Tầng B — quy ước phổ biến

Không trong spec, nhưng dùng rộng rãi. Chỉ hoạt động khi SKILL.md trỏ tay tới.

| Thứ | Ai dùng | Ghi chú |
|---|---|---|
| `examples/` | plugin-dev của Anthropic, `internal-comms`, `paint` | Được scaffold bằng `mkdir -p skills/<name>/{references,examples,scripts}` |
| **File .md phẳng cạnh SKILL.md** | `pdf` (FORMS.md, REFERENCE.md), `pdf-reading` (REFERENCE.md), `paint` (reference.md) | Thay `references/` khi chỉ 1–2 file |
| `reference/` số ít | `mcp-builder` | Cùng vai trò, tên khác — chạy được nhưng bị cảnh báo |
| `requirements.txt` | `slack-gif-creator` (root), `mcp-builder` (trong scripts/) | Dependency Python |
| `LICENSE.txt` | Gần như mọi skill Anthropic | **Validator flag là file cho người đọc** — chuẩn nội bộ bỏ nó khỏi skill |

## Tầng C — xuất hiện thực tế ở repo lớn

| Thứ | Ai dùng | Vai trò |
|---|---|---|
| `agents/` | `skill-creator` (analyzer.md, comparator.md, grader.md) | Prompt subagent **bên trong** skill |
| Python package | `paint/paintkit/`, `slack-gif-creator/core/` | Code có `__init__.py`, import được |
| `templates/` | `algorithmic-art` | = `assets/` đặt tên theo nội dung |
| `themes/` + file demo | `theme-factory` | Dữ liệu domain |
| `canvas-fonts/` | `canvas-design` | Font |
| `eval-viewer/` | `skill-creator` | Tooling phụ trợ (HTML + script) |
| `evals/` | Khuyến nghị trong hướng dẫn evaluating-skills | Test case; validator cần `--allow-dirs=evals` |
| File rời đủ loại | `superpowers/writing-skills`: render-graphs.js, graphviz-conventions.dot, persuasion-principles.md | Không thư mục nào cả |
| Prompt rời | `superpowers/writing-plans`: plan-document-reviewer-prompt.md | Prompt cho một bước cụ thể |

## Tầng D — không thuộc skill

Hay bị nhầm nhất. Tất cả là **component cấp plugin**, đặt ở plugin root, ngang hàng với `skills/`:

`workflows/` · `agents/` (loại đăng ký được) · `hooks/` · `commands/` · `output-styles/` · `themes/` · `monitors/` · `bin/` · `.mcp.json` · `.lsp.json` · `settings.json` · `.claude-plugin/plugin.json`

Chỉ `plugin.json` được nằm trong `.claude-plugin/`. Mọi thư mục component khác phải ở plugin root — đặt sai chỗ là nguyên nhân số một của lỗi "skill không xuất hiện".

## Ba mức độ phức tạp

**Minimal** — kiến thức đơn giản, không tài nguyên phụ. Khoảng hai phần ba skill Anthropic đang ship rơi vào mức này.

```
skill-name/
└── SKILL.md
```

**Standard** — khuyến nghị cho đa số plugin skill:

```
skill-name/
├── SKILL.md
├── references/detailed-guide.md
└── examples/working-example.sh
```

**Complete** — domain phức tạp, cần tiện ích kiểm chứng:

```
skill-name/
├── SKILL.md
├── references/{patterns.md, advanced.md}
├── examples/{example1.sh, example2.json}
└── scripts/validate.sh
```

## Bằng chứng từ repo thật

Ba tầng nạp context, và cái giá của mỗi tầng:

| Tầng | Nội dung | Khi nào vào context | Ai trả giá |
|---|---|---|---|
| 1 | `name` + `description` | **Mọi phiên**, kể cả phiên không dùng skill | Tất cả mọi người |
| 2 | Thân SKILL.md | Khi trigger, rồi ở lại đến hết phiên | Phiên đó |
| 3 | `references/` `scripts/` `assets/` | Chỉ khi Claude chủ động mở | Lượt đó |

Số dòng SKILL.md thực tế của skill Anthropic đang chạy (đo `wc -l`):

| Skill | Dòng | Ghi chú |
|---|---|---|
| `product-self-knowledge` | 65 | Type knowledge, ngắn + references |
| `frontend-design` | 71 | Type taste, không bundle gì |
| `import-memory` | 89 | |
| `docx` | 91 | Nặng về scripts/ |
| `xlsx` | 99 | |
| `morning` | 152 | |
| `pptx` | 241 | |
| `pdf` | 314 | Vẫn phải tách REFERENCE.md + FORMS.md |
| `file-reading` | 372 | Type router — bản chất là bảng tra |
| `skill-creator` | 485 | Sát ngưỡng 500 |

Chưa skill nào vượt 500. Thứ gần chạm là skill-creator, và nó đã đẩy schema xuống `references/`.

Khảo sát cấu trúc `/mnt/skills/`:

| Skill | Nội dung |
|---|---|
| `frontend-design`, `file-reading`, `brand-guidelines`, `event-planning`, `learn`, `doc-coauthoring` | Chỉ SKILL.md (+ LICENSE.txt) |
| `docx`, `pptx`, `xlsx` | SKILL.md + scripts/ |
| `pdf` | SKILL.md + FORMS.md + REFERENCE.md + scripts/ — file .md phẳng, không có thư mục references/ |
| `paint` | SKILL.md + reference.md + render.py + examples/ + paintkit/ |
| `mcp-builder` | SKILL.md + reference/ (số ít) + scripts/ có requirements.txt và .xml |
| `theme-factory` | SKILL.md + themes/ + theme-showcase.pdf |
| `skill-creator` | Phức tạp nhất: agents/ + assets/ + eval-viewer/ + references/ + scripts/ (9 file .py) |

Kết luận rút ra: **mặc định là không có thư mục con**. Thư mục mọc ra khi có nhu cầu thật, không phải scaffold sẵn.

## agents/ trong skill vs agents/ cấp plugin

Hai thứ khác hẳn nhau, trùng tên:

| | `<skill>/agents/` | `<plugin>/agents/` |
|---|---|---|
| Bản chất | File prompt mà skill tự đọc rồi truyền cho Task tool | Subagent đăng ký với Claude Code |
| Auto-discovery | Không | Có |
| Gọi được bằng @ | Không | Có, dạng `@plugin:tên` |
| Frontmatter | Không cần | `name`, `description`, `model`, `tools`… |

Quy tắc chọn: vai trò dùng chung nhiều dự án → `agents/` cấp plugin. Vai phụ chỉ tồn tại bên trong một quy trình cụ thể → `agents/` trong skill đó.

`skill-creator` dùng cách thứ hai cho analyzer/comparator/grader — ba vai chỉ có nghĩa trong vòng lặp đánh giá skill, không đáng chiếm chỗ trong danh sách agent cấp plugin.

# Frontmatter & cấu hình — tra cứu đầy đủ

Đọc file này khi cần chi tiết vượt bảng tóm tắt trong SKILL.md.

## Mục lục

- [Ranh giới spec vs Claude Code](#ranh-giới-spec-vs-claude-code)
- [Bảng field đầy đủ](#bảng-field-đầy-đủ)
- [Skill lấy tên lệnh từ đâu](#skill-lấy-tên-lệnh-từ-đâu)
- [Biến thay thế trong body](#biến-thay-thế-trong-body)
- [Đối số](#đối-số)
- [Inject context động](#inject-context-động)
- [Vòng đời nội dung skill](#vòng-đời-nội-dung-skill)
- [Budget listing](#budget-listing)
- [skillOverrides](#skilloverrides)
- [Nơi skill được nạp](#nơi-skill-được-nạp)
- [Ví dụ frontmatter sai và cách sửa](#ví-dụ-frontmatter-sai-và-cách-sửa)

## Ranh giới spec vs Claude Code

| Đường phân phối | Field được phép |
|---|---|
| Claude Code — mọi cấp, kể cả plugin | Toàn bộ bảng dưới |
| claude.ai upload, Skills API, `package_skill.py` | `name` `description` `license` `compatibility` `metadata` `allowed-tools` |

Lỗi khi vi phạm:

```
Unexpected key(s) in SKILL.md frontmatter: argument-hint.
Allowed properties are: allowed-tools, compatibility, description, license, metadata, name
```

Đây là lỗi cứng, không phải cảnh báo. Frontmatter theo spec vẫn load bình thường trong Claude Code, nên khi phân vân thì chọn spec.

Boolean nhận `yes` `no` `on` `off` `1` `0` mọi kiểu chữ, ngoài `true`/`false`.

## Bảng field đầy đủ

Mọi field đều tùy chọn. Chỉ `description` là khuyến nghị.

| Field | Nhóm | Ghi chú |
|---|---|---|
| `name` | Nhận diện | Nhãn hiển thị. Xem [Skill lấy tên lệnh từ đâu](#skill-lấy-tên-lệnh-từ-đâu) |
| `description` | Nhận diện | Bỏ trống → lấy đoạn markdown đầu tiên |
| `when_to_use` | Nhận diện | Nối vào `description`; chung cap 1.536 ký tự. **Gạch dưới**, không gạch ngang |
| `paths` | Nhận diện | Glob giới hạn kích hoạt tự động. Chuỗi phân cách phẩy hoặc YAML list |
| `disable-model-invocation` | Gọi | `true` = chỉ user gọi. Cũng chặn preload vào subagent và chặn scheduled task |
| `user-invocable` | Gọi | `false` = chỉ Claude gọi, ẩn khỏi menu `/` |
| `allowed-tools` | Quyền | Pre-approve trong lượt gọi. Không hạn chế tool khác |
| `disallowed-tools` | Quyền | Gỡ tool khỏi pool khi skill active |
| `model` | Thực thi | Giá trị như `/model`, hoặc `inherit`. Với `context: fork` thì áp cho subagent |
| `effort` | Thực thi | `low` `medium` `high` `xhigh` `max` |
| `context` | Thực thi | `fork` = chạy trong subagent cô lập |
| `agent` | Thực thi | Loại subagent khi fork. Mặc định `general-purpose` |
| `background` | Thực thi | Chỉ có tác dụng với `context: fork`. `false` = chờ trong lượt |
| `hooks` | Thực thi | Đăng ký khi gọi, chạy đến hết session |
| `shell` | Thực thi | `bash` (mặc định) hoặc `powershell` |
| `argument-hint` | Đối số | Hiển thị trong autocomplete |
| `arguments` | Đối số | Tên đối số vị trí, cho `$tên` |
| `metadata` | Meta | Map tự do. Giá trị không phải map bị bỏ qua |
| `license` | Meta | Thuộc spec, Claude Code không xử lý |
| `compatibility` | Meta | Thuộc spec, tối đa 500 ký tự |

### Ma trận gọi & nạp context

| Frontmatter | User gọi | Claude gọi | Khi nào vào context |
|---|---|---|---|
| (mặc định) | Có | Có | Description luôn có; body nạp khi gọi |
| `disable-model-invocation: true` | Có | Không | Description **không** có; body nạp khi user gọi |
| `user-invocable: false` | Không | Có | Description luôn có; body nạp khi gọi |

## Skill lấy tên lệnh từ đâu

| Vị trí | Nguồn tên lệnh | Ví dụ |
|---|---|---|
| `~/.claude/skills/` hoặc `.claude/skills/` | **Tên thư mục** | `deploy-staging/SKILL.md` → `/deploy-staging` |
| `.claude/skills/` lồng, khi trùng tên | Đường dẫn tương đối + tên thư mục | `apps/web/.claude/skills/deploy/` → `/apps/web:deploy` |
| `.claude/commands/*.md` | Tên file | `deploy.md` → `/deploy` |
| Plugin `skills/<dir>/` | Frontmatter `name` hoặc tên thư mục, namespace theo plugin | → `/my-plugin:review` |
| Plugin root `SKILL.md` | Frontmatter `name`, fallback tên thư mục plugin | → `/my-plugin:review` |

Điểm hay nhầm: ở skill cá nhân/dự án, `name` **không** đổi lệnh gõ. Chỉ plugin skill mới đổi.

## Biến thay thế trong body

| Biến | Giá trị |
|---|---|
| `${CLAUDE_SKILL_DIR}` | Thư mục chứa SKILL.md. Plugin skill: thư mục con của skill, không phải plugin root |
| `${CLAUDE_PLUGIN_ROOT}` | Thư mục cài plugin. Chỉ plugin skill |
| `${CLAUDE_PLUGIN_DATA}` | Thư mục dữ liệu sống qua update. Chỉ plugin skill |
| `${CLAUDE_PROJECT_DIR}` | Project root |
| `${CLAUDE_SESSION_ID}` | Session ID hiện tại |
| `${CLAUDE_EFFORT}` | `low`/`medium`/`high`/`xhigh`/`max` |

`${CLAUDE_SKILL_DIR}` và `${CLAUDE_PROJECT_DIR}` được thay thế ở **hai chỗ**: body markdown và Bash rule trong `allowed-tools`. Plugin skill thêm `${CLAUDE_PLUGIN_ROOT}` và `${CLAUDE_PLUGIN_DATA}`. Dùng cùng biến ở cả hai chỗ để script bundled chạy không cần hỏi quyền.

## Đối số

| Cú pháp | Ý nghĩa |
|---|---|
| `$ARGUMENTS` | Toàn bộ đối số. Nếu body không có, Claude Code nối `ARGUMENTS: <giá trị>` vào cuối |
| `$ARGUMENTS[N]` / `$N` | Đối số theo vị trí, đánh số từ 0 |
| `$tên` | Đối số có tên khai trong `arguments` |

Đối số theo vị trí dùng quoting kiểu shell: `/my-skill "hello world" second` → `$0` = `hello world`, `$1` = `second`.

Placeholder không có đối số tương ứng thì giữ nguyên (dạng `$N`) hoặc thành chuỗi rỗng (dạng `$tên`). Escape `$` bằng backslash: `\$1.00`.

Stack skill: gõ `/write-tests /fix-issue 123` nạp cả hai và truyền `123` cho từng cái. Tối đa 1 + 5 skill; dừng ở token đầu tiên không phải skill inline user-invocable.

## Inject context động

Inline: `` !`lệnh` `` — chỉ được nhận khi `!` ở đầu dòng hoặc ngay sau khoảng trắng. `KEY=!`cmd`` không chạy.

Nhiều dòng: mở fenced block bằng ` ```! `.

Hành vi:

- Thay thế chạy **một lần** trên file gốc. Output không được quét lại để tìm placeholder mới.
- Chạy ở cwd của session shell. Dùng `${CLAUDE_SKILL_DIR}`/`${CLAUDE_PROJECT_DIR}` cho đường dẫn cần ổn định.
- Timeout mặc định 2 phút của Bash tool.
- stderr gộp vào stdout với shell `bash`.

**Lệnh fail hủy toàn bộ lượt gọi skill**, Claude không thấy nội dung skill lần đó. Với `bash`, mọi exit code khác 0 đều là fail, trừ exit code 1 từ nhóm lệnh search/compare. Nối `|| true` cho lệnh dự kiến exit non-zero (ví dụ script check exit 1 khi tìm thấy lỗi).

Lệnh inject **không bao giờ hỏi quyền**. Nếu permission check trả về khác "allow", lượt gọi bị hủy. Pre-approve bằng `allowed-tools`; rule ask hoặc deny vẫn hủy bất kể `allowed-tools`.

Tắt toàn cục: `"disableSkillShellExecution": true` trong settings.

## Vòng đời nội dung skill

Khi skill được gọi, nội dung render vào hội thoại như **một message và ở lại đến hết session**. Claude Code không đọc lại file ở lượt sau.

Hệ quả thực tế:

- Viết hướng dẫn như **chỉ thị thường trực**, không phải bước làm một lần.
- Mỗi dòng là chi phí token lặp lại.
- Grant `allowed-tools` thì ngược lại — hết hiệu lực khi user gửi tin nhắn kế tiếp.
- Gọi lại skill với nội dung y hệt → chỉ thêm ghi chú "đã nạp", không nhân đôi. Nội dung khác đi (đối số đổi, lệnh inject ra output mới) → nối bản đầy đủ lần nữa.
- Auto-compaction giữ lại 5.000 token đầu của mỗi skill, tổng ngân sách 25.000 token, ưu tiên skill gọi gần nhất. Skill cũ có thể bị rơi hẳn.

Nếu skill "hết tác dụng" sau lượt đầu, nội dung thường vẫn còn — model chỉ đang chọn cách khác. Siết `description` và hướng dẫn, hoặc dùng hook để cưỡng chế.

## Budget listing

Description của mọi skill được nạp sẵn để Claude biết có gì. Budget mặc định **1% context window**. Khi tràn, Claude Code cắt description bắt đầu từ skill ít dùng nhất — có thể mất đúng keyword cần match.

Công cụ:

- `/doctor` — ước tính chi phí listing và các skill đóng góp nhiều nhất
- `/context` — dòng Skills cho kích thước sau khi áp budget
- `--debug` — cảnh báo khi listing vượt budget

Nới budget: `skillListingBudgetFraction` (ví dụ `0.02`) hoặc env `SLASH_COMMAND_TOOL_CHAR_BUDGET`. Giải phóng budget: đặt skill phụ thành `name-only`. Cap mỗi entry là 1.536 ký tự, chỉnh bằng `skillListingMaxDescChars`.

## skillOverrides

Bật/tắt skill từ settings mà không sửa SKILL.md — hữu ích với skill checked-in của repo chung.

```json
{
  "skillOverrides": {
    "legacy-context": "name-only",
    "deploy": "off"
  }
}
```

| Giá trị | Liệt kê cho Claude | Trong menu `/` |
|---|---|---|
| `on` | Tên + description | Có |
| `name-only` | Chỉ tên | Có |
| `user-invocable-only` | Ẩn | Có |
| `off` | Ẩn | Ẩn |

Menu `/skills` ghi giúp: chọn skill, `Space` để đổi trạng thái, `Enter` để lưu vào `.claude/settings.local.json`. Plugin skill **không** chịu ảnh hưởng — quản qua `/plugin`.

## Nơi skill được nạp

| Cấp | Đường dẫn | Phạm vi |
|---|---|---|
| Enterprise | Managed settings | Toàn tổ chức |
| Cá nhân | `~/.claude/skills/<name>/SKILL.md` | Mọi dự án |
| Dự án | `.claude/skills/<name>/SKILL.md` | Dự án đó |
| Plugin | `<plugin>/skills/<name>/SKILL.md` | Nơi plugin được bật |

Trùng tên: enterprise > cá nhân > dự án. Plugin skill có namespace `plugin:skill` nên không xung đột. Skill ở mọi cấp đè bundled skill cùng tên, nhưng không đè alias của nó.

Skill dự án nạp từ `.claude/skills/` ở thư mục khởi động và **mọi thư mục cha lên tới repo root**. Skill trong thư mục con **không** nạp lúc khởi động — chỉ nạp lần đầu Claude đọc/sửa file trong thư mục đó.

Live change detection chỉ áp cho text của `SKILL.md`. Với thư mục skill kiêm plugin, thay đổi `hooks/`, `.mcp.json`, `agents/`, `output-styles/` cần `/reload-plugins`.

## Ví dụ frontmatter sai và cách sửa

### Field tự chế ở cấp cao nhất

```yaml
# SAI — category, keywords bị Claude Code bỏ qua; upload claude.ai fail
name: idea-validator
description: ...
category: business
keywords: [idea, validation, startup]
metadata:
  author: cpp
  version: 3.0.0
```

```yaml
# ĐÚNG
name: idea-validator
description: ...
metadata:
  category: business
  keywords: [idea, validation, startup]
  author: cpp
  version: 3.0.0
```

### Khai lại giá trị mặc định

```yaml
# THỪA
user-invocable: true
disable-model-invocation: false
```

### Fork một skill không có nhiệm vụ

```yaml
# SAI — subagent nhận quy ước nhưng không có việc, trả về rỗng
name: api-conventions
description: Quy ước thiết kế API của dự án
context: fork
```

```yaml
# ĐÚNG — kiến thức nền thì để Claude tự áp dụng inline
name: api-conventions
description: Quy ước thiết kế API của dự án
user-invocable: false
```

### Description viết cho người, không cho model

```yaml
# YẾU — không có trigger, Claude không biết khi nào dùng
description: Công cụ hỗ trợ đánh giá ý tưởng.
```

```yaml
# CŨNG SAI — nhồi trigger, bị flag keyword stuffing
description: Đánh giá ý tưởng. "validate ý tưởng", "có nên làm không",
  "ý tưởng này ổn không", "so sánh ý tưởng", "nên đầu tư không", "phân tích thị trường"
```

```yaml
# ĐÚNG — văn xuôi trước, trigger sau
description: >
  Đánh giá ý tưởng có đáng thử không, dựa trên bằng chứng và nguồn lực thực tế.
  Dùng khi người dùng mô tả một ý tưởng và muốn nhận xét thẳng thắn, hoặc cần
  so sánh nhiều hướng trước khi đầu tư.
  Triggers: "validate ý tưởng", "có nên làm không", "so sánh mấy ý tưởng này".
```

Ngưỡng keyword stuffing: ≥5 chuỗi trích dẫn khi văn xuôi có ít từ hơn số chuỗi, hoặc ≥8 đoạn ngắn ngăn bằng phẩy. Chi tiết ở `references/validation.md`.

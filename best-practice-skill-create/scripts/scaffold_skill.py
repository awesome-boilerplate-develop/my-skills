#!/usr/bin/env python3
"""Dựng khung một skill mới theo chuẩn nội bộ. Chỉ dùng thư viện chuẩn Python 3.

Mặc định chỉ tạo SKILL.md — đúng theo rule S1 (mặc định là không có thư mục con).
Thêm thư mục bằng --with, chỉ khi đã biết chắc cần.

Usage:
    python3 scripts/scaffold_skill.py <skill-name> [--dir .] [--with references,scripts,assets,examples,evals]

Ví dụ:
    python3 scripts/scaffold_skill.py srs-lookup --with references,scripts
    python3 scripts/scaffold_skill.py commit-helper
"""

import re
import sys
from pathlib import Path

VALID_DIRS = {"references", "scripts", "assets", "examples", "evals", "agents"}

SKILL_TEMPLATE = """---
name: {name}
description: >
  <Một câu nói skill làm gì và khi nào dùng — văn xuôi thật, không phải danh sách keyword.>
  Triggers: "<cụm người dùng thật sự gõ>", "<cụm khác>".
---

# {title}

## Mục đích

<2–3 câu: skill giải quyết vấn đề gì, ranh giới ở đâu. Chỉ viết điều Claude chưa biết.>

## Quy trình

1. <Bước 1 — thể mệnh lệnh, không dùng "bạn nên".>
2. <Bước 2.>
3. <Bước cuối: định dạng output, nơi ghi kết quả.>

## Định dạng output

<Mô tả chính xác đầu ra: cấu trúc, nơi lưu, độ dài.>

## Giới hạn

- <Điều tuyệt đối không làm.>
- <Phạm vi được phép đụng tới.>
{resources}"""

EVALS_TEMPLATE = """{{
  "skill_name": "{name}",
  "evals": [
    {{
      "id": 1,
      "prompt": "<câu người dùng thật sự sẽ gõ>",
      "expected_output": "<mô tả kết quả mong đợi>",
      "files": [],
      "assertions": [
        "<điều kiểm chứng được khách quan>",
        "<điều kiểm chứng được khác>"
      ]
    }}
  ]
}}
"""

REFERENCE_TEMPLATE = """# <Chủ đề>

> Nạp theo yêu cầu bởi skill `{name}`. Không lặp lại nội dung đã có trong SKILL.md.

## Mục lục

- <mục 1>
- <mục 2>

## <Mục 1>

<Nội dung chi tiết: schema, bảng tra, luật nghiệp vụ, edge case.>
"""


def slug_ok(name: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9-]{1,64}", name))


def main(argv: list[str]) -> int:
    if not argv or argv[0].startswith("--"):
        print(__doc__)
        return 3

    name = argv[0]
    if not slug_ok(name):
        print(f"Tên không hợp lệ: {name!r} — chỉ chữ thường, số, gạch ngang, tối đa 64 ký tự.")
        return 3
    for reserved in ("anthropic", "claude"):
        if reserved in name.lower():
            print(f"Tên chứa từ khóa bị cấm: {reserved!r}")
            return 3

    base = Path(".")
    wanted: set[str] = set()
    for arg in argv[1:]:
        if arg.startswith("--dir="):
            base = Path(arg.split("=", 1)[1])
        elif arg.startswith("--with="):
            wanted |= {d.strip() for d in arg.split("=", 1)[1].split(",") if d.strip()}

    unknown = wanted - VALID_DIRS
    if unknown:
        print(f"Thư mục không nhận diện được: {', '.join(sorted(unknown))}")
        print(f"Hợp lệ: {', '.join(sorted(VALID_DIRS))}")
        return 3

    skill_dir = base / name
    if skill_dir.exists():
        print(f"Đã tồn tại: {skill_dir}")
        return 3
    skill_dir.mkdir(parents=True)

    created = []
    resources_lines = []

    if "references" in wanted:
        (skill_dir / "references").mkdir()
        (skill_dir / "references" / "guide.md").write_text(
            REFERENCE_TEMPLATE.format(name=name), encoding="utf-8"
        )
        created.append("references/guide.md")
        resources_lines.append("- `references/guide.md` — <nội dung> · tra bằng `grep -n \"<pattern>\"`")

    if "scripts" in wanted:
        (skill_dir / "scripts").mkdir()
        script = skill_dir / "scripts" / "run.py"
        script.write_text(
            '#!/usr/bin/env python3\n'
            '"""<Một dòng: script làm gì.>\n\n'
            'Usage:\n'
            '    python3 run.py <arg>\n'
            '"""\n\n'
            'import sys\n\n\n'
            'def main(argv: list[str]) -> int:\n'
            '    return 0\n\n\n'
            'if __name__ == "__main__":\n'
            '    sys.exit(main(sys.argv[1:]))\n',
            encoding="utf-8",
        )
        script.chmod(0o755)
        created.append("scripts/run.py")
        resources_lines.append(
            "- `scripts/run.py` — <chức năng> · **chạy**: `python3 ${CLAUDE_SKILL_DIR}/scripts/run.py <args>`"
        )

    if "assets" in wanted:
        (skill_dir / "assets").mkdir()
        (skill_dir / "assets" / "template.md").write_text(
            "# <Tiêu đề>\n\n<Khung output mà Claude điền vào.>\n", encoding="utf-8"
        )
        created.append("assets/template.md")
        resources_lines.append("- `assets/template.md` — khung output")

    if "examples" in wanted:
        (skill_dir / "examples").mkdir()
        (skill_dir / "examples" / "sample.md").write_text(
            "# Ví dụ hoàn chỉnh\n\n<Một kết quả mẫu đã điền đầy đủ.>\n", encoding="utf-8"
        )
        created.append("examples/sample.md")
        resources_lines.append("- `examples/sample.md` — kết quả mẫu")

    if "evals" in wanted:
        (skill_dir / "evals").mkdir()
        (skill_dir / "evals" / "evals.json").write_text(
            EVALS_TEMPLATE.format(name=name), encoding="utf-8"
        )
        created.append("evals/evals.json")
        resources_lines.append("- `evals/evals.json` — test case cho skill này")

    if "agents" in wanted:
        (skill_dir / "agents").mkdir()
        (skill_dir / "agents" / "reviewer.md").write_text(
            "# Reviewer\n\n<Prompt cho subagent mà skill này spawn.>\n", encoding="utf-8"
        )
        created.append("agents/reviewer.md")
        resources_lines.append("- `agents/reviewer.md` — prompt subagent")

    resources = ""
    if resources_lines:
        resources = "\n## Tài liệu liên quan\n\n" + "\n".join(resources_lines) + "\n"

    title = name.replace("-", " ").capitalize()
    (skill_dir / "SKILL.md").write_text(
        SKILL_TEMPLATE.format(name=name, title=title, resources=resources), encoding="utf-8"
    )

    print(f"Đã tạo {skill_dir}/")
    print("  SKILL.md")
    for f in created:
        print(f"  {f}")
    print("\nBước tiếp theo:")
    print("  1. Điền SKILL.md, thay mọi chỗ <...>")
    print("  2. Xóa thư mục nào không dùng tới")
    print(f"  3. python3 scripts/check_skill.py {skill_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

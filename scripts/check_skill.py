#!/usr/bin/env python3
"""Kiểm tra một skill theo chuẩn nội bộ. Chỉ dùng thư viện chuẩn Python 3.

Chạy được các check không cần binary ngoài: cấu trúc thư mục, frontmatter,
code fence, internal link, file mồ côi, đếm dòng và token ước lượng.

Usage:
    python3 scripts/check_skill.py <đường-dẫn-skill> [--strict] [--allow-dirs=a,b]

Exit codes:
    0  sạch, không error không warning
    1  có error
    2  có warning, không error
    3  lỗi sử dụng (đường dẫn sai, thiếu tham số)
"""

import re
import sys
from pathlib import Path

SPEC_DIRS = {"scripts", "references", "assets"}
CONVENTION_DIRS = {"examples", "evals", "agents"}
HUMAN_FILES = {"README.md", "CHANGELOG.md", "LICENSE", "LICENSE.txt", "AGENTS.md"}
SPEC_FRONTMATTER = {"name", "description", "license", "compatibility", "metadata", "allowed-tools"}

# SKILL.md body: cảnh báo khi vượt các ngưỡng này
MAX_BODY_LINES = 500
MAX_BODY_TOKENS = 5_000
REF_WARN_TOKENS = 10_000
REF_ERROR_TOKENS = 25_000
REFS_TOTAL_WARN = 25_000
REFS_TOTAL_ERROR = 50_000
TOC_MIN_LINES = 100

errors: list[str] = []
warnings: list[str] = []
infos: list[str] = []


def err(msg: str) -> None:
    errors.append(msg)


def warn(msg: str) -> None:
    warnings.append(msg)


def info(msg: str) -> None:
    infos.append(msg)


def est_tokens(text: str) -> int:
    """Ước lượng token. Xấp xỉ 4 ký tự mỗi token — đủ dùng để so ngưỡng."""
    return len(text) // 4


def split_frontmatter(text: str) -> tuple[dict[str, str], str]:
    """Tách frontmatter YAML. Parser tối giản: chỉ lấy khóa cấp cao nhất."""
    if not text.startswith("---"):
        return {}, text
    parts = text.split("---", 2)
    if len(parts) < 3:
        return {}, text
    raw, body = parts[1], parts[2]
    fields: dict[str, str] = {}
    for line in raw.splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        if line[0] in " \t-":  # giá trị lồng, bỏ qua
            continue
        if ":" in line:
            key, _, value = line.partition(":")
            fields[key.strip()] = value.strip()
    return fields, body


def check_fences(path: Path, text: str) -> None:
    opens = len(re.findall(r"^```", text, re.M))
    if opens % 2 != 0:
        err(f"{path}: code fence chưa đóng ({opens} dấu ```)")


def check_frontmatter(fields: dict[str, str], skill_dir: Path) -> None:
    if not fields:
        err("SKILL.md: không có frontmatter YAML")
        return

    name = fields.get("name")
    if not name:
        warn("SKILL.md: thiếu `name` (sẽ lấy theo tên thư mục)")
    else:
        if not re.fullmatch(r"[a-z0-9-]{1,64}", name):
            err(f"SKILL.md: `name` không hợp lệ: {name!r} (chữ thường, số, gạch ngang, ≤64)")
        if name != skill_dir.name:
            err(f"SKILL.md: `name` ({name}) không khớp tên thư mục ({skill_dir.name})")
        for reserved in ("anthropic", "claude"):
            if reserved in name.lower():
                err(f"SKILL.md: `name` chứa từ khóa bị cấm: {reserved!r}")

    desc = fields.get("description", "")
    if not desc:
        err("SKILL.md: thiếu `description`")
    else:
        if len(desc) > 1024:
            err(f"SKILL.md: `description` dài {len(desc)} ký tự, tối đa 1024")
        quoted = re.findall(r'"[^"]+"', desc)
        prose = re.sub(r'"[^"]+"', "", desc)
        prose_words = len(prose.split())
        if len(quoted) >= 5 and prose_words < len(quoted):
            warn(
                f"SKILL.md: nghi keyword stuffing — {len(quoted)} chuỗi trích dẫn "
                f"nhưng chỉ {prose_words} từ văn xuôi. Viết một câu văn xuôi trước, "
                f"rồi mới tới danh sách Triggers"
            )
        segments = [s for s in prose.split(",") if 0 < len(s.split()) <= 4]
        if len(segments) >= 8:
            warn(f"SKILL.md: nghi danh sách keyword — {len(segments)} đoạn ngắn ngăn bằng phẩy")

    extra = set(fields) - SPEC_FRONTMATTER
    if extra:
        info(
            f"SKILL.md: field ngoài spec: {', '.join(sorted(extra))}. "
            f"Chạy được trong Claude Code, nhưng upload claude.ai/Skills API sẽ fail"
        )


def check_structure(skill_dir: Path, allow_dirs: set[str]) -> None:
    for child in sorted(skill_dir.iterdir()):
        if child.name.startswith("."):
            continue
        if child.is_dir():
            if child.name in SPEC_DIRS or child.name in allow_dirs:
                continue
            count = sum(1 for _ in child.rglob("*") if _.is_file())
            hint = " (quy ước phổ biến — dùng --allow-dirs để tắt cảnh báo)" if child.name in CONVENTION_DIRS else ""
            warn(f"thư mục ngoài chuẩn: {child.name}/ ({count} file){hint}")
        elif child.name in HUMAN_FILES:
            warn(f"{child.name} là file cho người đọc, không nên nằm trong skill — đặt ở cấp plugin")

    # nesting sâu trong thư mục spec
    for d in SPEC_DIRS:
        target = skill_dir / d
        if not target.is_dir():
            continue
        for f in target.rglob("*"):
            if f.is_file() and len(f.relative_to(target).parts) > 2:
                warn(f"nesting sâu: {f.relative_to(skill_dir)}")


def check_links(skill_dir: Path, skill_text: str) -> None:
    for target in re.findall(r"\]\(([^)#:]+)\)", skill_text):
        if target.startswith(("http://", "https://", "mailto:")):
            continue
        if not (skill_dir / target).exists():
            err(f"SKILL.md: internal link gãy: {target}")
    # Backtick references to files under references/ must exist too
    for target in set(re.findall(r"`(references/[A-Za-z0-9_./-]+)`", skill_text)):
        if not (skill_dir / target).exists():
            err(f"SKILL.md: nhắc file không tồn tại: {target}")


def check_reachability(skill_dir: Path, skill_text: str, allow_dirs: set[str]) -> None:
    """Đồ thị reachability bắc cầu, dùng string containment như validator thật."""
    candidates = [
        p for p in skill_dir.rglob("*")
        if p.is_file() and p.name != "SKILL.md" and not p.name.startswith(".")
        and p.name != "__init__.py"
    ]
    reached: set[Path] = set()
    frontier = [(skill_text, "SKILL.md")]

    while frontier:
        text, _origin = frontier.pop()
        for p in candidates:
            if p in reached:
                continue
            rel = p.relative_to(skill_dir).as_posix()
            if rel in text or p.name in text:
                reached.add(p)
                try:
                    frontier.append((p.read_text(encoding="utf-8"), rel))
                except (UnicodeDecodeError, OSError):
                    pass

    for p in sorted(candidates):
        if p in reached:
            continue
        rel = p.relative_to(skill_dir).as_posix()
        if rel.split("/")[0] in allow_dirs:
            info(f"bỏ qua check mồ côi cho thư mục được phép: {rel}")
            continue
        warn(f"file mồ côi (không được nhắc ở đâu reachable từ SKILL.md): {rel}")

    # tham chiếu thiếu đuôi mở rộng
    for p in candidates:
        rel = p.relative_to(skill_dir).as_posix()
        stem = rel.rsplit(".", 1)[0]
        if p not in reached and stem in skill_text:
            warn(f"tham chiếu thiếu đuôi mở rộng: {stem} → phải ghi {rel}")


def check_sizes(skill_dir: Path, body: str) -> None:
    lines = len(body.splitlines())
    tokens = est_tokens(body)
    info(f"SKILL.md body: {lines} dòng, ~{tokens} token")
    if lines > MAX_BODY_LINES:
        warn(f"SKILL.md body {lines} dòng, vượt ngưỡng {MAX_BODY_LINES}")
    if tokens > MAX_BODY_TOKENS:
        warn(f"SKILL.md body ~{tokens} token, vượt ngưỡng {MAX_BODY_TOKENS}")

    refs = skill_dir / "references"
    if not refs.is_dir():
        return
    total = 0
    for f in sorted(refs.rglob("*.md")):
        text = f.read_text(encoding="utf-8")
        t = est_tokens(text)
        total += t
        rel = f.relative_to(skill_dir).as_posix()
        info(f"{rel}: {len(text.splitlines())} dòng, ~{t} token")
        if t > REF_ERROR_TOKENS:
            err(f"{rel}: ~{t} token, vượt mức lỗi {REF_ERROR_TOKENS}")
        elif t > REF_WARN_TOKENS:
            warn(f"{rel}: ~{t} token, vượt ngưỡng cảnh báo {REF_WARN_TOKENS}")
        if len(text.splitlines()) > TOC_MIN_LINES and "## Mục lục" not in text and "## Contents" not in text:
            warn(f"{rel}: trên {TOC_MIN_LINES} dòng nhưng không có mục lục")
    if total > REFS_TOTAL_ERROR:
        err(f"tổng references ~{total} token, vượt mức lỗi {REFS_TOTAL_ERROR}")
    elif total > REFS_TOTAL_WARN:
        warn(f"tổng references ~{total} token, vượt ngưỡng cảnh báo {REFS_TOTAL_WARN}")


def check_ref_depth(skill_text: str, skill_dir: Path) -> None:
    """Reference phải một tầng: file được SKILL.md trỏ tới không nên trỏ tiếp sang file thứ ba."""
    direct = set()
    for target in re.findall(r"\]\(([^)#:]+)\)", skill_text):
        if not target.startswith(("http", "mailto")):
            direct.add(target)
    for target in direct:
        p = skill_dir / target
        if not p.is_file() or p.suffix != ".md":
            continue
        text = p.read_text(encoding="utf-8")
        for nested in re.findall(r"\]\(([^)#:]+)\)", text):
            if nested.startswith(("http", "mailto")):
                continue
            if nested not in direct and (skill_dir / nested).exists():
                warn(f"reference lồng hai tầng: SKILL.md → {target} → {nested}")


def main(argv: list[str]) -> int:
    if not argv:
        print(__doc__)
        return 3
    strict = "--strict" in argv
    allow_dirs: set[str] = set()
    positional = []
    for arg in argv:
        if arg.startswith("--allow-dirs="):
            allow_dirs |= {d.strip() for d in arg.split("=", 1)[1].split(",") if d.strip()}
        elif not arg.startswith("--"):
            positional.append(arg)
    if not positional:
        print("Thiếu đường dẫn skill.")
        return 3

    skill_dir = Path(positional[0]).resolve()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        print(f"Không tìm thấy {skill_md}")
        return 3

    text = skill_md.read_text(encoding="utf-8")
    fields, body = split_frontmatter(text)

    check_frontmatter(fields, skill_dir)
    check_structure(skill_dir, allow_dirs)
    check_links(skill_dir, text)
    check_reachability(skill_dir, text, allow_dirs)
    check_sizes(skill_dir, body)
    check_ref_depth(text, skill_dir)
    for f in sorted(skill_dir.rglob("*.md")):
        check_fences(f.relative_to(skill_dir), f.read_text(encoding="utf-8"))

    print(f"Kiểm tra skill: {skill_dir.name}/\n")
    for line in infos:
        print(f"  ·  {line}")
    if infos and (warnings or errors):
        print()
    for line in warnings:
        print(f"  !  {line}")
    for line in errors:
        print(f"  X  {line}")

    print(f"\nKết quả: {len(errors)} error, {len(warnings)} warning")
    if errors:
        return 1
    if warnings:
        return 1 if strict else 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

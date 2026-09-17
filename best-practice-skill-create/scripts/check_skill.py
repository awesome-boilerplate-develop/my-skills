#!/usr/bin/env python3
"""Kiểm tra một skill theo chuẩn nội bộ. Cần PyYAML; cài từ scripts/requirements.txt.

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

import argparse
import re
from urllib.parse import unquote, urlsplit

import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("Thiếu PyYAML. Cài bằng python3 -m pip install -r scripts/requirements.txt", file=sys.stderr)
    raise SystemExit(3)

SPEC_DIRS = {"scripts", "references", "assets"}
CONVENTION_DIRS = {"examples", "evals", "agents", "tests"}
HUMAN_FILES = {"README.md", "CHANGELOG.md", "AGENTS.md"}
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


class UniqueKeyLoader(yaml.SafeLoader):
    """Reject duplicate keys instead of silently accepting the last value."""


def unique_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str) or key in result:
            raise yaml.constructor.ConstructorError(
                None, None, "mapping keys must be unique strings", key_node.start_mark
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, unique_mapping
)


def split_frontmatter(text: str) -> tuple[dict, str]:
    match = re.match(r"\A---[ \t]*\r?\n(.*?)^---[ \t]*(?:\r?\n|$)", text, re.M | re.S)
    if not match:
        return {}, text
    try:
        fields = yaml.load(match.group(1), Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        err(f"SKILL.md: YAML không hợp lệ: {exc}")
        return {}, text[match.end():]
    if not isinstance(fields, dict):
        err("SKILL.md: frontmatter phải là mapping")
        return {}, text[match.end():]
    return fields, text[match.end():]


def check_fences(path: Path, text: str) -> None:
    opened = None
    for number, line in enumerate(text.splitlines(), 1):
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if not match:
            continue
        marker, tail = match.groups()
        if opened is None:
            if marker[0] == "`" and "`" in tail:
                continue
            opened = (marker[0], len(marker), number)
        elif marker[0] == opened[0] and len(marker) >= opened[1] and not tail.strip():
            opened = None
    if opened:
        err(f"{path}:{opened[2]}: code fence chưa đóng")


def check_frontmatter(fields: dict, skill_dir: Path, profile: str = "portable") -> None:
    if not fields:
        err("SKILL.md: không có frontmatter YAML")
        return

    name = fields.get("name")
    if not isinstance(name, str) or not name:
        err("SKILL.md: `name` phải là chuỗi không rỗng")
    else:
        if len(name) > 64 or not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
            err(f"SKILL.md: `name` không hợp lệ: {name!r} (chữ thường, số, gạch ngang, ≤64)")
        if name != skill_dir.name:
            err(f"SKILL.md: `name` ({name}) không khớp tên thư mục ({skill_dir.name})")
        for reserved in ("anthropic", "claude"):
            if profile == "claude-code" and reserved in name.lower():
                err(f"SKILL.md: `name` chứa từ khóa bị cấm: {reserved!r}")

    desc = fields.get("description", "")
    if not isinstance(desc, str) or not desc.strip():
        err("SKILL.md: `description` phải là chuỗi không rỗng")
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

    for key, limit in (("compatibility", 500), ("license", None), ("allowed-tools", None)):
        if key in fields and (not isinstance(fields[key], str) or not fields[key].strip()
                              or (limit and len(fields[key]) > limit)):
            err(f"SKILL.md: `{key}` phải là chuỗi không rỗng" + (f", tối đa {limit} ký tự" if limit else ""))
    if "metadata" in fields:
        meta = fields["metadata"]
        if not isinstance(meta, dict) or any(not isinstance(v, str) for v in meta.values()):
            err("SKILL.md: `metadata` phải là mapping string → string")
    extra = set(fields) - SPEC_FRONTMATTER
    if extra:
        message = f"SKILL.md: field ngoài profile portable: {', '.join(sorted(extra))}"
        if profile == "portable":
            err(message)
        else:
            info(message + "; kiểm tra hỗ trợ ở phiên bản Claude Code đích")


def check_structure(skill_dir: Path, allow_dirs: set[str]) -> None:
    for child in sorted(skill_dir.iterdir()):
        if child.name.startswith("."):
            continue
        if child.is_dir():
            if child.name in SPEC_DIRS | CONVENTION_DIRS | allow_dirs:
                continue
            count = sum(1 for _ in child.rglob("*") if _.is_file())
            warn(f"quy ước nội bộ: xem lại thư mục {child.name}/ ({count} file); spec cho phép")
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


def without_fenced_code(text: str) -> str:
    opened = None
    lines = []
    for line in text.splitlines():
        match = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if match:
            marker, tail = match.groups()
            if opened is None:
                if marker[0] != "`" or "`" not in tail:
                    opened = (marker[0], len(marker))
                    continue
            elif marker[0] == opened[0] and len(marker) >= opened[1] and not tail.strip():
                opened = None
                continue
        if opened is None:
            lines.append(line)
    return "\n".join(lines)


def file_targets(text: str, include_inline: bool = True) -> set[str]:
    """Literal Markdown links and standalone inline-code paths, not shell commands."""
    text = without_fenced_code(text)
    targets = set()
    for raw in re.findall(r"\]\(([^)]+)\)", text):
        target = raw.strip().split(' "', 1)[0].strip("<>")
        parsed = urlsplit(target)
        if not parsed.scheme and not parsed.netloc and parsed.path:
            targets.add(unquote(parsed.path))
    for raw in re.findall(r"(?<!`)`([^`\n]+)`(?!`)", text) if include_inline else ():
        if re.fullmatch(r"[A-Za-z0-9_./-]+", raw) and "." in Path(raw).name:
            targets.add(raw)
    return {t for t in targets if not any(c in t for c in "<>*{}$") and not t.endswith("/")}


def resolve_target(skill_dir: Path, origin: Path, target: str) -> Path:
    # Documentation uses both paths from the current file and skill-root paths.
    local = (origin.parent / target).resolve()
    rooted = (skill_dir / target).resolve()
    if target.startswith(("./", "../")) or local.exists():
        return local
    return rooted if rooted.exists() else local


def resource_graph(skill_dir: Path, skill_text: str):
    root = skill_dir.resolve()
    start = root / "SKILL.md"
    reached = {start}
    edges = {}
    frontier = [(start, skill_text)]
    while frontier:
        origin, text = frontier.pop()
        edges[origin] = set()
        explicit_links = file_targets(text, include_inline=False)
        for target in sorted(file_targets(text)):
            path = resolve_target(root, origin, target)
            if not path.is_relative_to(root):
                warn(f"{origin.relative_to(root)}: tham chiếu ngoài skill: {target}")
                continue
            if not path.exists():
                if target in explicit_links:
                    err(f"{origin.relative_to(root)}: internal link gãy: {target}")
                continue
            if not path.is_file():
                continue
            edges[origin].add(path)
            if path not in reached:
                reached.add(path)
                if path.suffix == ".md" and path.relative_to(root).parts[0] not in {"examples", "assets", "tests", "evals"}:
                    try:
                        frontier.append((path, path.read_text(encoding="utf-8")))
                    except (UnicodeError, OSError) as exc:
                        err(f"Không đọc được {path}: {exc}")
    return reached, edges


def check_resources(skill_dir: Path, skill_text: str) -> None:
    reached, edges = resource_graph(skill_dir, skill_text)
    direct = edges.get(skill_dir / "SKILL.md", set())
    for origin in direct:
        for nested in edges.get(origin, set()):
            if nested.suffix == ".md" and nested not in direct:
                warn(f"reference gián tiếp: {nested.relative_to(skill_dir)}; cân nhắc link từ SKILL.md")
    # Only documentation is checked for orphans. Code imports and copied asset
    # dependencies need runtime tests, not basename/string-containment guesses.
    for path in sorted(skill_dir.rglob("*.md")):
        rel = path.relative_to(skill_dir)
        if any(part.startswith(".") or part == "__pycache__" for part in rel.parts):
            continue
        if path not in reached and path.name not in HUMAN_FILES and rel.parts[0] not in {"assets", "examples", "tests", "evals"}:
            warn(f"tài liệu chưa được tham chiếu: {rel}")


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


def main(argv: list[str]) -> int:
    errors.clear()
    warnings.clear()
    infos.clear()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir")
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--allow-dirs", default="")
    parser.add_argument("--profile", choices=("portable", "claude-code"), default="portable")
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return 0 if exc.code == 0 else 3
    strict = args.strict
    allow_dirs = {d.strip() for d in args.allow_dirs.split(",") if d.strip()}
    skill_dir = Path(args.skill_dir).resolve()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        print(f"Không tìm thấy {skill_md}")
        return 3

    text = skill_md.read_text(encoding="utf-8")
    fields, body = split_frontmatter(text)

    check_frontmatter(fields, skill_dir, args.profile)
    check_structure(skill_dir, allow_dirs)
    check_resources(skill_dir, text)
    check_sizes(skill_dir, body)
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
    try:
        sys.exit(main(sys.argv[1:]))
    except (OSError, UnicodeError) as exc:
        print(f"Không đọc được skill: {exc}", file=sys.stderr)
        sys.exit(3)

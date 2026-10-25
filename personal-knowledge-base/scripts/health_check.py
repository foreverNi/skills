#!/usr/bin/env python3
"""Structural health checks for a portable Markdown LLM Wiki.

Layout-agnostic: supports both the flat root layout
    ROOT/{SCHEMA.md,index.md,log.md,entities/,concepts/,comparisons/,queries/,raw/}
and the nested layout
    ROOT/wiki/{index.md,log.md,entities/,...} + ROOT/raw/

No third-party dependencies. Python 3.9+.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from datetime import date, datetime
from pathlib import Path
from typing import Iterable

PAGE_DIRS = ["entities", "concepts", "comparisons", "queries", "summaries", "topics", "people"]
SPECIAL_PAGES = {"index.md", "log.md", "health.md", "readme.md", "schema.md",
                 "knowledge_schema.md", "inbox.md"}
SKIP_DIRS = {"_archive", "raw", ".git", ".obsidian", ".trash", "node_modules", "assets"}

REQUIRED_FRONTMATTER = ["title", "created", "updated", "type", "tags", "sources"]
VALID_TYPES = {"entity", "concept", "comparison", "query", "summary", "topic", "person"}
TYPE_TO_DIR = {
    "entity": "entities",
    "person": "people",
    "concept": "concepts",
    "comparison": "comparisons",
    "query": "queries",
    "summary": "summaries",
    "topic": "topics",
}

LOG_HEADING_RE = re.compile(r"^##\s+\[(\d{4}-\d{2}-\d{2})\]\s+(.+?)\s*\|\s*(.+)$")
MD_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
WIKI_LINK_RE = re.compile(r"(?<!!)\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
TAG_LINE_RE = re.compile(r"^-\s+([A-Za-z0-9][A-Za-z0-9_-]*)\s*:\s*(.+)$")


@dataclass
class Finding:
    level: str
    code: str
    message: str
    path: str | None = None


@dataclass
class Report:
    root: Path
    page_root: Path
    layout: str
    findings: list[Finding] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)

    def add(self, level: str, code: str, message: str, path: Path | str | None = None) -> None:
        rel = None
        if path is not None:
            try:
                rel = str(Path(path).resolve().relative_to(self.root))
            except (ValueError, OSError):
                rel = str(path)
        self.findings.append(Finding(level, code, message, rel))

    @property
    def ok(self) -> bool:
        return not any(f.level == "error" for f in self.findings)

    def at(self, level: str) -> list[Finding]:
        return [f for f in self.findings if f.level == level]


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def detect_layout(root: Path) -> tuple[Path, str]:
    wiki = root / "wiki"
    if wiki.is_dir() and any((wiki / d).is_dir() for d in PAGE_DIRS):
        return wiki, "nested"
    if wiki.is_dir() and any(p.suffix == ".md" for p in wiki.iterdir() if p.is_file()):
        return wiki, "nested"
    return root, "flat"


def iter_pages(page_root: Path) -> list[Path]:
    pages: list[Path] = []
    for path in sorted(page_root.rglob("*.md")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(page_root).parts
        if any(part in SKIP_DIRS or part.startswith(".") for part in rel_parts[:-1]):
            continue
        if path.name.lower() in SPECIAL_PAGES:
            continue
        pages.append(path)
    return pages


# ---------------------------------------------------------------- frontmatter

def split_frontmatter(text: str) -> tuple[str | None, str]:
    if not text.startswith("---"):
        return None, text
    lines = text.splitlines()
    if lines[0].strip() != "---":
        return None, text
    for idx in range(1, len(lines)):
        if lines[idx].strip() in {"---", "..."}:
            return "\n".join(lines[1:idx]), "\n".join(lines[idx + 1:])
    return None, text


def parse_frontmatter(raw: str) -> dict[str, object]:
    data: dict[str, object] = {}
    current_key: str | None = None
    sequence: list[str] = []

    def flush() -> None:
        nonlocal current_key, sequence
        if current_key is not None and sequence:
            data[current_key] = sequence
        current_key, sequence = None, []

    for line in raw.splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        stripped = line.strip()
        if stripped.startswith("- ") or stripped == "-":
            if current_key is not None:
                value = stripped[1:].strip().strip("'\"")
                if value:
                    sequence.append(value)
            continue
        match = re.match(r"^([A-Za-z0-9_-]+)\s*:\s*(.*)$", line)
        if match:
            flush()
            key, value = match.group(1).lower(), match.group(2).strip()
            if value == "":
                current_key = key
                continue
            data[key] = parse_scalar(value)
            current_key = None
    flush()
    return data


def parse_scalar(value: str) -> object:
    value = value.strip()
    if value.startswith("[") and value.endswith("]"):
        inner = value[1:-1].strip()
        if not inner:
            return []
        return [v.strip().strip("'\"") for v in inner.split(",") if v.strip()]
    return value.strip("'\"")


def as_list(value: object) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    return [str(value)]


# ------------------------------------------------------------- schema parsing

def load_tag_taxonomy(schema_text: str) -> set[str]:
    tags: set[str] = set()
    in_section = False
    for line in schema_text.splitlines():
        if line.startswith("## "):
            in_section = "taxonomy" in line.lower() or "标签" in line
            continue
        if not in_section:
            continue
        if line.startswith("### "):
            continue
        match = TAG_LINE_RE.match(line.strip())
        if match:
            tags.add(match.group(1).lower())
    return tags


# ---------------------------------------------------------------- link index

def slugify(text: str) -> str:
    """把 [[Naval Ravikant]] / naval_ravikant 之类归一成 naval-ravikant。"""
    text = text.strip().lower()
    text = re.sub(r"[\s_]+", "-", text)
    return re.sub(r"-{2,}", "-", text).strip("-")


def build_link_index(pages: Iterable[Path], page_root: Path) -> dict[str, list[Path]]:
    index: dict[str, list[Path]] = {}
    for page in pages:
        index.setdefault(page.stem.lower(), []).append(page)
        slug = slugify(page.stem)
        if slug != page.stem.lower():
            index.setdefault(slug, []).append(page)
    return index


def resolve_target(target: str, page_root: Path, link_index: dict[str, list[Path]]) -> tuple[list[Path], str]:
    target = target.strip().strip("/")
    if target.endswith(".md"):
        target = target[:-3]
    if "/" in target:
        candidate = (page_root / f"{target}.md").resolve()
        return ([candidate] if candidate.exists() else []), "path"
    hits = link_index.get(target.lower(), [])
    if not hits:
        hits = link_index.get(slugify(target), [])
    return hits, "stem"


# -------------------------------------------------------------------- checks

def check_core(report: Report, schema_name: str, has_health: bool) -> None:
    required = [schema_name, "index.md", "log.md"]
    for name in required:
        if not (report.page_root / name).is_file():
            report.add("error", "missing-core-file", f"缺少核心文件: {name}", report.page_root / name)
    if not (report.root / "raw").is_dir():
        report.add("error", "missing-directory", "缺少 raw/ 目录（原始素材层）", report.root / "raw")
    if not has_health:
        report.add("info", "no-health-file", "尚无 health.md，首次体检后建议创建", report.page_root / "health.md")


def check_frontmatter(report: Report, pages: list[Path], taxonomy: set[str], strict: bool) -> None:
    level_fm = "error" if strict else "warning"
    for page in pages:
        text = read_text(page)
        raw, _body = split_frontmatter(text)
        if raw is None:
            report.add(level_fm, "missing-frontmatter", "页面缺少 YAML frontmatter", page)
            continue
        data = parse_frontmatter(raw)
        missing = [k for k in REQUIRED_FRONTMATTER if k not in data]
        empty = [k for k in REQUIRED_FRONTMATTER if k in data and not data.get(k)]
        if missing:
            report.add(level_fm, "frontmatter-missing-field", f"frontmatter 缺字段: {', '.join(missing)}", page)
        if empty:
            report.add("warning", "frontmatter-empty-field", f"frontmatter 字段为空: {', '.join(empty)}", page)
        for key in ("created", "updated"):
            value = str(data.get(key, ""))
            if value and not DATE_RE.match(value):
                report.add("warning", "frontmatter-bad-date", f"{key} 不是 YYYY-MM-DD: {value}", page)
        page_type = str(data.get("type", "")).strip().lower()
        if page_type and page_type not in VALID_TYPES:
            report.add("warning", "frontmatter-bad-type", f"未知 type: {page_type}", page)
        elif page_type and page_type != "summary":
            expected = TYPE_TO_DIR.get(page_type)
            actual_parent = page.parent.name if page.parent != report.page_root else ""
            if expected and actual_parent and actual_parent != expected and (report.page_root / expected).is_dir():
                report.add(
                    "info",
                    "type-dir-mismatch",
                    f"type={page_type} 但文件位于 {actual_parent}/（若 SCHEMA 允许「目录按主题、index 按 type」则无需处理）",
                    page,
                )
        if taxonomy:
            unknown = [t for t in as_list(data.get("tags")) if t.lower() not in taxonomy]
            if unknown:
                report.add(
                    "warning",
                    "tag-not-in-taxonomy",
                    f"标签不在 SCHEMA taxonomy 中: {', '.join(unknown)}（先加进 SCHEMA.md 再用）",
                    page,
                )
        for src in as_list(data.get("sources")):
            clean = src.strip().lstrip("./")
            if not clean or clean.startswith(("http://", "https://")):
                continue
            if not (report.root / clean).exists() and not (report.page_root / clean).exists():
                report.add("warning", "missing-source-file", f"sources 指向的文件不存在: {clean}", page)


def check_index(report: Report, pages: list[Path]) -> None:
    index_path = report.page_root / "index.md"
    if not index_path.is_file():
        return
    index_text = read_text(index_path)
    for page in pages:
        rel = page.relative_to(report.page_root).as_posix()
        if page.stem not in index_text and rel not in index_text:
            report.add("warning", "missing-index-entry", f"页面未登记到 index.md: {rel}", page)

    total_match = re.search(r"Total pages[:：]\s*(\d+)", index_text)
    if total_match:
        declared = int(total_match.group(1))
        if declared != len(pages):
            report.add(
                "warning",
                "index-count-mismatch",
                f"index.md 声明 Total pages: {declared}，实际 {len(pages)} 个页面",
                index_path,
            )


def check_links(report: Report, pages: list[Path]) -> None:
    link_index = build_link_index(pages, report.page_root)
    inbound: dict[Path, int] = {p.resolve(): 0 for p in pages}
    known_stems = {p.stem.lower() for p in pages}

    for page in pages:
        text = read_text(page)
        _raw, body = split_frontmatter(text)
        for match in WIKI_LINK_RE.finditer(body):
            target = match.group(1).strip()
            hits, mode = resolve_target(target, report.page_root, link_index)
            if not hits:
                suggestion = ""
                close = [s for s in known_stems if target.lower() in s or s in target.lower()]
                if close:
                    suggestion = f"（相近页面: {', '.join(sorted(close)[:3])}）"
                report.add("error", "broken-link", f"断链 `[[{target}]]` 无对应页面{suggestion}", page)
                continue
            if mode == "stem":
                if len(hits) > 1:
                    names = ", ".join(str(h.relative_to(report.page_root)) for h in hits)
                    report.add("warning", "ambiguous-link", f"`[[{target}]]` 匹配到多个页面: {names}", page)
                for hit in hits:
                    if hit.resolve() != page.resolve():
                        inbound[hit.resolve()] = inbound.get(hit.resolve(), 0) + 1

        for match in MD_LINK_RE.finditer(body):
            target = match.group(1).split("#")[0].split("?")[0].strip()
            if not target or target.startswith(("http://", "https://", "mailto:", "tel:", "#")):
                continue
            if not (page.parent / target).exists():
                report.add("warning", "broken-relative-link", f"相对链接目标不存在: {target}", page)

    for page in pages:
        if inbound.get(page.resolve(), 0) == 0:
            report.add("warning", "orphan-page", "孤儿页面：没有任何其他页面链接到它", page)


def check_log(report: Report, max_entries: int) -> None:
    log_path = report.page_root / "log.md"
    if not log_path.is_file():
        return
    entries = 0
    for lineno, line in enumerate(read_text(log_path).splitlines(), start=1):
        if not line.startswith("## "):
            continue
        if LOG_HEADING_RE.match(line):
            entries += 1
        else:
            report.add(
                "warning",
                "invalid-log-heading",
                f"log 标题格式不符（应为 `## [YYYY-MM-DD] action | subject`）第 {lineno} 行: {line[:60]}",
                log_path,
            )
    report.counts["log_entries"] = entries
    if entries > max_entries:
        report.add(
            "warning",
            "log-rotation-due",
            f"log 已有 {entries} 条（阈值 {max_entries}），建议轮换为 log-{date.today().year}.md",
            log_path,
        )


def check_page_size(report: Report, pages: list[Path], limit: int) -> None:
    for page in pages:
        lines = len(read_text(page).splitlines())
        if lines > limit:
            report.add("warning", "page-too-long", f"页面 {lines} 行（超过 {limit}），考虑拆分为子专题", page)


def load_ignore_patterns(root: Path) -> list[str]:
    """读取 KB 根目录的 .wikilintignore：每行一个 glob，用于排除语料目录/附件。"""
    ignore_file = root / ".wikilintignore"
    if not ignore_file.is_file():
        return []
    patterns = []
    for line in read_text(ignore_file).splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            patterns.append(line)
    return patterns


def is_ignored(rel_posix: str, patterns: list[str]) -> bool:
    from fnmatch import fnmatch

    return any(fnmatch(rel_posix, pattern) or rel_posix.startswith(pattern.rstrip("*").rstrip("/") + "/") for pattern in patterns)


def check_raw_usage(report: Report, pages: list[Path], ignore: list[str]) -> None:
    raw_dir = report.root / "raw"
    if not raw_dir.is_dir():
        return
    raw_files = [
        p for p in sorted(raw_dir.rglob("*"))
        if p.is_file() and not any(part.startswith(".") for part in p.relative_to(raw_dir).parts)
    ]
    report.counts["raw_files"] = len(raw_files)
    if not raw_files:
        return
    corpus = "\n".join(read_text(p) for p in pages)
    log_path = report.page_root / "log.md"
    if log_path.is_file():
        corpus += "\n" + read_text(log_path)
    unreferenced: list[str] = []
    ignored_count = 0
    for raw in raw_files:
        rel = raw.relative_to(report.root).as_posix()
        if is_ignored(rel, ignore):
            ignored_count += 1
            continue
        if raw.name not in corpus and rel not in corpus:
            unreferenced.append(rel)
    report.counts["unreferenced_raw"] = len(unreferenced)
    report.counts["ignored_raw"] = ignored_count
    if unreferenced:
        sample = ", ".join(unreferenced[:5])
        more = f" 等 {len(unreferenced)} 个" if len(unreferenced) > 5 else ""
        report.add(
            "warning",
            "unreferenced-raw-source",
            f"{len(unreferenced)} 个原始素材未被任何页面或 log 引用（{sample}{more}）",
            raw_dir,
        )


def check_stale(report: Report, pages: list[Path], stale_days: int) -> None:
    if stale_days <= 0:
        return
    today = date.today()
    stale = 0
    for page in pages:
        raw, _ = split_frontmatter(read_text(page))
        if raw is None:
            continue
        updated = str(parse_frontmatter(raw).get("updated", ""))
        if not DATE_RE.match(updated):
            continue
        try:
            delta = (today - datetime.strptime(updated, "%Y-%m-%d").date()).days
        except ValueError:
            continue
        if delta > stale_days:
            stale += 1
    report.counts["stale_pages"] = stale
    if stale:
        report.add(
            "info",
            "stale-candidates",
            f"{stale} 个页面 updated 早于 {stale_days} 天前，可考虑复核（非错误）",
            report.page_root,
        )


def check_contradictions(report: Report, pages: list[Path]) -> None:
    stems = {p.stem.lower() for p in pages}
    for page in pages:
        raw, _ = split_frontmatter(read_text(page))
        if raw is None:
            continue
        for ref in as_list(parse_frontmatter(raw).get("contradictions")):
            if ref.lower() not in stems:
                report.add("warning", "bad-contradiction-ref", f"contradictions 指向不存在的页面: {ref}", page)


# ----------------------------------------------------------------------- main

def build_report(root: Path, strict: bool, size_limit: int, stale_days: int, max_log: int) -> Report:
    root = root.resolve()
    page_root, layout = detect_layout(root)
    report = Report(root=root, page_root=page_root, layout=layout)
    pages = iter_pages(page_root)
    schema_name = "SCHEMA.md" if (page_root / "SCHEMA.md").is_file() else "KNOWLEDGE_SCHEMA.md"
    has_health = (page_root / "health.md").is_file() or (root / "health.md").is_file()

    report.counts.update(
        {
            "layout": layout,
            "pages": len(pages),
            "entities": sum(1 for p in pages if p.parent.name == "entities"),
            "concepts": sum(1 for p in pages if p.parent.name == "concepts"),
            "comparisons": sum(1 for p in pages if p.parent.name == "comparisons"),
            "queries": sum(1 for p in pages if p.parent.name == "queries"),
        }
    )

    check_core(report, schema_name, has_health)
    schema_path = page_root / schema_name
    taxonomy = load_tag_taxonomy(read_text(schema_path)) if schema_path.is_file() else set()
    report.counts["taxonomy_tags"] = len(taxonomy)

    check_frontmatter(report, pages, taxonomy, strict)
    check_index(report, pages)
    check_links(report, pages)
    check_log(report, max_log)
    check_page_size(report, pages, size_limit)
    check_raw_usage(report, pages, load_ignore_patterns(root))
    check_stale(report, pages, stale_days)
    check_contradictions(report, pages)
    return report


def print_text(report: Report) -> None:
    c = report.counts
    print(f"LLM Wiki 结构体检: {'OK' if report.ok else 'ERROR'}")
    print(f"根目录: {report.root}")
    print(f"页面根: {report.page_root} (layout={report.layout})")
    print(
        "统计: 页面 {pages} (entities {entities} / concepts {concepts} / comparisons {comparisons} / queries {queries}) | "
        "raw {raw} | taxonomy {tax} 个标签 | log {log} 条".format(
            pages=c.get("pages", 0),
            entities=c.get("entities", 0),
            concepts=c.get("concepts", 0),
            comparisons=c.get("comparisons", 0),
            queries=c.get("queries", 0),
            raw=c.get("raw_files", 0),
            tax=c.get("taxonomy_tags", 0),
            log=c.get("log_entries", 0),
        )
    )
    if not report.findings:
        print("\n无结构性问题。")
        return
    for level in ("error", "warning", "info"):
        items = report.at(level)
        if not items:
            continue
        print(f"\n[{level.upper()}] {len(items)} 项")
        for item in items:
            loc = f" [{item.path}]" if item.path else ""
            print(f"- {item.code}{loc}: {item.message}")
    errors, warnings = len(report.at("error")), len(report.at("warning"))
    print(f"\n汇总: {errors} error / {warnings} warning / {len(report.at('info'))} info")


def main() -> int:
    parser = argparse.ArgumentParser(description="LLM Wiki 结构体检（无第三方依赖）")
    parser.add_argument("--root", default=str(Path.home() / "Projects" / "LLMWiki"), help="知识库根目录")
    parser.add_argument("--strict", action="store_true", help="frontmatter 问题升级为 error")
    parser.add_argument("--size-limit", type=int, default=200, help="页面行数上限（默认 200）")
    parser.add_argument("--stale-days", type=int, default=180, help="过时提示阈值天数（0 关闭）")
    parser.add_argument("--max-log", type=int, default=500, help="log 轮换阈值条数")
    parser.add_argument("--json", action="store_true", help="输出 JSON")
    args = parser.parse_args()

    root = Path(args.root).expanduser()
    if not root.is_dir():
        print(f"根目录不存在: {root}", file=sys.stderr)
        return 2

    report = build_report(root, args.strict, args.size_limit, args.stale_days, args.max_log)
    if args.json:
        print(
            json.dumps(
                {
                    "ok": report.ok,
                    "root": str(report.root),
                    "page_root": str(report.page_root),
                    "layout": report.layout,
                    "counts": report.counts,
                    "findings": [f.__dict__ for f in report.findings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print_text(report)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

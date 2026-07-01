#!/usr/bin/env python3
"""Structural health checks for a portable Markdown LLM Wiki."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable


CORE_FILES = [
    "KNOWLEDGE_SCHEMA.md",
    "wiki/index.md",
    "wiki/log.md",
    "wiki/health.md",
]

SPECIAL_WIKI_FILES = {
    "index.md",
    "log.md",
    "health.md",
}

LOG_HEADING_RE = re.compile(
    r"^## \[\d{4}-\d{2}-\d{2}\] (ingest|query-filed|health|maintenance) \| .+"
)
MD_LINK_RE = re.compile(r"(?<!!)\[[^\]]+\]\(([^)]+)\)")
WIKI_LINK_RE = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")


@dataclass
class Finding:
    level: str
    code: str
    message: str
    path: str | None = None


@dataclass
class Report:
    root: Path
    findings: list[Finding] = field(default_factory=list)
    counts: dict[str, int] = field(default_factory=dict)

    def add(self, level: str, code: str, message: str, path: Path | str | None = None) -> None:
        rel_path = None
        if path is not None:
            path_obj = Path(path)
            try:
                rel_path = str(path_obj.relative_to(self.root))
            except ValueError:
                rel_path = str(path_obj)
        self.findings.append(Finding(level, code, message, rel_path))

    @property
    def ok(self) -> bool:
        return not any(item.level == "error" for item in self.findings)


def iter_markdown_files(path: Path) -> Iterable[Path]:
    if not path.exists():
        return []
    return sorted(p for p in path.rglob("*.md") if p.is_file())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def normalize_link_target(link: str) -> str | None:
    target = link.strip()
    if not target or target.startswith(("#", "http://", "https://", "mailto:", "tel:")):
        return None
    return target.split("#", 1)[0].split("?", 1)[0].strip()


def resolve_markdown_link(source_file: Path, target: str) -> Path:
    return (source_file.parent / target).resolve()


def resolve_wiki_link(wiki_dir: Path, target: str) -> Path:
    target = target.strip()
    if not target.endswith(".md"):
        target = f"{target}.md"
    return (wiki_dir / target).resolve()


def collect_links(root: Path, wiki_files: list[Path]) -> tuple[dict[Path, set[Path]], list[tuple[Path, str, Path]]]:
    links: dict[Path, set[Path]] = {path.resolve(): set() for path in wiki_files}
    broken: list[tuple[Path, str, Path]] = []
    wiki_dir = root / "wiki"

    for path in wiki_files:
        text = read_text(path)
        for match in MD_LINK_RE.finditer(text):
            raw_target = normalize_link_target(match.group(1))
            if raw_target is None:
                continue
            resolved = resolve_markdown_link(path, raw_target)
            links[path.resolve()].add(resolved)
            if not resolved.exists():
                broken.append((path, match.group(1), resolved))
        for match in WIKI_LINK_RE.finditer(text):
            resolved = resolve_wiki_link(wiki_dir, match.group(1))
            links[path.resolve()].add(resolved)
            if not resolved.exists():
                broken.append((path, match.group(0), resolved))
    return links, broken


def check_core(report: Report) -> None:
    for directory in ["raw", "wiki", "agent-skills/personal-knowledge-base"]:
        path = report.root / directory
        if not path.is_dir():
            report.add("error", "missing-directory", f"Missing required directory: {directory}", path)
    for file_name in CORE_FILES:
        path = report.root / file_name
        if not path.is_file():
            report.add("error", "missing-core-file", f"Missing required file: {file_name}", path)


def check_index(report: Report, wiki_files: list[Path]) -> None:
    index_path = report.root / "wiki/index.md"
    if not index_path.exists():
        return
    index_text = read_text(index_path)
    for page in wiki_files:
        if page.name in SPECIAL_WIKI_FILES:
            continue
        rel_from_wiki = page.relative_to(report.root / "wiki").as_posix()
        if rel_from_wiki not in index_text and page.name not in index_text:
            report.add(
                "warning",
                "missing-index-entry",
                f"Wiki page is not listed in wiki/index.md: {rel_from_wiki}",
                page,
            )


def check_log(report: Report) -> None:
    log_path = report.root / "wiki/log.md"
    if not log_path.exists():
        return
    for line_number, line in enumerate(read_text(log_path).splitlines(), start=1):
        if line.startswith("## ") and not LOG_HEADING_RE.match(line):
            report.add(
                "warning",
                "invalid-log-heading",
                f"Log heading does not match expected format at line {line_number}: {line}",
                log_path,
            )


def check_links_and_orphans(report: Report, wiki_files: list[Path]) -> None:
    links, broken = collect_links(report.root, wiki_files)
    for source, raw_target, resolved in broken:
        report.add(
            "error",
            "broken-link",
            f"Broken link target `{raw_target}` resolves to `{resolved}`",
            source,
        )

    inbound: dict[Path, int] = {path.resolve(): 0 for path in wiki_files}
    for source, targets in links.items():
        for target in targets:
            if target in inbound and target != source:
                inbound[target] += 1

    for page in wiki_files:
        if page.name in SPECIAL_WIKI_FILES:
            continue
        if inbound.get(page.resolve(), 0) == 0:
            report.add("warning", "orphan-page", "Wiki page has no inbound links", page)


def check_raw_references(report: Report, wiki_files: list[Path]) -> None:
    raw_dir = report.root / "raw"
    if not raw_dir.exists():
        return
    raw_files = sorted(path for path in raw_dir.rglob("*") if path.is_file())
    if not raw_files:
        return

    wiki_text = "\n".join(read_text(path) for path in wiki_files)
    log_path = report.root / "wiki/log.md"
    if log_path.exists():
        wiki_text += "\n" + read_text(log_path)

    for raw_file in raw_files:
        rel_root = raw_file.relative_to(report.root).as_posix()
        rel_from_wiki = Path("..") / raw_file.relative_to(report.root)
        if rel_root not in wiki_text and rel_from_wiki.as_posix() not in wiki_text:
            report.add("warning", "unreferenced-raw-source", "Raw source is not referenced by wiki pages or log", raw_file)


def build_report(root: Path) -> Report:
    root = root.resolve()
    report = Report(root=root)
    check_core(report)

    wiki_files = list(iter_markdown_files(root / "wiki"))
    raw_files = sorted(path for path in (root / "raw").rglob("*") if path.is_file()) if (root / "raw").exists() else []

    report.counts = {
        "wiki_markdown_files": len(wiki_files),
        "raw_files": len(raw_files),
    }

    check_index(report, wiki_files)
    check_log(report)
    check_links_and_orphans(report, wiki_files)
    check_raw_references(report, wiki_files)
    return report


def print_text_report(report: Report) -> None:
    status = "OK" if report.ok else "ERROR"
    print(f"Knowledge base structural health: {status}")
    print(f"Root: {report.root}")
    print(f"Wiki markdown files: {report.counts.get('wiki_markdown_files', 0)}")
    print(f"Raw files: {report.counts.get('raw_files', 0)}")
    if not report.findings:
        print("No structural findings.")
        return
    print()
    for item in report.findings:
        location = f" [{item.path}]" if item.path else ""
        print(f"- {item.level.upper()} {item.code}{location}: {item.message}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run structural checks for a Markdown LLM Wiki.")
    parser.add_argument("--root", default=".", help="Knowledge base root directory.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of text.")
    args = parser.parse_args()

    report = build_report(Path(args.root))
    if args.json:
        print(
            json.dumps(
                {
                    "ok": report.ok,
                    "root": str(report.root),
                    "counts": report.counts,
                    "findings": [item.__dict__ for item in report.findings],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print_text_report(report)
    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

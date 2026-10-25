#!/usr/bin/env python3
"""Scaffold a portable Markdown LLM Wiki.

Creates the directory tree, SCHEMA.md (from references/schema-template.md),
index.md / log.md / health.md, and a .gitignore. Never overwrites existing
files unless --force is given.
"""

from __future__ import annotations

import argparse
import subprocess
from datetime import date
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
TEMPLATE = SKILL_DIR / "references" / "schema-template.md"

SUBDIRS = [
    "entities",
    "concepts",
    "comparisons",
    "queries",
    "raw/articles",
    "raw/papers",
    "raw/transcripts",
    "raw/assets",
    "_archive",
]

INDEX_MD = """# Wiki Index

> 内容目录。每个 Wiki 页面按类型分类，附一行摘要。
> 查找相关页面时先读此文件。
> Last updated: {today} | Total pages: 0

## Entities
<!-- 按字母顺序排列 -->

## Concepts
<!-- 按字母顺序排列 -->

## Comparisons
<!-- 按字母顺序排列 -->

## Queries
<!-- 按字母顺序排列 -->

## Root Pages
<!-- 跨类别综合页 -->
"""

LOG_MD = """# Wiki Log

> 所有 Wiki 操作的按时间顺序记录。仅追加，不删除。
> 格式：`## [YYYY-MM-DD] action | subject`
> Actions: init, ingest, update, query-filed, health, maintenance, archive
> 超过 500 条时轮换：重命名为 log-{{year}}.md，新建空白 log.md
> 历史条目的页面名用反引号而非 `[[wikilink]]`，避免过期链接污染体检

## [{today}] init | Wiki initialized

- Domain: {domain}
- Structure: SCHEMA.md / index.md / log.md / entities / concepts / comparisons / queries / raw / _archive
- Total pages: 0→0
"""

HEALTH_MD = """# Wiki Health

> 每次体检后覆盖更新时间、结构问题、语义问题和建议动作。
> 结构部分由 health_check.py 生成，语义部分由 Agent 补充。历史体检结论保留最近 3 次。

## {today}

### 结构

- 尚未运行体检。执行：`python3 ~/.workbuddy/skills/personal-knowledge-base/scripts/health_check.py --root .`

### 语义

- 待补充

### 建议动作

- 待补充
"""

GITIGNORE = """.DS_Store
.obsidian/workspace.json
.obsidian/cache
.trash/
*.tmp
"""

WIKILINTIGNORE = """# 体检忽略清单：每行一个 glob，命中的 raw 文件不计入「未被引用」告警。
# 语料/整本书/附件不适合逐篇要求被 wiki 引用，按需打开下面几行。
# raw/dive-into-llms/**
# raw/book/**
# raw/assets/**
"""


def write_file(path: Path, content: str, force: bool, created: list[Path], skipped: list[Path]) -> None:
    if path.exists() and not force:
        skipped.append(path)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    created.append(path)


def main() -> int:
    parser = argparse.ArgumentParser(description="初始化一个 LLM Wiki 知识库")
    parser.add_argument("--root", required=True, help="知识库根目录")
    parser.add_argument("--domain", default="待定义：请编辑 SCHEMA.md 的 Domain 一节", help="知识库覆盖的领域")
    parser.add_argument("--force", action="store_true", help="覆盖已存在的文件（谨慎）")
    parser.add_argument("--git", action="store_true", help="同时在根目录 git init")
    args = parser.parse_args()

    root = Path(args.root).expanduser().resolve()
    today = date.today().isoformat()
    created: list[Path] = []
    skipped: list[Path] = []

    root.mkdir(parents=True, exist_ok=True)
    for sub in SUBDIRS:
        path = root / sub
        if not path.is_dir():
            path.mkdir(parents=True, exist_ok=True)
            created.append(path)

    if not TEMPLATE.is_file():
        print(f"缺少模板文件: {TEMPLATE}")
        return 2
    schema = TEMPLATE.read_text(encoding="utf-8")
    schema = schema.replace("{{DOMAIN}}", args.domain).replace("{{DATE}}", today)

    write_file(root / "SCHEMA.md", schema, args.force, created, skipped)
    write_file(root / "index.md", INDEX_MD.format(today=today), args.force, created, skipped)
    write_file(root / "log.md", LOG_MD.format(today=today, domain=args.domain), args.force, created, skipped)
    write_file(root / "health.md", HEALTH_MD.format(today=today), args.force, created, skipped)
    write_file(root / ".gitignore", GITIGNORE, args.force, created, skipped)
    write_file(root / ".wikilintignore", WIKILINTIGNORE, args.force, created, skipped)

    print(f"知识库根目录: {root}")
    print(f"已创建 {len(created)} 项:")
    for path in created:
        print(f"  + {path.relative_to(root) if path != root else '.'}")
    if skipped:
        print(f"已跳过 {len(skipped)} 项（已存在，需 --force 覆盖）:")
        for path in skipped:
            print(f"  = {path.relative_to(root)}")

    if args.git and not (root / ".git").exists():
        try:
            subprocess.run(["git", "init", "-q", str(root)], check=True)
            print("已初始化 git 仓库（尚未提交）")
        except (subprocess.CalledProcessError, FileNotFoundError) as exc:
            print(f"git init 失败: {exc}")

    print("\n下一步:")
    print(f"  1. 编辑 {root / 'SCHEMA.md'} 的 Domain 与 Tag Taxonomy")
    print(f"  2. 跑一次体检: python3 {SKILL_DIR / 'scripts' / 'health_check.py'} --root {root}")
    print("  3. 开始第一次 ingest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

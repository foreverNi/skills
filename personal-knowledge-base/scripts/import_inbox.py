#!/usr/bin/env python3
"""收件箱去重器 —— 把一批链接整理成"待入库清单"。

用途：微信收藏、浏览器书签、群里转来的链接，先统一倒进 KB 根目录的
`inbox.md`，再用本脚本做 URL 归一 + 全库查重，输出干净的待办清单。

公众号链接的关键坑：同一篇文章，每次分享出来的 `chksm` 参数都不同，
`&scene=`、`#rd` 之类也常变。所以查重必须按 `__biz + mid + idx + sn`
归一，否则同一篇会被反复入库。

用法：
  python3 import_inbox.py --root ~/Projects/LLMWiki              # 扫描并整理
  python3 import_inbox.py --root ~/Projects/LLMWiki --dry-run    # 只看结果不写文件
  python3 import_inbox.py --root ~/Projects/LLMWiki --json       # 机器可读
  python3 import_inbox.py --root ~/Projects/LLMWiki --add URL    # 往收件箱追加一条

无第三方依赖。
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

URL_RE = re.compile(r"https?://[^\s<>\)\]\"'，。；、]+")
MD_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\)]+)\)")
WEIXIN_WANTED = ["__biz", "mid", "idx", "sn", "chksm"]
# 分享/追踪参数，一律丢弃后再比较
DROP_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "spm", "from", "scene", "share_token", "share_from", "isappinstalled",
    "clicktime", "enterid", "ascene", "devicetype", "version", "nettype",
    "abtest_cookie", "key", "pass_ticket", "wx_header", "exportkey",
    "fbclid", "gclid", "ref", "ref_src", "source",
}
LEDGER_NAME = ".ingest-ledger.json"
INBOX_NAME = "inbox.md"
SKIP_DIRS = {".git", "_archive", "node_modules", ".obsidian", ".trash"}

INBOX_HEADER = """# 收件箱

> 把要入库的文章链接贴到下面的列表里，然后说「导入收件箱」。
> 格式：`- 标题 | 链接`，标题可以省略。已入库的条目会自动打勾并标注落点。
> 同一篇文章的公众号链接即使 `chksm` 参数不同，也只会算一条。

"""


def normalize_url(url: str) -> str:
    """归一化 URL：去 fragment、去追踪参数、公众号按 biz/mid/idx/sn 重排。"""
    url = url.strip().rstrip(".,;:，。；）)")
    parts = urlsplit(url)
    host = (parts.netloc or "").lower()
    if host.startswith("www."):
        host = host[4:]
    pairs = parse_qsl(parts.query, keep_blank_values=False)
    if host == "mp.weixin.qq.com":
        keep = {k: v for k, v in pairs if k in WEIXIN_WANTED and k != "chksm"}
        ordered = [(k, keep[k]) for k in ("__biz", "mid", "idx", "sn") if k in keep]
        query = urlencode(ordered)
    else:
        kept = [(k, v) for k, v in pairs if k.lower() not in DROP_PARAMS
                and not k.lower().startswith("utm_")]
        query = urlencode(sorted(kept))
    path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.lower() or "https", host, path, query, ""))


def slug_from(title: str, url: str, norm: str = "") -> str:
    base = title.strip()
    if not base:
        parts = urlsplit(norm or url)
        host = parts.netloc.replace("www.", "")
        if host == "mp.weixin.qq.com":
            q = dict(parse_qsl(parts.query))
            base = f"wx-{q.get('mid', 'na')}-{q.get('idx', '1')}"
        else:
            seg = parts.path.rstrip("/").split("/")[-1]
            base = seg if seg and seg not in {"s", "index", "index.html"} else host
    base = re.sub(r"[\\/:*?\"<>|#\[\]（）()【】]", " ", base)
    base = re.sub(r"\s+", "-", base.strip()).strip("-").lower()
    return (base[:60] or "untitled")


def is_cjk(ch: str) -> bool:
    return "\u4e00" <= ch <= "\u9fff"


def load_known_urls(root: Path) -> dict[str, str]:
    """扫描全库 markdown，把出现过的 URL 映射到它所在的文件。"""
    known: dict[str, str] = {}
    for path in root.rglob("*.md"):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name == INBOX_NAME:
            continue
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for m in URL_RE.finditer(text):
            key = normalize_url(m.group(0))
            known.setdefault(key, path.relative_to(root).as_posix())
    return known


def load_ledger(root: Path) -> dict[str, dict]:
    path = root / LEDGER_NAME
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def save_ledger(root: Path, ledger: dict[str, dict]) -> None:
    (root / LEDGER_NAME).write_text(
        json.dumps(ledger, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def parse_entries(lines: list[str]) -> list[dict]:
    """从收件箱的行里提取条目。保持行号，便于原地改写。"""
    entries: list[dict] = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if not stripped or stripped.startswith(("#", ">")):
            continue
        checked = None
        if re.match(r"^[-*]\s*\[[ xX]\]", stripped):
            checked = "x" in stripped[:8].lower()
        md = MD_LINK_RE.search(stripped)
        if md:
            title, url = md.group(1).strip(), md.group(2)
        else:
            found = URL_RE.search(stripped)
            if not found:
                continue
            url = found.group(0)
            before = stripped[: found.start()].strip(" -*[]()")
            before = re.sub(r"^\[[ xX]\]\s*", "", before).strip(" |—-·:：")
            title = before
        if title and title.lower() in {"http", "https"}:
            title = ""
        title = re.sub(r"（已在库[^）]*）", "", title).strip()
        entries.append({"line": idx, "title": title, "url": url,
                        "norm": normalize_url(url), "checked": checked})
    return entries


def rewrite_inbox(path: Path, lines: list[str], results: list[dict]) -> str:
    """原地打勾 + 标注落点，保留用户原有格式。"""
    out = list(lines)
    for r in results:
        if r["status"] not in {"known", "duplicate"}:
            continue
        line = out[r["line"]]
        if r["status"] == "known":
            note = f"（已在库：{r['where']}）"
        else:
            note = f"（{r['where']}）"
        if "（已在库" in line or re.search(r"（与第 \d+ 行重复）", line):
            new = re.sub(r"（(?:已在库|与第)[^）]*）", note, line)
        else:
            new = line.rstrip() + " " + note
        if re.match(r"^(\s*)[-*]\s*\[ \]", new):
            new = re.sub(r"^(\s*[-*]\s*)\[ \]", r"\1[x]", new, count=1)
        elif re.match(r"^(\s*)[-*]\s+[^\[]", new):
            new = re.sub(r"^(\s*[-*]\s+)", r"\1[x] ", new, count=1)
        out[r["line"]] = new if new.endswith("\n") else new + "\n"
    path.write_text("".join(out), encoding="utf-8")
    return path.as_posix()


def ensure_inbox(root: Path) -> Path:
    path = root / INBOX_NAME
    if not path.is_file():
        path.write_text(INBOX_HEADER, encoding="utf-8")
    return path


def main() -> int:
    ap = argparse.ArgumentParser(description="收件箱去重器")
    ap.add_argument("--root", required=True, help="知识库根目录")
    ap.add_argument("--dry-run", action="store_true", help="只报告，不写任何文件")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    ap.add_argument("--add", action="append", default=[], metavar="URL",
                    help="往收件箱追加一条（可重复）")
    args = ap.parse_args()

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir():
        print(f"目录不存在：{root}", file=sys.stderr)
        return 2

    inbox = ensure_inbox(root)
    if args.add:
        existing = inbox.read_text(encoding="utf-8")
        if not existing.endswith("\n"):
            existing += "\n"
        for url in args.add:
            existing += f"- [ ] {url}\n"
        inbox.write_text(existing, encoding="utf-8")

    lines = inbox.read_text(encoding="utf-8").splitlines(keepends=True)
    entries = parse_entries(lines)
    known = load_known_urls(root)
    ledger = load_ledger(root)

    results: list[dict] = []
    seen: dict[str, int] = {}
    for e in entries:
        norm = e["norm"]
        if norm in known:
            status, where = "known", known[norm]
        elif norm in ledger and ledger[norm].get("raw"):
            # 只有登记了落盘路径才算已入库；只排队未落盘的仍算待办
            status, where = "known", ledger[norm]["raw"]
        elif norm in seen:
            status, where = "duplicate", f"与第 {seen[norm] + 1} 行重复"
        else:
            status, where = "new", ""
        if norm not in seen:
            seen[norm] = e["line"]
        results.append({**e, "status": status, "where": where,
                        "slug": slug_from(e["title"], e["url"])})

    if not args.dry_run:
        rewrite_inbox(inbox, lines, results)
        for r in results:
            if r["status"] == "new" and r["norm"] not in ledger:
                ledger[r["norm"]] = {"title": r["title"], "url": r["url"],
                                     "slug": r["slug"], "raw": ""}
        save_ledger(root, ledger)

    new = [r for r in results if r["status"] == "new"]
    dup = [r for r in results if r["status"] == "duplicate"]
    kn = [r for r in results if r["status"] == "known"]

    if args.json:
        print(json.dumps({
            "root": root.as_posix(),
            "counts": {"new": len(new), "known": len(kn), "duplicate": len(dup)},
            "new": [{k: r[k] for k in ("title", "url", "slug", "line")} for r in new],
            "known": [{k: r[k] for k in ("title", "url", "where")} for r in kn],
            "duplicate": [{k: r[k] for k in ("title", "url", "where")} for r in dup],
        }, ensure_ascii=False, indent=2))
        return 0

    print(f"收件箱：{inbox}")
    print(f"新增 {len(new)} 条 | 已在库 {len(kn)} 条 | 箱内重复 {len(dup)} 条")
    if new:
        print("\n待入库：")
        for i, r in enumerate(new, 1):
            label = r["title"] or "（无标题）"
            print(f"  {i}. {label}")
            print(f"     {r['url']}")
            print(f"     → raw/articles/{r['slug']}.md")
    if kn:
        print("\n已在库（已打勾）：")
        for r in kn:
            print(f"  - {r['title'] or r['url']} → {r['where']}")
    if dup:
        print("\n箱内重复（同一篇贴了多次）：")
        for r in dup:
            print(f"  - {r['url']}  {r['where']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

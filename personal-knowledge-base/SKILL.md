---
name: personal-knowledge-base
description: |
  维护可移植的 Markdown LLM Wiki 个人知识库（Karpathy LLM Wiki 模式）：把文章、链接、段落、文件、灵感 ingested 成带交叉引用的持久 wiki 页面，并做结构与语义体检。触发语：「把这个加入知识库 / 把这段加入知识库 / 加入知识库 / 存进知识库 / 收录这篇 / 摄入这篇 / 归档到知识库 / 记到知识库 / 存到 wiki / 加进我的 wiki / 沉淀一下这篇」「检查知识库健康状态 / 体检 wiki / 找断链 / 找孤儿页面 / 有没有过时内容 / 矛盾」「我的 wiki 里关于 X 有哪些页面」。默认库根目录 ~/Projects/LLMWiki。默认先出确认稿再落盘；用户说「直接加 / 不用确认」则跳过确认直接执行完整 ingest 流程。
description_en: |
  Maintain a portable personal Markdown LLM Wiki (Karpathy LLM Wiki pattern). Use when the user wants to ingest an article, URL, file, note or idea into their knowledge base ("add this to my knowledge base", "save this to my wiki", "ingest this"), or asks to check knowledge base health — broken links, orphan pages, stale claims, missing index entries, tag drift, contradictions. Default KB root: ~/Projects/LLMWiki. Defaults to showing a confirmation draft before writing; skip confirmation when the user says "just add it".
---

# Personal Knowledge Base

## 库位置与首次定位（每次会话必做）

- **默认根目录**：`~/Projects/LLMWiki`。用户指定了别的路径就用指定的。
- 根目录下的关键文件：`SCHEMA.md`（宪法）、`index.md`（内容目录）、`log.md`（操作日志）、`health.md`（体检报告）。
- 页面目录：`entities/`、`concepts/`、`comparisons/`、`queries/`，跨类别综合页可放根目录；原始素材在 `raw/`（含 `articles/ papers/ transcripts/ assets/`）；废弃页在 `_archive/`。
- 两种布局都支持：页面直接在根目录下（flat），或全部收在 `wiki/` 子目录内（nested）。用体检脚本输出的 `layout=` 确认，不要假设。

**在任何写入之前，按顺序读**：`SCHEMA.md` → `index.md` → `log.md` 最近 20-30 条。跳过这一步会导致重复建页、漏交叉引用、违反约定、重复记录已做的工作。

原理与完整方法论见 `references/llm-wiki-pattern.md`；架构要点见 `references/llm-wiki-principles.md`；新库模板见 `references/schema-template.md`。

## 安全规则

- 未经用户确认不写入新知识（用户明确说「不用确认，直接加」时除外）。
- 永不修改或删除 `raw/` 里的文件 —— 它是事实来源。修正写在 wiki 页面里。
- 不编造引用、来源元数据，或不来自素材/现有页面的论断。
- 不把密钥、密码、token、无关隐私写进 wiki。
- 单次 ingest 不做大范围重写，改动只限当前素材及相关页面。
- 不静默解决矛盾 —— 标出双方立场与来源日期，交用户裁决。

## 工作流 A：初始化新库

仅当根目录不存在或缺少 `SCHEMA.md` / `index.md` / `log.md` 时执行。

1. 确认根目录路径与知识库领域（Domain）。领域决定 tag taxonomy，必须问清，不要替我猜。
2. 跑脚手架（不覆盖已存在文件）：

   ```bash
   python3 ~/.workbuddy/skills/personal-knowledge-base/scripts/init_kb.py --root <KB_ROOT> --domain "<领域描述>"
   ```

3. 按领域改写 `SCHEMA.md` 的 `Domain` 与 `Tag Taxonomy` 两节（10-20 个顶级标签为宜）。
4. 跑一次体检确认基线为 OK，再开始首次 ingest。
5. 已存在的库**不要**跑 init —— 直接进工作流 B / D。

## 工作流 B：加知识（ingest）

触发语：「帮我把这个加入知识库」「把这段加入知识库」「存进知识库」「收录这篇」「摄入这篇」「归档到知识库」「加进我的 wiki」「存到 wiki」「沉淀一下这篇」「add this to my knowledge base」。

**两种执行模式**（先判断，再决定要不要停）：

| 模式 | 判定 | 行为 |
|---|---|---|
| 确认稿模式（默认） | 用户没明说 | 走到第 3 步出确认稿，**等用户点头**再落盘 |
| 直接落盘模式 | 用户说「直接加 / 不用确认 / 别问了 / 全部自动」 | 跳过第 4 步的等待，按 3→9 一次跑完，最后回报改动清单 |

不论哪种模式，第 5-9 步（存 raw → 建/改页面 → 更新 index → 追加 log → 体检自检 → 回报）都必须完整执行，不能只建一个页面就结束。

1. **确认素材存在**。用户没给正文、URL、本地文件路径或足够上下文时，先要素材。URL 用 WebFetch 抓成 markdown；本地文件用 Read 读取。
2. **定位**：读 `SCHEMA.md`、`index.md`、`log.md` 近期条目；用 Grep 在页面目录搜素材里出现的关键实体/概念，检查是否已有页面（注意文件名可能略有差异，应合并而非新建）。
3. **出确认稿**（写在对话里，不要先落盘）：
   - 拟定标题与 slug（小写连字符；中文专名可直接中文）
   - 素材类型与 raw 存放路径（`raw/articles/<slug>-<year>.md` 等）
   - 3-6 行摘要
   - tags（必须来自 SCHEMA 的 taxonomy）
   - 将新建的页面 / 将更新的页面（列出路径）
   - 要加的交叉链接（每个页面至少 2 个出站链接）
   - 可疑矛盾、信息缺口、隐私风险
4. **等用户确认**。用户要改就改稿再确认。
5. 落盘顺序：先存 `raw/`（用日期或年份前缀，文件名有描述性）→ 再写/改 wiki 页面（frontmatter 六字段齐全，新建页面至少 2 个 `[[wikilink]]`，更新页改 `updated`）。
6. 更新 `index.md`：新页面进对应分区并保持字母序，同步头部 `Total pages` 与 `Last updated`。
7. 追加 `log.md`：`## [YYYY-MM-DD] ingest | 素材标题`，列出每个新建/更新的文件路径、来源 URL 或路径、页面数变化（如 `Total pages: 42→43`）。
8. **收尾自检**：跑体检（工作流 D 第 1 步），确认没有新增断链；`[[X]]` 若没有对应页面，要么建页、要么改纯文本 —— 断链比没有链接更糟。
9. 回报：一句话结论 + 改动路径清单 + 未决问题。

一个素材触发 5-15 个页面更新是正常且期望的（复利效应）。

## 工作流 C：查询与归档

1. 先读 `index.md` 定位，再读相关页面；页面多时用 Grep 在整棵页面目录搜关键词（单靠 index 会漏）。
2. 回答时引用页面：「基于 [[page-a]] 和 [[page-b]]…」，必要时给出 raw 来源路径。
3. 若回答产生了值得留存的综合（对比、深度分析、新结论），问用户是否要以新页面归档（`queries/` 或 `comparisons/`），归档后照工作流 B 第 6-8 步更新 index/log。

## 工作流 D：健康检查（lint）

触发语：「帮我检查下知识库健康状态」「体检 wiki」「找断链 / 孤儿页面 / 过时内容」。

1. 跑结构检查：

   ```bash
   python3 ~/.workbuddy/skills/personal-knowledge-base/scripts/health_check.py --root ~/Projects/LLMWiki
   ```

   可选参数：`--strict`（frontmatter 问题升级为 error）、`--json`、`--size-limit 200`、`--stale-days 180`、`--max-log 500`。

   若库根存在 `.wikilintignore`（每行一个 glob），其中命中的 raw 文件不算「未被引用」——用它排除整本书语料（如 `raw/dive-into-llms/**`）和附件图集（`raw/assets/**`），否则会产生大量噪音。

2. 读 `index.md`、`log.md`、`health.md` 以及脚本点名的页面。
3. **补脚本做不了的语义检查**：
   - 页面之间的实质矛盾（同一事实两个版本）
   - 被新素材取代的过时论断
   - 被反复提及却没有自己页面的概念（是否达到 Page Threshold）
   - 缺失的关键交叉引用
   - 论断过弱、只有断言没有来源
   - 值得补的后续素材或待答问题
4. 把结论写进 `health.md`：日期 + 结构问题 + 语义问题 + 建议动作，保留最近 3 次。
5. **大修前先给修复计划**，用户确认后再批量改。

## 工作流 E：多设备同步（可选）

其他设备只允许往 `raw/` 写；wiki 页面由 Agent 维护。同步循环：`git pull` → 找出 `raw/` 新增/变更文件 → 逐个 ingest → 收尾自检（断链/tag/index）→ `git add -A && git commit && git push`。

macOS 上取文件指纹用 BSD 语法：

```bash
find raw -type f -exec stat -f '%m %N' {} \; | sort -k2
```

不要用 GNU 的 `find -printf` / `stat --format`（原版脚本在 macOS 上会静默失败）。

## 工作流 F：批量收件箱（微信收藏、书签、群里转来的链接）

用户一次给一批链接，或说「导入收件箱」「把收件箱清一下」时走这条。

1. **收**。链接统一倒进 KB 根目录的 `inbox.md`（脚本会自动创建）。用户可以自己贴，也可以让 Agent 用 `--add` 追加。
2. **去重**：

   ```bash
   python3 ~/.workbuddy/skills/personal-knowledge-base/scripts/import_inbox.py --root <KB_ROOT>
   ```

   脚本会做 URL 归一（公众号按 `__biz+mid+idx+sn` 归一，丢弃每次都变的 `chksm`/`scene`/`#rd`）、全库查重、原地打勾并标注落点，输出「待入库 / 已在库 / 箱内重复」三段。加 `--json` 取机器可读结果。
3. **取正文**。按来源分两类：
   - 普通网站：`WebFetch` 直接抓。
   - **微信公众号：先试 WebFetch，不要直接放弃**。实测短链 `mp.weixin.qq.com/s/<hash>` 有较大概率抓到全文；带 `__biz&mid&idx&sn&chksm` 的长链经常返回 302「环境异常」，`curl` 加 UA / 加 Referer / 走 r.jina.ai 代理都不行。短链失败时，让用户在微信里全选复制正文，或「在浏览器中打开」后再抓。**不要用搜索摘要冒充原文**（搜索引擎重排过、可能截断），也不要在缺正文时建空壳页面。
4. **落盘**：正文写进 `raw/articles/<slug>-<year>.md`，头部沿用既有约定：

   ```markdown
   # 标题

   > 来源: <URL>
   > 公众号: <名称>（有则写）
   > 收藏日期: YYYY-MM-DD

   正文…
   ```

   然后把 `.ingest-ledger.json` 里对应条目的 `raw` 字段填上落盘路径 —— 这是「已入库」的唯一判据，不填就会一直算待办。
5. **建页**：之后照工作流 B 第 6-9 步走（新建/合并页面 → 更新 index → 追加 log → 体检）。一批 10 篇素材建 3-8 个页面是正常的，不要把每篇都建一页。
6. **收尾**报告：`收 N 条 → 新增 X 条 → 建页 Y 个 / 合并进已有页 Z 处 → 待补正文 W 条`。

## 硬性陷阱

| 陷阱 | 后果 |
|---|---|
| 改 `raw/` 文件 | 事实来源被污染，无法回溯 |
| 跳过首次定位 | 重复页面、漏链接、违反约定 |
| 忘记更新 index / log | 导航失效，知识库退化为文件堆 |
| 为顺带提及建页面 | 页面数量膨胀、全是单薄页；遵守 Page Thresholds |
| 页面没有入站链接 | 孤儿页面，等于不存在 |
| 顺手给每个名词加 `[[链接]]` | 制造断链；不值得建页就用纯文本 |
| 自由使用新 tag | taxonomy 退化为噪音；先写进 SCHEMA 再用 |
| 静默覆盖矛盾内容 | 丢失信息；标注双方并交用户裁决 |
| 页面超过 200 行不拆 | 无法 30 秒扫读 |
| 拿搜索摘要冒充公众号原文 | 事实被改写且无来源可回溯；抓不到就要用户给正文 |
| 一批链接不先去重 | 同一篇公众号文章换个 `chksm` 就被当成新素材，重复建页 |

## 参考资源

- `references/llm-wiki-pattern.md`：完整方法论（三层架构、SCHEMA 模板、ingest/query/lint 细则、同步脚本、Obsidian 集成、16 条生产踩坑）
- `references/llm-wiki-principles.md`：架构要点速览
- `references/schema-template.md`：新库 SCHEMA 模板
- `scripts/init_kb.py`：脚手架（目录 + SCHEMA/index/log/health + .gitignore）
- `scripts/health_check.py`：结构体检，无第三方依赖，支持 flat / nested 两种布局
- `scripts/import_inbox.py`：收件箱去重器（URL 归一 + 全库查重 + 原地打勾），无第三方依赖
- `adapters/AGENTS.md`、`adapters/CLAUDE.md`：在其他 Agent 工具里接入的片段

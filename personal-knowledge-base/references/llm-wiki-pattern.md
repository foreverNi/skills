# Karpathy's LLM Wiki Pattern — 可移植版

## 什么是 LLM Wiki？

> 构建一个持久的、不断积累的知识库，以相互链接的 markdown 文件形式存在。
> 基于 [Andrej Karpathy 的 LLM Wiki 模式](https://gist.github.com/karpathy/442a6bf555914893e9891c11519de94f)。

**核心思想**：传统 RAG 每次查询都重新发现知识，而 Wiki 一次性编译知识并持续更新。交叉引用已经存在，矛盾已被标记，综合反映所有已摄入的内容。

**适用场景**：任何需要长期积累、持续迭代的知识领域 — 技术研究、行业洞察、项目文档、个人学习笔记。

---

## 一、三层架构

```
wiki/
├── SCHEMA.md           # 规范、结构规则、领域配置
├── index.md            # 按类型分节的内容目录，带一行摘要
├── log.md              # 按时间顺序的操作日志（仅追加，按年轮换）
├── scripts/            # 辅助脚本
├── raw/                # 第一层：不可变的原始素材
│   ├── articles/       # 网页文章、剪报
│   ├── papers/         # 论文、PDF
│   ├── transcripts/    # 会议记录、访谈
│   └── assets/         # 图片、图表
├── entities/           # 第二层：实体页面（人物、组织、产品、模型）
├── concepts/           # 第二层：概念/主题页面
├── comparisons/        # 第二层：对比分析页面
└── queries/            # 第二层：值得保留的查询结果
```

### 各层职责

| 层级 | 内容 | 谁拥有 | 规则 |
|------|------|-------|------|
| Layer 1 — raw/ | 原始来源（URL 抓取、PDF、粘贴文本） | AI **只读**，人类可写入 | 永久不可变，不修改 |
| Layer 2 — entities/ concepts/ comparisons/ queries/ | 编译后的知识页面 | AI 创建、更新、交叉引用 | 标准 frontmatter，至少 2 个出站链接 |
| Layer 3 — SCHEMA.md | 领域约定、标签分类法、更新策略 | 人机共同维护 | 每次会话先读此文件 |

---

## 二、如何使用

### 恢复已有 Wiki（每次会话必须先做）

在操作之前，**必须先定位**：

1. **读 `SCHEMA.md`** — 了解领域、约定和标签分类法
2. **读 `index.md`** — 了解有哪些页面及其摘要
3. **扫最近 `log.md`** — 阅读最近 20-30 条记录了解近期活动

只有定位之后，才能进行摄入、查询或检查。这防止：
- 为已存在的实体创建重复页面
- 遗漏与现有内容的交叉引用
- 违背规范的约定
- 重复记录已做的工作

对于大型 Wiki（100+ 页面），创建新内容前先用搜索工具搜一下主题。

### 初始化新 Wiki

1. 确定 Wiki 根目录（任意位置均可）
2. 创建上述目录结构
3. 明确 Wiki 覆盖的领域
4. 编写 `SCHEMA.md`（见下方模板，按领域定制）
5. 编写初始 `index.md`（按类型分节）
6. 编写初始 `log.md`（创建记录）
7. 确认 Wiki 已就绪，建议首批摄入来源

---

## 三、SCHEMA.md 模板

这是 Wiki 的宪法文件，约束所有操作，确保一致性。**首次创建时必须按领域定制**。

```markdown
# Wiki Schema

## Domain
[Wiki 覆盖的领域 — 例如 "AI/ML 研究"、"个人健康"、"创业情报"]

## Conventions
- 文件名：小写字母 + 连字符，无空格（如 `transformer-architecture.md`）
- 每个 Wiki 页面必须以 YAML frontmatter 开头
- 使用 `[[wikilinks]]` 连接页面（每个页面至少 2 个出站链接）
- 更新页面时必须更新 `updated` 日期
- 每个新页面必须添加到 `index.md` 对应分区
- 每次操作必须追加到 `log.md`

## Frontmatter
```yaml
---
title: Page Title
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [from taxonomy below]
sources: [raw/articles/source-name.md]
---
```

## Tag Taxonomy
[定义 10-20 个顶级标签。先在此处添加新标签再使用。]
规则：每个页面的 tag 必须出现在此 taxonomy 中。

### 示例 — LLM 领域
#### 模型 (Models)
- model: 具体模型（GPT-4, Llama 3, etc.）
- architecture: 模型架构（Transformer, MoE, etc.）
- benchmark: 评估基准（MMLU, HumanEval, etc.）
- training: 训练相关
- fine-tuning: 微调方法
- inference: 推理优化
- alignment: 对齐技术（RLHF, DPO, etc.）

#### 人物与组织 (People & Orgs)
- person: 研究者、工程师
- company: 公司（OpenAI, Anthropic, etc.）
- lab: 研究实验室
- open-source: 开源项目/社区

#### 技术 (Techniques)
- optimization: 优化技术
- data: 数据工程
- evaluation: 评估方法
- safety: 安全与伦理
- prompt-engineering: 提示工程

#### 元信息 (Meta)
- comparison: 对比分析
- timeline: 时间线/发展史
- controversy: 争议与讨论
- prediction: 趋势预测
- resource: 工具/资源推荐

## Page Thresholds（页面创建门槛）
- **创建页面**：实体/概念出现在 2+ 来源中，或对 1 个来源至关重要
- **添加到已有页面**：来源提到了已有页面涉及的内容
- **不创建页面**：仅顺带提及、细节琐碎、超出领域范围
- **拆分页面**：超过 ~200 行时拆分为子专题，加交叉链接
- **归档页面**：内容已被完全取代 → 移至 `_archive/`，从 index 移除

## Entity Pages（实体页面）
每个值得关注的实体一个页面，包括：
- 概述 / 是什么
- 关键事实和日期
- 与其他实体的关系（`[[wikilinks]]`）
- 来源引用

## Concept Pages（概念页面）
每个概念/主题一个页面，包括：
- 定义 / 解释
- 当前知识状态
- 开放问题或争议
- 相关概念（`[[wikilinks]]`）

## Comparison Pages（对比页面）
对比分析页面，包括：
- 被比较的对象和原因
- 对比维度（表格式优先）
- 综合判断
- 来源

## Update Policy（更新策略）
当新信息与现有内容冲突时：
1. 检查日期 — 较新的来源通常优先
2. 如确实矛盾，标注两个立场及日期和来源
3. 在 frontmatter 中标记：`contradictions: [page-name]`
4. 标记供用户审核
```

### 实际案例：LLM 知识库的 SCHEMA.md 额外标签

如果你的领域涉及底层系统（如嵌入式、车载），可以在此基础上扩展：

```markdown
### 底层系统 (Low-Level Systems)
- compilation: 编译与链接（编译器、链接器、目标文件格式）
- embedded: 嵌入式系统（单片机、RTOS、硬件抽象）
- communication: 通信协议（CAN、UDS、ISO-TP、TCP/IP 等）
```

---

## 四、核心操作

### 1. 摄入（Ingest）

当有一个新来源（URL、文件、粘贴文本）需要整合进 Wiki：

1. **保存原始素材**
   - URL → 保存为 markdown 到 `raw/articles/`
   - PDF → 保存为 `raw/papers/`
   - 粘贴文本 → 保存到对应 `raw/` 子目录
   - 文件名要有描述性：`raw/articles/source-title-2026.md`

2. **讨论要点** — 与用户讨论什么有趣、什么对领域重要

3. **检查已有内容** — 搜索 `index.md` 和已有页面，检查提及的实体/概念是否已存在。这是区分"成长中的 Wiki"和"重复堆砌"的关键。

4. **编写或更新 Wiki 页面**
   - **新实体/概念**：只在满足 Page Thresholds 时创建（2+ 来源提及，或对 1 个来源至关重要）
   - **已有页面**：添加新信息，更新事实，更新 `updated` 日期。新信息冲突时遵循 Update Policy
   - **交叉引用**：每个新建/更新页面必须链接到至少 2 个其他页面 `[[wikilinks]]`
   - **标签**：只使用 SCHEMA.md taxonom 中的标签

5. **更新导航**
   - 新页面添加到 `index.md` 对应分区，按字母顺序
   - 更新 index 头部的"总页面数"和"最后更新"日期
   - 追加到 `log.md`：`## [YYYY-MM-DD] ingest | Source Title`
   - 在 log 条目中列出每个创建或更新的文件

**一个来源可以触发 5-15 个页面的更新。这是正常且期望的 — 这就是复利效应。**

### 2. 查询（Query）

当用户问 Wiki 领域内的问题时：

1. 读 `index.md` 找到相关页面
2. 对于 100+ 页面的 Wiki，也用搜索工具搜一下所有 `.md` 文件 — 单靠 index 可能遗漏
3. 读相关页面，综合回答。引用来源页面："基于 [[page-a]] 和 [[page-b]]..."
4. **有价值的回答要归档**：如果是重要的对比、深度分析或新颖综合，创建一页到 `queries/` 或 `comparisons/`
5. 更新 `log.md`

### 3. 检查（Lint）

定期或按需检查 Wiki 健康度：

1. **孤儿页面**：没有其他页面入站 `[[wikilinks]]` 的页面
2. **断链**：`[[links]]` 指向不存在的页面
3. **Index 完整性**：每个 Wiki 页面都应出现在 `index.md` 中
4. **Frontmatter 验证**：每个页面必须有所有必填字段
5. **过时内容**：`updated` 日期比最近提及同一实体的来源早 90 天以上
6. **矛盾**：同一主题的冲突声明
7. **页面大小**：超过 200 行的页面 — 考虑拆分
8. **标签审计**：列出所有在用的标签，检查是否在 SCHEMA.md taxonomy 中
9. **日志轮换**：如果 `log.md` 超过 500 条，轮换它

**每次摄入后必须做的完整性检查：**

1. **断链检查**：扫描所有 `[[wikilinks]]`，提取目标，与存在的页面文件名对比。每个断链逐一决策：
   - 实体在 2+ 来源中出现或有 1 个关键来源 → 创建新页面
   - 概念已有更好页面 → 重定向到已有页面
   - 仅是顺带一提 → 移除链接

2. **标签验证**：扫描 frontmatter 中的 `tags:`，与 SCHEMA.md taxonomy 对比。不在 taxonomy 中的标签要么先加入 SCHEMA.md，要么改成已有标签。

3. **Index 完整性**：验证每个 Wiki 页面文件在 index.md 中有对应条目，反之亦然。

---

## 五、index.md 和 log.md 模板

### index.md

```markdown
# Wiki Index

> 内容目录。每个 Wiki 页面按类型分类，附一行摘要。
> 查找相关页面时先读此文件。
> Last updated: YYYY-MM-DD | Total pages: N

## Entities
<!-- 按字母顺序排列 -->
- [[entity-name]] — 一行摘要

## Concepts
<!-- 按字母顺序排列 -->
- [[concept-name]] — 一行摘要

## Comparisons
<!-- 按字母顺序排列 -->
- [[comparison-name]] — 一行摘要

## Queries
<!-- 按字母顺序排列 -->
- [[query-name]] — 一行摘要
```

**扩展规则**：当某个分区超过 50 条，按首字母或子域拆分子分区。当 index 总计超过 200 条，创建 `_meta/topic-map.md` 按主题分组加速导航。

### log.md

```markdown
# Wiki Log

> 按时间顺序记录所有 Wiki 操作。仅追加。
> 格式：`## [YYYY-MM-DD] action | subject`
> Actions: ingest, update, query, lint, create, archive, delete
> 超过 500 条时轮换：重命名为 log-YYYY.md，新建空白 log.md

## [YYYY-MM-DD] create | Wiki initialized
- Domain: [domain]
- Structure created with SCHEMA.md, index.md, log.md
```

---

## 六、辅助脚本

以下是在实际生产环境中运行 LLM Wiki 时使用的脚本。用于自动同步和变更检测。

### detect-changes.sh — 检测变更

```bash
#!/bin/bash
# 检测 raw/ 目录是否有文件变更
# 返回码: 0=有变更, 1=无变更, 2=出错

set -e

WIKI_DIR="$HOME/llm-wiki"
STATE_FILE="/tmp/wiki-raw-state"

cd "$WIKI_DIR"

# 生成当前 raw/ 文件指纹（文件名+大小+修改时间）
find raw/ -type f -printf '%s %T@ %p\n' 2>/dev/null | sort -k3 > "${STATE_FILE}.new" || true

# 对比
if [ ! -f "${STATE_FILE}.old" ]; then
    cp "${STATE_FILE}.new" "${STATE_FILE}.old"
    echo "CHANGES_DETECTED"
    exit 0
fi

if ! diff -q "${STATE_FILE}.old" "${STATE_FILE}.new" > /dev/null 2>&1; then
    echo "CHANGES_DETECTED"
    diff "${STATE_FILE}.old" "${STATE_FILE}.new" | grep "^[<>]" | while read line; do
        echo "  $line"
    done
    cp "${STATE_FILE}.new" "${STATE_FILE}.old"
    exit 0
else
    echo "NO_CHANGES"
    exit 1
fi
```

### sync.sh — 从远程拉取并检测变更

```bash
#!/bin/bash
# 从远程 Git 仓库拉取并检测 raw/ 目录变更
# 返回码: 0=有变更需要编译, 1=无变更, 2=出错

set -e

WIKI_DIR="$HOME/llm-wiki"
cd "$WIKI_DIR"

# 记录 pull 前的 raw/ 状态
BEFORE_FILE="/tmp/wiki-raw-state-before"
AFTER_FILE="/tmp/wiki-raw-state-after"

# 保存当前 raw/ 的文件树（统一格式：mtime + 路径）
find raw/ -type f -exec stat --format='%Y %n' {} \; | sort -k2 > "$BEFORE_FILE" 2>/dev/null || true

# 拉取远程更新
if ! git pull origin master 2>&1; then
    echo "ERROR: git pull failed"
    exit 2
fi

# 保存 pull 后的 raw/ 文件树
find raw/ -type f -exec stat --format='%Y %n' {} \; | sort -k2 > "$AFTER_FILE" 2>/dev/null || true

# 对比变更
if ! diff -q "$BEFORE_FILE" "$AFTER_FILE" > /dev/null 2>&1; then
    echo "CHANGES_DETECTED"
    echo "=== New/modified raw files ==="
    diff "$BEFORE_FILE" "$AFTER_FILE" | grep "^>" | awk '{$1=""; print substr($0,2)}' | while read f; do
        [ -n "$f" ] && echo "  $f"
    done
    echo "=== Deleted raw files ==="
    diff "$BEFORE_FILE" "$AFTER_FILE" | grep "^<" | awk '{$1=""; print substr($0,2)}' | while read f; do
        [ -n "$f" ] && echo "  $f"
    done
    exit 0
else
    echo "NO_CHANGES"
    exit 1
fi
```

### git-push.sh — 编译后提交推送

```bash
#!/bin/bash
# 编译完成后提交并推送变更到远程仓库

set -e

WIKI_DIR="$HOME/llm-wiki"
cd "$WIKI_DIR"

# 检查是否有变更
if git diff --quiet && git diff --cached --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo "NOTHING_TO_PUSH"
    exit 0
fi

CHANGED_FILES=$(git status --short | wc -l)
ADD_COUNT=$(git ls-files --others --exclude-standard | wc -l)
MOD_COUNT=$(git diff --name-only | wc -l)

MSG="wiki sync: ${ADD_COUNT} added, ${MOD_COUNT} modified"

git add -A
git commit -m "$MSG" --allow-empty-message 2>/dev/null || true

if git push origin master 2>&1; then
    echo "PUSH_OK: $MSG"
else
    echo "PUSH_FAILED: will retry next cycle"
    exit 1
fi
```

---

## 七、多设备同步模式

其他设备可以推送新内容到 `raw/`（且**只能**到 `raw/`）。AI 定期拉取并检测变更，然后编译成 Wiki 页面。

### 同步流程（建议每 30 分钟运行）

1. `git pull origin master` — 获取其他设备的变更
2. 对比 `raw/` 文件树的 before 和 after 状态（用 `stat --format='%Y %n'` 格式，排序后对比）
3. 如果检测到变更：定位 → 识别新增/修改的 `.md` 文件 → 逐个摄入 → 编译
4. 编译后做完整性检查：验证没有断链 `[[wikilinks]]`，所有标签在 SCHEMA.md taxonomy 中
5. 编译+修复后：`git add -A && git commit && git push`

**关键规则**：
- 只有 `raw/` 被其他设备写入 — `raw/` 之外的文件由 AI 管理
- AI 从不修改 `raw/` 内容（不变性原则）
- `raw/` 冲突应优先选择较新版本
- 同步脚本放在 `scripts/` 目录下，提交到 git

### 格式一致性陷阱

对比 `raw/` 状态的 before 和 after 时，必须使用**完全相同的格式**。一个常见的 bug 是 before 用 `find -type f`（只有路径），after 用 `stat --format='%Y %n'`（时间戳+路径），diff 总会报告变更。始终用 `stat --format='%Y %n'` 格式，按路径排序。

---

## 八、Obsidian 集成

Wiki 目录开箱即用可作为 Obsidian 知识库：

- `[[wikilinks]]` 渲染为可点击链接
- 图谱视图可视化知识网络
- YAML frontmatter 支持 Dataview 查询
- `raw/assets/` 文件夹存放通过 `![[image.png]]` 引用的图片

**建议配置**：
- 设置 Obsidian 附件文件夹为 `raw/assets/`
- 开启 "Wikilinks"（通常默认开启）
- 安装 Dataview 插件运行查询：`TABLE tags FROM "entities" WHERE contains(tags, "company")`
- `.gitignore` 中加入 `.obsidian/`

---

## 九、陷阱与经验教训

### 通用陷阱

| 陷阱 | 说明 |
|------|------|
| **永远不要修改 raw/ 文件** | 来源不可变。修正写在 Wiki 页面中 |
| **必须先定位** | 每次新会话读 SCHEMA + index + 最近 log，跳过会导致重复 |
| **必须更新 index 和 log** | 跳过让 Wiki 退化。它们是导航的脊梁 |
| **不为顺带提及创建页面** | 遵循 Page Thresholds。脚注出现一次的名字不配实体页面 |
| **不为没有交叉引用的页面** | 孤立的页面不可见。每个页面至少链出 2 个 |
| **Frontmatter 是必须的** | 它支持搜索、过滤、过时检测 |
| **标签必须来自 taxonomy** | 自由标签退化为噪音。新标签先加 SCHEMA.md 再用 |
| **页面要可扫描** | 30 秒内读完一个页面。过 200 行就拆分 |
| **明确处理矛盾** | 不要静默覆盖。标注两个立场和日期，标记供审核 |
| **检查摄入后的断链** | 写 `[[claude]]` 但没创建实体页 → 断链。每个 `[[link]]` 要么有页面，要么移除 |

### 生产运行中发现的坑

- **上次同步可能不完整** — 创建新页面前，总是搜索一下主题。之前可能已存在文件名略有差别的页面，需要合并而非重复创建

- **过度的 `[[wikilinks]]` 转为纯文本** — 摄入一个丰富来源（如 38 个模型的清单），忍不住给每个概念加 `[[wikilinks]]`。但许多概念只是顺带提及，不满足 Page Thresholds。每个 `[[link]]` 问自己：这值得一个页面吗？不值得就用纯文本。断链比没有链接更糟 — 它暗示了不存在的页面

- **清理 raw 处理产生的垃圾文件** — 有时原始来源的作者名或元数据被提取成单独的 `.md` 文件（如 `金小牛柿.md`）。这些 `raw/` 之外的空文件是产物，不是 Wiki 页面。同步后检查并清理

- **每次同步都跑完整的完整性检查** — 断链、缺失 index 条目、无效标签、孤儿文件跨多次同步累积。完整性检查（断链→标签→index）是唯一能发现它们的方式。不要认为同步完成了——直到所有三项检查通过

- **不要把 `log.md` 中的 `[[wikilinks]]` 算作断链** — 记录操作日志时，`[[page-name]]` 对实际页面没问题。但对于重命名、删除或从未创建的页面的历史记录，用纯文本或反引号（`` `[page-name]` ``），以免在完整性检查中显示为断链

---

## 十、如何在不同 AI 工具中使用

| 工具 | 方法 |
|------|------|
| **Claude Projects** | 上传此文件到 Project Knowledge |
| **ChatGPT** | 粘贴到 Custom Instructions 或对话开头，加上"请使用 LLM Wiki 模式管理知识" |
| **Gemini** | 粘贴到 Saved Info / Custom Instructions |
| **Cursor / Windsurf** | 放入 `.cursorrules` 或 `AGENTS.md` |
| **Cline / Roo Code** | 放入 `CLAUDE.md` 或作为 System Prompt |
| **Any System Prompt** | 直接粘贴全文 |

**使用方式**：
- "帮我把这篇文章摄入到我的 Wiki：..."
- "我的 Wiki 里关于 [主题] 有哪些页面？"
- "帮我检查一下 Wiki 的健康度"
- "初始化一个新的 LLM Wiki，领域是 [你的领域]"

### 初始化步骤（在新工具中首次使用）

```
1. 告诉 AI："请用 Karpathy 的 LLM Wiki 模式，在 [路径] 创建知识库"
2. AI 会创建目录结构、SCHEMA.md、index.md、log.md
3. 编辑 SCHEMA.md 中的 Tag Taxonomy 匹配你的领域
4. 开始第一个摄入："帮我摄入这篇文章：[URL/内容]"
5. AI 会保存原始素材，创建/更新 Wiki 页面，更新 index 和 log
```

---

> **版本**: 2.2.0（移植版）
> **原始来源**: Hermes Agent llm-wiki 技能
> **核心作者**: Andrej Karpathy（原始模式）、Hermes Agent（工程化实现）

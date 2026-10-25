# Wiki Schema

> 本文件是知识库的「宪法」。每次操作前必须先读它，新约定先写进这里再使用。
> 最后更新：{{DATE}}

## Domain

{{DOMAIN}}

## Conventions

- 文件名：小写字母 + 连字符，无空格（如 `transformer-architecture.md`）；中文专名可直接用中文
- 每个 Wiki 页面必须以 YAML frontmatter 开头
- 使用 `[[wikilinks]]` 连接页面（每个页面至少 2 个出站链接）
- 更新页面时必须更新 `updated` 日期
- 每个新页面必须添加到 `index.md` 对应分区，并更新头部的 Total pages
- 每次操作必须追加到 `log.md`
- 图片等附件放 `raw/assets/`，用 `![[image.png]]` 引用；不要为附件建页面

## Frontmatter

```yaml
---
title: 页面标题
created: YYYY-MM-DD
updated: YYYY-MM-DD
type: entity | concept | comparison | query | summary
tags: [from taxonomy below]
sources: [raw/articles/source-name.md]
contradictions: []   # 可选，指向存在冲突的页面
---
```

`type` 必须与所在目录对应：`entity`→`entities/`、`concept`→`concepts/`、`comparison`→`comparisons/`、`query`→`queries/`。跨类别的综合页（如学习路线）可放根目录，但 type 仍取上面之一。

## Tag Taxonomy

> 规则：每个页面使用的 tag 必须出现在此清单中。新 tag 需先添加到此处再使用。

### 模型 (Models)

- model: 具体模型
- architecture: 模型架构
- benchmark: 评估基准
- training: 训练相关
- fine-tuning: 微调方法
- inference: 推理优化
- alignment: 对齐技术

### 人物与组织 (People & Orgs)

- person: 研究者、工程师
- company: 公司
- lab: 研究实验室
- open-source: 开源项目/社区

### 技术 (Techniques)

- optimization: 优化技术
- data: 数据工程
- evaluation: 评估方法
- safety: 安全与伦理
- prompt-engineering: 提示工程

### 元信息 (Meta)

- comparison: 对比分析
- timeline: 时间线/发展史
- controversy: 争议与讨论
- prediction: 趋势预测
- resource: 工具/资源推荐

## Page Thresholds

- **创建页面**：某个实体/概念出现在 2+ 来源中，或对 1 个来源至关重要
- **添加到已有页面**：来源提到了已有页面涉及的内容
- **不创建页面**：仅顺带提及、细节琐碎、超出领域范围
- **拆分页面**：超过 ~200 行时拆分为子专题，加上交叉链接
- **归档页面**：内容已被完全取代 → 移至 `_archive/`，从 index 移除

## Entity Pages

每个值得关注的实体一个页面，包括：

- 概述 / 是什么
- 关键事实和日期
- 与其他实体的关系（`[[wikilinks]]`）
- 来源引用

## Concept Pages

每个概念/主题一个页面，包括：

- 定义 / 解释
- 当前知识状态
- 开放问题或争议
- 相关概念（`[[wikilinks]]`）

## Comparison Pages

对比分析页面，包括：

- 被比较的对象和原因
- 对比维度（表格式优先）
- 综合判断
- 来源

## Update Policy

当新信息与现有内容冲突时：

1. 检查日期 — 较新的来源通常优先
2. 如确实矛盾，标注两个立场及日期和来源
3. 在 frontmatter 中标记：`contradictions: [page-name]`
4. 在体检报告中列出，交由用户裁决，不静默覆盖

## Lint Baseline

体检脚本：`~/.workbuddy/skills/personal-knowledge-base/scripts/health_check.py --root <KB_ROOT>`

检查项：核心文件、frontmatter 必填字段与日期格式、type 与目录一致性、tag 是否在 taxonomy 中、断链、相对链接、孤儿页面、index 覆盖与计数、log 标题格式与轮换、页面长度、raw 引用、sources 文件存在性、contradictions 引用有效性、过时页面提示。

# AGENTS.md Adapter: Personal Knowledge Base

当用户要求「加入知识库 / 摄入这篇 / 检查知识库健康状态」时，使用本适配片段。

## 定位

- 知识库根目录：`~/Projects/LLMWiki`（或用户指定路径）
- 技能目录：`~/.workbuddy/skills/personal-knowledge-base`

## 操作前

1. 读 `<KB_ROOT>/SCHEMA.md`
2. 读 `<KB_ROOT>/index.md` 与 `<KB_ROOT>/log.md` 最近 20-30 条
3. 读技能内的 `SKILL.md`

## 命令

- 体检：`python3 ~/.workbuddy/skills/personal-knowledge-base/scripts/health_check.py --root <KB_ROOT>`
- 初始化新库：`python3 ~/.workbuddy/skills/personal-knowledge-base/scripts/init_kb.py --root <KB_ROOT> --domain "<领域>"`

## 规则

- 摄入前先出确认稿，用户确认后才落盘
- `raw/` 目录只读，永不改写
- 每次变更后更新 `index.md` 与 `log.md`
- 大修前先给计划，确认后再批量改

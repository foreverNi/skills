# CLAUDE.md Adapter: Personal Knowledge Base

当用户说「加入知识库」「帮我把这个文章加入知识库」「把这段话加入知识库」「检查知识库健康状态」「add this to my knowledge base」或类似措辞时，按下面执行。

## 必读顺序

1. `<KB_ROOT>/SCHEMA.md` —— 领域、约定、tag taxonomy
2. `<KB_ROOT>/index.md` —— 已有页面清单
3. `<KB_ROOT>/log.md` 最近 20-30 条 —— 近期活动
4. `~/.workbuddy/skills/personal-knowledge-base/SKILL.md` —— 工作流细节

## 流程

- **加知识**：定位 → 出确认稿（标题/slug/raw 路径/摘要/tags/待建待改页面/交叉链接/矛盾与隐私风险）→ 等确认 → 存 `raw/` → 写页面 → 更新 `index.md` → 追加 `log.md` → 跑体检确认无新增断链
- **体检**：`python3 ~/.workbuddy/skills/personal-knowledge-base/scripts/health_check.py --root <KB_ROOT>` → 补充语义问题到 `health.md`
- **查询**：读 `index.md` 定位 → 读页面 → 带 `[[引用]]` 回答 → 有价值的综合问是否归档

## 红线

- `raw/` 不可变，修正写在 wiki 页面里
- 不编造来源与论断
- 不静默覆盖矛盾，标注双方并标记待审核
- 页面至少 2 个出站 `[[wikilink]]`，tag 必须来自 SCHEMA taxonomy

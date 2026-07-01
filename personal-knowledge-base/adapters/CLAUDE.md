# CLAUDE.md Adapter: Personal Knowledge Base

When the user says "加入知识库", "帮我把这个文章加入知识库", "帮我把这段话加入知识库", "add this to my knowledge base", "检查知识库健康状态", or similar wording, use the repository-local skill in `agent-skills/personal-knowledge-base/`.

Required flow:

1. Read `KNOWLEDGE_SCHEMA.md` and `agent-skills/personal-knowledge-base/SKILL.md`.
2. For additions, inspect `wiki/index.md` and `wiki/log.md`, prepare a confirmation draft, and wait for approval before writing.
3. For health checks, run `python3 agent-skills/personal-knowledge-base/scripts/health_check.py --root .`, then add semantic findings to `wiki/health.md`.
4. Preserve raw sources under `raw/` and do not overwrite them.
5. Keep `wiki/index.md` and `wiki/log.md` current after confirmed changes.

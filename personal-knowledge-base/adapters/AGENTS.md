# AGENTS.md Adapter: Personal Knowledge Base

Use the portable skill at `agent-skills/personal-knowledge-base/` when the user asks to add an article, paragraph, note, URL, file, or idea to the knowledge base, or asks to check knowledge base health.

Before modifying the knowledge base:

1. Read `KNOWLEDGE_SCHEMA.md`.
2. Read `agent-skills/personal-knowledge-base/SKILL.md`.
3. For health checks, run `python3 agent-skills/personal-knowledge-base/scripts/health_check.py --root .`.
4. For ingestion, present the confirmation draft first and write only after user confirmation.

Do not install this skill into a Codex-specific directory. Treat it as a repository-local, portable Agent workflow package.

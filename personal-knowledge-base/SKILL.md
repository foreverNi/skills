---
name: personal-knowledge-base
description: Maintain a portable personal Markdown LLM Wiki knowledge base. Use when the user says in Chinese or English that they want to add an article, paragraph, note, URL, file, or idea to the knowledge base, for example "帮我把这个文章加入知识库", "把这段话加入知识库", "加入知识库", "add this to my knowledge base", or when the user asks to check knowledge base health, lint the wiki, find stale claims, broken links, orphan pages, missing index entries, contradictions, or similar health/status checks.
---

# Personal Knowledge Base

## Overview

Use this skill to maintain an LLM-owned, user-readable Markdown wiki under a repository or folder that contains `KNOWLEDGE_SCHEMA.md`, `raw/`, and `wiki/`. The default root for this package is `/Users/noah/WorkSpace/LLMWiki`, but use the current project root when another Agent copies this skill elsewhere.

The wiki is a compiled knowledge artifact, not a chat transcript. The Agent should preserve raw sources, synthesize them into durable wiki pages, maintain cross-links and indexes, and record every confirmed operation in `wiki/log.md`.

Read `KNOWLEDGE_SCHEMA.md` before changing the knowledge base. Read `references/llm-wiki-principles.md` when the repository structure is unfamiliar or when adjusting the workflow.

## Safety Rules

- Do not write new knowledge before user confirmation unless the user has explicitly disabled confirmation for the current task.
- Do not overwrite or mutate files in `raw/`; preserve raw sources as source-of-truth evidence.
- Do not invent citations, source metadata, or claims not supported by the provided source or existing wiki pages.
- Do not commit secrets, passwords, private tokens, or unrelated personal data into the wiki.
- Do not perform broad rewrites during an ingest. Keep changes scoped to the source being processed and directly related pages.
- Do not silently resolve contradictions. Mark them with source references and ask the user when judgment is needed.

## Add Knowledge Workflow

Use this workflow for requests like "帮我把这个文章加入知识库", "帮我把这段话加入知识库", "加入知识库", "add this to my knowledge base", or similar wording.

1. Confirm the source exists. If the user did not provide text, a URL, a local file path, or enough surrounding context, ask for the missing source before editing.
2. Inspect the wiki entry points: `wiki/index.md`, `wiki/log.md`, and any pages likely related to the source.
3. Prepare a confirmation draft before writing:
   - proposed title and slug
   - source type and raw storage path
   - concise summary
   - tags or categories
   - pages to create or update
   - cross-links to add
   - possible contradictions, uncertainty, or privacy concerns
4. Wait for user confirmation. If the user asks for changes to the draft, revise the plan and ask again.
5. After confirmation, save the raw source under `raw/` with a date-prefixed path, then update or create the relevant wiki pages.
6. Update `wiki/index.md` so every maintained wiki page is discoverable with a one-line summary.
7. Append an entry to `wiki/log.md` using the schema format.
8. Report the changed paths and any unresolved questions.

## Health Check Workflow

Use this workflow for requests like "帮我检查下知识库健康状态", "检查知识库健康状态", "lint the wiki", "check stale claims", "find orphan pages", or similar wording.

1. Run the structural checker:

   ```bash
   python3 agent-skills/personal-knowledge-base/scripts/health_check.py --root .
   ```

2. Read `wiki/index.md`, `wiki/log.md`, `wiki/health.md`, and pages identified by the checker.
3. Add semantic analysis that a script cannot reliably do:
   - contradictions between pages or sources
   - stale claims superseded by newer entries
   - important concepts mentioned repeatedly but lacking their own page
   - missing cross-references
   - weakly sourced claims
   - useful follow-up sources or questions
4. Update `wiki/health.md` with the date, structural findings, semantic findings, and recommended actions.
5. Do not perform large repairs unless the user confirms the repair plan.

## Query And Filing Workflow

When the user asks a question about the knowledge base:

1. Read `wiki/index.md` first, then relevant pages and sources.
2. Answer with citations to wiki pages and, when needed, raw source paths.
3. If the answer creates durable synthesis, ask whether to file it back into the wiki as a new page or update.

## Resources

- `references/llm-wiki-principles.md`: compressed rationale and architecture from the original LLM Wiki method.
- `scripts/health_check.py`: deterministic structural checks for core files, links, index coverage, log format, orphan pages, and raw source references.
- `adapters/AGENTS.md`: snippet for Codex-style `AGENTS.md`.
- `adapters/CLAUDE.md`: snippet for Claude Code `CLAUDE.md`.

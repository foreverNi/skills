# LLM Wiki Principles

This reference summarizes the method described in `llm-wiki.md` for Agents that maintain this knowledge base.

## Core Idea

The knowledge base is not a passive retrieval folder. It is a persistent, compounding wiki maintained by an Agent. When new sources arrive, the Agent reads them once, extracts durable knowledge, updates existing topic and entity pages, creates new pages when needed, flags contradictions, and maintains links and logs.

## Layers

- Raw sources are immutable source-of-truth evidence. The Agent reads them but does not rewrite them.
- The wiki is the maintained synthesis layer. The Agent owns page creation, updates, cross-links, summaries, and consistency.
- The schema defines how the Agent should operate. It records directory structure, naming, ingest rules, log format, and health checks.

## Operations

- Ingest: process one source or a small batch, preserve raw material, update the wiki, update the index, and append the log.
- Query: answer from the wiki first, using the index as the navigation entry point. Durable answers can be filed back into the wiki after confirmation.
- Health check: look for broken structure, contradictions, stale claims, orphan pages, missing cross-links, missing topic pages, and data gaps.

## Index And Log

- `wiki/index.md` is content-oriented. It helps the Agent discover relevant pages before reading deeply.
- `wiki/log.md` is chronological and append-only. It shows what changed, when, and why.

## User Preferences

- Prefer Markdown files and local attachments as the long-term asset layer.
- Prefer an IM/chat-first capture pattern when operating through mobile or another Agent interface.
- Prefer confirmation before persistence.
- Prefer concise feedback after ingest: summary plus the changed wiki path or link.

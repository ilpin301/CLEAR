---
tags:
  - "concept"
topics:
  - "llm-wiki"
status: seed
created: 2026-05-25
updated: 2026-05-25
sources:
  - "Raw/Sources/llm-wiki-starter-demo.md"
source_count: 1
aliases:
  - "two-layer architecture"
---

# Two-Layer Workflow

The two-layer workflow is the core pattern of an LLM Wiki: separate captured source material from compiled knowledge notes.

## Layers

| Layer | Path | Purpose |
|---|---|---|
| Raw | `Raw/Sources/` | Captured source material. Preserved as-is. |
| Wiki | `Wiki/` | Compiled, reusable knowledge notes. |

## Why It Works

Raw sources preserve original context. Wiki notes turn useful claims into short, linked, reusable knowledge. By keeping them separate, the system stays traceable — every fact in a Wiki note points back to its source.

## Query Pattern

Search the compiled Wiki first, then open Raw sources only when more evidence or detail is needed.

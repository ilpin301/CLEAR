# Welcome to Your LLM Wiki

This vault is a structured knowledge system built around a two-layer workflow:

- **`Raw/Sources/`** — captured source material (articles, notes, transcripts). These are preserved as-is.
- **`Wiki/`** — compiled, reusable knowledge notes distilled from Raw sources.

## How It Works

1. Drop cleaned Markdown source files into `Raw/Sources/`.
2. An agent (or you) compiles them into focused notes under `Wiki/`.
3. Every Wiki note links back to its Raw source(s).
4. Indexes and a machine-readable catalog are rebuilt automatically.
5. Health checks run before commits to keep the Wiki consistent.

## Quick Start

**Query the Wiki:**
```bash
python3 scripts/wiki_tool.py search-catalog --query "your topic"
```

**Run the maintenance gate:**
```bash
python3 scripts/wiki_tool.py doctor
python3 scripts/wiki_tool.py build
python3 scripts/wiki_tool.py lint
python3 scripts/wiki_tool.py source-lint
python3 scripts/audit_public.py
```

See `AGENTS.md` for full agent instructions and `Schema/command-reference.md` for all tool commands.

# AGENTS.md — LLM Wiki Rules For AI Agents

Read this file before doing any work in this vault.

## Core Principle

This vault separates two distinct layers:

- **Raw/Sources/** — original source material, captured as-is. Do not treat this as compiled knowledge.
- **Wiki/** — compiled, reusable knowledge notes. This is the authoritative layer.

## Rules

### Raw Sources

- Treat every file in `Raw/Sources/` as raw input material, not as a knowledge source to cite directly.
- Do not modify Raw source files when compiling Wiki notes.
- Raw sources preserve the original context and wording of the creator.

### Wiki Notes

- Write all reusable knowledge exclusively under `Wiki/`.
- Every compiled Wiki note **must** link back to at least one Raw source in the `sources` frontmatter field.
- Do not invent citations or create unsupported claims. Every claim must be traceable to a Raw source.
- Keep `source_count` equal to the number of entries in `sources`.
- Use only allowed tags: `topic`, `concept`, `entity`, `project`, `log`.

### Before Answering a Question

1. Search `Wiki/catalog.jsonl` before opening any Raw sources:
   ```bash
   python scripts/wiki_tool.py search-catalog --query "your topic"
   ```
2. Open relevant Wiki notes.
3. Open Raw sources only when the compiled note is insufficient or the user needs source-level verification.
4. Cite both the compiled note and the Raw source when the answer depends on source material.

### Before Every Commit

Run the full maintenance gate:

```powershell
python scripts/wiki_tool.py doctor
python scripts/wiki_tool.py build
python scripts/wiki_tool.py lint
python scripts/wiki_tool.py source-lint
python scripts/audit_public.py
```

After source ingestion, also run:

```powershell
python scripts/wiki_tool.py source-scan --update --accept-covered
python scripts/wiki_tool.py source-lint
```

### PDF Files in Raw/Files/

- Before ingesting any file from `Raw/Files/`, check if a `.pdf.md` companion exists.
- If a PDF has no companion `.pdf.md`, run the `llm-wiki-pdf-extract` skill first.
- Never ingest a raw PDF directly — always ingest the `.pdf.md` companion.

### Schema

- Follow frontmatter schemas defined in `Schema/frontmatter-schema.md`.
- Follow naming conventions in `Schema/naming-conventions.md`.
- Consult `Schema/workflow-examples.md` for ingest and query examples.

### Security

- Never commit secrets, private keys, machine-local paths, or plugin/cache state.
- Run `python scripts/audit_public.py` to catch these before committing.
- Never edit raw exports.
- Never invent frequencies.
- Never present a tiny sample as a dataset-wide truth.

## Folder Map

```
Raw/Sources/     — original source notes (Processed: false until compiled)
Raw/Files/       — binary source files (ignored by git except .gitkeep)
Wiki/Topics/     — broad topic notes
Wiki/Concepts/   — specific concept notes
Wiki/Entities/   — people, tools, organizations
Wiki/Projects/   — project-level notes
Wiki/Logs/       — log and change notes
Schema/          — rules, schemas, and the source manifest
Samples/         - not for wiki processing, just samples of style and structure for some out creation
Autors           - not for wiki processing, its names of autors for notebookLM creation
_templates/      — note templates
.agents/skills/  — agent skill definitions
scripts/         — deterministic tooling
tutorial/        — tutorial fixtures and examples
```

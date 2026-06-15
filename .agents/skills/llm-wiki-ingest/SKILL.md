# Skill: llm-wiki-ingest

## Purpose

Compile one or more Raw source notes into focused, reusable Wiki notes.

## When To Use

- A new file has been added to `Raw/Sources/` with `Processed: false`
- The user asks to "ingest", "process", or "compile" a source

## Steps

1. Search the catalog for related existing notes:
   ```powershell
   python scripts/wiki_tool.py search-catalog --query "<relevant terms from source>"
   ```
2. Read the Raw source file.
3. Open only the most relevant existing Wiki notes (not all of them).
4. For each key claim or concept in the source:
   - Decide whether to create a new Wiki note or update an existing one.
   - Keep notes focused: one concept, topic, entity, project, or log per file.
5. Add `Raw/Sources/<filename>.md` to `sources` in every new or updated Wiki note.
6. Set `source_count` equal to the number of entries in `sources`.
7. Mark the Raw source as processed: set `Processed: true`.
8. Run the post-ingest maintenance gate:
   ```powershell
   python scripts/wiki_tool.py build
   python scripts/wiki_tool.py lint
   python scripts/wiki_tool.py source-scan --update --accept-covered
   python scripts/wiki_tool.py source-lint
   ```
9. Add a log entry if the ingest meaningfully changed the Wiki.

## Constraints

- Do not invent claims. Every fact must be traceable to the Raw source.
- Do not write broad summaries. Write focused, reusable notes.
- Do not copy the Raw source wholesale. Transform it into structured Wiki notes.

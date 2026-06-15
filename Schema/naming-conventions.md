# Naming Conventions

## File Names

- Use **kebab-case** for all file names: `llm-wiki-overview.md`, not `LLM Wiki Overview.md`.
- Keep names short but descriptive.
- Do not use spaces, underscores, or camelCase in file names.
- Use `.md` extension for all notes.

## Folder Names

- Folder names under `Wiki/` use **TitleCase**: `Topics/`, `Concepts/`, `Entities/`, `Projects/`, `Logs/`.
- All other folders use **lowercase-kebab-case**: `Raw/`, `_templates/`, `.agents/`, `scripts/`, `Schema/` (Schema is the exception — kept as-is for readability).

## Raw Source Files

- Name source files after their content, not their origin format: `llm-wiki-intro.md`, not `video-2024-01-15.md`.
- Use the creation date as a prefix if the source is time-sensitive: `2024-01-15-llm-wiki-intro.md`.

## Wiki Note Files

- Name Wiki notes after the concept or topic they describe.
- Topic notes: `llm-wiki.md`, `knowledge-management.md`
- Concept notes: `two-layer-workflow.md`, `source-coverage.md`
- Entity notes: `obsidian.md`, `python.md`
- Project notes: `llm-wiki-setup.md`
- Log notes: `YYYY-MM-DD-event-name.md`

## Catalog and Manifest

- `Wiki/catalog.jsonl` — auto-generated; do not rename.
- `Schema/source-manifest.jsonl` — auto-generated; do not rename.
- `Wiki/index.md` — auto-generated; do not rename.
- Per-folder index files: `Wiki/Topics/index.md`, `Wiki/Concepts/index.md`, etc. — auto-generated.

## Tags

- Tags must be lowercase single words or hyphenated: `concept`, `topic`, `entity`, `project`, `log`, `source`.
- Do not add custom tags to compiled Wiki notes without updating `Schema/frontmatter-schema.md`.

# Skill: llm-wiki-lint

## Purpose

Validate the Wiki for schema compliance, broken source links, and coverage gaps.

## When To Use

- Before committing changes
- After ingest
- When the user asks to "check", "validate", or "lint" the Wiki

## Steps

Run these commands in order:

```powershell
python scripts/wiki_tool.py doctor
python scripts/wiki_tool.py build
python scripts/wiki_tool.py lint
python scripts/wiki_tool.py source-lint
python scripts/audit_public.py
```

## What Each Check Does

| Command | Checks |
|---|---|
| `doctor` | Folder structure, Python version, catalog/manifest existence, note counts |
| `build` | Regenerates catalog.jsonl, index.md, per-folder indexes |
| `lint` | Wiki note frontmatter, allowed tags, source links, source_count accuracy |
| `source-lint` | Raw source frontmatter, coverage (processed sources must have Wiki coverage) |
| `audit_public.py` | Secrets, private keys, machine-local paths, plugin/cache state |

## Fixing Failures

- **lint failure on source_count**: update `source_count` to match `len(sources)`
- **lint failure on missing source**: the file in `sources` does not exist under `Raw/Sources/`
- **source-lint failure on covered**: source is `Processed: true` but no Wiki note references it — either add a Wiki note or set `Processed: false`
- **audit failure**: remove secrets or local paths before committing

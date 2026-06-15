# Lint Checklist

This checklist describes what `wiki_tool.py lint` and `wiki_tool.py source-lint` validate.

---

## `wiki_tool.py lint` — Compiled Wiki Notes

Checks every `.md` file under `Wiki/` (excluding `index.md` files):

| Check | Rule |
|---|---|
| `tags` present | The `tags` frontmatter field must exist. |
| Allowed tag | `tags[0]` must be one of: `topic`, `concept`, `entity`, `project`, `log`. |
| `sources` present | The `sources` field must exist (may be empty list for seed notes). |
| `source_count` accurate | `source_count` must equal `len(sources)`. |
| Source files exist | Every path in `sources` must point to an existing file under `Raw/Sources/`. |
| `status` present | Must be one of: `seed`, `draft`, `stable`. |
| `created` present | Must be a date string. |
| `updated` present | Must be a date string. |

**Failure action:** Print the file path and failing check. Exit non-zero.

---

## `wiki_tool.py source-lint` — Raw Source Notes

Checks every `.md` file under `Raw/Sources/`:

| Check | Rule |
|---|---|
| `Title` present | Required string field. |
| `Reference` present | Required string field. |
| `Created` present | Required date field. |
| `Processed` present | Required boolean field. |
| `tags` present | Must include `"source"`. |
| Coverage check | If `Processed: true`, at least one Wiki note must list this source in its `sources` field. |

**Failure action:** Print the file path and failing check. Exit non-zero.

---

## `scripts/audit_public.py` — Secrets And Privacy

Checks all tracked files for:

| Check | Rule |
|---|---|
| Private keys | No `-----BEGIN ... PRIVATE KEY-----` patterns. |
| Obvious secrets | No patterns like `password=`, `secret=`, `api_key=`, `token=` with values. |
| Machine-local paths | No absolute paths like `C:\Users\`, `/home/`, `/Users/`. |
| Plugin/cache state | No `.obsidian/plugins/` or `.obsidian/cache/` content committed. |

**Failure action:** Print the offending file and pattern. Exit non-zero.

---

## `wiki_tool.py doctor` — Health Summary

Non-mutating check:

| Check | Rule |
|---|---|
| Required folders exist | `Raw/Sources/`, `Wiki/`, `Schema/`, `scripts/`, `_templates/` |
| Python version | Python 3.8+ |
| Catalog exists | `Wiki/catalog.jsonl` present |
| Source manifest exists | `Schema/source-manifest.jsonl` present |
| Note counts | Reports counts of Raw sources and compiled Wiki notes |

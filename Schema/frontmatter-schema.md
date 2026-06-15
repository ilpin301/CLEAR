# Frontmatter Schema

This document defines the required and optional frontmatter fields for each note type.

---

## Raw Source Notes (`Raw/Sources/`)

```yaml
---
Title: ""           # Required. Human-readable title of the source.
Author: ""          # Required. Author or creator name.
Reference: ""       # Required. URL, DOI, ISBN, or unique identifier.
ContentType:        # Required. List; allowed values: markdown, pdf, video, audio, web, other.
  - "markdown"
Created: YYYY-MM-DD # Required. Date the source was captured.
Processed: false    # Required. Set to true after Wiki notes have been compiled from this source.
tags:               # Required. Must include "source".
  - "source"
---
```

**All six fields are required.** `source-lint` will fail if any are missing.

---

## Compiled Wiki Notes (`Wiki/`)

```yaml
---
tags:               # Required. Exactly one of: topic, concept, entity, project, log.
  - "concept"
topics: []          # Optional. List of related topic note filenames.
status: seed        # Required. One of: seed, draft, stable.
created: YYYY-MM-DD # Required.
updated: YYYY-MM-DD # Required.
sources: []         # Required. List of Raw source paths, e.g. "Raw/Sources/example.md".
source_count: 0     # Required. Must equal len(sources). lint will fail if mismatched.
aliases: []         # Optional. Alternative names for this note.
---
```

**Allowed tag values:** `topic`, `concept`, `entity`, `project`, `log`

**`source_count` must exactly equal the number of entries in `sources`.** The lint gate checks this.

---

## Notes

- Do not add extra frontmatter fields not listed here without updating this schema.
- `YYYY-MM-DD` format is required for all date fields.
- `sources` entries must be paths relative to the vault root, e.g. `Raw/Sources/example.md`.

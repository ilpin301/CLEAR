# Workflow Examples

Worked examples of the two core workflows: ingest and query.

---

## Example 1: Ingest A New Source

**Scenario:** A new file `Raw/Sources/llm-wiki-intro.md` has been added with `Processed: false`.

### 1. Search the catalog for related notes

```bash
python scripts/wiki_tool.py search-catalog --query "llm wiki knowledge management"
```

Output might show: `Wiki/Concepts/two-layer-workflow.md`, `Wiki/Topics/llm-wiki.md`

### 2. Open only the most relevant existing Wiki notes

Read `Wiki/Topics/llm-wiki.md` — it looks like an update candidate.

### 3. Compile new or updated notes

Create `Wiki/Concepts/source-coverage.md`:

```yaml
---
tags:
  - "concept"
topics: []
status: seed
created: 2024-01-15
updated: 2024-01-15
sources:
  - "Raw/Sources/llm-wiki-intro.md"
source_count: 1
aliases: []
---

# Source Coverage

Source coverage describes whether a Raw source has been compiled into Wiki notes.
A source is "covered" when at least one Wiki note references it in its `sources` field.
```

### 4. Mark the Raw source as processed

In `Raw/Sources/llm-wiki-intro.md`, set `Processed: true`.

### 5. Run the maintenance gate

```bash
python scripts/wiki_tool.py build
python scripts/wiki_tool.py lint
python scripts/wiki_tool.py source-scan --update --accept-covered
python scripts/wiki_tool.py source-lint
```

---

## Example 2: Query The Wiki

**Scenario:** The user asks "What is the two-layer workflow in LLM Wiki?"

### 1. Check the master index

```bash
# Read Wiki/index.md for a map of available topics
```

### 2. Search the catalog

```bash
python scripts/wiki_tool.py search-catalog --query "two-layer workflow"
```

Output: `Wiki/Concepts/two-layer-workflow.md`

### 3. Open the Wiki note

Read `Wiki/Concepts/two-layer-workflow.md` and answer from it.

### 4. If more detail is needed

Open `Raw/Sources/llm-wiki-intro.md` (listed in the note's `sources`).

Cite both: "According to `Wiki/Concepts/two-layer-workflow.md` (sourced from `Raw/Sources/llm-wiki-intro.md`), …"

---

## Example 3: Running The Full Maintenance Gate

```bash
python scripts/wiki_tool.py doctor
python scripts/wiki_tool.py build
python scripts/wiki_tool.py lint
python scripts/wiki_tool.py source-scan --update --accept-covered
python scripts/wiki_tool.py source-lint
python scripts/audit_public.py
```

All commands should exit 0 before committing.

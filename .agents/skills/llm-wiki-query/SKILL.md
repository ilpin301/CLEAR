# Skill: llm-wiki-query

## Purpose

Answer questions using the compiled Wiki, minimizing unnecessary Raw source reads.

## When To Use

- The user asks a question that may be answered from existing Wiki notes
- Before reading any Raw sources

## Steps

1. Start with `Wiki/index.md` for a high-level map of available topics.
2. Search the catalog for the most relevant notes:
   ```powershell
   python scripts/wiki_tool.py search-catalog --query "<user's question or key terms>"
   ```
3. Open the top matching Wiki notes.
4. Answer from the compiled Wiki notes.
5. If the compiled notes are insufficient or the user needs source-level verification:
   - Open the Raw sources listed in the `sources` field of the Wiki note.
   - Cite both the Wiki note and the Raw source in your answer.

## Constraints

- Do not open Raw sources unnecessarily — the Wiki is the authoritative layer.
- Cite the compiled note and Raw source when the answer depends on source material.
- If no relevant Wiki notes exist, say so and suggest running the ingest skill.

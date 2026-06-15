# Skill: llm-wiki-pdf-extract

## Purpose

Convert PDF files in `Raw/Files/` into readable `.pdf.md` companion files using NotebookLM, so they can be ingested into the Wiki.

## When To Use

- A PDF exists in `Raw/Files/` without a matching `.pdf.md` companion file
- The user asks to "extract", "convert", or "process" a PDF
- Before running `llm-wiki-ingest` on a PDF-sourced file

## Prerequisites

- `notebooklm` CLI must be authenticated: `notebooklm status`
- If not authenticated, run: `notebooklm login`

## Steps

1. Identify which PDFs are missing a companion file:
   - For each `Raw/Files/*.pdf`, check if `Raw/Files/<name>.pdf.md` exists.
   - Process only the missing ones (do not overwrite existing companions unless asked).

2. For each PDF to process:

   a. Create a dedicated notebook:
   ```bash
   notebooklm create "<title from filename>" --json
   # parse: .notebook.id
   ```

   b. Upload the PDF:
   ```bash
   notebooklm source add "Raw/Files/<filename>.pdf" --notebook <notebook_id> --json
   # parse: .source.id
   ```

   c. Wait for processing:
   ```bash
   notebooklm source wait <source_id> --notebook <notebook_id> --timeout 300
   ```

   d. Generate a study guide:
   ```bash
   notebooklm generate report --format study-guide --notebook <notebook_id> --json
   # parse: .task_id
   ```

   e. Wait for generation to complete:
   ```bash
   notebooklm artifact wait <task_id> --notebook <notebook_id> --timeout 600
   ```

   f. Download as markdown companion file:
   ```bash
   notebooklm download report "Raw/Files/<filename>.pdf.md" \
     --artifact <task_id> --notebook <notebook_id>
   ```

   g. If the download saved to a different filename (NotebookLM may append suffixes),
      rename the output to the correct `<filename>.pdf.md` path.

3. Verify the companion file exists and is non-empty before continuing.

4. The resulting `.pdf.md` file is now ready for `llm-wiki-ingest`.

## Output Format

The companion file is saved as `Raw/Files/<original-name>.pdf.md` and contains
a structured markdown study guide: key concepts, Q&A, glossary, and essay prompts.

## Constraints

- Do not modify the original PDF files.
- One NotebookLM notebook per PDF — keeps sources clean and isolated.
- Do not overwrite an existing `.pdf.md` unless the user explicitly requests a refresh.
- If `notebooklm source wait` or `artifact wait` times out, report the failure and do not save an empty file.

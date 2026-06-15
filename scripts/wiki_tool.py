#!/usr/bin/env python3
"""
wiki_tool.py — Deterministic LLM Wiki tooling.
Uses only the Python standard library.

Commands:
  doctor                              Non-mutating health check.
  build                               Generate catalog, index files.
  lint                                Validate compiled Wiki note frontmatter.
  source-scan [--update] [--accept-covered]
                                      List Raw sources; optionally update source manifest.
  source-lint                         Validate Raw source frontmatter and coverage.
  source-delta                        Show Raw sources not in the manifest.
  source-coverage                     Show which Raw sources are covered by Wiki notes.
  search-catalog --query "text"       Search compiled Wiki notes through the catalog.
  log --title "title" --details "text"
                                      Append entry to Wiki/log.md.
"""

import sys
import os
import json
import re
import argparse
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent


def find_md_files(folder: Path):
    """Yield all .md files under folder, skipping index.md and .gitkeep."""
    if not folder.exists():
        return
    for p in sorted(folder.rglob("*.md")):
        if p.name.lower() == "index.md":
            continue
        yield p


def parse_frontmatter(text: str):
    """Parse YAML-like frontmatter from a Markdown string.
    Returns (meta_dict, body_str). meta_dict is empty if no frontmatter found.
    """
    meta = {}
    body = text
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            fm_block = text[3:end].strip()
            body = text[end + 4:].lstrip("\n")
            meta = _parse_simple_yaml(fm_block)
    return meta, body


def _parse_simple_yaml(block: str) -> dict:
    """Very small YAML parser — handles the subset used in this wiki."""
    result = {}
    lines = block.splitlines()
    i = 0
    while i < len(lines):
        line = lines[i]
        # Skip blank lines and comments
        if not line.strip() or line.strip().startswith("#"):
            i += 1
            continue
        # List item under a key
        if line.startswith("  - ") or line.startswith("- "):
            # orphan list item — skip
            i += 1
            continue
        # Key: value
        m = re.match(r'^(\w[\w\-]*):\s*(.*)', line)
        if m:
            key = m.group(1)
            val = m.group(2).strip()
            # Strip inline quotes
            if val and val[0] in ('"', "'") and val[-1] == val[0]:
                val = val[1:-1]
            # Check if next lines are list items
            sub_list = []
            j = i + 1
            while j < len(lines) and (lines[j].startswith("  - ") or lines[j].startswith("- ")):
                item = lines[j].strip()[2:].strip()
                if item and item[0] in ('"', "'") and item[-1] == item[0]:
                    item = item[1:-1]
                sub_list.append(item)
                j += 1
            if sub_list:
                result[key] = sub_list
                i = j
                continue
            # Boolean
            if val.lower() == "true":
                result[key] = True
            elif val.lower() == "false":
                result[key] = False
            elif val == "":
                result[key] = None
            else:
                # Try integer
                try:
                    result[key] = int(val)
                except ValueError:
                    result[key] = val
        i += 1
    return result


def today() -> str:
    return date.today().isoformat()


def rel(path: Path) -> str:
    """Return path relative to ROOT, with forward slashes."""
    try:
        return path.relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


# ---------------------------------------------------------------------------
# doctor
# ---------------------------------------------------------------------------

def cmd_doctor():
    print("=== wiki_tool doctor ===")
    ok = True

    # Required folders
    required_dirs = [
        ROOT / "Raw" / "Sources",
        ROOT / "Wiki",
        ROOT / "Schema",
        ROOT / "scripts",
        ROOT / "_templates",
        ROOT / ".agents" / "skills",
    ]
    for d in required_dirs:
        if d.exists():
            print(f"  [OK]  {rel(d)}/")
        else:
            print(f"  [MISS] {rel(d)}/")
            ok = False

    # Python version
    major, minor = sys.version_info[:2]
    if major >= 3 and minor >= 8:
        print(f"  [OK]  Python {major}.{minor}")
    else:
        print(f"  [WARN] Python {major}.{minor} — 3.8+ recommended")

    # Catalog
    catalog = ROOT / "Wiki" / "catalog.jsonl"
    if catalog.exists():
        count = sum(1 for _ in catalog.read_text(encoding="utf-8").splitlines() if _.strip())
        print(f"  [OK]  Wiki/catalog.jsonl ({count} entries)")
    else:
        print("  [MISS] Wiki/catalog.jsonl — run `build` to generate")

    # Source manifest
    manifest = ROOT / "Schema" / "source-manifest.jsonl"
    if manifest.exists():
        count = sum(1 for _ in manifest.read_text(encoding="utf-8").splitlines() if _.strip())
        print(f"  [OK]  Schema/source-manifest.jsonl ({count} entries)")
    else:
        print("  [MISS] Schema/source-manifest.jsonl — run `source-scan --update`")

    # Note counts
    raw_count = len(list(find_md_files(ROOT / "Raw" / "Sources")))
    wiki_count = sum(
        len(list(find_md_files(ROOT / "Wiki" / sub)))
        for sub in ("Topics", "Concepts", "Entities", "Projects", "Logs")
    )
    print(f"  [INFO] Raw sources: {raw_count}")
    print(f"  [INFO] Compiled Wiki notes: {wiki_count}")

    if ok:
        print("\ndoctor: all checks passed.")
    else:
        print("\ndoctor: some checks failed — see above.")
        sys.exit(1)


# ---------------------------------------------------------------------------
# build
# ---------------------------------------------------------------------------

def _load_wiki_notes():
    """Return list of dicts for all compiled Wiki notes."""
    notes = []
    for sub in ("Topics", "Concepts", "Entities", "Projects", "Logs"):
        folder = ROOT / "Wiki" / sub
        for p in find_md_files(folder):
            text = p.read_text(encoding="utf-8")
            meta, _ = parse_frontmatter(text)
            tags = meta.get("tags") or []
            if isinstance(tags, str):
                tags = [tags]
            tag = tags[0] if tags else ""
            sources = meta.get("sources") or []
            if isinstance(sources, str):
                sources = [sources]
            topics = meta.get("topics") or []
            if isinstance(topics, str):
                topics = [topics]
            title = meta.get("title") or meta.get("Title") or p.stem.replace("-", " ").title()
            notes.append({
                "path": rel(p),
                "title": title,
                "tag": tag,
                "topics": topics,
                "sources": sources,
                "updated": meta.get("updated") or meta.get("Updated") or "",
            })
    return notes


def cmd_build():
    print("=== wiki_tool build ===")
    notes = _load_wiki_notes()

    # Write catalog.jsonl
    catalog_path = ROOT / "Wiki" / "catalog.jsonl"
    lines = [json.dumps(n, ensure_ascii=False) for n in notes]
    catalog_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
    print(f"  Wrote {catalog_path.name} ({len(notes)} entries)")

    # Write per-folder index files
    sub_tags = {
        "Topics": "topic",
        "Concepts": "concept",
        "Entities": "entity",
        "Projects": "project",
        "Logs": "log",
    }
    for sub, tag in sub_tags.items():
        folder = ROOT / "Wiki" / sub
        folder_notes = [n for n in notes if n["tag"] == tag]
        lines_md = [f"# {sub} Index\n", f"_Auto-generated by wiki_tool build on {today()}._\n"]
        if folder_notes:
            for n in sorted(folder_notes, key=lambda x: x["title"].lower()):
                fname = Path(n["path"]).name
                lines_md.append(f"- [[{fname[:-3]}]] — {n['title']}")
        else:
            lines_md.append("_No notes yet._")
        idx_path = folder / "index.md"
        idx_path.write_text("\n".join(lines_md) + "\n", encoding="utf-8")
        print(f"  Wrote Wiki/{sub}/index.md ({len(folder_notes)} notes)")

    # Write master Wiki/index.md
    master_lines = [
        "# Wiki Index\n",
        f"_Auto-generated by wiki_tool build on {today()}._\n",
        f"**Total compiled notes:** {len(notes)}\n",
    ]
    for sub in ("Topics", "Concepts", "Entities", "Projects", "Logs"):
        sub_notes = [n for n in notes if n["tag"] == sub.rstrip("s").lower()
                     or (sub == "Logs" and n["tag"] == "log")]
        # Fix: match correctly
        tag_map = {"Topics": "topic", "Concepts": "concept", "Entities": "entity",
                   "Projects": "project", "Logs": "log"}
        sub_notes = [n for n in notes if n["tag"] == tag_map[sub]]
        master_lines.append(f"\n## {sub} ({len(sub_notes)})\n")
        if sub_notes:
            for n in sorted(sub_notes, key=lambda x: x["title"].lower()):
                fname = Path(n["path"]).name
                master_lines.append(f"- [[Wiki/{sub}/{fname[:-3]}]] — {n['title']}")
        else:
            master_lines.append("_No notes yet._")
    idx_path = ROOT / "Wiki" / "index.md"
    idx_path.write_text("\n".join(master_lines) + "\n", encoding="utf-8")
    print(f"  Wrote Wiki/index.md")
    print(f"\nbuild: complete.")


# ---------------------------------------------------------------------------
# lint
# ---------------------------------------------------------------------------

ALLOWED_TAGS = {"topic", "concept", "entity", "project", "log"}
ALLOWED_STATUS = {"seed", "draft", "stable"}


def cmd_lint():
    print("=== wiki_tool lint ===")
    errors = []

    for sub in ("Topics", "Concepts", "Entities", "Projects", "Logs"):
        folder = ROOT / "Wiki" / sub
        for p in find_md_files(folder):
            text = p.read_text(encoding="utf-8")
            meta, _ = parse_frontmatter(text)
            path_str = rel(p)

            # tags
            tags = meta.get("tags")
            if not tags:
                errors.append(f"{path_str}: missing 'tags' field")
                continue
            if isinstance(tags, str):
                tags = [tags]
            if not any(t in ALLOWED_TAGS for t in tags):
                errors.append(f"{path_str}: tag '{tags[0]}' not in allowed set {ALLOWED_TAGS}")

            # status
            status = meta.get("status")
            if status and status not in ALLOWED_STATUS:
                errors.append(f"{path_str}: status '{status}' not in {ALLOWED_STATUS}")

            # sources
            sources = meta.get("sources")
            if sources is None:
                errors.append(f"{path_str}: missing 'sources' field")
                sources = []
            if isinstance(sources, str):
                sources = [sources]

            # source_count
            sc = meta.get("source_count")
            if sc is None:
                errors.append(f"{path_str}: missing 'source_count' field")
            elif sc != len(sources):
                errors.append(f"{path_str}: source_count={sc} but len(sources)={len(sources)}")

            # source files exist
            for src in sources:
                src_path = ROOT / src
                if not src_path.exists():
                    errors.append(f"{path_str}: source '{src}' does not exist")

            # created / updated
            if not meta.get("created"):
                errors.append(f"{path_str}: missing 'created' field")
            if not meta.get("updated"):
                errors.append(f"{path_str}: missing 'updated' field")

    if errors:
        print(f"\nlint: {len(errors)} error(s) found:\n")
        for e in errors:
            print(f"  ERROR: {e}")
        sys.exit(1)
    else:
        print("lint: all checks passed.")


# ---------------------------------------------------------------------------
# source-scan
# ---------------------------------------------------------------------------

def cmd_source_scan(update: bool, accept_covered: bool):
    print("=== wiki_tool source-scan ===")
    sources_dir = ROOT / "Raw" / "Sources"
    sources = list(find_md_files(sources_dir))
    print(f"  Found {len(sources)} source file(s) in Raw/Sources/\n")

    # Build coverage map from Wiki notes
    coverage = {}  # src_rel_path -> [wiki_note_paths]
    for sub in ("Topics", "Concepts", "Entities", "Projects", "Logs"):
        for p in find_md_files(ROOT / "Wiki" / sub):
            meta, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
            srcs = meta.get("sources") or []
            if isinstance(srcs, str):
                srcs = [srcs]
            for s in srcs:
                coverage.setdefault(s, []).append(rel(p))

    entries = []
    for p in sources:
        meta, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
        src_rel = rel(p)
        covered_by = coverage.get(src_rel, [])
        processed = meta.get("Processed") or meta.get("processed") or False
        if accept_covered and covered_by and not processed:
            processed = True  # treat as covered
        entry = {
            "path": src_rel,
            "title": meta.get("Title") or meta.get("title") or p.stem,
            "processed": processed,
            "covered_by": covered_by,
            "updated": today(),
        }
        entries.append(entry)
        status = "covered" if covered_by else ("processed" if processed else "unprocessed")
        print(f"  [{status:>11}] {src_rel}")

    if update:
        manifest_path = ROOT / "Schema" / "source-manifest.jsonl"
        lines = [json.dumps(e, ensure_ascii=False) for e in entries]
        manifest_path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")
        print(f"\n  Wrote Schema/source-manifest.jsonl ({len(entries)} entries)")
    print("\nsource-scan: complete.")


# ---------------------------------------------------------------------------
# source-lint
# ---------------------------------------------------------------------------

def cmd_source_lint():
    print("=== wiki_tool source-lint ===")
    errors = []

    # Build coverage map
    coverage = {}
    for sub in ("Topics", "Concepts", "Entities", "Projects", "Logs"):
        for p in find_md_files(ROOT / "Wiki" / sub):
            meta, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
            srcs = meta.get("sources") or []
            if isinstance(srcs, str):
                srcs = [srcs]
            for s in srcs:
                coverage.setdefault(s, []).append(rel(p))

    sources_dir = ROOT / "Raw" / "Sources"
    for p in find_md_files(sources_dir):
        text = p.read_text(encoding="utf-8")
        meta, _ = parse_frontmatter(text)
        path_str = rel(p)

        for field in ("Title", "Reference", "Created", "Processed"):
            if meta.get(field) is None and meta.get(field.lower()) is None:
                errors.append(f"{path_str}: missing '{field}' field")

        tags = meta.get("tags") or []
        if isinstance(tags, str):
            tags = [tags]
        if "source" not in tags:
            errors.append(f"{path_str}: 'tags' must include 'source'")

        processed = meta.get("Processed") if meta.get("Processed") is not None else meta.get("processed")
        if processed is True:
            if not coverage.get(path_str):
                errors.append(
                    f"{path_str}: Processed=true but no Wiki note references this source"
                )

    if errors:
        print(f"\nsource-lint: {len(errors)} error(s):\n")
        for e in errors:
            print(f"  ERROR: {e}")
        sys.exit(1)
    else:
        print("source-lint: all checks passed.")


# ---------------------------------------------------------------------------
# source-delta
# ---------------------------------------------------------------------------

def cmd_source_delta():
    print("=== wiki_tool source-delta ===")
    manifest_path = ROOT / "Schema" / "source-manifest.jsonl"
    if not manifest_path.exists():
        print("  source-manifest.jsonl not found — run `source-scan --update` first.")
        sys.exit(1)

    manifest_paths = set()
    for line in manifest_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            entry = json.loads(line)
            manifest_paths.add(entry["path"])

    sources_dir = ROOT / "Raw" / "Sources"
    delta = []
    for p in find_md_files(sources_dir):
        r = rel(p)
        if r not in manifest_paths:
            delta.append(r)

    if delta:
        print(f"  {len(delta)} source(s) not in manifest:")
        for d in delta:
            print(f"  - {d}")
    else:
        print("  No delta — all sources are in the manifest.")
    print("\nsource-delta: complete.")


# ---------------------------------------------------------------------------
# source-coverage
# ---------------------------------------------------------------------------

def cmd_source_coverage():
    print("=== wiki_tool source-coverage ===")
    coverage = {}
    for sub in ("Topics", "Concepts", "Entities", "Projects", "Logs"):
        for p in find_md_files(ROOT / "Wiki" / sub):
            meta, _ = parse_frontmatter(p.read_text(encoding="utf-8"))
            srcs = meta.get("sources") or []
            if isinstance(srcs, str):
                srcs = [srcs]
            for s in srcs:
                coverage.setdefault(s, []).append(rel(p))

    sources_dir = ROOT / "Raw" / "Sources"
    covered = 0
    uncovered = 0
    for p in find_md_files(sources_dir):
        r = rel(p)
        wiki_notes = coverage.get(r, [])
        if wiki_notes:
            covered += 1
            print(f"  [covered]   {r}")
            for n in wiki_notes:
                print(f"              -> {n}")
        else:
            uncovered += 1
            print(f"  [uncovered] {r}")

    print(f"\n  Total: {covered} covered, {uncovered} uncovered.")
    print("\nsource-coverage: complete.")


# ---------------------------------------------------------------------------
# search-catalog
# ---------------------------------------------------------------------------

def cmd_search_catalog(query: str):
    print(f"=== wiki_tool search-catalog: '{query}' ===")
    catalog_path = ROOT / "Wiki" / "catalog.jsonl"
    if not catalog_path.exists():
        print("  catalog.jsonl not found — run `build` first.")
        sys.exit(1)

    terms = query.lower().split()
    results = []
    for line in catalog_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        entry = json.loads(line)
        text = (entry.get("title", "") + " " + entry.get("tag", "") + " " +
                " ".join(entry.get("topics", []))).lower()
        score = sum(1 for t in terms if t in text)
        if score > 0:
            results.append((score, entry))

    results.sort(key=lambda x: -x[0])
    if results:
        print(f"  {len(results)} result(s):\n")
        for score, entry in results:
            print(f"  [{entry['tag']:>7}] {entry['path']}")
            print(f"            Title: {entry['title']}")
    else:
        print("  No matching notes found.")
    print("\nsearch-catalog: complete.")


# ---------------------------------------------------------------------------
# log
# ---------------------------------------------------------------------------

def cmd_log(title: str, details: str):
    print(f"=== wiki_tool log ===")
    log_path = ROOT / "Wiki" / "log.md"
    entry = f"\n## {today()} — {title}\n\n{details}\n"
    if log_path.exists():
        existing = log_path.read_text(encoding="utf-8")
        log_path.write_text(existing + entry, encoding="utf-8")
    else:
        log_path.write_text(f"# Wiki Log\n\nAuto-generated log of notable Wiki changes.\n{entry}",
                            encoding="utf-8")
    print(f"  Appended entry to Wiki/log.md: {title}")
    print("\nlog: complete.")


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="LLM Wiki deterministic tooling.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("doctor", help="Non-mutating health check.")
    sub.add_parser("build", help="Generate catalog and index files.")
    sub.add_parser("lint", help="Validate compiled Wiki note frontmatter.")

    p_scan = sub.add_parser("source-scan", help="List Raw sources; optionally update manifest.")
    p_scan.add_argument("--update", action="store_true", help="Write source-manifest.jsonl.")
    p_scan.add_argument("--accept-covered", action="store_true",
                        help="Mark sources as processed if covered by Wiki notes.")

    sub.add_parser("source-lint", help="Validate Raw source frontmatter and coverage.")
    sub.add_parser("source-delta", help="Show Raw sources not in the manifest.")
    sub.add_parser("source-coverage", help="Show which Raw sources are covered by Wiki notes.")

    p_search = sub.add_parser("search-catalog", help="Search compiled Wiki notes.")
    p_search.add_argument("--query", required=True, help="Search terms.")

    p_log = sub.add_parser("log", help="Append entry to Wiki/log.md.")
    p_log.add_argument("--title", required=True)
    p_log.add_argument("--details", required=True)

    args = parser.parse_args()

    if args.command == "doctor":
        cmd_doctor()
    elif args.command == "build":
        cmd_build()
    elif args.command == "lint":
        cmd_lint()
    elif args.command == "source-scan":
        cmd_source_scan(update=args.update, accept_covered=args.accept_covered)
    elif args.command == "source-lint":
        cmd_source_lint()
    elif args.command == "source-delta":
        cmd_source_delta()
    elif args.command == "source-coverage":
        cmd_source_coverage()
    elif args.command == "search-catalog":
        cmd_search_catalog(query=args.query)
    elif args.command == "log":
        cmd_log(title=args.title, details=args.details)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

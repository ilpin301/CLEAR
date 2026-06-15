#!/usr/bin/env python3
"""
audit_public.py — Check tracked files for secrets, private keys,
machine-local paths, and plugin/cache state.

Exits 0 if clean, 1 if any issues found.
"""

import sys
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Patterns that must NOT appear in committed files
FORBIDDEN = [
    (re.compile(r'-----BEGIN (?:RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----'), "private key"),
    (re.compile(r'(?i)(?:password|passwd|secret|api_key|apikey|auth_token|access_token)\s*[=:]\s*["\']?\S{4,}'), "secret/credential"),
    (re.compile(r'C:\\Users\\[^\\"\s]+'), "machine-local Windows path"),
    (re.compile(r'/home/[^/"\s]+/'), "machine-local Unix home path"),
    (re.compile(r'/Users/[^/"\s]+/'), "machine-local macOS path"),
]

# File/folder patterns to skip entirely
SKIP_PATTERNS = [
    ".obsidian/plugins/",
    ".obsidian/cache/",
    ".obsidian/logs/",
    ".obsidian/workspace",
    "Raw/Files/",
    ".git/",
    "Drafts/",
    "__pycache__/",
    ".pyc",
    # Skip this script itself — it intentionally contains the forbidden patterns as regex strings
    "scripts/audit_public.py",
]

AUDIT_EXTENSIONS = {
    ".md", ".py", ".sh", ".json", ".jsonl", ".yaml", ".yml", ".txt", ".toml", ".cfg", ".ini"
}


def should_skip(path: Path) -> bool:
    path_str = path.as_posix()
    for pat in SKIP_PATTERNS:
        if pat in path_str:
            return True
    return False


def audit_file(path: Path):
    """Return list of (line_number, pattern_name, line) tuples for violations.

    For Markdown files, lines inside fenced code blocks (``` or ~~~) are
    treated as documentation examples and are not flagged.
    """
    violations = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return violations
    is_markdown = path.suffix.lower() == ".md"
    in_code_block = False
    for i, line in enumerate(text.splitlines(), 1):
        # Track fenced code blocks in Markdown
        if is_markdown:
            stripped = line.strip()
            if stripped.startswith("```") or stripped.startswith("~~~"):
                in_code_block = not in_code_block
            if in_code_block:
                continue
        # For Markdown, strip inline code spans before checking
        check_line = re.sub(r'`[^`]*`', '', line) if is_markdown else line
        for pattern, name in FORBIDDEN:
            if pattern.search(check_line):
                violations.append((i, name, line.strip()))
    return violations


def main():
    print("=== audit_public.py ===")
    all_violations = []

    for p in sorted(ROOT.rglob("*")):
        if p.is_dir():
            continue
        if should_skip(p):
            continue
        if p.suffix.lower() not in AUDIT_EXTENSIONS:
            continue
        violations = audit_file(p)
        for lineno, name, line in violations:
            try:
                rel_path = p.relative_to(ROOT).as_posix()
            except ValueError:
                rel_path = str(p)
            all_violations.append((rel_path, lineno, name, line))

    if all_violations:
        print(f"\naudit_public: {len(all_violations)} violation(s) found:\n")
        for rel_path, lineno, name, line in all_violations:
            print(f"  {rel_path}:{lineno} [{name}]")
            print(f"    {line[:120]}")
        sys.exit(1)
    else:
        print("audit_public: clean — no secrets, private keys, or local paths found.")


if __name__ == "__main__":
    main()

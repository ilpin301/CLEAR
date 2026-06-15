#!/usr/bin/env bash
# install_hooks.sh — Install git hooks for the LLM Wiki.
# Run once after cloning: bash scripts/install_hooks.sh

set -e

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
HOOKS_DIR="$REPO_ROOT/.githooks"
GIT_HOOKS_DIR="$REPO_ROOT/.git/hooks"

if [ ! -d "$GIT_HOOKS_DIR" ]; then
    echo "ERROR: .git/hooks directory not found. Are you in a git repository?"
    exit 1
fi

# Copy pre-commit hook
cp "$HOOKS_DIR/pre-commit" "$GIT_HOOKS_DIR/pre-commit"
chmod +x "$GIT_HOOKS_DIR/pre-commit"
echo "Installed .githooks/pre-commit -> .git/hooks/pre-commit"

# Configure git to use the custom hooks directory (git 2.9+)
git config core.hooksPath .githooks
echo "Configured core.hooksPath = .githooks"

echo "Hooks installed successfully."

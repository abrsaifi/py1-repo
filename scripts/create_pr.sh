#!/usr/bin/env bash
set -euo pipefail

# Usage: ./scripts/create_pr.sh [branch-name] [remote] [base-branch]
BRANCH=${1:-"hybrid/soffice-hybrid-$(date +%Y%m%d-%H%M%S)"}
REMOTE=${2:-origin}
BASE=${3:-main}

echo "Creating branch: $BRANCH"
git fetch "$REMOTE"
git checkout -b "$BRANCH"

echo "Staging changes..."
git add -A

echo "Committing..."
git commit -m "feat(hybrid): prefer LibreOffice UNO daemon with CLI fallback" -m "Includes: services/document_conversion.py, docs, tests, deployment configs"

echo "Pushing to $REMOTE/$BRANCH"
git push -u "$REMOTE" "$BRANCH"

if command -v gh >/dev/null 2>&1; then
  echo "Opening PR with GitHub CLI..."
  gh pr create --base "$BASE" --head "$BRANCH" \
    --title "Hybrid: LibreOffice UNO daemon + CLI fallback" \
    --body "Implements hybrid UNO daemon + CLI fallback, adds docs, tests, and deployment configs."
else
  echo "gh CLI not found. To open a PR manually run:"
  echo "  gh pr create --base $BASE --head $BRANCH --title \"Hybrid: LibreOffice UNO daemon + CLI fallback\" --body \"...\""
fi

echo "Done."

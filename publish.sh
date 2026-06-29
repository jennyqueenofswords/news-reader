#!/bin/bash
# publish.sh — rebuild The News Reader and push the day's reading to GitHub Pages.
#
# Idempotent: if nothing changed, it pushes nothing and exits clean. Safe to run
# every night (or by hand). The daily card pull triggers this from run-studio.sh.
set -euo pipefail
cd "$(dirname "$0")"

python3 build.py

git add -A
if git diff --cached --quiet; then
  echo "[news-reader] nothing new to publish"
  exit 0
fi

git commit -m "reading: $(date '+%Y-%m-%d')"
git push origin main
echo "[news-reader] published $(date '+%Y-%m-%d')"

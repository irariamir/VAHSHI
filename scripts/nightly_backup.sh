#!/bin/bash
# VAHSHI Nightly Backup — هر شب ورک‌اسپیس رو به گیت‌هاب پوش می‌کنه
set -e
cd "$(dirname "$0")/.."
BRANCH="arena/019fe630-vahshi"
DATE=$(date +"%Y-%m-%d %H:%M")
echo "[VAHSHI Backup] $DATE"

# add all changes (data/memories, skills usage, etc.)
git add -A

if git diff --cached --quiet; then
  echo "No changes to backup"
  exit 0
fi

git commit -m "backup: nightly $DATE — auto VAHSHI [skip ci]" || true
git push origin $BRANCH || echo "push failed — check auth"

echo "Backup done: $DATE"

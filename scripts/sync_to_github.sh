#!/usr/bin/env bash
set -euo pipefail
MSG=${1:-"chore: sync brain"}
KEY="${VAHSHI_SSH_KEY:-$HOME/.vahshi/keys/vahshi_github}"
REPO_DIR="${VAHSHI_REPO:-$HOME/VAHSHI}"
export GIT_SSH_COMMAND="ssh -i $KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
cd "$REPO_DIR"
git add -A
git status --short
git commit -m "$MSG" || echo "no changes"
git push origin HEAD
echo pushed

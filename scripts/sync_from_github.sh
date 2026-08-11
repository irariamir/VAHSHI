#!/usr/bin/env bash
set -euo pipefail
KEY="${VAHSHI_SSH_KEY:-$HOME/.vahshi/keys/vahshi_github}"
REPO_DIR="${VAHSHI_REPO:-$HOME/VAHSHI}"
LOCAL="${VAHSHI_HOME:-$HOME/.vahshi}"
export GIT_SSH_COMMAND="ssh -i $KEY -o IdentitiesOnly=yes -o StrictHostKeyChecking=accept-new"
if [ ! -d "$REPO_DIR/.git" ]; then
  git clone git@github.com:irariamir/VAHSHI.git "$REPO_DIR"
fi
cd "$REPO_DIR" && git pull --ff-only
mkdir -p "$LOCAL/memories" "$LOCAL/skills" "$LOCAL/plans" "$LOCAL/state" "$LOCAL/telegram"
cp -f soul/SOUL.md "$LOCAL/SOUL.md"
cp -f memories/*.md "$LOCAL/memories/" 2>/dev/null || true
cp -a skills/. "$LOCAL/skills/"
cp -a plans/. "$LOCAL/plans/" 2>/dev/null || true
cp -f state/* "$LOCAL/state/" 2>/dev/null || true
cp -f config.yaml "$LOCAL/" 2>/dev/null || true
cp -f telegram/channels.json "$LOCAL/telegram/" 2>/dev/null || true
echo "pulled -> $LOCAL"

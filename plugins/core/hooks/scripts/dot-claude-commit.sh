#!/bin/bash
# Pre-command commit hook
# Creates a snapshot commit in ~/.claude and ./.claude before modifying commands

commit_if_git() {
    local dir="$1"
    local label="$2"

    # Check if directory exists
    if [ ! -d "$dir" ]; then
        return 0
    fi

    cd "$dir" || return 0

    # Check if git is initialized
    if [ ! -d ".git" ]; then
        echo "[$label] No git repo, skipping"
        return 0
    fi

    # Check if there are changes to commit
    if git diff --quiet && git diff --cached --quiet; then
        echo "[$label] No changes to commit"
        return 0
    fi

    # Stage all changes and commit
    git add -A
    git commit -m "snapshot: pre-command backup $(date +%Y-%m-%d_%H:%M)" --no-verify 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "[$label] Snapshot created"
    else
        echo "[$label] Nothing to commit"
    fi
}

# Commit in global context
commit_if_git "$HOME/.claude" "global"

# Commit in local context (if exists)
if [ -d "./.claude" ]; then
    commit_if_git "$(pwd)/.claude" "local"
fi

exit 0

#!/bin/bash
# Clawdbot Workspace Backup Script
# Creates timestamped backups of workspace and config

set -e

BACKUP_DIR="$HOME/clawd/backups"
TIMESTAMP=$(date +%Y-%m-%d_%H%M%S)
BACKUP_NAME="clawdbot-backup-$TIMESTAMP"

mkdir -p "$BACKUP_DIR"

echo "📦 Creating backup: $BACKUP_NAME"

# Backup workspace (excluding backups dir and large files)
tar -czf "$BACKUP_DIR/${BACKUP_NAME}-workspace.tar.gz" \
    -C "$HOME" \
    --exclude='clawd/backups' \
    --exclude='clawd/.git' \
    --exclude='*.log' \
    clawd 2>/dev/null || true

# Backup Clawdbot config (excluding sensitive tokens inline - they're in the file but this is local)
tar -czf "$BACKUP_DIR/${BACKUP_NAME}-config.tar.gz" \
    -C "$HOME" \
    --exclude='.clawdbot/sandboxes' \
    --exclude='.clawdbot/logs' \
    --exclude='.clawdbot/agents/*/sessions' \
    .clawdbot 2>/dev/null || true

# Cleanup old backups (keep last 7)
cd "$BACKUP_DIR"
ls -t *-workspace.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm -f
ls -t *-config.tar.gz 2>/dev/null | tail -n +8 | xargs -r rm -f

echo "✅ Backup complete: $BACKUP_DIR"
ls -lh "$BACKUP_DIR"/*$TIMESTAMP* 2>/dev/null || true

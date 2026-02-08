#!/bin/bash
# ========================================
# Encrypted Backup Script
# ========================================
# Backs up /data/ directory to encrypted location
# Runs nightly at 11pm via launchd
# Uses macOS Disk Utility for encryption

set -e  # Exit on error

# Configuration
SOURCE_DIR="/Users/clawdbot/clawd/data"
BACKUP_BASE_DIR="/Users/clawdbot/clawd/backups"
ENCRYPTED_BACKUP_DIR="$BACKUP_BASE_DIR/encrypted-data-backups"
LOG_DIR="/Users/clawdbot/clawd/security-logs"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
BACKUP_NAME="data-backup-$TIMESTAMP"
RETENTION_DAYS=30  # Keep backups for 30 days

# Security audit logger
AUDIT_LOGGER="/Users/clawdbot/clawd/scripts/security_audit_logger.py"

# Ensure directories exist
mkdir -p "$ENCRYPTED_BACKUP_DIR"
mkdir -p "$LOG_DIR"

# Log start
echo "[$TIMESTAMP] Starting encrypted backup..." | tee -a "$LOG_DIR/backup.log"

# Count files and calculate size
FILE_COUNT=$(find "$SOURCE_DIR" -type f | wc -l | xargs)
SIZE_MB=$(du -sm "$SOURCE_DIR" | cut -f1)

echo "Source: $SOURCE_DIR"
echo "Files: $FILE_COUNT"
echo "Size: ${SIZE_MB}MB"

# Create temporary unencrypted archive
TEMP_ARCHIVE="/tmp/$BACKUP_NAME.tar.gz"
echo "Creating archive..."
tar -czf "$TEMP_ARCHIVE" -C "$(dirname "$SOURCE_DIR")" "$(basename "$SOURCE_DIR")"

if [ $? -ne 0 ]; then
    echo "ERROR: Failed to create archive"
    python3 "$AUDIT_LOGGER" BACKUP_EXECUTION encrypted_data_backup failed 0 0 2>/dev/null || true
    exit 1
fi

# Create encrypted sparse bundle (macOS native encryption)
# Using hdiutil to create encrypted disk image
ENCRYPTED_IMAGE="$ENCRYPTED_BACKUP_DIR/$BACKUP_NAME.dmg"

echo "Creating encrypted disk image..."
# Use AES-128 encryption (compatible, secure)
# Password stored in Keychain (more secure than plaintext)
BACKUP_PASSWORD=$(security find-generic-password -w -s "jarvis-backup-encryption" -a "clawdbot" 2>/dev/null || echo "JarvisBackup2026!")

# Create encrypted DMG
hdiutil create \
    -size $(( SIZE_MB + 100 ))m \
    -fs HFS+ \
    -volname "$BACKUP_NAME" \
    -encryption AES-128 \
    -stdinpass \
    -srcfolder "$TEMP_ARCHIVE" \
    "$ENCRYPTED_IMAGE" <<< "$BACKUP_PASSWORD"

if [ $? -eq 0 ]; then
    echo "✅ Encrypted backup created: $ENCRYPTED_IMAGE"
    
    # Cleanup temp archive
    rm -f "$TEMP_ARCHIVE"
    
    # Set secure permissions on encrypted backup
    chmod 600 "$ENCRYPTED_IMAGE"
    
    # Calculate backup size
    BACKUP_SIZE_MB=$(du -sm "$ENCRYPTED_IMAGE" | cut -f1)
    
    # Log success to audit system
    python3 "$AUDIT_LOGGER" BACKUP_EXECUTION encrypted_data_backup success "$FILE_COUNT" "$BACKUP_SIZE_MB" 2>/dev/null || true
    
    echo "[$TIMESTAMP] Backup completed successfully" | tee -a "$LOG_DIR/backup.log"
    
    # Cleanup old backups (keep last 30 days)
    echo "Cleaning up old backups (keeping last $RETENTION_DAYS days)..."
    find "$ENCRYPTED_BACKUP_DIR" -name "data-backup-*.dmg" -mtime +$RETENTION_DAYS -delete
    
    # List current backups
    echo "Current backups:"
    ls -lh "$ENCRYPTED_BACKUP_DIR" | grep "data-backup-"
    
else
    echo "❌ ERROR: Failed to create encrypted backup"
    rm -f "$TEMP_ARCHIVE"
    python3 "$AUDIT_LOGGER" BACKUP_EXECUTION encrypted_data_backup failed 0 0 2>/dev/null || true
    exit 1
fi

# Optional: Sync to iCloud Drive (if available)
ICLOUD_DIR="$HOME/Library/Mobile Documents/com~apple~CloudDocs/Jarvis-Backups"
if [ -d "$HOME/Library/Mobile Documents/com~apple~CloudDocs" ]; then
    echo "Syncing to iCloud Drive..."
    mkdir -p "$ICLOUD_DIR"
    cp "$ENCRYPTED_IMAGE" "$ICLOUD_DIR/" 2>/dev/null || echo "iCloud sync skipped (not available)"
fi

echo "Backup complete!"
echo "Location: $ENCRYPTED_IMAGE"
echo "To restore: hdiutil attach $ENCRYPTED_IMAGE (enter password: stored in Keychain or JarvisBackup2026!)"

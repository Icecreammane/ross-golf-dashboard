# Automated Backup System Setup

**Goal:** Never lose work. Auto-commit and push to GitHub every hour.

**Time to complete:** 5 minutes

**Benefit:** Peace of mind. Never lose more than 1 hour of work.

---

## What This System Does

**Every hour, automatically:**
1. ✅ Checks workspace for changes
2. ✅ Commits changes with timestamp
3. ✅ Pushes to GitHub (full history)
4. ✅ Logs all activity
5. ✅ Runs silently in background

**If no changes:** Logs "No changes" and exits (no spam commits)

**If changes:** Commits and pushes immediately

---

## Prerequisites

✅ Git installed (already have this)  
✅ GitHub repo created: `github.com/Icecreammane/clawd`  
✅ Git authentication configured (SSH or token)

---

## Step 1: Verify Git Configuration (1 min)

**Check current Git setup:**

```bash
cd ~/clawd
git config user.name
git config user.email
git remote -v
```

**Expected output:**
```
Ross Iceman
your-email@example.com
origin  git@github.com:Icecreammane/clawd.git (fetch)
origin  git@github.com:Icecreammane/clawd.git (push)
```

**If not configured:**
```bash
git config --global user.name "Ross Iceman"
git config --global user.email "your-email@example.com"
```

**Verify push access:**
```bash
cd ~/clawd
git push origin main
```

If this works ✅, you're ready. If authentication fails, see "Git Authentication" below.

---

## Step 2: Make Backup Script Executable (30 seconds)

```bash
chmod +x ~/clawd/scripts/auto-backup.sh
```

**Verify permissions:**
```bash
ls -l ~/clawd/scripts/auto-backup.sh
```

Should show: `-rwxr-xr-x` (the `x` means executable)

---

## Step 3: Test the Script (1 min)

**Run manually to test:**

```bash
# Create a test change
echo "Test backup $(date)" >> ~/clawd/test-backup.txt

# Run backup script
~/clawd/scripts/auto-backup.sh

# Check results
cat ~/clawd/logs/auto-backup.log
```

**Expected log output:**
```
[2026-02-07 14:30:00] 🔍 Starting auto-backup check...
[2026-02-07 14:30:00] 📝 Changes detected, starting backup...
[2026-02-07 14:30:00]    Files changed: 1
[2026-02-07 14:30:01] ✅ Changes committed successfully
[2026-02-07 14:30:01] 📤 Pushing to GitHub...
[2026-02-07 14:30:03] ✅ Pushed to GitHub successfully
[2026-02-07 14:30:03] 🎉 Backup complete: 1 files backed up
[2026-02-07 14:30:03] ✅ Auto-backup check complete
```

**Verify on GitHub:**
- Visit: https://github.com/Icecreammane/clawd/commits/main
- Should see new commit: "Auto-backup: 2026-02-07 14:30:00"

✅ **If you see this, backup script works!**

---

## Step 4: Set Up Cron Job (2 minutes)

**Cron** runs the script automatically every hour.

### Edit Crontab

```bash
crontab -e
```

(This opens your cron configuration in a text editor)

### Add This Line

**Copy-paste exactly:**
```
0 * * * * /Users/clawdbot/clawd/scripts/auto-backup.sh
```

**What this means:**
- `0` = At minute 0
- `*` = Every hour
- `*` = Every day
- `*` = Every month
- `*` = Every weekday
- `/Users/clawdbot/clawd/scripts/auto-backup.sh` = Run this script

**Translation:** "Every hour on the hour (1:00, 2:00, 3:00...), run the backup script"

### Save and Exit

- **If using vim:** Press `Esc`, type `:wq`, press `Enter`
- **If using nano:** Press `Ctrl+X`, then `Y`, then `Enter`

### Verify Cron Job Installed

```bash
crontab -l
```

**Should show:**
```
0 * * * * /Users/clawdbot/clawd/scripts/auto-backup.sh
```

✅ **Cron job active!**

---

## Step 5: Test Cron Execution (Optional, 1 min)

**Wait for next hour and check log:**

```bash
# Check current time
date

# Wait for next hour (e.g., if 2:45pm, wait until 3:00pm)
# Then check log
tail -20 ~/clawd/logs/auto-backup.log
```

**Or test immediately with a 1-minute cron:**

```bash
# Temporarily change cron to run every minute
crontab -e
```

Change line to:
```
* * * * * /Users/clawdbot/clawd/scripts/auto-backup.sh
```

Save, wait 1 minute, check log:
```bash
tail -20 ~/clawd/logs/auto-backup.log
```

**After testing, change back to hourly:**
```bash
crontab -e
```

Change back to:
```
0 * * * * /Users/clawdbot/clawd/scripts/auto-backup.sh
```

---

## Verification Checklist

Before considering this complete:

- ✅ Script is executable (`chmod +x`)
- ✅ Manual test run works (commits + pushes)
- ✅ Log file created: `~/clawd/logs/auto-backup.log`
- ✅ Commit visible on GitHub
- ✅ Cron job installed (`crontab -l` shows job)
- ✅ Git authentication works (no password prompts)

---

## What Gets Backed Up

**Included:**
- ✅ All files in `~/clawd/`
- ✅ New files (untracked)
- ✅ Modified files
- ✅ Deleted files (tracked in Git history)

**Excluded (via .gitignore):**
- ❌ `node_modules/`
- ❌ `.DS_Store`
- ❌ `*.log` (except auto-backup.log)
- ❌ Sensitive credentials (if in `.gitignore`)

**Check your .gitignore:**
```bash
cat ~/clawd/.gitignore
```

**Recommended .gitignore contents:**
```
# Dependencies
node_modules/
venv/
__pycache__/

# OS files
.DS_Store
Thumbs.db

# Logs (except auto-backup)
*.log
!logs/auto-backup.log

# Sensitive
.env
*.key
secrets/

# Build artifacts
dist/
build/
*.pyc
```

---

## Manual Backup Command (Bonus)

**Add to your shell (bash/zsh):**

```bash
# Add to ~/.zshrc or ~/.bashrc
alias backup='cd ~/clawd && git add . && git commit -m "Manual backup: $(date)" && git push origin main'
```

**Reload shell:**
```bash
source ~/.zshrc  # or source ~/.bashrc
```

**Now you can manually backup anytime:**
```bash
backup
```

This commits and pushes immediately (doesn't wait for hourly cron).

---

## Monitoring Your Backups

### Check Recent Backups

**View log:**
```bash
tail -50 ~/clawd/logs/auto-backup.log
```

**View recent commits:**
```bash
cd ~/clawd
git log --oneline -10
```

**Check GitHub:**
- Visit: https://github.com/Icecreammane/clawd/commits/main
- Should see hourly "Auto-backup" commits (when changes exist)

### Backup Success Metrics

**Healthy backup system:**
- ✅ Log shows successful pushes
- ✅ GitHub shows recent commits
- ✅ No errors in log file
- ✅ Cron job running (`crontab -l`)

**Problem indicators:**
- ❌ Log shows "Push failed"
- ❌ No recent GitHub commits (when you've been working)
- ❌ Authentication errors in log
- ❌ Cron job missing

---

## Troubleshooting

### ❌ "Push failed - authentication required"

**Problem:** Git doesn't have push access

**Fix Option 1 - SSH Key (Recommended):**

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add to GitHub:
# 1. GitHub.com → Settings → SSH and GPG keys
# 2. "New SSH key"
# 3. Paste public key

# Update remote to use SSH
cd ~/clawd
git remote set-url origin git@github.com:Icecreammane/clawd.git

# Test
git push origin main
```

**Fix Option 2 - Personal Access Token:**

```bash
# GitHub.com → Settings → Developer settings → Personal access tokens
# Generate new token (classic)
# Scopes: "repo" (full control)
# Copy token (save it securely)

# Update remote URL with token
cd ~/clawd
git remote set-url origin https://YOUR_TOKEN@github.com/Icecreammane/clawd.git

# Test
git push origin main
```

### ❌ "Cron job not running"

**Check if cron is running:**
```bash
# macOS
sudo launchctl list | grep cron

# Linux
systemctl status cron
```

**If cron disabled on macOS:**
```bash
# Enable cron via System Preferences
# System Preferences → Security & Privacy → Privacy → Full Disk Access
# Add: /usr/sbin/cron
```

### ❌ "No changes to backup" every hour (but you ARE making changes)

**Problem:** Files might be in `.gitignore`

**Check what's excluded:**
```bash
cd ~/clawd
git status
```

If files you expect aren't listed, they might be gitignored.

**Override gitignore (if needed):**
```bash
git add -f path/to/file  # Force add
```

### ❌ Log file growing too large

**Script auto-rotates logs at 5MB.** Old logs saved as `.old`.

**Manually clear if needed:**
```bash
rm ~/clawd/logs/auto-backup.log
# New log created on next run
```

---

## Restore from Backup

**If you need to restore old work:**

### View Available Commits

```bash
cd ~/clawd
git log --oneline -20  # Show last 20 commits
```

**Example output:**
```
a1b2c3d Auto-backup: 2026-02-13 18:00:00
e4f5g6h Auto-backup: 2026-02-13 17:00:00
i7j8k9l Auto-backup: 2026-02-13 16:00:00
```

### Restore Specific File from Past Commit

```bash
# Restore file from 3 commits ago
git checkout HEAD~3 -- path/to/file.txt

# Or restore from specific commit hash
git checkout a1b2c3d -- path/to/file.txt
```

### Restore Entire Workspace to Earlier Time

```bash
# View state of workspace 5 hours ago
git checkout HEAD~5

# If you want to keep this state:
git checkout -b recovered-state

# Or go back to latest:
git checkout main
```

### Undo Recent Changes (Rollback)

```bash
# Undo last commit (keep changes in workspace)
git reset HEAD~1

# Undo last commit (discard changes - CAREFUL!)
git reset --hard HEAD~1
```

**Always have backups.** With hourly commits, you can roll back to any hour.

---

## Advanced: Multiple Backup Targets

**Backup to multiple Git remotes (GitHub + GitLab/Bitbucket):**

```bash
# Add second remote
cd ~/clawd
git remote add backup https://gitlab.com/yourusername/clawd.git

# Modify script to push to both:
# In auto-backup.sh, replace the push line with:
# git push origin main && git push backup main
```

Now backs up to 2 locations every hour (extra redundancy).

---

## Cost

| Item | Cost |
|------|------|
| **GitHub repo** | FREE (public or private) |
| **Cron job** | FREE (built into macOS) |
| **Disk space** | ~10MB/week for text files |
| **Total** | **$0/month** |

---

## Summary: What You Have Now

✅ **Automated hourly backups** to GitHub  
✅ **Never lose more than 1 hour of work**  
✅ **Full version history** (can restore any hourly snapshot)  
✅ **Zero manual effort** (runs silently in background)  
✅ **Detailed logs** (see exactly what was backed up when)  
✅ **Manual backup command** (`backup` alias for instant commits)

**Setup time:** 5 minutes  
**Maintenance:** Zero (runs automatically forever)  
**Value:** Priceless (saved countless hours of lost work)

---

## Next Steps

1. ✅ Verify cron job running (check log in 1 hour)
2. ✅ Test manual `backup` command
3. ✅ Add backup status to morning routine:
   - Check: `tail -20 ~/clawd/logs/auto-backup.log`
   - Verify recent GitHub commits
4. ✅ Sleep well knowing work is backed up hourly

---

**Your work is now protected. Build with confidence. 🚀**

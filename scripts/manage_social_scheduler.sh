#!/bin/bash
# Social Post Scheduler Manager
# Manage launchd jobs for automated social media posting

LAUNCHD_DIR="/Users/clawdbot/clawd/launchd"
AGENTS_DIR="$HOME/Library/LaunchAgents"

JOBS=(
    "com.clawdbot.social-post-generator"
    "com.clawdbot.social-post-2am"
    "com.clawdbot.social-post-6am"
    "com.clawdbot.social-post-12pm"
    "com.clawdbot.social-post-6pm"
)

function show_usage() {
    echo "Social Post Scheduler Manager"
    echo ""
    echo "Usage: $0 [command]"
    echo ""
    echo "Commands:"
    echo "  install   - Install and load all scheduler jobs"
    echo "  uninstall - Unload and remove all scheduler jobs"
    echo "  start     - Load all jobs (if already installed)"
    echo "  stop      - Unload all jobs"
    echo "  status    - Show status of all jobs"
    echo "  test      - Test post generation (dry run)"
    echo ""
}

function install_jobs() {
    echo "📦 Installing social scheduler jobs..."
    
    for job in "${JOBS[@]}"; do
        SOURCE="$LAUNCHD_DIR/${job}.plist"
        DEST="$AGENTS_DIR/${job}.plist"
        
        if [ -f "$SOURCE" ]; then
            cp "$SOURCE" "$DEST"
            echo "  ✅ Copied $job"
        else
            echo "  ❌ Source file not found: $SOURCE"
        fi
    done
    
    echo ""
    echo "🚀 Loading jobs..."
    start_jobs
}

function uninstall_jobs() {
    echo "🗑️  Uninstalling social scheduler jobs..."
    
    stop_jobs
    
    for job in "${JOBS[@]}"; do
        DEST="$AGENTS_DIR/${job}.plist"
        if [ -f "$DEST" ]; then
            rm "$DEST"
            echo "  ✅ Removed $job"
        fi
    done
    
    echo "✅ Uninstall complete"
}

function start_jobs() {
    echo "🚀 Starting jobs..."
    
    for job in "${JOBS[@]}"; do
        launchctl load "$AGENTS_DIR/${job}.plist" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "  ✅ Loaded $job"
        else
            echo "  ⚠️  $job (may already be loaded)"
        fi
    done
    
    echo "✅ Start complete"
}

function stop_jobs() {
    echo "🛑 Stopping jobs..."
    
    for job in "${JOBS[@]}"; do
        launchctl unload "$AGENTS_DIR/${job}.plist" 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "  ✅ Unloaded $job"
        else
            echo "  ⚠️  $job (may not be loaded)"
        fi
    done
    
    echo "✅ Stop complete"
}

function show_status() {
    echo "📊 Social Scheduler Status"
    echo ""
    
    for job in "${JOBS[@]}"; do
        STATUS=$(launchctl list | grep "$job" || echo "not loaded")
        
        if [ "$STATUS" != "not loaded" ]; then
            echo "  ✅ $job: RUNNING"
        else
            echo "  ❌ $job: NOT LOADED"
        fi
    done
    
    echo ""
    echo "📝 Queue Status:"
    if [ -f "/Users/clawdbot/clawd/data/social-posts-queue.json" ]; then
        TOTAL=$(python3 -c "import json; data=json.load(open('/Users/clawdbot/clawd/data/social-posts-queue.json')); print(len(data))")
        UNPOSTED=$(python3 -c "import json; data=json.load(open('/Users/clawdbot/clawd/data/social-posts-queue.json')); print(len([p for p in data if not p.get('posted', False)]))")
        echo "  Total posts: $TOTAL"
        echo "  Unposted: $UNPOSTED"
    else
        echo "  Queue file not found (run generator first)"
    fi
    
    echo ""
    echo "📅 Schedule:"
    echo "  Post Generation: Daily at 11:00 PM CST"
    echo "  Auto-Posting:    2am, 6am, 12pm, 6pm CST"
}

function test_generation() {
    echo "🧪 Testing post generation..."
    echo ""
    python3 /Users/clawdbot/clawd/scripts/generate_social_posts.py
    echo ""
    echo "📋 Generated posts:"
    python3 -c "
import json
with open('/Users/clawdbot/clawd/data/social-posts-queue.json', 'r') as f:
    queue = json.load(f)
    unposted = [p for p in queue if not p.get('posted', False)]
    for i, post in enumerate(unposted[-3:], 1):
        print(f'\n{i}. [{post[\"theme\"]}]')
        print(f'   {post[\"text\"]}')
        if post.get('image_placeholder'):
            print(f'   {post[\"image_placeholder\"]}')
" 2>/dev/null || echo "Error reading queue"
}

# Main command handler
case "${1:-}" in
    install)
        install_jobs
        ;;
    uninstall)
        uninstall_jobs
        ;;
    start)
        start_jobs
        ;;
    stop)
        stop_jobs
        ;;
    status)
        show_status
        ;;
    test)
        test_generation
        ;;
    *)
        show_usage
        exit 1
        ;;
esac

#!/bin/bash
# Complete Cost Optimization Setup
# Reduces monthly costs by 85% ($300-600 → $50-100/month)

set -e

echo "🎯 OpenClaw Cost Optimization Setup"
echo "===================================="
echo ""

# Check Ollama
echo "✓ Checking Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama not installed. Installing..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# Check Qwen model
echo "✓ Checking Qwen 32B model..."
if ! ollama list | grep -q "qwen2.5:32b"; then
    echo "📥 Pulling Qwen 32B (19GB, this will take a while)..."
    ollama pull qwen2.5:32b-instruct-q4_K_M
fi

# Test Ollama
echo "✓ Testing Ollama..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama running"
else
    echo "⚠️  Starting Ollama..."
    ollama serve &
    sleep 3
fi

# Update cron jobs file to use Haiku
echo "✓ Updating cron jobs to use Haiku..."
CRON_FILE=~/.clawdbot/cron/jobs.json
if [ -f "$CRON_FILE" ]; then
    # Backup
    cp "$CRON_FILE" "$CRON_FILE.bak"
    
    # Update model references (if any hardcoded Sonnet)
    sed -i.tmp 's/"model": "anthropic\/claude-sonnet-4-5"/"model": "anthropic\/claude-haiku-4-5"/g' "$CRON_FILE"
    rm -f "$CRON_FILE.tmp"
    echo "✅ Cron jobs updated"
fi

echo ""
echo "✅ Cost Optimization Complete!"
echo ""
echo "📊 Expected Savings:"
echo "   Before: $300-600/month"
echo "   After:  $50-100/month (85% reduction)"
echo ""
echo "🔍 Monitor usage:"
echo "   python3 ~/clawd/scripts/cost_tracker.py month"
echo ""
echo "📝 Full docs: ~/clawd/docs/COST_OPTIMIZATION.md"

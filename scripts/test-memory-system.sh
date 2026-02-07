#!/bin/bash
# Test script for semantic memory system

set -e  # Exit on error

WORKSPACE="/Users/clawdbot/clawd"
VENV_PYTHON="$WORKSPACE/memory/venv/bin/python3"

echo "========================================="
echo "SEMANTIC MEMORY SYSTEM - TEST SUITE"
echo "========================================="
echo ""

# Test 1: Verify installations
echo "Test 1: Verifying Python environment..."
$VENV_PYTHON --version
echo "✓ Python available"
echo ""

echo "Test 2: Checking dependencies..."
$VENV_PYTHON -c "import chromadb; print('✓ ChromaDB installed')"
$VENV_PYTHON -c "import sentence_transformers; print('✓ Sentence-transformers installed')"
echo ""

# Test 3: Embed all sources
echo "Test 3: Embedding all memory sources..."
cd $WORKSPACE
$VENV_PYTHON scripts/semantic_memory.py embed
echo ""

# Test 4: Database stats
echo "Test 4: Checking database statistics..."
$VENV_PYTHON scripts/semantic_memory.py stats
echo ""

# Test 5: Search queries
echo "Test 5: Running test searches..."
echo ""

echo "Query 1: What's Ross's calorie goal?"
$VENV_PYTHON scripts/memory-search.py -n 2 "Ross calorie goal"
echo ""

echo "Query 2: Ross's food preferences?"
$VENV_PYTHON scripts/memory-search.py -n 2 "food preferences Publix"
echo ""

echo "Query 3: What did we build yesterday?"
$VENV_PYTHON scripts/memory-search.py -n 2 --type daily_log "what did we build"
echo ""

# Test 6: Memory helper function
echo "Test 6: Testing memory helper function..."
$VENV_PYTHON scripts/memory_helper.py "Ross workout schedule"
echo ""

echo "========================================="
echo "ALL TESTS COMPLETE!"
echo "========================================="
echo ""
echo "If you see this message, the semantic memory system is working!"
echo ""
echo "Next steps:"
echo "  1. Run 'scripts/search-memory.sh \"your query\"' to search memory"
echo "  2. Integrate check_memory_before_response() into main agent"
echo "  3. Set up cron job for nightly memory extraction"
echo ""

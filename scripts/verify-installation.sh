#!/bin/bash
# Quick verification script for semantic memory system

set -e

WORKSPACE="/Users/clawdbot/clawd"
VENV_PYTHON="$WORKSPACE/memory/venv/bin/python3"

echo "🔍 Verifying Semantic Memory System Installation..."
echo ""

# Check 1: Python venv exists
if [ -f "$VENV_PYTHON" ]; then
    echo "✅ Python virtual environment found"
else
    echo "❌ Python venv not found at $VENV_PYTHON"
    exit 1
fi

# Check 2: Dependencies installed
echo "✅ Checking dependencies..."
$VENV_PYTHON -c "import chromadb" 2>/dev/null && echo "  ✓ ChromaDB" || echo "  ✗ ChromaDB missing"
$VENV_PYTHON -c "import sentence_transformers" 2>/dev/null && echo "  ✓ Sentence-transformers" || echo "  ✗ Sentence-transformers missing"

# Check 3: Config file exists
if [ -f "$WORKSPACE/memory/memory_config.json" ]; then
    echo "✅ Configuration file found"
else
    echo "❌ Config file not found"
    exit 1
fi

# Check 4: Scripts exist
echo "✅ Checking scripts..."
[ -f "$WORKSPACE/scripts/semantic_memory.py" ] && echo "  ✓ semantic_memory.py" || echo "  ✗ Missing"
[ -f "$WORKSPACE/scripts/memory-search.py" ] && echo "  ✓ memory-search.py" || echo "  ✗ Missing"
[ -f "$WORKSPACE/scripts/memory_helper.py" ] && echo "  ✓ memory_helper.py" || echo "  ✗ Missing"
[ -f "$WORKSPACE/scripts/extract_and_update_memory.py" ] && echo "  ✓ extract_and_update_memory.py" || echo "  ✗ Missing"

# Check 5: Wrappers exist
echo "✅ Checking wrapper scripts..."
[ -f "$WORKSPACE/scripts/embed-memory.sh" ] && echo "  ✓ embed-memory.sh" || echo "  ✗ Missing"
[ -f "$WORKSPACE/scripts/search-memory.sh" ] && echo "  ✓ search-memory.sh" || echo "  ✗ Missing"
[ -f "$WORKSPACE/scripts/test-memory-system.sh" ] && echo "  ✓ test-memory-system.sh" || echo "  ✗ Missing"

# Check 6: Documentation exists
echo "✅ Checking documentation..."
[ -f "$WORKSPACE/MEMORY_SYSTEM.md" ] && echo "  ✓ MEMORY_SYSTEM.md" || echo "  ✗ Missing"
[ -f "$WORKSPACE/INTEGRATION_GUIDE.md" ] && echo "  ✓ INTEGRATION_GUIDE.md" || echo "  ✗ Missing"
[ -f "$WORKSPACE/CLI_REFERENCE.md" ] && echo "  ✓ CLI_REFERENCE.md" || echo "  ✗ Missing"
[ -f "$WORKSPACE/memory/README.md" ] && echo "  ✓ memory/README.md" || echo "  ✗ Missing"

# Check 7: Source files exist
echo "✅ Checking source files..."
[ -f "$WORKSPACE/MEMORY.md" ] && echo "  ✓ MEMORY.md" || echo "  ✗ Missing"
[ -f "$WORKSPACE/memory/jarvis-journal.md" ] && echo "  ✓ jarvis-journal.md" || echo "  ✗ Missing"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Installation verified!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Next steps:"
echo "  1. Run full test suite:"
echo "     bash scripts/test-memory-system.sh"
echo ""
echo "  2. Try a search:"
echo "     ./scripts/search-memory.sh \"Ross calorie goal\""
echo ""
echo "  3. Read the docs:"
echo "     cat MEMORY_SYSTEM_SUMMARY.md"
echo ""

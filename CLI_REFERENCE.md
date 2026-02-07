# Semantic Memory - CLI Reference

**Command-line tools for searching and managing Jarvis's memory**

---

## Quick Reference

```bash
# Search memory
./scripts/search-memory.sh "what did Ross say about X?"

# Embed all sources
./scripts/embed-memory.sh

# Run full test suite
bash scripts/test-memory-system.sh

# Get database stats
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py stats

# Prune old embeddings
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py prune 30
```

---

## memory-search.py

Search semantic memory using natural language queries.

### Basic Usage

```bash
# Simple search
./scripts/memory-search.py "Ross calorie goal"

# Using the wrapper script
./scripts/search-memory.sh "Ross calorie goal"
```

### Options

```
positional arguments:
  query                 Search query (multiple words OK)

optional arguments:
  -h, --help            Show help message
  -n N, --num-results N
                        Number of results to return (default: 5)
  -t TYPE, --type TYPE  
                        Filter by source type:
                        - memory (MEMORY.md)
                        - journal (jarvis-journal.md)
                        - daily_log (daily files)
                        - conversation (chat history)
  --min-relevance X     Minimum relevance score 0-1 (default: 0.5)
  --stats               Show database statistics before searching
  --embed               Re-embed all sources before searching
```

### Examples

**Example 1: Basic search**
```bash
./scripts/memory-search.py "calorie goal"

# Output:
# ✓ Semantic memory initialized
# Searching for: "calorie goal"
# Filters: type=all, min_relevance=0.5
# ===================================
# 
# [1] Relevance: 92%
# Source: MEMORY.md (memory)
# Modified: 2026-02-04
# 
# **Daily Calorie Goal:** 2,200 calories
# **Daily Protein Goal:** 200g
# ...
```

**Example 2: Filter by source type**
```bash
# Only search journal entries
./scripts/memory-search.py --type journal "fitness goals"

# Only search recent daily logs
./scripts/memory-search.py --type daily_log "what did we build"
```

**Example 3: Adjust relevance threshold**
```bash
# Only show high-confidence matches
./scripts/memory-search.py --min-relevance 0.8 "food preferences"

# Show more results (including lower relevance)
./scripts/memory-search.py --min-relevance 0.3 "projects"
```

**Example 4: Get more results**
```bash
# Return top 10 results instead of default 5
./scripts/memory-search.py -n 10 "Ross mentioned"
```

**Example 5: Re-embed before searching**
```bash
# Useful if you just updated MEMORY.md
./scripts/memory-search.py --embed "new information"
```

**Example 6: Show statistics**
```bash
./scripts/memory-search.py --stats "anything"

# Output includes:
# Database Statistics:
#   Total chunks: 847
#   Collection: jarvis_memory
#   Source breakdown:
#     memory: 42
#     journal: 156
#     daily_log: 649
```

### Output Format

Results are color-coded by relevance:
- **Green** (>80%): High confidence match
- **Yellow** (60-80%): Good match
- **Red** (<60%): Weak match

Each result shows:
- Relevance score (percentage)
- Source file name and type
- Last modified date
- Matching text excerpt

---

## semantic_memory.py

Core memory management tool.

### Usage

```bash
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py COMMAND
```

### Commands

#### `embed` - Embed all source files

```bash
./scripts/semantic_memory.py embed

# Output:
# ✓ Semantic memory initialized
# Loading embedding model: sentence-transformers/all-MiniLM-L6-v2
# ✓ Embedded 42 chunks from MEMORY.md
# ✓ Embedded 156 chunks from jarvis-journal.md
# ✓ Embedded 89 chunks from 2026-02-01.md
# ✓ Embedded 127 chunks from 2026-02-02.md
# ...
# 
# Embedding complete:
#   MEMORY.md: 42 chunks
#   jarvis-journal.md: 156 chunks
#   2026-02-01.md: 89 chunks
#   ...
```

#### `stats` - Show database statistics

```bash
./scripts/semantic_memory.py stats

# Output:
# Total chunks: 847
# Collection: jarvis_memory
# Source breakdown:
#   memory: 42
#   journal: 156
#   daily_log: 649
```

#### `prune [days]` - Remove old embeddings

```bash
# Remove embeddings older than 30 days (default)
./scripts/semantic_memory.py prune

# Remove embeddings older than 60 days
./scripts/semantic_memory.py prune 60

# Output:
# ✓ Pruned 127 embeddings older than 30 days
```

**Note:** This only removes old daily_log and conversation embeddings. MEMORY.md and journal are never pruned.

#### `reset` - Clear all embeddings (CAUTION!)

```bash
./scripts/semantic_memory.py reset

# Prompts for confirmation:
# Reset all embeddings? (yes/no): yes
# ✓ Memory database reset
```

**Warning:** This deletes the entire vector database. You'll need to re-run `embed` afterwards.

---

## extract_and_update_memory.py

Auto-extract facts from conversations and update memory files.

### Usage

```bash
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/extract_and_update_memory.py [OPTIONS]
```

### Options

```
-f FILE, --file FILE  Process conversation from file
-t TEXT, --text TEXT  Process conversation text directly
--no-memory           Skip updating MEMORY.md
--no-journal          Skip updating journal
--embed-only          Only re-embed existing files (don't process text)
```

### Examples

**Example 1: Process conversation from file**
```bash
./scripts/extract_and_update_memory.py -f conversation.txt

# Output:
# Processing conversation...
# Extracted 8 potential facts
# ✓ Logged to 2026-02-04.md
# ✓ Added 5 new facts to MEMORY.md
# ✓ Updated journal
# 
# Embedding recent changes...
# ✓ Embedded 43 chunks from MEMORY.md
# ✓ Embedded 158 chunks from jarvis-journal.md
# ✓ Embedded 12 chunks from 2026-02-04.md
# 
# ✓ Memory extraction complete
#   Facts extracted: 5
#   Files embedded: 213 chunks
```

**Example 2: Process text directly**
```bash
./scripts/extract_and_update_memory.py -t "Ross mentioned his target weight is 210 lbs"

# Extracts: "Ross's target weight is 210 lbs"
# Adds to MEMORY.md and today's daily log
```

**Example 3: Read from stdin**
```bash
# Type or paste conversation, then press Ctrl+D
./scripts/extract_and_update_memory.py

# Or pipe from another command
echo "Ross prefers dark mode" | ./scripts/extract_and_update_memory.py
```

**Example 4: Only re-embed (don't extract)**
```bash
# Useful after manually editing MEMORY.md
./scripts/extract_and_update_memory.py --embed-only

# Output:
# Re-embedding recent changes...
# ✓ Embedded 43 chunks from MEMORY.md
# ✓ Embedded 158 chunks from jarvis-journal.md
# ✓ Embedded 12 chunks from 2026-02-04.md
```

**Example 5: Skip MEMORY.md update**
```bash
# Log to daily file and journal, but don't update MEMORY.md
./scripts/extract_and_update_memory.py --no-memory -f conversation.txt
```

---

## memory_helper.py

Python helper functions for integration.

### Usage

```bash
# Quick search from command line
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/memory_helper.py "search query"
```

### Python Import

```python
import sys
sys.path.insert(0, '/Users/clawdbot/clawd/scripts')

from memory_helper import (
    check_memory_before_response,
    search_memory,
    quick_embed,
    memory_stats
)

# Check for context
context = check_memory_before_response("Ross calorie goal")
if context:
    print(context)

# Direct search
results = search_memory("food preferences", n_results=5)

# Re-embed recent changes
quick_embed()

# Get statistics
stats = memory_stats()
print(f"Total chunks: {stats['total_chunks']}")
```

### Functions

#### `check_memory_before_response(user_message, min_relevance=0.7)`

Returns formatted context string or None.

```python
context = check_memory_before_response("What's my protein goal?")
# Returns:
# 📚 Relevant memories:
# 
# 1. [MEMORY.md] (94% relevant)
#    **Daily Protein Goal:** 200g
```

#### `search_memory(query, n_results=5, source_type=None)`

Returns list of result dictionaries.

```python
results = search_memory("calorie goal", n_results=3)

for result in results:
    print(f"Relevance: {result['relevance']:.0%}")
    print(f"Text: {result['text']}")
    print(f"Source: {result['metadata']['file_name']}")
```

#### `quick_embed()`

Re-embed recently modified files.

```python
stats = quick_embed()
# Returns: {'MEMORY.md': 43, 'journal': 158, 'today_log': 12}
```

#### `memory_stats()`

Get database statistics.

```python
stats = memory_stats()
print(stats['total_chunks'])  # e.g., 847
print(stats['source_types'])   # {'memory': 42, 'journal': 156, ...}
```

---

## Wrapper Scripts

### embed-memory.sh

Simple wrapper for nightly embedding.

```bash
#!/bin/bash
cd /Users/clawdbot/clawd
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py embed
```

**Usage:**
```bash
./scripts/embed-memory.sh

# In crontab:
0 2 * * * /Users/clawdbot/clawd/scripts/embed-memory.sh >> ~/clawd/memory/embed.log 2>&1
```

### search-memory.sh

Simple wrapper for memory search.

```bash
#!/bin/bash
cd /Users/clawdbot/clawd
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/memory-search.py "$@"
```

**Usage:**
```bash
./scripts/search-memory.sh "Ross calorie goal"
./scripts/search-memory.sh --type journal "fitness"
```

---

## test-memory-system.sh

Comprehensive test suite.

### Usage

```bash
bash scripts/test-memory-system.sh

# Output:
# =========================================
# SEMANTIC MEMORY SYSTEM - TEST SUITE
# =========================================
# 
# Test 1: Verifying Python environment...
# Python 3.13.11
# ✓ Python available
# 
# Test 2: Checking dependencies...
# ✓ ChromaDB installed
# ✓ Sentence-transformers installed
# 
# Test 3: Embedding all memory sources...
# ✓ Embedded 42 chunks from MEMORY.md
# ...
# 
# Test 4: Checking database statistics...
# Total chunks: 847
# ...
# 
# Test 5: Running test searches...
# 
# Query 1: What's Ross's calorie goal?
# [Results shown]
# 
# Query 2: Ross's food preferences?
# [Results shown]
# 
# =========================================
# ALL TESTS COMPLETE!
# =========================================
```

### What It Tests

1. ✅ Python environment
2. ✅ Dependency installation
3. ✅ Embedding all sources
4. ✅ Database statistics
5. ✅ Multiple search scenarios
6. ✅ Memory helper functions

---

## Common Workflows

### Workflow 1: Initial Setup

```bash
# 1. Embed all sources
./scripts/embed-memory.sh

# 2. Verify it worked
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py stats

# 3. Test search
./scripts/search-memory.sh "Ross"

# 4. Run full test suite
bash scripts/test-memory-system.sh
```

### Workflow 2: Daily Maintenance

```bash
# Morning: Check what happened yesterday
./scripts/search-memory.sh --type daily_log "yesterday"

# After updating MEMORY.md manually
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/extract_and_update_memory.py --embed-only

# Evening: Let auto-extraction run
# (scheduled via cron or heartbeat)
```

### Workflow 3: Debugging

```bash
# Check database stats
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py stats

# Try different relevance thresholds
./scripts/search-memory.sh --min-relevance 0.3 "query"
./scripts/search-memory.sh --min-relevance 0.7 "query"
./scripts/search-memory.sh --min-relevance 0.9 "query"

# Re-embed everything
./scripts/embed-memory.sh

# Run tests
bash scripts/test-memory-system.sh
```

### Workflow 4: Cleanup

```bash
# Prune old embeddings (>30 days)
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py prune 30

# Check space saved
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py stats
```

---

## Tips & Tricks

### Tip 1: Multi-word queries don't need quotes in wrapper

```bash
# These are equivalent:
./scripts/search-memory.sh "Ross calorie goal"
./scripts/search-memory.sh Ross calorie goal
```

### Tip 2: Use grep to filter results

```bash
./scripts/search-memory.sh "fitness" | grep -A 5 "Relevance: 9"
# Shows only high-relevance (90%+) results
```

### Tip 3: Pipe to file for later review

```bash
./scripts/search-memory.sh "projects" > ~/Desktop/projects-memory.txt
```

### Tip 4: Batch searching

```bash
# Create a file with queries
cat > queries.txt << EOF
Ross calorie goal
food preferences
workout schedule
EOF

# Search each query
while read query; do
  echo "=== $query ==="
  ./scripts/search-memory.sh "$query" -n 1
done < queries.txt
```

### Tip 5: Quick stats check

```bash
# Add alias to .zshrc / .bashrc
alias memstats='/Users/clawdbot/clawd/memory/venv/bin/python3 /Users/clawdbot/clawd/scripts/semantic_memory.py stats'

# Then just run:
memstats
```

---

## Troubleshooting

### Error: "No module named 'chromadb'"

**Solution:** Use the venv Python:
```bash
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py stats
```

### Error: "spawn EBADF"

**Solution:** Run the Python script directly instead of via wrapper:
```bash
cd /Users/clawdbot/clawd
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py embed
```

### Error: "Collection not found"

**Solution:** Run initial embedding:
```bash
./scripts/embed-memory.sh
```

### Slow performance

**Solution:** Check chunk count and prune if needed:
```bash
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py stats
# If >10,000 chunks:
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py prune 30
```

---

## Environment Variables

```bash
# Optional: Set custom config path
export MEMORY_CONFIG="/path/to/custom/config.json"
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py stats
```

---

*Last updated: 2026-02-04*

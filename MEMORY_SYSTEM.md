# Semantic Memory System - Technical Documentation

**Production-ready vector search for Jarvis's long-term memory**

---

## Overview

The Semantic Memory System eliminates session amnesia by providing persistent, searchable memory across all conversations. It uses vector embeddings to enable semantic search - finding relevant information based on meaning, not just keywords.

### Key Features

- **Semantic Search:** Find information by meaning, not just keywords
- **Fast Retrieval:** <500ms search latency target
- **Auto-Embedding:** Automatically index new memory files
- **Multi-Source:** Searches across MEMORY.md, journal, daily logs, and conversations
- **Production Ready:** Robust error handling, persistent storage, zero external API costs

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Main Agent Loop                      │
│                                                         │
│  1. User message received                              │
│  2. check_memory_before_response(message)              │
│  3. Semantic search returns relevant context           │
│  4. Response generated with memory context             │
│  5. Conversation logged & auto-embedded                │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│              Semantic Memory System                     │
│                                                         │
│  ┌──────────────┐    ┌──────────────┐                 │
│  │   ChromaDB   │◄───┤ SentenceTrans│                 │
│  │  Vector DB   │    │    former    │                 │
│  └──────────────┘    └──────────────┘                 │
│         │                   │                           │
│         │                   │                           │
│  ┌──────▼───────────────────▼───────┐                 │
│  │      Embeddings Collection       │                 │
│  │  (cosine similarity search)      │                 │
│  └──────────────────────────────────┘                 │
└─────────────────────────────────────────────────────────┘
                          ▼
┌─────────────────────────────────────────────────────────┐
│                  Source Files                           │
│                                                         │
│  • MEMORY.md (curated facts)                           │
│  • jarvis-journal.md (session logs)                    │
│  • memory/2026-*.md (daily logs)                       │
│  • memory/conversations/* (chat history)               │
└─────────────────────────────────────────────────────────┘
```

---

## Components

### 1. Vector Database (ChromaDB)

- **Type:** Persistent local vector store
- **Location:** `~/clawd/memory/vector_db/`
- **Collection:** `jarvis_memory`
- **Distance Metric:** Cosine similarity
- **No external API calls** - fully local

### 2. Embedding Model

- **Model:** `sentence-transformers/all-MiniLM-L6-v2`
- **Dimensions:** 384
- **Speed:** ~100 sentences/second on M-series Mac
- **Quality:** Optimized for semantic similarity

### 3. Core Modules

#### `semantic_memory.py`
Main memory system with vector search capabilities.

**Key Methods:**
- `embed_file(file_path, source_type)` - Index a single file
- `embed_all_sources()` - Index all configured sources
- `search(query, n_results, source_type)` - Semantic search
- `check_memory_before_response(user_message)` - Pre-response context check
- `get_stats()` - Database statistics
- `prune_old_embeddings(days)` - Cleanup old data

#### `memory-search.py`
CLI tool for searching memory from command line.

**Usage:**
```bash
./scripts/search-memory.sh "what is Ross's calorie goal?"
./scripts/memory-search.py -n 5 --type journal "fitness goals"
```

**Options:**
- `-n, --num-results N` - Number of results (default: 5)
- `-t, --type TYPE` - Filter by source type (memory/journal/daily_log/conversation)
- `--min-relevance X` - Minimum relevance score (0-1, default: 0.5)
- `--stats` - Show database statistics
- `--embed` - Re-embed all sources before searching

#### `extract_and_update_memory.py`
Auto-extraction system for processing conversations.

**Functions:**
- Extract key facts from conversation text
- Update MEMORY.md with new learnings
- Log to daily files
- Auto-embed new content

**Usage:**
```bash
# Process conversation from file
./scripts/memory/venv/bin/python3 scripts/extract_and_update_memory.py -f conversation.txt

# Process from stdin
echo "Ross mentioned his calorie goal is 2200" | ./scripts/memory/venv/bin/python3 scripts/extract_and_update_memory.py

# Just re-embed recent changes
./scripts/memory/venv/bin/python3 scripts/extract_and_update_memory.py --embed-only
```

#### `memory_helper.py`
Integration helper for main agent loop.

**Key Functions:**
```python
from memory_helper import check_memory_before_response, search_memory

# Check for relevant context before responding
context = check_memory_before_response(user_message)
if context:
    print(context)  # Include in response

# Direct search
results = search_memory("Ross fitness goals", n_results=5)
```

---

## Configuration

**File:** `memory/memory_config.json`

```json
{
  "vector_db_path": "/Users/clawdbot/clawd/memory/vector_db",
  "conversations_path": "/Users/clawdbot/clawd/memory/conversations",
  "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
  "collection_name": "jarvis_memory",
  "chunk_size": 500,
  "chunk_overlap": 50,
  "max_search_results": 5,
  "search_timeout_ms": 500,
  "retention_days": 30,
  "auto_embed": true,
  "sources": {
    "memory_file": "/Users/clawdbot/clawd/MEMORY.md",
    "journal_file": "/Users/clawdbot/clawd/memory/jarvis-journal.md",
    "daily_logs_pattern": "/Users/clawdbot/clawd/memory/2026-*.md",
    "conversations_dir": "/Users/clawdbot/clawd/memory/conversations"
  }
}
```

### Configuration Options

- **chunk_size:** Maximum characters per text chunk (default: 500)
- **chunk_overlap:** Characters to overlap between chunks (default: 50)
- **max_search_results:** Default number of results to return (default: 5)
- **search_timeout_ms:** Target search latency in milliseconds (default: 500)
- **retention_days:** How long to keep embeddings before pruning (default: 30)

---

## Performance

### Benchmarks (M-series Mac)

| Operation | Target | Typical |
|-----------|--------|---------|
| Search latency | <500ms | ~150ms |
| Embedding 1 file | - | ~2-5s |
| Embedding all sources | - | ~30-60s |
| Database startup | <2s | ~1s |

### Optimization Tips

1. **Chunk Size:** Smaller chunks = more precise, but more storage
2. **Batch Embedding:** Process multiple files together
3. **Lazy Loading:** Model loads only when needed
4. **Pruning:** Run monthly to remove old embeddings

---

## Storage

### Disk Usage

- **Vector DB:** ~1-2 MB per 1000 chunks
- **Embedding Model:** ~90 MB (cached after first use)
- **Expected Total:** ~200-500 MB for typical usage

### Data Retention

- **Daily logs:** Embedded immediately, kept 30 days
- **MEMORY.md:** Always embedded, never pruned
- **Journal:** Always embedded, never pruned
- **Conversations:** Kept 7 days, then pruned

---

## Maintenance

### Daily Tasks (Automated)

1. **Nightly Embedding** (via cron)
   ```bash
   0 2 * * * /Users/clawdbot/clawd/scripts/embed-memory.sh >> /Users/clawdbot/clawd/memory/embed.log 2>&1
   ```

2. **Conversation Logging** (via heartbeat)
   - Log significant exchanges to daily files
   - Auto-embed at end of day

### Weekly Tasks

1. **Memory Review** (manual)
   - Review auto-extracted facts
   - Curate MEMORY.md
   - Remove redundancies

2. **Statistics Check**
   ```bash
   ./scripts/memory/venv/bin/python3 scripts/semantic_memory.py stats
   ```

### Monthly Tasks

1. **Prune Old Embeddings**
   ```bash
   ./scripts/memory/venv/bin/python3 scripts/semantic_memory.py prune 30
   ```

2. **Database Backup**
   ```bash
   cd ~/clawd
   tar -czf backups/vector_db_$(date +%Y%m%d).tar.gz memory/vector_db/
   ```

---

## Troubleshooting

### Problem: Search returns no results

**Solutions:**
1. Check if sources are embedded: `semantic_memory.py stats`
2. Re-embed sources: `semantic_memory.py embed`
3. Lower min_relevance threshold
4. Try broader search terms

### Problem: Slow search performance

**Solutions:**
1. Check chunk count (>10,000 chunks may slow down)
2. Prune old embeddings
3. Reduce max_search_results
4. Ensure SSD storage for vector_db

### Problem: Import errors

**Solutions:**
1. Verify venv is activated: `source memory/venv/bin/activate`
2. Reinstall dependencies: `pip install chromadb sentence-transformers`
3. Check Python version: Must be 3.11-3.13 (not 3.14+)

### Problem: Embedding fails

**Solutions:**
1. Check file permissions
2. Verify file encoding (must be UTF-8)
3. Check for empty files
4. Look for corrupted markdown

---

## Security

### Data Privacy

- **100% Local:** No data sent to external APIs
- **No Telemetry:** ChromaDB telemetry disabled
- **File Permissions:** Vector DB readable only by clawdbot user

### Access Control

- Memory files should remain in `~/clawd/` workspace
- Only load MEMORY.md in main session (not shared contexts)
- Don't embed sensitive credentials or tokens

---

## Extending the System

### Adding New Source Types

1. **Update config:** Add source pattern to `memory_config.json`
2. **Embed sources:** Run `semantic_memory.py embed`
3. **Test search:** Use `--type` filter to query new source

### Custom Embedding Models

Edit `memory_config.json`:
```json
{
  "embedding_model": "sentence-transformers/all-mpnet-base-v2"
}
```

Better models (slower but more accurate):
- `all-mpnet-base-v2` (768 dims, higher quality)
- `multi-qa-mpnet-base-dot-v1` (optimized for Q&A)

### Integration with Other Tools

```python
# Example: Search before email draft
from memory_helper import search_memory

results = search_memory("Ross email preferences")
if results:
    # Use context to personalize email
    pass
```

---

## Version History

- **v1.0.0** (2026-02-04) - Initial production release
  - ChromaDB vector search
  - Auto-embedding pipeline
  - CLI tools
  - Integration helpers

---

## Support & Feedback

For issues or questions:
1. Check troubleshooting section above
2. Review logs: `memory/embed.log`
3. Run test suite: `scripts/test-memory-system.sh`
4. Ask Ross for manual debugging

---

*Last updated: 2026-02-04*

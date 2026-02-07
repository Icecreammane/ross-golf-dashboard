# Semantic Memory - Quick Reference Cheat Sheet

**One-page reference for common operations**

---

## 🚀 Quick Start (First Time)

```bash
cd ~/clawd

# 1. Verify installation
bash scripts/verify-installation.sh

# 2. Run full test suite
bash scripts/test-memory-system.sh

# 3. You're ready!
```

---

## 🔍 Search Memory

### Basic Search
```bash
./scripts/search-memory.sh "Ross calorie goal"
```

### Filter by Source
```bash
./scripts/search-memory.sh --type memory "preferences"
./scripts/search-memory.sh --type journal "fitness"
./scripts/search-memory.sh --type daily_log "yesterday"
```

### Adjust Results
```bash
# More results
./scripts/search-memory.sh -n 10 "Ross"

# Only high confidence
./scripts/search-memory.sh --min-relevance 0.8 "goals"

# Lower threshold for exploration
./scripts/search-memory.sh --min-relevance 0.3 "projects"
```

---

## 📝 Update Memory

### After Editing Files
```bash
# Re-embed everything
./scripts/embed-memory.sh
```

### Check What's Embedded
```bash
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py stats
```

---

## 🧹 Maintenance

### Prune Old Data
```bash
# Remove embeddings >30 days old
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py prune 30
```

### Reset Everything (CAREFUL!)
```bash
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py reset
# Then re-embed:
./scripts/embed-memory.sh
```

---

## 🔗 Python Integration

### Import in Script
```python
import sys
sys.path.insert(0, '/Users/clawdbot/clawd/scripts')
from memory_helper import check_memory_before_response, search_memory
```

### Check Memory Before Response
```python
context = check_memory_before_response("What's my calorie goal?")
if context:
    print(context)  # Use in response
```

### Direct Search
```python
results = search_memory("food preferences", n_results=5)
for result in results:
    print(f"{result['relevance']:.0%}: {result['text'][:100]}...")
```

### Quick Re-embed
```python
from memory_helper import quick_embed
quick_embed()  # Re-embed recent changes
```

---

## ⏰ Automation

### Nightly Cron Job
```bash
# Add to crontab (crontab -e)
0 2 * * * /Users/clawdbot/clawd/scripts/embed-memory.sh >> ~/clawd/memory/embed.log 2>&1
```

### Heartbeat Check
```python
# In heartbeat function
from memory_helper import quick_embed
import os
from datetime import datetime, timedelta

memory_file = "/Users/clawdbot/clawd/MEMORY.md"
if os.path.exists(memory_file):
    mtime = datetime.fromtimestamp(os.path.getmtime(memory_file))
    if datetime.now() - mtime < timedelta(hours=1):
        quick_embed()
```

---

## 🧪 Testing

### Run All Tests
```bash
bash scripts/test-memory-system.sh
```

### Test Specific Queries
```bash
./scripts/search-memory.sh "calorie goal"      # Should find 2,200
./scripts/search-memory.sh "food preferences"  # Should find Publix
./scripts/search-memory.sh "what did we build" # Recent projects
```

---

## 📊 Database Stats

```bash
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py stats

# Output:
# Total chunks: 847
# Collection: jarvis_memory
# Source breakdown:
#   memory: 42
#   journal: 156
#   daily_log: 649
```

---

## 🛠 Troubleshooting

### No Results Found
```bash
# 1. Check if sources are embedded
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py stats

# 2. Re-embed if needed
./scripts/embed-memory.sh

# 3. Try lower relevance threshold
./scripts/search-memory.sh --min-relevance 0.3 "query"
```

### Slow Performance
```bash
# Check chunk count
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py stats

# If >10,000 chunks, prune
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py prune 30
```

### Import Errors
```bash
# Always use venv Python
/Users/clawdbot/clawd/memory/venv/bin/python3 your_script.py
```

---

## 📚 Documentation

- **Quick Start:** `memory/README.md`
- **Technical:** `MEMORY_SYSTEM.md`
- **Integration:** `INTEGRATION_GUIDE.md`
- **CLI Reference:** `CLI_REFERENCE.md`
- **Summary:** `MEMORY_SYSTEM_SUMMARY.md`
- **This Cheat Sheet:** `MEMORY_CHEATSHEET.md`

---

## 💡 Common Use Cases

### "What did I tell you about X?"
```bash
./scripts/search-memory.sh "X"
```

### "What did we do yesterday?"
```bash
./scripts/search-memory.sh --type daily_log "yesterday"
```

### "What are my preferences for Y?"
```bash
./scripts/search-memory.sh "Y preferences"
```

### "When did we discuss Z?"
```bash
./scripts/search-memory.sh "Z" | grep "Modified:"
```

---

## ⚡ Quick Commands

```bash
# Search
./scripts/search-memory.sh "query"

# Embed
./scripts/embed-memory.sh

# Stats
/Users/clawdbot/clawd/memory/venv/bin/python3 scripts/semantic_memory.py stats

# Test
bash scripts/test-memory-system.sh

# Verify
bash scripts/verify-installation.sh
```

---

## 🎯 Performance Targets

| Metric | Target | Typical |
|--------|--------|---------|
| Search | <500ms | ~150ms |
| Embed file | - | 2-5s |
| Startup | <2s | ~1s |

---

## 📦 File Locations

```
~/clawd/
├── scripts/
│   ├── search-memory.sh         ← Quick search
│   ├── embed-memory.sh          ← Re-embed
│   └── test-memory-system.sh    ← Test suite
├── memory/
│   ├── memory_config.json       ← Config
│   └── vector_db/               ← Database
└── MEMORY_CHEATSHEET.md         ← This file
```

---

## 🔑 Key Files to Update

When you update these, re-embed:

1. **MEMORY.md** - Curated facts
2. **memory/jarvis-journal.md** - Session logs
3. **memory/2026-*.md** - Daily logs

Then run:
```bash
./scripts/embed-memory.sh
```

---

**Print this page and keep it handy! 📄**

*Last updated: 2026-02-04*

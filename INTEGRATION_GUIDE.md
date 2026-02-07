# Semantic Memory Integration Guide

**How to integrate the semantic memory system into the main Jarvis agent**

---

## Quick Start

### 1. One-Time Setup

```bash
# Run the initial embedding
cd ~/clawd
./scripts/embed-memory.sh

# Verify it works
./scripts/test-memory-system.sh
```

### 2. Integration Pattern

Add this to your agent's main response loop:

```python
import sys
sys.path.insert(0, '/Users/clawdbot/clawd/scripts')
from memory_helper import check_memory_before_response, search_memory

def handle_user_message(user_message: str):
    """Main message handler with memory integration."""
    
    # STEP 1: Check memory for relevant context
    memory_context = check_memory_before_response(user_message)
    
    # STEP 2: If relevant memories found, include in prompt/context
    if memory_context:
        # Option A: Include in your prompt to LLM
        enhanced_prompt = f"{memory_context}\n\nUser: {user_message}"
        
        # Option B: Mention in response
        print(f"💡 I recall: {memory_context}")
    
    # STEP 3: Generate response as normal
    response = generate_response(user_message)
    
    # STEP 4: Log interaction for future embedding
    log_conversation(user_message, response)
    
    return response
```

---

## Integration Points

### 1. Session Startup (Every Session)

**When:** Agent starts new session

**Action:** Pre-load memory for fast access

```python
def session_startup():
    """Initialize memory at session start."""
    import sys
    sys.path.insert(0, '/Users/clawdbot/clawd/scripts')
    
    # Pre-load memory instance (lazy loads model)
    from memory_helper import get_memory
    memory = get_memory()
    
    print("✓ Semantic memory ready")
```

### 2. Before Each Response (Real-time)

**When:** User sends a message

**Action:** Check for relevant context

```python
def before_response(user_message: str):
    """Check memory before generating response."""
    from memory_helper import check_memory_before_response
    
    context = check_memory_before_response(user_message, min_relevance=0.7)
    
    if context:
        # We have relevant memories!
        return context
    else:
        # No strong matches
        return None
```

**Performance:** ~150ms typical latency (well under 500ms target)

### 3. After Each Conversation (Logging)

**When:** After each exchange or at end of session

**Action:** Log conversation for embedding

```python
def after_conversation(user_msg: str, assistant_msg: str):
    """Log conversation to daily file."""
    from datetime import datetime
    from pathlib import Path
    
    # Log to today's file
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = Path(f"/Users/clawdbot/clawd/memory/{today}.md")
    
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"\n### {timestamp}\n**User:** {user_msg}\n**Jarvis:** {assistant_msg}\n"
    
    with open(log_path, 'a') as f:
        f.write(entry)
```

### 4. Heartbeat Check (Periodic)

**When:** During heartbeat polls (~30 minutes)

**Action:** Re-embed recent changes

```python
def heartbeat_memory_update():
    """Periodically re-embed recent changes."""
    from memory_helper import quick_embed
    
    # Check if MEMORY.md or journal were modified recently
    import os
    from datetime import datetime, timedelta
    
    memory_file = "/Users/clawdbot/clawd/MEMORY.md"
    if os.path.exists(memory_file):
        mtime = datetime.fromtimestamp(os.path.getmtime(memory_file))
        if datetime.now() - mtime < timedelta(hours=1):
            # File was modified recently, re-embed
            quick_embed()
            print("✓ Memory embeddings updated")
```

### 5. Nightly Maintenance (Cron)

**When:** 2:00 AM daily

**Action:** Full re-embedding of all sources

**Setup:**
```bash
# Add to crontab (crontab -e)
0 2 * * * /Users/clawdbot/clawd/scripts/embed-memory.sh >> /Users/clawdbot/clawd/memory/embed.log 2>&1
```

Or use Clawdbot cron:
```bash
clawdbot cron add "0 2 * * *" "bash /Users/clawdbot/clawd/scripts/embed-memory.sh" --label "nightly-memory-embed"
```

---

## Usage Patterns

### Pattern 1: Fact Lookup

**Use Case:** User asks about something you should know

```python
# User: "What's my calorie goal?"

context = check_memory_before_response("calorie goal")
# Returns: "Ross's daily calorie goal is 2,200"

# Use context to answer directly without guessing
```

### Pattern 2: Conversation History

**Use Case:** "What did we talk about yesterday?"

```python
results = search_memory("yesterday discussion", source_type="daily_log")

# Format results
for result in results[:3]:
    print(f"• {result['text'][:200]}...")
```

### Pattern 3: Preference Recall

**Use Case:** Making a suggestion

```python
# Before suggesting food
food_prefs = search_memory("Ross food preferences")

# Check if relevant
if food_prefs and food_prefs[0]['relevance'] > 0.8:
    # Use preferences in suggestion
    pass
```

### Pattern 4: Learning Detection

**Use Case:** User teaches you something new

```python
# User: "I prefer dark mode for all dashboards"

# Option A: Immediately log to MEMORY.md
update_memory("UI Preferences", "Ross prefers dark mode for all dashboards")

# Option B: Log to daily file for later review
log_to_daily("Preference learned: Dark mode for dashboards")

# Option C: Use auto-extraction (run nightly)
# System automatically extracts and categorizes
```

---

## Code Examples

### Example 1: Basic Integration

```python
#!/usr/bin/env python3
"""Simple agent with memory integration."""

import sys
sys.path.insert(0, '/Users/clawdbot/clawd/scripts')

from memory_helper import check_memory_before_response, search_memory


def chat_loop():
    """Simple chat loop with memory."""
    print("Jarvis with Memory - Type 'quit' to exit")
    
    while True:
        user_input = input("\nYou: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            break
        
        # Check memory
        context = check_memory_before_response(user_input)
        
        # Simple response
        if context:
            print(f"\n💡 From memory:\n{context}")
        else:
            print("\n🤔 No relevant memories found")
        
        # You would generate actual response here
        # response = your_llm_call(user_input, context)


if __name__ == '__main__':
    chat_loop()
```

### Example 2: Advanced Integration with LLM

```python
def generate_response_with_memory(user_message: str, llm_function):
    """Generate response with memory context."""
    from memory_helper import check_memory_before_response
    
    # Get memory context
    memory_context = check_memory_before_response(user_message, min_relevance=0.7)
    
    # Build enhanced prompt
    if memory_context:
        prompt = f"""You are Jarvis, Ross's AI assistant.

RELEVANT MEMORIES:
{memory_context}

USER MESSAGE:
{user_message}

Respond naturally, incorporating relevant information from your memories.
Don't explicitly say "from my memory" - just know it.
"""
    else:
        prompt = f"""You are Jarvis, Ross's AI assistant.

USER MESSAGE:
{user_message}

Respond naturally based on your general knowledge of Ross.
"""
    
    # Call LLM
    response = llm_function(prompt)
    
    return response
```

### Example 3: Heartbeat Integration

```python
def heartbeat_with_memory():
    """Heartbeat check with memory maintenance."""
    from datetime import datetime
    import os
    from memory_helper import quick_embed
    
    # Read HEARTBEAT.md if exists
    # ... your normal heartbeat logic ...
    
    # Check if we should re-embed
    last_embed_file = "/Users/clawdbot/clawd/memory/.last_embed"
    
    should_embed = False
    if os.path.exists(last_embed_file):
        with open(last_embed_file, 'r') as f:
            last_embed = datetime.fromisoformat(f.read().strip())
        
        # Re-embed if it's been >2 hours
        if (datetime.now() - last_embed).seconds > 7200:
            should_embed = True
    else:
        should_embed = True
    
    if should_embed:
        print("🧠 Updating memory embeddings...")
        quick_embed()
        
        # Update timestamp
        with open(last_embed_file, 'w') as f:
            f.write(datetime.now().isoformat())
    
    # Continue with normal heartbeat
    return "HEARTBEAT_OK"
```

---

## Testing Integration

### Test 1: Basic Search

```python
from memory_helper import search_memory

results = search_memory("Ross calorie goal")
assert len(results) > 0
assert "2200" in results[0]['text'] or "2,200" in results[0]['text']
print("✓ Can find calorie goal")
```

### Test 2: Context Check

```python
from memory_helper import check_memory_before_response

context = check_memory_before_response("What's my calorie goal?")
assert context is not None
assert "2200" in context or "2,200" in context
print("✓ Context check working")
```

### Test 3: Performance

```python
import time
from memory_helper import search_memory

start = time.time()
results = search_memory("test query")
elapsed_ms = (time.time() - start) * 1000

assert elapsed_ms < 500, f"Search took {elapsed_ms}ms (target: <500ms)"
print(f"✓ Search performance: {elapsed_ms:.0f}ms")
```

---

## Workflow Examples

### Workflow 1: Morning Greeting

```python
def morning_greeting():
    """Generate personalized morning greeting."""
    from memory_helper import search_memory
    from datetime import datetime
    
    # Check yesterday's activities
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    recent_context = search_memory(f"activity on {yesterday}", source_type="daily_log", n_results=3)
    
    greeting = "Good morning, Ross! "
    
    if recent_context:
        # Reference yesterday's events
        greeting += "Picking up where we left off yesterday... "
    
    return greeting
```

### Workflow 2: Smart Suggestions

```python
def suggest_meal():
    """Suggest meal based on preferences."""
    from memory_helper import search_memory
    
    # Get food preferences
    prefs = search_memory("Ross food preferences", n_results=5)
    
    # Extract likes
    likes = []
    for result in prefs:
        if result['relevance'] > 0.7:
            likes.append(result['text'])
    
    # Generate suggestion based on actual preferences
    if "Publix" in str(likes):
        return "How about a Publix Boar's Head Deluxe sub? I know you love those."
    else:
        return "What sounds good for lunch?"
```

### Workflow 3: Progress Tracking

```python
def check_progress(area: str):
    """Check progress in a specific area."""
    from memory_helper import search_memory
    from datetime import datetime, timedelta
    
    # Search recent logs
    results = search_memory(f"{area} progress", source_type="daily_log", n_results=10)
    
    # Group by date
    progress_by_date = {}
    for result in results:
        date = result['metadata'].get('modified_time', '')[:10]
        if date:
            if date not in progress_by_date:
                progress_by_date[date] = []
            progress_by_date[date].append(result['text'])
    
    return progress_by_date
```

---

## Best Practices

### DO ✅

1. **Check memory before answering factual questions**
   - Prevents guessing when you should know
   - Reduces "I don't recall" moments

2. **Log significant interactions**
   - New preferences
   - Goals stated
   - Decisions made
   - Lessons learned

3. **Re-embed after updating MEMORY.md**
   - Use `quick_embed()` after manual edits
   - Keeps search index fresh

4. **Use appropriate relevance thresholds**
   - 0.8+ for high-confidence facts
   - 0.7+ for general context
   - 0.5+ for exploratory searches

5. **Filter by source type when appropriate**
   - `source_type="memory"` for curated facts
   - `source_type="daily_log"` for recent events
   - `source_type="journal"` for behavioral insights

### DON'T ❌

1. **Don't over-rely on memory for everything**
   - Use for facts, preferences, history
   - Don't use for real-time data (weather, stocks, etc.)

2. **Don't skip the initial embedding**
   - System won't work without embeddings
   - Run `embed-memory.sh` first!

3. **Don't ignore relevance scores**
   - Low relevance = weak match
   - Always check before using results

4. **Don't embed sensitive data**
   - No passwords, tokens, API keys
   - Keep security-sensitive info separate

5. **Don't modify vector_db directly**
   - Always use provided functions
   - Direct DB edits can corrupt index

---

## Troubleshooting Integration

### Issue: "No module named 'chromadb'"

**Solution:**
```python
# Make sure to use the venv Python
import subprocess
subprocess.run([
    '/Users/clawdbot/clawd/memory/venv/bin/python3',
    'scripts/semantic_memory.py',
    'stats'
])
```

### Issue: Search returns irrelevant results

**Solution:**
1. Check embedding quality - re-run `embed-memory.sh`
2. Increase `min_relevance` threshold
3. Try more specific search terms
4. Filter by `source_type`

### Issue: Slow performance

**Solution:**
1. Check chunk count: `semantic_memory.py stats`
2. If >10,000 chunks, prune old data
3. Ensure memory model is cached (first search is slower)

---

## Next Steps

1. **Run the test suite**
   ```bash
   bash scripts/test-memory-system.sh
   ```

2. **Test manual search**
   ```bash
   ./scripts/search-memory.sh "Ross calorie goal"
   ```

3. **Integrate into main agent**
   - Add `check_memory_before_response()` to message handler
   - Test with a few example queries

4. **Set up automation**
   - Add nightly embedding cron job
   - Add heartbeat re-embedding check

5. **Monitor and iterate**
   - Watch for missed recalls
   - Adjust relevance thresholds
   - Refine auto-extraction rules

---

## Support

Questions? Check:
1. `MEMORY_SYSTEM.md` - Full technical docs
2. `CLI_REFERENCE.md` - Command-line tools
3. Test scripts in `scripts/test-memory-system.sh`

---

*Last updated: 2026-02-04*

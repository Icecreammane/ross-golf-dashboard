# Memory Protocol - Automatic Context Loading

## How It Works

### Before Every Response (Automatic)
1. **Instant Recall Search** - Semantic search across all memory files
2. **Load Recent Logs** - Yesterday + today's memory files
3. **Project Detection** - Identify mentioned projects (FitTrack, golf, etc.)
4. **Surface Context** - Top 3 relevant memories presented automatically

### After Every Response (Automatic)
1. **Extract Key Details** - Decisions, features, preferences, goals
2. **Real-Time Logging** - Immediate append to memory/YYYY-MM-DD.md
3. **Update Index** - Refresh semantic search index
4. **Thread Tracking** - Link related conversations across time

## Usage

### Standalone Testing
```bash
# Test pre-query (before responding)
python3 ~/clawd/scripts/auto_memory.py pre "How's the FitTrack voice logging?"

# Test post-logging (after responding)
python3 ~/clawd/scripts/auto_memory.py post '{"type": "Feature", "content": "Built voice logging"}'
```

### Integration with Jarvis
```bash
# Process message with automatic memory
python3 ~/clawd/scripts/memory_wrapper.py "What did we build yesterday?"
```

## What Gets Logged Automatically
- ✅ Feature builds and completions
- ✅ Decisions made
- ✅ Preferences stated
- ✅ Goals discussed
- ✅ Problems identified
- ✅ Solutions implemented

## Files
- `scripts/auto_memory.py` - Core memory system
- `scripts/memory_wrapper.py` - Message interceptor
- `memory/auto_memory_state.json` - Conversation thread tracking

## State Tracking
The system maintains conversation threads:
```json
{
  "last_recall_query": "What did we build?",
  "last_log_time": "2026-02-13T08:11:00",
  "conversation_thread": [
    {
      "message": "Build voice logging",
      "timestamp": "2026-02-13T07:54:00",
      "context_found": 5
    }
  ]
}
```

## Benefits
1. **No more rehashing** - Automatically surfaces relevant past work
2. **Real-time memory** - Logs as we go, not at end of session
3. **Context awareness** - Knows what we've discussed before
4. **Thread continuity** - Connects related conversations across days

## Next Steps
- Integrate into Clawdbot gateway as pre-processing hook
- Add confidence scoring for memory relevance
- Build conversation summarization for long threads

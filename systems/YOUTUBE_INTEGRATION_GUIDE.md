# YouTube Integration Guide for Jarvis

## Quick Integration

Add this to your imports when you need YouTube functionality:

```python
import sys
sys.path.append('/Users/clawdbot/clawd/systems')
from youtube_integration import (
    quick_fetch,
    summarize_youtube,
    implement_from_youtube,
    detect_youtube_url
)
```

## Natural Language Triggers

### When Ross says: "Watch this video: [URL]"

```python
# Detect if message contains YouTube URL
urls = detect_youtube_url(message)

if urls:
    url = urls[0]  # Take first URL
    result = quick_fetch(url)
    
    if result['success']:
        # Pass transcript to AI for processing
        transcript = result['transcript']
        # Then ask AI to summarize or process it
        response = f"I've read the transcript ({result['duration_minutes']} min video). "
        # ... continue with AI analysis
    else:
        response = f"I couldn't fetch the transcript: {result['error']}"
```

### When Ross says: "Summarize this: [URL]"

```python
result = summarize_youtube(url)

if result['success']:
    # Use result['summary_prompt'] directly with AI
    # The prompt is pre-formatted with metadata and instructions
    summary = ask_ai(result['summary_prompt'])
    response = summary
else:
    response = f"Error: {result['error']}"
```

### When Ross says: "Implement [feature] from [URL]"

```python
# Extract feature name from message (e.g., "authentication", "JWT system", etc.)
feature_name = extract_feature_name(message)

result = implement_from_youtube(url, feature_name)

if result['success']:
    # Use result['implementation_prompt'] with AI
    implementation = ask_ai(result['implementation_prompt'])
    response = implementation
else:
    response = f"Error: {result['error']}"
```

## Command Line Quick Reference

```bash
# Quick transcript fetch
~/clawd/scripts/youtube-transcript.sh "https://www.youtube.com/watch?v=VIDEO_ID"

# Or directly with Python
python3 ~/clawd/systems/youtube-reader.py "VIDEO_URL"

# Integration helpers
python3 ~/clawd/systems/youtube-integration.py summarize "VIDEO_URL"
python3 ~/clawd/systems/youtube-integration.py implement "VIDEO_URL" "feature_name"
python3 ~/clawd/systems/youtube-integration.py detect "text with URLs"
```

## Auto-Detection in Messages

```python
# Check every message for YouTube URLs
urls = detect_youtube_url(message_text)

if urls:
    # Offer to process them
    response = f"I found {len(urls)} YouTube video(s). Would you like me to summarize them?"
    # Or just auto-process if it's a clear request
```

## Example Workflows

### Workflow 1: Summarize on Demand
```python
# Ross: "Summarize https://www.youtube.com/watch?v=VIDEO_ID"

result = summarize_youtube(url)
if result['success']:
    summary = ask_ai(result['summary_prompt'])
    send_message(f"**Video Summary ({result['duration_minutes']} min):**\n\n{summary}")
```

### Workflow 2: Extract Implementation
```python
# Ross: "Watch this tutorial and implement the authentication system"

result = implement_from_youtube(url, "authentication system")
if result['success']:
    implementation = ask_ai(result['implementation_prompt'])
    send_message(f"**Implementation Guide:**\n\n{implementation}")
```

### Workflow 3: Multi-Video Processing
```python
# Ross: "Compare these three videos: [URL1] [URL2] [URL3]"

urls = detect_youtube_url(message)
transcripts = []

for url in urls:
    result = quick_fetch(url)
    if result['success']:
        transcripts.append({
            'url': url,
            'transcript': result['transcript'],
            'duration': result['duration_minutes']
        })

# Now compare them with AI
comparison = ask_ai(f"Compare these video transcripts: {transcripts}")
```

## Error Handling

Always check `result['success']` before processing:

```python
result = quick_fetch(url)

if not result['success']:
    # Handle specific errors
    error = result['error']
    
    if "disabled" in error.lower():
        response = "This video doesn't have captions available."
    elif "unavailable" in error.lower():
        response = "This video is private or no longer available."
    else:
        response = f"I couldn't fetch the transcript: {error}"
```

## Performance Tips

1. **Use caching**: The system automatically caches for 24 hours
2. **Use `quick_fetch()`** for simple needs (no timestamps)
3. **Use `summarize_youtube()`** when you need AI-ready prompts
4. **Batch process**: Check for multiple URLs at once with `detect_youtube_url()`

## Integration Checklist

- [x] Import functions are available
- [x] YouTube URLs are auto-detected in messages
- [x] Error handling is graceful
- [x] Cache is working (~/clawd/cache/youtube-transcripts/)
- [x] Documentation is accessible

## Files Reference

- **Core:** `~/clawd/systems/youtube-reader.py`
- **Integration:** `~/clawd/systems/youtube-integration.py`
- **CLI:** `~/clawd/scripts/youtube-transcript.sh`
- **Docs:** `~/clawd/systems/YOUTUBE_READER.md`
- **Cache:** `~/clawd/cache/youtube-transcripts/`

---

**Built:** 2026-01-30  
**Status:** Ready for integration into main Jarvis system

# YouTube Transcript Reader

## Overview

Jarvis can now read YouTube video transcripts/captions! This enables workflows like:
- "Watch this video and summarize it"
- "Watch this tutorial and implement the feature"
- "Extract code examples from this YouTube video"

## Quick Start

### From Python (Recommended for Jarvis)

```python
import sys
sys.path.append('/Users/clawdbot/clawd/systems')
from youtube_integration import quick_fetch, summarize_youtube, implement_from_youtube

# Quick fetch (no timestamps)
result = quick_fetch("https://www.youtube.com/watch?v=VIDEO_ID")
if result['success']:
    print(result['transcript'])
else:
    print(f"Error: {result['error']}")

# Get transcript ready for summarization
result = summarize_youtube("https://www.youtube.com/watch?v=VIDEO_ID")
# Use result['summary_prompt'] with AI

# Get transcript ready for implementation extraction
result = implement_from_youtube("https://www.youtube.com/watch?v=VIDEO_ID", "authentication system")
# Use result['implementation_prompt'] with AI
```

### From Command Line

```bash
# Quick transcript fetch
~/clawd/scripts/youtube-transcript.sh "https://www.youtube.com/watch?v=VIDEO_ID"

# Summarization helper
python3 ~/clawd/systems/youtube-integration.py summarize "https://www.youtube.com/watch?v=VIDEO_ID"

# Implementation extraction helper
python3 ~/clawd/systems/youtube-integration.py implement "https://www.youtube.com/watch?v=VIDEO_ID" "feature name"

# Auto-detect YouTube URLs in text
python3 ~/clawd/systems/youtube-integration.py detect "Check out https://youtu.be/VIDEO_ID"
```

## URL Formats Supported

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/live/VIDEO_ID` (livestreams with captions)
- `https://www.youtube.com/embed/VIDEO_ID`
- Direct video ID: `VIDEO_ID`

## Features

### ✓ Caching
- Transcripts are cached for 24 hours
- Cache location: `~/clawd/cache/youtube-transcripts/`
- Significantly speeds up repeated requests

### ✓ Timestamps (Optional)
- Include timestamps with `include_timestamps=True`
- Format: `[HH:MM:SS] transcript text`
- Useful for referencing specific moments

### ✓ Error Handling
- Graceful failures for missing captions
- Clear error messages
- Works with try/except for automated workflows

### ✓ Fast
- Typical fetch: <2 seconds
- Cached fetch: <0.1 seconds

## Example Workflows

### Workflow 1: Summarize a Video

```python
from youtube_integration import summarize_youtube

result = summarize_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
if result['success']:
    # Pass result['summary_prompt'] to your AI model
    print(f"Video: {result['video_id']} ({result['duration_minutes']} min)")
    # Then use the transcript for summarization
```

### Workflow 2: Implement from Tutorial

```python
from youtube_integration import implement_from_youtube

result = implement_from_youtube(
    "https://www.youtube.com/watch?v=VIDEO_ID",
    "JWT authentication"
)
if result['success']:
    # Use result['implementation_prompt'] with AI to extract implementation details
    print(result['implementation_prompt'])
```

### Workflow 3: Auto-Process YouTube Links in Messages

```python
from youtube_integration import detect_youtube_url, quick_fetch

message = "Check out this tutorial: https://youtu.be/VIDEO_ID"
urls = detect_youtube_url(message)

for url in urls:
    result = quick_fetch(url)
    if result['success']:
        print(f"Found transcript: {len(result['transcript'])} chars")
```

## Limitations

### ❌ No Captions = No Transcript
If a video doesn't have captions/subtitles (auto-generated or manual), we can't fetch a transcript. This is a YouTube API limitation, not a bug.

### ❌ Private/Unavailable Videos
Can't access transcripts from private, deleted, or region-restricted videos.

### ❌ Live Streams
Live streams only work if:
1. The stream has ended (archived)
2. Captions were enabled during the stream

### ⚠️ Rate Limiting
YouTube may rate-limit excessive requests. The caching system helps avoid this.

## Troubleshooting

### "No transcript found"
- Check if the video has captions (CC button on YouTube)
- Try a different video
- Some videos only have auto-generated captions in certain languages

### "Video unavailable"
- Video may be private, deleted, or region-restricted
- Check if the URL is correct

### "Too many requests"
- Wait a few minutes and try again
- Check cache directory for existing transcripts

### Cache Issues
```bash
# Clear cache if needed
rm -rf ~/clawd/cache/youtube-transcripts/*.json
```

## Testing

The system was tested with:
- ✓ Regular videos with captions
- ✓ Livestream archives (https://www.youtube.com/live/UpM2H83MJO8)
- ✓ Various URL formats
- ✓ Videos without captions (graceful failure)
- ✓ Caching (repeated requests)

## For Jarvis: Natural Language Integration

When Ross says:
- **"Watch this video: [URL]"** → Use `quick_fetch()` to get transcript, then summarize
- **"Summarize this: [URL]"** → Use `summarize_youtube()` to get structured prompt
- **"Implement [feature] from [URL]"** → Use `implement_from_youtube()` with feature name
- **"What's in this video?"** → Fetch transcript and extract key topics

Auto-detect YouTube URLs in messages and offer to fetch transcripts!

## Technical Notes

- Library: `youtube-transcript-api` (MIT License)
- Cache format: JSON with ISO timestamps
- Cache expiry: 24 hours
- Video ID extraction: Regex-based, supports all common formats
- Error handling: Try/except with specific error types

## Files

- `~/clawd/systems/youtube-reader.py` - Core module
- `~/clawd/systems/youtube-integration.py` - High-level integration functions
- `~/clawd/scripts/youtube-transcript.sh` - CLI tool
- `~/clawd/cache/youtube-transcripts/` - Cache directory
- `~/clawd/systems/YOUTUBE_READER.md` - This documentation

---

**Built:** 2026-01-30  
**Status:** Production ready ✓

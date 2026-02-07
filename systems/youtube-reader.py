#!/usr/bin/env python3
"""
YouTube Transcript Reader
Fetches transcripts/captions from YouTube videos for Jarvis.
"""

import re
import json
import time
from pathlib import Path
from datetime import datetime, timedelta
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import (
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable
)

# TooManyRequests may not be available in all versions
try:
    from youtube_transcript_api._errors import TooManyRequests
except ImportError:
    TooManyRequests = None

# Cache directory
CACHE_DIR = Path.home() / "clawd" / "cache" / "youtube-transcripts"
CACHE_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DURATION = timedelta(hours=24)


def extract_video_id(url):
    """
    Extract video ID from various YouTube URL formats.
    Supports:
    - https://www.youtube.com/watch?v=VIDEO_ID
    - https://youtu.be/VIDEO_ID
    - https://www.youtube.com/live/VIDEO_ID
    - https://www.youtube.com/embed/VIDEO_ID
    """
    patterns = [
        r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/live\/|youtube\.com\/embed\/)([a-zA-Z0-9_-]{11})',
        r'youtube\.com\/watch\?.*v=([a-zA-Z0-9_-]{11})',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    # If no match, assume the input itself might be a video ID
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
        return url
    
    return None


def get_cache_path(video_id):
    """Get cache file path for a video ID."""
    return CACHE_DIR / f"{video_id}.json"


def load_from_cache(video_id):
    """Load transcript from cache if it exists and is fresh."""
    cache_path = get_cache_path(video_id)
    
    if not cache_path.exists():
        return None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check if cache is still fresh
        cached_time = datetime.fromisoformat(data.get('cached_at', '2000-01-01'))
        if datetime.now() - cached_time < CACHE_DURATION:
            return data
        else:
            # Cache expired
            cache_path.unlink()
            return None
    except Exception:
        # Corrupted cache, remove it
        cache_path.unlink(missing_ok=True)
        return None


def save_to_cache(video_id, data):
    """Save transcript data to cache."""
    cache_path = get_cache_path(video_id)
    data['cached_at'] = datetime.now().isoformat()
    
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Warning: Failed to cache transcript: {e}")


def get_youtube_transcript(url, include_timestamps=False):
    """
    Fetch transcript from a YouTube video.
    
    Args:
        url: YouTube URL or video ID
        include_timestamps: If True, include timestamp info in transcript
    
    Returns:
        dict: {
            "success": bool,
            "transcript": str,
            "title": str,
            "duration": int,  # in seconds
            "video_id": str,
            "error": str  # only present if success=False
        }
    """
    # Extract video ID
    video_id = extract_video_id(url)
    if not video_id:
        return {
            "success": False,
            "error": "Invalid YouTube URL or video ID",
            "transcript": "",
            "title": "",
            "duration": 0,
            "video_id": ""
        }
    
    # Check cache first
    cached = load_from_cache(video_id)
    if cached:
        return cached
    
    try:
        # Fetch transcript using the API
        api = YouTubeTranscriptApi()
        fetched = api.fetch(video_id)
        snippets = fetched.snippets
        
        # Build full transcript text
        if include_timestamps:
            transcript_parts = []
            for snippet in snippets:
                timestamp = time.strftime('%H:%M:%S', time.gmtime(snippet.start))
                transcript_parts.append(f"[{timestamp}] {snippet.text}")
            transcript_text = "\n".join(transcript_parts)
        else:
            transcript_text = " ".join([snippet.text for snippet in snippets])
        
        # Calculate duration (last entry's start + duration)
        duration = 0
        if snippets:
            last_snippet = snippets[-1]
            duration = int(last_snippet.start + last_snippet.duration)
        
        # Try to get video title (requires additional API, skip for now - can add later)
        title = f"YouTube Video {video_id}"
        
        result = {
            "success": True,
            "transcript": transcript_text,
            "title": title,
            "duration": duration,
            "video_id": video_id
        }
        
        # Cache the result
        save_to_cache(video_id, result)
        
        return result
        
    except TranscriptsDisabled:
        return {
            "success": False,
            "error": "Transcripts are disabled for this video",
            "transcript": "",
            "title": "",
            "duration": 0,
            "video_id": video_id
        }
    
    except NoTranscriptFound:
        return {
            "success": False,
            "error": "No transcript/captions found for this video",
            "transcript": "",
            "title": "",
            "duration": 0,
            "video_id": video_id
        }
    
    except VideoUnavailable:
        return {
            "success": False,
            "error": "Video is unavailable (may be private or deleted)",
            "transcript": "",
            "title": "",
            "duration": 0,
            "video_id": video_id
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": f"Unexpected error: {str(e)}",
            "transcript": "",
            "title": "",
            "duration": 0,
            "video_id": video_id
        }


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 youtube-reader.py <YouTube URL>")
        print("Example: python3 youtube-reader.py https://www.youtube.com/watch?v=VIDEO_ID")
        sys.exit(1)
    
    url = sys.argv[1]
    result = get_youtube_transcript(url)
    
    if result['success']:
        print(f"✓ Successfully fetched transcript")
        print(f"Video ID: {result['video_id']}")
        print(f"Duration: {result['duration']}s ({result['duration']//60}min)")
        print(f"\nTranscript ({len(result['transcript'])} characters):")
        print("-" * 80)
        print(result['transcript'][:500])
        if len(result['transcript']) > 500:
            print(f"\n... (truncated, {len(result['transcript']) - 500} more characters)")
    else:
        print(f"✗ Failed to fetch transcript")
        print(f"Error: {result['error']}")
        sys.exit(1)

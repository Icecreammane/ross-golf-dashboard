#!/usr/bin/env python3
"""
Auto Voice Generation System
Converts text to speech using OpenAI TTS (Onyx voice) for morning briefs, 
build updates, and notifications.

Usage:
    from systems.auto_voice import generate_voice_message
    
    audio_path = generate_voice_message(
        text="Good morning Ross! Here's your brief.",
        output_path="/path/to/output.opus"
    )
"""

import os
import json
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Tuple

# Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_TTS_URL = "https://api.openai.com/v1/audio/speech"
VOICE = "onyx"  # Deep, authoritative voice Ross prefers
MODEL = "tts-1-hd"  # High quality model
MAX_CHARS_PER_CLIP = 4096  # OpenAI TTS limit
WORKSPACE = Path.home() / "clawd"
COST_LOG = WORKSPACE / "logs" / "voice-cost-tracking.json"


class VoiceGenerationError(Exception):
    """Raised when voice generation fails."""
    pass


def estimate_cost(text: str) -> float:
    """
    Estimate cost of TTS generation.
    OpenAI pricing: $15.00 / 1M characters (tts-1-hd)
    
    Args:
        text: Text to convert
        
    Returns:
        Estimated cost in USD
    """
    char_count = len(text)
    cost_per_char = 15.00 / 1_000_000
    return char_count * cost_per_char


def log_cost(text_length: int, cost: float, purpose: str):
    """
    Log voice generation cost for tracking.
    
    Args:
        text_length: Character count
        cost: Estimated cost in USD
        purpose: What this voice was generated for
    """
    COST_LOG.parent.mkdir(parents=True, exist_ok=True)
    
    # Load existing log
    if COST_LOG.exists():
        with open(COST_LOG, 'r') as f:
            log = json.load(f)
    else:
        log = {"total_cost": 0.0, "total_chars": 0, "generations": []}
    
    # Add new entry
    entry = {
        "timestamp": datetime.now().isoformat(),
        "purpose": purpose,
        "char_count": text_length,
        "cost_usd": cost
    }
    
    log["generations"].append(entry)
    log["total_cost"] += cost
    log["total_chars"] += text_length
    
    # Keep last 1000 entries
    log["generations"] = log["generations"][-1000:]
    
    with open(COST_LOG, 'w') as f:
        json.dump(log, f, indent=2)


def split_text(text: str, max_chars: int = MAX_CHARS_PER_CLIP) -> List[str]:
    """
    Split long text into chunks that fit within TTS limits.
    Tries to split on sentence boundaries for natural breaks.
    
    Args:
        text: Text to split
        max_chars: Maximum characters per chunk
        
    Returns:
        List of text chunks
    """
    if len(text) <= max_chars:
        return [text]
    
    chunks = []
    current_chunk = ""
    
    # Split on sentences first
    sentences = text.replace('. ', '.|').replace('! ', '!|').replace('? ', '?|').split('|')
    
    for sentence in sentences:
        if len(current_chunk) + len(sentence) <= max_chars:
            current_chunk += sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = sentence
    
    if current_chunk:
        chunks.append(current_chunk.strip())
    
    return chunks


def generate_voice_message(
    text: str,
    output_path: str | Path,
    voice: str = VOICE,
    model: str = MODEL,
    format: str = "opus",  # opus (Telegram native) or mp3 (universal)
    speed: float = 1.0,
    log_purpose: str = "generic"
) -> Path:
    """
    Generate voice message from text using OpenAI TTS.
    
    Args:
        text: Text to convert to speech
        output_path: Where to save the audio file
        voice: OpenAI voice to use (alloy, echo, fable, onyx, nova, shimmer)
        model: TTS model (tts-1 or tts-1-hd)
        format: Output format (opus, mp3, aac, flac)
        speed: Playback speed (0.25 to 4.0)
        log_purpose: Purpose of this voice generation (for cost tracking)
        
    Returns:
        Path to generated audio file
        
    Raises:
        VoiceGenerationError: If generation fails
    """
    if not OPENAI_API_KEY:
        raise VoiceGenerationError("OPENAI_API_KEY not found in environment")
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Check if text needs splitting
    chunks = split_text(text)
    
    if len(chunks) > 1:
        # Multiple chunks - generate separately and concatenate
        print(f"⚠️  Text is {len(text)} chars, splitting into {len(chunks)} clips...")
        chunk_paths = []
        
        for i, chunk in enumerate(chunks, 1):
            chunk_path = output_path.parent / f"{output_path.stem}_part{i}{output_path.suffix}"
            _generate_single_clip(chunk, chunk_path, voice, model, format, speed)
            chunk_paths.append(chunk_path)
        
        # TODO: Concatenate clips if needed (requires ffmpeg)
        # For now, just return the first clip and log a warning
        print(f"⚠️  Generated {len(chunks)} clips. Using first clip only.")
        print(f"    Full clips: {[str(p) for p in chunk_paths]}")
        
        # Estimate cost for all chunks
        cost = estimate_cost(text)
        log_cost(len(text), cost, log_purpose)
        
        return chunk_paths[0]
    
    else:
        # Single clip - generate directly
        cost = estimate_cost(text)
        log_cost(len(text), cost, log_purpose)
        return _generate_single_clip(text, output_path, voice, model, format, speed)


def _generate_single_clip(
    text: str,
    output_path: Path,
    voice: str,
    model: str,
    format: str,
    speed: float
) -> Path:
    """
    Generate a single voice clip (internal function).
    
    Args:
        text: Text to convert
        output_path: Where to save
        voice: Voice to use
        model: TTS model
        format: Output format
        speed: Playback speed
        
    Returns:
        Path to generated audio
        
    Raises:
        VoiceGenerationError: If API call fails
    """
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": model,
        "input": text,
        "voice": voice,
        "response_format": format,
        "speed": speed
    }
    
    try:
        response = requests.post(
            OPENAI_TTS_URL,
            headers=headers,
            json=payload,
            timeout=30
        )
        
        if response.status_code != 200:
            error_msg = f"OpenAI TTS API error: {response.status_code} - {response.text}"
            raise VoiceGenerationError(error_msg)
        
        # Save audio file
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        print(f"✅ Voice generated: {output_path}")
        print(f"   Length: {len(text)} chars")
        print(f"   Size: {len(response.content) / 1024:.1f} KB")
        
        return output_path
    
    except requests.exceptions.RequestException as e:
        raise VoiceGenerationError(f"Network error during TTS generation: {e}")


def generate_with_transcript(
    text: str,
    output_dir: Path,
    filename_base: str,
    **kwargs
) -> Tuple[Path, Path]:
    """
    Generate voice + save transcript alongside.
    
    Args:
        text: Text to convert
        output_dir: Directory to save files
        filename_base: Base filename (without extension)
        **kwargs: Additional args for generate_voice_message()
        
    Returns:
        Tuple of (audio_path, transcript_path)
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Determine audio format
    format = kwargs.get('format', 'opus')
    audio_path = output_dir / f"{filename_base}.{format}"
    transcript_path = output_dir / f"{filename_base}.txt"
    
    # Generate voice
    audio_path = generate_voice_message(text, audio_path, **kwargs)
    
    # Save transcript
    with open(transcript_path, 'w') as f:
        f.write(f"Voice Transcript - Generated {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("=" * 80 + "\n\n")
        f.write(text)
    
    print(f"📝 Transcript saved: {transcript_path}")
    
    return audio_path, transcript_path


def get_cost_summary() -> dict:
    """
    Get summary of voice generation costs.
    
    Returns:
        Dictionary with total cost, char count, and recent generations
    """
    if not COST_LOG.exists():
        return {
            "total_cost_usd": 0.0,
            "total_chars": 0,
            "generation_count": 0,
            "recent": []
        }
    
    with open(COST_LOG, 'r') as f:
        log = json.load(f)
    
    return {
        "total_cost_usd": log.get("total_cost", 0.0),
        "total_chars": log.get("total_chars", 0),
        "generation_count": len(log.get("generations", [])),
        "recent": log.get("generations", [])[-10:]  # Last 10
    }


# CLI interface for testing
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python auto-voice.py 'Your text here' [output.opus]")
        print("  python auto-voice.py --cost-summary")
        sys.exit(1)
    
    if sys.argv[1] == '--cost-summary':
        summary = get_cost_summary()
        print("\n💰 Voice Generation Cost Summary")
        print("=" * 50)
        print(f"Total Cost: ${summary['total_cost_usd']:.4f}")
        print(f"Total Characters: {summary['total_chars']:,}")
        print(f"Total Generations: {summary['generation_count']}")
        print("\nRecent Generations:")
        for gen in summary['recent']:
            print(f"  • {gen['timestamp'][:19]} | {gen['purpose']} | {gen['char_count']} chars | ${gen['cost_usd']:.4f}")
    
    else:
        # Generate voice from command line
        text = sys.argv[1]
        output = sys.argv[2] if len(sys.argv) > 2 else "test-voice.opus"
        
        print(f"\n🎙️  Generating voice...")
        print(f"Text: {text[:100]}{'...' if len(text) > 100 else ''}")
        print(f"Output: {output}")
        
        try:
            path = generate_voice_message(text, output, log_purpose="cli-test")
            print(f"\n✅ Success! Audio saved to: {path}")
        except VoiceGenerationError as e:
            print(f"\n❌ Error: {e}")
            sys.exit(1)

#!/usr/bin/env python3
"""
Telegram Voice Message Handler for Jarvis
Integrates with Clawdbot's message system to process voice messages
"""

import os
import sys
import json
import requests
from pathlib import Path
from voice_commands import process_voice_message

WORKSPACE = Path.home() / "clawd"
TEMP_DIR = WORKSPACE / "voice" / "temp"
TEMP_DIR.mkdir(parents=True, exist_ok=True)


def download_telegram_voice(file_id, bot_token):
    """Download voice message from Telegram"""
    # Get file path
    file_info_url = f"https://api.telegram.org/bot{bot_token}/getFile?file_id={file_id}"
    file_info_response = requests.get(file_info_url).json()
    
    if not file_info_response.get("ok"):
        raise Exception(f"Failed to get file info: {file_info_response}")
    
    file_path = file_info_response["result"]["file_path"]
    
    # Download file
    download_url = f"https://api.telegram.org/file/bot{bot_token}/{file_path}"
    audio_data = requests.get(download_url).content
    
    # Save to temp file
    temp_file = TEMP_DIR / f"{file_id}.ogg"
    with open(temp_file, "wb") as f:
        f.write(audio_data)
    
    return temp_file


def handle_voice_message(file_id, bot_token=None):
    """
    Handle incoming voice message from Telegram
    
    Args:
        file_id: Telegram file_id for the voice message
        bot_token: Telegram bot token (optional, will read from env if not provided)
    
    Returns:
        dict: Processing result with transcript, command, and result
    """
    if bot_token is None:
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
        if not bot_token:
            raise Exception("TELEGRAM_BOT_TOKEN not set in environment")
    
    # Download voice message
    audio_file = download_telegram_voice(file_id, bot_token)
    
    # Process it
    result = process_voice_message(str(audio_file))
    
    # Cleanup
    audio_file.unlink()
    
    return result


def send_telegram_reply(chat_id, text, bot_token=None):
    """Send reply back to Telegram"""
    if bot_token is None:
        bot_token = os.environ.get("TELEGRAM_BOT_TOKEN")
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    response = requests.post(url, json=payload)
    return response.json()


if __name__ == "__main__":
    # CLI for testing
    if len(sys.argv) > 1:
        file_id = sys.argv[1]
        result = handle_voice_message(file_id)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python3 telegram_voice_handler.py <telegram_file_id>")
        print("\nThis script is meant to be called by Clawdbot when a voice message arrives.")

#!/usr/bin/env python3
import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

story = """Here's a story for your drive, sir. The Builder. There was once a man who decided he was tired of building other people's dreams. Every morning, he drove to work. Built products for a company that would never make him free. Good work. Important work. But not his work. So he made a choice: build twice. By day, he did his job well. Lifted weights. Tracked his progress. Showed up. But at night? That's when the real work began. Small tools. Side projects. Things no one asked for but everyone would eventually need. Some nights, nothing worked. Some mornings, he wondered if it was worth it. But every small win compounded. Every tool he built made the next one easier. Every system he created bought him back a little time, a little freedom, a little closer to the beach in Florida. One day, he looked back and realized: he'd built an empire while everyone else was sleeping. The company didn't own him anymore. He owned his time. And that's when the real life began. Now go build your day, Ross. You're already building your future."""

with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="onyx",
    input=story
) as response:
    response.stream_to_file("/Users/clawdbot/clawd/voice/builder_story.mp3")

print("✅ Audio generated")

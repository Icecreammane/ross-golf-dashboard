#!/usr/bin/env python3
"""Generate Jarvis avatar concepts"""
import os
from openai import OpenAI
import base64

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

prompts = [
    {
        "name": "concept1_butler",
        "prompt": "Professional AI assistant avatar - sleek robotic butler with blue and silver accents, refined and capable, modern digital art style, friendly but sophisticated, clean minimalist design suitable for profile picture, no background"
    },
    {
        "name": "concept2_copilot",
        "prompt": "AI co-pilot avatar - blend of aviation helmet visor and holographic interface, blue/cyan tech aesthetics, partnership energy, modern and sleek, confident capable look, profile picture style, transparent background"
    },
    {
        "name": "concept3_builder",
        "prompt": "Empire builder AI assistant avatar - architectural blueprint aesthetic mixed with modern tech, construction/building theme, blue and white color scheme, strategic and capable, clean professional design for profile picture"
    },
    {
        "name": "concept4_hybrid",
        "prompt": "Strategic AI co-pilot avatar - combination of tactical war room hologram and aviation tech, blue holographic aesthetic, partnership and capability vibes, modern sleek design, building-the-future energy, profile picture style, minimal background"
    }
]

print("Generating 4 avatar concepts for Jarvis...")

for i, concept in enumerate(prompts, 1):
    print(f"\n[{i}/4] Generating {concept['name']}...")
    
    try:
        response = client.images.generate(
            model="dall-e-3",
            prompt=concept['prompt'],
            size="1024x1024",
            quality="hd",
            n=1
        )
        
        image_url = response.data[0].url
        revised_prompt = response.data[0].revised_prompt
        
        # Download the image
        import urllib.request
        filename = f"{concept['name']}.png"
        urllib.request.urlretrieve(image_url, filename)
        
        print(f"✅ Saved: {filename}")
        print(f"📝 Revised prompt: {revised_prompt[:100]}...")
        
    except Exception as e:
        print(f"❌ Error: {e}")

print("\n🎨 Avatar generation complete!")
print(f"📁 Files saved in: {os.getcwd()}")

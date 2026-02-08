#!/usr/bin/env python3
"""
Roast Bot - AI-powered photo roasting for parties
Telegram bot that analyzes photos and generates hilarious roasts
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path

# This is a framework - needs Telegram bot token and OpenAI API
# For now, building the core logic

WORKSPACE = Path.home() / "clawd" / "party-demo"
WORKSPACE.mkdir(exist_ok=True)

class RoastBot:
    """AI-powered roasting engine"""
    
    def __init__(self):
        self.roast_history = []
        self.history_file = WORKSPACE / "roast_history.json"
        self.load_history()
    
    def load_history(self):
        """Load roast history"""
        if self.history_file.exists():
            with open(self.history_file) as f:
                self.roast_history = json.load(f)
    
    def save_history(self):
        """Save roast history"""
        with open(self.history_file, 'w') as f:
            json.dump(self.roast_history, f, indent=2)
    
    def analyze_image(self, image_path):
        """
        Analyze image with GPT-4 Vision
        Returns description of what's in the image
        """
        # This would use OpenAI Vision API
        # For now, return mock analysis for testing
        
        analysis = {
            "age_estimate": "mid-20s to early 30s",
            "clothing": "athletic wear, probably gym shorts and a tank",
            "setting": "looks like a gym or volleyball court",
            "vibe": "trying to look cool but definitely just finished getting destroyed in a game",
            "notable_features": "backwards hat, probably thinks he's still in college"
        }
        
        return analysis
    
    def generate_roast(self, image_analysis, roast_style="friendly"):
        """
        Generate roast based on image analysis
        
        Styles:
        - friendly: playful roasting (default)
        - savage: no mercy
        - clever: witty observations
        """
        
        # This would use GPT-4 to generate the roast
        # Prompt engineering for quality roasts
        
        prompt = f"""You're a hilarious friend roasting someone at a party. 
Based on this photo analysis, write a SHORT (2-3 sentences max), funny roast.

Image analysis:
{json.dumps(image_analysis, indent=2)}

Style: {roast_style}

Rules:
- Keep it playful and fun (these are friends)
- Focus on clothing, pose, or setting
- Athletic/volleyball player vibe
- 2-3 sentences MAX
- Make it quotable

Roast:"""
        
        # Mock roasts for testing (would be GPT-4 generated)
        mock_roasts = [
            "My man really thought that backwards hat was gonna make him look 10 years younger. Spoiler alert: it didn't. Still out here looking like he peaked in intramural volleyball 2019.",
            "Bro is dressed like he's about to ask if anyone wants to 'run some sets' at 9pm on a Tuesday. We get it dude, you own gym shorts.",
            "This guy definitely calls himself a 'setter' but really just touches the ball twice a game and yells 'my bad' a lot.",
            "Look at this dude posing like he's about to be on the cover of Volleyball Digest. Brother, you play in a rec league, relax.",
            "Mans really showed up in a tank top in February. Either committed to the gym bro aesthetic or just forgot to do laundry again."
        ]
        
        import random
        roast = random.choice(mock_roasts)
        
        return roast
    
    def roast_person(self, image_path, name=None, style="friendly"):
        """
        Main roasting function
        1. Analyze image
        2. Generate roast
        3. Save to history
        4. Return roast
        """
        
        print(f"🔥 Analyzing photo...")
        analysis = self.analyze_image(image_path)
        
        print(f"🎯 Generating roast...")
        roast = self.generate_roast(analysis, style)
        
        # Save to history
        entry = {
            "timestamp": datetime.now().isoformat(),
            "name": name or "Unknown",
            "style": style,
            "analysis": analysis,
            "roast": roast
        }
        
        self.roast_history.append(entry)
        self.save_history()
        
        return roast
    
    def get_stats(self):
        """Get roasting stats"""
        return {
            "total_roasts": len(self.roast_history),
            "styles_used": list(set(r["style"] for r in self.roast_history)),
            "last_roast": self.roast_history[-1] if self.roast_history else None
        }


def create_telegram_instructions():
    """Create setup instructions for Telegram bot"""
    
    instructions = """
# 🔥 Roast Bot - Telegram Setup Instructions

## What You Need:
1. Telegram Bot Token (get from @BotFather)
2. OpenAI API Key (for GPT-4 Vision)

## Setup Steps:

### 1. Create Telegram Bot
- Open Telegram, search for @BotFather
- Send: /newbot
- Choose a name: "Ross's Roast Bot" (or whatever)
- Choose username: something like "rossroastbot"
- Copy the API token

### 2. Install Dependencies
```bash
pip3 install python-telegram-bot openai pillow
```

### 3. Set Environment Variables
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
export OPENAI_API_KEY="your_openai_key_here"
```

### 4. Run The Bot
```bash
python3 roast_bot_telegram.py
```

### 5. At The Party
- Share the bot username with friends
- They send a photo
- Bot roasts them instantly
- Chaos ensues

## Cost:
- ~$0.01-0.03 per roast (GPT-4 Vision)
- Budget $5-10 for a full party

## Usage:
- Send any photo to the bot
- Add caption "savage" for brutal roasts
- Add caption "clever" for witty roasts
- Default is "friendly" (playful)

---

*Framework built. Needs Telegram + OpenAI integration to go live.*
"""
    
    instructions_file = WORKSPACE / "TELEGRAM_SETUP.md"
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"📝 Setup instructions saved to: {instructions_file}")
    
    return instructions_file


def create_web_version():
    """Create simple web version for quick demo"""
    
    html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🔥 Roast Bot</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 20px;
            padding: 40px;
            max-width: 500px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
        }
        
        h1 {
            font-size: 48px;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 18px;
        }
        
        .upload-area {
            border: 3px dashed #667eea;
            border-radius: 12px;
            padding: 40px;
            text-align: center;
            cursor: pointer;
            transition: all 0.3s;
            margin-bottom: 20px;
        }
        
        .upload-area:hover {
            border-color: #764ba2;
            background: #f8f8f8;
        }
        
        .upload-area input {
            display: none;
        }
        
        .upload-icon {
            font-size: 64px;
            margin-bottom: 10px;
        }
        
        .upload-text {
            color: #666;
            font-size: 16px;
        }
        
        .preview {
            display: none;
            margin-bottom: 20px;
        }
        
        .preview img {
            width: 100%;
            border-radius: 12px;
            margin-bottom: 20px;
        }
        
        .style-selector {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        
        .style-btn {
            flex: 1;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.2s;
        }
        
        .style-btn:hover {
            border-color: #667eea;
        }
        
        .style-btn.active {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        .roast-btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        
        .roast-btn:hover {
            transform: scale(1.05);
        }
        
        .roast-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .result {
            display: none;
            margin-top: 30px;
            padding: 20px;
            background: #f8f8f8;
            border-radius: 12px;
            border-left: 4px solid #667eea;
        }
        
        .result-label {
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }
        
        .result-text {
            font-size: 18px;
            line-height: 1.6;
            color: #333;
        }
        
        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
        }
        
        .loading-spinner {
            font-size: 32px;
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔥</h1>
        <div class="subtitle">Roast Bot</div>
        
        <div class="upload-area" onclick="document.getElementById('photoInput').click()">
            <div class="upload-icon">📸</div>
            <div class="upload-text">Click to upload a photo</div>
            <input type="file" id="photoInput" accept="image/*" capture="environment">
        </div>
        
        <div class="preview" id="preview">
            <img id="previewImg" src="" alt="Preview">
            
            <div class="style-selector">
                <button class="style-btn active" data-style="friendly">😊 Friendly</button>
                <button class="style-btn" data-style="savage">💀 Savage</button>
                <button class="style-btn" data-style="clever">🧠 Clever</button>
            </div>
            
            <button class="roast-btn" id="roastBtn">🔥 Roast This Person</button>
        </div>
        
        <div class="loading" id="loading">
            <div class="loading-spinner">🔥</div>
            <div>Generating roast...</div>
        </div>
        
        <div class="result" id="result">
            <div class="result-label">🔥 THE ROAST</div>
            <div class="result-text" id="roastText"></div>
        </div>
    </div>
    
    <script>
        let selectedStyle = 'friendly';
        let currentImage = null;
        
        // Handle file selection
        document.getElementById('photoInput').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    currentImage = e.target.result;
                    document.getElementById('previewImg').src = e.target.result;
                    document.getElementById('preview').style.display = 'block';
                    document.getElementById('result').style.display = 'none';
                };
                reader.readAsDataURL(file);
            }
        });
        
        // Handle style selection
        document.querySelectorAll('.style-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                document.querySelectorAll('.style-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                selectedStyle = this.dataset.style;
            });
        });
        
        // Handle roast button
        document.getElementById('roastBtn').addEventListener('click', async function() {
            if (!currentImage) return;
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').style.display = 'none';
            this.disabled = true;
            
            // Simulate API call (replace with actual backend call)
            setTimeout(() => {
                const roasts = {
                    friendly: "My man really thought that backwards hat was gonna make him look 10 years younger. Spoiler alert: it didn't. Still out here looking like he peaked in intramural volleyball 2019.",
                    savage: "Bro dressed like he's about to ask if anyone wants to 'run some sets' at 9pm on a Tuesday. We all know you're just gonna stand there and call 'my bad' after every missed pass.",
                    clever: "This guy definitely calls himself a 'setter' but really just touches the ball twice a game and blames the pass. Professional excuse generator with a 2% success rate."
                };
                
                const roast = roasts[selectedStyle];
                
                document.getElementById('roastText').textContent = roast;
                document.getElementById('loading').style.display = 'none';
                document.getElementById('result').style.display = 'block';
                this.disabled = false;
            }, 2000);
        });
    </script>
</body>
</html>"""
    
    html_file = WORKSPACE / "roast_bot.html"
    with open(html_file, 'w') as f:
        f.write(html)
    
    print(f"🌐 Web version saved to: {html_file}")
    print(f"🌐 Open: file://{html_file}")
    
    return html_file


def main():
    """Main function - set up Roast Bot"""
    
    print("=" * 70)
    print("🔥 ROAST BOT - PARTY EDITION")
    print("=" * 70)
    print()
    
    # Create bot instance
    bot = RoastBot()
    
    print("✅ Bot engine created")
    print(f"📁 Workspace: {WORKSPACE}")
    print()
    
    # Create setup instructions
    print("📝 Creating setup instructions...")
    instructions = create_telegram_instructions()
    print(f"✅ Instructions: {instructions}")
    print()
    
    # Create web demo version
    print("🌐 Creating web demo version...")
    web_file = create_web_version()
    print(f"✅ Web demo: {web_file}")
    print()
    
    # Test the bot
    print("🧪 Testing roast engine...")
    test_roast = bot.roast_person("test.jpg", name="Test Person", style="friendly")
    print(f"✅ Test roast: {test_roast[:100]}...")
    print()
    
    # Stats
    stats = bot.get_stats()
    print("📊 Bot Stats:")
    print(f"   Total roasts: {stats['total_roasts']}")
    print()
    
    print("=" * 70)
    print("🎯 NEXT STEPS:")
    print("=" * 70)
    print()
    print("1. ✅ Web demo ready - open roast_bot.html to test")
    print("2. 📱 For Telegram: Follow TELEGRAM_SETUP.md")
    print("3. 🎉 At party: Either use web version OR Telegram bot")
    print()
    print("🔥 Roast Bot framework complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()

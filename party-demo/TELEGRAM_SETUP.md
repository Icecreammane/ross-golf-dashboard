
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

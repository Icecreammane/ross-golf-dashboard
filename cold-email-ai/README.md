# Cold Email AI Platform - MVP

> Generate personalized cold emails from company URLs using AI. Built with Flask + OpenAI.

## 🚀 Quick Start

### 1. Set OpenAI API Key

```bash
export OPENAI_API_KEY='your-openai-api-key-here'
```

Add to `~/.zshrc` or `~/.bashrc` to persist:
```bash
echo "export OPENAI_API_KEY='your-key'" >> ~/.zshrc
source ~/.zshrc
```

### 2. Start the App

```bash
cd ~/clawd/cold-email-ai
chmod +x start.sh
./start.sh
```

The script will:
- Create a Python virtual environment (if needed)
- Install dependencies
- Kill any existing process on port 3001
- Start the Flask app

### 3. Access the App

- **Main App:** http://localhost:3001
- **Landing Page:** http://localhost:3001/landing
- **Health Check:** http://localhost:3001/health

## 📋 Features

- ✅ **Simple UI** - Paste company URL, get personalized email
- ✅ **AI-Powered** - Uses GPT-4 for intelligent email generation
- ✅ **Company Research** - Automatically scrapes and analyzes company websites
- ✅ **Copy to Clipboard** - One-click copy functionality
- ✅ **Professional Design** - Clean, modern UI
- ✅ **Fast** - Generates emails in ~10 seconds

## 🛠 Tech Stack

- **Backend:** Flask (Python)
- **AI:** OpenAI GPT-4
- **Web Scraping:** BeautifulSoup4 + requests
- **Frontend:** Vanilla HTML/CSS/JS (no frameworks)
- **Port:** 3001

## 📁 Project Structure

```
cold-email-ai/
├── app.py                 # Flask backend + OpenAI integration
├── requirements.txt       # Python dependencies
├── start.sh              # Easy restart script
├── README.md             # This file
├── templates/
│   ├── index.html        # Main app UI
│   └── landing.html      # Marketing landing page
└── examples/             # Generated email samples
```

## 🎯 How It Works

1. **User Input:** Paste company website URL (e.g., `stripe.com`)
2. **Research:** App scrapes the website for company info (title, description, content)
3. **AI Generation:** OpenAI GPT-4 analyzes company data and generates personalized cold email
4. **Output:** Display email with subject line + body, ready to copy

## 🧪 Testing

Generate test emails:
```bash
# Examples saved in examples/ directory
curl -X POST http://localhost:3001/api/generate \
  -H "Content-Type: application/json" \
  -d '{"url": "stripe.com", "context": "AI automation services"}'
```

## 🔧 Manual Setup (if start.sh doesn't work)

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export OPENAI_API_KEY='your-key'

# Run app
python app.py
```

## 🚨 Troubleshooting

**Port 3001 already in use:**
```bash
lsof -ti:3001 | xargs kill -9
./start.sh
```

**OpenAI API errors:**
- Check API key is set: `echo $OPENAI_API_KEY`
- Verify API key is valid at https://platform.openai.com/api-keys
- Check account has credits

**Module not found:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## 📊 API Endpoints

### `POST /api/generate`
Generate cold email from company URL.

**Request:**
```json
{
  "url": "example.com",
  "context": "Your offering (optional)"
}
```

**Response:**
```json
{
  "email": "Subject: ...\n\n[email body]",
  "company_info": {
    "domain": "example.com",
    "title": "Example Company",
    "description": "...",
    "content": "..."
  }
}
```

### `GET /health`
Health check endpoint.

## 🎨 Customization

**Change AI Model:**
Edit `app.py`, line ~85:
```python
model="gpt-4"  # Change to "gpt-3.5-turbo" for cheaper/faster
```

**Adjust Email Length:**
Edit prompt in `app.py`, line ~68:
```python
- Keeps it under 150 words  # Increase/decrease as needed
```

**Customize UI:**
Edit `templates/index.html` and `templates/landing.html`

## 📝 License

MIT - Do whatever you want with it.

## 🚢 Shipping Checklist

- [x] Flask backend with OpenAI integration
- [x] Web scraping for company research
- [x] Clean, professional UI
- [x] Copy to clipboard functionality
- [x] Landing page with pricing
- [x] Health check endpoint
- [x] Easy restart script
- [x] Documentation

**Status:** ✅ MVP COMPLETE - Ready to ship!

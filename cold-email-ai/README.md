# 🤖 Cold Email AI Platform

**Generate personalized cold emails from company URLs in seconds.**

Built as MVP for AI Concierge Service business demonstration.

---

## Features

✅ **Simple Input**: Paste any company URL
✅ **AI Analysis**: Scrapes website to understand the company
✅ **Smart Generation**: Creates personalized cold emails using OpenAI
✅ **Beautiful UI**: Landing page + app interface
✅ **Copy & Use**: One-click copy to clipboard
✅ **Mock Mode**: Works without API key for demo purposes

---

## Quick Start

### 1. Install Dependencies

```bash
cd /Users/clawdbot/clawd/cold-email-ai
pip3 install -r requirements.txt
```

### 2. Set OpenAI API Key (Optional)

For AI-powered emails (otherwise uses mock mode):

```bash
export OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Run the App

```bash
python3 app.py
```

Or with custom port:

```bash
PORT=3001 python3 app.py
```

### 4. Open in Browser

- **Landing Page:** http://localhost:3001
- **App Interface:** http://localhost:3001/app

---

## Usage

1. Go to http://localhost:3001
2. Click "Try It Free"
3. Paste a company URL (e.g., `https://stripe.com`)
4. Click "Generate Email"
5. Get personalized cold email with subject + body
6. Copy and use!

---

## Architecture

### Tech Stack
- **Backend:** Flask (Python)
- **Frontend:** HTML/CSS/JavaScript (no framework, pure vanilla)
- **AI:** OpenAI GPT-4 API
- **Web Scraping:** BeautifulSoup + Requests

### Project Structure
```
cold-email-ai/
├── app.py                  # Flask backend
├── requirements.txt        # Python dependencies
├── templates/
│   ├── index.html         # Landing page
│   └── app.html           # Main app interface
└── README.md              # This file
```

### API Endpoints

**`POST /api/generate`**
- Input: `{ "url": "https://company.com" }`
- Output: `{ "success": true, "company": {...}, "email": {...} }`

**`GET /health`**
- Health check + OpenAI status

---

## How It Works

1. **Web Scraping**: Fetches company website and extracts:
   - Page title
   - Meta description
   - Key headings (H1, H2)
   - Paragraph content samples

2. **AI Prompt Engineering**: Sends company context to OpenAI with instructions:
   - Show research understanding
   - Identify pain points
   - Offer clear value
   - Soft CTA
   - Under 150 words

3. **Email Formatting**: Parses AI response into:
   - Subject line
   - Email body

4. **Mock Mode**: If no OpenAI API key, generates template-based email for demo

---

## Examples

### Input
```
https://stripe.com
```

### Output
```
Subject: Quick question about Stripe's payment infrastructure

Hi there,

I was just browsing Stripe's website and noticed you're focused on 
helping businesses accept payments online seamlessly.

I work with companies like yours to help them streamline their 
outreach and close more enterprise deals using AI-powered 
personalization.

Would love to show you a quick 10-minute demo of how we've helped 
similar fintech companies increase response rates by 3x.

Worth a quick call?

Best,
[Your Name]
```

---

## Customization

### Modify Email Style
Edit the prompt in `app.py` function `generate_email_with_openai()`:

```python
prompt = f"""You are an expert cold email writer...
[customize instructions here]
"""
```

### Change Port
```bash
PORT=5000 python3 app.py
```

### Adjust AI Model
In `app.py`, change:
```python
'model': 'gpt-4'  # or 'gpt-3.5-turbo' for cheaper/faster
```

---

## Deployment

### Local (Development)
```bash
python3 app.py
```

### Production (Docker)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "app.py"]
```

### Environment Variables
- `OPENAI_API_KEY`: OpenAI API key (optional, uses mock mode without)
- `PORT`: Server port (default: 3001)

---

## Limitations

1. **Rate Limits**: OpenAI API has rate limits
2. **Website Access**: Some sites block scraping (403/Cloudflare)
3. **Email Quality**: Depends on website content quality
4. **Mock Mode**: Template-based when no API key

---

## Future Enhancements

**V2 Ideas:**
- [ ] Save generated emails history
- [ ] A/B test subject lines
- [ ] Bulk URL processing
- [ ] Email template library
- [ ] Chrome extension
- [ ] CRM integrations
- [ ] Analytics dashboard
- [ ] User accounts & auth

---

## Cost Analysis

**Per Email (with OpenAI):**
- ~400 tokens (prompt + completion)
- GPT-4: $0.03/1K tokens input + $0.06/1K tokens output
- **Cost: ~$0.02-0.04 per email**

**At Scale:**
- 100 emails/day = $2-4/day
- 1,000 emails/day = $20-40/day

---

## Business Model Ideas

1. **Freemium**: 10 free emails, then $20/month unlimited
2. **Pay-per-email**: $0.10 per email (5x markup on cost)
3. **API Access**: $100/month for API integration
4. **White Label**: $500/month for agencies
5. **Enterprise**: Custom pricing for bulk users

---

## Contributing

This is an MVP. Improvements welcome:
- Better error handling
- More AI models (Anthropic, etc)
- Email validation
- A/B testing
- Template variations

---

## License

MIT License - Do whatever you want with this code.

---

## Built By

Builder Agent (AI subagent)
Part of AI Concierge Service ecosystem
Built: Feb 5-6, 2026

---

## Questions?

This is a working MVP meant to demonstrate:
1. AI can generate quality cold emails
2. Simple UX = high conversion
3. Value is immediate and obvious

Ship it, test it, iterate. 🚀

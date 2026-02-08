```markdown
# 📧 Email Template Generator

> AI-powered golf outreach email generator with learning capabilities. Uses local Llama LLM to generate personalized email templates based on past successful patterns.

**Status:** ✅ Production-Ready  
**Version:** 1.0.0  
**Built:** 2026-02-08

---

## 🎯 Features

### Core Capabilities
- ✅ **Local LLM Integration** - Uses Llama 3.1 via Ollama (no API costs)
- ✅ **Context-Aware Generation** - Understands recipient type and situation
- ✅ **3 Automatic Variations** - Formal, casual, and urgent tone per request
- ✅ **Pattern Learning** - Learns from your past successful emails
- ✅ **Performance Tracking** - Tracks which templates convert
- ✅ **Continuous Improvement** - Gets better with feedback
- ✅ **CLI Tool** - Command-line interface for quick generation
- ✅ **Web Dashboard** - Beautiful UI for browsing and managing templates

### Intelligence Features
- 📊 **Pattern Extraction** - Analyzes structure, phrases, openings, CTAs
- 🎯 **Smart Recommendations** - Suggests improvements based on what worked
- 🔄 **Feedback Loop** - Updates pattern effectiveness automatically
- 📈 **Performance Analytics** - Track conversion rates and success patterns

---

## 🚀 Quick Start

### 1. Prerequisites

**Install Ollama (if not already installed):**
```bash
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh
```

**Pull Llama model:**
```bash
ollama pull llama3.1:8b
```

**Verify Ollama is running:**
```bash
ollama list
```

### 2. Install

```bash
cd ~/clawd/email-template-generator

# Install Python dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Start Dashboard

```bash
./start_dashboard.sh
```

Access at: **http://localhost:3002**

### 4. Use CLI Tool

```bash
# Make executable
chmod +x cli/generate_email.py

# Optional: Link to path
sudo ln -sf $(pwd)/cli/generate_email.py /usr/local/bin/generate_email

# Generate emails
generate_email generate --to "golf_student" --type "inquiry_response"
```

---

## 📖 Usage

### CLI Examples

**Generate 3 variations:**
```bash
generate_email generate \
  --to golf_student \
  --type inquiry_response \
  --context "Student wants help with slice, plays at Oak Creek"
```

**List templates:**
```bash
# Recent templates
generate_email list

# Best performing
generate_email list --best

# Filtered
generate_email list --to partner --type collaboration
```

**View specific template:**
```bash
generate_email show 42          # Show template #42
generate_email show 42 --copy   # Copy to clipboard (macOS)
```

**Add feedback:**
```bash
# Mark as used
generate_email feedback 42 --used

# Mark as converted
generate_email feedback 42 --converted --score 5 --notes "Booked lesson"
```

**Add successful email:**
```bash
generate_email add-success \
  --to golf_student \
  --type follow_up \
  --subject "Following up on lesson inquiry" \
  --body "..." \
  --outcome "booked_lesson" \
  --conversion-rate 0.75
```

**Analyze patterns:**
```bash
generate_email analyze                          # All patterns
generate_email analyze --to golf_student        # Filtered
```

**Statistics:**
```bash
generate_email stats
```

### Recipient Types
- `golf_student` - Potential or current students
- `partner` - Business partners (facilities, clubs)
- `platform` - Golf tech platforms/apps
- `sponsor` - Potential sponsors
- `media` - Golf media/publications

### Email Types
- `inquiry_response` - Responding to inquiries
- `follow_up` - Following up on conversations
- `introduction` - Cold introduction/outreach
- `collaboration` - Partnership proposals
- `update` - Sharing progress/news
- `thank_you` - Thanking for meetings/opportunities

---

## 🎨 Web Dashboard

### Features

1. **Generate Tab**
   - Select recipient type and email type
   - Add context about the situation
   - Generate 3 variations instantly
   - Copy emails to clipboard

2. **Browse Tab**
   - Filter by recipient, type, variation
   - Sort by recent or best performing
   - Mark templates as used/converted
   - Copy emails directly

3. **Stats Tab**
   - Overall performance metrics
   - Conversion rates
   - Top performing templates
   - Usage analytics

4. **Learning Tab**
   - Add past successful emails
   - Analyze patterns from successful emails
   - View extracted patterns and effectiveness

### Dashboard Shortcuts

**Keyboard:**
- `Ctrl+C` - Copy selected email
- Tab through filters

**Actions:**
- Click "✓ Used" - Mark template as used
- Click "🎉 Converted" - Mark as converted (updates learning)
- Click "📋 Copy" - Copy email to clipboard

---

## 🧠 How Learning Works

### 1. Pattern Extraction

The system analyzes your successful emails and extracts:

**Structure Patterns:**
- Average email length
- Number of paragraphs
- Optimal length ranges

**Phrase Patterns:**
- High-performing keywords
- Effective terminology
- Common successful phrases

**Opening Patterns:**
- Question vs statement openings
- Personal vs direct approach
- Success rates by strategy

**CTA Patterns:**
- Question vs direct CTAs
- Soft vs urgent approach
- Conversion rates by type

### 2. Feedback Loop

1. Generate emails → stored in database
2. Mark templates as "used" when sent
3. Mark as "converted" when they get results
4. System calculates conversion rates
5. Pattern effectiveness scores update automatically
6. Future generations use improved patterns

### 3. Continuous Improvement

```
Generate → Use → Feedback → Learn → Better Generation
```

The more you use it and provide feedback, the better it gets at matching your style and what works for your audience.

---

## 🏗️ Architecture

### Components

```
email-template-generator/
├── cli/
│   └── generate_email.py      # CLI tool
├── web/
│   ├── app.py                 # Flask web server
│   └── templates/
│       └── dashboard.html     # Web UI
├── data/
│   └── templates.db           # SQLite database
├── database.py                # Database operations
├── pattern_learner.py         # Learning system
├── llama_generator.py         # LLM integration
├── test_suite.py              # Comprehensive tests
├── start_dashboard.sh         # Easy startup script
├── requirements.txt           # Dependencies
└── README.md                  # This file
```

### Database Schema

**templates** - Generated emails
- id, recipient_type, email_type, variation
- subject, body, context
- used, converted, feedback_score
- generated_at

**successful_emails** - Past successful emails for learning
- id, recipient_type, email_type
- subject, body, context
- outcome, conversion_rate
- added_at

**patterns** - Extracted patterns
- id, pattern_type, pattern_data
- effectiveness_score, usage_count
- created_at, updated_at

**performance_log** - Action tracking
- id, template_id, action, result
- timestamp

### Tech Stack

- **LLM:** Llama 3.1 8B via Ollama
- **Backend:** Python 3 + Flask
- **Database:** SQLite
- **Frontend:** Vanilla HTML/CSS/JS
- **CLI:** Click framework
- **ML:** scikit-learn (pattern analysis)

---

## 🧪 Testing

### Run Full Test Suite

```bash
python3 test_suite.py
```

Tests:
1. Database operations (CRUD, feedback, queries)
2. Pattern learning (extraction, analysis, recommendations)
3. Llama generation (all variations, all types)
4. Full workflow (generate → use → feedback → learn)
5. CLI interface (import, commands)

### Manual Testing

**Test CLI:**
```bash
./cli/generate_email.py generate \
  --to partner \
  --type collaboration \
  --context "Golf facility with simulators"
```

**Test Dashboard:**
1. Start dashboard: `./start_dashboard.sh`
2. Open http://localhost:3002
3. Generate emails in all tabs
4. Add feedback
5. Check stats

**Test Learning:**
1. Add 3-5 successful emails (via CLI or dashboard)
2. Run `generate_email analyze`
3. Generate new emails
4. Compare quality - should improve over time

---

## 📊 Performance

### Generation Speed
- **Single email:** ~3-5 seconds
- **3 variations:** ~10-15 seconds
- **With cold start:** ~15-20 seconds

### Accuracy
- Uses proven patterns from successful emails
- Matches tone consistently (formal/casual/urgent)
- Contextually relevant based on input

### Scalability
- Local LLM = no API limits
- SQLite handles 1000s of templates easily
- Can switch to larger Llama models for better quality

---

## 🔧 Configuration

### Change Llama Model

Edit `llama_generator.py`:
```python
# Default: llama3.1:8b
generator = LlamaEmailGenerator(model="llama3.1:8b")

# Larger/better: llama3.1:70b (if you have RAM)
generator = LlamaEmailGenerator(model="llama3.1:70b")

# Faster/smaller: llama3.2:3b
generator = LlamaEmailGenerator(model="llama3.2:3b")
```

### Adjust Temperature

Edit `llama_generator.py`, line ~80:
```python
options={
    'temperature': 0.7,  # 0.5 = conservative, 0.9 = creative
    'top_p': 0.9,
    'num_predict': 500   # Max tokens
}
```

### Change Database Location

Edit `database.py`:
```python
DB_PATH = '/path/to/custom/location/templates.db'
```

### Dashboard Port

Edit `web/app.py`:
```python
app.run(host='0.0.0.0', port=3002, debug=True)  # Change port here
```

---

## 🚨 Troubleshooting

### "Ollama not available"

**Problem:** Ollama server not running

**Solution:**
```bash
# Start Ollama
ollama serve

# In another terminal
ollama list  # Verify it's running
```

### "Model not found"

**Problem:** Llama model not installed

**Solution:**
```bash
ollama pull llama3.1:8b
```

### Port 3002 in use

**Solution:**
```bash
lsof -ti:3002 | xargs kill -9
./start_dashboard.sh
```

### Slow generation

**Causes:**
- First run (model loading) - normal
- Large model on slow hardware
- Low RAM

**Solutions:**
- Use smaller model: `llama3.2:3b`
- Wait for first generation to cache model
- Close other applications
- Upgrade RAM if using 70B models

### Import errors

**Solution:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Database locked

**Cause:** Multiple processes accessing DB

**Solution:**
```bash
# Close all CLI/dashboard instances
# Restart one at a time
```

---

## 🎯 Best Practices

### For Best Results

1. **Add your successful emails** - The more examples, the better
2. **Provide feedback** - Mark templates as used/converted
3. **Add context** - More context = more personalized emails
4. **Review before sending** - AI is good but not perfect
5. **Track conversions** - Update feedback to improve learning

### When to Use Each Variation

**Formal:**
- First contact with partners
- Professional inquiries
- Sponsor outreach
- Media communications

**Casual:**
- Student communications
- Follow-ups with existing contacts
- Friendly introductions
- Repeat customers

**Urgent:**
- Time-sensitive offers
- Limited availability
- Follow-ups that need response
- Event deadlines

### Adding Successful Emails

Include these details:
- Full email text (subject + body)
- What happened (outcome)
- Conversion rate if you know it
- Any special context

The more successful emails you add, the more the system learns your style and what works.

---

## 📈 Roadmap

### v1.1 (Next)
- [ ] Email history/favorites
- [ ] Template editing in dashboard
- [ ] Export templates (CSV, JSON)
- [ ] Bulk generation
- [ ] Email preview formatting

### v1.2
- [ ] A/B testing framework
- [ ] More granular patterns (time of day, etc)
- [ ] Integration with email clients
- [ ] Mobile-responsive dashboard
- [ ] Template categories/tags

### v2.0
- [ ] Multi-user support
- [ ] Team collaboration features
- [ ] Advanced analytics dashboard
- [ ] API for integrations
- [ ] Chrome extension

---

## 🤝 Contributing

This is a personal project for Ross's golf business, but feel free to:
- Report bugs
- Suggest features
- Fork and customize

---

## 📄 License

MIT - Do whatever you want with it.

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM infrastructure
- **Meta** - Llama models
- **Flask** - Web framework
- **Click** - CLI framework

---

## 📞 Support

**Issues?**
1. Check troubleshooting section
2. Run test suite: `python3 test_suite.py`
3. Check logs in terminal

**Questions?**
- Read this README fully
- Check code comments
- Experiment and learn!

---

**Built with ⚡ by Jarvis for Ross's Golf Business**

*Generate better emails. Track what works. Improve continuously.*
```

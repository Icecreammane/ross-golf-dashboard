# 🚀 Email Template Generator - Deployment Guide

## For Ross: How to Use This

---

## 🎯 What You've Got

An AI email generator that:
- **Learns your style** from past successful emails
- **Generates 3 variations** (formal/casual/urgent) for any situation
- **Gets smarter** with your feedback
- **No API costs** - runs locally with Llama
- **Both CLI + Web** - use however you prefer

---

## ⚡ Quick Start (First Time)

### 1. Install Ollama (One-Time)

```bash
# Install Ollama
brew install ollama

# Pull Llama model (takes 5-10 min, ~5GB download)
ollama pull llama3.1:8b

# Start Ollama (run this in a separate terminal, keep it running)
ollama serve
```

**Tip:** Set Ollama to auto-start on login:
- Open "System Preferences" → "Users & Groups" → "Login Items"
- Add Ollama to startup apps

### 2. Set Up Email Generator

```bash
cd ~/clawd/email-template-generator

# Install dependencies (one-time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Make scripts executable (one-time)
chmod +x start_dashboard.sh cli/generate_email.py

# Optional: Install CLI globally (one-time)
sudo ln -sf $(pwd)/cli/generate_email.py /usr/local/bin/generate_email
```

### 3. Start Dashboard

```bash
./start_dashboard.sh
```

Open in browser: **http://localhost:3002**

---

## 📱 Daily Usage

### Option A: Web Dashboard (Recommended)

1. **Start it:**
   ```bash
   cd ~/clawd/email-template-generator
   ./start_dashboard.sh
   ```

2. **Generate emails:**
   - Go to "🔮 Generate" tab
   - Select who you're emailing (student, partner, etc.)
   - Select type (inquiry response, follow-up, etc.)
   - Add context (e.g., "Student wants help with slice")
   - Click "Generate" → Get 3 variations
   - Click "📋 Copy" to use in your email client

3. **Track performance:**
   - After sending: Go to "📚 Browse" tab
   - Find the email you sent
   - Click "✓ Used"
   - If they respond/book: Click "🎉 Converted"

4. **Check stats:**
   - Go to "📊 Stats" tab
   - See what's working best
   - View conversion rates

### Option B: Command Line (Quick)

```bash
# Generate emails
generate_email generate \
  --to golf_student \
  --type inquiry_response \
  --context "Wants help with driver distance"

# List templates
generate_email list --best

# Show specific template and copy
generate_email show 42 --copy

# Mark as used/converted
generate_email feedback 42 --converted --score 5
```

---

## 🧠 Making It Smarter

### Add Your Past Successful Emails

The more successful emails you add, the better it gets!

**Via Dashboard:**
1. Go to "🧠 Learning" tab
2. Fill in a past email that got good results:
   - Who it was to
   - Subject line
   - Full email body
   - Outcome (booked_lesson, partnership, etc.)
   - Conversion rate if you know it (0.75 = 75%)
3. Click "✅ Add Successful Email"
4. Click "🧠 Analyze Patterns" to update learning

**Via CLI:**
```bash
generate_email add-success \
  --to golf_student \
  --type follow_up \
  --subject "Following up on your lesson inquiry" \
  --body "Hey [Name],

Just wanted to follow up on your interest in lessons. I have a couple spots opening up next week if you're still interested.

Let me know!

Ross" \
  --outcome "booked_lesson" \
  --conversion-rate 0.80
```

**Tip:** Add 5-10 of your best emails to start. The system will:
- Learn your tone and style
- Identify what phrases work
- Understand your typical structure
- Apply these patterns to new emails

---

## 💡 Common Scenarios

### Responding to Golf Student Inquiry

```bash
generate_email generate \
  --to golf_student \
  --type inquiry_response \
  --context "Student wants to work on putting, mentioned they play at Oak Creek"
```

### Following Up on Unanswered Inquiry

```bash
generate_email generate \
  --to golf_student \
  --type follow_up \
  --context "Inquired 2 weeks ago about lessons, haven't heard back"
```

### Reaching Out to Partner

```bash
generate_email generate \
  --to partner \
  --type collaboration \
  --context "Golf facility with new indoor simulators, want to discuss lesson program partnership"
```

### Cold Outreach to Platform

```bash
generate_email generate \
  --to platform \
  --type introduction \
  --context "Golf swing analysis app, potential integration for lesson feedback"
```

### Thank You After Meeting

```bash
generate_email generate \
  --to partner \
  --type thank_you \
  --context "Met at conference, discussed collaboration on junior golf program"
```

---

## 📊 Understanding the Output

### 3 Variations Explained

**FORMAL** - Use for:
- First contact with partners/sponsors
- Professional inquiries
- Media outreach
- Important business communications

**CASUAL** - Use for:
- Current students
- Follow-ups with people you know
- Friendly introductions
- Repeat communications

**URGENT** - Use for:
- Time-sensitive offers
- Limited availability spots
- Follow-ups that need response
- Event deadlines

**Pick the one that feels right for the situation!**

---

## 🎓 Best Practices

### 1. Always Review Before Sending
The AI is good, but not perfect. Quick proofread:
- Check recipient's name if you added it
- Verify facts/details are accurate
- Ensure tone matches your style
- Add any specific personal touches

### 2. Provide Feedback Consistently
- Mark "used" when you send
- Mark "converted" when it works
- This trains the AI to match what works for you

### 3. Add Context Details
The more context you provide, the better:
- Bad: "Follow up with student"
- Good: "Follow up with student who inquired about fixing slice, mentioned they play at Oak Creek and have upcoming tournament"

### 4. Learn from Stats
Check your stats weekly:
- Which variation converts best for you?
- Which email types perform well?
- What patterns are working?

### 5. Iterate and Improve
- Add your successful emails regularly
- Run pattern analysis monthly
- Adjust your approach based on data

---

## 🔧 Maintenance

### Keeping It Running

**Start Ollama:**
If generation fails, check Ollama is running:
```bash
ollama serve
```

**Restart Dashboard:**
If dashboard has issues:
```bash
cd ~/clawd/email-template-generator
lsof -ti:3002 | xargs kill -9  # Kill old instance
./start_dashboard.sh           # Start fresh
```

**Update Templates:**
Database grows over time. Clean old templates if needed:
```bash
# View database
sqlite3 data/templates.db
sqlite> DELETE FROM templates WHERE generated_at < date('now', '-90 days');
sqlite> .quit
```

### Backing Up Your Data

```bash
# Backup database (do this monthly)
cp data/templates.db data/templates-backup-$(date +%Y-%m-%d).db

# Or backup entire system
cd ~/clawd
tar -czf email-generator-backup-$(date +%Y-%m-%d).tar.gz email-template-generator/
```

---

## 🚨 Troubleshooting

### "Ollama not available"
**Fix:** Start Ollama in a terminal: `ollama serve`

### "Model not found"
**Fix:** Pull the model: `ollama pull llama3.1:8b`

### Slow generation
**Normal:** First generation takes 15-20 seconds (loading model)  
**After:** Should be 5-10 seconds per set of 3 emails

### Port 3002 in use
**Fix:** `lsof -ti:3002 | xargs kill -9`

### Dashboard won't start
**Fix:**
```bash
cd ~/clawd/email-template-generator
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
./start_dashboard.sh
```

---

## 📈 Workflow Example

**Day 1: Setup**
1. Install Ollama, pull Llama model
2. Install email generator
3. Add 5 of your past successful emails
4. Run pattern analysis

**Day 2-7: Usage**
1. New inquiry comes in
2. Generate 3 email variations
3. Pick the best one, personalize slightly
4. Send it
5. Mark as "used" in dashboard

**Week 2: Feedback**
1. Check which emails converted
2. Mark them as "converted"
3. System automatically updates patterns
4. Future emails improve

**Monthly: Review**
1. Check stats dashboard
2. See what's working best
3. Add more successful emails
4. Re-analyze patterns
5. Notice improvement in quality

---

## 🎯 Success Metrics

After 1 month of use, you should see:
- ✅ 50-100 templates generated
- ✅ 10-20 templates marked as used
- ✅ 3-5 conversions tracked
- ✅ Clear patterns emerging
- ✅ Better generation quality
- ✅ Time saved: 10-15 min/email → 2-3 min

---

## 🆘 Need Help?

1. **Check docs:**
   - `README.md` - Full documentation
   - `QUICK_START.md` - Fast setup
   - `BUILD_COMPLETE.md` - Technical details

2. **Run tests:**
   ```bash
   cd ~/clawd/email-template-generator
   source venv/bin/activate
   python3 test_suite.py
   ```

3. **Check logs:**
   - Dashboard errors show in terminal
   - CLI errors are self-explanatory

4. **Ask Jarvis:**
   Just ping me on Telegram: "Email generator not working" with error details

---

## 📝 Quick Reference Card

```bash
# Start dashboard
cd ~/clawd/email-template-generator && ./start_dashboard.sh

# Generate via CLI
generate_email generate --to golf_student --type inquiry_response

# List templates
generate_email list --best

# View template
generate_email show 42 --copy

# Add feedback
generate_email feedback 42 --converted --score 5

# Add successful email
generate_email add-success --to golf_student --type follow_up \
  --subject "..." --body "..." --outcome "booked_lesson"

# Check stats
generate_email stats

# Analyze patterns
generate_email analyze
```

---

**That's it! Start generating better emails today.** 🚀

Questions? Just ask. I'm here to help.

- Jarvis

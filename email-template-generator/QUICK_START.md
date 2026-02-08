# ⚡ Email Template Generator - Quick Start

## 30-Second Setup

```bash
cd ~/clawd/email-template-generator

# 1. Install dependencies (one-time)
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Start dashboard
./start_dashboard.sh
```

Open: **http://localhost:3002**

---

## CLI Quick Commands

```bash
# Make CLI executable (one-time)
chmod +x cli/generate_email.py

# Generate emails
./cli/generate_email.py generate \
  --to golf_student \
  --type inquiry_response

# List templates
./cli/generate_email.py list

# Show stats
./cli/generate_email.py stats

# Help
./cli/generate_email.py --help
```

---

## Test Everything

```bash
python3 test_suite.py
```

Should see: ✅ ALL TESTS PASSED

---

## Common Scenarios

### Respond to Golf Student Inquiry

```bash
./cli/generate_email.py generate \
  --to golf_student \
  --type inquiry_response \
  --context "Wants help with driver slice, mentioned playing at Oak Creek"
```

### Follow Up with Partner

```bash
./cli/generate_email.py generate \
  --to partner \
  --type collaboration \
  --context "Golf facility with indoor simulators, interested in joint lessons"
```

### Cold Outreach to Platform

```bash
./cli/generate_email.py generate \
  --to platform \
  --type introduction \
  --context "Golf app focused on swing analysis, potential integration opportunity"
```

---

## Web Dashboard Workflow

1. **Generate** - Create 3 email variations
2. **Copy** - Click "📋 Copy" to use in email client
3. **Mark Used** - Click "✓ Used" after sending
4. **Mark Converted** - Click "🎉 Converted" when you get results
5. **Check Stats** - See what's working best

---

## Add Your Successful Emails

**Via Dashboard:**
1. Go to "🧠 Learning" tab
2. Fill in your past successful email
3. Click "✅ Add Successful Email"
4. Click "🧠 Analyze Patterns"

**Via CLI:**
```bash
./cli/generate_email.py add-success \
  --to golf_student \
  --type follow_up \
  --subject "Quick follow-up on lesson inquiry" \
  --body "Hey [Name], just wanted to check if you're still interested..." \
  --outcome "booked_lesson" \
  --conversion-rate 0.80
```

---

## Troubleshooting

**"Ollama not available"**
```bash
ollama serve
# Then in another terminal:
ollama pull llama3.1:8b
```

**Port 3002 in use**
```bash
lsof -ti:3002 | xargs kill -9
./start_dashboard.sh
```

**Import errors**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

---

## What Makes This Special?

✅ **No API costs** - Runs locally with Llama  
✅ **Learns your style** - Gets better with feedback  
✅ **Pattern matching** - Uses what works for you  
✅ **3 variations** - Pick the right tone  
✅ **Tracks performance** - Know what converts  
✅ **Both CLI + Web** - Use however you want  

---

## Next Steps

1. Generate 5-10 emails with different contexts
2. Add 3-5 of your past successful emails
3. Run pattern analysis
4. Use feedback to improve

The system gets smarter the more you use it! 🧠

---

**Full docs:** See README.md  
**Support:** Run test_suite.py if issues

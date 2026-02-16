# ⚡ QUICKSTART: Triple Threat Features

**Ready to use NOW. Here's how to activate everything.**

---

## 🌅 1. MORNING BRIEF (5 minutes to setup)

### Activate It:
```bash
# Setup daily 7:30am delivery
bash ~/clawd/scripts/setup_cron.sh

# Test it right now
python3 ~/clawd/scripts/morning_brief_v2.py
```

### What You'll Get:
Every morning at 7:30am CST, Telegram message with:
- Weather + clothing recommendation
- Calendar events (when integrated)
- Yesterday's fitness performance
- Top 3 job matches
- NFL Draft flight prices
- Link to Mission Control

### Where To Find It:
- **Telegram:** Delivered automatically
- **File:** `logs/morning-brief-latest.json`
- **Outbox:** `outbox/morning-brief-*.txt` (if Telegram fails)

---

## 💼 2. AUTO-JOB APPLICATIONS (Ready NOW)

### Check What's Ready:
```bash
# View pending applications
python3 ~/clawd/scripts/auto_job_apply.py pending
```

**YOU HAVE 3 APPLICATIONS READY RIGHT NOW:**
1. ✅ Nestlé Purina PetCare - Senior Food Scientist (Tampa) - 10/10 match
2. ✅ Procter & Gamble - Senior Product Development Scientist (Tampa) - 10/10 match
3. ✅ Hill's Pet Nutrition - R&D Scientist (Miami) - 10/10 match

### Review & Submit:
```bash
# Read any application
cat ~/clawd/applications/Nestlé_Purina_PetCare_20260215.json | jq .cover_letter -r

# Or open in editor
code ~/clawd/applications/
```

### Each Application Includes:
- ✅ Custom cover letter (company-specific)
- ✅ Pre-filled form data (copy/paste ready)
- ✅ Job details and URL
- ✅ Your resume path

### How To Apply:
1. Open application JSON file
2. Read cover letter (customize if desired)
3. Go to job URL
4. Copy/paste:
   - Cover letter
   - Form data (name, email, phone, etc.)
5. Attach resume (update path in script if needed)
6. Submit!

### Generate More Applications:
```bash
# After running job scan
python3 ~/clawd/scripts/job_hunter.py scan
python3 ~/clawd/scripts/auto_job_apply.py generate
```

---

## 🎤 3. VOICE CONTROL (Works NOW)

### How To Use:
**Send Telegram voice messages - they'll be processed automatically**

### Fitness Commands:
- "Log bench press 185 pounds 8 reps"
- "I just ate chicken breast 300 calories"
- "Log 2 eggs for breakfast"
- "I did 50 push-ups"

### Life Admin:
- "Add eggs to shopping list"
- "Add milk and bread to grocery list"
- "Need to buy protein powder"

### Queries:
- "What's my calorie target?"
- "Show my fitness stats"
- "What's on my calendar?"

### Test Voice Router:
```bash
# Test from command line
python3 ~/clawd/scripts/voice_command_router.py "Log bench press 185 pounds 8 reps"
python3 ~/clawd/scripts/voice_command_router.py "Add milk to shopping list"

# Or run full test suite
bash ~/clawd/scripts/test_voice_commands.sh
```

### Where Data Goes:
- Workouts → `data/fitness_data.json`
- Nutrition → `data/fitness_data.json`
- Shopping list → `data/shopping_list.json`
- Command log → `logs/voice-commands.log`

---

## 🔄 RUN EVERYTHING TOGETHER

### Daily Automation (Morning Brief + Job Apps):
```bash
bash ~/clawd/scripts/daily_automation.sh
```

This runs:
1. Morning brief generation
2. Job application generation for new matches
3. Summary report

**Cron job runs this automatically at 7:30am daily.**

---

## 📂 IMPORTANT FILES

### Scripts:
- `scripts/morning_brief_v2.py` - Morning brief generator
- `scripts/auto_job_apply.py` - Job application generator
- `scripts/voice_command_router.py` - Voice command handler
- `scripts/daily_automation.sh` - Runs everything together

### Data:
- `data/job_matches.json` - Job matches from scanner
- `data/applications.json` - Application tracker
- `data/fitness_data.json` - Fitness logs
- `data/flight_prices.json` - Flight price history

### Applications:
- `applications/*.json` - Draft job applications (REVIEW THESE!)

### Logs:
- `logs/morning-brief.log` - Morning brief execution log
- `logs/voice-commands.log` - Voice command history
- `logs/daily-automation.log` - Daily automation log

---

## ⚠️ IMPORTANT NOTES

### Resume:
Update your resume path in `scripts/auto_job_apply.py`:
```python
RESUME_PATH = Path.home() / "Documents" / "resume.pdf"
```

### Contact Info:
Update your real contact info in `scripts/auto_job_apply.py`:
```python
PROFILE = {
    "email": "your.real.email@gmail.com",  # UPDATE THIS
    "phone": "(615) 555-0123",  # UPDATE THIS
    ...
}
```

### Safety:
- ✅ Job applications NEVER auto-submit
- ✅ Always saved as drafts first
- ✅ You review before applying
- ✅ Voice commands log everything

---

## 🚀 FIRST STEPS (Do This Now)

### 1. Setup Morning Brief:
```bash
bash ~/clawd/scripts/setup_cron.sh
```

### 2. Review Your 3 Ready Applications:
```bash
ls ~/clawd/applications/
cat ~/clawd/applications/Nestlé_Purina_PetCare_20260215.json | jq .cover_letter -r
```

### 3. Update Your Contact Info:
```bash
code ~/clawd/scripts/auto_job_apply.py
# Update PROFILE section with real email/phone
```

### 4. Test Voice Commands:
Send a voice message in Telegram:
- "Add test item to shopping list"

---

## 💪 YOU'RE READY

**Morning brief:** Activates at 7:30am tomorrow  
**Job applications:** 3 ready to submit right now  
**Voice control:** Already listening  

**GO APPLY FOR THOSE JOBS.**
**LET'S GET YOU TO FLORIDA.**

🔥

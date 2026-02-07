# Voice Brief Setup Guide

**Goal:** Audio morning brief that plays at 7:30am  
**Time to set up:** 15 minutes  
**Cost:** ~$5-10/month (ElevenLabs Pro)

---

## 🎯 What You Get

**Instead of reading:**
5-minute audio briefing you listen to while getting ready

**Contains:**
- Overnight system status
- Night shift results (tweets, opportunities, insights)
- Today's priorities
- Calendar overview
- Fitness tracking update
- Goals progress

**Voice:** Deep, authoritative (like Onyx from OpenAI, or JARVIS from Iron Man)

---

## 📋 Setup Options

### Option 1: ElevenLabs (Best Quality)

**Pros:**
- Professional voice cloning
- Natural-sounding
- Customizable voice
- Can clone your own voice

**Cons:**
- Costs ~$5-10/month
- Requires API setup

**Steps:**

1. **Sign up:** https://elevenlabs.io
2. **Get API key:** 
   - Go to Profile → API Keys
   - Generate new key
   - Copy it

3. **Add to environment:**
```bash
nano ~/clawd/.env

# Add:
ELEVENLABS_API_KEY=your_api_key_here

# Save: Ctrl+X, Y, Enter
```

4. **Test:**
```bash
python3 ~/clawd/scripts/voice_brief.py
```

5. **Should generate:** `~/clawd/voice-briefs/morning-brief-YYYYMMDD.mp3`

### Option 2: OpenAI TTS (Good, Cheaper)

**Pros:**
- Cheaper (~$1-2/month)
- Good quality
- "Onyx" voice available

**Cons:**
- Less customization
- Slightly robotic

**Already have OpenAI API?** Can use that instead.

**Modify voice_brief.py to use OpenAI TTS instead.**

### Option 3: macOS Built-in (Free)

**Pros:**
- Free
- No setup

**Cons:**
- Robotic voice
- Lower quality

**Use:**
```bash
say -v Alex "$(cat ~/clawd/morning-briefs/latest.txt)" -o ~/clawd/voice-briefs/brief.aiff
```

---

## 🤖 Auto-Play Setup

**Make it play at 7:30am automatically:**

### iOS (iPhone)

**Option A: Shortcuts app**
1. Open Shortcuts app
2. Create automation: "Time of Day" → 7:30am
3. Add action: "Play Sound" → select brief file (stored in iCloud)
4. Done

**Option B: Telegram bot**
- Voice brief sends as Telegram voice message at 7:30am
- You just tap play

### macOS (if you're home)

Add to morning brief script:
```bash
# Play audio at 7:30am
afplay ~/clawd/voice-briefs/morning-brief-$(date +%Y%m%d).mp3
```

---

## 🎙️ Voice Customization

**ElevenLabs voice options:**
- **Onyx-style:** Deep, authoritative, professional
- **Clone your voice:** Upload 1 min of your voice
- **British JARVIS:** Paul Bettany style
- **Custom:** Design your perfect AI voice

**My recommendation:** Start with their "Adam" or "Antoni" voice (deep, clear). Adjust stability/similarity settings in the script.

---

## 📊 What It Sounds Like

**Example script:**

> "Good morning, Ross. This is your brief for Friday, February seventh.
>
> Let me catch you up on what happened overnight and what's ahead today.
>
> SYSTEM STATUS: Your AI operations center ran successfully through the night. All systems operational.
>
> NIGHT SHIFT RESULTS: Twenty tweet ideas generated. Reddit scanner found three high-priority opportunities.
>
> TODAY'S PRIORITIES: 
> One: Review and schedule tweets for next week.
> Two: Check Reddit opportunities - two posts need responses within 6 hours.
> Three: FitTrack development ready to prototype.
>
> That's your brief. Now go build something great."

**Length:** 3-5 minutes  
**Pace:** Conversational, not rushed  
**Tone:** Supportive but direct

---

## 🚀 Integration with Morning Brief

Once working, update `scripts/generate-morning-brief.py`:

```python
# At the end:
os.system("python3 ~/clawd/scripts/voice_brief.py")
```

**Now every morning brief generates both:**
- HTML file (for reading)
- MP3 file (for listening)

---

## 💡 Pro Tips

**Use SSML tags for better pacing:**
```xml
<break time="1s"/> <!-- Pause 1 second -->
<emphasis level="strong">Important</emphasis> <!-- Emphasize -->
<prosody rate="slow">Slower</prosody> <!-- Adjust speed -->
```

**Experiment with voice settings:**
- Stability: 0.5 = natural variation
- Similarity boost: 0.75 = matches voice closely
- Adjust until it sounds right to YOU

---

## 📁 File Structure

```
voice-briefs/
  morning-brief-20260207.mp3   ← Today's audio
  brief-script-20260207.txt    ← Generated script
  latest.mp3                   ← Symlink to most recent
```

---

## 🎯 Current Status

**Right now:** Script generation works  
**Audio:** Requires ElevenLabs API key  
**Auto-play:** Manual for now

**Takes 15 minutes to fully set up when you're ready.**

---

*For now, you can read the brief. When you want audio, follow this guide. It's a game-changer for your morning routine.*

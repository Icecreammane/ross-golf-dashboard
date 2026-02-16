# Smart Email Triage

**AI-powered email classification and alerts using Gmail API + Ollama**

## Features

- 🤖 **AI classification** using local Ollama (FREE!)
- 🔴 **Urgent detection** (boss, client, deadlines)
- 🟡 **Action tracking** (needs response within 24h)
- 🔵 **FYI filtering** (informational only)
- ⚫ **Auto-archive spam** (promotional, newsletters)
- 📱 **Telegram alerts** for urgent emails
- 📊 **Daily summary** reports

## Quick Start

### 1. Install Dependencies

```bash
pip3 install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### 2. Setup Gmail API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project: "Jarvis Email Triage"
3. Enable **Gmail API**
4. Create **OAuth 2.0 credentials** (Desktop app)
5. Download credentials as `credentials.json`
6. Place at: `~/clawd/credentials/gmail_credentials.json`

### 3. Authenticate

```bash
python3 ~/clawd/scripts/email_triage.py --setup
```

This opens a browser to authorize Gmail access.

### 4. Check Inbox

```bash
python3 ~/clawd/scripts/email_triage.py --check
```

### 5. Setup Hourly Checks

Add to crontab:

```bash
# Check inbox every hour
0 * * * * python3 ~/clawd/scripts/email_triage_daemon.py >> ~/clawd/logs/email-triage.log 2>&1
```

## Usage

### Manual Inbox Check

```bash
python3 ~/clawd/scripts/email_triage.py --check
```

**Output:**
```
[2024-02-15 10:30:00] Checking inbox...
📧 Found 12 new emails
   Classifying: RE: Budget approval needed...
   Classifying: Your weekly newsletter...
   Classifying: Meeting reminder for tomorrow...

📊 Classification Summary:
   🔴 Urgent: 2
   🟡 Action Required: 4
   🔵 FYI: 3
   ⚫ Spam: 3

🚨 URGENT EMAIL ALERTS:

   🔴 RE: Budget approval needed by EOD
      From: Nicole <nicole@company.com>
      Preview: Hi, I need your approval on the Q1 budget before 5pm today...
      Link: https://mail.google.com/mail/u/0/#inbox/abc123

   🔴 Client issue - immediate response needed
      From: John Smith <john@client.com>
      Preview: We're experiencing downtime and need your help ASAP...
      Link: https://mail.google.com/mail/u/0/#inbox/def456

🗑️  Auto-archiving 3 spam emails...
```

### Daily Summary

```bash
python3 ~/clawd/scripts/email_triage.py --summary
```

**Output:**
```
📊 DAILY EMAIL SUMMARY - 2024-02-15

Total: 47 emails
   🔴 Urgent: 3
   🟡 Action Required: 12
   🔵 FYI: 24
   ⚫ Spam: 8

🔴 URGENT EMAILS:
   • Budget approval needed by EOD
     From: Nicole <nicole@company.com>
   • Client issue - immediate response needed
     From: John Smith <john@client.com>

🟡 ACTION REQUIRED:
   • Feedback on draft proposal
     From: Marketing Team <team@company.com>
   • Schedule meeting for next week
     From: Sarah Johnson <sarah@company.com>
```

## How It Works

### 1. AI Classification (Ollama)

Uses local Ollama with `qwen2.5` model:

```python
classify_email_with_ollama(subject, sender, body_preview)
```

**Categories:**
- 🔴 **Urgent**: Boss, client, deadline-related
- 🟡 **Action Required**: Needs response within 24h
- 🔵 **FYI**: Informational, no action needed
- ⚫ **Spam/Promo**: Auto-archive

### 2. Fallback Rules

If Ollama fails, uses rule-based classification:

**Urgent keywords:**
- urgent, asap, immediate, deadline, today
- emergency, critical, time-sensitive

**Spam keywords:**
- unsubscribe, promotional, sale, newsletter
- marketing, advertisement

### 3. Auto-Archive Spam

Spam emails are automatically moved out of inbox:

```python
service.users().messages().modify(
    userId='me',
    id=email_id,
    body={'removeLabelIds': ['INBOX']}
)
```

### 4. Telegram Alerts

Urgent emails trigger immediate Telegram notifications to Ross.

## Data Storage

Stored in `data/email_classifications.json`:

```json
{
  "emails": [
    {
      "id": "abc123",
      "subject": "Budget approval needed",
      "sender": "Nicole <nicole@company.com>",
      "date": "Thu, 15 Feb 2024 10:30:00",
      "category": "urgent",
      "body_preview": "Hi, I need your approval...",
      "classified_at": "2024-02-15T10:31:00",
      "gmail_url": "https://mail.google.com/mail/u/0/#inbox/abc123"
    }
  ],
  "last_check": "2024-02-15T10:31:00",
  "stats": {
    "urgent": 3,
    "action_required": 12,
    "fyi": 24,
    "spam": 8
  }
}
```

## Gmail API Setup (Detailed)

### Step 1: Create Google Cloud Project

1. Visit: https://console.cloud.google.com/
2. Click "New Project"
3. Name: "Jarvis Email Triage"
4. Click "Create"

### Step 2: Enable Gmail API

1. Go to "APIs & Services" > "Library"
2. Search for "Gmail API"
3. Click "Enable"

### Step 3: Create OAuth Credentials

1. Go to "APIs & Services" > "Credentials"
2. Click "Create Credentials" > "OAuth 2.0 Client ID"
3. Configure consent screen:
   - User Type: External
   - App name: "Jarvis Email Triage"
   - User support email: your email
   - Authorized domains: (leave blank)
   - Scopes: Add Gmail API scopes
4. Create OAuth Client ID:
   - Application type: Desktop app
   - Name: "Jarvis Desktop Client"
5. Download credentials as JSON

### Step 4: Place Credentials

```bash
mkdir -p ~/clawd/credentials
mv ~/Downloads/credentials.json ~/clawd/credentials/gmail_credentials.json
```

### Step 5: Authenticate

```bash
python3 ~/clawd/scripts/email_triage.py --setup
```

A browser will open. Sign in and authorize.

## Customization

### Adjust Urgency Keywords

Edit `email_triage.py`:

```python
URGENT_KEYWORDS = [
    'urgent', 'asap', 'immediate', 'deadline',
    'your_boss_name', 'your_client_name',
]
```

### Change Classification Model

Using different Ollama model:

```python
result = subprocess.run(
    ['ollama', 'run', 'llama2', prompt],  # Change model here
    ...
)
```

### Disable Auto-Archive

Comment out the auto-archive section in `email_triage.py`.

## Integration with Jarvis

Ask Jarvis:

```
"Check my email"
"Any urgent emails?"
"Give me today's email summary"
```

Jarvis will run the triage and report back!

## Troubleshooting

### "Gmail credentials not found"
**Solution:** Place credentials at `~/clawd/credentials/gmail_credentials.json`

### "Authentication failed"
**Solution:** Re-authenticate:
```bash
rm ~/clawd/credentials/gmail_token.pickle
python3 ~/clawd/scripts/email_triage.py --setup
```

### "Ollama classification failed"
**Solution:** Check Ollama is running:
```bash
ollama list
ollama pull qwen2.5  # If model not found
```

### No emails showing
**Solution:** Check Gmail API permissions include `gmail.readonly` and `gmail.modify`

## The Pitch

> "I never check email manually anymore. My AI flags urgent stuff, drafts responses for common emails, and filters out noise. I only see what matters."

Show your friends:
- AI classifies every email automatically
- Urgent emails = instant Telegram alert
- Spam auto-archived (never see it)
- Daily summary of what actually matters

**This is inbox zero, automated.**

## Future Enhancements

- [ ] Draft response generation (using Ollama)
- [ ] Smart reply suggestions
- [ ] Meeting detection + calendar integration
- [ ] Email thread summarization
- [ ] Sender importance learning
- [ ] Follow-up reminders
- [ ] VIP sender priority
- [ ] Custom classification rules

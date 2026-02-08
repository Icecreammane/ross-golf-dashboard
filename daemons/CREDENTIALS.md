# Twitter API Credentials Setup

You need Twitter API credentials to run the daemon. Here's how to get them.

---

## Quick Setup

Add these lines to `/Users/clawdbot/clawd/.env`:

```bash
# Twitter API Credentials (X API)
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
```

---

## How to Get Twitter API Credentials

### Step 1: Apply for Twitter Developer Account

1. Go to https://developer.twitter.com/en/portal/petition/essential/basic-info
2. Sign in with Ross's Twitter account (@_icecreammane)
3. Apply for **Elevated** access (recommended for DM functionality)
   - Select "Making a bot" or "Building a tool for yourself"
   - Describe: "Personal automation tool to monitor mentions and opportunities"
4. Wait for approval (usually instant for Elevated access)

### Step 2: Create a New App

1. Go to https://developer.twitter.com/en/portal/dashboard
2. Click "Create Project" or use existing project
3. Give it a name: "Ross Twitter Monitor"
4. App use case: "Making a bot"

### Step 3: Generate Keys and Tokens

1. In your app settings, go to "Keys and tokens" tab
2. Click "Generate" for:
   - **API Key and Secret** (Consumer Keys)
   - **Access Token and Secret**
   - **Bearer Token**
3. Copy each value immediately (they're only shown once!)

### Step 4: Set Permissions

1. In app settings, go to "User authentication settings"
2. Set up OAuth 1.0a:
   - App permissions: **Read and write and Direct message**
   - Type of App: **Web App**
   - Callback URL: `http://localhost:3000` (required but not used)
   - Website URL: Your website or `http://localhost`
3. Save settings

### Step 5: Add to .env File

Edit `/Users/clawdbot/clawd/.env` and add:

```bash
# Twitter API Credentials
TWITTER_API_KEY=abc123xyz...
TWITTER_API_SECRET=def456uvw...
TWITTER_ACCESS_TOKEN=789012345-abc...
TWITTER_ACCESS_SECRET=ghi789rst...
TWITTER_BEARER_TOKEN=AAAAAAAAAA...
```

**Important:** Never commit this file to git! It's already in `.gitignore`.

---

## Alternative: Store in 1Password

For better security, store credentials in 1Password:

```bash
# Create item in 1Password
op item create \
  --category="API Credential" \
  --title="Twitter API - Ross Monitor" \
  --vault="Private" \
  api_key=YOUR_API_KEY \
  api_secret=YOUR_API_SECRET \
  access_token=YOUR_ACCESS_TOKEN \
  access_secret=YOUR_ACCESS_SECRET \
  bearer_token=YOUR_BEARER_TOKEN
```

Then retrieve when needed:
```bash
# Get specific field
op item get "Twitter API - Ross Monitor" --fields api_key

# Or export all to .env format
op item get "Twitter API - Ross Monitor" --format json | \
  jq -r '.fields[] | "TWITTER_\(.label | ascii_upcase)=\(.value)"' >> .env
```

---

## Verify Credentials

Test that credentials work:

```bash
cd /Users/clawdbot/clawd/daemons
python3 test_twitter_daemon.py
```

You should see:
```
✅ TWITTER_API_KEY: abc123xyz...
✅ TWITTER_API_SECRET: def456uvw...
✅ TWITTER_ACCESS_TOKEN: 789012345-...
✅ TWITTER_ACCESS_SECRET: ghi789rst...
✅ Successfully authenticated as @_icecreammane
```

---

## Troubleshooting

### "Authentication failed: 401 Unauthorized"
- Double-check credentials are copied correctly (no extra spaces)
- Verify app has correct permissions (Read + Write + DMs)
- Regenerate tokens if needed

### "DM access requires elevated API access"
- This is normal for Basic access tier
- Daemon will still work for mentions
- Apply for Elevated access for DM monitoring

### "Rate limit exceeded"
- Twitter has rate limits (900 requests per 15 minutes for mentions)
- Daemon automatically waits when rate limited
- Running every 15 minutes stays well within limits

---

## Security Best Practices

1. ✅ Never share credentials publicly
2. ✅ Use environment variables (not hardcoded)
3. ✅ Keep `.env` in `.gitignore`
4. ✅ Rotate credentials every 90 days
5. ✅ Use 1Password for secure storage
6. ✅ Set app permissions to minimum required

---

## Rate Limits (Elevated Access)

| Endpoint | Limit |
|----------|-------|
| User mentions | 450 requests / 15 min |
| Direct messages | 300 requests / 15 min |
| User lookup | 900 requests / 15 min |

Running every 15 minutes = 1 request per endpoint = well within limits ✅

---

**Questions?** Check Twitter Developer Docs: https://developer.twitter.com/en/docs

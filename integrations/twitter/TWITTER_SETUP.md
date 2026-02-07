# Twitter Automation Setup

Complete setup in **5 minutes**. Daily content + engagement on autopilot.

---

## Step 1: Create Twitter Developer Account (2 minutes)

1. **Go to Twitter Developer Portal:** https://developer.twitter.com
2. **Sign up for developer account:**
   - Use your FitTrack Twitter account
   - Select "Building tools for Twitter users"
   - Describe project: "Automated posting and engagement for fitness app"
3. **Create a project:**
   - Name: "FitTrack Automation"
   - Use case: "Exploring the API"
   - App name: "FitTrack Bot"

---

## Step 2: Get API Credentials (2 minutes)

1. **In your app settings, generate:**
   - API Key
   - API Secret
   - Bearer Token
   
2. **Under "User authentication settings":**
   - Enable OAuth 1.0a
   - Set app permissions to "Read and write"
   - Generate Access Token & Secret

3. **Copy all 5 credentials:**
   - API Key
   - API Secret
   - Bearer Token
   - Access Token
   - Access Token Secret

---

## Step 3: Configure Environment (30 seconds)

Add to `.env`:

```bash
# Twitter API Credentials
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_SECRET=your_access_token_secret_here
```

---

## Step 4: Install Dependencies (30 seconds)

```bash
pip install tweepy python-dotenv
```

---

## Step 5: Test Authentication (30 seconds)

```bash
cd integrations/twitter
python twitter_bot.py
```

**Expected output:**
```
✅ Authenticated as @YourTwitterHandle
```

---

## Step 6: Review Tweet Queue (30 seconds)

Open `tweet_queue.json` - 30 pre-written tweets ready to go!

**Categories:**
- Value propositions
- Build in public updates
- Fitness tips
- Launch countdown
- Product updates
- Testimonials

**Customize:** Edit any tweets to match your voice!

---

## Step 7: Post First Tweet (30 seconds)

```bash
python twitter_bot.py
# Choose option 1: Post from queue
```

Your first tweet is live! 🚀

---

## Step 8: Automated Posting (Optional - 3 minutes)

### Daily Tweet Posting

Add to crontab (posts 1 tweet daily at 10 AM):

```bash
crontab -e

# Add this line:
0 10 * * * cd /path/to/integrations/twitter && python -c "from twitter_bot import TwitterBot; TwitterBot().post_from_queue()"
```

### Auto-Engagement (Run twice daily)

```bash
# 11 AM and 4 PM engagement cycles
0 11,16 * * * cd /path/to/integrations/twitter && python auto_engage.py
```

### Monitoring (Every hour)

```bash
# Check for mentions and opportunities
0 * * * * cd /path/to/integrations/twitter && python engagement_monitor.py
```

---

## How It Works

### Tweet Bot (`twitter_bot.py`)

**Features:**
- Posts from pre-written queue
- Tracks what's been posted
- Likes relevant content
- Replies to mentions
- Logs all engagement

**Usage:**
```python
from twitter_bot import TwitterBot

bot = TwitterBot()
bot.authenticate()

# Post next tweet from queue
bot.post_from_queue()

# Auto-engage with fitness content
bot.auto_engage(keywords=['macro tracking', 'fitness app'])

# Search mentions
mentions = bot.search_mentions('FitTrack')
```

### Engagement Monitor (`engagement_monitor.py`)

**Monitors:**
- FitTrack mentions
- Competitor discussions
- Macro tracking questions

**Identifies opportunities:**
- High priority: Direct mentions → Reply with thanks
- Medium priority: Questions → Reply with helpful answer
- Low priority: General content → Like

**Output:** Saves opportunities to `engagement_opportunities.json`

### Auto-Engage (`auto_engage.py`)

**Smart engagement:**
- Loads opportunities from monitor
- Filters by priority
- Engages automatically (likes + replies)
- Rate limit protection
- Logs all actions

**Safety limits:**
- Max 10 likes per hour
- Max 3 replies per hour
- Max 50 total per day

---

## Tweet Queue Management

### Adding New Tweets

Edit `tweet_queue.json`:

```json
{
  "text": "Your tweet text here",
  "day": 25,
  "category": "your_category",
  "posted": false
}
```

### Categories

- `value_prop` - Product value propositions
- `build_in_public` - Transparent updates
- `educational` - Fitness/nutrition tips
- `launch_countdown` - Pre-launch hype
- `testimonial` - User feedback
- `metrics` - Growth numbers
- `product_update` - New features

### Checking Queue Status

```bash
python -c "from twitter_bot import TwitterBot; bot = TwitterBot(); queue = bot.load_tweet_queue(); print(f'Posted: {sum(1 for t in queue if t[\"posted\"])} / {len(queue)}')"
```

---

## Customization

### Adjust Engagement Keywords

Edit `twitter_bot.py`:

```python
keywords = [
    'macro tracking',
    'fitness app',
    'nutrition tracking',
    'your custom keywords'
]
```

### Change Posting Schedule

Adjust cron times:
```bash
# Post at 2 PM instead of 10 AM
0 14 * * * cd /path/to/integrations/twitter && python -c "..."

# Post twice daily
0 10,18 * * * cd /path/to/integrations/twitter && python -c "..."
```

### Reply Templates

Edit `engagement_monitor.py` → `get_reply_template()`:

```python
templates = {
    'reply_thanks': "Your custom thank you message",
    'reply_helpful': "Your custom helpful reply",
}
```

---

## Monitoring Performance

### View Engagement Stats

```bash
python twitter_bot.py
# Choose option 4: View engagement stats
```

**Shows:**
- Likes given (last 7 days)
- Replies sent (last 7 days)
- Tweets posted (last 7 days)

### Check Opportunities

```bash
python engagement_monitor.py
```

Shows latest mentions, questions, and competitor discussions.

### Engagement Log

View full history:
```bash
cat engagement_log.json
```

---

## Safety Features

### Dry Run Mode

Test auto-engagement without actually posting:

```bash
python auto_engage.py --dry-run
```

Shows what WOULD happen without taking action.

### Rate Limiting

Built-in delays between actions:
- 2-7 seconds between likes
- 5-10 seconds between replies
- Respects Twitter API limits

### Manual Review

High-priority replies are suggested but NOT auto-sent. Review in `engagement_opportunities.json` and send manually if needed.

---

## Troubleshooting

### "Authentication failed"
- Verify all 5 credentials in `.env`
- Check Twitter Developer Portal for errors
- Make sure app has "Read and write" permissions

### "Rate limit exceeded"
- Twitter has strict limits (300 tweets per 3 hours)
- Reduce posting frequency
- Wait and try again

### "Duplicate tweet detected"
- Twitter blocks identical tweets within 24h
- Add unique elements: timestamps, emojis, variations
- Don't repeat the same tweet too quickly

### Tweets not posting from queue
- Check `tweet_queue.json` format is valid JSON
- Verify tweets are marked `"posted": false`
- Look for error messages in terminal

---

## Advanced Features

### Thread Posting

Post Twitter threads:

```python
bot = TwitterBot()
bot.authenticate()

# Post thread
tweet1_id = bot.post_tweet("1/ Thread about macro tracking...")
tweet2_id = bot.client.create_tweet(
    text="2/ Here's how to calculate your macros...",
    in_reply_to_tweet_id=tweet1_id
)
```

### Scheduled Tweets

Post at specific time:

```python
from datetime import datetime
import time

target_time = datetime(2024, 1, 15, 10, 0)  # Jan 15, 10 AM
while datetime.now() < target_time:
    time.sleep(60)

bot.post_from_queue()
```

### Image Tweets

Upload images (requires tweepy v1.1 API):

```python
media = bot.api.media_upload('fittrack-screenshot.png')
bot.client.create_tweet(text="Check out FitTrack!", media_ids=[media.media_id])
```

---

## Best Practices

✅ **Personalize pre-written tweets**
- Add your voice
- Include real metrics
- Be authentic

✅ **Engage authentically**
- Don't spam
- Provide real value
- Build relationships

✅ **Monitor your mentions**
- Reply to users quickly
- Thank people for sharing
- Address concerns promptly

✅ **Track what works**
- Note which tweets get engagement
- Double down on successful topics
- Iterate and improve

❌ **Don't:**
- Auto-follow everyone
- Spam hashtags
- Reply with generic messages
- Over-automate (stay human!)

---

## Growth Strategy

### Week 1-2: Foundation
- Post daily value content
- Engage with 5-10 tweets daily
- Build presence

### Week 3-4: Consistency
- Continue daily posts
- Reply to all mentions
- Share user wins

### Month 2+: Scale
- Increase posting to 2x daily
- More engagement
- Thread series
- Community building

**Goal:** 1,000 followers in 90 days through authentic, valuable content.

---

## Next Steps

✅ **Done!** Twitter automation is ready.

**Daily workflow:**
1. Queue posts automatically (10 AM)
2. Auto-engagement runs (11 AM, 4 PM)
3. Monitor checks hourly
4. You review opportunities & reply manually to important ones

**Result:**
- Consistent Twitter presence
- Growing audience
- More users discovering FitTrack
- Time saved: 5-10 hours per week

**Time to activation:** 5 minutes ⚡  
**Tweets per month:** 30+ scheduled 📝  
**Engagement:** Automated + authentic 🤖  
**Growth:** Predictable and sustainable 📈

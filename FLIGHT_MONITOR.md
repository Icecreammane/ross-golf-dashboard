# ✈️ NFL Draft Flight Monitor

**Automated price tracking for BNA → PIT, April 23-27, 2025**

---

## 🚀 Quick Start

### Check Current Prices
```bash
python3 scripts/flight_monitor.py check
```

### View Latest Report
```bash
python3 scripts/flight_monitor.py report
```

---

## 🎯 What It Monitors

**Route:** Nashville (BNA) → Pittsburgh (PIT)  
**Event:** NFL Draft  
**Dates:** April 23-27, 2025

### Date Combinations Tracked
- **Depart April 23** → Return April 26
- **Depart April 23** → Return April 27
- **Depart April 24** → Return April 26
- **Depart April 24** → Return April 27

### Airlines Monitored
- Southwest
- Delta
- American
- United

---

## 🚨 Alert System

### Price Thresholds
- **<$250** - 🔥 GREAT DEAL - Book now!
- **<$300** - 👍 GOOD DEAL - Consider booking
- **>$300** - ⏳ WAIT - Keep monitoring

### Price Drop Alerts
- **>$20 drop** - Notification sent immediately
- **New lowest price** - Alert with booking link

---

## 📊 What You Get

### Daily Report Includes:
1. **Best deal right now**
   - Cheapest option
   - Airline, stops, duration
   - Direct booking link
   - Price evaluation

2. **All options compared**
   - Every date combination
   - Sorted by price
   - Stops and duration

3. **Price trends** (after a few days)
   - Current vs. average
   - Lowest/highest seen
   - Trend direction

---

## 📈 Sample Report

```
# ✈️ NFL Draft Flight Monitor - 2025-02-13 14:30

Route: BNA → PIT
Event: NFL Draft, April 23-27, 2025

## 🚨 ALERTS
- 🔽 Price dropped $22 for 2025-04-23 → 2025-04-26
  Was: $287, Now: $265

## 💰 BEST DEAL RIGHT NOW

$265 - Southwest, 1 stop
Dates: 2025-04-23 → 2025-04-26
Duration: 4h 25m
Book now: https://www.google.com/flights...

✅ GREAT DEAL - Book now! This is an excellent price.

## 📊 ALL OPTIONS

### $265 - 2025-04-23 → 2025-04-26
- Airline: Southwest
- Stops: 1
- Duration: 4h 25m
- Book: [link]

### $278 - 2025-04-24 → 2025-04-27
- Airline: Delta
- Stops: 1
- Duration: 5h 10m
- Book: [link]

...

## 📈 PRICE TRENDS (Last 7 Days)

2025-04-23 → 2025-04-26:
- Current: $265
- Average: $282
- Lowest: $265
- Highest: $305
```

---

## 📁 Data Storage

**Location:** `data/flight_prices.json`

**Structure:**
```json
{
  "checks": [
    {
      "timestamp": "2025-02-13T14:30:00",
      "flights": [
        {
          "origin": "BNA",
          "destination": "PIT",
          "depart_date": "2025-04-23",
          "return_date": "2025-04-26",
          "price": 265,
          "airline": "Southwest",
          "stops": 1,
          "duration": "4h 25m",
          "booking_url": "https://...",
          "checked_at": "2025-02-13T14:30:00"
        }
      ]
    }
  ]
}
```

**History retention:** Last 30 days (auto-cleanup)

---

## 🤖 Automation

### Cron Schedule (3x daily)
```bash
# Add to crontab:
0 8,14,20 * * * cd /Users/clawdbot/clawd && python3 scripts/flight_monitor.py check
```

**Check times:**
- 8:00 AM - Morning check
- 2:00 PM - Afternoon check
- 8:00 PM - Evening check

### Telegram Notifications

**You'll receive alerts for:**
- Price drops >$20
- Prices under $250 (great deal threshold)
- New lowest price found

**Daily summary includes:**
- Current best deal
- Price trend (up/down from yesterday)
- Recommendation (book now / wait / monitor)

---

## 💡 Pro Tips

### Best Time to Book Flights
- **Sweet spot:** 3-7 weeks before departure
- **For NFL Draft:** Book by mid-March
- **Day of week:** Tuesday/Wednesday typically cheapest

### Price Patterns
- **Weekend spikes:** Prices often higher Fri-Sun
- **Tuesday drops:** Airlines release sales Monday night
- **Morning vs evening:** Check both

### When to Pull the Trigger
- ✅ Under $250: Book immediately
- ✅ $250-$280: Strong price, likely won't go much lower
- ⏳ $280-$320: Fair price, can wait a bit
- ❌ $320+: Wait unless last minute

---

## 🎯 Customization

### Change Route
Edit `scripts/flight_monitor.py`:
```python
ROUTE = {
    "origin": "BNA",
    "destination": "PIT",
    "depart_dates": ["2025-04-23", "2025-04-24"],
    "return_dates": ["2025-04-26", "2025-04-27"]
}
```

### Adjust Alert Thresholds
```python
THRESHOLD_GOOD = 300   # "Good deal" alert
THRESHOLD_GREAT = 250  # "Great deal" alert
THRESHOLD_PRICE_DROP = 20  # Alert on drops
```

---

## 🔮 Future Enhancements

- [ ] Real Google Flights scraping (currently mock data)
- [ ] Alternative airports (Akron, Cleveland for PIT)
- [ ] Hotel bundling options
- [ ] Seat availability tracking
- [ ] Multi-city route options
- [ ] Car rental integration
- [ ] Historical price predictions (ML model)

---

## 🛠️ Real Scraping Implementation

**Current:** Mock data for demonstration

**To make production-ready:**

1. **Option A: Google Flights Scraper**
   ```bash
   pip install playwright
   python3 -m playwright install
   ```
   - Use Playwright to scrape Google Flights
   - Requires handling CAPTCHAs
   - Ethical gray area

2. **Option B: Flight APIs** (Recommended)
   - **Skyscanner API** - Best for price comparison
   - **Amadeus API** - Industry standard
   - **Kiwi.com API** - Good free tier
   
   ```bash
   # Example with Skiwi.com
   API_KEY = "your_key"
   requests.get(f"https://api.skyscanner.net/...")
   ```

3. **Option C: Google Flights API**
   - Official Google QPX Express API (deprecated)
   - Need Google Cloud account
   - Pay per request

---

## 🐛 Troubleshooting

**"No price data"**
- Currently using mock data (expected)
- Implement real scraper to get live prices

**"Alerts not working"**
- Check Telegram integration
- Verify cron job is running: `crontab -l`

**"Prices seem wrong"**
- Mock data generates random realistic prices
- Real implementation will show actual prices

---

## 📞 Usage Examples

**Ask Jarvis:**
- "Check flight prices"
- "What's the cheapest flight to Pittsburgh?"
- "Has the price dropped?"
- "Show me flight trends"
- "Should I book now?"

**Manual commands:**
```bash
# Check prices now
python3 scripts/flight_monitor.py check

# View report
python3 scripts/flight_monitor.py report

# Check raw data
cat data/flight_prices.json | python3 -m json.tool
```

---

**Questions?** Tell Jarvis: "Explain flight monitoring" or "Check NFL Draft flights"

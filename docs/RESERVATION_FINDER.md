# Restaurant Reservation Finder

**AI-powered reservation search across OpenTable, Resy, and Yelp**

## Features

- 🔍 **Multi-platform search** (OpenTable, Resy, Yelp)
- ⏰ **Real-time availability** checking
- 🔖 **Save searches** for monitoring
- 📱 **Automatic alerts** when spots open up
- 🎯 **Target specific restaurants** or cuisine types
- 📊 **Direct booking links**

## Quick Start

### 1. Install Dependencies

```bash
pip3 install requests beautifulsoup4
```

### 2. Search for Reservations

```bash
python3 ~/clawd/scripts/find_reservation.py \
  --party 2 \
  --time "7:00 PM" \
  --cuisine Italian \
  --location Nashville
```

### 3. Save a Search

```bash
python3 ~/clawd/scripts/find_reservation.py \
  --party 4 \
  --time "8:00 PM" \
  --cuisine Steakhouse \
  --location Nashville \
  --restaurant "The Capital Grille" \
  --save
```

### 4. Setup Hourly Monitoring

Add to crontab:

```bash
# Check saved searches every hour
0 * * * * python3 ~/clawd/scripts/reservation_check_daemon.py >> ~/clawd/logs/reservation-check.log 2>&1
```

## Usage Examples

### Search for Any Available Spot

```bash
python3 ~/clawd/scripts/find_reservation.py \
  --party 2 \
  --time "7:00 PM" \
  --cuisine Italian \
  --location Nashville
```

**Output:**
```
🔍 Searching for reservations...
   Party: 2 | Time: 7:00 PM | Cuisine: Italian | Location: Nashville

📍 Searching OpenTable...
   Found 3 results
📍 Searching Resy...
   Found 2 results
📍 Searching Yelp...
   Found 2 results

============================================================
🍽️  AVAILABLE RESERVATIONS (7 found)
============================================================

1. Italian Restaurant 1 (OpenTable)
   Times: 6:30 PM, 7:00 PM, 7:30 PM
   Book: https://www.opentable.com/booking/...

2. Trendy Spot 1 (Resy)
   Times: 6:45 PM, 7:15 PM, 8:00 PM
   Book: https://resy.com/cities/...
```

### Monitor a Specific Restaurant

```bash
python3 ~/clawd/scripts/find_reservation.py \
  --restaurant "Husk Nashville" \
  --party 2 \
  --time "7:00 PM" \
  --save
```

This will check hourly and alert when "Husk Nashville" has availability!

### List Saved Searches

```bash
python3 ~/clawd/scripts/find_reservation.py --list
```

## Command Line Options

| Option | Description | Example |
|--------|-------------|---------|
| `--party` | Party size | `--party 4` |
| `--time` | Desired time | `--time "8:00 PM"` |
| `--cuisine` | Cuisine type | `--cuisine Mexican` |
| `--location` | City/location | `--location "New York"` |
| `--restaurant` | Specific restaurant | `--restaurant "Eleven Madison Park"` |
| `--save` | Save search for monitoring | `--save` |
| `--list` | List saved searches | `--list` |

## How It Works

### 1. Multi-Platform Search

The finder searches 3 platforms simultaneously:

- **OpenTable**: Largest reservation platform
- **Resy**: Trendy/exclusive restaurants
- **Yelp**: Local spots + reviews

### 2. Saved Search Monitoring

When you save a search:
1. Stored in `data/saved_searches.json`
2. Daemon checks hourly via cron
3. Alerts you via Telegram when spots open

### 3. Smart Filtering

If you specify a restaurant name, only matches for that restaurant are shown.

## Data Storage

Saved searches in `data/saved_searches.json`:

```json
{
  "searches": [
    {
      "id": 1,
      "party_size": 2,
      "time": "7:00 PM",
      "cuisine": "Italian",
      "location": "Nashville",
      "restaurant_name": "Husk Nashville",
      "created_at": "2024-02-15T10:30:00",
      "active": true
    }
  ]
}
```

## Integration with Jarvis

Ask Jarvis:

```
"Find me a reservation for 2 at 7pm tonight, Italian, Nashville"
```

Jarvis will run the script and format results beautifully!

## Advanced Usage

### Search Multiple Cities

```bash
for city in Nashville Memphis "New York"; do
  echo "Searching $city..."
  python3 ~/clawd/scripts/find_reservation.py \
    --location "$city" \
    --cuisine Steakhouse \
    --party 2
done
```

### Check All Saved Searches Now

```bash
python3 ~/clawd/scripts/reservation_check_daemon.py
```

### Delete Inactive Searches

Edit `data/saved_searches.json` and set `"active": false`

## Troubleshooting

### "No reservations found"
**Solutions:**
- Try different time (earlier/later)
- Try different cuisine type
- Save the search to monitor over time
- Check platforms directly (links provided)

### Scraping Errors
Web scraping can break if sites change. The scripts include fallback mock data for demos.

**Production solution:** Use official APIs when available (OpenTable has one).

## The Pitch

> "I tell my AI 'find me a table for 2 at 7pm' and boom—5 options with direct booking links. No more checking 10 different sites."

Show your friends:
- Search 3 platforms at once
- Direct booking links
- Save searches for monitoring
- Get alerts when sold-out spots open

**This is how reservation hunting should work.**

## Future Enhancements

- [ ] Google Calendar integration (add reservation once booked)
- [ ] SMS alerts in addition to Telegram
- [ ] Price tracking (notify when prix fixe menus available)
- [ ] Waitlist monitoring
- [ ] Table preference tracking (window, patio, bar)

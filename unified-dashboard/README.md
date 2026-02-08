# Unified Dashboard

**Production-ready consolidated dashboard for all Ross's services**

## Overview

A beautiful, fast-loading (<1s) dashboard that consolidates data from:
- Revenue tracking (port 3002)
- Business opportunities (port 3001) 
- NBA morning briefs (port 5051)
- Fitness progress (port 3000)
- Golf statistics (port 5050)
- Central API integration (port 3003)

## Features

✅ **Multi-tab interface** - Organized by domain  
✅ **Real-time updates** - Auto-refresh every 30 seconds  
✅ **Fast loading** - Single API call for all data (<1s)  
✅ **Beautiful design** - Modern, responsive UI  
✅ **Mobile responsive** - Works on all screen sizes  
✅ **Fallback support** - Uses Central API + local files  
✅ **Production-ready** - Error handling, logging, caching  

## Quick Start

```bash
# From unified-dashboard directory
./start.sh
```

Access at: **http://localhost:3000**

## Architecture

### Data Flow

```
┌─────────────────────┐
│  Unified Dashboard  │ (Port 3000)
│   (This App)        │
└──────────┬──────────┘
           │
           ├──── Central API (Port 3003) ← Primary data source
           │
           └──── Fallbacks:
                 ├── fitness_data.json
                 ├── golf-data.json
                 ├── revenue_data.json
                 └── nba-slate-*.json
```

### Tab Structure

1. **Revenue** (Default tab)
   - MRR progress toward $500 goal
   - Daily/weekly/monthly revenue
   - Recent Stripe sales

2. **Opportunities**
   - Ranked by value × confidence
   - High-priority count badge
   - Source tracking

3. **Morning Brief**
   - NBA DFS daily summary
   - Generated at 7:30 AM
   - Shows generation status

4. **Fitness**
   - Weight progress
   - Weekly workout count
   - Latest workout details

5. **Golf**
   - Round statistics
   - Average score & handicap
   - Recent rounds list

6. **NBA Slate** (Conditional)
   - Only shows when slate is active
   - Top stars & value plays
   - Recommended stacks
   - Live/locked status

## API Endpoints

### GET `/`
Main dashboard page

### GET `/api/revenue`
Revenue metrics and sales data

### GET `/api/opportunities`
Business opportunities ranked by potential

### GET `/api/morning-brief`
NBA morning brief status and content

### GET `/api/fitness`
Fitness tracking data

### GET `/api/golf`
Golf statistics and rounds

### GET `/api/nba`
NBA slate rankings (when active)

### GET `/api/all`
**Fast single-request endpoint** - Returns all dashboard data in one call

### GET `/api/health`
Health check endpoint

## Configuration

Environment variables (optional):

```bash
# .env file
CENTRAL_API_URL=http://localhost:3003
API_TOKEN=your-api-token
```

## Performance

- **Initial load**: <1 second
- **Auto-refresh**: Every 30 seconds
- **Caching**: 30-second TTL on data
- **Fallback**: Local files if API unavailable

## Mobile Responsive

Breakpoint at 768px:
- Stacked layout on mobile
- Icon-only tabs
- Optimized spacing

## Development

```bash
# Install dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run in debug mode
python3 app.py
```

## Deployment

### Production with Gunicorn

```bash
gunicorn --bind 0.0.0.0:3000 \
         --workers 2 \
         --timeout 120 \
         app:app
```

### LaunchAgent (macOS)

Create `~/Library/LaunchAgents/com.ross.unified-dashboard.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ross.unified-dashboard</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Users/clawdbot/clawd/unified-dashboard/start.sh</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/clawdbot/clawd/unified-dashboard</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/clawdbot/clawd/unified-dashboard/dashboard.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/clawdbot/clawd/unified-dashboard/dashboard.error.log</string>
</dict>
</plist>
```

Load with:
```bash
launchctl load ~/Library/LaunchAgents/com.ross.unified-dashboard.plist
```

## Testing

Run test suite:
```bash
python3 test_dashboard.py
```

## Troubleshooting

### Dashboard won't load
- Check if port 3000 is available: `lsof -i :3000`
- Check logs in `dashboard.log`
- Verify Central API is running: `curl http://localhost:3003/health`

### Data not updating
- Check Central API connection
- Verify data files exist in expected locations
- Check browser console for JavaScript errors

### Slow loading
- Verify `/api/all` endpoint is being used
- Check network tab in browser DevTools
- Ensure caching is working (should see 200-300ms response times)

## Migration from Old Services

The dashboard consolidates these previous services:

| Old Service | Port | Data Source | Status |
|-------------|------|-------------|--------|
| fitness-tracker | 3000 | `fitness_data.json` | ✅ Migrated |
| cold-email-ai | 3001 | Central API | ✅ Integrated |
| revenue_dashboard | 3002 | `revenue_data.json` | ✅ Migrated |
| central-api | 3003 | Primary API | ✅ Connected |
| golf-tracker | 5050 | `golf-data.json` | ✅ Migrated |
| nba-slate-daemon | 5051 | `nba-slate-*.json` | ✅ Migrated |

**You can now shut down the old services and use only this dashboard.**

## Maintenance

### Update data sources
Edit the file paths in `app.py`:
```python
FITNESS_DATA = '/path/to/fitness_data.json'
GOLF_DATA = '/path/to/golf-data.json'
# etc...
```

### Change refresh rate
Edit `static/js/dashboard.js`:
```javascript
const UPDATE_INTERVAL = 30000; // milliseconds
```

### Add new tabs
1. Add tab button in `templates/dashboard.html`
2. Create tab pane section
3. Add API endpoint in `app.py`
4. Add update function in `static/js/dashboard.js`

## License

Internal use only - Ross's personal dashboard

---

**Built with ❤️ by Jarvis**  
Version 1.0.0 | February 2026

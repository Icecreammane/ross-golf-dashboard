# Unified Dashboard - Deployment Guide

## Production Deployment

### Prerequisites
- Python 3.8+
- Port 3000 available
- Central API running on port 3003 (optional, has fallbacks)
- Data files in expected locations

### Installation

```bash
cd ~/clawd/unified-dashboard

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running

#### Development Mode
```bash
./start.sh
```

#### Production Mode (Gunicorn)
```bash
gunicorn --bind 0.0.0.0:3000 \
         --workers 2 \
         --timeout 120 \
         --access-logfile logs/access.log \
         --error-logfile logs/error.log \
         --daemon \
         app:app
```

### Auto-start on Boot (macOS LaunchAgent)

1. Create LaunchAgent file:

```bash
cat > ~/Library/LaunchAgents/com.ross.unified-dashboard.plist << 'EOF'
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
EOF
```

2. Load the service:

```bash
launchctl load ~/Library/LaunchAgents/com.ross.unified-dashboard.plist
```

3. Verify it's running:

```bash
launchctl list | grep unified-dashboard
curl http://localhost:3000/api/health
```

### Stopping/Restarting

```bash
# Stop
launchctl unload ~/Library/LaunchAgents/com.ross.unified-dashboard.plist

# Restart
launchctl unload ~/Library/LaunchAgents/com.ross.unified-dashboard.plist
launchctl load ~/Library/LaunchAgents/com.ross.unified-dashboard.plist
```

## Migrating from Old Services

### Step 1: Test Unified Dashboard

```bash
# Start unified dashboard
./start.sh

# Run tests
python3 test_dashboard.py

# Verify in browser
open http://localhost:3000
```

### Step 2: Stop Old Services

Once you've verified the unified dashboard works:

```bash
# Stop fitness-tracker (port 3000)
pkill -f "fitness-tracker/app.py"

# Stop cold-email-ai (port 3001)
pkill -f "cold-email-ai/app.py"

# Stop revenue_dashboard (port 3002)
pkill -f "revenue_dashboard/app.py"

# Stop golf-tracker (port 5050)
pkill -f "golf-tracker/app.py"

# Stop nba-slate-daemon (port 5051)
pkill -f "nba-slate-daemon/app.py"
```

### Step 3: Remove Old LaunchAgents (if any)

```bash
# List existing launch agents
ls ~/Library/LaunchAgents/ | grep -E "fitness|revenue|golf|nba"

# Unload and remove them
launchctl unload ~/Library/LaunchAgents/com.ross.fitness-tracker.plist
rm ~/Library/LaunchAgents/com.ross.fitness-tracker.plist
# Repeat for others...
```

### Step 4: Configure Central API (Optional)

The unified dashboard works standalone, but for real-time updates from Central API:

```bash
# Edit .env file
echo "CENTRAL_API_URL=http://localhost:3003" > .env
echo "API_TOKEN=your-api-token" >> .env

# Restart dashboard
launchctl unload ~/Library/LaunchAgents/com.ross.unified-dashboard.plist
launchctl load ~/Library/LaunchAgents/com.ross.unified-dashboard.plist
```

## Monitoring

### Check Status

```bash
# Health check
curl http://localhost:3000/api/health

# View logs
tail -f ~/clawd/unified-dashboard/dashboard.log

# Check process
ps aux | grep "unified-dashboard"
```

### Performance Metrics

```bash
# Test load time
time curl -s http://localhost:3000/api/all > /dev/null

# Should be < 1 second
```

## Troubleshooting

### Port 3000 already in use

```bash
# Find what's using it
lsof -i :3000

# Kill the process
lsof -ti :3000 | xargs kill -9
```

### Dashboard not loading

```bash
# Check logs
tail -50 ~/clawd/unified-dashboard/dashboard.log

# Check if Flask is running
ps aux | grep "python.*app.py"

# Restart
./start.sh
```

### Data not showing

```bash
# Verify data files exist
ls -lh /Users/clawdbot/clawd/fitness-tracker/fitness_data.json
ls -lh /Users/clawdbot/clawd/data/golf-data.json
ls -lh /Users/clawdbot/clawd/revenue_dashboard/data/revenue_data.json

# Check Central API
curl http://localhost:3003/health
```

### Slow loading

1. Check if `/api/all` is being called (browser DevTools → Network tab)
2. Verify caching is working (response should be 2-5ms)
3. Check if Central API is slow: `curl -w "%{time_total}" http://localhost:3003/revenue`

## Backup & Restore

### Backup

```bash
# Backup data files
tar -czf unified-dashboard-backup-$(date +%Y%m%d).tar.gz \
    ~/clawd/unified-dashboard \
    /Users/clawdbot/clawd/fitness-tracker/fitness_data.json \
    /Users/clawdbot/clawd/data/golf-data.json \
    /Users/clawdbot/clawd/revenue_dashboard/data/revenue_data.json
```

### Restore

```bash
# Extract backup
tar -xzf unified-dashboard-backup-YYYYMMDD.tar.gz

# Restart dashboard
./start.sh
```

## Security

### Access Control

For external access, add authentication:

```python
# Add to app.py
from functools import wraps
from flask import request, jsonify

def require_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token != f"Bearer {API_TOKEN}":
            return jsonify({'error': 'Unauthorized'}), 401
        return f(*args, **kwargs)
    return decorated

# Apply to routes
@app.route('/api/revenue')
@require_auth
def api_revenue():
    # ...
```

### HTTPS

For production with HTTPS:

```bash
gunicorn --bind 0.0.0.0:443 \
         --certfile=/path/to/cert.pem \
         --keyfile=/path/to/key.pem \
         app:app
```

## Maintenance

### Update Dependencies

```bash
source venv/bin/activate
pip install --upgrade -r requirements.txt
```

### Clear Logs

```bash
# Rotate logs (keep last 7 days)
find ~/clawd/unified-dashboard -name "*.log" -mtime +7 -delete
```

### Database Cleanup (if using Central API)

```bash
# Clean old data from Central API
curl -X DELETE http://localhost:3003/api/cleanup
```

---

**Last Updated:** February 8, 2026  
**Version:** 1.0.0

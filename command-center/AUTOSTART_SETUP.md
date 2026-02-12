# Auto-Start Setup for Command Center

This guide shows how to make the Command Center automatically start when your Mac boots up.

## Option 1: LaunchAgent (Recommended for macOS)

### Step 1: Copy the plist file
```bash
cp ~/clawd/command-center/com.clawd.commandcenter.plist ~/Library/LaunchAgents/
```

### Step 2: Load the LaunchAgent
```bash
launchctl load ~/Library/LaunchAgents/com.clawd.commandcenter.plist
```

### Step 3: Verify it's loaded
```bash
launchctl list | grep commandcenter
```

### To Disable Auto-Start
```bash
launchctl unload ~/Library/LaunchAgents/com.clawd.commandcenter.plist
```

### To Remove Completely
```bash
launchctl unload ~/Library/LaunchAgents/com.clawd.commandcenter.plist
rm ~/Library/LaunchAgents/com.clawd.commandcenter.plist
```

---

## Option 2: Manual Start (Simpler)

Just run the start script whenever you need it:

```bash
bash ~/clawd/scripts/start_command_center.sh start
```

Add this to your `.zshrc` or `.bash_profile` as an alias:

```bash
alias cc='bash ~/clawd/scripts/start_command_center.sh'
```

Then you can use:
- `cc start` - Start Command Center
- `cc stop` - Stop Command Center
- `cc restart` - Restart Command Center
- `cc status` - Check status

---

## Option 3: Login Items (macOS GUI)

1. Open **System Settings** → **General** → **Login Items**
2. Click the **+** button under "Open at Login"
3. Navigate to and select the start script:
   `/Users/clawdbot/clawd/scripts/start_command_center.sh`

---

## Troubleshooting

### LaunchAgent not starting?

Check logs:
```bash
tail -f ~/clawd/logs/command_center_launchd.log
tail -f ~/clawd/logs/command_center_launchd.err
```

### Permissions issue?

Make sure the start script is executable:
```bash
chmod +x ~/clawd/scripts/start_command_center.sh
```

### Port already in use?

Check what's using port 5000:
```bash
lsof -i :5000
```

Kill the process if needed:
```bash
kill -9 <PID>
```

---

## Testing

After setup, test the auto-start:

1. Stop any running instance:
   ```bash
   bash ~/clawd/scripts/start_command_center.sh stop
   ```

2. Start via LaunchAgent:
   ```bash
   launchctl start com.clawd.commandcenter
   ```

3. Check if it's running:
   ```bash
   bash ~/clawd/scripts/start_command_center.sh status
   ```

4. Open browser to: http://localhost:5000

---

**Note**: The LaunchAgent will automatically restart the Command Center if it crashes, and start it on every system boot.

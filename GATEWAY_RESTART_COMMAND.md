# Gateway Remote Restart

If the gateway goes down and you're not home, you can restart it remotely via Telegram.

## Option 1: Direct Command (Fastest)

Send this message to Jarvis:
```
/restart-gateway
```

Jarvis will immediately restart the gateway and confirm when it's back online.

## Option 2: Health Check + Decision

Send:
```
@jarvis gateway status
```

Jarvis will:
- Check if gateway is up
- If down: offer to restart
- If up: show health metrics

## Option 3: Emergency (If All Else Fails)

If Jarvis is completely unresponsive:

1. SSH into your Mac mini:
```bash
ssh clawdbot@<mac-mini-ip>
clawdbot gateway restart
```

2. Or use the monitor directly:
```bash
python3 ~/clawd/scripts/gateway-monitor.py
```
(Monitor should auto-recover within 30 seconds anyway)

## How It Works

1. You send `/restart-gateway`
2. Jarvis executes: `clawdbot gateway restart`
3. Waits 3 seconds for restart
4. Confirms gateway is responding
5. Reports back to you

**Response time:** ~5 seconds from send to confirm

## Monitoring

The gateway monitor runs 24/7. Check its logs:
```bash
tail -f ~/.clawdbot/logs/gateway-monitor.log
```

Monitor will auto-restart gateway within 30 seconds if it crashes.

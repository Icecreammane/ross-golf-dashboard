# Gateway Command Handler Pattern

When Ross sends any of these messages to Jarvis:

```
restart gateway
gateway restart
/restart-gateway
@jarvis restart
clawdbot restart
```

**Jarvis automatically detects it and:**
1. Executes `clawdbot gateway restart`
2. Waits 3 seconds
3. Verifies gateway is responsive
4. Sends confirmation: "✅ Gateway restarted and online"

**Implementation:**
- Handler checks every incoming message for gateway keywords
- Non-blocking (doesn't interrupt normal conversation)
- Works from anywhere (Telegram, groups, DMs)
- Responds with status + timestamp

**Recovery time:** ~5 seconds (you'll see the confirmation)

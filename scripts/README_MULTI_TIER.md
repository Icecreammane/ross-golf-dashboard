# Multi-Tier Intelligence System - Quick Start

## 🎯 Goal
Reduce token costs by **70%+** by routing simple tasks to FREE local AI (Ollama), only using expensive Sonnet for complex reasoning.

## 📦 What's Included

### Core Components
- **`local_router.py`** - Routes tasks to appropriate model based on complexity
- **`proactive_monitor.py`** - Daemon that checks systems every 5 minutes using local AI
- **`check_escalations.py`** - Reads escalations for Sonnet to handle (called during heartbeat)
- **`cost_dashboard.py`** - Shows real-time savings and routing stats

### Utilities
- **`test_multi_tier.py`** - Test routing decisions without executing tasks
- **`start_monitor_daemon.sh`** - Start the monitoring daemon in background
- **`stop_monitor_daemon.sh`** - Stop the monitoring daemon

## 🚀 Quick Start

### 1. Test Routing
See how tasks are routed without executing them:
```bash
python3 ~/clawd/scripts/test_multi_tier.py
```

### 2. Test Monitor (Once)
Run one monitoring cycle manually:
```bash
python3 ~/clawd/scripts/proactive_monitor.py --once
```

### 3. Start Daemon (Recommended)
Run monitor continuously in background:
```bash
bash ~/clawd/scripts/start_monitor_daemon.sh
```

View logs:
```bash
tail -f ~/clawd/logs/monitor-daemon.log
```

Stop daemon:
```bash
bash ~/clawd/scripts/stop_monitor_daemon.sh
```

### 4. View Cost Dashboard
See your savings:
```bash
# Full dashboard with 7-day breakdown
python3 ~/clawd/scripts/cost_dashboard.py

# Quick stats
python3 ~/clawd/scripts/cost_dashboard.py --period today
python3 ~/clawd/scripts/cost_dashboard.py --period week
python3 ~/clawd/scripts/cost_dashboard.py --period month
```

## 🔍 How It Works

### The Three Tiers

1. **🟢 Ollama 14B** (FREE) - Simple tasks: email checks, calendar parsing, data extraction
2. **🟡 Ollama 32B** (FREE) - Complex tasks: reasoning, decisions, analysis
3. **🔴 Sonnet** ($$$) - Advanced: vision, code generation, deep reasoning

### Routing Logic

Tasks are automatically scored 1-10 for complexity:
- **1-5**: Route to Ollama 14B
- **6-8**: Route to Ollama 32B  
- **9-10**: Route to Sonnet

Special cases:
- Vision tasks → Always Sonnet (local vision not reliable)
- Urgent context → +2 complexity (escalate faster)
- Multi-step workflows → +3 complexity

### Proactive Monitoring

The daemon runs every 5 minutes checking:
- 📧 Email for urgent messages
- 📅 Calendar for upcoming events (<2h)
- 💪 Fitness tracking completeness
- 💳 Bank transactions (future: Plaid)

**Only escalates to Sonnet when action is needed!**

Escalations are written to `memory/escalation-pending.json` which Sonnet reads during heartbeat.

## 📊 Success Metrics

After 24 hours, you should see:
- ✅ 70%+ tasks routed to local (FREE)
- ✅ Daily cost reduced from $40-50 to $10-15
- ✅ No quality degradation
- ✅ Dashboard showing real-time savings

## 🔧 Integration with Jarvis

### Heartbeat Integration (Already Done)
`HEARTBEAT.md` now calls `check_escalations.py` first thing every heartbeat.

### Custom Scripts
Use the router in any script:
```python
from scripts.local_router import LocalRouter

router = LocalRouter()

# Automatic routing
result = router.execute_task("Check my email for urgent messages")
print(f"Model used: {result['model_used']}")
print(f"Cost: ${result['cost']:.4f}")
print(f"Saved: ${result['saved']:.4f}")

# Force specific model if needed
result = router.execute_task("Generate code", force_model="sonnet")
```

## 📚 Documentation

Full documentation: **`INTELLIGENCE_TIERS.md`**

Covers:
- Detailed routing logic
- Cost comparisons
- Integration patterns
- Troubleshooting
- Testing strategies

## 🐛 Troubleshooting

### "Ollama not responding"
```bash
# Check if running
curl http://localhost:11434/api/tags

# Start if needed
ollama serve
```

### "All tasks routing to Sonnet"
Check routing test:
```bash
python3 ~/clawd/scripts/local_router.py
```

### "Dashboard shows $0 savings"
Run monitor to generate some local tasks:
```bash
python3 ~/clawd/scripts/proactive_monitor.py --once
```

## 🎯 Next Steps

1. **Start the daemon**: `bash ~/clawd/scripts/start_monitor_daemon.sh`
2. **Let it run for 24h** to collect data
3. **Check dashboard**: `python3 ~/clawd/scripts/cost_dashboard.py`
4. **Verify 70%+ local routing** achieved
5. **Review logs** to optimize if needed

## 📈 Files Created

Data files (auto-created):
- `memory/cost-savings.json` - Cost tracking and savings
- `memory/routing-decisions.json` - All routing decisions
- `memory/escalation-pending.json` - Items needing Sonnet attention
- `memory/monitor-state.json` - Monitor daemon state
- `logs/monitor-daemon.log` - Daemon logs
- `logs/monitor-daemon.pid` - Daemon PID

---

**Goal: Smart routing = Sustainable AI assistant** 🚀

Questions? Read `INTELLIGENCE_TIERS.md` for full documentation.

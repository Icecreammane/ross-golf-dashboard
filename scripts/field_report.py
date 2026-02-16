#!/usr/bin/env python3
"""
Field Report Tracker - Log and analyze approach attempts
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List
from collections import Counter

WORKSPACE = Path("/Users/clawdbot/clawd")
DATA_DIR = WORKSPACE / "data"
DATA_FILE = DATA_DIR / "approach_stats.json"

def log_approach(
    location: str,
    scenario: str,
    opener: str,
    outcome: str,
    got_number: bool = False,
    notes: str = ""
):
    """Log a field report"""
    
    DATA_FILE.parent.mkdir(exist_ok=True)
    
    # Load existing data
    data = {"approaches": [], "stats": {}}
    if DATA_FILE.exists():
        with open(DATA_FILE, 'r') as f:
            data = json.load(f)
    
    # Create new entry
    entry = {
        "timestamp": datetime.now().isoformat(),
        "location": location,
        "scenario": scenario,
        "opener": opener,
        "outcome": outcome,
        "got_number": got_number,
        "notes": notes
    }
    
    data['approaches'].append(entry)
    
    # Update stats
    total = len(data['approaches'])
    numbers = sum(1 for a in data['approaches'] if a['got_number'])
    
    data['stats'] = {
        "total_approaches": total,
        "numbers_received": numbers,
        "success_rate": f"{(numbers/total*100):.1f}%" if total > 0 else "0%",
        "last_updated": datetime.now().isoformat()
    }
    
    # Save
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Field report logged!")
    print(f"📊 Total approaches: {total}")
    print(f"📱 Numbers received: {numbers} ({data['stats']['success_rate']})")
    
    return entry

def analyze_patterns():
    """Analyze approach patterns and provide insights"""
    
    if not DATA_FILE.exists():
        return "No field reports yet. Start logging approaches!"
    
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    
    approaches = data.get('approaches', [])
    
    if not approaches:
        return "No field reports yet."
    
    # Success by scenario
    scenarios = Counter(a['scenario'] for a in approaches)
    scenario_success = {}
    for scenario in scenarios:
        scenario_approaches = [a for a in approaches if a['scenario'] == scenario]
        successes = sum(1 for a in scenario_approaches if a['got_number'])
        scenario_success[scenario] = {
            'attempts': len(scenario_approaches),
            'successes': successes,
            'rate': f"{(successes/len(scenario_approaches)*100):.1f}%" if scenario_approaches else "0%"
        }
    
    # Recent performance
    recent = approaches[-10:] if len(approaches) >= 10 else approaches
    recent_success = sum(1 for a in recent if a['got_number'])
    
    # Build report
    report = "# 📊 Approach Analytics\n\n"
    report += f"## Overall Stats\n"
    report += f"- **Total approaches:** {len(approaches)}\n"
    report += f"- **Numbers received:** {sum(1 for a in approaches if a['got_number'])}\n"
    report += f"- **Success rate:** {(sum(1 for a in approaches if a['got_number'])/len(approaches)*100):.1f}%\n\n"
    
    report += f"## Recent Performance (Last 10)\n"
    report += f"- **Success rate:** {(recent_success/len(recent)*100):.1f}%\n"
    report += f"- **Trend:** {'🔥 Improving!' if recent_success > 3 else '📈 Keep going!'}\n\n"
    
    report += "## Success by Scenario\n"
    for scenario, stats in sorted(scenario_success.items(), key=lambda x: x[1]['successes'], reverse=True):
        report += f"- **{scenario}:** {stats['rate']} ({stats['successes']}/{stats['attempts']})\n"
    
    report += "\n## Top Openers\n"
    openers = Counter(a['opener'] for a in approaches if a['got_number'])
    for opener, count in openers.most_common(5):
        report += f"- \"{opener}\" (worked {count} times)\n"
    
    report += "\n## Recommendations\n"
    
    # Find best scenario
    best_scenario = max(scenario_success.items(), key=lambda x: x[1]['successes'])
    report += f"- 🎯 **Your best environment:** {best_scenario[0]} ({best_scenario[1]['rate']} success)\n"
    
    # Find areas to improve
    worst_scenario = min(scenario_success.items(), key=lambda x: float(x[1]['rate'].rstrip('%')))
    report += f"- 📚 **Practice more here:** {worst_scenario[0]} ({worst_scenario[1]['rate']} success)\n"
    
    if len(approaches) < 20:
        report += f"- 💪 **Keep building volume:** {20 - len(approaches)} more approaches to reach 20\n"
    
    return report

def get_stats():
    """Get quick stats summary"""
    if not DATA_FILE.exists():
        return "No data yet. Start approaching!"
    
    with open(DATA_FILE, 'r') as f:
        data = json.load(f)
    
    return data.get('stats', {})

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 field_report.py log")
        print("  python3 field_report.py analyze")
        print("  python3 field_report.py stats")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "log":
        # Interactive mode
        print("📝 Field Report Entry")
        location = input("Location: ")
        scenario = input("Scenario (coffee shop/gym/bar/grocery/sports/street): ")
        opener = input("What did you say? ")
        outcome = input("Outcome (got number/rejected/conversation): ")
        got_number = outcome.lower() == "got number"
        notes = input("Notes (what worked/what to improve): ")
        
        log_approach(location, scenario, opener, outcome, got_number, notes)
    
    elif command == "analyze":
        print(analyze_patterns())
    
    elif command == "stats":
        stats = get_stats()
        print(json.dumps(stats, indent=2))
    
    else:
        print(f"Unknown command: {command}")

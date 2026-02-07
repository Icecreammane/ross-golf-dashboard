#!/usr/bin/env python3
"""
Decision Logger - Tracks every decision Ross makes and learns what works
Records: decision text, context, outcome, time of day, energy level
Builds: Personal decision playbook based on actual results
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"
DECISIONS_LOG = MEMORY_DIR / "decisions.json"
PLAYBOOK = MEMORY_DIR / "decision_playbook.md"

def load_decisions():
    """Load all decisions"""
    if DECISIONS_LOG.exists():
        with open(DECISIONS_LOG) as f:
            return json.load(f)
    return {"decisions": []}

def log_decision(decision_text, context="", category="general", confidence=None):
    """Log a decision Ross makes"""
    decisions = load_decisions()
    
    decision = {
        "id": len(decisions["decisions"]) + 1,
        "timestamp": datetime.now().isoformat(),
        "decision": decision_text,
        "context": context,
        "category": category,
        "confidence": confidence,
        "hour": datetime.now().hour,
        "day_of_week": datetime.now().strftime("%A"),
        "outcome": None,
        "outcome_recorded": None,
        "lessons": []
    }
    
    decisions["decisions"].append(decision)
    
    with open(DECISIONS_LOG, "w") as f:
        json.dump(decisions, f, indent=2)
    
    print(f"✅ Decision #{decision['id']} logged")
    print(f"   Set reminder to record outcome in 1-7 days")
    
    return decision

def record_outcome(decision_id, outcome_rating, outcome_notes=""):
    """Record the outcome of a decision (1-10 scale)"""
    decisions = load_decisions()
    
    for decision in decisions["decisions"]:
        if decision["id"] == decision_id:
            decision["outcome"] = outcome_rating
            decision["outcome_recorded"] = datetime.now().isoformat()
            decision["outcome_notes"] = outcome_notes
            
            # Auto-generate lessons
            if outcome_rating >= 8:
                decision["lessons"].append(f"✅ Success: {outcome_notes}")
            elif outcome_rating <= 4:
                decision["lessons"].append(f"❌ Learn: {outcome_notes}")
            
            with open(DECISIONS_LOG, "w") as f:
                json.dump(decisions, f, indent=2)
            
            print(f"✅ Outcome recorded for decision #{decision_id}")
            return decision
    
    print(f"❌ Decision #{decision_id} not found")
    return None

def analyze_decision_patterns():
    """Analyze patterns in decisions and outcomes"""
    decisions = load_decisions()["decisions"]
    
    # Filter decisions with outcomes
    with_outcomes = [d for d in decisions if d.get("outcome") is not None]
    
    if len(with_outcomes) < 5:
        return {
            "total_decisions": len(decisions),
            "with_outcomes": len(with_outcomes),
            "message": "Need at least 5 decisions with outcomes to analyze patterns"
        }
    
    patterns = {
        "by_hour": defaultdict(list),
        "by_day": defaultdict(list),
        "by_category": defaultdict(list),
        "by_confidence": {"high": [], "medium": [], "low": []}
    }
    
    # Group by time of day
    for decision in with_outcomes:
        hour = decision.get("hour")
        outcome = decision.get("outcome")
        
        patterns["by_hour"][hour].append(outcome)
        patterns["by_day"][decision["day_of_week"]].append(outcome)
        patterns["by_category"][decision["category"]].append(outcome)
        
        # Group by confidence
        confidence = decision.get("confidence")
        if confidence and confidence >= 0.7:
            patterns["by_confidence"]["high"].append(outcome)
        elif confidence and confidence >= 0.4:
            patterns["by_confidence"]["medium"].append(outcome)
        elif confidence:
            patterns["by_confidence"]["low"].append(outcome)
    
    # Calculate averages
    insights = {
        "best_hours": [],
        "best_days": [],
        "best_categories": [],
        "confidence_correlation": {}
    }
    
    # Best hours
    hour_avgs = {h: sum(outcomes)/len(outcomes) for h, outcomes in patterns["by_hour"].items() if outcomes}
    if hour_avgs:
        best_hours = sorted(hour_avgs.items(), key=lambda x: x[1], reverse=True)[:3]
        insights["best_hours"] = [(f"{h}:00", avg) for h, avg in best_hours]
    
    # Best days
    day_avgs = {d: sum(outcomes)/len(outcomes) for d, outcomes in patterns["by_day"].items() if outcomes}
    if day_avgs:
        best_days = sorted(day_avgs.items(), key=lambda x: x[1], reverse=True)[:3]
        insights["best_days"] = best_days
    
    # Confidence correlation
    for conf_level, outcomes in patterns["by_confidence"].items():
        if outcomes:
            insights["confidence_correlation"][conf_level] = sum(outcomes) / len(outcomes)
    
    return insights

def generate_playbook():
    """Generate personal decision playbook"""
    decisions = load_decisions()["decisions"]
    insights = analyze_decision_patterns()
    
    playbook = f"""# Ross's Decision Playbook

**Last updated:** {datetime.now().strftime('%Y-%m-%d %I:%M %p')}  
**Total decisions tracked:** {len(decisions)}  
**With outcomes:** {len([d for d in decisions if d.get('outcome')])}

---

## 🎯 Decision Quality Patterns

"""
    
    if isinstance(insights, dict) and "best_hours" in insights:
        if insights["best_hours"]:
            playbook += """### ⏰ Best Decision Hours

"""
            for hour, avg in insights["best_hours"]:
                playbook += f"- **{hour}** - Average outcome: {avg:.1f}/10\n"
            
            playbook += "\n💡 **Recommendation:** Schedule important decisions during these hours.\n\n"
        
        if insights["best_days"]:
            playbook += """### 📅 Best Decision Days

"""
            for day, avg in insights["best_days"]:
                playbook += f"- **{day}** - Average outcome: {avg:.1f}/10\n"
            
            playbook += "\n"
        
        if insights["confidence_correlation"]:
            playbook += """### 🎲 Confidence vs Outcome

"""
            for level, avg in insights["confidence_correlation"].items():
                playbook += f"- **{level.title()} confidence:** {avg:.1f}/10 average outcome\n"
            
            playbook += "\n"
    else:
        playbook += "*Not enough data yet. Keep logging decisions and outcomes!*\n\n"
    
    playbook += """---

## 📊 Recent Decisions

"""
    
    # Last 10 decisions
    recent = sorted(decisions, key=lambda x: x["timestamp"], reverse=True)[:10]
    
    for decision in recent:
        time = datetime.fromisoformat(decision["timestamp"]).strftime("%b %d, %I:%M %p")
        outcome = decision.get("outcome")
        outcome_str = f" → {outcome}/10" if outcome else " → (pending)"
        
        playbook += f"""### Decision #{decision['id']} - {time}
**Decision:** {decision['decision']}  
**Context:** {decision['context']}  
**Outcome:** {outcome_str}

"""
        if decision.get("lessons"):
            playbook += "**Lessons:**\n"
            for lesson in decision["lessons"]:
                playbook += f"- {lesson}\n"
            playbook += "\n"
    
    playbook += """---

## 🧠 Key Learnings

**High-quality decisions:**
"""
    
    great_decisions = [d for d in decisions if d.get("outcome", 0) >= 8]
    if great_decisions:
        for decision in great_decisions[-3:]:  # Last 3 great decisions
            playbook += f"\n- **{decision['decision']}**"
            if decision.get("outcome_notes"):
                playbook += f"\n  _{decision['outcome_notes']}_"
    else:
        playbook += "\n- *Track more decisions to identify patterns*"
    
    playbook += """

**Lessons learned:**
"""
    
    poor_decisions = [d for d in decisions if d.get("outcome", 10) <= 4]
    if poor_decisions:
        for decision in poor_decisions[-3:]:  # Last 3 poor decisions
            playbook += f"\n- **Avoid:** {decision['decision']}"
            if decision.get("outcome_notes"):
                playbook += f"\n  _{decision['outcome_notes']}_"
    else:
        playbook += "\n- *No bad decisions tracked yet - nice!*"
    
    playbook += """

---

## 🎯 Decision Framework

**Before making important decisions:**

1. ✅ Is it your best decision hour? (Check patterns above)
2. ✅ Are you confident? (High confidence = better outcomes)
3. ✅ Have you slept well? (Energy affects decisions)
4. ✅ Is it urgent or can it wait for optimal timing?

**After decisions:**
- Log them immediately (while context is fresh)
- Set reminder to record outcome in 1-7 days
- Review monthly to identify patterns

---

*This playbook improves as you log more decisions. Aim for 20+ decisions to see strong patterns.*
"""
    
    with open(PLAYBOOK, "w") as f:
        f.write(playbook)
    
    return playbook

def get_pending_outcomes():
    """Get decisions that need outcomes recorded"""
    decisions = load_decisions()["decisions"]
    
    pending = [d for d in decisions if d.get("outcome") is None]
    
    # Check age
    aged_pending = []
    for decision in pending:
        timestamp = datetime.fromisoformat(decision["timestamp"])
        age_hours = (datetime.now() - timestamp).total_seconds() / 3600
        
        if age_hours >= 24:  # At least 1 day old
            aged_pending.append({
                **decision,
                "age_days": int(age_hours / 24)
            })
    
    return aged_pending

def main():
    """CLI for decision logging"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 decision_logger.py log '<decision>' '<context>' [category]")
        print("  python3 decision_logger.py outcome <id> <rating> '<notes>'")
        print("  python3 decision_logger.py analyze")
        print("  python3 decision_logger.py playbook")
        print("  python3 decision_logger.py pending")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "log":
        if len(sys.argv) < 3:
            print("Error: Provide decision text")
            sys.exit(1)
        
        decision_text = sys.argv[2]
        context = sys.argv[3] if len(sys.argv) > 3 else ""
        category = sys.argv[4] if len(sys.argv) > 4 else "general"
        
        log_decision(decision_text, context, category)
    
    elif command == "outcome":
        if len(sys.argv) < 4:
            print("Error: Provide decision ID and rating (1-10)")
            sys.exit(1)
        
        decision_id = int(sys.argv[2])
        rating = int(sys.argv[3])
        notes = sys.argv[4] if len(sys.argv) > 4 else ""
        
        record_outcome(decision_id, rating, notes)
    
    elif command == "analyze":
        print("🔍 Analyzing decision patterns...\n")
        insights = analyze_decision_patterns()
        
        if isinstance(insights, dict) and "message" in insights:
            print(insights["message"])
        else:
            print(json.dumps(insights, indent=2))
    
    elif command == "playbook":
        print("📖 Generating decision playbook...\n")
        generate_playbook()
        print(f"✅ Playbook generated: {PLAYBOOK}")
        print("\nView it: cat ~/clawd/memory/decision_playbook.md")
    
    elif command == "pending":
        print("⏳ Decisions pending outcome:\n")
        pending = get_pending_outcomes()
        
        if not pending:
            print("No pending decisions (all tracked!)")
        else:
            for decision in pending:
                print(f"#{decision['id']} ({decision['age_days']} days ago)")
                print(f"  Decision: {decision['decision']}")
                print(f"  Record: python3 decision_logger.py outcome {decision['id']} <1-10> '<notes>'\n")

if __name__ == "__main__":
    main()

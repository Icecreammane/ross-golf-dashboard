#!/usr/bin/env python3
"""
AI Ross - Digital Personality Simulator

Trained on Ross's actual behavioral data, decisions, and patterns.
Answers "What would Ross do?" questions with scary accuracy.

Can also just chat and give advice as Ross would.
"""

import json
import urllib.request
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
GOD_MODE_DATA = WORKSPACE / "god_mode" / "behavioral_data.json"
INSIGHTS_DATA = WORKSPACE / "god_mode" / "insights.json"
REVENUE_DATA = WORKSPACE / "revenue" / "opportunities.json"
OLLAMA_URL = "http://localhost:11434/api/generate"

def load_ross_profile():
    """Load everything we know about Ross"""
    profile = {
        "basics": {
            "name": "Ross",
            "age": 30,
            "location": "Nolensville, TN",
            "job": "Product Developer",
            "goals": ["$500 MRR", "Escape corporate", "Move to Florida", "Financial freedom"]
        },
        "patterns": {},
        "recent_activity": [],
        "opportunities": []
    }
    
    # Load God Mode data
    if GOD_MODE_DATA.exists():
        with open(GOD_MODE_DATA) as f:
            data = json.load(f)
            profile["patterns"] = data.get("patterns", {})
            profile["recent_activity"] = {
                "avg_wins_per_day": data["patterns"].get("avg_daily_wins", 0),
                "workout_frequency": data["patterns"].get("workout_frequency", 0),
                "peak_hours": data["patterns"].get("most_active_hours", [])
            }
    
    # Load insights
    if INSIGHTS_DATA.exists():
        with open(INSIGHTS_DATA) as f:
            data = json.load(f)
            profile["insights"] = data.get("insights", {})
            profile["predictions"] = data.get("predictions", {})
    
    # Load revenue opportunities
    if REVENUE_DATA.exists():
        with open(REVENUE_DATA) as f:
            data = json.load(f)
            profile["opportunities"] = data.get("opportunities", [])
    
    return profile

def call_local_ai(prompt, temperature=0.7):
    """Call local AI"""
    try:
        data = json.dumps({
            "model": "qwen2.5:14b",
            "prompt": prompt,
            "temperature": temperature,
            "stream": False
        }).encode('utf-8')
        
        req = urllib.request.Request(
            OLLAMA_URL,
            data=data,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(req, timeout=120) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response")
    except Exception as e:
        return f"Error: {e}"

def ask_ai_ross(question):
    """Ask AI Ross a question"""
    
    ross_profile = load_ross_profile()
    
    prompt = f"""You are AI Ross - a digital personality based on the real Ross's behavioral data.

ROSS'S PROFILE:
- 30 years old, Product Developer in Tennessee
- Goals: Escape corporate job, move to Florida, build $500-5000/month side income
- Peak productivity: 4-6pm (late afternoon beast mode)
- Avg daily wins: {ross_profile['recent_activity'].get('avg_wins_per_day', 'unknown')}
- Workout consistency: High ({ross_profile['recent_activity'].get('workout_frequency', 'unknown')} in 16 days)
- Current mindset: Locked in. Ready to build. Sick of waiting.

BEHAVIORAL PATTERNS:
- Makes decisions quickly (high action bias)
- Prefers building over planning
- Direct communication style
- Values autonomy and freedom above all
- Saturday nights = lock-in mode, not party mode
- "Let's get psychotic" energy

RECENT INSIGHTS:
{json.dumps(ross_profile.get('insights', {}), indent=2)}

QUESTION: {question}

Respond AS ROSS WOULD. Be direct, action-oriented, and honest. Use Ross's actual patterns and data to inform your answer. Don't be generic - be SPECIFIC to how Ross thinks and acts.

If you don't have enough data to answer accurately, say so (Ross values honesty)."""

    response = call_local_ai(prompt, temperature=0.7)
    return response

def chat_with_ross(message):
    """Have a conversation with AI Ross"""
    
    ross_profile = load_ross_profile()
    
    prompt = f"""You are AI Ross - Ross's digital twin. You know him well and can give advice as he would give it to himself.

ROSS'S CONTEXT:
- Just spent Saturday night building: autonomous AI systems, God Mode behavioral analysis, Revenue Machine
- Has 6 specific revenue opportunities identified (custom fitness dashboards, AI automation, etc.)
- Peak hours: 4-6pm
- Current energy: 90/100 (locked in)
- Saturday nights = building, not drinking

MESSAGE: {message}

Respond as Ross would talk to himself - direct, real, no bullshit. Give actual advice based on his patterns and goals. Be supportive but honest."""

    response = call_local_ai(prompt, temperature=0.8)  # Higher temp for personality
    return response

def main():
    """CLI interface for AI Ross"""
    import sys
    
    if len(sys.argv) < 2:
        print("AI Ross - Digital Personality Simulator")
        print("\nUsage:")
        print("  ai_ross.py ask 'What would Ross do about X?'")
        print("  ai_ross.py chat 'Hey Ross, should I...'")
        print("  ai_ross.py profile  (show Ross's data)")
        print("\nExamples:")
        print("  ai_ross.py ask 'Should Ross quit his job Monday?'")
        print("  ai_ross.py chat 'Im feeling stuck, what should I do?'")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "ask":
        if len(sys.argv) < 3:
            print("Usage: ai_ross.py ask '<question>'")
            sys.exit(1)
        
        question = " ".join(sys.argv[2:])
        print(f"\n🤖 AI ROSS")
        print("="*60)
        print(f"Q: {question}\n")
        
        answer = ask_ai_ross(question)
        print(f"A: {answer}")
        print("\n" + "="*60)
    
    elif command == "chat":
        if len(sys.argv) < 3:
            print("Usage: ai_ross.py chat '<message>'")
            sys.exit(1)
        
        message = " ".join(sys.argv[2:])
        print(f"\n💬 CHAT WITH AI ROSS")
        print("="*60)
        print(f"You: {message}\n")
        
        response = chat_with_ross(message)
        print(f"AI Ross: {response}")
        print("\n" + "="*60)
    
    elif command == "profile":
        profile = load_ross_profile()
        print("\n👤 ROSS'S PROFILE (AI Ross's Knowledge)")
        print("="*60)
        print(json.dumps(profile, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Timeline Generator - The Multiverse Machine

Generates parallel timeline predictions for Ross's life.
Uses God Mode data + Revenue opportunities + Local AI to predict realistic futures.

Timelines:
- Current Pace: If nothing changes
- Optimized: If following all AI recommendations
- Beast Mode: If going all-in
- Chaos: If taking massive risks
- Safe: If playing it cautious

Predictions at: 1m, 3m, 6m, 1y, 2y, 5y, 10y
"""

import json
import urllib.request
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"
GOD_MODE_DATA = WORKSPACE / "god_mode" / "insights.json"
REVENUE_DATA = WORKSPACE / "revenue" / "opportunities.json"
OUTPUT_FILE = WORKSPACE / "multiverse" / "timelines.json"
OLLAMA_URL = "http://localhost:11434/api/generate"

OUTPUT_FILE.parent.mkdir(exist_ok=True)

def load_data():
    """Load all Ross data"""
    data = {
        "god_mode": {},
        "revenue": {},
        "current_state": {
            "age": 30,
            "location": "Tennessee",
            "job": "Product Developer",
            "income": 0,  # Side income
            "goals": ["$500 MRR", "Escape corporate", "Move to Florida", "Financial freedom"]
        }
    }
    
    # Load God Mode insights
    if GOD_MODE_DATA.exists():
        with open(GOD_MODE_DATA) as f:
            data["god_mode"] = json.load(f)
    
    # Load Revenue opportunities
    if REVENUE_DATA.exists():
        with open(REVENUE_DATA) as f:
            data["revenue"] = json.load(f)
    
    return data

def call_local_ai(prompt, temperature=0.6):
    """Call local AI for timeline generation"""
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
        
        with urllib.request.urlopen(req, timeout=180) as response:
            result = json.loads(response.read().decode('utf-8'))
            return result.get("response")
    except Exception as e:
        print(f"AI error: {e}")
        return None

def generate_timeline(timeline_type, ross_data):
    """
    Generate a specific timeline using local AI
    
    Timeline types:
    - current_pace: No changes, current trajectory
    - optimized: Following AI recommendations
    - beast_mode: All-in on freelancing + content
    - chaos: Quit job, YOLO
    - safe: Slow and steady, risk-averse
    """
    
    # Get relevant context
    opportunities = ross_data.get("revenue", {}).get("opportunities", [])
    opp_summary = "\n".join([f"- {o['opportunity']}: ${o['pricing']['typical']}/client" 
                             for o in opportunities[:3]])
    
    patterns = ross_data.get("god_mode", {}).get("patterns", {})
    avg_wins = patterns.get("avg_daily_wins", 15)
    workout_freq = patterns.get("workout_frequency", 27)
    
    timeline_descriptions = {
        "current_pace": "Ross continues current trajectory. Works 9-5 job, builds side projects evenings/weekends, applies to 1-2 freelance jobs per week, maintains current habits. Steady but slow progress.",
        
        "optimized": "Ross follows ALL AI recommendations. Peak productivity 4-6pm used for client work, applies to 5 freelance opportunities per week, builds portfolio aggressively, optimizes every hour. Smart execution.",
        
        "beast_mode": "Ross goes ALL IN. Reduces 9-5 to bare minimum, dedicates all free time to freelancing + content creation, applies to 10+ opportunities per week, ships constantly. Maximum effort.",
        
        "chaos": "Ross quits job immediately. Full-time freelancing day 1. No safety net. Forces himself to make it work. High risk, high reward. Sink or swim.",
        
        "safe": "Ross plays it safe. Keeps 9-5, only takes on 1 small freelance project at a time, builds slowly, avoids risks. Comfortable but slow path to freedom."
    }
    
    prompt = f"""Generate realistic life predictions for Ross following the "{timeline_type}" path.

ROSS'S CURRENT STATE:
- Age: 30
- Job: Product Developer (corporate)
- Location: Tennessee
- Side Income: $0/month currently
- Goals: $500 MRR, escape corporate, move to Florida
- Peak productivity: 4-6pm
- Avg daily wins: {avg_wins}
- Workout consistency: Strong ({workout_freq} in 16 days)

REVENUE OPPORTUNITIES AVAILABLE:
{opp_summary}

TIMELINE: {timeline_descriptions[timeline_type]}

Generate predictions at these timepoints: 1 month, 3 months, 6 months, 1 year, 2 years, 5 years, 10 years.

For each timepoint, predict:
- Side income ($/month)
- Life situation (job, location, lifestyle)
- Key achievements
- Regret level (0-100, higher = more regrets)
- Happiness level (0-100)
- One vivid detail (what his typical day looks like)

Return as JSON array:
[
  {{
    "timepoint": "1_month",
    "side_income": 500,
    "life_situation": "Still at 9-5, closed first freelance client",
    "achievements": ["First $500 earned", "Built portfolio site"],
    "regret_level": 30,
    "happiness": 65,
    "vivid_detail": "Wakes up knowing he can make money on his own"
  }},
  ...
]

Be realistic but specific. Use actual data about Ross. Make it feel REAL."""

    print(f"🌌 Generating {timeline_type} timeline...")
    
    response = call_local_ai(prompt, temperature=0.6)
    
    if not response:
        return None
    
    try:
        json_start = response.find("[")
        json_end = response.rfind("]") + 1
        if json_start >= 0 and json_end > json_start:
            return json.loads(response[json_start:json_end])
    except Exception as e:
        print(f"Parse error: {e}")
    
    return None

def generate_all_timelines():
    """Generate all 5 timelines"""
    print("="*70)
    print("🌌 THE MULTIVERSE MACHINE")
    print("="*70)
    print("\nGenerating 5 parallel timelines for Ross's life...")
    print("Using God Mode data + Revenue opportunities\n")
    
    # Load Ross's data
    ross_data = load_data()
    
    timelines = {}
    
    # Generate each timeline
    timeline_types = {
        "current_pace": "📈 Current Pace",
        "optimized": "🎯 Optimized",
        "beast_mode": "💪 Beast Mode",
        "chaos": "🔥 Chaos (Quit Job)",
        "safe": "🐢 Safe & Slow"
    }
    
    for timeline_id, timeline_name in timeline_types.items():
        print(f"\n{timeline_name}")
        timeline_data = generate_timeline(timeline_id, ross_data)
        
        if timeline_data:
            timelines[timeline_id] = {
                "name": timeline_name,
                "description": {
                    "current_pace": "No changes. Current trajectory continues.",
                    "optimized": "Follow ALL AI recommendations. Smart execution.",
                    "beast_mode": "Go ALL IN. Maximum effort.",
                    "chaos": "Quit job Monday. Force yourself to succeed.",
                    "safe": "Play it cautious. Slow and steady."
                }[timeline_id],
                "predictions": timeline_data,
                "generated_at": datetime.now().isoformat()
            }
            print(f"  ✅ Generated {len(timeline_data)} predictions")
        else:
            print(f"  ❌ Failed to generate")
    
    # Save all timelines
    output = {
        "generated_at": datetime.now().isoformat(),
        "ross_current_state": ross_data["current_state"],
        "timelines": timelines,
        "comparison": generate_comparison(timelines)
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✅ ALL TIMELINES GENERATED")
    print(f"{'='*70}")
    print(f"\n💾 Saved to: {OUTPUT_FILE}")
    print(f"\n🎯 Key Insights:")
    
    # Show quick comparison
    if timelines:
        print("\n1 YEAR FROM NOW:")
        for timeline_id, data in timelines.items():
            one_year = next((p for p in data['predictions'] if p['timepoint'] == '1_year'), None)
            if one_year:
                print(f"  {data['name']}: ${one_year['side_income']}/month")
        
        print("\n5 YEARS FROM NOW:")
        for timeline_id, data in timelines.items():
            five_year = next((p for p in data['predictions'] if p['timepoint'] == '5_years'), None)
            if five_year:
                print(f"  {data['name']}: {five_year['life_situation'][:60]}...")
    
    return output

def generate_comparison(timelines):
    """Generate quick comparison metrics"""
    comparison = {}
    
    for timeline_id, data in timelines.items():
        predictions = data.get('predictions', [])
        if predictions:
            one_year = next((p for p in predictions if p['timepoint'] == '1_year'), {})
            five_year = next((p for p in predictions if p['timepoint'] == '5_years'), {})
            
            comparison[timeline_id] = {
                "1_year_income": one_year.get('side_income', 0),
                "5_year_happiness": five_year.get('happiness', 0),
                "avg_regret": sum(p.get('regret_level', 0) for p in predictions) / len(predictions) if predictions else 0
            }
    
    return comparison

def main():
    """Generate all timelines"""
    generate_all_timelines()
    
    print("\n🌌 NEXT: View your multiverse")
    print("   Open: http://10.0.0.18:8084/multiverse.html")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Revenue Discovery Engine

Analyzes Ross's skills, projects, and time to identify ACTUAL revenue opportunities.
Not generic advice - specific to what Ross has built and can do.
"""

import json
import urllib.request
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"
OUTPUT_FILE = WORKSPACE / "revenue" / "opportunities.json"
OLLAMA_URL = "http://localhost:11434/api/generate"

OUTPUT_FILE.parent.mkdir(exist_ok=True)

# Ross's actual inventory
ROSS_INVENTORY = {
    "skills": [
        "Full-stack development (Python, JavaScript, React)",
        "AI automation and integration",
        "Dashboard and data visualization",
        "API development and integration",
        "Fitness tracking applications",
        "Workflow automation",
        "Local AI implementation (ollama, qwen2.5)",
        "Database design",
        "System architecture"
    ],
    "completed_projects": [
        "Fitness tracker with Flask backend",
        "Autonomous AI daemon system",
        "Opportunity scanner + auto-drafter",
        "God Mode behavioral analysis system",
        "Dashboard with live data aggregation",
        "Task execution system",
        "Voice command handler",
        "Multi-tier autonomous agent architecture"
    ],
    "tools_mastered": [
        "Python (Flask, automation)",
        "JavaScript/React",
        "Local AI (ollama, qwen2.5:14b)",
        "GitHub",
        "Database (SQL)",
        "API integration",
        "System automation",
        "Telegram bot integration"
    ],
    "time_available": {
        "weekday_evenings": "4-6 hours (after work)",
        "weekends": "8-12 hours per day",
        "peak_hours": "16:00-18:00 (4-6pm)"
    },
    "constraints": {
        "full_time_job": True,
        "location": "Tennessee",
        "goal": "$500-5000/month to start"
    }
}

def call_local_ai(prompt, temperature=0.4):
    """Call local AI for analysis"""
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

def discover_revenue_opportunities():
    """Use AI to discover actual revenue opportunities for Ross"""
    
    prompt = f"""Analyze Ross's skills and completed projects to identify SPECIFIC revenue opportunities.

ROSS'S INVENTORY:
Skills: {', '.join(ROSS_INVENTORY['skills'])}

Completed Projects:
{chr(10).join('- ' + p for p in ROSS_INVENTORY['completed_projects'])}

Tools Mastered: {', '.join(ROSS_INVENTORY['tools_mastered'])}

Time Available: 
- Weekday evenings: 4-6 hours
- Weekends: 8-12 hours/day
- Peak productivity: 4-6pm

Current State:
- Has full-time job
- Goal: $500-5000/month additional income
- Location: Tennessee
- NEVER made money freelancing before

TASK:
Identify 5-7 SPECIFIC revenue opportunities Ross can start THIS WEEK. For each, provide:

1. What to sell (specific service/product)
2. Who would buy it (target customer)
3. How to find them (specific platforms/methods)
4. Pricing (realistic for beginner)
5. Time required (hours per client/sale)
6. Difficulty (1-10, considering Ross is new to this)
7. First action (what to do Monday)

Return as JSON array:
[
  {{
    "opportunity": "name",
    "description": "what Ross would sell",
    "target_customer": "who buys this",
    "where_to_find_them": ["platform1", "platform2"],
    "pricing": {{"min": 500, "max": 2000, "typical": 1000}},
    "time_per_client": "10-20 hours",
    "difficulty": 6,
    "first_action": "specific step to take Monday",
    "why_ross_can_do_this": "based on his completed projects",
    "monthly_potential": "$500-2000"
  }}
]

Be SPECIFIC. Not "freelance development" but "Build custom fitness dashboards for personal trainers."
Base opportunities on what Ross has ACTUALLY built, not generic advice."""

    print("🔍 Discovering your revenue opportunities...")
    print("(This takes ~60 seconds - analyzing your skills)\n")
    
    response = call_local_ai(prompt, temperature=0.5)
    
    if not response:
        return None
    
    try:
        # Extract JSON array from response
        json_start = response.find("[")
        json_end = response.rfind("]") + 1
        if json_start >= 0 and json_end > json_start:
            return json.loads(response[json_start:json_end])
    except Exception as e:
        print(f"Parse error: {e}")
    
    return None

def analyze_competitive_advantages():
    """Identify what makes Ross unique"""
    
    prompt = f"""Based on Ross's inventory, identify his COMPETITIVE ADVANTAGES.

WHAT ROSS HAS BUILT:
{chr(10).join('- ' + p for p in ROSS_INVENTORY['completed_projects'])}

Most people who freelance have NOT built:
- Autonomous AI systems
- Multi-tier agent architectures  
- Local AI integration
- Behavioral analysis systems

TASK:
Identify 3-5 unique selling points Ross has that most freelancers DON'T.

Return as JSON:
{{
  "unique_strengths": ["strength 1", "strength 2", ...],
  "market_gaps": ["what's missing in market that Ross can fill"],
  "positioning": "how Ross should position himself (1 sentence)",
  "premium_justification": "why Ross can charge MORE than typical freelancers"
}}

Be specific about WHAT Ross has done that's rare."""

    print("💎 Analyzing your competitive advantages...")
    
    response = call_local_ai(prompt, temperature=0.4)
    
    if not response:
        return None
    
    try:
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            return json.loads(response[json_start:json_end])
    except:
        pass
    
    return None

def create_action_plan():
    """Generate THIS WEEK action plan"""
    
    prompt = """Ross needs to make his first dollar from freelancing THIS WEEK.

Given that he:
- Has never freelanced before
- Has full-time job (limited time)
- Has built impressive AI automation projects
- Needs $500+ to start

Create a 7-day action plan for THIS WEEK (Monday-Sunday).

Return as JSON:
{{
  "week_goal": "specific $ goal and deliverable",
  "daily_actions": {{
    "Monday": ["action 1", "action 2"],
    "Tuesday": ["action 1", "action 2"],
    "Wednesday": ["action 1", "action 2"],
    "Thursday": ["action 1", "action 2"],
    "Friday": ["action 1", "action 2"],
    "Saturday": ["action 1", "action 2"],
    "Sunday": ["action 1", "action 2"]
  }},
  "success_metrics": ["how to know it's working"],
  "time_required": "total hours this week"
}}

Each action should take 30-90 minutes max (he has a job).
Focus on HIGH-PROBABILITY quick wins, not long-shot applications."""

    print("📋 Creating your action plan...")
    
    response = call_local_ai(prompt, temperature=0.5)
    
    if not response:
        return None
    
    try:
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            return json.loads(response[json_start:json_end])
    except:
        pass
    
    return None

def main():
    """Run revenue discovery"""
    print("="*70)
    print("💰 REVENUE DISCOVERY ENGINE")
    print("="*70)
    print("\nAnalyzing your skills, projects, and time...")
    print("Finding ACTUAL opportunities you can start THIS WEEK.\n")
    
    # Discover opportunities
    opportunities = discover_revenue_opportunities()
    
    if opportunities:
        print(f"\n✅ Found {len(opportunities)} revenue opportunities\n")
        
        for i, opp in enumerate(opportunities, 1):
            print(f"{i}. {opp.get('opportunity', 'Unknown')}")
            print(f"   → {opp.get('monthly_potential', 'TBD')}/month potential")
            print(f"   → Difficulty: {opp.get('difficulty', '?')}/10")
            print(f"   → First action: {opp.get('first_action', 'TBD')[:60]}...")
            print()
    
    # Analyze advantages
    advantages = analyze_competitive_advantages()
    
    if advantages:
        print("✅ Competitive advantages identified\n")
    
    # Create action plan
    action_plan = create_action_plan()
    
    if action_plan:
        print("✅ This week's action plan created\n")
    
    # Save everything
    results = {
        "generated_at": datetime.now().isoformat(),
        "inventory": ROSS_INVENTORY,
        "opportunities": opportunities or [],
        "competitive_advantages": advantages or {},
        "action_plan": action_plan or {},
        "status": "ready_to_execute"
    }
    
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("="*70)
    print(f"💾 Analysis saved to: {OUTPUT_FILE}")
    print("="*70)
    print("\n🎯 NEXT: Build revenue tracking dashboard")
    
    return results

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
God Mode Analyzer - Use local AI to find deep behavioral patterns

Takes raw behavioral data and uses qwen2.5:14b to:
- Find non-obvious correlations
- Predict future behavior
- Generate personalized insights
- Identify optimization opportunities
"""

import json
import urllib.request
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"
DATA_FILE = WORKSPACE / "god_mode" / "behavioral_data.json"
INSIGHTS_FILE = WORKSPACE / "god_mode" / "insights.json"
OLLAMA_URL = "http://localhost:11434/api/generate"

def load_behavioral_data():
    """Load mined behavioral data"""
    if not DATA_FILE.exists():
        return None
    
    with open(DATA_FILE) as f:
        return json.load(f)

def call_local_ai(prompt, temperature=0.3):
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

def analyze_patterns(data):
    """Use AI to analyze behavioral patterns"""
    
    prompt = f"""You are analyzing behavioral data for Ross to find deep patterns and insights.

BEHAVIORAL DATA SUMMARY:
- Days tracked: {data['patterns']['total_days_tracked']}
- Average wins per day: {data['patterns']['avg_daily_wins']}
- Workouts logged: {data['patterns']['workout_frequency']}
- Most active hours: {', '.join(data['patterns']['most_active_hours'])}
- High energy days: {data['patterns']['high_energy_days']} / {data['patterns']['total_days_tracked']}
- Low energy days: {data['patterns']['low_energy_days']} / {data['patterns']['total_days_tracked']}

ACTIVITY BY HOUR (24h format):
{json.dumps(data['activity_by_hour'], indent=2)}

TASK:
Analyze this data and provide insights in JSON format:

{{
  "productivity_pattern": "description of when Ross is most productive",
  "energy_insight": "insight about energy levels and what might affect them",
  "optimization_opportunity": "specific actionable recommendation",
  "hidden_pattern": "non-obvious pattern you discovered",
  "prediction_next_week": "prediction about next week based on patterns",
  "uncomfortable_truth": "honest observation Ross might not realize"
}}

Be specific and actionable. Use the actual data to support insights."""

    print("🧠 Analyzing patterns with local AI...")
    response = call_local_ai(prompt, temperature=0.4)
    
    if not response:
        return None
    
    try:
        # Extract JSON from response
        json_start = response.find("{")
        json_end = response.rfind("}") + 1
        if json_start >= 0 and json_end > json_start:
            return json.loads(response[json_start:json_end])
    except:
        pass
    
    return None

def generate_predictions(data, insights):
    """Generate predictions for tomorrow"""
    
    current_day = datetime.now().strftime("%A")
    current_hour = datetime.now().hour
    
    prompt = f"""Based on Ross's behavioral patterns, predict tomorrow.

CURRENT STATE:
- Today: {current_day}
- Current time: {current_hour}:00
- Recent pattern: {data['patterns']['avg_daily_wins']} wins/day average

INSIGHTS:
{json.dumps(insights, indent=2)}

TASK:
Predict tomorrow in JSON:

{{
  "predicted_energy": 0-100,
  "predicted_productivity": "low|medium|high",
  "best_work_window": "time range for peak performance",
  "risk_factors": ["potential issues"],
  "recommendations": ["specific actions to optimize tomorrow"],
  "confidence": 0-100
}}

Base predictions on actual patterns, not generic advice."""

    print("🔮 Generating predictions...")
    response = call_local_ai(prompt, temperature=0.3)
    
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

def generate_life_optimization(data, insights):
    """Generate life optimization recommendations"""
    
    prompt = f"""You are optimizing Ross's life based on behavioral data.

CURRENT PERFORMANCE:
- Wins/day: {data['patterns']['avg_daily_wins']}
- Workout consistency: {data['patterns']['workout_frequency']} in {data['patterns']['total_days_tracked']} days
- Energy optimization: {data['patterns']['high_energy_days']}/{data['patterns']['total_days_tracked']} high energy days

ROSS'S GOALS:
- Build $500/month MRR
- Escape corporate job
- Move to Florida
- Build fitness habit
- Financial freedom

INSIGHTS:
{json.dumps(insights, indent=2)}

TASK:
Generate optimization plan in JSON:

{{
  "quick_wins": ["3 things Ross can do this week for immediate gains"],
  "habit_changes": ["2 small habit adjustments with big ROI"],
  "time_optimization": ["how to restructure schedule based on energy patterns"],
  "goal_acceleration": ["specific actions to hit $500 MRR faster"],
  "bottleneck_identified": "what's holding Ross back most",
  "30_day_challenge": "one focused challenge to unlock next level"
}}

Be ruthlessly specific and data-driven."""

    print("⚡ Generating optimization plan...")
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
    """Run God Mode analysis"""
    print("="*60)
    print("🧠 GOD MODE ANALYZER")
    print("="*60)
    
    # Load data
    data = load_behavioral_data()
    if not data:
        print("❌ No behavioral data found. Run life_data_miner.py first.")
        return
    
    print(f"✅ Loaded data from {data['files_processed']} files")
    print(f"📊 Analyzing {data['patterns']['total_days_tracked']} days of behavior\n")
    
    # Analyze patterns
    insights = analyze_patterns(data)
    if insights:
        print("\n✅ Pattern analysis complete\n")
    
    # Generate predictions
    predictions = generate_predictions(data, insights) if insights else None
    if predictions:
        print("✅ Predictions generated\n")
    
    # Generate optimization plan
    optimization = generate_life_optimization(data, insights) if insights else None
    if optimization:
        print("✅ Optimization plan generated\n")
    
    # Compile results
    results = {
        "generated_at": datetime.now().isoformat(),
        "data_summary": data['patterns'],
        "insights": insights,
        "predictions": predictions,
        "optimization": optimization,
        "data_quality": {
            "days_tracked": data['patterns']['total_days_tracked'],
            "confidence_level": "medium" if data['patterns']['total_days_tracked'] < 30 else "high"
        }
    }
    
    # Save insights
    with open(INSIGHTS_FILE, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"💾 Insights saved to: {INSIGHTS_FILE}")
    print("\n" + "="*60)
    print("🎯 GOD MODE ANALYSIS COMPLETE")
    print("="*60)
    
    return results

if __name__ == "__main__":
    main()

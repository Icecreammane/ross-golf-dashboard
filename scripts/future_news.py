#!/usr/bin/env python3
"""
Future News Generator

Generates realistic news articles about Ross's future successes.
"Ross Caster Hits $100k/Year, Moves to Florida Beach House"

Creates screenshot-worthy articles for each timeline.
"""

import json
import urllib.request
from pathlib import Path
from datetime import datetime, timedelta

WORKSPACE = Path.home() / "clawd"
TIMELINES_FILE = WORKSPACE / "multiverse" / "timelines.json"
NEWS_DIR = WORKSPACE / "multiverse" / "news"
OLLAMA_URL = "http://localhost:11434/api/generate"

NEWS_DIR.mkdir(parents=True, exist_ok=True)

def call_local_ai(prompt, temperature=0.7):
    """Generate news article with local AI"""
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
        print(f"AI error: {e}")
        return None

def calculate_future_date(timepoint):
    """Calculate actual future date"""
    months_map = {
        "1_month": 1,
        "3_months": 3,
        "6_months": 6,
        "1_year": 12,
        "2_years": 24,
        "5_years": 60,
        "10_years": 120
    }
    
    months = months_map.get(timepoint, 12)
    future_date = datetime.now() + timedelta(days=months * 30)
    return future_date.strftime("%B %Y")

def generate_news_article(timeline_type, timepoint, prediction_data):
    """Generate a news article about future Ross"""
    
    future_date = calculate_future_date(timepoint)
    income = prediction_data.get('side_income', 0)
    situation = prediction_data.get('life_situation', '')
    achievements = prediction_data.get('achievements', [])
    
    timeline_descriptions = {
        "current_pace": "steady growth",
        "optimized": "strategic execution",
        "beast_mode": "aggressive expansion",
        "chaos": "bold risk-taking",
        "safe": "cautious approach"
    }
    
    approach = timeline_descriptions.get(timeline_type, "unique approach")
    
    prompt = f"""Write a realistic news article about Ross Caster's success.

DATE: {future_date}
ACHIEVEMENT: Making ${income}/month from freelancing/business
SITUATION: {situation}
KEY WINS: {', '.join(achievements) if achievements else 'N/A'}
APPROACH: {approach}

Write a 200-300 word news article in the style of a tech/business publication.

Include:
- Catchy headline
- Opening paragraph with the main achievement
- Quote from Ross about his journey
- Specific numbers and details
- What he's working on next
- Make it feel REAL and professional

Format as:
HEADLINE: [headline]

[Article body]

Be specific and realistic. Reference actual tech/business terms."""

    print(f"  📰 Writing article: {timeline_type} / {timepoint}...")
    
    article = call_local_ai(prompt, temperature=0.7)
    
    if article:
        return {
            "date": future_date,
            "income": income,
            "content": article.strip(),
            "generated_at": datetime.now().isoformat()
        }
    
    return None

def generate_all_news():
    """Generate news articles for all timelines"""
    
    print("="*70)
    print("📰 FUTURE NEWS GENERATOR")
    print("="*70)
    print("\nWriting news articles about your future successes...\n")
    
    # Load timelines
    if not TIMELINES_FILE.exists():
        print("❌ Timelines not generated yet")
        print("   Waiting for timeline_generator.py to finish...")
        return None
    
    with open(TIMELINES_FILE) as f:
        data = json.load(f)
    
    timelines = data.get('timelines', {})
    
    all_articles = {}
    
    # Generate articles for major milestones
    key_timepoints = ['1_year', '5_years']
    
    for timeline_id, timeline_data in timelines.items():
        timeline_name = timeline_data.get('name', timeline_id)
        predictions = timeline_data.get('predictions', [])
        
        print(f"\n{timeline_name} Timeline:")
        
        timeline_articles = {}
        
        for pred in predictions:
            timepoint = pred.get('timepoint')
            if timepoint in key_timepoints and pred.get('side_income', 0) > 0:
                article = generate_news_article(timeline_id, timepoint, pred)
                if article:
                    timeline_articles[timepoint] = article
                    print(f"  ✅ {timepoint.replace('_', ' ')}: ${article['income']}/mo article")
        
        all_articles[timeline_id] = timeline_articles
    
    # Save articles
    output_file = NEWS_DIR / "articles.json"
    with open(output_file, 'w') as f:
        json.dump(all_articles, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"✅ NEWS ARTICLES GENERATED")
    print(f"{'='*70}")
    print(f"\n💾 Saved to: {output_file}")
    print(f"\n📰 Total articles: {sum(len(a) for a in all_articles.values())}")
    
    return all_articles

def show_article(timeline, timepoint):
    """Display a specific news article"""
    
    articles_file = NEWS_DIR / "articles.json"
    if not articles_file.exists():
        print("No articles generated yet")
        return
    
    with open(articles_file) as f:
        all_articles = json.load(f)
    
    timeline_articles = all_articles.get(timeline, {})
    article_data = timeline_articles.get(timepoint)
    
    if article_data:
        print("\n" + "="*70)
        print(f"📰 NEWS FROM THE FUTURE ({article_data['date']})")
        print("="*70)
        print(f"\n{article_data['content']}\n")
        print("="*70)
        print(f"(From {timeline} timeline)")
    else:
        print(f"No article for {timeline} / {timepoint}")

def main():
    """CLI interface"""
    import sys
    
    if len(sys.argv) < 2:
        print("Future News Generator")
        print("\nCommands:")
        print("  generate              - Generate all articles")
        print("  show <timeline> <time> - Show specific article")
        print("\nExamples:")
        print("  generate")
        print("  show beast_mode 5_years")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "generate":
        generate_all_news()
    
    elif command == "show":
        if len(sys.argv) < 4:
            print("Usage: show <timeline> <timepoint>")
            print("\nTimelines: current_pace, optimized, beast_mode, chaos, safe")
            print("Timepoints: 1_year, 5_years")
        else:
            timeline = sys.argv[2]
            timepoint = sys.argv[3]
            show_article(timeline, timepoint)
    
    else:
        print(f"Unknown command: {command}")

if __name__ == "__main__":
    main()

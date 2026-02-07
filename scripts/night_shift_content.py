#!/usr/bin/env python3
"""
Night Shift: Content Generation
Generates tweets, Reddit posts, LinkedIn content using local model
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
OUTPUT_DIR = WORKSPACE / "content" / "night-shift"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def generate_with_ollama(prompt, model="qwen2.5:14b"):
    """Generate content using local Ollama model"""
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=300
        )
        return result.stdout.strip()
    except Exception as e:
        return f"Error: {str(e)}"

def generate_tweets():
    """Generate tweet ideas"""
    prompt = """Generate 20 tweet ideas for a builder working on side projects and fitness.

Themes:
1. Tech tips & productivity (7 tweets)
2. Fitness & health insights (7 tweets)
3. Side project journey / building in public (6 tweets)

For each tweet:
- Make it engaging and authentic
- Include a hook in the first line
- Keep under 280 characters
- No hashtags unless natural

Format as numbered list."""

    content = generate_with_ollama(prompt)
    
    output = f"""# Tweet Ideas - {datetime.now().strftime('%Y-%m-%d')}

Generated at: {datetime.now().strftime('%I:%M %p')}

{content}

---
**Usage:** Pick 3-5, edit to your voice, schedule throughout the week
"""
    
    output_file = OUTPUT_DIR / f"tweets-{datetime.now().strftime('%Y%m%d')}.md"
    with open(output_file, "w") as f:
        f.write(output)
    
    return output_file

def generate_reddit_posts():
    """Generate Reddit post variations"""
    prompt = """Generate 5 Reddit post variations for launching a fitness tracking app.

Each variation should:
- Have a different angle/hook
- Be authentic and not salesy
- Include a story or insight
- End with soft CTA
- Suitable for r/Fitness or r/SideProject

Vary the styles: story, question, insight, problem/solution, results

Format as:
## Post 1: [Title]
[Body]
---"""

    content = generate_with_ollama(prompt)
    
    output = f"""# Reddit Post Ideas - {datetime.now().strftime('%Y-%m-%d')}

Generated at: {datetime.now().strftime('%I:%M %p')}

{content}

---
**Usage:** Pick one, personalize, post when ready to launch
"""
    
    output_file = OUTPUT_DIR / f"reddit-posts-{datetime.now().strftime('%Y%m%d')}.md"
    with open(output_file, "w") as f:
        f.write(output)
    
    return output_file

def generate_linkedin_posts():
    """Generate LinkedIn thought leadership"""
    prompt = """Generate 3 LinkedIn posts for a product developer / side project builder.

Themes:
1. Lesson learned from building (storytelling)
2. Productivity/efficiency insight (value-focused)
3. Industry observation (thought leadership)

Each post:
- Professional but authentic tone
- Hook in first 2 lines
- 150-250 words
- Ends with engagement question

Format as:
## Post 1: [One-line summary]
[Body]
---"""

    content = generate_with_ollama(prompt)
    
    output = f"""# LinkedIn Posts - {datetime.now().strftime('%Y-%m-%d')}

Generated at: {datetime.now().strftime('%I:%M %p')}

{content}

---
**Usage:** Post 1-2 per week, builds professional brand
"""
    
    output_file = OUTPUT_DIR / f"linkedin-{datetime.now().strftime('%Y%m%d')}.md"
    with open(output_file, "w") as f:
        f.write(output)
    
    return output_file

def main():
    print("🎨 Night Shift: Content Generation")
    print("=" * 50)
    
    print("\n1. Generating tweets...")
    tweet_file = generate_tweets()
    print(f"✅ Tweets: {tweet_file}")
    
    print("\n2. Generating Reddit posts...")
    reddit_file = generate_reddit_posts()
    print(f"✅ Reddit: {reddit_file}")
    
    print("\n3. Generating LinkedIn posts...")
    linkedin_file = generate_linkedin_posts()
    print(f"✅ LinkedIn: {linkedin_file}")
    
    print("\n✨ Content generation complete!")
    print(f"📁 Check: {OUTPUT_DIR}")
    
    return {
        "tweets": str(tweet_file),
        "reddit": str(reddit_file),
        "linkedin": str(linkedin_file)
    }

if __name__ == "__main__":
    main()

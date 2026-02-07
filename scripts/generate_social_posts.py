#!/usr/bin/env python3
"""
AI Social Post Generator - Jarvis
Generates social media posts for Ross's side projects
Uses GPT-5.2 for creative content generation
"""

import json
import os
from datetime import datetime
from pathlib import Path

POSTS_DIR = Path.home() / "clawd" / "social_posts"
POSTS_DIR.mkdir(exist_ok=True)

# Post templates and themes
POST_THEMES = [
    "tech_tips",
    "productivity",
    "fitness_motivation",
    "side_project_journey",
    "building_in_public",
    "fantasy_sports_insights",
    "ai_automation"
]

def generate_post(theme, context=""):
    """
    Generate a social media post using AI
    In production, this would call GPT-5.2 API
    """
    
    # Placeholder - would use OpenAI API
    sample_posts = {
        "building_in_public": f"""🚀 Day {datetime.now().day} of building in public

Just shipped a new feature that automates my calendar management.
Now my AI assistant handles scheduling while I focus on what matters.

The best productivity hack? Build tools that work FOR you, not the other way around.

#BuildInPublic #AIAutomation #ProductivityHacks""",
        
        "tech_tips": """💡 Pro tip: Your AI assistant should feel like a co-pilot, not a chatbot.

Here's what changed the game for me:
→ Gave it permission to make decisions
→ Let it build tools proactively
→ Treated it like a team member, not a tool

Result? 10x more productive in one week.

#TechTips #AIProductivity""",
        
        "fitness_motivation": """💪 Fitness tracking just got smarter.

Instead of manually logging every meal, I send voice messages.
My AI parses it, calculates macros, and updates my dashboard.

Tech should make discipline EASIER, not harder.

What's your secret to staying consistent?

#FitnessTech #SmartTracking""",
        
        "fantasy_sports_insights": """🏀 The edge in daily fantasy isn't just about rankings.

It's about having the intel BEFORE everyone else:
→ Injury updates in real-time
→ Auto-pulled rankings from top sources
→ Pattern recognition on what actually wins

Built a dashboard that gives me this edge. Game changer.

#FantasySports #DailyFantasy #NBA"""
    }
    
    post = sample_posts.get(theme, "Post generation placeholder")
    
    return {
        "theme": theme,
        "content": post,
        "timestamp": datetime.now().isoformat(),
        "platforms": ["twitter", "linkedin", "threads"],
        "scheduled": False
    }

def save_post(post_data):
    """Save generated post to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{post_data['theme']}_{timestamp}.json"
    filepath = POSTS_DIR / filename
    
    with open(filepath, 'w') as f:
        json.dump(post_data, f, indent=2)
    
    # Also save as markdown for easy reading
    md_file = POSTS_DIR / filename.replace('.json', '.md')
    with open(md_file, 'w') as f:
        f.write(f"# {post_data['theme']}\n\n")
        f.write(f"{post_data['content']}\n\n")
        f.write(f"**Generated:** {post_data['timestamp']}\n")
        f.write(f"**Platforms:** {', '.join(post_data['platforms'])}\n")
    
    return filepath, md_file

def generate_daily_posts(count=3):
    """Generate multiple posts for the day"""
    import random
    
    themes = random.sample(POST_THEMES, count)
    posts = []
    
    for theme in themes:
        post = generate_post(theme)
        json_path, md_path = save_post(post)
        posts.append({
            "theme": theme,
            "json": str(json_path),
            "markdown": str(md_path)
        })
        print(f"✅ Generated: {theme}")
        print(f"   → {md_path}")
    
    return posts

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        theme = sys.argv[1]
        post = generate_post(theme)
        json_path, md_path = save_post(post)
        print(f"✅ Post generated!")
        print(f"\nPreview:\n{post['content']}\n")
        print(f"Saved to: {md_path}")
    else:
        print("🎨 Generating daily posts...\n")
        posts = generate_daily_posts(3)
        print(f"\n🎉 Generated {len(posts)} posts!")
        print(f"📁 Saved to: {POSTS_DIR}")

#!/usr/bin/env python3
"""
Social Media Post Generator
Generates 2-3 variations of high-value content daily using local LLM
Topics: golf coaching, fitness, monetization journey, products
"""

import json
import logging
import random
import subprocess
from datetime import datetime
from pathlib import Path

# Configuration
WORKSPACE = Path("/Users/clawdbot/clawd")
QUEUE_FILE = WORKSPACE / "data" / "social-posts-queue.json"
LOG_FILE = WORKSPACE / "logs" / "social-scheduler.log"
OLLAMA_MODEL = "llama3.1:8b"  # Fast and capable

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Content themes and prompts
THEMES = {
    "golf_coaching": [
        "Share a counter-intuitive golf swing tip that most coaches get wrong",
        "Explain the mental game aspect of golf that separates pros from amateurs",
        "Share a specific drill that improved your students' accuracy by 20%",
        "Discuss the business of golf coaching and how to scale beyond 1-on-1 lessons"
    ],
    "fitness": [
        "Share a mobility exercise that directly improves golf performance",
        "Explain the connection between core strength and swing power",
        "Discuss the fitness routine that keeps you performing at your peak",
        "Share a recovery technique that changed your training approach"
    ],
    "monetization": [
        "Share a specific revenue milestone and what you learned getting there",
        "Discuss a product launch that succeeded (or failed) and the lessons",
        "Explain how you priced your coaching to match the value you deliver",
        "Share the most profitable hour you spend in your business each week"
    ],
    "products": [
        "Announce a product update and the problem it solves",
        "Share customer results from your coaching program",
        "Explain the transformation your product delivers in concrete terms",
        "Discuss the research behind your latest offering"
    ],
    "high_value": [
        "Share a mental model that changed how you approach your business",
        "Explain a pattern you've noticed that most people miss",
        "Discuss a tactical decision that 10x'd your results",
        "Share the question you ask yourself every day to stay focused"
    ]
}

def call_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Call local Ollama LLM and return generated text"""
    try:
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=120  # Increased timeout for local LLM
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            logger.error(f"Ollama error: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        logger.error("Ollama request timed out")
        return None
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        return None

def generate_post(theme: str, prompt_template: str) -> dict:
    """Generate a single social media post"""
    
    # Simplified, more direct prompt for faster local LLM response
    system_prompt = f"""Write a short Twitter post (under 280 chars) about: {prompt_template}

Style: Direct, conversational, actionable. For a golf coach/fitness expert.
Include 2-3 hashtags. Output only the post text."""

    generated = call_ollama(system_prompt)
    
    if not generated:
        return None
    
    # Parse image suggestion if present
    image_placeholder = None
    post_text = generated
    
    if "[IMAGE:" in generated and "]" in generated:
        start = generated.find("[IMAGE:")
        end = generated.find("]", start) + 1
        image_placeholder = generated[start:end]
        post_text = generated[:start].strip() + " " + generated[end:].strip()
        post_text = post_text.strip()
    
    return {
        "id": f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
        "text": post_text,
        "image_placeholder": image_placeholder,
        "theme": theme,
        "generated_at": datetime.now().isoformat(),
        "scheduled_for": None,  # Will be assigned by posting script
        "posted": False,
        "posted_at": None,
        "twitter_id": None
    }

def load_queue() -> list:
    """Load existing queue or create new"""
    if QUEUE_FILE.exists():
        try:
            with open(QUEUE_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading queue: {e}")
            return []
    return []

def save_queue(queue: list):
    """Save queue to file"""
    QUEUE_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(QUEUE_FILE, 'w') as f:
        json.dump(queue, f, indent=2)

def generate_daily_batch():
    """Generate 2-3 post variations for the day"""
    logger.info("Starting daily post generation batch")
    
    # Select 2-3 random themes
    num_posts = random.randint(2, 3)
    selected_themes = random.sample(list(THEMES.keys()), num_posts)
    
    queue = load_queue()
    generated_count = 0
    
    for theme in selected_themes:
        prompt = random.choice(THEMES[theme])
        logger.info(f"Generating post for theme: {theme}")
        
        post = generate_post(theme, prompt)
        
        if post:
            queue.append(post)
            generated_count += 1
            logger.info(f"✅ Generated post: {post['id']}")
            logger.info(f"   Text: {post['text'][:100]}...")
        else:
            logger.error(f"❌ Failed to generate post for theme: {theme}")
    
    # Remove posted items older than 7 days to keep queue clean
    cutoff = datetime.now().timestamp() - (7 * 24 * 60 * 60)
    queue = [
        p for p in queue 
        if not p['posted'] or 
        (p['posted_at'] and datetime.fromisoformat(p['posted_at']).timestamp() > cutoff)
    ]
    
    save_queue(queue)
    
    logger.info(f"✅ Batch complete: {generated_count} posts generated")
    logger.info(f"📊 Queue status: {len([p for p in queue if not p['posted']])} unposted, {len(queue)} total")
    
    return generated_count

if __name__ == "__main__":
    try:
        count = generate_daily_batch()
        print(f"✅ Generated {count} social media posts")
        exit(0)
    except Exception as e:
        logger.error(f"Fatal error in post generation: {e}", exc_info=True)
        print(f"❌ Error: {e}")
        exit(1)

#!/usr/bin/env python3
"""
Social Media Post Generator v2
Fast template-based generation with optional LLM enhancement
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
OLLAMA_MODEL = "qwen2.5:32b-instruct-q4_K_M"
USE_LLM = False  # Set to True to use LLM, False for fast templates

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

# Content templates with variations
POST_TEMPLATES = {
    "golf_coaching": [
        "Most golfers focus on their swing plane. But the real issue? Hip rotation timing. If your hips fire before your shoulders load, you're losing 20+ yards. #GolfTips #GolfCoaching #GolfSwing",
        "The #1 mistake I see in amateur swings: trying to hit the ball hard. Focus on tempo instead. Power comes from sequence, not force. #GolfCoaching #GolfLife #GolfTips",
        "Want more distance? Stop thinking about your arms. Your power comes from the ground up - legs, hips, core, then arms. Master the kinetic chain. #GolfFitness #GolfCoaching",
        "Mental game beats physical skill at golf. The difference between a 90 and 80? Not talent. It's how you handle bad shots. #GolfMindset #GolfCoaching #MentalGame",
        "Teaching golf for 10+ years taught me: Students don't need more technique. They need more clarity on the ONE thing holding them back. #GolfCoaching #GolfTips"
    ],
    "fitness": [
        "Golfers: Your core strength directly impacts your clubhead speed. 20 minutes of rotational exercises = 10+ yards. Do the work. #GolfFitness #Fitness #GolfTraining",
        "Recovery is training. If you're sore from yesterday's workout, you're not ready for today's. Listen to your body. #FitnessJourney #Recovery #Training",
        "Mobility > Flexibility for golf. You don't need to be flexible like a gymnast. You need to move efficiently through YOUR swing range. #GolfFitness #Mobility",
        "The fitness routine that transformed my game: 3x/week strength, 2x/week mobility, 1x/week cardio. Simple. Sustainable. Effective. #FitnessRoutine #Golf #Training",
        "Core exercises for golf aren't crunches. They're rotational movements under load. Anti-rotation work. Stability training. #CoreStrength #GolfFitness"
    ],
    "monetization": [
        "Hit $10K/month by doing ONE thing: Raising my prices to match the value I deliver. Stopped discounting. Started owning my worth. #EntrepreneurLife #Monetization",
        "The most profitable hour in my business? The one I spend planning content. Consistent value = consistent income. #ContentStrategy #Entrepreneur #Business",
        "Lesson learned at $50K revenue: 1-on-1 coaching doesn't scale. Digital products do. Now building systems that work while I sleep. #DigitalProducts #PassiveIncome",
        "Pricing insight: People don't pay for coaching. They pay for transformation. Once I understood that, revenue doubled. #BusinessGrowth #Coaching #Value",
        "Revenue milestone: First $100K year. The lesson? Consistency beats intensity. Show up every day. Deliver value. Repeat. #RevenueGoals #Entrepreneur"
    ],
    "products": [
        "New program launching: Golf Fundamentals Reset. 6 weeks to rebuild your swing from the ground up. DM for early access. #GolfProgram #GolfCoaching",
        "Student result: Sarah went from 95 to 82 in 12 weeks using my Core-to-Club system. The proof is in the performance. #GolfResults #Transformation",
        "Behind the scenes: Every drill in my programs is tested on 50+ students first. If it doesn't work for them, it doesn't make the cut. #QualityControl #Golf",
        "Product update: Added video analysis feature to the coaching app. Upload your swing, get detailed feedback within 24hrs. #GolfTech #Innovation",
        "My signature product solves ONE problem: Inconsistent ball striking. Everything else is noise. Stay focused on what matters. #GolfCoaching #Products"
    ],
    "high_value": [
        "Mental model that changed my business: Work backwards from the outcome. What does success look like? Now reverse-engineer the path. #Strategy #BusinessThinking",
        "Pattern I've noticed: People overestimate what they can do in a week. Underestimate what they can do in a year. Think long-term. #Growth #Mindset",
        "Tactical decision that 10x'd results: Batch creating content once/week instead of daily scrambling. More time for delivery. #Productivity #ContentCreation",
        "Question I ask myself daily: 'Will this matter in 6 months?' If no, it's a distraction. Stay ruthlessly focused. #Focus #Prioritization #Success",
        "Most valuable skill I've developed: Saying no to good opportunities so I can say yes to great ones. Opportunity cost is real. #Decisions #Strategy"
    ]
}

def call_ollama(prompt: str, model: str = OLLAMA_MODEL) -> str:
    """Call local Ollama LLM and return generated text (optional)"""
    try:
        logger.info("Calling Ollama LLM...")
        result = subprocess.run(
            ["ollama", "run", model, prompt],
            capture_output=True,
            text=True,
            timeout=180
        )
        
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            logger.error(f"Ollama error: {result.stderr}")
            return None
    except subprocess.TimeoutExpired:
        logger.error("Ollama request timed out after 180s")
        return None
    except Exception as e:
        logger.error(f"Error calling Ollama: {e}")
        return None

def generate_post_from_template(theme: str) -> dict:
    """Generate post from template (fast method)"""
    templates = POST_TEMPLATES.get(theme, [])
    if not templates:
        logger.error(f"No templates found for theme: {theme}")
        return None
    
    post_text = random.choice(templates)
    
    # Check if image would add value (simple heuristic)
    image_placeholder = None
    if theme in ["golf_coaching", "fitness", "products"]:
        if random.random() < 0.3:  # 30% chance of image suggestion
            if theme == "golf_coaching":
                image_placeholder = "[IMAGE: Golf swing sequence or drill demonstration]"
            elif theme == "fitness":
                image_placeholder = "[IMAGE: Exercise demonstration or before/after]"
            elif theme == "products":
                image_placeholder = "[IMAGE: Product screenshot or student testimonial]"
    
    return {
        "id": f"post_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}",
        "text": post_text,
        "image_placeholder": image_placeholder,
        "theme": theme,
        "generated_at": datetime.now().isoformat(),
        "method": "template",
        "scheduled_for": None,
        "posted": False,
        "posted_at": None,
        "twitter_id": None
    }

def generate_post_with_llm(theme: str) -> dict:
    """Generate post using LLM (slower, more varied)"""
    prompt_guidance = {
        "golf_coaching": "Share a specific golf coaching insight about swing mechanics or the mental game",
        "fitness": "Share a fitness tip that improves golf performance",
        "monetization": "Share a specific revenue milestone or business lesson learned",
        "products": "Announce product value or share student transformation results",
        "high_value": "Share a mental model or tactical business decision"
    }
    
    guidance = prompt_guidance.get(theme, "Share valuable content")
    
    prompt = f"""Write one Twitter post (under 260 chars) about: {guidance}

Style: Direct, conversational tone. For a golf coach building digital products.
Include 2-3 relevant hashtags.
Output only the post text."""
    
    generated = call_ollama(prompt)
    
    if not generated:
        logger.warning("LLM generation failed, falling back to template")
        return generate_post_from_template(theme)
    
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
        "method": "llm",
        "scheduled_for": None,
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
    logger.info(f"Generation method: {'LLM' if USE_LLM else 'Template'}")
    
    # Select 2-3 random themes
    num_posts = random.randint(2, 3)
    selected_themes = random.sample(list(POST_TEMPLATES.keys()), num_posts)
    
    queue = load_queue()
    generated_count = 0
    
    for theme in selected_themes:
        logger.info(f"Generating post for theme: {theme}")
        
        if USE_LLM:
            post = generate_post_with_llm(theme)
        else:
            post = generate_post_from_template(theme)
        
        if post:
            queue.append(post)
            generated_count += 1
            logger.info(f"✅ Generated post: {post['id']} (method: {post['method']})")
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

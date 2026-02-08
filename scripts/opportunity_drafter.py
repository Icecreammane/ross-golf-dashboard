#!/usr/bin/env python3
"""
Opportunity Auto-Drafter

Uses local AI (qwen2.5:14b) to draft personalized responses to opportunities.
Learns from Ross's feedback to improve over time.
"""

import json
import urllib.request
import urllib.error
from pathlib import Path
from datetime import datetime
import sys

sys.path.insert(0, str(Path.home() / "clawd" / "scripts"))
from opportunity_scanner import OpportunityQueue

WORKSPACE = Path.home() / "clawd"
OLLAMA_URL = "http://localhost:11434/api/generate"
LEARNING_FILE = WORKSPACE / "memory" / "drafting_feedback.json"

# Ross's profile for context injection
ROSS_PROFILE = """
Ross Caster - Developer & AI Automation Specialist

Skills:
- Full-stack development (Python, JavaScript, React)
- AI automation & workflow optimization
- Dashboard & data visualization
- API integration & backend systems
- Fitness tracking applications (built personal tracker)

Services:
- Custom web applications
- Automation systems
- Data dashboards
- AI integration
- MVP development

Style: Professional but conversational. Direct, helpful, shows expertise without overselling.
"""

def call_local_model(prompt, temperature=0.7):
    """Call local ollama model"""
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
        print(f"Local model error: {e}", file=sys.stderr)
        return None

def load_learning_data():
    """Load feedback from previous drafts"""
    if LEARNING_FILE.exists():
        with open(LEARNING_FILE) as f:
            return json.load(f)
    return {"approved": [], "rejected": [], "edited": []}

def save_feedback(opp_id, action, draft, final_text=None):
    """Save feedback for learning"""
    data = load_learning_data()
    
    feedback = {
        "opp_id": opp_id,
        "timestamp": datetime.now().isoformat(),
        "draft": draft,
        "final": final_text
    }
    
    data[action].append(feedback)
    
    # Keep last 50 of each type
    for key in data:
        data[key] = data[key][-50:]
    
    LEARNING_FILE.parent.mkdir(exist_ok=True)
    with open(LEARNING_FILE, 'w') as f:
        json.dump(data, f, indent=2)

def get_learning_context():
    """Get context from previous feedback"""
    data = load_learning_data()
    
    if not data["approved"]:
        return ""
    
    # Sample recent approved drafts
    recent = data["approved"][-3:]
    
    context = "\n\nLEARNING FROM PREVIOUS APPROVED DRAFTS:\n"
    for i, item in enumerate(recent, 1):
        context += f"\n{i}. Draft that worked well:\n{item['draft'][:200]}...\n"
    
    return context

def draft_response(opportunity):
    """Generate draft response for an opportunity"""
    
    learning_context = get_learning_context()
    
    prompt = f"""You are drafting a response for Ross Caster to a business opportunity.

{ROSS_PROFILE}

OPPORTUNITY:
Source: {opportunity.source}
Title: {opportunity.title}
Context: {opportunity.context}

{learning_context}

TASK:
Write a personalized response that:
1. Shows genuine interest and expertise
2. Addresses their specific need
3. Suggests next steps (call, email, quick chat)
4. Keeps it concise (3-5 sentences)
5. Sounds like Ross - professional but friendly

IMPORTANT:
- Don't quote prices unless they mentioned budget
- Don't oversell - be helpful first
- Match their tone (formal email vs casual Reddit)
- End with a clear call-to-action

Response:"""

    draft = call_local_model(prompt, temperature=0.7)
    
    if draft:
        # Clean up response (remove any "Subject:" or metadata local model adds)
        draft = draft.strip()
        lines = draft.split('\n')
        # Skip lines that look like metadata
        cleaned_lines = [l for l in lines if not l.startswith(('Subject:', 'From:', 'To:'))]
        draft = '\n'.join(cleaned_lines).strip()
    
    return draft

def main():
    """Draft responses for all pending opportunities"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Auto-Drafting Responses...")
    
    queue = OpportunityQueue()
    pending = queue.get_pending()
    
    if not pending:
        print("  No pending opportunities")
        return
    
    drafted = 0
    for opp in pending:
        print(f"\n  📝 Drafting for: {opp.title}")
        print(f"     Score: {opp.score} | Source: {opp.source}")
        
        draft = draft_response(opp)
        
        if draft:
            queue.update_status(opp.id, "drafted", draft)
            drafted += 1
            print(f"     ✅ Draft complete ({len(draft)} chars)")
            print(f"\n     Preview:")
            preview = draft[:150] + "..." if len(draft) > 150 else draft
            print(f"     {preview}")
        else:
            print(f"     ❌ Drafting failed")
    
    print(f"\n✅ Drafted {drafted}/{len(pending)} opportunities")
    
    stats = queue.get_stats()
    print(f"📊 Queue stats: {stats['pending']} pending, {stats['drafted']} drafted")

if __name__ == "__main__":
    main()

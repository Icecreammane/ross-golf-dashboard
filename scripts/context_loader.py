#!/usr/bin/env python3
"""
Context Loader - Automatically prepares relevant context based on current work
Watches: active files, recent commits, conversation topics
Loads: docs, past work, related code, decision history
"""

import os
import json
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"
CONTEXT_CACHE = MEMORY_DIR / "context_cache.json"

def load_context_cache():
    """Load cached context"""
    if CONTEXT_CACHE.exists():
        with open(CONTEXT_CACHE) as f:
            return json.load(f)
    return {
        "current_work": None,
        "recent_files": [],
        "active_topics": [],
        "loaded_context": {}
    }

def detect_current_work():
    """Detect what Ross is currently working on"""
    
    # Check recent git activity
    try:
        result = subprocess.run(
            ["git", "-C", str(WORKSPACE), "log", "-5", "--format=%s"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            recent_commits = result.stdout.strip().split("\n")
            
            # Analyze commit messages for topics
            topics = []
            for commit in recent_commits:
                commit_lower = commit.lower()
                if "twitter" in commit_lower or "tweet" in commit_lower:
                    topics.append("twitter")
                if "reddit" in commit_lower:
                    topics.append("reddit")
                if "fitness" in commit_lower or "fittrack" in commit_lower:
                    topics.append("fitness_tracker")
                if "voice" in commit_lower or "brief" in commit_lower:
                    topics.append("voice_briefs")
                if "upgrade" in commit_lower or "build" in commit_lower:
                    topics.append("weekend_build")
            
            return list(set(topics))  # Unique topics
    except:
        pass
    
    return []

def get_recent_files(hours=24):
    """Get recently modified files"""
    cutoff = datetime.now().timestamp() - (hours * 3600)
    recent = []
    
    # Scan workspace for recent files
    for filepath in WORKSPACE.rglob("*.py"):
        if filepath.stat().st_mtime > cutoff:
            recent.append({
                "path": str(filepath),
                "name": filepath.name,
                "modified": datetime.fromtimestamp(filepath.stat().st_mtime).isoformat()
            })
    
    # Sort by modification time
    recent.sort(key=lambda x: x["modified"], reverse=True)
    
    return recent[:10]  # Top 10

def load_relevant_docs(topics):
    """Load documentation relevant to current topics"""
    docs = {}
    
    topic_files = {
        "twitter": ["content/tweets-scheduled.md", "TOOLS.md"],
        "reddit": ["REDDIT_SETUP.md"],
        "fitness_tracker": ["data/fitness_data.json", "USER.md"],
        "voice_briefs": ["VOICE_BRIEF_SETUP.md"],
        "weekend_build": ["WEEKEND_BUILD.md", "ARCHITECTURE.md"]
    }
    
    for topic in topics:
        if topic in topic_files:
            docs[topic] = []
            for filepath in topic_files[topic]:
                full_path = WORKSPACE / filepath
                if full_path.exists():
                    docs[topic].append(str(full_path))
    
    return docs

def load_related_decisions(topics):
    """Load past decisions related to current work"""
    decisions_file = MEMORY_DIR / "decisions.json"
    
    if not decisions_file.exists():
        return {}
    
    with open(decisions_file) as f:
        all_decisions = json.load(f)["decisions"]
    
    related = {}
    
    for topic in topics:
        related[topic] = []
        for decision in all_decisions:
            if topic.replace("_", " ") in decision.get("decision", "").lower():
                related[topic].append({
                    "id": decision["id"],
                    "decision": decision["decision"],
                    "outcome": decision.get("outcome"),
                    "timestamp": decision["timestamp"]
                })
    
    return related

def load_memory_context(topics):
    """Load relevant memory entries"""
    # Use persistent memory search
    memory_results = {}
    
    for topic in topics:
        # Search memory for topic
        try:
            result = subprocess.run(
                ["python3", str(WORKSPACE / "scripts" / "persistent_memory.py"), topic.replace("_", " ")],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                memory_results[topic] = result.stdout
        except:
            pass
    
    return memory_results

def prepare_context():
    """Prepare complete context for current work"""
    
    print("🔍 Detecting current work...")
    topics = detect_current_work()
    
    if not topics:
        print("No active topics detected. Continue working and context will load automatically.")
        return None
    
    print(f"📊 Active topics: {', '.join(topics)}")
    
    # Load all relevant context
    context = {
        "timestamp": datetime.now().isoformat(),
        "active_topics": topics,
        "recent_files": get_recent_files(),
        "relevant_docs": load_relevant_docs(topics),
        "related_decisions": load_related_decisions(topics),
        "memory_context": load_memory_context(topics)
    }
    
    # Cache it
    cache = load_context_cache()
    cache["current_work"] = context
    cache["active_topics"] = topics
    
    with open(CONTEXT_CACHE, "w") as f:
        json.dump(cache, f, indent=2)
    
    return context

def generate_context_summary(context):
    """Generate human-readable context summary"""
    if not context:
        return "No context available"
    
    summary = f"""# Context Summary - {datetime.now().strftime('%I:%M %p')}

## 🎯 Active Topics
{', '.join(context['active_topics'])}

---

## 📁 Recent Files (last 24h)
"""
    
    for file_info in context["recent_files"][:5]:
        modified = datetime.fromisoformat(file_info["modified"]).strftime("%I:%M %p")
        summary += f"- {file_info['name']} (modified {modified})\n"
    
    summary += "\n---\n\n## 📖 Relevant Documentation\n\n"
    
    for topic, docs in context["relevant_docs"].items():
        if docs:
            summary += f"**{topic.replace('_', ' ').title()}:**\n"
            for doc in docs:
                summary += f"- {Path(doc).name}\n"
            summary += "\n"
    
    summary += "---\n\n## 🧠 Related Decisions\n\n"
    
    has_decisions = False
    for topic, decisions in context["related_decisions"].items():
        if decisions:
            has_decisions = True
            summary += f"**{topic.replace('_', ' ').title()}:**\n"
            for decision in decisions[:3]:  # Top 3
                outcome_str = f" ({decision['outcome']}/10)" if decision.get('outcome') else " (pending)"
                summary += f"- Decision #{decision['id']}: {decision['decision']}{outcome_str}\n"
            summary += "\n"
    
    if not has_decisions:
        summary += "*No related decisions found*\n\n"
    
    summary += """---

## 💡 Quick Actions

Based on your current work, here's what's ready:

"""
    
    if "twitter" in context["active_topics"]:
        summary += "- **Twitter:** Tweets 1, 3, 9 scheduled for next week\n"
    
    if "reddit" in context["active_topics"]:
        summary += "- **Reddit:** Scanner ready, needs API setup (10 min)\n"
    
    if "fitness_tracker" in context["active_topics"]:
        summary += "- **FitTrack:** Meal planning feature ready to prototype\n"
    
    if "voice_briefs" in context["active_topics"]:
        summary += "- **Voice:** Brief script ready, needs ElevenLabs key\n"
    
    summary += "\n---\n\n*Context refreshes automatically as you work.*\n"
    
    return summary

def auto_load_context_for_file(filepath):
    """Auto-load context when specific file is opened"""
    filename = Path(filepath).name
    
    context_map = {
        "fitness": ["USER.md", "GOALS.md", "data/fitness_data.json"],
        "twitter": ["content/tweets-scheduled.md", "TOOLS.md"],
        "reddit": ["REDDIT_SETUP.md", "revenue/"],
        "autonomous": ["AUTONOMOUS_AGENT.md", "HEARTBEAT.md"]
    }
    
    # Detect topic from filename
    topic = None
    filename_lower = filename.lower()
    for key in context_map.keys():
        if key in filename_lower:
            topic = key
            break
    
    if topic:
        print(f"📚 Auto-loading context for: {topic}")
        docs = context_map[topic]
        for doc in docs:
            doc_path = WORKSPACE / doc
            if doc_path.exists():
                print(f"   → {doc}")
        return docs
    
    return []

def main():
    """CLI for context loading"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 context_loader.py prepare   - Prepare context for current work")
        print("  python3 context_loader.py summary   - Show context summary")
        print("  python3 context_loader.py file <path> - Auto-load for specific file")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "prepare":
        context = prepare_context()
        if context:
            print("\n✅ Context prepared")
            print(f"   Topics: {', '.join(context['active_topics'])}")
            print(f"   Files: {len(context['recent_files'])}")
            print(f"   Docs: {sum(len(d) for d in context['relevant_docs'].values())}")
    
    elif command == "summary":
        cache = load_context_cache()
        context = cache.get("current_work")
        
        if not context:
            print("No context loaded. Run: python3 context_loader.py prepare")
        else:
            summary = generate_context_summary(context)
            print(summary)
            
            # Also save to file
            summary_file = WORKSPACE / "reports" / "context-summary.md"
            summary_file.parent.mkdir(exist_ok=True)
            with open(summary_file, "w") as f:
                f.write(summary)
            print(f"\n📁 Saved to: {summary_file}")
    
    elif command == "file":
        if len(sys.argv) < 3:
            print("Error: Provide file path")
            sys.exit(1)
        
        filepath = sys.argv[2]
        docs = auto_load_context_for_file(filepath)
        
        if not docs:
            print("No specific context for this file")

if __name__ == "__main__":
    main()

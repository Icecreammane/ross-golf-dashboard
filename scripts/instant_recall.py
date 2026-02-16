#!/usr/bin/env python3
"""
Instant Recall System - Semantic Memory Search
Auto-triggers before responses, surfaces relevant context from all past interactions
"""

import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import hashlib

WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"
RECALL_INDEX = MEMORY_DIR / "recall_index.json"
CROSS_REF = MEMORY_DIR / "cross_references.json"

class InstantRecall:
    def __init__(self):
        self.index = self.load_index()
        self.cross_refs = self.load_cross_refs()
    
    def load_index(self):
        """Load recall index"""
        if RECALL_INDEX.exists():
            with open(RECALL_INDEX) as f:
                return json.load(f)
        return {
            "entries": [],
            "topics": defaultdict(list),
            "entities": defaultdict(list),  # People, projects, places
            "decisions": [],  # Important decisions made
            "preferences": {},  # Ross's stated preferences
            "last_indexed": None
        }
    
    def load_cross_refs(self):
        """Load cross-reference database"""
        if CROSS_REF.exists():
            with open(CROSS_REF) as f:
                return json.load(f)
        return {
            "connections": [],  # Topic → Topic relationships
            "timelines": {},  # Topic → chronological entries
            "context_chains": []  # Sequential conversation threads
        }
    
    def index_memory_file(self, filepath):
        """Index a memory file for instant recall"""
        with open(filepath) as f:
            content = f.read()
        
        # Extract structured information
        entries = self._extract_entries(content, filepath)
        
        for entry in entries:
            # Add to index
            self.index["entries"].append(entry)
            
            # Update topic index
            for topic in entry["topics"]:
                self.index["topics"][topic].append(entry["id"])
            
            # Update entity index
            for entity in entry["entities"]:
                self.index["entities"][entity].append(entry["id"])
        
        self.index["last_indexed"] = datetime.now().isoformat()
        self.save_index()
    
    def _extract_entries(self, content, filepath):
        """Extract structured entries from memory content"""
        entries = []
        
        # Split by headers or timestamps
        sections = re.split(r'\n## ', content)
        
        for section in sections:
            if not section.strip():
                continue
            
            lines = section.split('\n')
            title = lines[0].strip('#').strip()
            body = '\n'.join(lines[1:])
            
            # Generate unique ID
            entry_id = hashlib.md5(f"{filepath}:{title}".encode()).hexdigest()[:12]
            
            # Extract topics (bolded or in headers)
            topics = re.findall(r'\*\*(.+?)\*\*', body)
            topics += re.findall(r'`(.+?)`', body)
            topics = [t.lower() for t in topics if len(t) > 2]
            
            # Extract entities (capitalized words, project names)
            entities = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', body)
            entities = list(set(entities))[:10]  # Top 10
            
            # Detect if this is a decision
            is_decision = any(keyword in body.lower() for keyword in [
                'decided', 'decision', 'will do', 'plan to', 'going to'
            ])
            
            # Detect preferences
            preferences = re.findall(r'(?:prefer|like|want|love|hate)\s+(.+?)(?:\.|$)', body, re.IGNORECASE)
            
            entry = {
                "id": entry_id,
                "title": title,
                "content": body[:500],  # First 500 chars
                "filepath": str(filepath),
                "topics": list(set(topics)),
                "entities": entities,
                "is_decision": is_decision,
                "preferences": preferences,
                "timestamp": datetime.now().isoformat()
            }
            
            entries.append(entry)
        
        return entries
    
    def rebuild_index(self):
        """Rebuild entire index from all memory files"""
        print("Rebuilding recall index...")
        self.index = {
            "entries": [],
            "topics": defaultdict(list),
            "entities": defaultdict(list),
            "decisions": [],
            "preferences": {},
            "last_indexed": None
        }
        
        # Index all markdown files
        if MEMORY_DIR.exists():
            for md_file in MEMORY_DIR.glob("*.md"):
                if md_file.name != "README.md":
                    print(f"Indexing {md_file.name}...")
                    self.index_memory_file(md_file)
        
        # Extract decisions and preferences
        for entry in self.index["entries"]:
            if entry["is_decision"]:
                self.index["decisions"].append({
                    "id": entry["id"],
                    "title": entry["title"],
                    "timestamp": entry["timestamp"]
                })
            
            for pref in entry["preferences"]:
                self.index["preferences"][pref] = entry["id"]
        
        self.save_index()
        print(f"Indexed {len(self.index['entries'])} entries")
        return len(self.index["entries"])
    
    def search(self, query, limit=5):
        """Search memory with semantic matching"""
        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        
        results = []
        
        # Search entries
        for entry in self.index["entries"]:
            score = 0
            
            # Title match (highest weight)
            if query_lower in entry["title"].lower():
                score += 10
            
            # Topic match
            for topic in entry["topics"]:
                if query_lower in topic or topic in query_lower:
                    score += 5
                # Word overlap
                topic_words = set(re.findall(r'\w+', topic))
                overlap = len(query_words & topic_words)
                score += overlap * 2
            
            # Entity match
            for entity in entry["entities"]:
                if query_lower in entity.lower():
                    score += 3
            
            # Content match
            content_words = set(re.findall(r'\w+', entry["content"].lower()))
            overlap = len(query_words & content_words)
            score += overlap
            
            if score > 0:
                results.append({
                    "entry_id": entry["id"],
                    "title": entry["title"],
                    "content": entry["content"],
                    "filepath": entry["filepath"],
                    "score": score,
                    "topics": entry["topics"]
                })
        
        # Sort by score
        results = sorted(results, key=lambda x: x["score"], reverse=True)
        
        return results[:limit]
    
    def find_related(self, topic):
        """Find related conversations and context"""
        # Find all entries with this topic
        entry_ids = self.index["topics"].get(topic.lower(), [])
        
        related = []
        for entry in self.index["entries"]:
            if entry["id"] in entry_ids:
                related.append({
                    "date": entry["timestamp"],
                    "title": entry["title"],
                    "context": entry["content"][:200]
                })
        
        return sorted(related, key=lambda x: x["date"], reverse=True)
    
    def get_decision_history(self, topic=None):
        """Get history of decisions made"""
        decisions = self.index.get("decisions", [])
        
        if topic:
            # Filter by topic
            decisions = [d for d in decisions if topic.lower() in d["title"].lower()]
        
        return sorted(decisions, key=lambda x: x["timestamp"], reverse=True)
    
    def get_preferences(self, category=None):
        """Get Ross's stated preferences"""
        prefs = self.index.get("preferences", {})
        
        if category:
            return {k: v for k, v in prefs.items() if category.lower() in k.lower()}
        
        return prefs
    
    def auto_recall(self, message):
        """Automatically recall relevant context before responding"""
        # Extract key topics from message
        words = re.findall(r'\w+', message.lower())
        meaningful_words = [w for w in words if len(w) > 3]
        
        recalls = []
        
        # Search for each meaningful word
        for word in meaningful_words[:5]:  # Top 5 words
            results = self.search(word, limit=2)
            for result in results:
                if result not in recalls:
                    recalls.append(result)
        
        return recalls[:3]  # Top 3 most relevant
    
    def create_cross_reference(self, topic1, topic2, relationship="related"):
        """Create cross-reference between topics"""
        self.cross_refs["connections"].append({
            "topic1": topic1,
            "topic2": topic2,
            "relationship": relationship,
            "created": datetime.now().isoformat()
        })
        self.save_cross_refs()
    
    def get_timeline(self, topic):
        """Get chronological timeline of topic"""
        entries = self.find_related(topic)
        
        timeline = []
        for entry in entries:
            date_str = entry["date"]
            try:
                date_obj = datetime.fromisoformat(date_str)
                timeline.append({
                    "date": date_obj.strftime("%Y-%m-%d"),
                    "event": entry["title"],
                    "context": entry["context"]
                })
            except:
                pass
        
        return timeline
    
    def save_index(self):
        """Save index to disk"""
        RECALL_INDEX.parent.mkdir(exist_ok=True)
        with open(RECALL_INDEX, "w") as f:
            json.dump(self.index, f, indent=2)
    
    def save_cross_refs(self):
        """Save cross-references"""
        CROSS_REF.parent.mkdir(exist_ok=True)
        with open(CROSS_REF, "w") as f:
            json.dump(self.cross_refs, f, indent=2)


def test_recall():
    """Test instant recall system"""
    recall = InstantRecall()
    
    print("Rebuilding index...")
    count = recall.rebuild_index()
    print(f"✅ Indexed {count} entries\n")
    
    # Test search
    print("Testing search for 'workout':")
    results = recall.search("workout", limit=3)
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result['title']} (score: {result['score']})")
        print(f"   {result['content'][:100]}...")
    
    # Test auto-recall
    print("\n\nTesting auto-recall for: 'How's my workout progress?'")
    recalls = recall.auto_recall("How's my workout progress?")
    for recall_item in recalls:
        print(f"- {recall_item['title']} (relevance: {recall_item['score']})")
    
    # Test decision history
    print("\n\nRecent decisions:")
    decisions = recall.get_decision_history()
    for dec in decisions[:3]:
        print(f"- {dec['title']} ({dec['timestamp'][:10]})")
    
    print("\n✅ Instant recall system working!")


if __name__ == "__main__":
    test_recall()

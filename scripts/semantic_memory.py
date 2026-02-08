#!/usr/bin/env python3
"""
Semantic Memory System
Vector-based memory search with emotional tagging and relationship graphs
Makes memory feel continuous instead of just reading logs
"""

import json
import re
import hashlib
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path.home() / "clawd"
MEMORY_INDEX = WORKSPACE / "memory" / "semantic_index.json"

class SemanticMemory:
    """Semantic memory system with emotional tagging"""
    
    def __init__(self):
        self.index_file = MEMORY_INDEX
        self.load_index()
    
    def load_index(self):
        """Load semantic memory index"""
        if self.index_file.exists():
            with open(self.index_file) as f:
                self.index = json.load(f)
        else:
            self.index = {
                "version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "memories": [],
                "relationships": [],
                "emotional_tags": {},
                "key_moments": []
            }
    
    def save_index(self):
        """Save semantic memory index"""
        self.index["last_updated"] = datetime.now().isoformat()
        self.index_file.parent.mkdir(exist_ok=True)
        with open(self.index_file, 'w') as f:
            json.dump(self.index, f, indent=2)
    
    def create_memory_id(self, content, timestamp):
        """Create unique ID for memory"""
        data = f"{content}{timestamp}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def extract_keywords(self, text):
        """Extract keywords from text"""
        # Remove common words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
                      'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
                      'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 
                      'should', 'could', 'can', 'may', 'might', 'must', 'i', 'you', 'he',
                      'she', 'it', 'we', 'they', 'this', 'that', 'these', 'those'}
        
        # Extract words
        words = re.findall(r'\b[a-z]{3,}\b', text.lower())
        
        # Filter and get unique
        keywords = list(set([w for w in words if w not in stop_words]))
        
        return keywords[:20]  # Top 20 keywords
    
    def detect_emotion(self, text):
        """Detect emotional tone of text"""
        text_lower = text.lower()
        
        # Emotion patterns
        emotions = {
            "excited": [r'(amazing|awesome|killer|insane|crushing|beast|hell yeah|fire|psychotic|ship it)'],
            "frustrated": [r'(annoying|frustrating|stuck|broken|failing|not working|error)'],
            "satisfied": [r'(shipped|complete|done|working|success|operational|built)'],
            "uncertain": [r'(not sure|maybe|might|could be|possibly|wondering)'],
            "motivated": [r'(let\'s go|ready|motivated|pumped|focused|locked in)'],
            "tired": [r'(tired|exhausted|burnt|drained|done for)']
        }
        
        detected = []
        for emotion, patterns in emotions.items():
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    detected.append(emotion)
                    break
        
        return detected if detected else ["neutral"]
    
    def add_memory(self, content, context=None, importance="medium"):
        """Add a memory with semantic indexing"""
        timestamp = datetime.now().isoformat()
        memory_id = self.create_memory_id(content, timestamp)
        
        # Extract features
        keywords = self.extract_keywords(content)
        emotions = self.detect_emotion(content)
        
        memory = {
            "id": memory_id,
            "timestamp": timestamp,
            "content": content,
            "context": context or {},
            "keywords": keywords,
            "emotions": emotions,
            "importance": importance,
            "related_memories": []
        }
        
        # Find related memories (keyword overlap)
        for existing in self.index["memories"]:
            overlap = set(keywords) & set(existing["keywords"])
            if len(overlap) >= 2:  # At least 2 keywords in common
                memory["related_memories"].append(existing["id"])
                
                # Add bidirectional relationship
                if memory_id not in existing.get("related_memories", []):
                    existing["related_memories"].append(memory_id)
        
        self.index["memories"].append(memory)
        
        # Track emotional patterns
        for emotion in emotions:
            if emotion not in self.index["emotional_tags"]:
                self.index["emotional_tags"][emotion] = []
            self.index["emotional_tags"][emotion].append(memory_id)
        
        # Mark key moments (high importance + strong emotion)
        if importance == "high" and any(e in ["excited", "satisfied", "motivated"] for e in emotions):
            self.index["key_moments"].append({
                "memory_id": memory_id,
                "timestamp": timestamp,
                "summary": content[:100]
            })
        
        self.save_index()
        return memory_id
    
    def search(self, query, limit=5):
        """Search memories semantically"""
        query_keywords = self.extract_keywords(query)
        query_emotions = self.detect_emotion(query)
        
        # Score each memory
        scored_memories = []
        
        for memory in self.index["memories"]:
            score = 0
            
            # Keyword overlap
            keyword_overlap = set(query_keywords) & set(memory["keywords"])
            score += len(keyword_overlap) * 2
            
            # Emotion match
            emotion_overlap = set(query_emotions) & set(memory["emotions"])
            score += len(emotion_overlap) * 3
            
            # Importance boost
            importance_boost = {"low": 0, "medium": 1, "high": 3}
            score += importance_boost.get(memory["importance"], 0)
            
            # Recency boost (recent memories slightly favored)
            days_ago = (datetime.now() - datetime.fromisoformat(memory["timestamp"])).days
            if days_ago <= 7:
                score += 2
            elif days_ago <= 30:
                score += 1
            
            if score > 0:
                scored_memories.append({
                    **memory,
                    "relevance_score": score
                })
        
        # Sort by score
        scored_memories.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return scored_memories[:limit]
    
    def get_emotional_context(self, emotion):
        """Get all memories with specific emotion"""
        memory_ids = self.index["emotional_tags"].get(emotion, [])
        
        memories = [
            m for m in self.index["memories"]
            if m["id"] in memory_ids
        ]
        
        return memories
    
    def get_key_moments(self, limit=10):
        """Get key moments chronologically"""
        return self.index["key_moments"][-limit:]
    
    def get_related_memories(self, memory_id):
        """Get memories related to a specific memory"""
        memory = next((m for m in self.index["memories"] if m["id"] == memory_id), None)
        
        if not memory:
            return []
        
        related_ids = memory.get("related_memories", [])
        
        related = [
            m for m in self.index["memories"]
            if m["id"] in related_ids
        ]
        
        return related
    
    def build_relationship_graph(self):
        """Build graph of memory relationships"""
        graph = defaultdict(list)
        
        for memory in self.index["memories"]:
            memory_id = memory["id"]
            for related_id in memory.get("related_memories", []):
                graph[memory_id].append(related_id)
        
        return dict(graph)
    
    def get_session_summary(self, days=1):
        """Get summary of recent memories"""
        cutoff = datetime.now() - timedelta(days=days)
        
        recent = [
            m for m in self.index["memories"]
            if datetime.fromisoformat(m["timestamp"]) > cutoff
        ]
        
        # Group by emotion
        by_emotion = defaultdict(list)
        for memory in recent:
            for emotion in memory["emotions"]:
                by_emotion[emotion].append(memory["content"][:100])
        
        # Count keywords
        all_keywords = []
        for memory in recent:
            all_keywords.extend(memory["keywords"])
        
        keyword_counts = defaultdict(int)
        for keyword in all_keywords:
            keyword_counts[keyword] += 1
        
        top_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "memory_count": len(recent),
            "emotions": dict(by_emotion),
            "top_topics": [k for k, v in top_keywords],
            "key_moments": [m for m in self.index["key_moments"] 
                           if datetime.fromisoformat(m["timestamp"]) > cutoff]
        }
    
    def generate_context_prompt(self, current_topic=None):
        """Generate context prompt for current session"""
        # Get recent key moments
        key_moments = self.get_key_moments(limit=5)
        
        # Get recent session summary
        summary = self.get_session_summary(days=2)
        
        # Search for related memories if topic provided
        related = []
        if current_topic:
            related = self.search(current_topic, limit=3)
        
        prompt_parts = []
        
        if key_moments:
            prompt_parts.append("🔑 KEY MOMENTS:")
            for moment in key_moments[-3:]:  # Last 3
                timestamp = datetime.fromisoformat(moment["timestamp"])
                prompt_parts.append(f"  • {timestamp.strftime('%m/%d %I:%M%p')}: {moment['summary']}")
        
        if summary["top_topics"]:
            prompt_parts.append(f"\n📌 RECENT TOPICS: {', '.join(summary['top_topics'][:5])}")
        
        if related:
            prompt_parts.append("\n💭 RELATED MEMORIES:")
            for mem in related:
                timestamp = datetime.fromisoformat(mem["timestamp"])
                prompt_parts.append(f"  • {timestamp.strftime('%m/%d')}: {mem['content'][:80]}...")
        
        return "\n".join(prompt_parts) if prompt_parts else "No recent context"
    
    def index_memory_files(self):
        """Index all memory markdown files"""
        memory_dir = WORKSPACE / "memory"
        
        if not memory_dir.exists():
            return
        
        count = 0
        
        # Index daily logs
        for md_file in memory_dir.glob("2026-*.md"):
            with open(md_file) as f:
                content = f.read()
            
            # Split into sections
            sections = re.split(r'^## ', content, flags=re.MULTILINE)
            
            for section in sections[1:]:  # Skip first (empty)
                lines = section.split('\n', 1)
                if len(lines) < 2:
                    continue
                
                title = lines[0].strip()
                body = lines[1].strip()
                
                if len(body) > 50:  # Meaningful content
                    # Detect importance
                    importance = "high" if any(marker in body.lower() for marker in 
                                             ['shipped', 'complete', 'built', 'operational']) else "medium"
                    
                    self.add_memory(
                        content=f"{title}: {body[:200]}",
                        context={"source": str(md_file.name), "section": title},
                        importance=importance
                    )
                    count += 1
        
        print(f"✅ Indexed {count} memories from daily logs")


def test_semantic_memory():
    """Test semantic memory system"""
    sm = SemanticMemory()
    
    print("=" * 70)
    print("🧠 SEMANTIC MEMORY SYSTEM TEST")
    print("=" * 70)
    print()
    
    # Add test memories
    test_memories = [
        ("Built party demo apps with Roast Bot", {"excitement": "high"}, "high"),
        ("Shipped Preference Engine to learn Ross's patterns", {}, "high"),
        ("Win Streak Amplifier gamifies daily progress", {}, "high"),
        ("Cool down system for post-build recovery", {}, "medium"),
        ("Feeling tired but productive", {}, "low"),
    ]
    
    print("📝 Adding test memories...")
    for content, context, importance in test_memories:
        memory_id = sm.add_memory(content, context, importance)
        print(f"  ✅ {memory_id}: {content[:50]}...")
    
    print()
    
    # Test search
    print("🔍 Search: 'party demo'")
    results = sm.search("party demo", limit=3)
    for result in results:
        print(f"  Score {result['relevance_score']}: {result['content'][:60]}...")
    
    print()
    
    # Test emotional search
    print("😊 Memories with 'excited' emotion:")
    excited = sm.get_emotional_context("excited")
    for mem in excited[:3]:
        print(f"  • {mem['content'][:60]}...")
    
    print()
    
    # Key moments
    print("🔑 Key moments:")
    moments = sm.get_key_moments(limit=5)
    for moment in moments:
        print(f"  • {moment['summary']}")
    
    print()
    
    # Context prompt
    print("💭 Context prompt for 'building':")
    prompt = sm.generate_context_prompt("building systems")
    print(prompt)
    
    print()
    print("=" * 70)


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        test_semantic_memory()
    elif len(sys.argv) > 1 and sys.argv[1] == "index":
        sm = SemanticMemory()
        sm.index_memory_files()
    else:
        sm = SemanticMemory()
        print(sm.generate_context_prompt())


if __name__ == "__main__":
    main()

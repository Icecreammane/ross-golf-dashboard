#!/usr/bin/env python3
"""
Persistent Memory System - Jarvis's Enhanced Memory
Searches across all sessions, builds knowledge graph, maintains continuity
"""

import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

WORKSPACE = Path("/Users/clawdbot/clawd")
MEMORY_DIR = WORKSPACE / "memory"
MEMORY_INDEX = MEMORY_DIR / "memory_index.json"

def build_memory_index():
    """Build searchable index of all memory files"""
    index = {
        "files": {},
        "topics": defaultdict(list),
        "keywords": defaultdict(list),
        "last_updated": datetime.now().isoformat()
    }
    
    # Index all markdown files in memory/
    if MEMORY_DIR.exists():
        for md_file in MEMORY_DIR.glob("*.md"):
            if md_file.name == "README.md":
                continue
            
            with open(md_file) as f:
                content = f.read()
            
            # Extract key information
            file_info = {
                "path": str(md_file),
                "size": len(content),
                "lines": len(content.splitlines()),
                "modified": datetime.fromtimestamp(md_file.stat().st_mtime).isoformat()
            }
            
            # Extract topics (headers)
            topics = re.findall(r'^##+ (.+)$', content, re.MULTILINE)
            file_info["topics"] = topics
            
            # Extract keywords (bold text, code blocks)
            keywords = re.findall(r'\*\*(.+?)\*\*', content)
            keywords += re.findall(r'`(.+?)`', content)
            file_info["keywords"] = list(set(keywords))[:50]  # Top 50
            
            # Store in index
            index["files"][md_file.name] = file_info
            
            # Build reverse index
            for topic in topics:
                index["topics"][topic.lower()].append(md_file.name)
            
            for keyword in file_info["keywords"]:
                index["keywords"][keyword.lower()].append(md_file.name)
    
    # Save index
    with open(MEMORY_INDEX, "w") as f:
        json.dump(index, f, indent=2)
    
    return index

def search_memory(query, limit=5):
    """Search across all memory files"""
    # Build/load index
    if MEMORY_INDEX.exists():
        with open(MEMORY_INDEX) as f:
            index = json.load(f)
    else:
        index = build_memory_index()
    
    query_lower = query.lower()
    results = []
    
    # Search topics
    for topic, files in index.get("topics", {}).items():
        if query_lower in topic:
            for filename in files:
                results.append({
                    "file": filename,
                    "match_type": "topic",
                    "match_text": topic,
                    "relevance": 1.0
                })
    
    # Search keywords
    for keyword, files in index.get("keywords", {}).items():
        if query_lower in keyword:
            for filename in files:
                results.append({
                    "file": filename,
                    "match_type": "keyword",
                    "match_text": keyword,
                    "relevance": 0.7
                })
    
    # Search content (slower, but thorough)
    for filename, file_info in index.get("files", {}).items():
        file_path = Path(file_info["path"])
        if file_path.exists():
            with open(file_path) as f:
                content = f.read()
            
            if query_lower in content.lower():
                # Find context around match
                lines = content.splitlines()
                for i, line in enumerate(lines):
                    if query_lower in line.lower():
                        context_start = max(0, i - 2)
                        context_end = min(len(lines), i + 3)
                        context = "\n".join(lines[context_start:context_end])
                        
                        results.append({
                            "file": filename,
                            "match_type": "content",
                            "match_text": line.strip(),
                            "context": context,
                            "line_number": i + 1,
                            "relevance": 0.5
                        })
                        break  # Only first match per file
    
    # Sort by relevance and dedupe
    seen_files = set()
    unique_results = []
    for result in sorted(results, key=lambda x: x["relevance"], reverse=True):
        if result["file"] not in seen_files:
            unique_results.append(result)
            seen_files.add(result["file"])
    
    return unique_results[:limit]

def get_related_context(topic):
    """Get all context related to a specific topic"""
    results = search_memory(topic, limit=10)
    
    context = f"# Related Context: {topic}\n\n"
    
    for result in results:
        file_path = MEMORY_DIR / result["file"]
        context += f"## From {result['file']}\n"
        context += f"**Match:** {result['match_text']}\n\n"
        
        if "context" in result:
            context += f"```\n{result['context']}\n```\n\n"
    
    return context

def auto_load_context(conversation_text):
    """Automatically load relevant context based on conversation"""
    # Extract key topics from conversation
    topics = []
    
    # Look for explicit mentions
    patterns = [
        r"about (\w+)",
        r"regarding (\w+)",
        r"working on (\w+)",
        r"building (\w+)",
        r"remember (\w+)"
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, conversation_text.lower())
        topics.extend(matches)
    
    # Load context for each topic
    context_dict = {}
    for topic in set(topics):
        results = search_memory(topic, limit=3)
        if results:
            context_dict[topic] = results
    
    return context_dict

def main():
    """CLI interface for memory search"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 persistent_memory.py <query>")
        print("       python3 persistent_memory.py --rebuild (rebuild index)")
        sys.exit(1)
    
    if sys.argv[1] == "--rebuild":
        print("Rebuilding memory index...")
        index = build_memory_index()
        print(f"✅ Indexed {len(index['files'])} files")
        print(f"   Topics: {len(index['topics'])}")
        print(f"   Keywords: {len(index['keywords'])}")
        sys.exit(0)
    
    query = " ".join(sys.argv[1:])
    print(f"Searching for: {query}\n")
    
    results = search_memory(query)
    
    if not results:
        print("No results found.")
        sys.exit(0)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['file']} ({result['match_type']})")
        print(f"   Match: {result['match_text']}")
        if "line_number" in result:
            print(f"   Line: {result['line_number']}")
        print()

if __name__ == "__main__":
    main()

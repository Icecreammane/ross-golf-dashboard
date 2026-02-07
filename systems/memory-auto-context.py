#!/usr/bin/env python3
"""
Memory-First Auto-Context System
Automatically searches memory files before EVERY response and injects relevant context.

Performance target: <100ms
Files searched:
- memory/jarvis-journal.md (learnings, preferences, patterns)
- USER.md (Ross's profile, goals, preferences)
- TASK_QUEUE.md (current priorities, active tasks)

Usage:
    from systems.memory_auto_context import search_memory, inject_context
    
    # Quick search
    results = search_memory("golf")
    
    # Full context injection (use this before responses)
    context = inject_context(user_message="What's my golf handicap?")
"""

import json
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from collections import defaultdict

# Configuration
WORKSPACE = Path.home() / "clawd"
MEMORY_FILES = {
    'journal': WORKSPACE / "memory" / "jarvis-journal.md",
    'user': WORKSPACE / "USER.md",
    'tasks': WORKSPACE / "TASK_QUEUE.md",
    'memory': WORKSPACE / "MEMORY.md"  # Long-term curated memories
}
SEARCH_LOG = WORKSPACE / "memory" / "auto-context-log.json"

# Performance: Cache file contents (invalidate every 5 minutes)
_file_cache = {}
_cache_timestamp = {}
CACHE_TTL = 300  # 5 minutes in seconds


def _get_file_content(file_path: Path) -> Optional[str]:
    """Get file content with caching for performance."""
    if not file_path.exists():
        return None
    
    now = datetime.now().timestamp()
    cache_key = str(file_path)
    
    # Check cache validity
    if cache_key in _file_cache:
        if now - _cache_timestamp.get(cache_key, 0) < CACHE_TTL:
            return _file_cache[cache_key]
    
    # Read and cache
    try:
        content = file_path.read_text()
        _file_cache[cache_key] = content
        _cache_timestamp[cache_key] = now
        return content
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None


def search_memory(query: str, max_results: int = 5) -> List[Dict[str, str]]:
    """
    Search all memory files for relevant context.
    
    Args:
        query: Search query (user's message or keywords)
        max_results: Maximum snippets to return per file
    
    Returns:
        List of dicts with 'file', 'snippet', 'relevance_score'
    """
    results = []
    query_lower = query.lower()
    
    # Extract keywords (simple but fast)
    keywords = set([
        word for word in re.findall(r'\b\w+\b', query_lower)
        if len(word) > 3  # Skip short words
    ])
    
    for file_name, file_path in MEMORY_FILES.items():
        content = _get_file_content(file_path)
        if not content:
            continue
        
        # Split into sections (by headers or paragraphs)
        sections = _split_into_sections(content)
        
        for section in sections:
            score = _calculate_relevance(section, keywords, query_lower)
            if score > 0:
                results.append({
                    'file': file_name,
                    'snippet': _truncate_snippet(section),
                    'relevance_score': score,
                    'file_path': str(file_path)
                })
    
    # Sort by relevance, limit results
    results.sort(key=lambda x: x['relevance_score'], reverse=True)
    return results[:max_results * len(MEMORY_FILES)]  # Scale with file count


def _split_into_sections(content: str) -> List[str]:
    """Split content into searchable sections."""
    # Split by markdown headers or double newlines
    sections = []
    
    # Try splitting by headers first
    header_pattern = r'^#{1,3}\s+.+$'
    current_section = []
    
    for line in content.split('\n'):
        if re.match(header_pattern, line):
            if current_section:
                sections.append('\n'.join(current_section))
            current_section = [line]
        else:
            current_section.append(line)
    
    if current_section:
        sections.append('\n'.join(current_section))
    
    # If no sections found, split by double newlines
    if len(sections) <= 1:
        sections = [s.strip() for s in content.split('\n\n') if s.strip()]
    
    return sections


def _calculate_relevance(section: str, keywords: set, query: str) -> float:
    """
    Calculate relevance score for a section.
    Simple but fast scoring:
    - Exact phrase match: +10
    - Keyword match: +1 per keyword
    - Recent date mention: +2
    """
    section_lower = section.lower()
    score = 0.0
    
    # Exact phrase match
    if query in section_lower:
        score += 10
    
    # Keyword matches
    for keyword in keywords:
        if keyword in section_lower:
            score += 1
    
    # Recency bonus (mentions of 2026)
    if '2026' in section:
        score += 2
    
    # Priority markers
    if any(marker in section_lower for marker in ['priority', 'urgent', 'important', '🔴']):
        score += 3
    
    return score


def _truncate_snippet(text: str, max_chars: int = 300) -> str:
    """Truncate snippet to reasonable length."""
    if len(text) <= max_chars:
        return text
    
    # Try to break at sentence
    truncated = text[:max_chars]
    last_period = truncated.rfind('.')
    last_newline = truncated.rfind('\n')
    
    break_point = max(last_period, last_newline)
    if break_point > max_chars * 0.7:  # At least 70% of max length
        return text[:break_point + 1]
    
    return truncated + "..."


def inject_context(user_message: str, include_files: List[str] = None) -> Dict[str, any]:
    """
    Main function: Search memory and return injected context.
    
    Args:
        user_message: The user's message to respond to
        include_files: Optional list of specific files to search
    
    Returns:
        Dict with 'snippets', 'summary', 'search_time_ms', 'found_relevant'
    """
    import time
    start_time = time.time()
    
    # Search memory
    results = search_memory(user_message)
    
    # Group by file
    by_file = defaultdict(list)
    for result in results[:10]:  # Top 10 results only
        by_file[result['file']].append(result['snippet'])
    
    # Generate summary
    summary = _generate_summary(by_file, user_message)
    
    # Calculate search time
    search_time_ms = (time.time() - start_time) * 1000
    
    # Log the search
    _log_search(user_message, results, search_time_ms)
    
    return {
        'snippets': dict(by_file),
        'summary': summary,
        'search_time_ms': round(search_time_ms, 2),
        'found_relevant': len(results) > 0,
        'top_results': results[:5]  # For debugging
    }


def _generate_summary(by_file: Dict[str, List[str]], query: str) -> str:
    """Generate a human-readable summary of what was found."""
    if not by_file:
        return "❌ No relevant context found in memory."
    
    lines = ["🧠 **Auto-Context Search Results:**\n"]
    
    for file_name, snippets in by_file.items():
        file_label = {
            'journal': 'Jarvis Journal',
            'user': 'User Profile',
            'tasks': 'Task Queue',
            'memory': 'Long-term Memory'
        }.get(file_name, file_name)
        
        lines.append(f"**{file_label}:** {len(snippets)} relevant snippet(s)")
    
    return '\n'.join(lines)


def _log_search(query: str, results: List[Dict], search_time_ms: float):
    """Log searches to help improve the system over time."""
    log_entry = {
        'timestamp': datetime.now().isoformat(),
        'query': query[:100],  # Truncate long queries
        'results_found': len(results),
        'search_time_ms': search_time_ms,
        'top_file': results[0]['file'] if results else None
    }
    
    # Load existing log
    log_data = {'searches': []}
    if SEARCH_LOG.exists():
        try:
            log_data = json.loads(SEARCH_LOG.read_text())
        except json.JSONDecodeError:
            pass
    
    # Append and keep last 1000 searches
    log_data['searches'].append(log_entry)
    log_data['searches'] = log_data['searches'][-1000:]
    
    # Save
    SEARCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    SEARCH_LOG.write_text(json.dumps(log_data, indent=2))


def get_search_stats() -> Dict[str, any]:
    """Get statistics about memory searches."""
    if not SEARCH_LOG.exists():
        return {'total_searches': 0}
    
    try:
        log_data = json.loads(SEARCH_LOG.read_text())
        searches = log_data.get('searches', [])
        
        if not searches:
            return {'total_searches': 0}
        
        avg_time = sum(s['search_time_ms'] for s in searches) / len(searches)
        hit_rate = sum(1 for s in searches if s['results_found'] > 0) / len(searches) * 100
        
        return {
            'total_searches': len(searches),
            'avg_search_time_ms': round(avg_time, 2),
            'hit_rate_percent': round(hit_rate, 1),
            'last_search': searches[-1]['timestamp']
        }
    except Exception as e:
        return {'error': str(e)}


# CLI interface for testing
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--stats':
        stats = get_search_stats()
        print("📊 **Memory Search Statistics**")
        for key, value in stats.items():
            print(f"  {key}: {value}")
    
    elif len(sys.argv) > 1 and sys.argv[1] == '--test':
        # Test search
        query = ' '.join(sys.argv[2:]) if len(sys.argv) > 2 else "golf"
        print(f"🔍 Testing search: '{query}'\n")
        
        context = inject_context(query)
        
        print(context['summary'])
        print(f"\n⏱️  Search time: {context['search_time_ms']}ms")
        print(f"✅ Found relevant: {context['found_relevant']}")
        
        if context['top_results']:
            print("\n📝 **Top Results:**")
            for i, result in enumerate(context['top_results'], 1):
                print(f"\n{i}. [{result['file']}] Score: {result['relevance_score']}")
                print(f"   {result['snippet'][:150]}...")
    
    else:
        print("Usage:")
        print("  python3 memory-auto-context.py --test [query]")
        print("  python3 memory-auto-context.py --stats")

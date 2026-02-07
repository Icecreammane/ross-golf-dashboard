#!/Users/clawdbot/clawd/memory/venv/bin/python3
"""
Memory Helper Functions - For integration into main agent loop.
"""

import sys
import os
sys.path.insert(0, '/Users/clawdbot/clawd/scripts')

from semantic_memory import SemanticMemory
from typing import Optional, List, Dict


# Global instance (lazy loaded)
_memory_instance = None


def get_memory() -> SemanticMemory:
    """Get or create global memory instance."""
    global _memory_instance
    if _memory_instance is None:
        _memory_instance = SemanticMemory()
    return _memory_instance


def check_memory_before_response(user_message: str, min_relevance: float = 0.7) -> Optional[str]:
    """
    Check memory for relevant context before responding to user.
    
    Args:
        user_message: The user's message/query
        min_relevance: Minimum relevance score (0-1, default 0.7)
    
    Returns:
        Context string if relevant memories found, None otherwise.
        
    Usage in main agent:
        context = check_memory_before_response(user_message)
        if context:
            # Include context in your response
            print(f"Memory context: {context}")
    """
    try:
        mem = get_memory()
        results = mem.search(user_message, n_results=3)
        
        if not results or results[0]['relevance'] < min_relevance:
            return None
        
        # Format context
        context_parts = []
        for result in results:
            if result['relevance'] < min_relevance:
                break
            
            source = result['metadata'].get('file_name', 'unknown')
            source_type = result['metadata'].get('source_type', '')
            text = result['text']
            
            # Truncate long texts
            if len(text) > 300:
                text = text[:300] + "..."
            
            context_parts.append({
                'source': source,
                'type': source_type,
                'text': text,
                'relevance': result['relevance']
            })
        
        if not context_parts:
            return None
        
        # Format as string
        context_str = "📚 Relevant memories:\n\n"
        for i, ctx in enumerate(context_parts, 1):
            context_str += f"{i}. [{ctx['source']}] ({ctx['relevance']:.0%} relevant)\n"
            context_str += f"   {ctx['text']}\n\n"
        
        return context_str
    
    except Exception as e:
        print(f"Error checking memory: {e}")
        return None


def search_memory(query: str, n_results: int = 5, source_type: str = None) -> List[Dict]:
    """
    Search memory with natural language query.
    
    Args:
        query: Search query
        n_results: Number of results (default 5)
        source_type: Filter by type (memory/journal/daily_log/conversation)
    
    Returns:
        List of result dictionaries with text, metadata, relevance
    """
    try:
        mem = get_memory()
        return mem.search(query, n_results=n_results, source_type=source_type)
    except Exception as e:
        print(f"Error searching memory: {e}")
        return []


def quick_embed():
    """Quick re-embed of recent changes. Call after updating memory files."""
    try:
        from extract_and_update_memory import MemoryExtractor
        extractor = MemoryExtractor()
        stats = extractor.embed_recent_changes()
        print(f"✓ Embedded {sum(stats.values())} chunks")
        return stats
    except Exception as e:
        print(f"Error embedding: {e}")
        return {}


def memory_stats() -> Dict:
    """Get memory database statistics."""
    try:
        mem = get_memory()
        return mem.get_stats()
    except Exception as e:
        print(f"Error getting stats: {e}")
        return {}


# Quick test
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        query = ' '.join(sys.argv[1:])
        print(f"Searching for: {query}\n")
        
        context = check_memory_before_response(query)
        if context:
            print(context)
        else:
            print("No relevant memories found")
    else:
        print("Memory Helper Functions")
        print("\nUsage:")
        print("  python memory_helper.py 'what is Ross calorie goal?'")
        print("\nOr import in Python:")
        print("  from memory_helper import check_memory_before_response")
        print("  context = check_memory_before_response(user_message)")

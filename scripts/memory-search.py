#!/Users/clawdbot/clawd/memory/venv/bin/python3
"""
Memory Search CLI - Query Jarvis's semantic memory from command line.
Usage: memory-search.py "what did Ross say about X?"
"""

import sys
import argparse
from semantic_memory import SemanticMemory


def format_result(result: dict, index: int) -> str:
    """Format a search result for display."""
    meta = result['metadata']
    relevance = result['relevance']
    text = result['text']
    
    # Color coding based on relevance
    if relevance > 0.8:
        color = '\033[92m'  # Green
    elif relevance > 0.6:
        color = '\033[93m'  # Yellow
    else:
        color = '\033[91m'  # Red
    reset = '\033[0m'
    
    output = []
    output.append(f"\n{color}[{index + 1}] Relevance: {relevance:.2%}{reset}")
    output.append(f"Source: {meta.get('file_name', 'unknown')} ({meta.get('source_type', 'unknown')})")
    
    if 'modified_time' in meta:
        output.append(f"Modified: {meta['modified_time'][:10]}")
    
    output.append(f"\n{text}")
    output.append("-" * 80)
    
    return '\n'.join(output)


def main():
    parser = argparse.ArgumentParser(
        description='Search Jarvis semantic memory',
        epilog='Example: memory-search.py "Ross calorie goal"'
    )
    
    parser.add_argument('query', nargs='+', help='Search query')
    parser.add_argument('-n', '--num-results', type=int, default=5,
                       help='Number of results to return (default: 5)')
    parser.add_argument('-t', '--type', choices=['memory', 'journal', 'daily_log', 'conversation'],
                       help='Filter by source type')
    parser.add_argument('--min-relevance', type=float, default=0.5,
                       help='Minimum relevance score (0-1, default: 0.5)')
    parser.add_argument('--stats', action='store_true',
                       help='Show database statistics')
    parser.add_argument('--embed', action='store_true',
                       help='Re-embed all sources before searching')
    
    args = parser.parse_args()
    
    # Initialize memory
    print("Initializing semantic memory...")
    mem = SemanticMemory()
    
    # Show stats if requested
    if args.stats:
        stats = mem.get_stats()
        print(f"\nDatabase Statistics:")
        print(f"  Total chunks: {stats['total_chunks']}")
        print(f"  Collection: {stats['collection_name']}")
        print(f"  Source breakdown:")
        for stype, count in stats['source_types'].items():
            print(f"    {stype}: {count}")
        print()
    
    # Embed if requested
    if args.embed:
        print("\nEmbedding all sources...")
        stats = mem.embed_all_sources()
        print("Embedding complete:")
        for source, count in stats.items():
            print(f"  {source}: {count} chunks")
        print()
    
    # Perform search
    query = ' '.join(args.query)
    print(f"\nSearching for: \"{query}\"")
    print(f"Filters: type={args.type or 'all'}, min_relevance={args.min_relevance}")
    print("=" * 80)
    
    results = mem.search(query, n_results=args.num_results, source_type=args.type)
    
    if not results:
        print("\nNo results found.")
        return
    
    # Filter by minimum relevance
    filtered_results = [r for r in results if r['relevance'] >= args.min_relevance]
    
    if not filtered_results:
        print(f"\nNo results above {args.min_relevance:.0%} relevance threshold.")
        print(f"Best match was {results[0]['relevance']:.0%}")
        return
    
    # Display results
    for i, result in enumerate(filtered_results):
        print(format_result(result, i))
    
    print(f"\nFound {len(filtered_results)} relevant results (out of {len(results)} total)")


if __name__ == '__main__':
    main()

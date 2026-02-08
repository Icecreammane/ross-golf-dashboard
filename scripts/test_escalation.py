#!/usr/bin/env python3
"""
Escalation Testing CLI - Test the smart escalation layer

Usage:
  python3 test_escalation.py "What time is it?"
  python3 test_escalation.py --interactive
  python3 test_escalation.py --stats
  python3 test_escalation.py --benchmark
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime
from smart_escalation_engine import get_engine, ComplexityScore

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def print_complexity_bar(label: str, value: int, width: int = 30):
    """Print a visual bar for complexity metrics"""
    filled = int((value / 100) * width)
    bar = "█" * filled + "░" * (width - filled)
    
    color = Colors.OKGREEN
    if value > 70:
        color = Colors.FAIL
    elif value > 40:
        color = Colors.WARNING
    
    print(f"  {label:25s} {color}{bar}{Colors.ENDC} {value:3d}/100")


def test_query(engine, query: str, context: dict = None, show_response: bool = True):
    """Test a single query"""
    print(f"\n{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}Query:{Colors.ENDC} {query}")
    print(f"{Colors.BOLD}{'='*70}{Colors.ENDC}\n")
    
    # Route the query
    decision = engine.route_query(query, context)
    
    # Show complexity breakdown
    print(f"{Colors.BOLD}Complexity Analysis:{Colors.ENDC}")
    print_complexity_bar("Overall", decision.complexity.overall)
    print_complexity_bar("Factual vs Reasoning", decision.complexity.factual_vs_reasoning)
    print_complexity_bar("Data Retrieval", decision.complexity.data_retrieval)
    print_complexity_bar("Decision Making", decision.complexity.decision_making)
    print_complexity_bar("Time Sensitivity", decision.complexity.time_sensitivity)
    print_complexity_bar("Reversibility", decision.complexity.reversibility)
    print_complexity_bar("Local Confidence", decision.complexity.confidence)
    
    # Show routing decision
    print(f"\n{Colors.BOLD}Routing Decision:{Colors.ENDC}")
    
    if decision.route == "local":
        print(f"  Route:        {Colors.OKGREEN}LOCAL{Colors.ENDC} (handled by Llama)")
        print(f"  Reason:       {decision.reason}")
        print(f"  Response time: {decision.response_time_ms}ms")
        print(f"  Tokens saved:  {decision.tokens_saved:,}")
        print(f"  Cost saved:    ${decision.cost_saved:.6f}")
        
        if show_response and decision.local_response:
            print(f"\n{Colors.BOLD}Local Response:{Colors.ENDC}")
            print(f"{Colors.OKCYAN}{decision.local_response}{Colors.ENDC}")
    else:
        print(f"  Route:        {Colors.WARNING}CLOUD{Colors.ENDC} (escalated to Sonnet)")
        print(f"  Reason:       {decision.reason}")
        print(f"  Evaluation:   {decision.response_time_ms}ms")
    
    print()
    return decision


def interactive_mode(engine):
    """Interactive testing mode"""
    print(f"{Colors.BOLD}Smart Escalation Testing - Interactive Mode{Colors.ENDC}")
    print("Type queries to test routing. Commands: /stats /quit /help\n")
    
    while True:
        try:
            query = input(f"{Colors.OKBLUE}>{Colors.ENDC} ").strip()
            
            if not query:
                continue
            
            if query == "/quit":
                break
            elif query == "/stats":
                show_stats(engine)
                continue
            elif query == "/help":
                print("\nCommands:")
                print("  /stats - Show cost savings statistics")
                print("  /quit  - Exit interactive mode")
                print("  /help  - Show this help")
                print("\nJust type any question to test routing.\n")
                continue
            
            test_query(engine, query, show_response=True)
        
        except KeyboardInterrupt:
            print("\n")
            break
        except EOFError:
            break


def show_stats(engine):
    """Show cost savings statistics"""
    savings = engine.get_cost_savings()
    
    print(f"\n{Colors.BOLD}Cost Savings Statistics{Colors.ENDC}")
    print(f"{'='*50}")
    print(f"Total queries:     {savings.get('total_queries', 0):,}")
    print(f"Local queries:     {Colors.OKGREEN}{savings.get('local_queries', 0):,}{Colors.ENDC} ({savings.get('local_percentage', 0)}%)")
    print(f"Cloud queries:     {Colors.WARNING}{savings.get('cloud_queries', 0):,}{Colors.ENDC}")
    print(f"Tokens saved:      {savings.get('tokens_saved', 0):,}")
    print(f"Cost saved:        {Colors.OKGREEN}${savings.get('cost_saved', 0):.4f}{Colors.ENDC}")
    
    if savings.get('started'):
        print(f"\nTracking since:    {savings['started']}")
    if savings.get('last_updated'):
        print(f"Last updated:      {savings['last_updated']}")
    
    print()


def benchmark_mode(engine):
    """Run benchmark with various query types"""
    print(f"{Colors.BOLD}Running Benchmark Suite{Colors.ENDC}\n")
    
    test_cases = [
        # Factual queries (should be local)
        ("What time is it?", "factual-simple"),
        ("What's the weather like?", "factual-data"),
        ("Show me today's memory", "factual-file"),
        
        # Light reasoning (should be local with high confidence)
        ("What's the difference between TCP and UDP?", "reasoning-light"),
        ("Explain how Python decorators work", "reasoning-light"),
        
        # Medium complexity (could go either way)
        ("Summarize the last week of work", "reasoning-medium"),
        ("What should I focus on today?", "reasoning-medium"),
        ("Analyze recent cost trends", "reasoning-medium"),
        
        # High complexity (should escalate)
        ("Design a distributed system architecture", "complex-architecture"),
        ("Should I invest in Bitcoin or Tesla?", "complex-decision"),
        ("Write a strategic plan for product launch", "complex-creative"),
        ("Refactor this entire codebase for performance", "complex-irreversible"),
    ]
    
    results = {"local": 0, "cloud": 0}
    
    for query, category in test_cases:
        decision = test_query(engine, query, show_response=False)
        results[decision.route] += 1
    
    print(f"\n{Colors.BOLD}Benchmark Results{Colors.ENDC}")
    print(f"{'='*50}")
    print(f"Total tests:       {len(test_cases)}")
    print(f"Local routing:     {Colors.OKGREEN}{results['local']}{Colors.ENDC} ({results['local']/len(test_cases)*100:.0f}%)")
    print(f"Cloud routing:     {Colors.WARNING}{results['cloud']}{Colors.ENDC} ({results['cloud']/len(test_cases)*100:.0f}%)")
    print()
    
    show_stats(engine)


def main():
    parser = argparse.ArgumentParser(
        description="Test the smart escalation layer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Test a single query
  %(prog)s "What time is it?"
  
  # Interactive mode
  %(prog)s --interactive
  
  # Show statistics
  %(prog)s --stats
  
  # Run benchmark suite
  %(prog)s --benchmark
        """
    )
    
    parser.add_argument("query", nargs="*", help="Query to test")
    parser.add_argument("-i", "--interactive", action="store_true", 
                       help="Interactive testing mode")
    parser.add_argument("-s", "--stats", action="store_true",
                       help="Show cost savings statistics")
    parser.add_argument("-b", "--benchmark", action="store_true",
                       help="Run benchmark suite")
    parser.add_argument("--no-response", action="store_true",
                       help="Don't show local responses")
    
    args = parser.parse_args()
    
    engine = get_engine()
    
    if args.stats:
        show_stats(engine)
    elif args.interactive:
        interactive_mode(engine)
    elif args.benchmark:
        benchmark_mode(engine)
    elif args.query:
        query = " ".join(args.query)
        test_query(engine, query, show_response=not args.no_response)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()

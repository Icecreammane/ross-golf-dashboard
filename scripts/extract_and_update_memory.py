#!/Users/clawdbot/clawd/memory/venv/bin/python3
"""
Auto-Memory Extraction System
Analyzes recent conversations and updates memory files + embeddings.
"""

import os
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Optional
from semantic_memory import SemanticMemory


class MemoryExtractor:
    """Extract and update memories from conversations."""
    
    def __init__(self):
        self.workspace = Path("/Users/clawdbot/clawd")
        self.memory_dir = self.workspace / "memory"
        self.memory_file = self.workspace / "MEMORY.md"
        self.journal_file = self.memory_dir / "jarvis-journal.md"
        self.semantic_mem = SemanticMemory()
    
    def get_today_log_path(self) -> Path:
        """Get path to today's daily log."""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.memory_dir / f"{today}.md"
    
    def log_conversation_snippet(self, snippet: str, tags: List[str] = None):
        """
        Log a conversation snippet to today's daily log.
        
        Args:
            snippet: Text to log
            tags: Optional tags for categorization
        """
        log_path = self.get_today_log_path()
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Create log entry
        entry = f"\n### {timestamp}"
        if tags:
            entry += f" [{', '.join(tags)}]"
        entry += f"\n{snippet}\n"
        
        # Append to daily log
        if log_path.exists():
            with open(log_path, 'a') as f:
                f.write(entry)
        else:
            # Create new daily log
            with open(log_path, 'w') as f:
                f.write(f"# Daily Log - {datetime.now().strftime('%Y-%m-%d')}\n")
                f.write(entry)
        
        print(f"✓ Logged to {log_path.name}")
    
    def extract_facts(self, text: str) -> List[str]:
        """
        Extract key facts from text.
        This is a simple implementation - can be enhanced with NLP.
        """
        facts = []
        
        # Look for explicit statements
        fact_indicators = [
            "Ross's", "My goal is", "I want to", "I prefer",
            "calorie goal", "protein goal", "weight goal",
            "email:", "lives in", "age:", "location:"
        ]
        
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(indicator.lower() in line.lower() for indicator in fact_indicators):
                # Clean up markdown
                cleaned = line.lstrip('#*- ').strip()
                if cleaned and len(cleaned) > 10:
                    facts.append(cleaned)
        
        return facts
    
    def update_memory_file(self, facts: List[str], section: str = None):
        """
        Update MEMORY.md with new facts.
        
        Args:
            facts: List of facts to add
            section: Optional section to update (default: append to end)
        """
        if not facts:
            return
        
        # Read current memory
        if self.memory_file.exists():
            with open(self.memory_file, 'r') as f:
                current_content = f.read()
        else:
            current_content = "# MEMORY.md — Long-Term Memory\n\n"
        
        # Check for duplicates
        new_facts = []
        for fact in facts:
            # Simple duplicate check (can be improved)
            if fact.lower() not in current_content.lower():
                new_facts.append(fact)
        
        if not new_facts:
            print("No new facts to add (duplicates)")
            return
        
        # Append new facts
        timestamp = datetime.now().strftime("%Y-%m-%d")
        update_section = f"\n\n## Auto-Extracted Facts ({timestamp})\n"
        for fact in new_facts:
            update_section += f"- {fact}\n"
        
        with open(self.memory_file, 'a') as f:
            f.write(update_section)
        
        print(f"✓ Added {len(new_facts)} new facts to MEMORY.md")
    
    def update_journal(self, entry: str):
        """Add entry to jarvis-journal.md."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M CST")
        
        journal_entry = f"\n\n---\n\n## Session: {timestamp}\n\n{entry}\n"
        
        with open(self.journal_file, 'a') as f:
            f.write(journal_entry)
        
        print(f"✓ Updated journal")
    
    def embed_recent_changes(self):
        """Re-embed files that were recently modified."""
        print("\nEmbedding recent changes...")
        
        # Always re-embed MEMORY.md and journal
        stats = {}
        
        if self.memory_file.exists():
            stats['MEMORY.md'] = self.semantic_mem.embed_file(
                str(self.memory_file), 'memory'
            )
        
        if self.journal_file.exists():
            stats['journal'] = self.semantic_mem.embed_file(
                str(self.journal_file), 'journal'
            )
        
        # Embed today's log
        today_log = self.get_today_log_path()
        if today_log.exists():
            stats['today_log'] = self.semantic_mem.embed_file(
                str(today_log), 'daily_log'
            )
        
        # Embed yesterday's log if it exists
        yesterday = datetime.now() - timedelta(days=1)
        yesterday_log = self.memory_dir / f"{yesterday.strftime('%Y-%m-%d')}.md"
        if yesterday_log.exists():
            stats['yesterday_log'] = self.semantic_mem.embed_file(
                str(yesterday_log), 'daily_log'
            )
        
        return stats
    
    def process_conversation(self, conversation_text: str, 
                            update_memory: bool = True,
                            update_journal: bool = True):
        """
        Process a conversation: extract facts, update files, embed.
        
        Args:
            conversation_text: The conversation to process
            update_memory: Whether to update MEMORY.md
            update_journal: Whether to update journal
        """
        print("Processing conversation...")
        
        # Extract facts
        facts = self.extract_facts(conversation_text)
        print(f"Extracted {len(facts)} potential facts")
        
        # Log to daily file
        self.log_conversation_snippet(
            conversation_text[:500] + "..." if len(conversation_text) > 500 else conversation_text,
            tags=['auto-extracted']
        )
        
        # Update memory file
        if update_memory and facts:
            self.update_memory_file(facts)
        
        # Update journal
        if update_journal:
            journal_entry = f"### Auto-Extraction Run\n\n"
            journal_entry += f"Processed {len(conversation_text)} chars of conversation.\n"
            journal_entry += f"Extracted {len(facts)} facts.\n"
            if facts:
                journal_entry += f"\nTop facts:\n"
                for fact in facts[:5]:
                    journal_entry += f"- {fact}\n"
            
            self.update_journal(journal_entry)
        
        # Re-embed changes
        embed_stats = self.embed_recent_changes()
        
        print("\n✓ Memory extraction complete")
        print(f"  Facts extracted: {len(facts)}")
        print(f"  Files embedded: {sum(embed_stats.values())} chunks")
        
        return {
            'facts_extracted': len(facts),
            'embedding_stats': embed_stats
        }


def main():
    """CLI interface for memory extraction."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Extract and update memories from conversations'
    )
    
    parser.add_argument('-f', '--file', help='Process conversation from file')
    parser.add_argument('-t', '--text', help='Process conversation text directly')
    parser.add_argument('--no-memory', action='store_true',
                       help='Skip updating MEMORY.md')
    parser.add_argument('--no-journal', action='store_true',
                       help='Skip updating journal')
    parser.add_argument('--embed-only', action='store_true',
                       help='Only re-embed existing files')
    
    args = parser.parse_args()
    
    extractor = MemoryExtractor()
    
    if args.embed_only:
        print("Re-embedding recent changes...")
        stats = extractor.embed_recent_changes()
        print("\nEmbedding complete:")
        for source, count in stats.items():
            print(f"  {source}: {count} chunks")
        return
    
    # Get conversation text
    conversation_text = None
    
    if args.file:
        with open(args.file, 'r') as f:
            conversation_text = f.read()
    elif args.text:
        conversation_text = args.text
    else:
        print("Reading conversation from stdin...")
        print("(Type your conversation, then press Ctrl+D when done)")
        conversation_text = sys.stdin.read()
    
    if not conversation_text:
        print("No conversation text provided")
        return
    
    # Process
    result = extractor.process_conversation(
        conversation_text,
        update_memory=not args.no_memory,
        update_journal=not args.no_journal
    )
    
    print(f"\nExtraction complete: {result['facts_extracted']} facts")


if __name__ == '__main__':
    main()

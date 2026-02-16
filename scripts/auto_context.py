#!/usr/bin/env python3
"""
Auto-Context Loader - Fixes persistent memory amnesia
Automatically loads relevant context at session start
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
import sys

WORKSPACE = Path('/Users/clawdbot/clawd')
MEMORY_DIR = WORKSPACE / 'memory'
LOGS_DIR = WORKSPACE / 'logs'

class AutoContextLoader:
    def __init__(self):
        self.context = {
            'loaded_files': [],
            'key_facts': [],
            'recent_activities': [],
            'active_projects': [],
            'important_urls': [],
            'warnings': []
        }
    
    def load_session_summary(self):
        """Load SESSION_SUMMARY.md"""
        session_summary = WORKSPACE / 'SESSION_SUMMARY.md'
        if session_summary.exists():
            content = session_summary.read_text()
            self.context['loaded_files'].append('SESSION_SUMMARY.md')
            
            # Extract key info
            if 'LIVE URL:' in content:
                lines = content.split('\n')
                for line in lines:
                    if 'LIVE URL:' in line or 'https://' in line:
                        self.context['important_urls'].append(line.strip())
            
            # Extract active projects
            if 'ACTIVE PROJECTS' in content or '## ACTIVE PROJECTS' in content:
                self.context['key_facts'].append('SESSION_SUMMARY.md contains active project info')
            
            return content
        return None
    
    def load_memory_files(self, days=2):
        """Load recent daily memory files"""
        loaded_content = []
        
        for i in range(days):
            date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            memory_file = MEMORY_DIR / f'{date}.md'
            
            if memory_file.exists():
                content = memory_file.read_text()
                self.context['loaded_files'].append(f'memory/{date}.md')
                loaded_content.append(content)
                
                # Extract activities
                if '##' in content:
                    lines = content.split('\n')
                    for line in lines:
                        if line.startswith('## '):
                            self.context['recent_activities'].append(line.strip('# '))
        
        return '\n\n'.join(loaded_content)
    
    def load_long_term_memory(self, session_type='main'):
        """Load MEMORY.md (only in main session)"""
        if session_type != 'main':
            self.context['warnings'].append('MEMORY.md NOT loaded - not in main session')
            return None
        
        memory_file = WORKSPACE / 'MEMORY.md'
        if memory_file.exists():
            self.context['loaded_files'].append('MEMORY.md')
            return memory_file.read_text()
        return None
    
    def check_instant_recall(self):
        """Check if instant_recall is available"""
        instant_recall_script = WORKSPACE / 'scripts' / 'instant_recall.py'
        if instant_recall_script.exists():
            self.context['key_facts'].append('instant_recall.py available for deep memory search')
            return True
        return False
    
    def scan_active_builds(self):
        """Scan for active BUILD_*.md files"""
        builds = list(WORKSPACE.glob('BUILD_*.md'))
        
        # Get most recent 5
        builds_sorted = sorted(builds, key=lambda p: p.stat().st_mtime, reverse=True)[:5]
        
        for build in builds_sorted:
            self.context['active_projects'].append(build.name)
    
    def scan_live_services(self):
        """Check what services are running"""
        services = []
        
        # Check for common ports
        import subprocess
        ports_to_check = [3000, 5001, 8080, 5000]
        
        for port in ports_to_check:
            try:
                result = subprocess.run(
                    ['lsof', '-i', f':{port}'],
                    capture_output=True,
                    text=True,
                    timeout=1
                )
                if result.returncode == 0 and result.stdout:
                    services.append(f'Service running on port {port}')
            except:
                pass
        
        if services:
            self.context['key_facts'].extend(services)
    
    def load_context_index(self):
        """Load memory index if it exists"""
        index_file = MEMORY_DIR / 'memory_index.json'
        if index_file.exists():
            try:
                with open(index_file) as f:
                    index = json.load(f)
                    self.context['loaded_files'].append('memory/memory_index.json')
                    
                    # Get recent topics
                    if 'topics' in index:
                        self.context['key_facts'].append(f"{len(index['topics'])} indexed topics available")
            except:
                pass
    
    def generate_context_summary(self):
        """Generate a human-readable context summary"""
        summary = []
        
        summary.append("🧠 AUTO-CONTEXT LOADED")
        summary.append("=" * 50)
        
        if self.context['loaded_files']:
            summary.append(f"\n📁 Loaded Files ({len(self.context['loaded_files'])}):")
            for file in self.context['loaded_files']:
                summary.append(f"  ✓ {file}")
        
        if self.context['important_urls']:
            summary.append(f"\n🔗 Important URLs:")
            for url in self.context['important_urls'][:5]:
                summary.append(f"  • {url}")
        
        if self.context['active_projects']:
            summary.append(f"\n🚀 Active Projects:")
            for project in self.context['active_projects'][:5]:
                summary.append(f"  • {project}")
        
        if self.context['key_facts']:
            summary.append(f"\n💡 Key Facts:")
            for fact in self.context['key_facts'][:10]:
                summary.append(f"  • {fact}")
        
        if self.context['warnings']:
            summary.append(f"\n⚠️  Warnings:")
            for warning in self.context['warnings']:
                summary.append(f"  ! {warning}")
        
        summary.append("\n" + "=" * 50)
        summary.append("✅ Context loading complete. Ready to assist.")
        
        return '\n'.join(summary)
    
    def load_all(self, session_type='main'):
        """Load all context sources"""
        print("Loading session context...")
        
        self.load_session_summary()
        self.load_memory_files(days=2)
        self.load_long_term_memory(session_type)
        self.check_instant_recall()
        self.scan_active_builds()
        self.scan_live_services()
        self.load_context_index()
        
        summary = self.generate_context_summary()
        
        # Log what was loaded
        log_file = LOGS_DIR / 'context-loader.log'
        with open(log_file, 'a') as f:
            f.write(f"\n{datetime.now().isoformat()}\n")
            f.write(summary)
            f.write("\n\n")
        
        return summary
    
    def should_have_known(self, question, topic=None):
        """
        Self-audit: Check if this question should have been answered from memory
        Returns: (should_have_known: bool, source: str)
        """
        # Check if topic is in loaded files
        if topic:
            for file in self.context['loaded_files']:
                # TODO: Actually search file contents
                pass
        
        # For now, just log the question
        audit_log = LOGS_DIR / 'memory-audit.log'
        with open(audit_log, 'a') as f:
            f.write(f"{datetime.now().isoformat()} - Question: {question}\n")
        
        return False, "unknown"

def main():
    """Run auto-context loader"""
    loader = AutoContextLoader()
    
    # Determine session type (default to main)
    session_type = 'main'
    if len(sys.argv) > 1:
        session_type = sys.argv[1]
    
    summary = loader.load_all(session_type)
    print(summary)
    
    # Return context data as JSON for programmatic use
    return loader.context

if __name__ == '__main__':
    main()

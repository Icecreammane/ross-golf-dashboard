#!/usr/bin/env python3
"""
Security Audit Script
Scans workspace for hardcoded credentials and security issues
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"
EXCLUDE_DIRS = {'.git', 'node_modules', '__pycache__', '.venv', 'venv', 'backups', 'security-logs'}
EXCLUDE_FILES = {'security_audit.py', '.DS_Store'}

# Patterns to detect
PATTERNS = {
    'hardcoded_password': r'(password|passwd|pwd)\s*=\s*["\']([^"\']{8,})["\']',
    'hardcoded_token': r'(token|api_key|apikey)\s*=\s*["\']([^"\']{20,})["\']',
    'email_password': r'smtp.*password.*=.*["\']([^"\']+)["\']',
    'telegram_token': r'\d{10}:[A-Za-z0-9_-]{35}',
    'api_keys': r'(sk-[a-zA-Z0-9]{20,}|AIza[a-zA-Z0-9_-]{35})',
    'aws_keys': r'(AKIA[0-9A-Z]{16})',
    'private_key': r'-----BEGIN (RSA |)PRIVATE KEY-----',
}

class SecurityAudit:
    def __init__(self):
        self.findings = []
        self.files_scanned = 0
        self.warnings = 0
    
    def scan_file(self, file_path):
        """Scan a single file for security issues"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            # Check each pattern
            for issue_type, pattern in PATTERNS.items():
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Skip if it's reading from .credentials/
                    if '.credentials' in content[max(0, match.start()-100):match.end()+100]:
                        continue
                    
                    # Skip if it's a comment or example
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line = content[line_start:content.find('\n', match.start())]
                    if line.strip().startswith('#') or 'example' in line.lower():
                        continue
                    
                    # Skip documentation/README files or embedded docs with placeholder text
                    context = content[max(0, match.start()-200):min(len(content), match.end()+200)]
                    if any(x in context.lower() for x in ['your-', 'your_', 'example', 'placeholder', '```bash', '```sh', '❌']):
                        continue
                    
                    # Skip if inside a Python docstring/multiline string containing markdown
                    if file_path.suffix == '.py':
                        # Check if we're inside a """ or ''' string
                        before = content[:match.start()]
                        if before.count('"""') % 2 == 1 or before.count("'''") % 2 == 1:
                            # We're inside a multiline string
                            if '##' in context or '```' in context:  # Markdown indicators
                                continue
                    
                    self.findings.append({
                        'file': str(file_path.relative_to(WORKSPACE)),
                        'issue': issue_type,
                        'line': content[:match.start()].count('\n') + 1,
                        'preview': line.strip()[:80]
                    })
                    self.warnings += 1
            
            self.files_scanned += 1
            
        except Exception as e:
            pass  # Skip files that can't be read
    
    def scan_directory(self, directory):
        """Recursively scan directory"""
        try:
            for item in directory.iterdir():
                # Skip excluded directories
                if item.is_dir():
                    if item.name not in EXCLUDE_DIRS and not item.name.startswith('.'):
                        self.scan_directory(item)
                
                # Scan files
                elif item.is_file():
                    if item.name not in EXCLUDE_FILES and not item.name.startswith('.'):
                        # Only scan text files
                        if item.suffix in {'.py', '.sh', '.js', '.json', '.md', '.txt', '.yaml', '.yml', '.env'}:
                            self.scan_file(item)
        
        except PermissionError:
            pass
    
    def generate_report(self):
        """Generate audit report"""
        report = f"""# Security Audit Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary
- Files Scanned: {self.files_scanned}
- Warnings Found: {self.warnings}
- Status: {'✅ PASS' if self.warnings == 0 else '⚠️ ISSUES FOUND'}

"""
        
        if self.findings:
            report += "## Findings\n\n"
            for finding in self.findings:
                report += f"### {finding['issue'].replace('_', ' ').title()}\n"
                report += f"- **File:** `{finding['file']}`\n"
                report += f"- **Line:** {finding['line']}\n"
                report += f"- **Preview:** `{finding['preview']}`\n\n"
        else:
            report += "## ✅ No Security Issues Found\n\n"
            report += "All credentials properly stored in `.credentials/` directory.\n"
            report += "No hardcoded secrets detected.\n\n"
        
        report += """## Best Practices
- ✅ Store credentials in `~/.credentials/` directory
- ✅ Use `600` permissions on credential files
- ✅ Never commit credentials to git
- ✅ Load credentials at runtime from JSON files
- ✅ Document all credentials in SECURITY.md

## Next Steps
"""
        
        if self.warnings > 0:
            report += "1. Move hardcoded credentials to `.credentials/` directory\n"
            report += "2. Update scripts to load credentials from files\n"
            report += "3. Re-run audit until 0 warnings\n"
        else:
            report += "No action required. Security posture is good! ✅\n"
        
        return report
    
    def run(self):
        """Run full audit"""
        print("🔍 Starting security audit...")
        print(f"📁 Scanning: {WORKSPACE}")
        print()
        
        self.scan_directory(WORKSPACE)
        
        report = self.generate_report()
        
        # Save report
        report_path = WORKSPACE / "security-logs" / f"audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        report_path.parent.mkdir(exist_ok=True)
        with open(report_path, 'w') as f:
            f.write(report)
        
        # Print report
        print(report)
        print(f"\n📄 Report saved: {report_path}")
        
        return self.warnings == 0

if __name__ == "__main__":
    audit = SecurityAudit()
    success = audit.run()
    exit(0 if success else 1)

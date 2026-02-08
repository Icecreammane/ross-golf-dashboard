#!/usr/bin/env python3
"""
Security Scanner
Scan files for sensitive data before git operations
Prevent accidental exposure of secrets
"""

import re
import os
from pathlib import Path
from datetime import datetime

WORKSPACE = Path.home() / "clawd"

class SecurityScanner:
    """Scan for sensitive data patterns"""
    
    def __init__(self):
        # Sensitive patterns to detect
        self.patterns = {
            "api_key": [
                r'(api[_-]?key|apikey)["\s:=]+[a-zA-Z0-9_\-]{20,}',
                r'sk-[a-zA-Z0-9]{20,}',  # OpenAI key
                r'AKIA[0-9A-Z]{16}',  # AWS key
            ],
            "token": [
                r'(access[_-]?token|bearer)["\s:=]+[a-zA-Z0-9_\-\.]{20,}',
                r'ghp_[a-zA-Z0-9]{36}',  # GitHub token
                r'gho_[a-zA-Z0-9]{36}',  # GitHub OAuth token
            ],
            "password": [
                r'password["\s:=]+[^\s]{8,}',
                r'passwd["\s:=]+[^\s]{8,}',
            ],
            "private_key": [
                r'-----BEGIN (RSA |DSA |EC )?PRIVATE KEY-----',
                r'-----BEGIN OPENSSH PRIVATE KEY-----',
            ],
            "credential": [
                r'(username|user)["\s:=]+[a-zA-Z0-9_\-]+["\s:=]+.*password',
                r'credentials?["\s:=]+\{',
            ],
            "ssn": [
                r'\b\d{3}-\d{2}-\d{4}\b',  # SSN format
            ],
            "credit_card": [
                r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b',  # Credit card
            ],
            "email_in_code": [
                r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}(?=["\'])',  # Email in quotes
            ],
            "phone": [
                r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # Phone number
            ]
        }
        
        # Whitelisted patterns (safe to include)
        self.whitelist = [
            r'example\.com',
            r'test@example\.com',
            r'your-api-key-here',
            r'placeholder',
            r'dummy',
            r'<[A-Z_]+>',  # Template variables like <API_KEY>
        ]
    
    def scan_text(self, text, filename="unknown"):
        """
        Scan text for sensitive data
        Returns: List of findings
        """
        findings = []
        
        for category, patterns in self.patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                
                for match in matches:
                    matched_text = match.group(0)
                    
                    # Check whitelist
                    is_whitelisted = any(
                        re.search(wl, matched_text, re.IGNORECASE)
                        for wl in self.whitelist
                    )
                    
                    if not is_whitelisted:
                        # Get line number
                        line_num = text[:match.start()].count('\n') + 1
                        
                        findings.append({
                            "category": category,
                            "pattern": pattern,
                            "match": matched_text[:50],  # First 50 chars
                            "file": filename,
                            "line": line_num,
                            "severity": self._get_severity(category)
                        })
        
        return findings
    
    def _get_severity(self, category):
        """Get severity level for category"""
        high = ["api_key", "token", "password", "private_key"]
        medium = ["credential", "ssn", "credit_card"]
        
        if category in high:
            return "HIGH"
        elif category in medium:
            return "MEDIUM"
        else:
            return "LOW"
    
    def scan_file(self, filepath):
        """Scan a single file"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            return self.scan_text(content, str(filepath))
        
        except Exception as e:
            return [{
                "category": "error",
                "file": str(filepath),
                "error": str(e),
                "severity": "LOW"
            }]
    
    def scan_directory(self, directory, extensions=None):
        """
        Scan directory for sensitive data
        
        Args:
            directory: Path to scan
            extensions: List of file extensions to scan (None = all text files)
        """
        if extensions is None:
            extensions = ['.py', '.js', '.json', '.md', '.txt', '.env', '.sh', '.yaml', '.yml']
        
        all_findings = []
        
        for root, dirs, files in os.walk(directory):
            # Skip certain directories
            skip_dirs = {'.git', 'node_modules', '__pycache__', '.venv', 'venv'}
            dirs[:] = [d for d in dirs if d not in skip_dirs]
            
            for file in files:
                filepath = Path(root) / file
                
                # Check extension
                if filepath.suffix in extensions or extensions is None:
                    findings = self.scan_file(filepath)
                    all_findings.extend(findings)
        
        return all_findings
    
    def scan_git_staged(self):
        """Scan only git staged files"""
        import subprocess
        
        try:
            # Get staged files
            result = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=WORKSPACE,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            staged_files = result.stdout.strip().split('\n')
            staged_files = [f for f in staged_files if f]  # Remove empty
            
            all_findings = []
            
            for filepath in staged_files:
                full_path = WORKSPACE / filepath
                if full_path.exists() and full_path.is_file():
                    findings = self.scan_file(full_path)
                    all_findings.extend(findings)
            
            return all_findings
        
        except Exception as e:
            return [{
                "category": "error",
                "error": f"Failed to scan staged files: {e}",
                "severity": "LOW"
            }]
    
    def generate_report(self, findings):
        """Generate human-readable report"""
        if not findings:
            return "✅ No sensitive data detected"
        
        # Group by severity
        by_severity = {"HIGH": [], "MEDIUM": [], "LOW": []}
        for finding in findings:
            severity = finding.get("severity", "LOW")
            by_severity[severity].append(finding)
        
        report = []
        report.append("=" * 70)
        report.append("🔒 SECURITY SCAN RESULTS")
        report.append("=" * 70)
        report.append("")
        
        total = len(findings)
        high = len(by_severity["HIGH"])
        medium = len(by_severity["MEDIUM"])
        low = len(by_severity["LOW"])
        
        report.append(f"Total findings: {total}")
        report.append(f"  🔴 HIGH: {high}")
        report.append(f"  🟡 MEDIUM: {medium}")
        report.append(f"  🟢 LOW: {low}")
        report.append("")
        
        # Show high priority findings
        if by_severity["HIGH"]:
            report.append("🔴 HIGH PRIORITY:")
            for finding in by_severity["HIGH"][:10]:  # First 10
                report.append(f"  • {finding['category'].upper()}")
                report.append(f"    File: {finding['file']}")
                report.append(f"    Line: {finding.get('line', '?')}")
                report.append(f"    Match: {finding.get('match', 'N/A')}")
            report.append("")
        
        # Show medium priority
        if by_severity["MEDIUM"]:
            report.append("🟡 MEDIUM PRIORITY:")
            for finding in by_severity["MEDIUM"][:5]:
                report.append(f"  • {finding['category'].upper()} in {finding['file']}")
            report.append("")
        
        report.append("=" * 70)
        report.append("⚠️  Review these findings before committing!")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def should_block_commit(self, findings):
        """Determine if commit should be blocked"""
        # Block if any HIGH severity findings
        high_severity = [f for f in findings if f.get("severity") == "HIGH"]
        
        return len(high_severity) > 0, high_severity


def scan_before_commit():
    """Run security scan before git commit"""
    scanner = SecurityScanner()
    
    print("🔍 Scanning staged files for sensitive data...")
    findings = scanner.scan_git_staged()
    
    if not findings:
        print("✅ No sensitive data detected - safe to commit")
        return True
    
    # Generate report
    report = scanner.generate_report(findings)
    print(report)
    
    # Check if should block
    should_block, high_findings = scanner.should_block_commit(findings)
    
    if should_block:
        print("\n❌ COMMIT BLOCKED - HIGH severity findings detected")
        print("   Remove sensitive data before committing")
        return False
    else:
        print("\n⚠️  WARNING - Medium/Low findings detected")
        print("   Review carefully before pushing")
        return True


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "staged":
            # Scan staged files
            result = scan_before_commit()
            sys.exit(0 if result else 1)
        
        elif sys.argv[1] == "scan":
            # Scan workspace
            scanner = SecurityScanner()
            print("🔍 Scanning workspace...")
            findings = scanner.scan_directory(WORKSPACE)
            report = scanner.generate_report(findings)
            print(report)
    
    else:
        print("Usage:")
        print("  python3 security_scanner.py staged   - Scan git staged files")
        print("  python3 security_scanner.py scan     - Scan entire workspace")


if __name__ == "__main__":
    main()

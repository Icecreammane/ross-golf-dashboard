#!/usr/bin/env python3
"""
Safe Git Wrapper
Add safety checks to git operations
Prevent accidental exposure and destructive operations
"""

import subprocess
import sys
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
sys.path.append(str(WORKSPACE / "scripts"))

from security_scanner import SecurityScanner

class SafeGit:
    """Safe git operations with security checks"""
    
    def __init__(self):
        self.scanner = SecurityScanner()
        self.workspace = WORKSPACE
    
    def safe_commit(self, message, additional_message=None, auto=False):
        """
        Safely commit with security scanning
        
        Args:
            message: Commit message
            additional_message: Extended description
            auto: If True, running in autonomous mode
        """
        # Scan staged files
        print("🔍 Security scan before commit...")
        findings = self.scanner.scan_git_staged()
        
        if findings:
            should_block, high_findings = self.scanner.should_block_commit(findings)
            
            if should_block:
                print("\n❌ COMMIT BLOCKED - Sensitive data detected:")
                for finding in high_findings[:5]:
                    print(f"  • {finding['category']} in {finding['file']} (line {finding.get('line', '?')})")
                
                return {"success": False, "reason": "sensitive_data_detected", "findings": findings}
        
        # Build commit command
        cmd = ["git", "commit", "-m", message]
        if additional_message:
            cmd.extend(["-m", additional_message])
        
        # Add auto flag to message if autonomous
        if auto:
            cmd.extend(["-m", "[AUTO-COMMIT]"])
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print("✅ Commit successful")
                return {"success": True, "output": result.stdout}
            else:
                print(f"❌ Commit failed: {result.stderr}")
                return {"success": False, "reason": "git_error", "error": result.stderr}
        
        except Exception as e:
            print(f"❌ Commit error: {e}")
            return {"success": False, "reason": "exception", "error": str(e)}
    
    def safe_push(self, branch="main", force=False):
        """
        Safely push with additional checks
        
        Args:
            branch: Branch to push
            force: Force push (dangerous, requires extra confirmation)
        """
        # Check for large files
        print("🔍 Checking for large files...")
        large_files = self._check_large_files()
        
        if large_files:
            print("⚠️  WARNING: Large files detected:")
            for filepath, size_mb in large_files[:5]:
                print(f"  • {filepath}: {size_mb:.1f} MB")
        
        # Check branch
        if branch != "main":
            print(f"⚠️  WARNING: Pushing to non-main branch: {branch}")
        
        # Check force push
        if force:
            print("🚨 FORCE PUSH DETECTED - This can overwrite history!")
            print("   This is a DANGEROUS operation.")
            
            # In autonomous mode, never allow force push
            return {"success": False, "reason": "force_push_blocked"}
        
        # Do the push
        cmd = ["git", "push", "origin", branch]
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ Pushed to {branch}")
                return {"success": True, "output": result.stdout}
            else:
                print(f"❌ Push failed: {result.stderr}")
                return {"success": False, "reason": "git_error", "error": result.stderr}
        
        except Exception as e:
            print(f"❌ Push error: {e}")
            return {"success": False, "reason": "exception", "error": str(e)}
    
    def _check_large_files(self, size_limit_mb=10):
        """Check for files larger than size limit"""
        large_files = []
        
        try:
            # Get list of tracked files
            result = subprocess.run(
                ["git", "ls-files"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            files = result.stdout.strip().split('\n')
            
            for filepath in files:
                full_path = self.workspace / filepath
                if full_path.exists():
                    size_mb = full_path.stat().st_size / (1024 * 1024)
                    if size_mb > size_limit_mb:
                        large_files.append((filepath, size_mb))
            
            large_files.sort(key=lambda x: x[1], reverse=True)
            
        except Exception:
            pass
        
        return large_files
    
    def safe_add(self, paths=None):
        """
        Safely add files with checks
        
        Args:
            paths: List of paths to add (None = add all)
        """
        if paths is None:
            paths = ["."]
        
        # Scan files before adding
        print("🔍 Scanning files before staging...")
        
        all_findings = []
        for path in paths:
            full_path = self.workspace / path
            
            if full_path.is_file():
                findings = self.scanner.scan_file(full_path)
                all_findings.extend(findings)
            elif full_path.is_dir():
                findings = self.scanner.scan_directory(full_path)
                all_findings.extend(findings)
        
        if all_findings:
            should_block, high_findings = self.scanner.should_block_commit(all_findings)
            
            if should_block:
                print("❌ ADD BLOCKED - Sensitive data detected")
                return {"success": False, "reason": "sensitive_data", "findings": all_findings}
            else:
                print("⚠️  WARNING: Medium/Low findings detected")
        
        # Do the add
        cmd = ["git", "add"] + paths
        
        try:
            result = subprocess.run(
                cmd,
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                print(f"✅ Staged {len(paths)} path(s)")
                return {"success": True}
            else:
                print(f"❌ Add failed: {result.stderr}")
                return {"success": False, "reason": "git_error", "error": result.stderr}
        
        except Exception as e:
            print(f"❌ Add error: {e}")
            return {"success": False, "reason": "exception", "error": str(e)}
    
    def status(self):
        """Get git status"""
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=self.workspace,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return {"success": True, "output": result.stdout}
        
        except Exception as e:
            return {"success": False, "error": str(e)}


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 safe_git.py commit <message>")
        print("  python3 safe_git.py push [branch]")
        print("  python3 safe_git.py add [paths...]")
        print("  python3 safe_git.py status")
        sys.exit(1)
    
    git = SafeGit()
    action = sys.argv[1]
    
    if action == "commit":
        if len(sys.argv) < 3:
            print("Error: Commit message required")
            sys.exit(1)
        
        message = sys.argv[2]
        additional = sys.argv[3] if len(sys.argv) > 3 else None
        
        result = git.safe_commit(message, additional)
        sys.exit(0 if result["success"] else 1)
    
    elif action == "push":
        branch = sys.argv[2] if len(sys.argv) > 2 else "main"
        result = git.safe_push(branch)
        sys.exit(0 if result["success"] else 1)
    
    elif action == "add":
        paths = sys.argv[2:] if len(sys.argv) > 2 else None
        result = git.safe_add(paths)
        sys.exit(0 if result["success"] else 1)
    
    elif action == "status":
        result = git.status()
        if result["success"]:
            print(result["output"])
        sys.exit(0 if result["success"] else 1)
    
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)


if __name__ == "__main__":
    main()

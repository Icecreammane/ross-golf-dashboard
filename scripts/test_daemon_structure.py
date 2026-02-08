#!/usr/bin/env python3
"""
Test daemon structure without connecting to Gmail
Verifies all components are properly configured
"""

import sys
from pathlib import Path

WORKSPACE = Path("/Users/clawdbot/clawd")

def check_file(path, should_be_executable=False):
    """Check if file exists and optionally if it's executable"""
    if not path.exists():
        return False, f"Missing: {path}"
    
    if should_be_executable:
        import stat
        is_executable = path.stat().st_mode & stat.S_IXUSR
        if not is_executable:
            return False, f"Not executable: {path}"
    
    return True, f"OK: {path.name}"

def main():
    print("=" * 60)
    print("Email Daemon Structure Test")
    print("=" * 60)
    print()
    
    tests = []
    
    # Check directories
    print("📁 Directories:")
    for dir_name in ["scripts", "data", "logs"]:
        dir_path = WORKSPACE / dir_name
        exists = dir_path.exists() and dir_path.is_dir()
        status = "✅" if exists else "❌"
        tests.append(exists)
        print(f"  {status} {dir_name}/")
    print()
    
    # Check scripts
    print("📜 Scripts:")
    scripts = [
        ("email_daemon.py", True),
        ("setup_email_daemon.sh", True),
        ("test_email_filters.py", True),
        ("view_email_summaries.py", True),
    ]
    
    for script_name, should_exec in scripts:
        script_path = WORKSPACE / "scripts" / script_name
        passed, msg = check_file(script_path, should_exec)
        status = "✅" if passed else "❌"
        tests.append(passed)
        print(f"  {status} {msg}")
    print()
    
    # Check documentation
    print("📚 Documentation:")
    docs = [
        "EMAIL_DAEMON.md",
        "EMAIL_DAEMON_TEST_REPORT.md",
        "QUICK_START_EMAIL_DAEMON.md",
    ]
    
    for doc_name in docs:
        doc_path = WORKSPACE / doc_name
        passed, msg = check_file(doc_path)
        status = "✅" if passed else "❌"
        tests.append(passed)
        print(f"  {status} {msg}")
    print()
    
    # Check launchd plist
    print("⚙️  LaunchD Configuration:")
    plist_path = Path.home() / "Library/LaunchAgents/com.jarvis.email-daemon.plist"
    passed, msg = check_file(plist_path)
    status = "✅" if passed else "❌"
    tests.append(passed)
    print(f"  {status} {msg}")
    
    # Validate plist syntax
    if passed:
        import subprocess
        result = subprocess.run(
            ["plutil", "-lint", str(plist_path)],
            capture_output=True,
            text=True
        )
        plist_valid = result.returncode == 0
        status = "✅" if plist_valid else "❌"
        tests.append(plist_valid)
        print(f"  {status} plist syntax valid")
    print()
    
    # Check .env file
    print("🔐 Configuration:")
    env_path = WORKSPACE / ".env"
    env_exists = env_path.exists()
    status = "✅" if env_exists else "❌"
    tests.append(env_exists)
    print(f"  {status} .env file exists")
    
    if env_exists:
        env_content = env_path.read_text()
        has_email_config = "JARVIS_EMAIL" in env_content
        status = "✅" if has_email_config else "❌"
        tests.append(has_email_config)
        print(f"  {status} Email config present")
        
        has_password = "JARVIS_EMAIL_PASSWORD" in env_content
        status = "✅" if has_password else "❌"
        tests.append(has_password)
        print(f"  {status} Password field present")
        
        needs_setup = "your-gmail-app-password-here" in env_content
        status = "⚠️ " if needs_setup else "✅"
        print(f"  {status} Password {'needs setup' if needs_setup else 'configured'}")
    print()
    
    # Check Python dependencies
    print("🐍 Python Dependencies:")
    deps = ["imaplib", "email", "json", "dotenv", "re", "traceback"]
    
    for dep in deps:
        try:
            __import__(dep)
            tests.append(True)
            print(f"  ✅ {dep}")
        except ImportError:
            tests.append(False)
            print(f"  ❌ {dep} (missing)")
    print()
    
    # Import and test filter logic
    print("🔍 Filter Logic:")
    try:
        sys.path.insert(0, str(WORKSPACE / "scripts"))
        from email_daemon import is_important
        
        # Quick test
        result, reason = is_important("urgent", "URGENT: Test", "test@example.com")
        if result:
            tests.append(True)
            print(f"  ✅ Filter logic works")
        else:
            tests.append(False)
            print(f"  ❌ Filter logic failed")
    except Exception as e:
        tests.append(False)
        print(f"  ❌ Filter import failed: {e}")
    print()
    
    # Summary
    print("=" * 60)
    passed = sum(tests)
    total = len(tests)
    percentage = (passed / total * 100) if total > 0 else 0
    
    print(f"Results: {passed}/{total} checks passed ({percentage:.1f}%)")
    
    if percentage == 100:
        print("✅ All systems ready!")
        print("\nNext step: Add Gmail app password to .env")
    elif percentage >= 90:
        print("⚠️  Nearly ready - check warnings above")
    else:
        print("❌ Setup incomplete - check errors above")
    
    print("=" * 60)
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

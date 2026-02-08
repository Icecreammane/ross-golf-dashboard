#!/usr/bin/env python3
"""
Security Audit Logger
Tracks all daemon executions, sensitive file access, and security events
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

# Audit log directory
AUDIT_LOG_DIR = Path.home() / "clawd" / "security-logs"
AUDIT_LOG_DIR.mkdir(exist_ok=True, mode=0o755)

class SecurityAuditLogger:
    def __init__(self):
        self.log_date = datetime.now().strftime("%Y-%m-%d")
        self.log_file = AUDIT_LOG_DIR / f"audit-{self.log_date}.json"
        self.markdown_file = AUDIT_LOG_DIR / f"audit-{self.log_date}.md"
        
    def log_event(self, event_type, details, severity="INFO"):
        """Log a security event"""
        timestamp = datetime.now().isoformat()
        
        event = {
            "timestamp": timestamp,
            "type": event_type,
            "severity": severity,
            "details": details,
            "user": os.getenv("USER", "unknown"),
            "pid": os.getpid()
        }
        
        # Append to JSON log
        self._append_json_event(event)
        
        # Append to human-readable markdown log
        self._append_markdown_event(event)
        
        return event
    
    def _append_json_event(self, event):
        """Append event to JSON log file"""
        events = []
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    events = json.load(f)
            except json.JSONDecodeError:
                events = []
        
        events.append(event)
        
        with open(self.log_file, 'w') as f:
            json.dump(events, f, indent=2)
        
        # Set secure permissions on log file
        os.chmod(self.log_file, 0o600)
    
    def _append_markdown_event(self, event):
        """Append event to markdown log file"""
        severity_emoji = {
            "CRITICAL": "🔴",
            "HIGH": "🟠",
            "MEDIUM": "🟡",
            "LOW": "🔵",
            "INFO": "ℹ️"
        }
        
        emoji = severity_emoji.get(event['severity'], "ℹ️")
        
        with open(self.markdown_file, 'a') as f:
            if not self.markdown_file.exists() or os.path.getsize(self.markdown_file) == 0:
                f.write(f"# Security Audit Log - {self.log_date}\n\n")
            
            f.write(f"## {emoji} [{event['timestamp']}] {event['type']}\n")
            f.write(f"**Severity:** {event['severity']}  \n")
            f.write(f"**User:** {event['user']} (PID: {event['pid']})  \n")
            f.write(f"**Details:**\n")
            for key, value in event['details'].items():
                f.write(f"- **{key}:** {value}\n")
            f.write("\n---\n\n")
        
        # Set secure permissions
        os.chmod(self.markdown_file, 0o600)
    
    def log_daemon_execution(self, daemon_name, status, exit_code=None, duration=None):
        """Log daemon execution"""
        details = {
            "daemon": daemon_name,
            "status": status,
            "exit_code": exit_code if exit_code is not None else "N/A",
            "duration_seconds": duration if duration else "N/A"
        }
        
        severity = "INFO" if status == "success" else "MEDIUM"
        return self.log_event("DAEMON_EXECUTION", details, severity)
    
    def log_sensitive_file_access(self, file_path, operation, authorized=True):
        """Log access to sensitive files"""
        details = {
            "file": str(file_path),
            "operation": operation,
            "authorized": authorized
        }
        
        severity = "INFO" if authorized else "HIGH"
        return self.log_event("SENSITIVE_FILE_ACCESS", details, severity)
    
    def log_credential_access(self, credential_name, purpose):
        """Log credential access"""
        details = {
            "credential": credential_name,
            "purpose": purpose
        }
        
        return self.log_event("CREDENTIAL_ACCESS", details, "MEDIUM")
    
    def log_backup_execution(self, backup_type, status, files_backed_up=0, size_mb=0):
        """Log backup execution"""
        details = {
            "backup_type": backup_type,
            "status": status,
            "files_backed_up": files_backed_up,
            "size_mb": size_mb
        }
        
        severity = "INFO" if status == "success" else "HIGH"
        return self.log_event("BACKUP_EXECUTION", details, severity)
    
    def log_permission_change(self, file_path, old_perms, new_perms, reason):
        """Log file permission changes"""
        details = {
            "file": str(file_path),
            "old_permissions": old_perms,
            "new_permissions": new_perms,
            "reason": reason
        }
        
        return self.log_event("PERMISSION_CHANGE", details, "MEDIUM")
    
    def log_security_scan(self, scan_type, findings_count, critical_count=0):
        """Log security scan results"""
        details = {
            "scan_type": scan_type,
            "total_findings": findings_count,
            "critical_findings": critical_count
        }
        
        severity = "CRITICAL" if critical_count > 0 else "INFO"
        return self.log_event("SECURITY_SCAN", details, severity)

def main():
    """CLI interface for audit logger"""
    if len(sys.argv) < 3:
        print("Usage: security_audit_logger.py <event_type> <daemon_name> [status] [exit_code] [duration]")
        print("Example: security_audit_logger.py DAEMON_EXECUTION email_daemon success 0 45.2")
        sys.exit(1)
    
    logger = SecurityAuditLogger()
    
    event_type = sys.argv[1]
    
    if event_type == "DAEMON_EXECUTION":
        daemon_name = sys.argv[2]
        status = sys.argv[3] if len(sys.argv) > 3 else "unknown"
        exit_code = int(sys.argv[4]) if len(sys.argv) > 4 else None
        duration = float(sys.argv[5]) if len(sys.argv) > 5 else None
        
        event = logger.log_daemon_execution(daemon_name, status, exit_code, duration)
        print(f"Logged: {event['type']} - {daemon_name}")
    
    elif event_type == "SENSITIVE_FILE_ACCESS":
        file_path = sys.argv[2]
        operation = sys.argv[3] if len(sys.argv) > 3 else "read"
        
        event = logger.log_sensitive_file_access(file_path, operation)
        print(f"Logged: File access - {file_path}")
    
    elif event_type == "SECURITY_SCAN":
        scan_type = sys.argv[2]
        findings_count = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        critical_count = int(sys.argv[4]) if len(sys.argv) > 4 else 0
        
        event = logger.log_security_scan(scan_type, findings_count, critical_count)
        print(f"Logged: Security scan - {scan_type}")
    
    else:
        print(f"Unknown event type: {event_type}")
        sys.exit(1)

if __name__ == "__main__":
    main()

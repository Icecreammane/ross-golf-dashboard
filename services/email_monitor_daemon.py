#!/usr/bin/env python3
"""
Email Monitor Daemon - 24/7 Background Service
Runs continuously, checking for new support emails
"""

import sys
import time
import os
import json
from pathlib import Path
from datetime import datetime
import signal

# Add integrations to path
sys.path.insert(0, str(Path.home() / "clawd" / "integrations" / "gmail"))

from gmail_monitor import GmailMonitor
from support_responder import SupportResponder

class EmailMonitorDaemon:
    def __init__(self):
        self.running = True
        self.monitor = GmailMonitor()
        self.responder = SupportResponder()
        self.check_interval = 300  # 5 minutes
        self.respond_interval = 600  # 10 minutes
        self.last_respond_time = 0
        
        # Stats tracking
        self.stats_file = Path.home() / "clawd" / "data" / "email_monitor_stats.json"
        self.stats_file.parent.mkdir(exist_ok=True)
        
        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.shutdown)
        signal.signal(signal.SIGINT, self.shutdown)
    
    def shutdown(self, signum=None, frame=None):
        """Graceful shutdown"""
        print(f"\n🛑 Shutting down email monitor daemon...")
        self.running = False
    
    def load_stats(self):
        """Load monitoring stats"""
        if self.stats_file.exists():
            with open(self.stats_file) as f:
                return json.load(f)
        return {
            "total_scans": 0,
            "total_emails_processed": 0,
            "total_drafts_created": 0,
            "last_scan": None,
            "started_at": datetime.now().isoformat()
        }
    
    def save_stats(self, stats):
        """Save monitoring stats"""
        with open(self.stats_file, 'w') as f:
            json.dump(stats, f, indent=2)
    
    def notify_high_priority(self, tickets):
        """Send Telegram notification for high priority tickets"""
        high_priority = [t for t in tickets if t['priority'] in ['P0', 'P1']]
        
        if not high_priority:
            return
        
        try:
            from security_logger import send_telegram_alert
            
            message = f"🚨 *{len(high_priority)} HIGH PRIORITY Support Tickets*\n\n"
            for ticket in high_priority:
                message += f"• *{ticket['priority']}:* {ticket['email']['subject'][:50]}\n"
                message += f"  From: {ticket['email']['from']}\n\n"
            
            message += "Check support queue for details."
            
            send_telegram_alert(message)
            print(f"📱 Sent Telegram alert for {len(high_priority)} high-priority tickets")
        
        except Exception as e:
            print(f"⚠️  Could not send Telegram alert: {e}")
    
    def scan_and_respond(self):
        """Single scan + respond cycle"""
        stats = self.load_stats()
        
        try:
            # Scan for new emails
            print(f"\n{'='*60}")
            print(f"📧 Email Scan - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"{'='*60}")
            
            new_tickets = self.monitor.scan_inbox()
            
            stats["total_scans"] += 1
            stats["total_emails_processed"] += len(new_tickets)
            stats["last_scan"] = datetime.now().isoformat()
            
            # Notify if high priority
            if new_tickets:
                self.notify_high_priority(new_tickets)
            
            # Auto-respond if it's time
            current_time = time.time()
            if current_time - self.last_respond_time >= self.respond_interval:
                print(f"\n📝 Generating draft responses...")
                
                drafts_created = self.responder.process_queue()
                stats["total_drafts_created"] += drafts_created
                
                if drafts_created > 0:
                    print(f"✅ Created {drafts_created} draft responses")
                
                self.last_respond_time = current_time
            
            self.save_stats(stats)
            
            # Print summary
            print(f"\n📊 Session Stats:")
            print(f"   • Total scans: {stats['total_scans']}")
            print(f"   • Emails processed: {stats['total_emails_processed']}")
            print(f"   • Drafts created: {stats['total_drafts_created']}")
            print(f"   • Next scan: {self.check_interval}s")
            print(f"{'='*60}\n")
        
        except Exception as e:
            print(f"❌ Error during scan: {e}")
            import traceback
            traceback.print_exc()
    
    def run(self):
        """Main daemon loop"""
        print("="*60)
        print("📧 EMAIL MONITOR DAEMON STARTING")
        print("="*60)
        print(f"Check interval: {self.check_interval}s")
        print(f"Respond interval: {self.respond_interval}s")
        print(f"Monitoring: bigmeatyclawd@gmail.com")
        print("="*60)
        
        # Initial authentication
        try:
            print("\n🔐 Authenticating with Gmail...")
            self.monitor.authenticate()
            print("✅ Authenticated!")
        except Exception as e:
            print(f"❌ Authentication failed: {e}")
            print("\n⚠️  Run setup first: python integrations/gmail/gmail_monitor.py")
            return 1
        
        # Main loop
        while self.running:
            try:
                self.scan_and_respond()
                
                # Sleep until next check
                if self.running:
                    time.sleep(self.check_interval)
            
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f"❌ Unexpected error: {e}")
                import traceback
                traceback.print_exc()
                
                # Sleep before retrying
                if self.running:
                    print(f"⏳ Retrying in {self.check_interval}s...")
                    time.sleep(self.check_interval)
        
        print("\n✅ Email monitor daemon stopped")
        return 0


def main():
    daemon = EmailMonitorDaemon()
    return daemon.run()


if __name__ == "__main__":
    exit(main())

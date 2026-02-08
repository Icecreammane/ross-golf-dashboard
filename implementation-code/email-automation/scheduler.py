"""
Email Drip Campaign Scheduler
Runs as background task to process scheduled emails
"""

import time
import schedule
from datetime import datetime
from welcome_sequence import WelcomeSequence


class EmailScheduler:
    """Background scheduler for processing email sequences"""
    
    def __init__(self, check_interval_minutes=30):
        self.sequence = WelcomeSequence()
        self.check_interval = check_interval_minutes
        self.running = False
    
    def process_emails(self):
        """Process due emails"""
        print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking for due emails...")
        
        try:
            results = self.sequence.process_due_emails()
            
            if results['sent'] > 0 or results['failed'] > 0:
                print(f"✓ Sent: {results['sent']}, ✗ Failed: {results['failed']}")
            else:
                print("No emails due")
                
        except Exception as e:
            print(f"✗ Error processing emails: {str(e)}")
    
    def start(self):
        """Start scheduler"""
        self.running = True
        
        # Schedule job
        schedule.every(self.check_interval).minutes.do(self.process_emails)
        
        print(f"🚀 Email scheduler started")
        print(f"⏰ Checking every {self.check_interval} minutes")
        print(f"Press Ctrl+C to stop\n")
        
        # Run immediately on start
        self.process_emails()
        
        # Keep running
        try:
            while self.running:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n\n⏹️  Scheduler stopped")
            self.running = False
    
    def stop(self):
        """Stop scheduler"""
        self.running = False


# Alternative: Cron job version
def run_once():
    """Run once (for cron job)"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Running email processor...")
    
    sequence = WelcomeSequence()
    results = sequence.process_due_emails()
    
    print(f"✓ Sent: {results['sent']}, ✗ Failed: {results['failed']}")


# Main
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'once':
        # Run once and exit (for cron)
        run_once()
    else:
        # Run as continuous scheduler
        scheduler = EmailScheduler(check_interval_minutes=30)
        scheduler.start()

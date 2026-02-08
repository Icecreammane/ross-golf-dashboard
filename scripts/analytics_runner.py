#!/usr/bin/env python3
"""
Analytics Runner - Continuous analytics processing
Runs periodically to update analytics data
"""

import json
import time
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path

# Configure logging
LOG_DIR = Path.home() / "clawd" / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "analytics_runner.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("analytics_runner")

# File paths
WORKSPACE = Path.home() / "clawd"
SCRIPTS_DIR = WORKSPACE / "scripts"
DATA_DIR = WORKSPACE / "data"
STATE_FILE = DATA_DIR / "analytics-state.json"


class AnalyticsRunner:
    """Continuous analytics processing"""
    
    def __init__(self):
        self.state = self._load_state()
        logger.info("Analytics Runner initialized")
    
    def _load_state(self) -> dict:
        """Load runner state"""
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE) as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading state: {e}")
        
        return {
            "last_sync": None,
            "last_insights": None,
            "last_report": None,
            "sync_count": 0,
            "insight_count": 0,
            "report_count": 0
        }
    
    def _save_state(self):
        """Save runner state"""
        try:
            with open(STATE_FILE, 'w') as f:
                json.dump(self.state, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving state: {e}")
    
    def _run_script(self, script_name: str) -> bool:
        """Run a Python script"""
        try:
            script_path = SCRIPTS_DIR / script_name
            if not script_path.exists():
                logger.error(f"Script not found: {script_path}")
                return False
            
            logger.info(f"Running {script_name}...")
            result = subprocess.run(
                ["python3", str(script_path)],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                logger.info(f"{script_name} completed successfully")
                return True
            else:
                logger.error(f"{script_name} failed: {result.stderr}")
                return False
        
        except Exception as e:
            logger.error(f"Error running {script_name}: {e}")
            return False
    
    def should_sync(self) -> bool:
        """Check if sync is needed (every 30 minutes)"""
        if not self.state['last_sync']:
            return True
        
        last_sync = datetime.fromisoformat(self.state['last_sync'])
        return datetime.utcnow() - last_sync > timedelta(minutes=30)
    
    def should_generate_insights(self) -> bool:
        """Check if insights generation is needed (every hour)"""
        if not self.state['last_insights']:
            return True
        
        last_insights = datetime.fromisoformat(self.state['last_insights'])
        return datetime.utcnow() - last_insights > timedelta(hours=1)
    
    def should_generate_report(self) -> bool:
        """Check if weekly report is needed (Sunday @ 6pm)"""
        now = datetime.utcnow()
        
        # Check if it's Sunday
        if now.weekday() != 6:  # 6 = Sunday
            return False
        
        # Check if it's around 6pm (18:00)
        if now.hour != 18:
            return False
        
        # Check if we already generated today
        if self.state['last_report']:
            last_report = datetime.fromisoformat(self.state['last_report'])
            if last_report.date() == now.date():
                return False
        
        return True
    
    def sync_data(self):
        """Sync analytics data"""
        logger.info("=== Starting Data Sync ===")
        
        if self._run_script("analytics_tracker.py"):
            self.state['last_sync'] = datetime.utcnow().isoformat()
            self.state['sync_count'] += 1
            self._save_state()
            logger.info("Data sync completed")
        else:
            logger.error("Data sync failed")
    
    def generate_insights(self):
        """Generate insights"""
        logger.info("=== Starting Insights Generation ===")
        
        if self._run_script("analytics_insights.py"):
            self.state['last_insights'] = datetime.utcnow().isoformat()
            self.state['insight_count'] += 1
            self._save_state()
            logger.info("Insights generation completed")
        else:
            logger.error("Insights generation failed")
    
    def generate_report(self):
        """Generate weekly report"""
        logger.info("=== Starting Weekly Report Generation ===")
        
        if self._run_script("analytics_weekly_report.py"):
            self.state['last_report'] = datetime.utcnow().isoformat()
            self.state['report_count'] += 1
            self._save_state()
            logger.info("Weekly report generated")
        else:
            logger.error("Weekly report generation failed")
    
    def run_cycle(self):
        """Run one analytics cycle"""
        logger.info("--- Analytics Cycle Starting ---")
        
        # Sync data if needed
        if self.should_sync():
            self.sync_data()
        
        # Generate insights if needed
        if self.should_generate_insights():
            self.generate_insights()
        
        # Generate weekly report if needed
        if self.should_generate_report():
            self.generate_report()
        
        logger.info("--- Analytics Cycle Complete ---")
    
    def run_continuous(self, interval: int = 900):
        """
        Run continuously
        
        Args:
            interval: Check interval in seconds (default 15 minutes)
        """
        logger.info(f"Starting continuous analytics runner (check every {interval}s)")
        
        try:
            while True:
                self.run_cycle()
                time.sleep(interval)
        except KeyboardInterrupt:
            logger.info("Analytics runner stopped by user")
        except Exception as e:
            logger.error(f"Error in continuous run: {e}")


def main():
    """Main execution"""
    import sys
    
    runner = AnalyticsRunner()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--continuous":
        # Run continuous mode
        runner.run_continuous()
    else:
        # Run single cycle
        logger.info("=== Analytics Runner - Single Cycle ===")
        runner.run_cycle()
        logger.info("=== Analytics Runner Complete ===")


if __name__ == "__main__":
    main()

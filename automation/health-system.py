#!/usr/bin/env python3
"""
Integrated Health System - Combines monitoring, recovery, and alerts
This is the main daemon that should be run continuously
"""

import sys
import time
import logging
from pathlib import Path

# Add automation directory to path
WORKSPACE = Path.home() / "clawd"
sys.path.insert(0, str(WORKSPACE / "automation"))

from health_monitor import HealthMonitor
from auto_recovery import AutoRecovery
from alert import AlertSystem

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('health-system')


class HealthSystem:
    """Integrated health monitoring and recovery system"""
    
    def __init__(self, check_interval=300):
        self.check_interval = check_interval
        self.monitor = HealthMonitor()
        self.recovery = AutoRecovery()
        self.alerts = AlertSystem()
        
        logger.info("=" * 80)
        logger.info("🏥 JARVIS HEALTH SYSTEM INITIALIZED")
        logger.info("=" * 80)
        logger.info(f"Workspace: {WORKSPACE}")
        logger.info(f"Check interval: {check_interval} seconds ({check_interval/60:.1f} minutes)")
        logger.info("Components:")
        logger.info("  ✓ Health Monitor")
        logger.info("  ✓ Auto Recovery")
        logger.info("  ✓ Alert System")
        logger.info("=" * 80)
    
    def run_cycle(self):
        """Run one complete health check cycle"""
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("🔍 STARTING HEALTH CHECK CYCLE")
        logger.info("=" * 80)
        
        # Step 1: Run health checks
        health_results = self.monitor.run_checks()
        
        # Step 2: Process results and attempt recovery
        recovery_actions = self.recovery.process_health_results(health_results)
        
        # Step 3: Check if alerts are needed
        failure_counts = self.recovery.state.get('failure_counts', {})
        alerts_sent = self.alerts.check_and_alert(recovery_actions, failure_counts)
        
        # Summary
        failures = sum(1 for r in health_results.values() if r['status'] in ['down', 'error'])
        warnings = sum(1 for r in health_results.values() if r['status'] == 'warning')
        
        logger.info("=" * 80)
        logger.info("📊 CYCLE SUMMARY")
        logger.info(f"  Health: {failures} failures, {warnings} warnings")
        logger.info(f"  Recovery: {len(recovery_actions)} actions taken")
        logger.info(f"  Alerts: {len(alerts_sent)} alerts sent")
        logger.info("=" * 80)
        
        return {
            'health_results': health_results,
            'recovery_actions': recovery_actions,
            'alerts_sent': alerts_sent,
            'failures': failures,
            'warnings': warnings
        }
    
    def run(self):
        """Main daemon loop"""
        
        try:
            while True:
                cycle_result = self.run_cycle()
                
                logger.info(f"💤 Next check in {self.check_interval} seconds")
                logger.info("")
                
                time.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info("")
            logger.info("=" * 80)
            logger.info("🛑 HEALTH SYSTEM STOPPED BY USER")
            logger.info("=" * 80)
        except Exception as e:
            logger.error("")
            logger.error("=" * 80)
            logger.error(f"🔥 HEALTH SYSTEM CRASHED: {e}")
            logger.error("=" * 80)
            raise


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Jarvis Health System')
    parser.add_argument('--interval', type=int, default=300,
                       help='Check interval in seconds (default: 300)')
    parser.add_argument('--once', action='store_true',
                       help='Run one check cycle and exit')
    
    args = parser.parse_args()
    
    system = HealthSystem(check_interval=args.interval)
    
    if args.once:
        logger.info("Running single check cycle...")
        system.run_cycle()
        logger.info("Single cycle complete")
    else:
        system.run()

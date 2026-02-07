#!/usr/bin/env python3
"""
Problem Prediction Engine

Monitors system resources, API usage, logs, and predicts problems before they happen.
Auto-fixes safe issues, escalates complex ones.
"""

import json
import os
import shutil
import glob
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import subprocess

class Problem:
    def __init__(self, severity: str, category: str, description: str, 
                 prediction: str, auto_fixable: bool = False, fix_action: str = None):
        self.id = f"prob_{int(datetime.now().timestamp())}"
        self.severity = severity  # critical, warning, info
        self.category = category
        self.description = description
        self.prediction = prediction
        self.auto_fixable = auto_fixable
        self.fix_action = fix_action
        self.detected_at = datetime.now()
        self.fixed = False
        self.fix_attempted_at = None
        self.fix_result = None
    
    def to_dict(self):
        return {
            "id": self.id,
            "severity": self.severity,
            "category": self.category,
            "description": self.description,
            "prediction": self.prediction,
            "auto_fixable": self.auto_fixable,
            "fix_action": self.fix_action,
            "detected_at": self.detected_at.isoformat(),
            "fixed": self.fixed,
            "fix_attempted_at": self.fix_attempted_at.isoformat() if self.fix_attempted_at else None,
            "fix_result": self.fix_result
        }

class ProblemPredictor:
    def __init__(self, state_file="autonomous/data/problems.json"):
        self.state_file = state_file
        self.problems: List[Problem] = []
        self.metrics_history_file = "autonomous/data/metrics_history.json"
        self.load_state()
    
    def load_state(self):
        """Load problem state"""
        if os.path.exists(self.state_file):
            with open(self.state_file, 'r') as f:
                data = json.load(f)
                # Rebuild problems (simplified - just keep recent)
                self.problems = data.get("active_problems", [])
    
    def save_state(self):
        """Save problem state"""
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        data = {
            "last_updated": datetime.now().isoformat(),
            "active_problems": [p.to_dict() if isinstance(p, Problem) else p for p in self.problems],
            "total_detected": len(self.problems),
            "total_fixed": sum(1 for p in self.problems if isinstance(p, Problem) and p.fixed)
        }
        with open(self.state_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def collect_metrics(self) -> Dict:
        """Collect current system metrics"""
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "disk": self._check_disk_space(),
            "log_files": self._check_log_files(),
            "database": self._check_databases(),
            "memory": self._check_memory()
        }
        
        # Save to history
        self._save_metrics_history(metrics)
        return metrics
    
    def _check_disk_space(self) -> Dict:
        """Check disk space usage"""
        try:
            usage = shutil.disk_usage('/')
            percent_used = (usage.used / usage.total) * 100
            gb_free = usage.free / (1024**3)
            
            return {
                "percent_used": round(percent_used, 2),
                "gb_free": round(gb_free, 2),
                "gb_total": round(usage.total / (1024**3), 2),
                "status": "critical" if percent_used > 90 else "warning" if percent_used > 80 else "ok"
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _check_log_files(self) -> Dict:
        """Check log file sizes"""
        log_dirs = [
            "autonomous/logs",
            "memory",
            "/tmp"
        ]
        
        total_size = 0
        large_files = []
        
        for log_dir in log_dirs:
            if not os.path.exists(log_dir):
                continue
            
            for root, dirs, files in os.walk(log_dir):
                for file in files:
                    if file.endswith('.log') or file.endswith('.jsonl'):
                        path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(path)
                            total_size += size
                            
                            if size > 10 * 1024 * 1024:  # >10MB
                                large_files.append({
                                    "path": path,
                                    "size_mb": round(size / (1024**2), 2)
                                })
                        except:
                            pass
        
        return {
            "total_size_mb": round(total_size / (1024**2), 2),
            "large_files": large_files,
            "status": "warning" if total_size > 100 * 1024**2 else "ok"
        }
    
    def _check_databases(self) -> Dict:
        """Check database sizes and health"""
        db_files = glob.glob("**/*.db", recursive=True) + glob.glob("**/*.sqlite", recursive=True)
        
        databases = []
        total_size = 0
        
        for db_file in db_files[:20]:  # Limit to first 20
            try:
                size = os.path.getsize(db_file)
                total_size += size
                
                if size > 50 * 1024**2:  # >50MB
                    databases.append({
                        "path": db_file,
                        "size_mb": round(size / (1024**2), 2),
                        "status": "large"
                    })
            except:
                pass
        
        return {
            "total_size_mb": round(total_size / (1024**2), 2),
            "large_databases": databases,
            "count": len(db_files)
        }
    
    def _check_memory(self) -> Dict:
        """Check memory usage (macOS)"""
        try:
            result = subprocess.run(['vm_stat'], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                # Parse vm_stat output (simplified)
                return {"status": "ok", "checked": True}
        except:
            pass
        
        return {"status": "unknown", "checked": False}
    
    def _save_metrics_history(self, metrics: Dict):
        """Save metrics to history for trend analysis"""
        history = []
        
        if os.path.exists(self.metrics_history_file):
            with open(self.metrics_history_file, 'r') as f:
                history = json.load(f)
        
        history.append(metrics)
        
        # Keep last 1000 entries (about 1 week of hourly checks)
        history = history[-1000:]
        
        os.makedirs(os.path.dirname(self.metrics_history_file), exist_ok=True)
        with open(self.metrics_history_file, 'w') as f:
            json.dump(history, f, indent=2)
    
    def predict_problems(self) -> List[Problem]:
        """Analyze metrics and predict problems"""
        metrics = self.collect_metrics()
        new_problems = []
        
        # Disk space predictions
        disk = metrics.get("disk", {})
        if disk.get("percent_used", 0) > 80:
            days_until_full = self._predict_disk_full(disk)
            
            problem = Problem(
                severity="warning" if days_until_full > 7 else "critical",
                category="disk_space",
                description=f"Disk usage at {disk['percent_used']:.1f}%",
                prediction=f"Will reach capacity in ~{days_until_full} days at current rate",
                auto_fixable=True,
                fix_action="clean_logs"
            )
            new_problems.append(problem)
        
        # Log file size
        logs = metrics.get("log_files", {})
        if logs.get("total_size_mb", 0) > 100:
            problem = Problem(
                severity="warning",
                category="log_files",
                description=f"Log files total {logs['total_size_mb']:.0f}MB",
                prediction="Log files need rotation",
                auto_fixable=True,
                fix_action="rotate_logs"
            )
            new_problems.append(problem)
        
        # Large databases
        db = metrics.get("database", {})
        if db.get("large_databases"):
            for large_db in db["large_databases"]:
                problem = Problem(
                    severity="info",
                    category="database",
                    description=f"Database {large_db['path']} is {large_db['size_mb']:.0f}MB",
                    prediction="May need optimization or archival",
                    auto_fixable=False,
                    fix_action=None
                )
                new_problems.append(problem)
        
        # Add to problems list
        self.problems.extend(new_problems)
        self.save_state()
        
        return new_problems
    
    def _predict_disk_full(self, disk_metrics: Dict) -> int:
        """Predict days until disk is full"""
        # Simplified: assume 1% growth per week
        percent_remaining = 100 - disk_metrics["percent_used"]
        days_until_full = int(percent_remaining * 7)  # weeks to days
        return max(1, days_until_full)
    
    def auto_fix_problems(self) -> List[Dict]:
        """Attempt to auto-fix problems"""
        fixes = []
        
        for problem in self.problems:
            if isinstance(problem, dict):
                continue  # Skip serialized problems
            
            if problem.fixed or not problem.auto_fixable:
                continue
            
            if problem.fix_action == "clean_logs":
                result = self._clean_old_logs()
                fixes.append({
                    "problem_id": problem.id,
                    "action": "clean_logs",
                    "result": result
                })
                problem.fixed = result["success"]
                problem.fix_attempted_at = datetime.now()
                problem.fix_result = result
            
            elif problem.fix_action == "rotate_logs":
                result = self._rotate_logs()
                fixes.append({
                    "problem_id": problem.id,
                    "action": "rotate_logs",
                    "result": result
                })
                problem.fixed = result["success"]
                problem.fix_attempted_at = datetime.now()
                problem.fix_result = result
        
        self.save_state()
        self._log_fixes(fixes)
        return fixes
    
    def _clean_old_logs(self) -> Dict:
        """Clean old log files"""
        try:
            deleted_count = 0
            freed_mb = 0
            cutoff = datetime.now() - timedelta(days=30)
            
            for log_dir in ["autonomous/logs", "memory"]:
                if not os.path.exists(log_dir):
                    continue
                
                for root, dirs, files in os.walk(log_dir):
                    for file in files:
                        path = os.path.join(root, file)
                        try:
                            mtime = datetime.fromtimestamp(os.path.getmtime(path))
                            if mtime < cutoff:
                                size = os.path.getsize(path)
                                os.remove(path)
                                deleted_count += 1
                                freed_mb += size / (1024**2)
                        except:
                            pass
            
            return {
                "success": True,
                "deleted_files": deleted_count,
                "freed_mb": round(freed_mb, 2)
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _rotate_logs(self) -> Dict:
        """Rotate large log files"""
        try:
            rotated = []
            
            for root, dirs, files in os.walk("autonomous/logs"):
                for file in files:
                    if file.endswith('.log'):
                        path = os.path.join(root, file)
                        try:
                            size = os.path.getsize(path)
                            if size > 10 * 1024**2:  # >10MB
                                # Rename to .old
                                new_path = path + '.old'
                                os.rename(path, new_path)
                                rotated.append(path)
                        except:
                            pass
            
            return {
                "success": True,
                "rotated_files": rotated
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _log_fixes(self, fixes: List[Dict]):
        """Log auto-fix actions"""
        log_file = "autonomous/logs/auto_fixes.log"
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        
        with open(log_file, 'a') as f:
            for fix in fixes:
                f.write(f"[{datetime.now().isoformat()}] {json.dumps(fix)}\n")
    
    def get_active_problems(self) -> List[Problem]:
        """Get active (unfixed) problems"""
        active = []
        for p in self.problems:
            if isinstance(p, Problem) and not p.fixed:
                active.append(p)
        return active

def main():
    """CLI interface"""
    import sys
    
    predictor = ProblemPredictor()
    
    if len(sys.argv) < 2:
        print("Usage: problem_predictor.py [command]")
        print("Commands: scan, fix, metrics, list")
        return
    
    command = sys.argv[1]
    
    if command == "scan":
        print("\n🔮 Scanning for problems...\n")
        problems = predictor.predict_problems()
        
        if problems:
            print(f"Found {len(problems)} potential issues:\n")
            for p in problems:
                icon = {"critical": "🚨", "warning": "⚠️", "info": "ℹ️"}.get(p.severity, "•")
                print(f"{icon} {p.category}: {p.description}")
                print(f"   Prediction: {p.prediction}")
                if p.auto_fixable:
                    print(f"   ✅ Auto-fixable: {p.fix_action}")
                print()
        else:
            print("✅ No problems detected")
    
    elif command == "fix":
        print("\n🔧 Auto-fixing problems...\n")
        fixes = predictor.auto_fix_problems()
        
        if fixes:
            for fix in fixes:
                print(f"• {fix['action']}: ", end="")
                if fix['result']['success']:
                    print("✅ Success")
                    if 'freed_mb' in fix['result']:
                        print(f"  Freed {fix['result']['freed_mb']:.1f}MB")
                else:
                    print(f"❌ Failed: {fix['result'].get('error')}")
        else:
            print("No auto-fixable problems")
    
    elif command == "metrics":
        metrics = predictor.collect_metrics()
        print("\n📊 System Metrics:\n")
        
        disk = metrics.get("disk", {})
        print(f"Disk: {disk.get('percent_used', 0):.1f}% used ({disk.get('gb_free', 0):.1f}GB free)")
        
        logs = metrics.get("log_files", {})
        print(f"Logs: {logs.get('total_size_mb', 0):.0f}MB total")
        
        db = metrics.get("database", {})
        print(f"Databases: {db.get('count', 0)} files, {db.get('total_size_mb', 0):.0f}MB total")
    
    elif command == "list":
        active = predictor.get_active_problems()
        if active:
            print(f"\n⚠️ Active Problems ({len(active)}):\n")
            for p in active:
                print(f"• [{p.severity}] {p.category}")
                print(f"  {p.description}")
                print(f"  {p.prediction}\n")
        else:
            print("\n✅ No active problems")

if __name__ == "__main__":
    main()

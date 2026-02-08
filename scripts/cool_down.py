#!/usr/bin/env python3
"""
Cool Down System
Post-build routine to consolidate learning and transition smoothly
Like a 20-min walk after lifting, but for your brain
"""

import json
import subprocess
from datetime import datetime
from pathlib import Path

WORKSPACE = Path.home() / "clawd"
COOLDOWN_LOG = WORKSPACE / "memory" / "cooldown_log.json"

class CoolDown:
    """Guided cool down routine after building"""
    
    def __init__(self):
        self.log_file = COOLDOWN_LOG
        self.session_data = {
            "timestamp": datetime.now().isoformat(),
            "completed_steps": [],
            "notes": {}
        }
        self.load_history()
    
    def load_history(self):
        """Load cool down history"""
        if self.log_file.exists():
            with open(self.log_file) as f:
                self.history = json.load(f)
        else:
            self.history = {
                "total_cooldowns": 0,
                "streak": 0,
                "sessions": []
            }
    
    def save_history(self):
        """Save cool down history"""
        self.log_file.parent.mkdir(exist_ok=True)
        with open(self.log_file, 'w') as f:
            json.dump(self.history, f, indent=2)
    
    def print_header(self):
        """Print cool down header"""
        print("\n" + "="*70)
        print("🧘 COOL DOWN ROUTINE")
        print("="*70)
        print("Post-build mental recovery • 15-20 minutes")
        print()
    
    def step_1_document(self):
        """Step 1: Quick documentation"""
        print("═══════════════════════════════════════════════════════════════════════")
        print("📝 STEP 1: Document What You Built (5 min)")
        print("═══════════════════════════════════════════════════════════════════════")
        print()
        
        # Get build summary
        print("What did you just build? (one sentence)")
        print("Example: 'Built party demo apps with AI roast bot'")
        build_summary = input("→ ").strip()
        
        if not build_summary:
            print("⚠️  Skipped documentation")
            return False
        
        self.session_data["notes"]["build_summary"] = build_summary
        
        # Get key features
        print("\nKey features/components? (comma-separated)")
        print("Example: 'Roast Bot, Ask Anything chat, Preference Engine'")
        features = input("→ ").strip()
        
        if features:
            self.session_data["notes"]["features"] = [f.strip() for f in features.split(",")]
        
        # Update memory file
        today = datetime.now().strftime("%Y-%m-%d")
        memory_file = WORKSPACE / "memory" / f"{today}.md"
        
        timestamp = datetime.now().strftime("%I:%M%p")
        entry = f"\n## {timestamp} - Cool Down: {build_summary}\n"
        
        if features:
            entry += f"**Built:** {features}\n"
        
        if memory_file.exists():
            with open(memory_file, 'a') as f:
                f.write(entry)
            print(f"\n✅ Added to {memory_file.name}")
        
        self.session_data["completed_steps"].append("document")
        return True
    
    def step_2_commit(self):
        """Step 2: Git commit"""
        print("\n═══════════════════════════════════════════════════════════════════════")
        print("💾 STEP 2: Commit Your Work (5 min)")
        print("═══════════════════════════════════════════════════════════════════════")
        print()
        
        # Check git status
        try:
            result = subprocess.run(
                ["git", "status", "--short"],
                cwd=WORKSPACE,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            changes = result.stdout.strip()
            
            if not changes:
                print("ℹ️  No changes to commit")
                return False
            
            print("📋 Changes detected:")
            print(changes[:500])  # Show first 500 chars
            print()
            
            # Get commit message
            print("Commit message (short description):")
            print("Example: 'feat: party demo apps + preference engine'")
            commit_msg = input("→ ").strip()
            
            if not commit_msg:
                print("⚠️  Skipped commit")
                return False
            
            # Optional detailed message
            print("\nDetailed description (optional, press Enter to skip):")
            details = input("→ ").strip()
            
            # Stage all changes
            subprocess.run(
                ["git", "add", "-A"],
                cwd=WORKSPACE,
                timeout=5
            )
            
            # Commit
            commit_args = ["git", "commit", "-m", commit_msg]
            if details:
                commit_args.extend(["-m", details])
            
            subprocess.run(
                commit_args,
                cwd=WORKSPACE,
                timeout=10
            )
            
            print("\n✅ Changes committed")
            
            # Ask about push
            push = input("\nPush to GitHub? (y/n): ").strip().lower()
            
            if push == 'y':
                subprocess.run(
                    ["git", "push", "origin", "main"],
                    cwd=WORKSPACE,
                    timeout=15
                )
                print("✅ Pushed to GitHub")
            
            self.session_data["notes"]["commit_message"] = commit_msg
            self.session_data["completed_steps"].append("commit")
            return True
            
        except Exception as e:
            print(f"⚠️  Git error: {e}")
            return False
    
    def step_3_reflect(self):
        """Step 3: Reflect and plan"""
        print("\n═══════════════════════════════════════════════════════════════════════")
        print("🤔 STEP 3: Reflect & Plan Next (10 min)")
        print("═══════════════════════════════════════════════════════════════════════")
        print()
        
        # What worked
        print("What worked well? (comma-separated)")
        print("Example: 'Fast builds, clear goals, good energy'")
        worked = input("→ ").strip()
        
        if worked:
            self.session_data["notes"]["what_worked"] = [w.strip() for w in worked.split(",")]
        
        # What didn't
        print("\nWhat could be better? (comma-separated, optional)")
        print("Example: 'Took too long, unclear requirements'")
        didnt_work = input("→ ").strip()
        
        if didnt_work:
            self.session_data["notes"]["what_didnt_work"] = [w.strip() for w in didnt_work.split(",")]
        
        # Next session
        print("\nWhat's next? (1-3 tasks for next session)")
        print("Example: 'Polish fitness tracker, test party demos'")
        next_tasks = input("→ ").strip()
        
        if next_tasks:
            self.session_data["notes"]["next_session"] = [t.strip() for t in next_tasks.split(",")]
            
            # Offer to add to task queue
            add_to_queue = input("\nAdd these to TASK_QUEUE.md? (y/n): ").strip().lower()
            
            if add_to_queue == 'y':
                task_queue = WORKSPACE / "TASK_QUEUE.md"
                if task_queue.exists():
                    with open(task_queue, 'a') as f:
                        f.write(f"\n## Cool Down Tasks ({datetime.now().strftime('%Y-%m-%d')})\n")
                        for task in self.session_data["notes"]["next_session"]:
                            f.write(f"- [ ] {task}\n")
                    print("✅ Added to TASK_QUEUE.md")
        
        self.session_data["completed_steps"].append("reflect")
        return True
    
    def bonus_wins(self):
        """Bonus: Log today's wins"""
        print("\n═══════════════════════════════════════════════════════════════════════")
        print("🏆 BONUS: Log Build Win (Optional)")
        print("═══════════════════════════════════════════════════════════════════════")
        print()
        
        log_win = input("Log this as a build win? (y/n): ").strip().lower()
        
        if log_win == 'y':
            try:
                # Import win streak system
                import sys
                sys.path.append(str(WORKSPACE / "scripts"))
                from win_streak import WinStreakAmplifier
                
                ws = WinStreakAmplifier()
                
                # Get build description
                build_desc = self.session_data["notes"].get("build_summary", "Build session")
                
                # Log it
                result = ws.log_win("side_project", build_desc, "high")
                
                if result:
                    print(f"\n🔥 +{result['points_earned']} points!")
                    print(f"   🔨 Builder Mode: {result['current_streak']} day streak")
                    print(f"   🎯 Combo: {result['multiplier']:.2f}x")
                    
                    self.session_data["completed_steps"].append("log_win")
                
            except Exception as e:
                print(f"⚠️  Couldn't log win: {e}")
    
    def complete(self):
        """Complete the cool down"""
        print("\n" + "="*70)
        print("✅ COOL DOWN COMPLETE")
        print("="*70)
        print()
        
        steps_completed = len(self.session_data["completed_steps"])
        
        print(f"Completed: {steps_completed} steps")
        print(f"Time: ~{steps_completed * 5} minutes")
        print()
        
        if steps_completed >= 3:
            print("🏆 Perfect cool down! Your brain is ready to switch modes.")
        elif steps_completed >= 2:
            print("💪 Good session! Most important steps done.")
        else:
            print("⚡ Quick cool down. Consider doing full routine next time.")
        
        # Update history
        self.history["total_cooldowns"] += 1
        
        # Check streak
        if self.history["sessions"]:
            last_session = self.history["sessions"][-1]
            last_date = datetime.fromisoformat(last_session["timestamp"]).date()
            today = datetime.now().date()
            
            days_diff = (today - last_date).days
            
            if days_diff <= 1:
                self.history["streak"] += 1
            else:
                self.history["streak"] = 1
        else:
            self.history["streak"] = 1
        
        self.history["sessions"].append(self.session_data)
        
        # Keep only last 30 sessions
        if len(self.history["sessions"]) > 30:
            self.history["sessions"] = self.history["sessions"][-30:]
        
        self.save_history()
        
        print(f"\n📊 Cool Down Stats:")
        print(f"   Total: {self.history['total_cooldowns']}")
        print(f"   Streak: {self.history['streak']} days")
        print()
        
        print("🎯 Your mind is clear. Context is saved. Ready for what's next.")
        print("="*70 + "\n")
    
    def run(self):
        """Run the full cool down routine"""
        self.print_header()
        
        # Step 1: Document
        self.step_1_document()
        
        # Step 2: Commit
        self.step_2_commit()
        
        # Step 3: Reflect
        self.step_3_reflect()
        
        # Bonus: Log win
        self.bonus_wins()
        
        # Complete
        self.complete()


def quick_cooldown():
    """Quick version - just essentials"""
    print("\n🚀 QUICK COOL DOWN (5 min)\n")
    
    print("What did you build?")
    build = input("→ ").strip()
    
    if not build:
        print("Skipped.")
        return
    
    print("\nWhat's next?")
    next_task = input("→ ").strip()
    
    # Log to memory
    today = datetime.now().strftime("%Y-%m-%d")
    memory_file = WORKSPACE / "memory" / f"{today}.md"
    timestamp = datetime.now().strftime("%I:%M%p")
    
    entry = f"\n## {timestamp} - Quick Cool Down\n"
    entry += f"**Built:** {build}\n"
    if next_task:
        entry += f"**Next:** {next_task}\n"
    
    if memory_file.exists():
        with open(memory_file, 'a') as f:
            f.write(entry)
    
    print("\n✅ Logged. You're good to go!")


def main():
    """Main entry point"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "quick":
        quick_cooldown()
    else:
        cd = CoolDown()
        cd.run()


if __name__ == "__main__":
    main()

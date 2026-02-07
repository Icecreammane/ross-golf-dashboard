#!/usr/bin/env python3
"""
Decision Framework Engine
Runs decisions through 7 proven frameworks to kill overthinking.
"""

import sys
import argparse
from datetime import datetime

class DecisionFramework:
    def __init__(self, decision):
        self.decision = decision
        self.results = {}
        
    def run_all_tests(self):
        """Run all 7 framework tests interactively"""
        print(f"\n{'='*60}")
        print(f"DECISION: {self.decision}")
        print(f"{'='*60}\n")
        
        # Speed Test
        self.results['speed'] = self._speed_test()
        
        # Validation Test
        self.results['validation'] = self._validation_test()
        
        # Risk Test
        self.results['risk'] = self._risk_test()
        
        # Regret Test
        self.results['regret'] = self._regret_test()
        
        # Revenue Test
        self.results['revenue'] = self._revenue_test()
        
        # Time ROI Test
        self.results['time_roi'] = self._time_roi_test()
        
        # Hell Yeah Test
        self.results['hell_yeah'] = self._hell_yeah_test()
        
        return self.results
    
    def _speed_test(self):
        """Can results happen in < 7 days?"""
        response = input("⚡ Speed Test - Can you see results in < 7 days? (y/n): ").lower()
        reason = input("   Why/timeline: ")
        
        passed = response == 'y'
        return {
            'passed': passed,
            'reason': reason,
            'display': f"{'✅' if passed else '❌'} Speed Test: {'YES' if passed else 'NO'} ({reason})"
        }
    
    def _validation_test(self):
        """Is there proof of demand?"""
        response = input("🔍 Validation Test - Is there proof of demand? (y/n): ").lower()
        reason = input("   Evidence: ")
        
        passed = response == 'y'
        return {
            'passed': passed,
            'reason': reason,
            'display': f"{'✅' if passed else '❌'} Validation Test: {'YES' if passed else 'NO'} ({reason})"
        }
    
    def _risk_test(self):
        """What's the worst case scenario?"""
        worst_case = input("⚠️  Risk Test - What's the WORST that could happen?: ")
        severity = input("   Severity (low/medium/high): ").lower()
        
        passed = severity in ['low', 'medium']
        return {
            'passed': passed,
            'severity': severity,
            'worst_case': worst_case,
            'display': f"{'✅' if passed else '❌'} Risk Test: {severity.upper()} ({worst_case})"
        }
    
    def _regret_test(self):
        """Will you regret NOT doing it in 1 year?"""
        response = input("⏰ Regret Test - Will you regret NOT doing this in 1 year? (y/n): ").lower()
        reason = input("   Why: ")
        
        passed = response == 'y'
        return {
            'passed': passed,
            'reason': reason,
            'display': f"{'✅' if passed else '❌'} Regret Test: {'YES' if passed else 'NO'} ({reason})"
        }
    
    def _revenue_test(self):
        """Does it lead to money?"""
        response = input("💰 Revenue Test - Does this lead to money? (y/n): ").lower()
        how = input("   How: ")
        
        passed = response == 'y'
        return {
            'passed': passed,
            'how': how,
            'display': f"{'✅' if passed else '❌'} Revenue Test: {'YES' if passed else 'NO'} ({how})"
        }
    
    def _time_roi_test(self):
        """Hours required vs potential return"""
        hours = input("⏱️  Time ROI - Hours required: ")
        potential = input("   Potential return ($): ")
        
        try:
            roi = float(potential) / float(hours)
            if roi > 50:
                level = "HIGH"
                passed = True
            elif roi > 20:
                level = "MEDIUM"
                passed = True
            else:
                level = "LOW"
                passed = False
                
            return {
                'passed': passed,
                'hours': hours,
                'potential': potential,
                'roi': roi,
                'display': f"{'✅' if passed else '⚠️'} Time ROI: {level} ({hours}hrs for ${potential} = ${roi:.0f}/hr)"
            }
        except:
            return {
                'passed': False,
                'display': "⚠️  Time ROI: UNKNOWN (invalid input)"
            }
    
    def _hell_yeah_test(self):
        """Does it excite you? Hell Yeah or No"""
        response = input("🔥 Hell Yeah Test - Does this excite you? (hell yeah/no): ").lower()
        
        passed = 'yeah' in response or response == 'y'
        return {
            'passed': passed,
            'display': f"{'✅' if passed else '❌'} Hell Yeah: {'YES' if passed else 'NO'}"
        }
    
    def generate_report(self):
        """Generate final report with recommendation"""
        print(f"\n{'='*60}")
        print("RESULTS:")
        print(f"{'='*60}\n")
        
        # Print all results
        for test in self.results.values():
            print(test['display'])
        
        # Calculate score
        score = sum(1 for r in self.results.values() if r['passed'])
        total = len(self.results)
        
        print(f"\nSCORE: {score}/{total} {'✅' if score >= 5 else '⚠️' if score >= 3 else '❌'}")
        
        # Generate recommendation
        if score >= 6:
            recommendation = "LAUNCH IT. Stop overthinking."
        elif score >= 4:
            recommendation = "PROMISING. Fix the gaps and ship."
        else:
            recommendation = "PAUSE. Too many red flags. Find something better."
        
        print(f"\n{'='*60}")
        print(f"RECOMMENDATION: {recommendation}")
        print(f"{'='*60}\n")
        
        return score, recommendation


def main():
    parser = argparse.ArgumentParser(
        description='Decision Framework Engine - Kill overthinking with proven frameworks'
    )
    parser.add_argument('decision', nargs='*', help='The decision to evaluate')
    parser.add_argument('--quick', action='store_true', help='Skip interactive mode, just show framework')
    
    args = parser.parse_args()
    
    if args.decision:
        decision = ' '.join(args.decision)
    else:
        decision = input("What decision are you evaluating? ")
    
    if not decision:
        print("Error: No decision provided")
        sys.exit(1)
    
    if args.quick:
        print(f"\nDecision: {decision}")
        print("\nFrameworks to consider:")
        print("1. ⚡ Speed Test - Can results happen in < 7 days?")
        print("2. 🔍 Validation Test - Is there proof of demand?")
        print("3. ⚠️  Risk Test - What's worst case scenario?")
        print("4. ⏰ Regret Test - Will you regret NOT doing it in 1 year?")
        print("5. 💰 Revenue Test - Does it lead to money?")
        print("6. ⏱️  Time ROI - Hours required vs potential return")
        print("7. 🔥 Hell Yeah or No - Does it excite you?")
        print("\nRun without --quick for interactive evaluation.\n")
        return
    
    framework = DecisionFramework(decision)
    framework.run_all_tests()
    framework.generate_report()


if __name__ == '__main__':
    main()

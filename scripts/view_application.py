#!/usr/bin/env python3
"""View job applications in readable format"""
import json
import sys
from pathlib import Path

def view_application(app_path):
    """Display application in readable format"""
    with open(app_path, 'r') as f:
        app = json.load(f)
    
    print("\n" + "="*80)
    print(f"📋 JOB APPLICATION - {app['job']['company']}")
    print("="*80 + "\n")
    
    print(f"Position: {app['job']['title']}")
    print(f"Company: {app['job']['company']}")
    print(f"Location: {app['job']['location']}")
    print(f"Match Score: {app['job']['match_score']}/10")
    print(f"Status: {app['status'].upper()}")
    print(f"URL: {app['job']['url']}")
    
    print("\n" + "-"*80)
    print("COVER LETTER:")
    print("-"*80 + "\n")
    print(app['cover_letter'])
    
    print("\n" + "-"*80)
    print("FORM DATA:")
    print("-"*80 + "\n")
    for key, value in app['form_data'].items():
        print(f"{key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        # List available applications
        apps_dir = Path.home() / "clawd" / "applications"
        apps = sorted(apps_dir.glob("*.json"))
        print("\n📁 Available Applications:\n")
        for i, app in enumerate(apps, 1):
            print(f"{i}. {app.stem}")
        print("\nUsage: python3 view_application.py <number or filename>")
        sys.exit(0)
    
    arg = sys.argv[1]
    apps_dir = Path.home() / "clawd" / "applications"
    
    # If number, list and select
    if arg.isdigit():
        apps = sorted(apps_dir.glob("*.json"))
        idx = int(arg) - 1
        if 0 <= idx < len(apps):
            view_application(apps[idx])
        else:
            print(f"Invalid number. Choose 1-{len(apps)}")
    else:
        # If filename
        app_path = apps_dir / f"{arg}.json" if not arg.endswith('.json') else apps_dir / arg
        if app_path.exists():
            view_application(app_path)
        else:
            print(f"Application not found: {app_path}")

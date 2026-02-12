#!/usr/bin/env python3
"""List all Clawdbot skills"""
import os
from pathlib import Path

skills_dir = Path.home() / ".npm-global/lib/node_modules/clawdbot/skills"

if not skills_dir.exists():
    print(f"Skills directory not found: {skills_dir}")
    exit(1)

skills = []
for item in sorted(skills_dir.iterdir()):
    if item.is_dir() and not item.name.startswith('.'):
        skill_md = item / "SKILL.md"
        status = "✓" if skill_md.exists() else "✗"
        skills.append((item.name, status))

print(f"=== Clawdbot Skills ({len(skills)} total) ===\n")
for name, status in skills:
    print(f"{status} {name}")

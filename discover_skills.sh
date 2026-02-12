#!/bin/bash
# Discover all Clawdbot skills

SKILLS_DIR=~/.npm-global/lib/node_modules/clawdbot/skills

echo "=== Clawdbot Skills Inventory ==="
echo ""

for skill_dir in "$SKILLS_DIR"/*; do
  if [ -d "$skill_dir" ]; then
    skill_name=$(basename "$skill_dir")
    skill_md="$skill_dir/SKILL.md"
    
    if [ -f "$skill_md" ]; then
      echo "✓ $skill_name (has SKILL.md)"
    else
      echo "✗ $skill_name (missing SKILL.md)"
    fi
  fi
done

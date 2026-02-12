#!/usr/bin/env python3
"""
Discover all Clawdbot skills and extract their metadata
"""
import os
import yaml
from pathlib import Path
import json

def extract_frontmatter(content):
    """Extract YAML frontmatter from skill file"""
    if not content.startswith('---'):
        return None
    
    lines = content.split('\n')
    end_idx = None
    for i, line in enumerate(lines[1:], 1):
        if line.strip() == '---':
            end_idx = i
            break
    
    if end_idx is None:
        return None
    
    frontmatter_text = '\n'.join(lines[1:end_idx])
    try:
        return yaml.safe_load(frontmatter_text)
    except:
        return None

def main():
    skills_dir = Path.home() / ".npm-global/lib/node_modules/clawdbot/skills"
    
    if not skills_dir.exists():
        print(f"❌ Skills directory not found: {skills_dir}")
        return
    
    skills = []
    
    for item in sorted(skills_dir.iterdir()):
        if not item.is_dir() or item.name.startswith('.'):
            continue
        
        skill_md = item / "SKILL.md"
        if not skill_md.exists():
            skills.append({
                'name': item.name,
                'has_skill_md': False,
                'description': None
            })
            continue
        
        # Read and parse SKILL.md
        content = skill_md.read_text()
        frontmatter = extract_frontmatter(content)
        
        skill_info = {
            'name': item.name,
            'has_skill_md': True,
            'description': frontmatter.get('description', '???') if frontmatter else '???',
            'path': str(item)
        }
        
        skills.append(skill_info)
    
    # Print results
    print(f"{'='*80}")
    print(f"Clawdbot Skills Discovery Report")
    print(f"{'='*80}\n")
    print(f"Total skills found: {len(skills)}\n")
    
    print(f"{'Name':<25} {'Has SKILL.md':<15} {'Description Length'}")
    print(f"{'-'*80}")
    
    for skill in skills:
        status = "✓" if skill['has_skill_md'] else "✗"
        desc_len = len(skill['description']) if skill['description'] and skill['description'] != '???' else 0
        print(f"{skill['name']:<25} {status:<15} {desc_len} chars")
    
    print(f"\n{'='*80}\n")
    
    # Save to JSON for processing
    output_path = Path.home() / "clawd/outputs/skills-upgrade/skills_inventory.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(skills, f, indent=2)
    
    print(f"✓ Detailed inventory saved to: {output_path}\n")
    
    # Print detailed descriptions
    print(f"{'='*80}")
    print(f"Current Descriptions (for audit)")
    print(f"{'='*80}\n")
    
    for skill in skills:
        if skill['has_skill_md'] and skill['description'] and skill['description'] != '???':
            print(f"### {skill['name']}")
            print(f"{skill['description']}\n")
            print(f"{'-'*80}\n")

if __name__ == '__main__':
    main()

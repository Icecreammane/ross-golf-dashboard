# Clawdbot Skills Best Practices

Based on OpenAI's "Shell + Skills + Compaction" guidance for agent routing accuracy.

**Last Updated:** 2026-02-11  
**Version:** 1.0

---

## Philosophy: Skills as Routing Targets

Skills aren't just documentation—they're **decision boundaries** for the routing system. Every word in the description helps the agent decide "should I use this skill or not?"

**Core principle:** The description must answer two questions:
1. What concrete scenarios trigger this skill?
2. What scenarios look similar but should NOT trigger it?

---

## Anatomy of an Optimized Skill

### 1. **Frontmatter Description** (THE ROUTING ENGINE)

The `description` field is the ONLY thing the router sees before triggering. It must contain:

#### **Format Template:**

```yaml
---
name: skill-name
description: "[What it does]. Use when: (1) [specific scenario], (2) [specific scenario], (3) [specific scenario]. Don't use when: (1) [negative example], (2) [negative example]. Outputs: [artifact type and location]. Tools required: [exec|web_fetch|browser|etc]."
---
```

#### **Quality Checklist:**
- ✅ 4-8 sentences with clear decision boundaries
- ✅ At least 3 "Use when:" scenarios (specific, concrete)
- ✅ At least 3 "Don't use when:" scenarios (prevent misfires)
- ✅ Explicit output description (format + location)
- ✅ Required tools listed
- ✅ Zero marketing fluff ("powerful", "comprehensive", etc.)
- ✅ Pure routing logic

#### **Example (GOOD):**

```yaml
description: "Manage GitHub repositories, PRs, issues, and workflows using the gh CLI. Use when: (1) checking PR status or CI failures, (2) creating/listing/merging PRs, (3) viewing workflow runs or logs, (4) querying GitHub API for repo data. Don't use when: (1) cloning repos (use git directly), (2) making local commits (use git), (3) searching code content (use ripgrep + git). Outputs: Terminal output (JSON when --json flag used). Tools required: exec."
```

#### **Example (BAD):**

```yaml
description: "Interact with GitHub using the gh CLI."
```

❌ Too vague  
❌ No use cases  
❌ No negative examples  
❌ No output specification  
❌ No tool requirements

---

### 2. **Negative Examples Section** (CRITICAL FOR ACCURACY)

After the main skill body, add a dedicated section:

```markdown
## When NOT to Use This Skill

This skill should NOT trigger for:

### Common Misfires
- **"Clone this GitHub repo"** → Use `git clone` directly (no gh CLI needed)
- **"Commit these changes"** → Use `git commit` (gh is for GitHub API, not local git)
- **"Search for code in the repo"** → Use ripgrep or git grep (gh search is for GitHub-wide searches)

### Similar-Sounding Alternatives
- **Local git operations** → Use git directly
- **Code search within repo** → Use ripgrep/grep
- **Repository browsing** → Use browser tool if UI-based exploration needed

### Edge Cases
- **Private repos without gh auth** → Will fail; check `gh auth status` first
- **Very old GitHub Enterprise** → May not support all gh CLI features
```

**Why this matters:**  
The router learns from mistakes. Negative examples create "anti-patterns" that prevent the skill from triggering incorrectly.

---

### 3. **Embedded Templates** (REDUCE REPEATED GENERATION)

If your skill produces structured output, embed the template INSIDE the skill:

#### **When to Embed Templates:**
- ✅ Skill produces consistent format (JSON, Markdown, CSV, etc.)
- ✅ Format has specific required fields
- ✅ Template is referenced multiple times
- ✅ Output quality matters (reports, documentation, etc.)

#### **Template Format:**

```markdown
## Output Template

When this skill generates [artifact type], use this structure:

\`\`\`markdown
# [Report Title]

## Summary
- **Status:** [status]
- **Last Updated:** [timestamp]
- **Author:** [author]

## Details
[content here]

## Next Steps
1. [action item]
2. [action item]
\`\`\`

**Required fields:**
- Title (H1)
- Summary section with Status, Last Updated, Author
- Details section with actual content
- Next Steps with numbered list

**Output location:** `~/clawd/outputs/[skill-name]/[timestamp]-[description].md`
```

#### **Example from openai-image-gen:**

```markdown
## Output Structure

All generated images are saved to:
- **Directory:** `~/Projects/tmp/openai-image-gen-[timestamp]/` (or `./tmp/` if ~/Projects/tmp doesn't exist)
- **Files:**
  - `*.png` or `*.webp` (generated images)
  - `prompts.json` (prompt → filename mapping)
  - `index.html` (thumbnail gallery for quick review)

**Gallery Template:**
\`\`\`html
<!DOCTYPE html>
<html>
<head><title>Generated Images</title></head>
<body>
  <h1>Generated Images</h1>
  <div class="gallery">
    <!-- Auto-generated thumbnails -->
  </div>
</body>
</html>
\`\`\`
```

---

### 4. **Artifact Output Documentation** (STANDARDIZATION)

Every skill that writes files must document:

#### **Standard Location Convention:**

```
~/clawd/outputs/[skill-name]/[artifact-files]
```

#### **Documentation Template:**

```markdown
## Output Location

This skill writes artifacts to:
- **Primary output:** `~/clawd/outputs/[skill-name]/[timestamp]-[name].[ext]`
- **Format:** [JSON|Markdown|CSV|etc.]
- **Naming convention:** `YYYY-MM-DD-HHMMSS-[description].[ext]`

**Example:**
\`\`\`
~/clawd/outputs/github-reports/2026-02-11-142030-pr-status.md
\`\`\`

**Structure:**
- One file per execution (unless batch mode)
- Timestamp-prefixed for automatic sorting
- Self-contained (no external dependencies)
```

#### **Why Standardization Matters:**
1. **Predictable file locations** → Easier to find/reference outputs
2. **Consistent naming** → Automatic chronological sorting
3. **Clear ownership** → `outputs/[skill-name]/` = this skill created it
4. **No conflicts** → Timestamp + description = unique filenames

---

## Anti-Patterns (AVOID THESE)

### ❌ Vague Descriptions

**Bad:**
```yaml
description: "Work with Notion"
```

**Good:**
```yaml
description: "Create and manage Notion pages, databases, and blocks via the Notion API. Use when: (1) creating new pages in databases, (2) querying database contents, (3) updating page properties, (4) adding blocks to pages. Don't use when: (1) browsing Notion UI (use browser tool), (2) reading pages not shared with integration, (3) setting database view filters (UI-only feature). Outputs: API responses (JSON). Tools required: exec."
```

---

### ❌ No Negative Examples

Negative examples prevent the most common source of routing errors: skills that sound similar but serve different purposes.

**Example:** `git` vs `gh` vs `github` skills
- `git` → Local version control
- `gh` → GitHub API (PRs, issues, workflows)
- `github` (browser-based) → UI automation for GitHub.com

Without negative examples, the router confuses them.

---

### ❌ Templates in System Prompts Instead of Skills

**Problem:** Templates in system prompts:
- Load into EVERY conversation (token waste)
- Hard to update (requires system prompt changes)
- Not skill-specific (loaded even when skill doesn't trigger)

**Solution:** Move templates into skills, loaded only when skill triggers.

---

### ❌ Generic Output Locations

**Bad:**
```bash
open /tmp/output.md
```

**Good:**
```bash
mkdir -p ~/clawd/outputs/github-reports
OUTPUT_PATH=~/clawd/outputs/github-reports/$(date +%Y-%m-%d-%H%M%S)-pr-status.md
echo "Results..." > "$OUTPUT_PATH"
echo "Report saved to: $OUTPUT_PATH"
```

---

## Skill Priority Matrix

### High-Use Skills (Check Daily for Improvements)
- github
- himalaya (email)
- weather
- things-mac

### Revenue-Critical Skills (Quality > Speed)
- notion
- openai-image-gen
- obsidian

### Infrastructure Skills (Affects Other Skills)
- skill-creator
- peekaboo

### Specialized Skills (Optimize After Core Stable)
- sonoscli
- camsnap
- video-frames
- apple-notes

---

## Upgrade Checklist

For each skill, verify:

1. **Description Audit**
   - [ ] Contains 3+ "Use when:" scenarios
   - [ ] Contains 3+ "Don't use when:" scenarios
   - [ ] Documents output format/location
   - [ ] Lists required tools
   - [ ] 4-8 sentences, clear boundaries
   - [ ] Zero marketing language

2. **Negative Examples**
   - [ ] "When NOT to Use This Skill" section exists
   - [ ] Lists common misfires
   - [ ] Lists similar-sounding alternatives
   - [ ] Documents edge cases

3. **Templates**
   - [ ] Embedded if skill produces structured output
   - [ ] Includes worked examples
   - [ ] Documents required fields
   - [ ] Shows expected format

4. **Artifact Outputs**
   - [ ] Documents output location(s)
   - [ ] Uses `~/clawd/outputs/[skill-name]/` convention
   - [ ] Specifies file format (JSON/MD/CSV/etc.)
   - [ ] Shows naming convention

5. **Tools Required**
   - [ ] Lists all tools (exec, browser, web_fetch, etc.)
   - [ ] Documents any external binaries needed
   - [ ] Notes OS restrictions if applicable

---

## Testing Routing Accuracy

After upgrading skills, test with ambiguous queries:

### Example Test Cases:

**Query:** "Show me recent changes to the codebase"  
**Should trigger:** `git` (local), NOT `github` (API)

**Query:** "What's the status of PR #42?"  
**Should trigger:** `github` (API), NOT `git` (local)

**Query:** "Add a task to my todo list"  
**Should trigger:** `things-mac`, NOT `apple-notes` (different purpose)

**Query:** "Take a note about this meeting"  
**Should trigger:** `apple-notes`, NOT `things-mac` (notes vs tasks)

---

## Metrics for Success

Track these before/after upgrade:

1. **Routing Accuracy:** % of queries that trigger correct skill
2. **False Positives:** Skills that trigger when they shouldn't
3. **False Negatives:** Skills that should trigger but don't
4. **Average Description Length:** Should be 4-8 sentences
5. **Output Standardization:** % of skills using `~/clawd/outputs/`

**Target Metrics:**
- Routing accuracy: >95%
- False positives: <5%
- False negatives: <5%
- Description length: 4-8 sentences (50-150 words)
- Output standardization: 100% for file-writing skills

---

## Version History

- **v1.0** (2026-02-11): Initial best practices based on OpenAI guidance

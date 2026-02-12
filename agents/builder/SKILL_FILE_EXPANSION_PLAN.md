# Arnold's Skill File Expansion Plan

**Inspired by:** Larry's 500+ line TikTok skill file  
**Goal:** Make Arnold as capable as Larry is at his domain

---

## What Larry Has That We Don't

### 1. Obsessively Specific Rules
**Larry's approach:** "Image sizes: 1024x1536 portrait. Always. Font size: 6.5% of canvas height. Text positioned 15% from top. Line length max: 28 characters."

**Our current state:** "Build working code fast."

**What Arnold needs:**
- Code formatting standards (PEP 8 for Python, ESLint rules for JS)
- File structure templates (Flask app structure, React component structure)
- Error handling patterns (try/except blocks, status codes)
- Security checklist (no hardcoded keys, input validation, SQL injection prevention)
- Testing requirements (what MUST work before calling it done)

### 2. Failure Logs
**Larry's approach:** Every mistake documented. "Early on I was generating 1536x1024 (landscape) instead of 1024x1536 (portrait). Fixed: Always portrait for TikTok."

**Our current state:** No systematic failure tracking.

**What Arnold needs:**
```markdown
## Failure Log

### 2026-02-15: Stripe Integration
**What went wrong:** Used wrong API version, checkout session failed  
**Fix:** Always use Stripe API version 2023-10-16 or newer  
**Rule added:** Check Stripe docs for current API version before integration

### 2026-02-16: Database Migration
**What went wrong:** SQLite locked during concurrent writes  
**Fix:** Add connection timeout, use WAL mode  
**Rule added:** SQLite config for multi-user apps in skill file
```

### 3. Success Patterns
**Larry's approach:** "Hooks that work: [Another person] + [conflict] → showed them AI → they changed. This formula clears 100K views minimum."

**Our current state:** No documented success patterns.

**What Arnold needs:**
```markdown
## Success Patterns

### Pattern: Flask + Stripe MVP (Used 3x, all successful)
1. Create checkout session endpoint
2. Success/cancel routes
3. Webhook handler (optional for MVP)
4. Test with card 4242...
**Time:** ~45 minutes
**Always works:** Yes

### Pattern: Plaid OAuth Flow (Used 1x, successful)
1. Create link token
2. Exchange public token for access token
3. Store access token (encrypted)
4. Fetch account data
**Time:** ~60 minutes
**Gotchas:** Sandbox vs Development mode confusion
```

### 4. Specific Prompts for Common Tasks
**Larry's approach:** Exact prompt templates for image generation with locked architecture.

**Our current state:** "Use local model for code generation."

**What Arnold needs:**
```markdown
## Code Generation Prompts

### Flask API Endpoint
"Write a Flask API endpoint for [purpose]. 
- Use Blueprint structure
- Include error handling (try/except)
- Return JSON with proper status codes
- Add docstring
- Follow PEP 8
Example: /api/create_checkout for Stripe"

### React Component
"Write a React component for [purpose].
- Functional component with hooks
- PropTypes defined
- Error boundary if needed
- Tailwind for styling
Example: AccountsList component"
```

---

## Expansion Plan

### Phase 1: Document Current Knowledge (This Week)
Add to Arnold's skill file:
- [ ] Tech stack decision tree (when Flask vs Next.js)
- [ ] File structure templates (Flask, React, Next.js)
- [ ] Common integrations (Stripe, Plaid, OAuth)
- [ ] Error handling patterns
- [ ] Security checklist
- [ ] Testing requirements

### Phase 2: Add Failure Logs (After First Weekend)
After Saturday/Sunday builds:
- [ ] Document what went wrong
- [ ] Document how we fixed it
- [ ] Turn fixes into rules
- [ ] Add to skill file so it never happens again

### Phase 3: Build Success Pattern Library (February-March)
After each successful build:
- [ ] Document the pattern
- [ ] Note time taken
- [ ] Capture gotchas
- [ ] Create reusable template

### Phase 4: Prompt Engineering (March)
- [ ] Test local model code generation quality
- [ ] Document which prompts produce best code
- [ ] Create prompt library for common tasks
- [ ] Measure: Does code work first try?

---

## Target State (End of March)

**Arnold's skill file should contain:**

### 1. Technical Specifications (~100 lines)
- Code formatting standards
- File structure templates
- Naming conventions
- Comment requirements

### 2. Integration Guides (~150 lines)
- Stripe (checkout, webhooks, subscriptions)
- Plaid (OAuth, account data, transactions)
- OAuth flows (Google, GitHub, etc.)
- Email (Resend, SendGrid)
- Database (SQLite, Postgres)

### 3. Success Patterns (~100 lines)
- Proven build patterns
- Time estimates
- Reusable code snippets
- Architecture decisions

### 4. Failure Logs (~50 lines)
- Mistakes made
- How they were fixed
- Rules to prevent recurrence

### 5. Quality Checklists (~50 lines)
- Security checklist
- Testing checklist
- Deployment checklist
- Code review checklist

### 6. Prompt Library (~50 lines)
- Best prompts for common tasks
- Examples of good/bad prompts
- Model-specific tips

**Total: ~500 lines** (like Larry's TikTok file)

---

## Implementation

**This weekend:** Arnold builds with current skill file, logs everything that goes wrong or takes longer than expected.

**Next week:** Jarvis and Arnold collaborate to expand skill file based on weekend learnings.

**March:** Continuous refinement as Arnold builds more products.

---

**Key Insight from Article:**

> "Write them like you're training a new team member who's incredibly capable but has zero context. Be obsessively specific."

Arnold is incredibly capable (Qwen 32B / Claude Sonnet).  
Arnold has zero context (wakes up fresh every session).  
Solution: Obsessively specific skill files.

---

**Created:** February 12, 2026  
**Target completion:** End of March 2026  
**Owner:** Jarvis + Arnold

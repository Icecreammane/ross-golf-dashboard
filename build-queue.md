# Build Queue

**Last Updated:** 2026-02-05 21:00 CST

Priority-ordered list of what to build next. Agents pull from this queue for autonomous work.

---

## 🔥 HIGH PRIORITY (Do First)

### ⏳ IN PROGRESS
*Currently being built*

- **Build System** (build-system-agent, started 21:00)
  - Components: build-queue.md, progress.html, generate-build-report.py, decision framework
  - ETA: 23:00 tonight
  - Agent: build-system-agent (session: b97579dc-b567-4a98-9b28-4882043b5d89)

### 📋 TODO
*Ready to start*

*(None yet - add items below)*

---

## 📊 MEDIUM PRIORITY (Do Soon)

*(Add items as they come up)*

---

## 💡 LOW PRIORITY (Nice to Have)

*(Future ideas and experiments)*

---

## ✅ COMPLETED

*(Finished builds move here)*

---

## 📝 Template: Add New Build Item

Copy this template when adding new items:

```markdown
- **[Project Name]** (label: [agent-label])
  - **Goal:** [What we're building and why]
  - **Deliverables:**
    - [ ] [Specific output 1]
    - [ ] [Specific output 2]
    - [ ] [Specific output 3]
  - **Success Criteria:** [How we know it's done]
  - **Blockers:** [Dependencies or unknowns]
  - **Estimated Time:** [hours or days]
  - **Priority:** [high/medium/low]
  - **Notes:** [Context, links, requirements]
```

---

## Queue Management Rules

### When to Add Items
- Ross explicitly requests something
- Natural next step from completed work
- Proactive improvement that's clearly beneficial
- Automation opportunity identified

### When to Start Building
Main agent spawns builder when:
- High priority item with clear requirements
- No blockers or dependencies
- Time available (evening/overnight builds)
- Ross has approved or it's autonomous work

### Status Flow
TODO → IN PROGRESS → COMPLETED

### Priority Guidelines
- **HIGH:** Direct Ross requests, core infrastructure, revenue-impacting
- **MEDIUM:** Improvements, experiments Ross mentioned interest in
- **LOW:** Nice-to-haves, optimizations, exploratory work

---

## Integration with Subagent System

**Main agent checks this queue during heartbeats** to:
1. See what's ready to build
2. Decide if time to spawn builder
3. Update progress on active builds
4. Move completed items

**Builder agents:**
- Pull tasks from IN PROGRESS
- Update status every 2 hours
- Mark COMPLETED when done
- Log deliverables and links

---

*This queue is the single source of truth for what's being built.*

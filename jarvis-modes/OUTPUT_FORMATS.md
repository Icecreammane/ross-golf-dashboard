# OUTPUT FORMATS

## Purpose

Consistent output formats make it easy for Ross to:
- Quickly scan reports
- Understand priorities
- Approve/reject actions
- Track progress over time

Every mode has standardized templates below.

---

## 📊 SALES MODE REPORT

**Frequency:** Daily (12pm after session complete)
**File:** `memory/sales-reports/sales-report-[DATE].md`

### Template

```markdown
📊 SALES MODE REPORT - [Date]

⏱️ TIME SPENT: [X hours] (8am-12pm)

---

## 🎯 LEADS FOUND: [Total number]

### HOT LEADS ([count])
1. u/[username] - "[complaint/need in their words]"
   - Link: [Reddit link]
   - Pain point: [Specific frustration]
   - Budget signal: [Quote showing willingness to pay]
   - Score: [🔥🔥🔥 out of 🔥🔥🔥]
   - Draft message: [See below]

[Repeat for each hot lead]

### WARM LEADS ([count])
1. u/[username] - "[complaint/need]"
   - Link: [Reddit link]
   - Pain: [Brief]
   - Score: [🌡️🌡️ out of 🔥🔥🔥]
   - Draft: [See below]

### COLD LEADS ([count])
[Brief list, less detail]

---

## 🔥 WARM LEAD FOLLOW-UPS: [count]

1. u/[username] (Day [X] follow-up)
   - Previous interaction: [What happened]
   - Today's action: [What I did]
   - Status: [Waiting/Converted/Cold]
   - Next action: [When/what to do next]

---

## 🔍 COMPETITOR INTEL:

- [Competitor]: [What changed / what I learned]
- [Competitor]: [Notable move or insight]
- [Competitor]: [User sentiment / threat level]

---

## 💡 RECOMMENDED ACTIONS:

1. ✅ APPROVE: [Action requiring approval]
2. ⏸️ CONSIDER: [Strategic suggestion]
3. 🚨 URGENT: [Time-sensitive opportunity/threat]
4. 💡 IDEA: [Low-priority idea to consider]

---

## 📝 DRAFTED MESSAGES: [count]

### MESSAGE #1: u/[username]
**Subject:** "[Subject line]"

[Full drafted message text]

---

[Repeat for each message]

---

## 📊 CRM UPDATE:

- New leads added: [count]
- Leads moved to warm: [count]
- Leads moved to cold: [count]
- Total pipeline: [total] ([hot] hot, [warm] warm, [cold] cold)

**Conversion Funnel:**
- Outreach sent (all time): [count]
- Replies: [count] ([%] reply rate)
- Trials: [count] ([%] of replies)
- Paid: [count] ([%] of trials)

**Pipeline Value:**
- Hot leads: [count] × $5/mo = $[value]/mo potential
- Warm leads: [count] × $5/mo × 20% = $[value]/mo potential
- **Total potential MRR: $[value]/mo**

---

END SALES MODE REPORT
```

---

## 🛡️ SUPPORT MODE CHECK

**Frequency:** 4 times daily (10am, 2pm, 6pm, 10pm)
**File:** `memory/support-logs/support-check-[DATE]-[TIME].md`

### Template

```markdown
🛡️ SUPPORT MODE CHECK - [Time]

⏱️ LAST CHECK: [X hours ago] ([previous time])
📧 INBOX: [count] new messages, [count] pending responses

---

## 🚨 HIGH PRIORITY: [count]

📌 Customer #[ID] - [Name] ([email])
- Issue: [Brief description]
- Type: [Billing/Bug/Question]/[P0/P1]
- Details: [More context]
- Impact: [Who/what affected]
- Drafted response: ✅ [see below] / ⏸️ [needs approval]
- Escalation: YES/NO - [Reason if yes]

[Repeat for each high priority]

---

## ⚠️ MEDIUM PRIORITY: [count]

📌 [Customer/User] - [email]
- Issue: [Brief]
- Type: [Category]/[Priority]
- Action taken: [What I did]
- Escalation: NO (unless exception)

[Repeat for each medium priority]

---

## ✅ LOW PRIORITY: [count]

[Brief list or "None"]

---

## 🐛 BUGS DETECTED:

**NEW:**
- [Bug description] ([count] reports, [priority])
  - Priority: [P0/P1/P2/P3]
  - Logged: ✅
  - Assigned: [DEV MODE backlog / Escalated to Ross]

**ONGOING:**
- [Bug description] ([status])
  - Priority: [P#]
  - Status: [Ross investigating / In progress / Waiting]
  - Follow-up: [When to check again]

---

## 📊 PATTERNS NOTICED:

- [X users asked/reported]: "[Common question/issue]"
  - Recommendation: [What to do about it]

[Repeat for each pattern]

---

## 💬 RESPONSE DRAFTS: [count]

### DRAFT #1: [Customer] ([Issue type]) - [NEEDS APPROVAL / READY TO SEND]

**Subject:** [Subject line]

[Full drafted response]

---

[Repeat for each draft]

---

## 🚨 ESCALATION NEEDED:

1. [Customer/Issue] - [Why escalated]
   - Action needed: [What Ross should do]
   - Urgency: [High/Medium/Low]
   - Deadline: [When to handle by]

---

## 📈 RESPONSE TIME METRICS:

- Average response time: [X hours] [✅/⚠️] (target: <4 hours)
- Open tickets: [count] ([new], [pending])
- Resolved today: [count]
- Customer satisfaction: [%] (based on replies)

---

## 📋 FOLLOW-UP REMINDERS:

- Customer #[ID]: [What to follow up on] ([when])
- [Action]: [Description] ([when])

---

## ✅ ACTIONS TAKEN:

- Drafted [count] responses
- Logged [count] bugs
- Updated [count] customer records
- Created [count] follow-up reminders
- Escalated [count] issues

---

## 🎯 RECOMMENDED ACTIONS:

1. ✅ APPROVE: [Action]
2. 🚨 URGENT: [Time-sensitive issue]
3. 💡 CONSIDER: [Product/UX improvement]
4. 🔧 DEV: [Bug to fix]

---

NEXT SUPPORT CHECK: [Time] ([X hours])

END SUPPORT MODE CHECK
```

---

## 🔍 RESEARCH MODE REPORT

**Frequency:** Daily (8pm after session complete)
**File:** `memory/research-reports/research-report-[DATE].md`

### Template

```markdown
🔍 RESEARCH MODE REPORT - [Date]

⏱️ TIME SPENT: [X hours] (6pm-8pm)

---

## 📊 COMPETITOR MOVES

### [Competitor Name]
**[Change/Announcement]:**
- What: [Description]
- When: [Date]
- Why: [Their reasoning or our hypothesis]
- User reaction: [Sentiment]
- Threat level: [HIGH/MEDIUM/LOW]
- Opportunity: [How we can capitalize]

[Repeat for each competitor]

---

## 📈 TRENDING TOPICS

### "[Topic]" ([Platform])
- Where: [r/subreddit or Twitter or ...]
- Volume: [Mentions/posts/engagement]
- Sentiment: [What people are saying]
- Opportunity: [How we can leverage]
- Action: [What to create/do]

[Repeat for each trend]

---

## 💡 OPPORTUNITIES

### [Opportunity #1]: [Name] ([POTENTIAL: HIGH/MEDIUM/LOW])

**What:**
[Description of opportunity]

**Why It Makes Sense:**
- [Reason 1]
- [Reason 2]
- [Reason 3]

**Potential Revenue:**
[Calculation/estimate]

**Next Steps:**
1. [Action 1]
2. [Action 2]
3. [Action 3]

**Effort:** [Low/Medium/High]
**Timeline:** [When we could execute]

[Repeat for each opportunity]

---

## ⚠️ THREATS

### [Threat Description]
- Severity: [HIGH/MEDIUM/LOW]
- Why it matters: [Impact on us]
- Our gap: [What we're missing]
- Timeline: [When to address]
- Action: [What to do about it]

[Repeat for each threat]

---

## 🎯 RECOMMENDED ACTIONS

### Immediate (This Week):
1. ✅ [Action with clear next step]
2. ✅ [Action with clear next step]

### Short-term (This Month):
1. 🔧 [Action]
2. 📊 [Action]

### Long-term (3-6 Months):
1. 🔍 [Action]
2. 🤝 [Action]

---

## 📝 CONTENT IDEAS

### "[Content Title]" ([Format])
**Why It's Timely:**
[Relevance/timing]

**Outline:**
[Brief structure or key points]

**Distribution:**
[Where to post/share]

**Expected Results:**
- [Metric 1]
- [Metric 2]
- [Metric 3]

**Effort:** [Hours to create]

[Repeat for top 3 content ideas]

---

## 📚 TECH MONITORING

### [Tool/API/Framework]
- What: [Description]
- Relevance: [How it applies to us]
- Cost: [Price if applicable]
- Action: [Integrate / Monitor / Skip]

[Repeat as needed]

---

## 💰 PIPELINE IMPACT ESTIMATE

**If we execute on top opportunities:**

[Opportunity 1]: $[revenue]/mo
[Opportunity 2]: $[revenue]/mo
[Opportunity 3]: $[revenue]/mo

**Total Potential: $[sum]/mo additional MRR**

Current MRR: $[current]
Potential MRR: $[current + opportunities]

---

## 📅 NEXT RESEARCH PRIORITIES

**Tomorrow's Session:**
1. [Priority 1]
2. [Priority 2]

**This Week:**
- [Topic to research]
- [Competitor to monitor]

---

END RESEARCH MODE REPORT
```

---

## 🔧 DEV MODE REPORT

**Frequency:** After significant work (bug fixes, deployments)
**File:** `memory/dev-logs/dev-report-[DATE]-[TIME].md`

### Template

```markdown
🔧 DEV MODE REPORT - [Date/Time]

⏱️ SESSION DURATION: [X hours] ([start]-[end])

---

## 🐛 BUGS FIXED: [count]

### Bug #[ID]: [Title] [P0/P1/P2/P3]
**Issue:**
[User-facing description]

**Root Cause:**
[Technical explanation]

**Fix:**
[What was changed]

**Results:**
[Improvement metrics if applicable]

**Testing:**
- [Test case 1]: ✅/❌
- [Test case 2]: ✅/❌

**Deployed:** ✅ [Build #] at [time] / ⏸️ [Pending approval]
**Monitoring:** [Status after 30 min]

[Repeat for each bug]

---

## ⚡ PERFORMANCE IMPROVEMENTS

**[Area Improved]:**
- Before: [Metric]
- After: [Metric]
- Improvement: [% or absolute]

**Changes:**
- [Change 1]
- [Change 2]

**Impact:**
[User-facing benefit]

[Repeat if multiple improvements]

---

## 🚀 DEPLOYED TO PRODUCTION

**Build #[number]**
- Time: [timestamp]
- Deployment: [Platform] ([method])
- Duration: [X minutes]
- Status: ✅ Successful / ❌ Failed / ⏸️ Rolled back

**Changes:**
- [Change 1]
- [Change 2]
- [Change 3]

**Post-Deploy Monitoring:**
- Error rate: [%] ([Change])
- Response time: [ms] ([Change])
- User reports: [Feedback]

**Changelog:** [Updated at URL / Pending]

---

## 🔍 PENDING BUGS

### [Bug Title] [P#]
**Status:** [Investigating / Blocked / Scheduled]
**Issue:** [Brief description]
**Root Cause:** [Known / Unknown]
**Next Steps:** [What needs to happen]
**Blocking?** [Yes/No]

[Repeat for each pending]

---

## 🧹 TECH DEBT

**High Priority:**
- [Debt item] ([Impact])

**Medium Priority:**
- [Debt item]

**Low Priority:**
- [Debt item]

**Recommended:** [Allocation suggestion]

---

## 📊 SYSTEM HEALTH

**Uptime:** [%] (last 30 days)
**Error Rate:** [%] ([Trend])
**Response Time:** [ms average] ([Status vs target])
**Database:** [% capacity] ([Status])
**Build Time:** [minutes] ([Status])

**Alerts:** [Count] ([Details if any])

---

## 🔒 SECURITY STATUS

**Vulnerabilities:** [count] high/critical
**SSL Certificate:** Valid until [date] ([days remaining])
**Dependencies:** [count] updates available ([urgency])
**Secrets:** All in environment variables ✅/⚠️

**Action Needed:** [If any security issues]

---

## 🎯 RECOMMENDED ACTIONS

**Immediate:**
1. ✅ DONE: [Completed action]

**This Week:**
1. 🔧 [Action]
2. 📊 [Action]

**This Month:**
1. 🏗️ [Action]
2. ⚡ [Action]

---

## 📝 NOTES

**What Went Well:**
- [Win 1]
- [Win 2]

**What Could Improve:**
- [Learning 1]
- [Learning 2]

**Lessons Learned:**
- [Lesson 1]
- [Lesson 2]

---

END DEV MODE REPORT
```

---

## 📊 ACCOUNTABILITY SCORECARD (Daily)

**Frequency:** Daily (9pm)
**File:** `memory/accountability-daily/scorecard-[DATE].md`

### Template

```markdown
📊 ACCOUNTABILITY SCORECARD - [Date]

---

## TODAY'S COMMITMENT

**What you committed to:**
"[Exact commitment text]"

**Status:** ✅ DONE ([time] - [X min early/late]) / ❌ MISSED / ⏸️ PARTIAL

**Tasks Completed:**
✅ [Task 1]
✅ [Task 2]
❌ [Task not done] ([reason])

**Actual time spent:** [X hours] (estimated: [Y hours])

---

## TIME BREAKDOWN

**Total work time:** [X hours]
- Revenue-generating: [X hours] ([%]) [✅/⚠️] (target: >50%)
  - [Activity]: [hours]
  - [Activity]: [hours]
- Building/optimizing: [X hours] ([%])
  - [Activity]: [hours]
- Administrative: [X hours] ([%])
  - [Activity]: [hours]

**Procrastination detected:** [X hours]
- [Activity]: [hours] ([when])
- [Activity]: [hours] ([when])

**Focus sessions:**
- Session 1: [start]-[end] ([duration]) [✅ Deep work / ⚠️ Fragmented]
- Session 2: [start]-[end] ([duration])
- Session 3: [start]-[end] ([duration])

**Peak productivity:** [timeframe] ([what got done])

---

## STREAK TRACKING

**Current streak:** [X days] [✅✅✅ emoji chain]
- Day 1: [Commitment] ✅
- Day 2: [Commitment] ✅
- Day 3: [Commitment] ✅

**This week:** [X/7] commitments hit ([%])
**This month:** [X/Y] commitments hit ([%])

**Longest streak:** [X days] ([date range])
**Goal:** [Beat X-day streak / Maintain / Build to X]

---

## PATTERN ANALYSIS

**What's Working:**
- [Observation 1]
- [Observation 2]

**What's Not:**
- [Observation 1]
- [Observation 2]

**Recommendation:**
[Specific, actionable suggestion]

---

## PROCRASTINATION FORENSICS

**Trigger detected:** [Activity] at [time]
- What happened: [Context]
- Duration: [X minutes]
- Impact: [How it affected work]

**Pattern:** [If recurring pattern noticed]

**Suggestion:** [How to prevent next time]

---

## WINS TODAY 🎉

1. [Win 1]
2. [Win 2]
3. [Win 3]

**Biggest win:** [Most significant achievement]

---

## TOMORROW'S COMMITMENT

**I recommend:**
"[Exact commitment text]"

**Why this:**
- [Reason 1]
- [Reason 2]
- [Reason 3]

**Success criteria:**
- [Specific outcome 1]
- [Specific outcome 2]

**Deadline:** [Time tomorrow]

**Do you commit?** Reply YES or suggest different commitment.

---

## WEEKLY SNAPSHOT (Last 7 days)

**Commitments:**
- Hit: [X/7] ([%])
- Missed: [X/7]
- Streak: [X days]

**Time allocation:**
- Revenue work: [%] (target: >50%)
- Building: [%]
- Admin: [%]

**Trend:** [Improving / Stable / Declining] ([observation])

**Momentum:** [Building / Maintaining / Losing] ([reason])

---

## REFLECTION PROMPT

Before bed, ask yourself:

1. Did I keep my commitment today? ([YES/NO])
2. Am I proud of what I shipped? ([YES/NO])
3. What would I do differently tomorrow? ([Answer])
4. Do I feel momentum? ([YES/NO] - [why])

Sleep well. Tomorrow we go again. 🚀

---

END ACCOUNTABILITY SCORECARD
```

---

## 📊 ACCOUNTABILITY WEEKLY REPORT (Sunday)

**Frequency:** Weekly (Sunday 9pm)
**File:** `memory/accountability-weekly/weekly-report-[DATE].md`

### Template

```markdown
📊 WEEKLY ACCOUNTABILITY REPORT - Week of [Date]

## EXECUTION SUMMARY

**Commitments:**
- Made: [count]
- Hit: [count] ([%])
- Missed: [count]
- Current streak: [X days]

**Missed commitments breakdown:**
- [Day]: [Reason]
- [Day]: [Reason]

**Time allocation:**
- Revenue work: [hours] ([%]) [✅/⚠️] (target: >50%)
- Building: [hours] ([%])
- Admin: [hours] ([%])

**Total work hours:** [hours] ([sustainable pace: 35-45 hours])

---

## PRODUCTIVITY PATTERNS

**Peak performance times:**
- Best work: [Days], [Times]
- Worst work: [Days], [Times]

**Focus quality:**
- Deep work sessions: [count] (avg [duration] each)
- Fragmented sessions: [count] (avg [duration] each)
- Ratio: [%] deep work [✅/⚠️] (target: >60%)

**Procrastination patterns:**
- Total procrastination: [hours] ([%] of work time)
- Primary trigger: [Activity/Context]
- Secondary trigger: [Activity/Context]

**Recommendation:** [Specific advice]

---

## MOMENTUM ANALYSIS

**Streaks:**
- Longest: [X days] ([when])
- Total days executed: [X/7] ([%])

**When you hit commitments:**
- Next day confidence: [High/Medium/Low]
- Next day productivity: [+X%]
- Next day focus: [Stronger/Same/Weaker]

**When you miss commitments:**
- Next day confidence: [Lower]
- Next day productivity: [-X%]
- Next day focus: [Weaker]

**Key insight:** [Pattern observation]

---

## WORK TYPE ANALYSIS

**Revenue-generating work:** [hours]
- [Activity]: [hours]
- [Activity]: [hours]

**Building work:** [hours]
- [Activity]: [hours]
- [Activity]: [hours]

**Admin work:** [hours]
- [Activity]: [hours]
- [Activity]: [hours]

**Ideal allocation:**
- Revenue: 50% (currently [%])
- Building: 35% (currently [%])
- Admin: 15% (currently [%])

**Recommendation:** [Adjustment suggestion]

---

## COMMITMENT QUALITY

**Good commitments (you hit):**
- "[Example]" ([why it worked])
- "[Example]" ([why it worked])

**Bad commitments (you struggled):**
- "[Example]" ([why it didn't work])
- "[Example]" ([why it didn't work])

**Pattern:** [Observation]

**Recommendation:** [How to improve commitment quality]

---

## ENERGY MANAGEMENT

**High energy days:** [Days listed]
- [Common factor 1]
- [Common factor 2]
- Result: [Productivity outcome]

**Low energy days:** [Days listed]
- [Common factor 1]
- [Common factor 2]
- Result: [Productivity outcome]

**Insight:** [Energy management observation]

**Recommendation:** [How to optimize energy]

---

## NEXT WEEK STRATEGY

**Focus:** [Primary goal]

**Commitment strategy:**
- [Approach 1]
- [Approach 2]

**Allocation targets:**
- Revenue work: [hours] ([%])
- Building: [hours] ([%])
- Admin: [hours] ([%])
- Total: [hours]

**Energy strategy:**
- [Priority 1]
- [Priority 2]

**Procrastination prevention:**
- [Tactic 1]
- [Tactic 2]

---

## WEEKLY WINS 🎉

1. [Win 1]
2. [Win 2]
3. [Win 3]
4. [Win 4]
5. [Win 5]

**Biggest win:** [Most significant]

---

## CHALLENGE FOR NEXT WEEK

**Goal:** [Specific challenge]

**What it takes:**
- [Requirement 1]
- [Requirement 2]
- [Requirement 3]

**Prize for success:**
- [Benefit 1]
- [Benefit 2]

[Encouraging message]

---

END WEEKLY REPORT
```

---

## 📋 Usage Guidelines

### For Each Mode:

**SALES MODE:**
- Use template daily at 12pm
- Include ALL sections (even if some are "0" or "None")
- Draft messages in full (don't abbreviate)

**SUPPORT MODE:**
- Use template at each check (4x daily)
- Skip sections with no content (mark as "None")
- Always include next check time

**RESEARCH MODE:**
- Use template daily at 8pm
- Focus on actionable insights
- Always include recommended actions

**DEV MODE:**
- Use template after deployments or bug fixes
- Include technical details (Ross wants to know)
- Always update system health

**ACCOUNTABILITY MODE:**
- Daily scorecard at 9pm (never skip)
- Weekly report on Sundays
- Be factual, not judgmental

---

## 🎨 Formatting Rules

**Markdown:**
- Use headers (##, ###) for structure
- Use emoji for visual scanning
- Use checkboxes (✅❌⏸️) for status
- Use horizontal rules (---) to separate sections

**Tone:**
- Professional but friendly
- Data-driven
- Action-oriented
- No fluff

**Length:**
- Daily reports: 300-600 words
- Weekly reports: 800-1200 words
- Be comprehensive but concise

---

These templates are production-ready. Use them consistently. 📊

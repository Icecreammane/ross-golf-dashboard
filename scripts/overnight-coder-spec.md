# Overnight Coder - Specification

**Status:** Design phase (build starts Feb 5, first output Feb 10)

## CORE CONCEPT

Every night at 23:00 CST:
1. Parse daily conversations for problems/opportunities
2. Identify if there's a tool-building opportunity
3. Use Codex CLI to generate minimal viable code
4. Test locally
5. Commit to GitHub
6. Morning report: "Built [app], here's what it does, try it"

## APP CATEGORIES (What Gets Built)

### FANTASY FOOTBALL
- **Injury Report Analyzer** - Scrape latest injuries, impact analysis
- **Waiver Wire Rank Calculator** - Position-by-position value rankings
- **Trade Analyzer** - Input trade, AI scores both sides
- **Playoff Bracket Predictor** - Based on team matchups
- **Player Consistency Score** - Weekly performance variance metric

### GOLF
- **Round Analyzer** - Parse scorecard, find weak holes/clubs/patterns
- **Score Trend Predictor** - Based on last 10 rounds, predict next round
- **Course Difficulty Ranker** - Track performance by course
- **Handicap Trend** - Track progression toward 80
- **Putting Pattern Detector** - Flag trends in 3-putts, GIRs

### AI/LEARNING
- **Concept Explainer** - Input topic, get 3-min explanation (ELI5)
- **Research Summarizer** - Parse article/paper, extract key insights
- **Pattern Detector** - Analyze text/data, find recurring themes
- **Learning Path Generator** - Build step-by-step learning plan
- **Mistake Logger** - Track errors, suggest prevents

### FITNESS
- **Workout Logger** - Quick CLI to log sets/reps/weight
- **PR Tracker** - Track personal records by lift
- **Progress Analyzer** - Monthly strength progression
- **Body Composition Calculator** - Track muscle vs fat trends
- **Recovery Advisor** - Suggest rest days based on frequency

### REVENUE/OPPORTUNITIES
- **Opportunity Dashboard** - Display flagged opportunities (from X Trends)
- **Content Scheduler** - Plan posts across platforms
- **Revenue Calculator** - Input idea, estimate potential
- **Competitor Monitor** - Track competitor activities
- **Email Drip Campaign Builder** - Auto-generate sequences

## BUILD PROCESS

### 1. Opportunity Detection
Look for:
- "I should build [x]" in conversation
- "It would be useful if [x]" → suggests tool-building
- Repeated manual tasks → opportunity for automation
- Gaps in existing tools

### 2. App Design
Define:
- **Problem it solves:** 1 sentence
- **Input:** What data/info user provides
- **Output:** What the app produces
- **Time to build:** Est. build time
- **Complexity:** Simple/Medium/Complex

### 3. Code Generation
- Use `codex` or `claude` to generate code
- Template-driven (start from existing if possible)
- Minimal viable product (not perfect, but works)
- 80/20 rule (80% value, 20% effort)

### 4. Testing
- Run locally
- Test with sample data
- Verify output makes sense
- No bugs/crashes

### 5. Deployment
- Commit to GitHub repo: `github.com/[username]/ross-tools/[app-name]`
- Branch: `feature/overnight-[app-name]`
- Commit message: "Overnight build: [App] - [brief description]"
- Push to main

### 6. Morning Report
```
🤖 OVERNIGHT CODER REPORT
Built: [App Name]
Purpose: [1 sentence]
How to use: [2-3 lines]
Try it: github.com/ross-tools/[app-name]
Time spent: [X min]
```

## OUTPUT TYPES

**Preferred (fastest to build):**
- Python scripts (3-5 min scripts, automation)
- JavaScript dashboards (HTML + JS, visualizations)
- Node CLI tools (interactive, quick)

**Also viable:**
- Telegram bots (interactive, easy to test)
- Google Sheets scripts (GAS)
- Data analysis notebooks

**Avoid (too complex for overnight):**
- Full web apps
- Database-backed systems
- Deployment to production

## SAFETY CONSTRAINTS

✅ **Safe to build:**
- Analysis tools
- Data processing
- Calculations
- Visualizations
- Personal dashboards
- CLI tools

❌ **Do NOT build:**
- Anything that sends external messages
- Financial transactions
- Any public-facing systems
- Anything that modifies external data

## GITHUB WORKFLOW

**Repo:** `github.com/rosscast/ross-tools` (or similar)

Structure:
```
ross-tools/
├── fantasy-football/
│   ├── waiver-analyzer.py
│   ├── injury-report.py
│   └── README.md
├── golf/
│   ├── round-analyzer.py
│   └── score-predictor.py
├── ai-tools/
│   ├── concept-explainer.py
│   └── research-summarizer.py
└── README.md (master index of all tools)
```

Each app gets:
- Main code file
- README with usage
- Requirements.txt (if needed)
- Sample data/example

## EXAMPLE BUILD (FANTASY FOOTBALL)

**Opportunity:** "I need a quick way to check if a waiver wire player is worth adding"

**App:** Waiver Wire Rank Calculator

**Input:** 
```
position: WR
week: 10
league_size: 10
scoring: PPR
```

**Output:**
```
Player: [Name]
Rank at position: 47/500 (WR)
ADP: Round 8
Trend: ↑ (up 12 spots this week)
Recommendation: ⚠️ WAIT (overvalued this week)
```

**Build time:** 15 min  
**Complexity:** Medium

## SUCCESS METRICS

- **Build frequency:** 5-7 apps/week
- **Usefulness:** Each app saves >5 min/week
- **Code quality:** No crashes, works as expected
- **User adoption:** You use it, or it gets archived

## CADENCE

- **Build time:** 23:00 - 23:45 CST nightly
- **Test time:** 23:45 - 23:55 CST
- **Commit time:** 23:55 - 00:00 CST
- **Report time:** 8:15 AM (next morning)

If no opportunity detected that night: Skip build, rest time.

## FIRST BUILD (FEB 10)

**Target:** Simple golf analyzer
- Input: Recent scorecard
- Output: Weak spots + trends
- Time: 20 min
- Complexity: Low

This will validate the whole system before scaling to more builds.

---

Ready to implement. Need:
- GitHub repo access
- Codex/Claude API access
- Permission to commit daily

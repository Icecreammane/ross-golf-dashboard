# PROPOSALS - Jarvis Build Queue

**Last Updated:** 2026-02-01 21:47 CST

This file tracks autonomous build proposals. Jarvis generates ideas, Ross approves/rejects, Jarvis builds.

---

## [Golf Club Spec Matcher & Comparison Tool]

**Status:** PENDING_APPROVAL  
**Created:** 2026-02-01 21:47 CST  
**Effort Estimate:** 4-6 hours  
**Category:** utility | golf

### What
Web-based tool where you input your swing data (speed, tempo, ball flight) and it recommends irons + shafts from the market, ranked by fit score. Includes price comparisons and "similar clubs" matching.

### Why Ross Would Want This
You literally just got a $4,700 Club Champion quote and asked "what clubs are similar to these?" This tool would:
- Let you compare T150s vs P790s vs Srixon objectively with YOUR swing data
- Find cheaper alternatives that fit your specs
- Reusable for future club purchases (wedges, driver, etc.)
- Potential side business angle: white-label for golf shops or monetize as subscription

### Implementation Plan
- Build Flask web app with simple form (swing speed, tempo, ball flight preference, budget)
- Database of popular irons + specs (pulled from manufacturer sites)
- Matching algorithm: assign fit scores based on swing profile
- Output: ranked list with prices, "why this fits," and alternatives
- Deploy to clawd/golf-club-matcher with simple HTML/CSS UI
- Data sources: MyGolfSpy tests, manufacturer specs, Reddit reviews (web scraping)

### Approval Needed
- [ ] APPROVED - Build it
- [ ] REJECTED - Don't build (reason: ___)
- [ ] MODIFY - Build with changes: ___

---

## [DraftKings Week 17 Playoff Correlation Analyzer]

**Status:** PENDING_APPROVAL  
**Created:** 2026-02-01 21:47 CST  
**Effort Estimate:** 5-7 hours  
**Category:** side-business | fantasy

### What
Script that pulls DraftKings playoff best ball data and identifies:
- QB + pass-catcher stacks with highest Week 17 correlation
- Defense + opposing offense negative correlation plays
- Contrarian low-ownership plays
- Outputs a draft guide with player tiers and stack recommendations

### Why Ross Would Want This
You mentioned wanting to win fantasy championships. Best ball is a growing DFS market. This tool:
- Gives you edge in playoff best ball drafts (correlation > raw projections)
- Could be packaged as a weekly newsletter/guide (revenue stream)
- Differentiates from generic DFS advice (you're targeting week 17 specifically)
- Aligns with your data-driven approach

### Implementation Plan
- Pull DFS pricing + ownership from DraftKings API (or scrape)
- Correlate historical Week 17 performance by team/stack type
- Calculate correlation scores for QB+WR, QB+TE, RB+DST stacks
- Generate draft guide PDF with tiers, stacks, and contrarian plays
- CLI tool that updates weekly, outputs markdown + PDF
- Optional: Flask dashboard for interactive exploration

### Approval Needed
- [ ] APPROVED - Build it
- [ ] REJECTED - Don't build (reason: ___)
- [ ] MODIFY - Build with changes: ___

---

## [Fitness Tracker Auto-Logger (Gym Session via Photo)]

**Status:** PENDING_APPROVAL  
**Created:** 2026-02-01 21:47 CST  
**Effort Estimate:** 3-4 hours  
**Category:** automation | fitness

### What
Take a photo of your workout journal/app screen → AI extracts exercises, sets, reps, weight → logs to SQLite DB → generates weekly progress charts.

### Why Ross Would Want This
You're into weightlifting and structured routines. This tool:
- Eliminates manual data entry (just snap a photo post-workout)
- Tracks progressive overload automatically
- Visualizes strength gains over time
- No subscription (unlike most fitness apps)
- Could be monetized as a simple app for lifters who hate logging

### Implementation Plan
- Use image tool (vision model) to OCR workout notes
- Parse exercises/sets/reps/weight into structured data
- SQLite database for workout history
- Flask dashboard to view progress charts (volume, PRs, trends)
- Telegram integration: send photo → get confirmation → auto-logged
- Optional: export to CSV for deeper analysis

### Approval Needed
- [ ] APPROVED - Build it
- [ ] REJECTED - Don't build (reason: ___)
- [ ] MODIFY - Build with changes: ___

---

## Backlog (Ideas Not Yet Proposed)
- Revenue dashboard aggregating all side projects
- LocalPrep competitor price monitor
- Pet food digestibility calculator (work tool)
- Automated golf score tracker with handicap trending
- Fantasy football draft kit with custom rankings

---

## Completed Builds
*None yet - awaiting first approval*

---

## Rejected Proposals
*None yet*


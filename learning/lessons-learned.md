# Lessons Learned - Jarvis Learning Log

**Purpose:** Track corrections Ross makes so I don't repeat mistakes.

---

## Food Portion Estimation (2026-02-02)

**Lesson:** I consistently underestimate Ross's portion sizes.

**Examples:**
- Ground beef in bowl: I guessed 8 oz → Ross corrected to 1 lb (16 oz)
- Cottage cheese: I guessed small scoop → Ross corrected to 8 oz (half container)

**What to do differently:**
- When Ross sends food photo, ask portion size before estimating
- Default to larger portions for his meals (he's bulking/cutting at 225 lbs)
- Use actual container labels when provided
- Store portion preferences in frequent-meals.json

**Rule:** If uncertain about portion size → ASK before logging

---

## Meal Logging Workflow (2026-02-02)

**Lesson:** Creating duplicate entries when correcting macros causes tracker confusion.

**What happened:**
- Dinner logged 4 times with different macro values
- Tracker summed all entries → wrong totals
- Had to manually clean database

**What to do differently:**
- When correcting a meal, UPDATE the existing entry (don't create new)
- Or: Build UI with Edit/Delete buttons so Ross fixes himself
- Track entry IDs to enable updates

**Rule:** One meal = one entry. Update, don't duplicate.

---

## Context Awareness (2026-02-02)

**Lesson:** I don't know Ross's schedule or location context.

**Missing context examples:**
- Don't know when he's at work vs home
- Don't know when he's at the gym (could offer workout logging)
- Don't know his calendar (upcoming meetings, events)

**What to do differently:**
- Get calendar API access
- Use time-of-day patterns (8am-6pm = likely at work)
- Ask before interrupting during likely work hours

**Rule:** Context matters. Time/location awareness = better assistance.

---

## Communication Style (2026-02-02)

**Lesson:** Ross prefers direct, concise communication. No fluff.

**What he likes:**
- Quick confirmations ("✅ Logged!")
- Direct answers
- Proactive building (just do it, explain later)
- Surprising him with completed work

**What to avoid:**
- Long explanations before acting
- Asking permission for things I should just do
- Over-apologizing
- Corporate/formal language

**Rule:** Be Jarvis. Be direct. Build first, explain after.

---

## Macro Knowledge (2026-02-02)

**Lesson:** Ross follows specific macro philosophy.

**His approach:**
- Protein: 0.75 × bodyweight
- Fat: 0.25 × bodyweight
- Carbs: Fill remaining calories
- At 225 lbs: 169p / 243c / 56f

**Rule:** Use this formula. Update targets as weight changes.

---

## Food Preferences (2026-02-02)

**Frequent meals logged:**
1. Work lunch: Chicken + Brussels + Mashed Potatoes (500 cal)
   - Note: MASHED POTATOES, not cauliflower
2. Beef Bowl: 1 lb ground beef + 8 oz cottage cheese + hash browns (1,040 cal)
   - Publix 93% lean beef
   - Post-workout staple

**Rule:** Recognize these meals instantly. Don't ask for details every time.

---

## How I Use This File:

Before responding to Ross about:
- Food logging → Check "Food Portion Estimation" + "Meal Logging Workflow"
- Communication → Check "Communication Style"
- Corrections → Log new lesson here

**This file grows smarter over time.**

---

*Last Updated: 2026-02-02 20:41 CST*

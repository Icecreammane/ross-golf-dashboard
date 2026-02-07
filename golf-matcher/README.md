# Golf Club Spec Matcher

## What It Does

Takes your swing data and matches you with the best irons on the market. Scores each club 0-100% based on how well it fits YOUR specs.

## How to Use

### On iPhone (Recommended)
1. Open this link in Safari: `file:///Users/clawdbot/clawd/golf-matcher/index.html`
2. Bookmark it for quick access
3. Fill out the form:
   - **Swing Speed:** Your 7-iron clubhead speed (use launch monitor if you have data)
   - **Handicap:** Your current or estimated handicap
   - **Ball Flight:** Typical trajectory (low/mid/high)
   - **Common Miss:** Which direction you miss most
   - **Priority:** What matters most (distance/accuracy/feel/forgiveness)
   - **Budget:** How much you want to spend

4. Tap "Find My Perfect Clubs"
5. Get ranked results with fit scores and prices

### On Desktop
Just open `index.html` in any browser.

## Club Database

Currently includes 9 popular irons:
- Titleist T150, T200, T100
- TaylorMade P790
- Srixon ZXi5
- Ping i230
- Mizuno JPX 925 Forged
- Callaway Apex Ai200
- PXG 0311 P GEN7

## Scoring Algorithm

Fit score (0-100%) based on:
- **30%** Handicap range fit
- **25%** Swing speed range fit
- **25%** Priority match (feel/distance/forgiveness/accuracy)
- **20%** Budget fit

## Example Use Cases

### "Should I buy the Club Champion T150 quote or go with P790s?"
Input your specs → see which scores higher → compare prices

### "What's the best club for a 12 handicap with 85mph swing speed?"
Fill out form → get personalized ranking

### "I want maximum feel under $2,000"
Set priority to "Feel", budget to $2,000 → see top matches

## Limitations

- **Static database:** Doesn't include every iron on market (easily expandable)
- **Simplified algorithm:** Real fitting includes lie angle, shaft, etc.
- **No shaft recommendations:** Club head only (could be added)

## Future Enhancements

- Add shaft recommendations
- Include wedges and drivers
- Pull live pricing from retailers
- Save/compare multiple builds
- White-label for golf shops (revenue opportunity)

## Technical Notes

- Pure HTML/CSS/JavaScript (no backend needed)
- Works offline
- Mobile-first responsive design
- Client-side matching (instant results)

---

*Built by Jarvis | 2026-02-01*

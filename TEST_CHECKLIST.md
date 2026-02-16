# ✅ Fitness Dashboard - Final Testing Checklist

**Server running at:** http://localhost:3000/  
**Status:** Production-ready, waiting for your testing ✨

---

## 📱 Quick Visual Check (5 minutes)

### On Load:
1. [ ] **Beautiful neon aesthetic** - Black background, cyan/lime gradients
2. [ ] **Fire emoji visible** - Shows current streak (13 days)
3. [ ] **4 macro cards displayed** - Calories, Protein, Carbs, Fat (all showing 0/goals)
4. [ ] **14-day chart visible** - Shows empty graph with target line
5. [ ] **Voice FAB (🎤)** - Bottom right, neon gradient circle
6. [ ] **Add meal button (➕)** - Bottom left, gray circle

### Animations:
1. [ ] **Smooth scrolling** - No janky animations
2. [ ] **Button press effects** - Scale down when tapped
3. [ ] **No console errors** - Open dev tools and check

---

## 🎯 Core Features Test (10 minutes)

### 1. Add a Meal (Manual)
1. [ ] Tap **➕** button (bottom left)
2. [ ] Modal opens with form
3. [ ] Fill in: "Chicken & Rice" / 450 cal / 45g protein / 50g carbs / 10g fat
4. [ ] Tap **Add Meal**
5. [ ] **Expected**: Confetti animation 🎉, meal appears in history, macro cards update

### 2. Voice Logging (Optional - needs mic)
1. [ ] **Hold** 🎤 button
2. [ ] Modal appears with "Listening..."
3. [ ] Say: "I just ate a banana"
4. [ ] **Release** button
5. [ ] **Expected**: Processes voice → logs meal → confetti

### 3. View 14-Day Chart
1. [ ] Scroll to "14-Day Progress" section
2. [ ] Chart shows **0 calories** for past days (empty data)
3. [ ] **Green dashed line** shows calorie target (2200)
4. [ ] After adding meal, **today's bar** should show calories

### 4. Goal Calculator
1. [ ] Tap **⚙️** (top right)
2. [ ] Settings panel appears
3. [ ] Tap **"Goal Calculator"**
4. [ ] Fill in your stats (age, height, weight, goal weight, activity level)
5. [ ] Tap **Calculate**
6. [ ] **Expected**: Shows BMR, TDEE, recommended calories, timeline
7. [ ] Tap **Apply These Goals**
8. [ ] **Expected**: Goals update throughout app

### 5. Edit Goals Manually
1. [ ] In settings, tap **"Calorie Goal"**
2. [ ] Change value to `2000`
3. [ ] Tap **Save**
4. [ ] **Expected**: All macro cards update to new target

### 6. Progress Photos
1. [ ] Scroll to "Your Progress" section
2. [ ] Tap **"Start Photo"** card
3. [ ] Select a photo from your device
4. [ ] **Expected**: Photo uploads, appears in card
5. [ ] Weight modal should appear (optional to fill)

### 7. Meal History & Delete
1. [ ] After adding meals, scroll to "Recent Meals"
2. [ ] Each meal shows: Time, description, macros
3. [ ] Tap **🗑️** on a meal
4. [ ] Confirm deletion
5. [ ] **Expected**: Meal disappears, macros recalculate

### 8. Export Data
1. [ ] Open settings
2. [ ] Tap **"Export Data"**
3. [ ] **Expected**: Downloads JSON file with all your data

### 9. Clear Data (DESTRUCTIVE - Test Last)
1. [ ] Open settings
2. [ ] Tap **"Clear All Data"**
3. [ ] Confirm twice
4. [ ] **Expected**: All data cleared, backup created, dashboard resets

---

## 🔧 API Endpoint Test (2 minutes)

Open terminal and run:

```bash
# Test all endpoints
curl http://localhost:3000/api/today | jq
curl http://localhost:3000/api/streak | jq
curl http://localhost:3000/api/history?days=14 | jq
curl http://localhost:3000/api/progress_photos | jq
```

**Expected**: All return valid JSON with 200 status

---

## 📱 Mobile Safari Test (iPhone/iPad)

1. [ ] Open on iPhone: `http://[YOUR_MAC_IP]:3000/`
2. [ ] **Voice FAB works** with touch hold
3. [ ] **No horizontal scroll**
4. [ ] **Animations are smooth** (60fps)
5. [ ] **Safe areas respected** (no content behind notch)
6. [ ] **Add to Home Screen** works (PWA)

---

## 🐛 Known Issues to Check

1. [ ] **Chart.js loading** - Should see graph, not error
2. [ ] **Voice recording** - Mic permission prompt appears
3. [ ] **Photo upload** - File picker opens
4. [ ] **Modal close** - All modals close properly
5. [ ] **Data persistence** - Refresh page, data still there

---

## ✅ Success Criteria

| Feature | Status | Notes |
|---------|--------|-------|
| Beautiful UI loads | [ ] | Neon aesthetic visible |
| Macro cards functional | [ ] | Show real data |
| Chart renders | [ ] | 14-day graph with target line |
| Add meal works | [ ] | Manual + voice |
| Meal history displays | [ ] | With delete functionality |
| Goal calculator works | [ ] | BMR/TDEE calculation |
| Settings functional | [ ] | Export, clear, edit goals |
| Photos upload | [ ] | Before/after display |
| Mobile responsive | [ ] | No issues on iPhone |
| No console errors | [ ] | Clean execution |

---

## 🚨 If Something Breaks

### Server won't start:
```bash
cd /Users/clawdbot/clawd/fitness-tracker
lsof -ti:3000 | xargs kill -9
python3 app_pro.py
```

### Chart doesn't show:
- Check browser console for Chart.js errors
- Verify CDN is loading: `https://cdn.jsdelivr.net/npm/chart.js`

### Data not saving:
- Check `fitness_data.json` exists
- Verify file permissions: `chmod 644 fitness_data.json`

### API errors:
- Check server logs for Python tracebacks
- Test endpoint in browser: `http://localhost:3000/api/today`

---

## 📊 Expected Results (Fresh Install)

**On first load:**
- Streak: 0 days (or current streak from existing data)
- Macros: 0/2200 calories, 0/200g protein, 0/250g carbs, 0/70g fat
- Chart: Empty graph with target line at 2200
- Meals: "No meals logged yet" message
- Photos: Empty dashed cards

**After adding 1 meal:**
- Macros update immediately
- Confetti animation plays
- Meal appears in history
- Chart shows today's calories

---

## 🎯 Final Verdict

If all checkboxes are ✅, the dashboard is **production-ready** and ready to deploy! 🚀

**Report any issues to:** This conversation thread  
**Backend logs:** `/tmp/fitness_test.log`  
**Data file:** `/Users/clawdbot/clawd/fitness-tracker/fitness_data.json`

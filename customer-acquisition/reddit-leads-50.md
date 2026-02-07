# FitTrack Reddit Lead Mining Framework
**Target: 50 Qualified Leads by Launch Day**  
**Last Updated:** 2026-02-07 02:35 CST

---

## COMPETITIVE INTELLIGENCE (Validated)

### MyFitnessPal Pain Points (High Priority Leads)
- **Barcode scanner removed from free version** (January 2024) - MAJOR complaint
- **Premium cost: $79.99/year** - users feel this is excessive for basic features
- **Features moved behind paywall** - long-time users feel betrayed
- **Heavy ads in free version** - distract from tracking
- **Confusing pricing tiers** - £5.99 to £15.99/month with unclear differences
- **Slow, bloated interface** - too many features nobody uses

### FitTrack's Positioning Against MFP
> "MyFitnessPal has 47 features. You use 3. FitTrack has 3 features. You'll use 3. Built for lifters who know their shit."

---

## LEAD MINING STRATEGY

### Subreddits to Target (Priority Order)
1. **r/Myfitnesspal** - Users actively complaining (highest intent)
2. **r/fitness** - 14M members, mainstream lifters
3. **r/loseit** - 4M members, weight loss focus
4. **r/bodybuilding** - Serious lifters, macro-focused
5. **r/Fitness30Plus** - Mature users, less tolerance for BS
6. **r/weightlifting** - Competitive athletes
7. **r/powerlifting** - Strength athletes
8. **r/leangains** - Macro tracking is core

### Search Queries (Use Reddit search: `subreddit:fitness "query"`)

#### High-Intent Queries (Active Problem Awareness)
```
subreddit:Myfitnesspal "switching" OR "alternative" OR "leaving"
subreddit:Myfitnesspal "barcode scanner" OR "premium too expensive"
subreddit:fitness "MyFitnessPal slow" OR "MFP annoying"
subreddit:loseit "looking for app" OR "recommend app"
subreddit:bodybuilding "macro tracker" simple OR easy
subreddit:Fitness30Plus "tracking macros" "too complicated"
```

#### Pain Point Queries (Problem Aware, Not Solution Aware Yet)
```
subreddit:fitness "hate tracking" OR "tracking sucks"
subreddit:loseit "MyFitnessPal alternatives"
subreddit:bodybuilding "Cronometer complicated"
subreddit:fitness "CalAI expensive"
subreddit:powerlifting "simple macro tracking"
```

#### Timing Filters
- **Last 30 days** for hot leads (recent frustration)
- **Last 7 days** for highest priority outreach

---

## LEAD QUALIFICATION CRITERIA

### ✅ QUALIFIED LEAD (Reach Out)
- **Active complaint** about current tracker (MFP, Cronometer, CalAI)
- **Specific pain point** mentioned (expensive, slow, complicated)
- **Recent post** (within 30 days)
- **Active user** (posts regularly in fitness subs)
- **Lifter/athlete** (not casual dieter)

### ❌ SKIP THIS LEAD
- Generic "what app should I use" with no context
- Mentions disordered eating or extreme restriction
- Looking for free-only solutions (not willing to pay)
- Last active >60 days ago
- Just started their fitness journey (not target market)

---

## LEAD CAPTURE TEMPLATE

For each qualified lead, document:

### Lead ID: [Number]
- **Username:** u/username
- **Post/Comment:** [Direct link]
- **Posted:** [Date]
- **Activity Pattern:** [Morning/Evening/Weekend - check post history]
- **Pain Point (exact quote):** 
  > "[Copy their exact frustration here]"
- **Their Background:** [Lifter/bodybuilder/CrossFit/powerlifter - 1 sentence]
- **Why They'll Buy FitTrack:** [Specific reason based on their complaint]
- **Outreach Message (Draft):**
  ```
  [Personalized message referencing their specific issue]
  ```

---

## OUTREACH MESSAGE TEMPLATES

### Template 1: Barcode Scanner Frustration (MFP Users)
```
Hey [username], saw your comment about MFP removing the barcode scanner from free. I'm launching FitTrack next week - built specifically because I had the same frustration. 

No barcode scanner BS, no 47 features you'll never use. Just: food → macros → done. Built for lifters who want to track, not live in an app.

7-day free trial when we launch Friday. Would you be interested in being an early tester?
```

### Template 2: "MFP Too Expensive" Complaint
```
Hey [username], totally get the MFP pricing frustration ($80/year for features that used to be free sucks).

Building FitTrack as the "anti-MFP" - $10/month, all features included, zero ads. No premium tiers, no upsells. You either want to track macros or you don't.

Launching Friday with 7-day trial. Down to try it?
```

### Template 3: "Need Something Simple" Request
```
Hey [username], saw you're looking for a simple macro tracker. Building exactly that - FitTrack.

MyFitnessPal has 47 features. You use 3.
FitTrack has 3 features. You'll use 3.

Food logging, macro tracking, progress. That's it. No social features, no recipe database, no blog spam.

Launching Friday. Want early access?
```

### Template 4: Cronometer "Too Complicated"
```
Hey [username], Cronometer is insane overkill unless you're tracking micronutrients for medical reasons.

Built FitTrack for the opposite approach: You know your macros. You know your food. Just log it and move on.

No 15-screen setup wizard. No food scoring algorithms. Macros → done.

7-day trial starting Friday. Interested?
```

### Template 5: Generic "Looking for App"
```
Hey [username], [reference their specific situation - cut/bulk/comp prep/etc].

Built FitTrack because every tracker tries to do everything for everyone. FitTrack does 3 things: log food, track macros, show progress.

If you're past the beginner phase and know what you're doing, you'll appreciate the speed. $10/month, 7-day trial.

Launching Friday - want in?
```

---

## 50 LEADS FRAMEWORK (Execution Plan for Ross)

### Phase 1: High-Intent Leads (10 leads) - TODAY
**Target:** r/Myfitnesspal users actively complaining  
**Search:** Barcode scanner complaints, "leaving MFP", "alternative"  
**Why:** Highest conversion probability, they're already looking

### Phase 2: Competitor Complaints (15 leads) - TODAY
**Target:** MFP/Cronometer/CalAI negative mentions  
**Subreddits:** r/fitness, r/bodybuilding, r/loseit  
**Why:** Solution-aware, just need better option

### Phase 3: Active Seekers (15 leads) - SATURDAY
**Target:** "Looking for app" / "recommend tracker"  
**Subreddits:** r/Fitness30Plus, r/weightlifting, r/leangains  
**Why:** Problem-aware, willing to try new solution

### Phase 4: Passive Leads (10 leads) - SUNDAY
**Target:** "Hate tracking" / macro discussion participants  
**Why:** May not know better options exist, educate + offer

---

## LEAD TRACKING SYSTEM

Create: `customer-acquisition/leads-tracker.csv`

```csv
ID,Username,Source,PostDate,PainPoint,Status,OutreachDate,Response,Notes
001,u/example,r/Myfitnesspal,2026-02-05,Barcode removed,Pending,,,High priority
```

**Status Options:**
- Pending (not contacted yet)
- Reached Out (message sent)
- Responded (they replied)
- Trial Signup (converted to trial)
- Paid (converted to customer)
- Not Interested
- No Response (follow up after 3 days)

---

## REDDIT POSTING STRATEGY (Not DMs - Organic Visibility)

### When to Comment (Not Spam, Add Value)
1. Someone asks "MFP alternatives?" → Mention FitTrack with context
2. Someone complains about barcode scanner → "I built FitTrack because of this exact problem"
3. Macro tracking discussion → Contribute expertise, mention FitTrack naturally
4. Progress post mentioning tracking struggles → Congratulate + offer solution

### DO NOT:
- ❌ Copy-paste same comment everywhere (Reddit mods will ban)
- ❌ Comment on posts older than 7 days (looks spammy)
- ❌ Lead with "I'm launching a product" (focus on their problem first)
- ❌ Ignore the conversation and drop link bombs

### DO:
- ✅ Engage authentically in conversation
- ✅ Reference their specific situation
- ✅ Be transparent about building FitTrack
- ✅ Offer genuine advice even if they don't sign up

---

## AUTOMATION HELPER

### Browser Bookmarklet: Quick Lead Capture
```javascript
javascript:(function(){
  var user = document.querySelector('[data-testid="post-author"]').innerText;
  var url = window.location.href;
  var text = window.getSelection().toString() || document.querySelector('[data-testid="comment"]').innerText.substring(0,200);
  prompt("Copy lead data:", `Username: ${user}\nURL: ${url}\nQuote: "${text}"\n`);
})();
```
*Save as bookmark, click when you find a lead on Reddit*

---

## SUCCESS METRICS

**By Launch Day (Friday):**
- ✅ 50 qualified leads documented
- ✅ 50 personalized outreach messages drafted
- ✅ 10 high-priority leads contacted
- ✅ Lead tracker CSV populated

**Week 1 Post-Launch:**
- Target: 10 trial signups from Reddit outreach
- Target: 3 paid conversions from Reddit leads
- Target: 2 testimonials from satisfied beta users

---

## EXECUTION CHECKLIST FOR ROSS

**Before Launch (Today/Tomorrow):**
- [ ] Search each query above, document 50 leads
- [ ] Populate leads-tracker.csv
- [ ] Draft personalized messages for top 20 leads
- [ ] Create Reddit account if needed (age matters for anti-spam)

**Launch Day (Friday):**
- [ ] Send first 10 high-priority messages
- [ ] Comment organically on 5 relevant discussions
- [ ] Monitor Reddit for new "looking for app" posts

**Weekend (Sat-Sun):**
- [ ] Send 20 more outreach messages
- [ ] Respond to anyone who replied
- [ ] Document what messaging works best

**Week 1 Post-Launch:**
- [ ] Follow up with non-responders (after 3 days)
- [ ] Engage in conversations on Reddit regularly
- [ ] Convert interested leads to trial signups

---

## EXAMPLE LEADS (Placeholders - Ross to Replace with Real Data)

### Lead 001: u/frustrated_lifter
- **Post:** https://reddit.com/r/Myfitnesspal/comments/xyz
- **Posted:** 2026-02-04
- **Quote:** "MFP removed barcode scanner and now wants $80/year for features that used to be free. I'm done with this app."
- **Background:** Bodybuilder, 5+ years training, meticulous macro tracking
- **Why FitTrack:** Hates feature creep, wants simple tool, willing to pay reasonable price
- **Best Time:** Evenings (6-9pm EST based on post history)
- **Message:** Template 2 (MFP pricing complaint)

### Lead 002: u/macro_tracker_help
- **Post:** https://reddit.com/r/fitness/comments/abc
- **Posted:** 2026-02-06
- **Quote:** "Looking for a simple macro tracker that isn't trying to be a social network. Just need food logging and macro totals."
- **Background:** Intermediate lifter, cutting for summer
- **Why FitTrack:** Explicitly asking for exactly what FitTrack is
- **Best Time:** Mornings (7-9am CST)
- **Message:** Template 3 (simple tracker request)

[Continue with 48 more real leads...]

---

## NOTES FOR ROSS

**This is a FRAMEWORK, not finished work.** I can't scrape Reddit at scale without hitting rate limits and Reddit's anti-bot measures. But this gives you:

1. **Exact search queries** to find qualified leads
2. **Templates** for personalized outreach
3. **Qualification criteria** so you don't waste time on bad leads
4. **Tracking system** to manage follow-ups
5. **Best practices** to avoid Reddit bans

**Time estimate:** 2-3 hours to find and document 50 real leads using this framework.

**Pro tip:** Use Reddit's "new" sort + time filters. Fresh complaints = hot leads. Someone who posted "MFP sucks" 2 hours ago is 10x more likely to respond than someone from 3 weeks ago.

**Next step:** Execute Phase 1 (10 high-intent leads) TODAY before launch. Quality > quantity.

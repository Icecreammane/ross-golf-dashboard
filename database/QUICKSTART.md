# SQLite Migration - Quick Start

Get up and running in 5 minutes.

## ⚡ One-Command Installation

```bash
cd ~/clawd/database
./upgrade.sh
```

That's it! The script will:
1. Check prerequisites
2. Backup your JSON files
3. Create the database
4. Migrate all data
5. Run tests
6. Verify performance

## 🎯 Verify It Worked

```bash
# Check database health
python3 -c "from database.query_library import Database; db = Database(); import json; print(json.dumps(db.health_check(), indent=2))"
```

Expected output:
```json
{
  "opportunities": 9,
  "workouts": 4,
  "food_logs": 25,
  "golf_rounds": 4,
  "emails": 3,
  "twitter": 4,
  "social_posts": 2,
  "conversions": 2,
  "decisions": 1
}
```

## 📖 Basic Usage

### Example 1: Get Top Opportunities

```python
from database.query_library import Database

db = Database()

with db.opportunities as opp:
    top = opp.get_top_opportunities(limit=5)
    for o in top:
        print(f"[{o['score']}] {o['title']} - {o['source']}")
```

### Example 2: Track Fitness Progress

```python
from database.query_library import Database

db = Database()

# Today's nutrition
with db.fitness as fit:
    nutrition = fit.get_daily_nutrition()
    print(f"Calories: {nutrition['total_calories']}")
    print(f"Protein: {nutrition['total_protein']}g")

# Recent workouts
with db.fitness as fit:
    workouts = fit.get_recent_workouts(days=7)
    for w in workouts:
        print(f"{w['date']}: {w['total_lifts']} lifts")
```

### Example 3: Revenue Analytics

```python
from database.query_library import Database

db = Database()

# Total revenue
with db.analytics as analytics:
    total = analytics.get_total_revenue()
    print(f"Total: ${total:.2f}")
    
    # By source
    by_source = analytics.get_revenue_by_source()
    for s in by_source:
        print(f"  {s['source']}: ${s['total_revenue']:.2f}")
```

## 🧪 Run Tests

```bash
cd ~/clawd/database
python3 test_database.py
```

All 32 tests should pass in <1 second.

## 📚 Learn More

- **Full Documentation**: See `README.md`
- **Schema Details**: See `SCHEMA_DOCUMENTATION.md`
- **Build Report**: See `BUILD_SQLITE_MIGRATION.md`
- **Query Examples**: Run `python3 query_library.py`

## 🔧 Troubleshooting

### "Python not found"
```bash
# Check Python version (need 3.7+)
python3 --version
```

### "Migration failed"
```bash
# Run in dry-run mode to see what would happen
python3 migrate.py --dry-run
```

### "Tests failed"
```bash
# Check test output for specific failures
python3 test_database.py -v
```

## 🎓 Common Tasks

### Backup Database
```bash
sqlite3 database/data.db ".backup database/backups/data_$(date +%Y%m%d).db"
```

### Query Directly
```bash
sqlite3 database/data.db "SELECT * FROM opportunities WHERE score > 70 LIMIT 5"
```

### Count Records
```bash
sqlite3 database/data.db "SELECT 'opportunities', COUNT(*) FROM opportunities UNION ALL SELECT 'workouts', COUNT(*) FROM workouts"
```

## 🚀 Integration

### Update Your Scripts

**Before (JSON):**
```python
import json
with open('revenue/opportunities.json') as f:
    data = json.load(f)
    opportunities = data['inventory']['opportunities']
```

**After (SQLite):**
```python
from database.query_library import Database
db = Database()
with db.opportunities as opp:
    opportunities = opp.get_top_opportunities()
```

### Benefits
- ⚡ 10-100x faster queries
- 🔍 Powerful filtering and search
- 📊 Aggregate statistics
- 🔒 Data integrity with constraints
- 📈 Scales to millions of records

## ✅ Verification Checklist

- [ ] `./upgrade.sh` completes successfully
- [ ] All tests pass
- [ ] Health check shows correct record counts
- [ ] Can query data with query_library
- [ ] JSON backups created in `backups/` directory

**Done!** You're ready to use SQLite. 🎉

---

**Questions?** See `README.md` or `SCHEMA_DOCUMENTATION.md`

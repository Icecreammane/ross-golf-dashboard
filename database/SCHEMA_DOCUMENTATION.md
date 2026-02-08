# Database Schema Documentation

Complete reference for all tables, indexes, and relationships.

## Table of Contents

- [Opportunities](#opportunities)
- [Fitness (Workouts, Lifts, Food, Weight)](#fitness)
- [Golf](#golf)
- [Email](#email)
- [Twitter](#twitter)
- [Analytics (Social Posts, Conversions)](#analytics)
- [Decisions](#decisions)
- [Metadata](#metadata)

---

## Opportunities

**Purpose**: Track all revenue opportunities from various sources

### Schema

```sql
CREATE TABLE opportunities (
    id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    type TEXT NOT NULL,
    title TEXT,
    context TEXT,
    url TEXT,
    score INTEGER NOT NULL,
    revenue_potential TEXT,
    detected_at TEXT NOT NULL,
    tracked_at TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    converted INTEGER DEFAULT 0,
    conversion_date TEXT,
    actual_revenue REAL,
    conversion_notes TEXT,
    sender TEXT,
    content_preview TEXT,
    last_updated TEXT NOT NULL,
    draft TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Indexes

```sql
CREATE INDEX idx_opportunities_score ON opportunities(score DESC);
CREATE INDEX idx_opportunities_source ON opportunities(source);
CREATE INDEX idx_opportunities_type ON opportunities(type);
CREATE INDEX idx_opportunities_status ON opportunities(status);
CREATE INDEX idx_opportunities_detected_at ON opportunities(detected_at DESC);
CREATE INDEX idx_opportunities_revenue ON opportunities(revenue_potential);
CREATE INDEX idx_opportunities_converted ON opportunities(converted);
CREATE INDEX idx_opportunities_composite ON opportunities(source, status, score DESC);
```

### Fields

| Field | Type | Description |
|-------|------|-------------|
| id | TEXT | Unique identifier (format varies by source) |
| source | TEXT | Origin: email, twitter, reddit, revenue_plan, etc. |
| type | TEXT | Opportunity type: coaching, partnership, feedback, etc. |
| title | TEXT | Short title/summary |
| context | TEXT | Full context/description |
| url | TEXT | URL if applicable |
| score | INTEGER | Priority score 0-100 |
| revenue_potential | TEXT | Estimated revenue (e.g., "$500-1000") |
| detected_at | TEXT | When opportunity was first detected |
| tracked_at | TEXT | When added to database |
| status | TEXT | pending, approved, drafted, rejected, closed |
| converted | INTEGER | 1 if converted to revenue, 0 otherwise |
| conversion_date | TEXT | When conversion happened |
| actual_revenue | REAL | Actual revenue generated |
| conversion_notes | TEXT | Notes about conversion |
| sender | TEXT | Person/account who sent |
| content_preview | TEXT | Preview of content |
| last_updated | TEXT | Last modification timestamp |
| draft | TEXT | Draft response if applicable |

### Common Queries

- Top opportunities by score
- Opportunities by source
- Pending opportunities
- Converted opportunities with revenue
- Search by keyword

---

## Fitness

### Workouts

**Purpose**: Track workout sessions

```sql
CREATE TABLE workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    timestamp REAL NOT NULL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_workouts_date ON workouts(date DESC);
CREATE INDEX idx_workouts_timestamp ON workouts(timestamp DESC);
```

### Lifts

**Purpose**: Individual lift records within workouts

```sql
CREATE TABLE lifts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workout_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    weight REAL NOT NULL,
    reps INTEGER NOT NULL,
    sets INTEGER NOT NULL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (workout_id) REFERENCES workouts(id) ON DELETE CASCADE
);

CREATE INDEX idx_lifts_workout ON lifts(workout_id);
CREATE INDEX idx_lifts_name ON lifts(name);
CREATE INDEX idx_lifts_date_name ON lifts(workout_id, name);
```

### Food Logs

**Purpose**: Nutrition tracking

```sql
CREATE TABLE food_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    timestamp REAL NOT NULL,
    description TEXT,
    calories INTEGER NOT NULL,
    protein REAL NOT NULL,
    carbs REAL NOT NULL,
    fat REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_food_date ON food_logs(date DESC);
CREATE INDEX idx_food_timestamp ON food_logs(timestamp DESC);
CREATE INDEX idx_food_calories ON food_logs(calories);
```

### Weight Logs

**Purpose**: Weight tracking over time

```sql
CREATE TABLE weight_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    timestamp REAL NOT NULL,
    weight REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_weight_date ON weight_logs(date DESC);
```

### Fitness Settings

**Purpose**: User fitness goals and targets

```sql
CREATE TABLE fitness_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    target_weight REAL,
    current_weight REAL,
    daily_calories INTEGER,
    daily_protein INTEGER,
    daily_carbs INTEGER,
    daily_fat INTEGER,
    birthday TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## Golf

### Golf Rounds

**Purpose**: Track golf round scores

```sql
CREATE TABLE golf_rounds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    course TEXT NOT NULL,
    score INTEGER NOT NULL,
    par INTEGER NOT NULL,
    differential REAL NOT NULL,
    handicap_estimate REAL,
    notes TEXT,
    timestamp TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_golf_date ON golf_rounds(date DESC);
CREATE INDEX idx_golf_course ON golf_rounds(course);
CREATE INDEX idx_golf_score ON golf_rounds(score);
CREATE INDEX idx_golf_differential ON golf_rounds(differential);
```

### Golf Courses

**Purpose**: Aggregate statistics per course

```sql
CREATE TABLE golf_courses (
    course_name TEXT PRIMARY KEY,
    rounds_played INTEGER DEFAULT 0,
    total_score INTEGER DEFAULT 0,
    best_score INTEGER,
    worst_score INTEGER,
    average_score REAL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

---

## Email

### Email Summaries

**Purpose**: Important email tracking

```sql
CREATE TABLE email_summaries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender TEXT NOT NULL,
    sender_email TEXT NOT NULL,
    subject TEXT NOT NULL,
    preview TEXT,
    importance_reason TEXT,
    timestamp TEXT NOT NULL,
    date TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_email_sender ON email_summaries(sender);
CREATE INDEX idx_email_timestamp ON email_summaries(timestamp DESC);
CREATE INDEX idx_email_subject ON email_summaries(subject);
```

### Email Key Points

**Purpose**: Extracted key points from emails

```sql
CREATE TABLE email_key_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id INTEGER NOT NULL,
    key_point TEXT NOT NULL,
    FOREIGN KEY (email_id) REFERENCES email_summaries(id) ON DELETE CASCADE
);

CREATE INDEX idx_email_keypoints ON email_key_points(email_id);
```

---

## Twitter

### Twitter Opportunities

**Purpose**: Track engagement opportunities on Twitter

```sql
CREATE TABLE twitter_opportunities (
    id TEXT PRIMARY KEY,
    type TEXT NOT NULL,
    sender TEXT NOT NULL,
    sender_id TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL,
    url TEXT NOT NULL,
    score INTEGER NOT NULL,
    opportunity_type TEXT NOT NULL,
    author_followers INTEGER,
    retweet_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    quote_count INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_twitter_score ON twitter_opportunities(score DESC);
CREATE INDEX idx_twitter_type ON twitter_opportunities(opportunity_type);
CREATE INDEX idx_twitter_timestamp ON twitter_opportunities(timestamp DESC);
CREATE INDEX idx_twitter_sender ON twitter_opportunities(sender);
CREATE INDEX idx_twitter_followers ON twitter_opportunities(author_followers DESC);
```

### Twitter Opportunity Types

**Purpose**: Many-to-many relationship for opportunity types

```sql
CREATE TABLE twitter_opportunity_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twitter_id TEXT NOT NULL,
    type TEXT NOT NULL,
    FOREIGN KEY (twitter_id) REFERENCES twitter_opportunities(id) ON DELETE CASCADE
);

CREATE INDEX idx_twitter_types ON twitter_opportunity_types(twitter_id);
```

### Twitter Opportunity Reasons

**Purpose**: Store reasons for opportunity classification

```sql
CREATE TABLE twitter_opportunity_reasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twitter_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    FOREIGN KEY (twitter_id) REFERENCES twitter_opportunities(id) ON DELETE CASCADE
);

CREATE INDEX idx_twitter_reasons ON twitter_opportunity_reasons(twitter_id);
```

---

## Analytics

### Social Posts

**Purpose**: Track social media posts and engagement

```sql
CREATE TABLE social_posts (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL,
    posted_at TEXT NOT NULL,
    tracked_at TEXT NOT NULL,
    likes INTEGER DEFAULT 0,
    retweets INTEGER DEFAULT 0,
    replies INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_social_posted ON social_posts(posted_at DESC);
CREATE INDEX idx_social_engagement ON social_posts(likes + retweets + replies DESC);
```

### Conversions

**Purpose**: Track revenue conversions

```sql
CREATE TABLE conversions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_id TEXT NOT NULL,
    source TEXT NOT NULL,
    type TEXT NOT NULL,
    revenue REAL NOT NULL,
    date TEXT NOT NULL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conversions_date ON conversions(date DESC);
CREATE INDEX idx_conversions_source ON conversions(source);
CREATE INDEX idx_conversions_revenue ON conversions(revenue DESC);
CREATE INDEX idx_conversions_tracking ON conversions(tracking_id);
```

### Engagement by Hour

**Purpose**: Analyze engagement patterns by hour of day

```sql
CREATE TABLE engagement_by_hour (
    hour INTEGER PRIMARY KEY CHECK (hour >= 0 AND hour <= 23),
    posts INTEGER DEFAULT 0,
    engagement INTEGER DEFAULT 0,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Source Performance

**Purpose**: Aggregate performance metrics by source

```sql
CREATE TABLE source_performance (
    source TEXT PRIMARY KEY,
    total INTEGER DEFAULT 0,
    converted INTEGER DEFAULT 0,
    revenue REAL DEFAULT 0,
    conversion_rate REAL GENERATED ALWAYS AS (
        CASE WHEN total > 0 THEN (converted * 100.0 / total) ELSE 0 END
    ) STORED,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Note**: `conversion_rate` is a **generated column** - automatically calculated!

---

## Decisions

### Decisions

**Purpose**: Track decisions and outcomes

```sql
CREATE TABLE decisions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    decision TEXT NOT NULL,
    context TEXT,
    category TEXT,
    confidence INTEGER,
    hour INTEGER,
    day_of_week TEXT,
    outcome TEXT,
    outcome_recorded TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_decisions_timestamp ON decisions(timestamp DESC);
CREATE INDEX idx_decisions_category ON decisions(category);
CREATE INDEX idx_decisions_confidence ON decisions(confidence DESC);
CREATE INDEX idx_decisions_hour ON decisions(hour);
CREATE INDEX idx_decisions_day ON decisions(day_of_week);
```

### Decision Lessons

**Purpose**: Store lessons learned from decisions

```sql
CREATE TABLE decision_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id INTEGER NOT NULL,
    lesson TEXT NOT NULL,
    FOREIGN KEY (decision_id) REFERENCES decisions(id) ON DELETE CASCADE
);

CREATE INDEX idx_decision_lessons ON decision_lessons(decision_id);
```

---

## Metadata

### Migration Metadata

**Purpose**: Track migration version and status

```sql
CREATE TABLE migration_metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
```

**Default Values**:
- `schema_version`: "1.0"
- `migrated_at`: Timestamp of migration

---

## Relationships

```
opportunities (standalone)

workouts
  ├── lifts (1:many)

food_logs (standalone)

weight_logs (standalone)

fitness_settings (singleton)

golf_rounds (standalone)

golf_courses (standalone)

email_summaries
  ├── email_key_points (1:many)

twitter_opportunities
  ├── twitter_opportunity_types (1:many)
  └── twitter_opportunity_reasons (1:many)

social_posts (standalone)

conversions (standalone)

engagement_by_hour (standalone)

source_performance (standalone)

decisions
  ├── decision_lessons (1:many)

migration_metadata (standalone)
```

---

## Data Types

### Text Fields
- All timestamps use **ISO 8601** format: `YYYY-MM-DDTHH:MM:SS` or `YYYY-MM-DDTHH:MM:SS.ffffff`
- Dates use **ISO date** format: `YYYY-MM-DD`
- IDs can be text (external) or auto-increment integers (internal)

### Numeric Fields
- `INTEGER`: Whole numbers (scores, counts)
- `REAL`: Floating point (weight, revenue, differentials)

### Boolean Fields
- Stored as `INTEGER`: 0 = false, 1 = true
- Example: `converted INTEGER DEFAULT 0`

---

## Constraints

### Primary Keys
- Text IDs for external references (opportunities, twitter)
- Auto-increment for internal records (workouts, lifts)

### Foreign Keys
- **CASCADE DELETE**: When parent deleted, children deleted
- Example: Deleting a workout deletes all its lifts

### Unique Constraints
- `weight_logs.date`: One weight entry per day
- `engagement_by_hour.hour`: One record per hour (0-23)
- `fitness_settings.id`: Singleton table (only id=1 allowed)

### Check Constraints
- `engagement_by_hour.hour CHECK (hour >= 0 AND hour <= 23)`
- `fitness_settings.id CHECK (id = 1)`

---

## Generated Columns

### source_performance.conversion_rate

```sql
conversion_rate REAL GENERATED ALWAYS AS (
    CASE WHEN total > 0 THEN (converted * 100.0 / total) ELSE 0 END
) STORED
```

Automatically calculates conversion rate percentage. Updated whenever `total` or `converted` changes.

---

## Index Strategy

### Single Column Indexes
- Primary keys (automatic)
- Foreign keys for joins
- Date/timestamp fields for range queries
- Score fields for sorting

### Composite Indexes
- Common query patterns: `(source, status, score DESC)`
- Multi-field filters: `(workout_id, name)`

### Expression Indexes
- Calculated values: `(likes + retweets + replies DESC)`

---

## Performance Tips

1. **Always use indexes**: All common query patterns are indexed
2. **Use LIMIT**: Don't fetch more than needed
3. **Use date ranges**: Index on date/timestamp fields
4. **Avoid LIKE '%term%'**: Use full-text search if needed
5. **Use prepared statements**: Prevents SQL injection, faster execution

---

## Schema Evolution

### Version 1.0 (Current)
- Initial schema with all core tables
- Strategic indexes for <10ms queries
- Generated columns for calculated values

### Future Additions
To add a new table:
1. Update `schema.sql`
2. Increment `schema_version` in migration_metadata
3. Add migration logic to `migrate.py`
4. Add query class to `query_library.py`
5. Add tests to `test_database.py`
6. Update this documentation

---

## Backup Strategy

### What to Backup
- `data.db` - The SQLite database
- JSON files - For rollback capability
- `schema.sql` - Schema definition
- Migration logs - Audit trail

### How Often
- Before schema changes
- Before bulk updates
- Daily for production

### Commands
```bash
# Quick backup
sqlite3 data.db ".backup backups/data_$(date +%Y%m%d).db"

# With compression
sqlite3 data.db ".backup backups/data.db" && gzip backups/data.db
```

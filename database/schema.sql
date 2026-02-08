-- SQLite Schema for All Data Migration
-- Version: 1.0
-- Created: 2026-02-08

-- =============================================================================
-- OPPORTUNITIES TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS opportunities (
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

CREATE INDEX IF NOT EXISTS idx_opportunities_score ON opportunities(score DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_source ON opportunities(source);
CREATE INDEX IF NOT EXISTS idx_opportunities_type ON opportunities(type);
CREATE INDEX IF NOT EXISTS idx_opportunities_status ON opportunities(status);
CREATE INDEX IF NOT EXISTS idx_opportunities_detected_at ON opportunities(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_opportunities_revenue ON opportunities(revenue_potential);
CREATE INDEX IF NOT EXISTS idx_opportunities_converted ON opportunities(converted);
CREATE INDEX IF NOT EXISTS idx_opportunities_composite ON opportunities(source, status, score DESC);

-- =============================================================================
-- FITNESS - WORKOUTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS workouts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL,
    timestamp REAL NOT NULL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_workouts_date ON workouts(date DESC);
CREATE INDEX IF NOT EXISTS idx_workouts_timestamp ON workouts(timestamp DESC);

-- =============================================================================
-- FITNESS - LIFTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS lifts (
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

CREATE INDEX IF NOT EXISTS idx_lifts_workout ON lifts(workout_id);
CREATE INDEX IF NOT EXISTS idx_lifts_name ON lifts(name);
CREATE INDEX IF NOT EXISTS idx_lifts_date_name ON lifts(workout_id, name);

-- =============================================================================
-- FITNESS - FOOD LOGS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS food_logs (
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

CREATE INDEX IF NOT EXISTS idx_food_date ON food_logs(date DESC);
CREATE INDEX IF NOT EXISTS idx_food_timestamp ON food_logs(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_food_calories ON food_logs(calories);

-- =============================================================================
-- FITNESS - WEIGHT LOGS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS weight_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT NOT NULL UNIQUE,
    timestamp REAL NOT NULL,
    weight REAL NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_weight_date ON weight_logs(date DESC);

-- =============================================================================
-- FITNESS - SETTINGS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS fitness_settings (
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

-- =============================================================================
-- GOLF TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS golf_rounds (
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

CREATE INDEX IF NOT EXISTS idx_golf_date ON golf_rounds(date DESC);
CREATE INDEX IF NOT EXISTS idx_golf_course ON golf_rounds(course);
CREATE INDEX IF NOT EXISTS idx_golf_score ON golf_rounds(score);
CREATE INDEX IF NOT EXISTS idx_golf_differential ON golf_rounds(differential);

-- =============================================================================
-- GOLF COURSES TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS golf_courses (
    course_name TEXT PRIMARY KEY,
    rounds_played INTEGER DEFAULT 0,
    total_score INTEGER DEFAULT 0,
    best_score INTEGER,
    worst_score INTEGER,
    average_score REAL,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- EMAIL SUMMARY TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS email_summaries (
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

CREATE INDEX IF NOT EXISTS idx_email_sender ON email_summaries(sender);
CREATE INDEX IF NOT EXISTS idx_email_timestamp ON email_summaries(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_email_subject ON email_summaries(subject);

-- =============================================================================
-- EMAIL KEY POINTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS email_key_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email_id INTEGER NOT NULL,
    key_point TEXT NOT NULL,
    FOREIGN KEY (email_id) REFERENCES email_summaries(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_email_keypoints ON email_key_points(email_id);

-- =============================================================================
-- TWITTER OPPORTUNITIES TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS twitter_opportunities (
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

CREATE INDEX IF NOT EXISTS idx_twitter_score ON twitter_opportunities(score DESC);
CREATE INDEX IF NOT EXISTS idx_twitter_type ON twitter_opportunities(opportunity_type);
CREATE INDEX IF NOT EXISTS idx_twitter_timestamp ON twitter_opportunities(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_twitter_sender ON twitter_opportunities(sender);
CREATE INDEX IF NOT EXISTS idx_twitter_followers ON twitter_opportunities(author_followers DESC);

-- =============================================================================
-- TWITTER OPPORTUNITY TYPES TABLE (Many-to-Many)
-- =============================================================================
CREATE TABLE IF NOT EXISTS twitter_opportunity_types (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twitter_id TEXT NOT NULL,
    type TEXT NOT NULL,
    FOREIGN KEY (twitter_id) REFERENCES twitter_opportunities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_twitter_types ON twitter_opportunity_types(twitter_id);

-- =============================================================================
-- TWITTER OPPORTUNITY REASONS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS twitter_opportunity_reasons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    twitter_id TEXT NOT NULL,
    reason TEXT NOT NULL,
    FOREIGN KEY (twitter_id) REFERENCES twitter_opportunities(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_twitter_reasons ON twitter_opportunity_reasons(twitter_id);

-- =============================================================================
-- REVENUE/ANALYTICS - SOCIAL POSTS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS social_posts (
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

CREATE INDEX IF NOT EXISTS idx_social_posted ON social_posts(posted_at DESC);
CREATE INDEX IF NOT EXISTS idx_social_engagement ON social_posts(likes + retweets + replies DESC);

-- =============================================================================
-- REVENUE/ANALYTICS - CONVERSIONS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS conversions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tracking_id TEXT NOT NULL,
    source TEXT NOT NULL,
    type TEXT NOT NULL,
    revenue REAL NOT NULL,
    date TEXT NOT NULL,
    notes TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_conversions_date ON conversions(date DESC);
CREATE INDEX IF NOT EXISTS idx_conversions_source ON conversions(source);
CREATE INDEX IF NOT EXISTS idx_conversions_revenue ON conversions(revenue DESC);
CREATE INDEX IF NOT EXISTS idx_conversions_tracking ON conversions(tracking_id);

-- =============================================================================
-- ANALYTICS - ENGAGEMENT BY HOUR TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS engagement_by_hour (
    hour INTEGER PRIMARY KEY CHECK (hour >= 0 AND hour <= 23),
    posts INTEGER DEFAULT 0,
    engagement INTEGER DEFAULT 0,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- ANALYTICS - SOURCE PERFORMANCE TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS source_performance (
    source TEXT PRIMARY KEY,
    total INTEGER DEFAULT 0,
    converted INTEGER DEFAULT 0,
    revenue REAL DEFAULT 0,
    conversion_rate REAL GENERATED ALWAYS AS (
        CASE WHEN total > 0 THEN (converted * 100.0 / total) ELSE 0 END
    ) STORED,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- =============================================================================
-- DECISIONS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS decisions (
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

CREATE INDEX IF NOT EXISTS idx_decisions_timestamp ON decisions(timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_decisions_category ON decisions(category);
CREATE INDEX IF NOT EXISTS idx_decisions_confidence ON decisions(confidence DESC);
CREATE INDEX IF NOT EXISTS idx_decisions_hour ON decisions(hour);
CREATE INDEX IF NOT EXISTS idx_decisions_day ON decisions(day_of_week);

-- =============================================================================
-- DECISION LESSONS TABLE
-- =============================================================================
CREATE TABLE IF NOT EXISTS decision_lessons (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    decision_id INTEGER NOT NULL,
    lesson TEXT NOT NULL,
    FOREIGN KEY (decision_id) REFERENCES decisions(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_decision_lessons ON decision_lessons(decision_id);

-- =============================================================================
-- METADATA TABLE (for migration tracking)
-- =============================================================================
CREATE TABLE IF NOT EXISTS migration_metadata (
    key TEXT PRIMARY KEY,
    value TEXT,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

-- Insert version info
INSERT OR REPLACE INTO migration_metadata (key, value) VALUES ('schema_version', '1.0');
INSERT OR REPLACE INTO migration_metadata (key, value) VALUES ('migrated_at', CURRENT_TIMESTAMP);

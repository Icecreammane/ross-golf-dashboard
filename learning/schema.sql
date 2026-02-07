-- Outcome Learning System Database Schema

CREATE TABLE IF NOT EXISTS suggestions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    text TEXT NOT NULL,
    category TEXT NOT NULL CHECK(category IN ('productivity', 'fun', 'revenue', 'infrastructure', 'learning', 'health', 'social', 'other')),
    confidence TEXT NOT NULL CHECK(confidence IN ('high', 'medium', 'low')),
    context TEXT,
    session_id TEXT,
    detected_response TEXT,  -- First detected response from Ross
    response_timestamp INTEGER
);

CREATE TABLE IF NOT EXISTS outcomes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    suggestion_id INTEGER NOT NULL,
    status TEXT NOT NULL CHECK(status IN ('implemented', 'ignored', 'deferred', 'rejected', 'in_progress')),
    result TEXT CHECK(result IN ('success', 'failure', 'partial', 'unknown')),
    notes TEXT,
    timestamp INTEGER NOT NULL,
    FOREIGN KEY (suggestion_id) REFERENCES suggestions(id)
);

CREATE TABLE IF NOT EXISTS patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_type TEXT NOT NULL,  -- 'category_success', 'confidence_accuracy', 'timing', etc.
    pattern_key TEXT NOT NULL,
    pattern_value TEXT NOT NULL,
    confidence REAL,
    sample_size INTEGER,
    last_updated INTEGER NOT NULL,
    UNIQUE(pattern_type, pattern_key)
);

CREATE INDEX IF NOT EXISTS idx_suggestions_timestamp ON suggestions(timestamp);
CREATE INDEX IF NOT EXISTS idx_suggestions_category ON suggestions(category);
CREATE INDEX IF NOT EXISTS idx_outcomes_suggestion_id ON outcomes(suggestion_id);
CREATE INDEX IF NOT EXISTS idx_outcomes_timestamp ON outcomes(timestamp);
CREATE INDEX IF NOT EXISTS idx_patterns_type ON patterns(pattern_type);

-- Revenue Forecast Database Schema
-- Tracks MRR over time and enables trend analysis

CREATE TABLE IF NOT EXISTS mrr_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    mrr_cents INTEGER NOT NULL,
    customer_count INTEGER DEFAULT 0,
    source TEXT DEFAULT 'manual',
    notes TEXT
);

CREATE TABLE IF NOT EXISTS growth_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE NOT NULL,
    daily_growth_rate REAL,
    weekly_growth_rate REAL,
    monthly_projection_cents INTEGER,
    days_to_target INTEGER,
    customers_needed INTEGER,
    calculated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS forecast_scenarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    scenario_name TEXT NOT NULL,
    additional_mrr_cents INTEGER NOT NULL,
    projected_days_to_target INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS daily_updates (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE UNIQUE NOT NULL,
    update_text TEXT NOT NULL,
    delivered BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_mrr_timestamp ON mrr_snapshots(timestamp);
CREATE INDEX IF NOT EXISTS idx_growth_date ON growth_metrics(date);
CREATE INDEX IF NOT EXISTS idx_scenario_date ON forecast_scenarios(date);
CREATE INDEX IF NOT EXISTS idx_daily_update_date ON daily_updates(date);

-- View for latest metrics
CREATE VIEW IF NOT EXISTS latest_metrics AS
SELECT 
    m.mrr_cents / 100.0 as current_mrr,
    m.customer_count,
    m.timestamp,
    g.daily_growth_rate,
    g.weekly_growth_rate,
    g.monthly_projection_cents / 100.0 as monthly_projection,
    g.days_to_target,
    g.customers_needed
FROM mrr_snapshots m
LEFT JOIN growth_metrics g ON DATE(m.timestamp) = g.date
ORDER BY m.timestamp DESC
LIMIT 1;

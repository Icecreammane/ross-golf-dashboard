#!/bin/bash
# SQLite Migration - One-Command Upgrade Script
# Usage: ./upgrade.sh

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Paths
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE="$HOME/clawd"
DB_PATH="$SCRIPT_DIR/data.db"
BACKUP_DIR="$SCRIPT_DIR/backups"

echo ""
echo "======================================================================="
echo "  SQLite Database Migration - Production Upgrade"
echo "======================================================================="
echo ""

# Step 1: Check prerequisites
echo -e "${BLUE}[1/7]${NC} Checking prerequisites..."

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}  ✓ Python $PYTHON_VERSION${NC}"

# Check SQLite
if ! command -v sqlite3 &> /dev/null; then
    echo -e "${RED}✗ SQLite not found${NC}"
    exit 1
fi
SQLITE_VERSION=$(sqlite3 --version | awk '{print $1}')
echo -e "${GREEN}  ✓ SQLite $SQLITE_VERSION${NC}"

# Check required files
REQUIRED_FILES=("schema.sql" "migrate.py" "query_library.py" "test_database.py")
for file in "${REQUIRED_FILES[@]}"; do
    if [ ! -f "$SCRIPT_DIR/$file" ]; then
        echo -e "${RED}✗ Missing required file: $file${NC}"
        exit 1
    fi
done
echo -e "${GREEN}  ✓ All required files present${NC}"

# Step 2: Backup JSON files
echo -e "\n${BLUE}[2/7]${NC} Creating backup of JSON files..."

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
JSON_BACKUP="$BACKUP_DIR/json_backup_$TIMESTAMP"
mkdir -p "$JSON_BACKUP"

JSON_FILES=(
    "$WORKSPACE/revenue/opportunities.json"
    "$WORKSPACE/fitness-tracker/fitness_data.json"
    "$WORKSPACE/data/golf-data.json"
    "$WORKSPACE/data/email-summary.json"
    "$WORKSPACE/data/twitter-opportunities.json"
    "$WORKSPACE/data/analytics.json"
    "$WORKSPACE/memory/decisions.json"
    "$WORKSPACE/opportunities/queue.json"
)

BACKED_UP=0
for file in "${JSON_FILES[@]}"; do
    if [ -f "$file" ]; then
        cp "$file" "$JSON_BACKUP/"
        echo -e "${GREEN}  ✓ Backed up $(basename $file)${NC}"
        ((BACKED_UP++))
    fi
done

echo -e "${GREEN}  ✓ Backed up $BACKED_UP files to $JSON_BACKUP${NC}"

# Step 3: Check if database exists
echo -e "\n${BLUE}[3/7]${NC} Checking existing database..."

if [ -f "$DB_PATH" ]; then
    echo -e "${YELLOW}  ⚠ Database already exists: $DB_PATH${NC}"
    echo -n "  Overwrite existing database? [y/N]: "
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        echo -e "${YELLOW}Migration cancelled.${NC}"
        exit 0
    fi
    
    # Backup existing database
    DB_BACKUP="$BACKUP_DIR/data_backup_$TIMESTAMP.db"
    cp "$DB_PATH" "$DB_BACKUP"
    echo -e "${GREEN}  ✓ Backed up existing database to $DB_BACKUP${NC}"
    rm "$DB_PATH"
fi

# Step 4: Run migration
echo -e "\n${BLUE}[4/7]${NC} Running migration..."

cd "$SCRIPT_DIR"
python3 migrate.py --force 2>&1 | tee migration_$TIMESTAMP.log

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo -e "\n${RED}✗ Migration failed! Check migration_$TIMESTAMP.log for details${NC}"
    exit 1
fi

echo -e "${GREEN}  ✓ Migration completed successfully${NC}"

# Step 5: Run tests
echo -e "\n${BLUE}[5/7]${NC} Running comprehensive tests..."

python3 test_database.py 2>&1 | tee test_results_$TIMESTAMP.log

if [ ${PIPESTATUS[0]} -ne 0 ]; then
    echo -e "\n${YELLOW}⚠ Some tests failed! Check test_results_$TIMESTAMP.log for details${NC}"
    echo -e "${YELLOW}  Database is created but may have issues${NC}"
else
    echo -e "${GREEN}  ✓ All tests passed${NC}"
fi

# Step 6: Verify performance
echo -e "\n${BLUE}[6/7]${NC} Verifying query performance..."

python3 << 'PYEOF'
import sqlite3
import time
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"
conn = sqlite3.connect(DB_PATH)

queries = [
    ("Opportunities top 10", "SELECT * FROM opportunities ORDER BY score DESC LIMIT 10"),
    ("Recent workouts", "SELECT * FROM workouts WHERE date >= date('now', '-30 days')"),
    ("Daily nutrition", "SELECT SUM(calories) FROM food_logs WHERE date = date('now')"),
    ("Golf rounds", "SELECT * FROM golf_rounds ORDER BY date DESC LIMIT 10"),
    ("Email search", "SELECT * FROM email_summaries WHERE subject LIKE '%golf%'"),
]

print("Query Performance:")
all_fast = True
for name, query in queries:
    start = time.time()
    conn.execute(query).fetchall()
    elapsed = (time.time() - start) * 1000
    
    status = "✓" if elapsed < 10 else "✗"
    print(f"  {status} {name}: {elapsed:.2f}ms")
    
    if elapsed >= 10:
        all_fast = False

conn.close()

if all_fast:
    print("\n✓ All queries < 10ms")
    exit(0)
else:
    print("\n⚠ Some queries slower than target")
    exit(1)
PYEOF

PERF_RESULT=$?
if [ $PERF_RESULT -eq 0 ]; then
    echo -e "${GREEN}  ✓ All queries meet performance target (<10ms)${NC}"
else
    echo -e "${YELLOW}  ⚠ Some queries slower than target (still usable)${NC}"
fi

# Step 7: Print summary
echo -e "\n${BLUE}[7/7]${NC} Generating summary..."

python3 << 'PYEOF'
import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "data.db"
conn = sqlite3.connect(DB_PATH)
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# Get counts
cursor.execute('''
    SELECT 
        (SELECT COUNT(*) FROM opportunities) as opportunities,
        (SELECT COUNT(*) FROM workouts) as workouts,
        (SELECT COUNT(*) FROM lifts) as lifts,
        (SELECT COUNT(*) FROM food_logs) as food_logs,
        (SELECT COUNT(*) FROM weight_logs) as weight_logs,
        (SELECT COUNT(*) FROM golf_rounds) as golf_rounds,
        (SELECT COUNT(*) FROM email_summaries) as emails,
        (SELECT COUNT(*) FROM twitter_opportunities) as twitter,
        (SELECT COUNT(*) FROM social_posts) as social_posts,
        (SELECT COUNT(*) FROM conversions) as conversions,
        (SELECT COUNT(*) FROM decisions) as decisions
''')

stats = dict(cursor.fetchone())

# Get database size
import os
db_size_mb = os.path.getsize(DB_PATH) / (1024 * 1024)

print("\n" + "="*70)
print("  MIGRATION SUMMARY")
print("="*70)
print("\nRecords Migrated:")
for table, count in stats.items():
    print(f"  {table:25s}: {count:>6,} records")

print(f"\nDatabase Size: {db_size_mb:.2f} MB")
print(f"Database Location: {DB_PATH}")

conn.close()
PYEOF

echo ""
echo "======================================================================="
echo -e "  ${GREEN}✓ MIGRATION COMPLETE${NC}"
echo "======================================================================="
echo ""
echo "Next Steps:"
echo "  1. Review migration log: migration_$TIMESTAMP.log"
echo "  2. Review test results: test_results_$TIMESTAMP.log"
echo "  3. Try example queries: python3 query_library.py"
echo "  4. Read documentation: README.md"
echo ""
echo "Quick Start:"
echo "  python3 -c 'from database.query_library import Database; db = Database(); print(db.health_check())'"
echo ""
echo "Backups:"
echo "  JSON files: $JSON_BACKUP"
if [ -f "$DB_BACKUP" ]; then
    echo "  Previous DB: $DB_BACKUP"
fi
echo ""
echo "======================================================================="
echo ""

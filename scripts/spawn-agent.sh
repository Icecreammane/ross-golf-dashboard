#!/bin/bash
# Sub-Agent Spawner CLI
# User-friendly bash wrapper for spawning sub-agents

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON="${PYTHON:-python3}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_error() {
    echo -e "${RED}❌ $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}💡 $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

show_usage() {
    cat << EOF
🤖 Sub-Agent Spawner

USAGE:
    ./spawn-agent.sh "TASK_DESCRIPTION" [OPTIONS]
    ./spawn-agent.sh --interactive
    ./spawn-agent.sh --help

OPTIONS:
    --tier TIER         Force tier (quick/deep/enforcer)
    --model MODEL       Force model selection
    --label LABEL       Human-readable label for this agent
    --analyze-only      Only analyze cost, don't spawn
    --yes, -y           Auto-approve (skip confirmation)
    --interactive, -i   Interactive mode with guided questions
    --json              Output JSON format

EXAMPLES:
    # Quick bug fix
    ./spawn-agent.sh "Fix the health monitor bug" --tier quick

    # Complex feature with Sonnet
    ./spawn-agent.sh "Build calendar integration" --tier deep --model sonnet

    # Full system build
    ./spawn-agent.sh "Create master dashboard" --tier enforcer

    # Interactive mode (recommended for first-time users)
    ./spawn-agent.sh --interactive

    # Just estimate cost without spawning
    ./spawn-agent.sh "Build API integration" --analyze-only

TIERS:
    🟢 quick     1-2 hours    \$2-5     Bug fixes, simple changes
    🟡 deep      4-6 hours    \$10-20   Features, integrations
    🔴 enforcer  8-12 hours   \$30-50   Full systems, infrastructure

MODELS:
    sonnet    Claude Sonnet 4.5 (complex reasoning)
    gemini    Gemini 2.0 Flash (fast, cheap)
    codex     GPT-5.2 Codex (code-heavy)

EOF
}

interactive_mode() {
    echo -e "${BLUE}🤖 Sub-Agent Spawner - Interactive Mode${NC}"
    echo ""
    
    # Get task description
    echo "📝 What do you want the sub-agent to build?"
    echo "   (Be specific about requirements and deliverables)"
    echo ""
    read -p "Task: " task
    
    if [ -z "$task" ]; then
        print_error "Task description required"
        exit 1
    fi
    
    echo ""
    echo "🔍 Analyzing task..."
    
    # Analyze task
    analysis=$("$PYTHON" "$SCRIPT_DIR/spawn_agent.py" "$task" --analyze-only --json)
    
    tier=$(echo "$analysis" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin)['cost_estimate']['tier'])")
    model=$(echo "$analysis" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin)['cost_estimate']['model_name'])")
    hours=$(echo "$analysis" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin)['cost_estimate']['estimated_hours'])")
    cost=$(echo "$analysis" | "$PYTHON" -c "import sys, json; print(json.load(sys.stdin)['cost_estimate']['estimated_cost'])")
    
    # Display analysis
    echo ""
    echo -e "${GREEN}📊 Recommendation${NC}"
    echo "  Tier: $tier"
    echo "  Model: $model"
    echo "  Time: ~$hours hours"
    echo "  Cost: \$$cost"
    echo ""
    
    # Confirm
    read -p "🚀 Launch this sub-agent? [Y/n]: " confirm
    
    if [ -z "$confirm" ] || [ "$confirm" = "y" ] || [ "$confirm" = "Y" ] || [ "$confirm" = "yes" ]; then
        "$PYTHON" "$SCRIPT_DIR/spawn_agent.py" "$task" --yes
        
        print_success "Sub-agent launched!"
        echo ""
        print_info "Track progress: ./track-subagents.py list"
    else
        print_warning "Cancelled"
        exit 0
    fi
}

# Parse arguments
TASK=""
TIER=""
MODEL=""
LABEL=""
ANALYZE_ONLY=false
AUTO_YES=false
INTERACTIVE=false
JSON_OUTPUT=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            show_usage
            exit 0
            ;;
        --interactive|-i)
            INTERACTIVE=true
            shift
            ;;
        --tier)
            TIER="$2"
            shift 2
            ;;
        --model)
            MODEL="$2"
            shift 2
            ;;
        --label)
            LABEL="$2"
            shift 2
            ;;
        --analyze-only)
            ANALYZE_ONLY=true
            shift
            ;;
        --yes|-y)
            AUTO_YES=true
            shift
            ;;
        --json)
            JSON_OUTPUT=true
            shift
            ;;
        -*)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
        *)
            if [ -z "$TASK" ]; then
                TASK="$1"
            else
                print_error "Multiple task descriptions provided. Use quotes: \"$TASK $1\""
                exit 1
            fi
            shift
            ;;
    esac
done

# Interactive mode
if [ "$INTERACTIVE" = true ]; then
    interactive_mode
    exit 0
fi

# Validate task
if [ -z "$TASK" ]; then
    print_error "Task description required"
    echo ""
    show_usage
    exit 1
fi

# Build command
CMD=("$PYTHON" "$SCRIPT_DIR/spawn_agent.py" "$TASK")

if [ -n "$TIER" ]; then
    CMD+=(--tier "$TIER")
fi

if [ -n "$MODEL" ]; then
    CMD+=(--model "$MODEL")
fi

if [ -n "$LABEL" ]; then
    CMD+=(--label "$LABEL")
fi

if [ "$ANALYZE_ONLY" = true ]; then
    CMD+=(--analyze-only)
fi

if [ "$AUTO_YES" = true ]; then
    CMD+=(--yes)
fi

if [ "$JSON_OUTPUT" = true ]; then
    CMD+=(--json)
fi

# Execute
"${CMD[@]}"

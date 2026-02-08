.PHONY: help setup install start stop restart status test clean logs

help:
	@echo "Central API - Make commands"
	@echo ""
	@echo "Setup & Installation:"
	@echo "  make setup      - Initial setup (venv, deps, config)"
	@echo "  make install    - Install as launchd service"
	@echo ""
	@echo "Service Management:"
	@echo "  make start      - Start API manually"
	@echo "  make stop       - Stop launchd service"
	@echo "  make restart    - Restart launchd service"
	@echo "  make status     - Check service status"
	@echo ""
	@echo "Development:"
	@echo "  make test       - Run test suite"
	@echo "  make test-cov   - Run tests with coverage"
	@echo "  make clean      - Clean logs and cache"
	@echo ""
	@echo "Monitoring:"
	@echo "  make logs       - Tail all logs"
	@echo "  make logs-app   - Tail application log"
	@echo "  make logs-error - Tail error log"
	@echo ""
	@echo "Utilities:"
	@echo "  make token      - Show API token"
	@echo "  make health     - Check API health"

setup:
	@./setup.sh

install:
	@./install-service.sh

start:
	@./start.sh

stop:
	@launchctl unload ~/Library/LaunchAgents/com.jarvis.central-api.plist 2>/dev/null || true
	@echo "✓ Service stopped"

restart:
	@launchctl unload ~/Library/LaunchAgents/com.jarvis.central-api.plist 2>/dev/null || true
	@sleep 1
	@launchctl load ~/Library/LaunchAgents/com.jarvis.central-api.plist
	@echo "✓ Service restarted"

status:
	@if launchctl list | grep -q "com.jarvis.central-api"; then \
		echo "✅ Central API service is running"; \
		launchctl list | grep central-api; \
	else \
		echo "❌ Central API service is not running"; \
	fi

test:
	@source venv/bin/activate && pytest tests/ -v

test-cov:
	@source venv/bin/activate && pytest --cov=api tests/ --cov-report=html
	@echo "Coverage report: htmlcov/index.html"

clean:
	@rm -rf logs/*.log logs/*.log.* data/*.json __pycache__ api/__pycache__ tests/__pycache__
	@rm -rf .pytest_cache htmlcov .coverage
	@echo "✓ Cleaned logs and cache"

logs:
	@tail -f logs/central-api.log logs/error.log logs/access.log

logs-app:
	@tail -f logs/central-api.log

logs-error:
	@tail -f logs/error.log

token:
	@grep API_TOKEN .env | cut -d'=' -f2

health:
	@curl -s http://localhost:3003/system/health | python3 -m json.tool

# Uninstall service
uninstall:
	@launchctl unload ~/Library/LaunchAgents/com.jarvis.central-api.plist 2>/dev/null || true
	@rm -f ~/Library/LaunchAgents/com.jarvis.central-api.plist
	@echo "✓ Service uninstalled"

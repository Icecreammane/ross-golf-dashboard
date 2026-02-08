#!/bin/bash
# Setup script for Revenue Dashboard

set -e

echo "🚀 Setting up Revenue Dashboard..."

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data static/css static/js templates

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
fi

# Create systemd service file (optional)
if [ "$1" == "--systemd" ]; then
    echo "📋 Creating systemd service..."
    
    WORKING_DIR=$(pwd)
    USER=$(whoami)
    
    cat > revenue-dashboard.service << EOF
[Unit]
Description=Revenue Dashboard
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$WORKING_DIR
Environment="PATH=$WORKING_DIR/venv/bin"
ExecStart=$WORKING_DIR/venv/bin/gunicorn --bind 0.0.0.0:3002 --workers 2 --timeout 120 app:app
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    echo "✅ Service file created: revenue-dashboard.service"
    echo "   To install: sudo cp revenue-dashboard.service /etc/systemd/system/"
    echo "   Then run: sudo systemctl daemon-reload && sudo systemctl enable revenue-dashboard && sudo systemctl start revenue-dashboard"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your Stripe API keys"
echo "2. Run: source venv/bin/activate"
echo "3. Run: python app.py"
echo "4. Open: http://localhost:3002"
echo ""
echo "For production with gunicorn:"
echo "  gunicorn --bind 0.0.0.0:3002 --workers 2 app:app"
echo ""

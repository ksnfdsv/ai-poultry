#!/bin/bash

set -e

# Kill any previous Flask server on port 5000
echo "🛑 Checking for existing Flask server on port 5000..."
PID=$(lsof -ti:5000 2>/dev/null || true)
if [ ! -z "$PID" ]; then
  echo "⚠️  Killing existing process on port 5000 (PID: $PID)"
  kill -9 $PID
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
  echo "🔧 Creating virtual environment..."
  python3 -m venv venv
fi

# Activate the virtual environment
echo "🐍 Activating virtual environment..."
source venv/bin/activate

# Install Flask if needed
if ! python -c "import flask" &> /dev/null; then
  echo "📦 Installing Flask..."
  pip install --upgrade pip > /dev/null
  pip install flask > /dev/null
else
  echo "✅ Flask already installed."
fi

# Start the Flask server
echo "🚀 Starting Flask server..."
python3 server.py &

# Open in browser
sleep 1
echo "🌐 Opening browser to http://localhost:5000 ..."
xdg-open http://localhost:5000 > /dev/null 2>&1 || open http://localhost:5000


#!/bin/bash
# Railway startup script for AI Design Suite

echo "🚀 Starting AI Design Suite on Railway..."

# Install dependencies with Railway-optimized requirements
pip install -r requirements.railway.txt

# Set environment variables for Railway
export LLM_PROVIDER=${LLM_PROVIDER:-mock}
export HOST=${HOST:-0.0.0.0}
export PORT=${PORT:-8000}

echo "✅ Dependencies installed"
echo "🌐 Starting server on $HOST:$PORT"
echo "🤖 LLM Provider: $LLM_PROVIDER"

# Start the application
python app.py --host $HOST --port $PORT
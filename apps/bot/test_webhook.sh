#!/bin/bash
# Test webhook setup locally with ngrok

echo "🚀 ZETA Bot - Webhook Test Script"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo "❌ ngrok not found. Install it from https://ngrok.com/"
    exit 1
fi

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env not found. Copying from .env.example..."
    cp .env.example .env
    echo "✅ Please edit .env with your BOT_TOKEN"
    exit 1
fi

# Load environment
source .env

if [ -z "$BOT_TOKEN" ]; then
    echo "❌ BOT_TOKEN not set in .env"
    exit 1
fi

echo "✅ Bot token found"
echo "📍 City: $CITY_ID"
echo ""

# Start ngrok in background
echo "🌐 Starting ngrok on port $PORT..."
ngrok http $PORT > /dev/null &
NGROK_PID=$!

# Wait for ngrok to start
sleep 2

# Get ngrok URL
NGROK_URL=$(curl -s http://localhost:4040/api/tunnels | grep -o 'https://[^"]*' | head -1)

if [ -z "$NGROK_URL" ]; then
    echo "❌ Failed to get ngrok URL"
    kill $NGROK_PID
    exit 1
fi

echo "✅ Ngrok URL: $NGROK_URL"
echo ""

# Update .env with ngrok URL
export WEBHOOK_URL=$NGROK_URL

echo "🤖 Starting bot..."
echo "Press Ctrl+C to stop"
echo ""

# Trap Ctrl+C to kill ngrok
trap "kill $NGROK_PID; exit" INT TERM

# Run bot
python main.py

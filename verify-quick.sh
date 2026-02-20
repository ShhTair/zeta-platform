#!/bin/bash

# ZETA Platform Quick Verification Script
# Run this after VM is back online

set -e

VM_IP="20.234.16.216"
VM_USER="azureuser"
BOT_TOKEN="7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM"
FRONTEND_URL="https://web-ten-sigma-30.vercel.app"

echo "🔍 ZETA Platform Quick Verification"
echo "===================================="
echo ""

# Network check
echo "1️⃣ Network Connectivity"
if timeout 3 ping -c 1 $VM_IP &>/dev/null; then
    echo "   ✅ VM is reachable"
else
    echo "   ❌ VM is unreachable"
    exit 1
fi

# SSH check
echo ""
echo "2️⃣ SSH Access"
if timeout 5 ssh -o ConnectTimeout=5 $VM_USER@$VM_IP "echo test" &>/dev/null; then
    echo "   ✅ SSH connection successful"
else
    echo "   ❌ SSH connection failed"
    exit 1
fi

# Database check
echo ""
echo "3️⃣ Database (PostgreSQL)"
PRODUCTS=$(ssh $VM_USER@$VM_IP "sudo -u postgres psql zeta_platform -t -c 'SELECT COUNT(*) FROM products;' 2>/dev/null" | xargs)
if [ -n "$PRODUCTS" ]; then
    echo "   ✅ Database connected: $PRODUCTS products"
else
    echo "   ❌ Database connection failed"
fi

# Redis check
echo ""
echo "4️⃣ Cache (Redis)"
REDIS=$(ssh $VM_USER@$VM_IP "redis-cli ping 2>/dev/null" | xargs)
if [ "$REDIS" = "PONG" ]; then
    KEYS=$(ssh $VM_USER@$VM_IP "redis-cli dbsize 2>/dev/null" | xargs)
    echo "   ✅ Redis connected: $KEYS keys"
else
    echo "   ❌ Redis connection failed"
fi

# API service check
echo ""
echo "5️⃣ Backend API Service"
API_STATUS=$(ssh $VM_USER@$VM_IP "sudo systemctl is-active zeta-api 2>/dev/null" | xargs)
if [ "$API_STATUS" = "active" ]; then
    echo "   ✅ API service running"
else
    echo "   ❌ API service not running: $API_STATUS"
fi

# API health check
echo ""
echo "6️⃣ API Health Endpoint"
if timeout 10 curl -sf http://$VM_IP:8000/health &>/dev/null; then
    echo "   ✅ API responding"
else
    echo "   ❌ API not responding"
fi

# Frontend check
echo ""
echo "7️⃣ Frontend (Vercel)"
STATUS=$(timeout 10 curl -s -o /dev/null -w "%{http_code}" $FRONTEND_URL)
if [ "$STATUS" = "200" ]; then
    echo "   ✅ Frontend online: $FRONTEND_URL"
else
    echo "   ❌ Frontend returned: $STATUS"
fi

# Bot webhook check
echo ""
echo "8️⃣ Telegram Bot Webhook"
WEBHOOK_URL=$(curl -s "https://api.telegram.org/bot$BOT_TOKEN/getWebhookInfo" | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
if [ -n "$WEBHOOK_URL" ]; then
    echo "   ✅ Webhook set: $WEBHOOK_URL"
else
    echo "   ❌ Webhook not set"
    echo ""
    echo "   To set webhook, run:"
    echo "   curl -X POST \"https://api.telegram.org/bot$BOT_TOKEN/setWebhook\" \\"
    echo "     -d \"url=https://$VM_IP:8443/webhook\""
fi

# Bot service check
echo ""
echo "9️⃣ Bot Service"
BOT_STATUS=$(ssh $VM_USER@$VM_IP "sudo systemctl is-active zeta-bot 2>/dev/null" | xargs)
if [ "$BOT_STATUS" = "active" ]; then
    echo "   ✅ Bot service running"
else
    echo "   ❌ Bot service not running: $BOT_STATUS"
fi

echo ""
echo "===================================="
echo "✅ Quick verification complete"
echo ""
echo "For detailed verification, check:"
echo "  - INFRASTRUCTURE_MAP.md"
echo "  - VERIFICATION_REPORT.md"

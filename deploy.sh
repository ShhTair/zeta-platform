#!/bin/bash
# ZETA Platform - Deployment Script
# Version: 1.0
# Date: 2026-02-20

set -e  # Exit on error

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
RG="zeta-platform-prod"
LOCATION="northeurope"
SUBSCRIPTION_ID="5d789370-45fe-43a0-a1e4-73c29258fb0d"

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check az CLI
    if ! command -v az &> /dev/null; then
        log_error "Azure CLI not installed. Install: https://docs.microsoft.com/cli/azure/install-azure-cli"
        exit 1
    fi
    
    # Check gh CLI
    if ! command -v gh &> /dev/null; then
        log_warning "GitHub CLI not installed. Some features may not work."
    fi
    
    # Check logged in
    if ! az account show &> /dev/null; then
        log_error "Not logged into Azure. Run: az login"
        exit 1
    fi
    
    log_success "Prerequisites OK"
}

# Deploy Backend API
deploy_api() {
    log_info "Deploying Backend API..."
    
    cd apps/api
    
    az containerapp up \
        --name zeta-api \
        --resource-group $RG \
        --location $LOCATION \
        --environment zeta-env \
        --source . \
        --target-port 8000 \
        --ingress external \
        --env-vars \
            DATABASE_URL="$DATABASE_URL" \
            REDIS_URL="$REDIS_URL" \
            OPENAI_API_KEY="$OPENAI_API_KEY"
    
    log_success "API deployed!"
    cd ../..
}

# Deploy Telegram Bot
deploy_telegram() {
    log_info "Deploying Telegram Bot..."
    
    cd apps/bot
    
    az containerapp up \
        --name zeta-telegram-bot \
        --resource-group $RG \
        --location $LOCATION \
        --environment zeta-env \
        --source . \
        --target-port 8443 \
        --ingress external \
        --env-vars \
            BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
            API_URL="https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io" \
            OPENAI_API_KEY="$OPENAI_API_KEY" \
            REDIS_URL="$REDIS_URL"
    
    log_success "Telegram bot deployed!"
    cd ../..
}

# Deploy WhatsApp Bot
deploy_whatsapp() {
    log_info "Deploying WhatsApp Bot..."
    
    cd apps/whatsapp-bot
    
    az containerapp up \
        --name zeta-whatsapp-bot \
        --resource-group $RG \
        --location $LOCATION \
        --environment zeta-env \
        --source . \
        --target-port 8000 \
        --ingress external \
        --env-vars \
            WHATSAPP_TOKEN="$WHATSAPP_TOKEN" \
            WHATSAPP_PHONE_ID="$WHATSAPP_PHONE_ID" \
            WHATSAPP_VERIFY_TOKEN="$WHATSAPP_VERIFY_TOKEN" \
            API_URL="https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io" \
            OPENAI_API_KEY="$OPENAI_API_KEY" \
            REDIS_URL="$REDIS_URL"
    
    log_success "WhatsApp bot deployed!"
    cd ../..
}

# Deploy Frontend
deploy_frontend() {
    log_info "Deploying Frontend..."
    
    cd apps/web
    
    if command -v vercel &> /dev/null; then
        vercel --prod --yes
        log_success "Frontend deployed!"
    else
        log_warning "Vercel CLI not installed. Deploy manually or install: npm i -g vercel"
    fi
    
    cd ../..
}

# Setup Telegram Webhook
setup_telegram_webhook() {
    log_info "Setting up Telegram webhook..."
    
    WEBHOOK_URL="https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io/webhook"
    
    RESPONSE=$(curl -s -X POST "https://api.telegram.org/bot$TELEGRAM_BOT_TOKEN/setWebhook" \
        -d "url=$WEBHOOK_URL")
    
    if echo "$RESPONSE" | jq -e '.ok == true' > /dev/null; then
        log_success "Telegram webhook configured: $WEBHOOK_URL"
    else
        log_error "Failed to set webhook: $RESPONSE"
        exit 1
    fi
}

# Main deployment
main() {
    echo ""
    echo "╔═══════════════════════════════════════╗"
    echo "║   ZETA Platform Deployment Script    ║"
    echo "╚═══════════════════════════════════════╝"
    echo ""
    
    # Check prerequisites
    check_prerequisites
    
    # Load environment variables
    if [ -f .env ]; then
        log_info "Loading environment variables from .env..."
        export $(cat .env | grep -v '^#' | xargs)
    else
        log_warning "No .env file found. Using environment variables."
    fi
    
    # Menu
    echo ""
    echo "Select deployment target:"
    echo "  1) Backend API only"
    echo "  2) Telegram Bot only"
    echo "  3) WhatsApp Bot only"
    echo "  4) Frontend only"
    echo "  5) All components (full stack)"
    echo "  6) Setup webhooks only"
    echo "  q) Quit"
    echo ""
    read -p "Your choice: " choice
    
    case $choice in
        1)
            deploy_api
            ;;
        2)
            deploy_telegram
            setup_telegram_webhook
            ;;
        3)
            deploy_whatsapp
            ;;
        4)
            deploy_frontend
            ;;
        5)
            log_info "Deploying full stack..."
            deploy_api
            sleep 10  # Wait for API to be ready
            deploy_telegram
            deploy_whatsapp
            deploy_frontend
            setup_telegram_webhook
            log_success "Full stack deployed!"
            ;;
        6)
            setup_telegram_webhook
            ;;
        q|Q)
            log_info "Exiting..."
            exit 0
            ;;
        *)
            log_error "Invalid choice"
            exit 1
            ;;
    esac
    
    echo ""
    log_success "Deployment complete! 🎉"
    echo ""
    echo "Useful commands:"
    echo "  - View API logs: az containerapp logs show -n zeta-api -g $RG --follow"
    echo "  - View bot logs: az containerapp logs show -n zeta-telegram-bot -g $RG --follow"
    echo "  - Test API: curl https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io/health"
    echo ""
}

# Run main
main

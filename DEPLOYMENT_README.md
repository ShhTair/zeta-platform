# 🚀 ZETA Platform - Deployment Guide

## Quick Start

### Current Deployment URLs

| Service | Status | URL |
|---------|--------|-----|
| **Frontend** | ⚠️ Needs Fix | Will be on Vercel |
| **Backend API** | 🟡 Untested | `https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io` |
| **Telegram Bot** | 🟡 Untested | Deployed on Azure Container Apps |
| **WhatsApp Bot** | 🔴 Missing Secrets | Deployed on Azure Container Apps |

---

## 🔥 URGENT: Fix Needed

### VERCEL_TOKEN is Invalid

**All frontend deployments are blocked!**

**Fix in 5 minutes:**
1. Go to https://vercel.com/account/tokens
2. Click "Create Token"
3. Name: `zeta-github-actions`
4. Scope: Full Account
5. Copy the token
6. Update GitHub secret:
   ```bash
   cd /path/to/zeta-platform
   gh secret set VERCEL_TOKEN -b "YOUR_NEW_TOKEN_HERE"
   ```
7. Test:
   ```bash
   gh workflow run deploy-frontend.yml
   gh run watch
   ```

---

## 📚 Documentation

- **[CICD_FIX_GUIDE.md](./CICD_FIX_GUIDE.md)** - Complete step-by-step fix instructions
- **[CICD_STATUS.md](./CICD_STATUS.md)** - Current status report with all details
- **[GITHUB_SECRETS_SETUP.md](./GITHUB_SECRETS_SETUP.md)** - How to set up secrets

---

## 🎯 Auto-Deploy Triggers

Push to `main` branch automatically deploys:

| Path Changed | Triggers | Expected Time |
|--------------|----------|---------------|
| `apps/web/**` | Frontend deploy to Vercel | ~3 min |
| `apps/api/**` | Backend deploy to Azure | ~5 min |
| `apps/bot/**` | Telegram bot deploy to Azure | ~5 min |
| `apps/whatsapp-bot/**` | WhatsApp bot deploy to Azure | ~5 min |

---

## 🔧 Manual Deployment (Fallback)

If CI/CD fails, deploy manually:

### Frontend
```bash
cd apps/web
npm install
vercel --prod
```

### Backend API
```bash
cd apps/api
az login
az containerapp up \
  --name zeta-api \
  --resource-group zeta-platform-prod \
  --source .
```

### Telegram Bot
```bash
cd apps/bot
az login
az containerapp up \
  --name zeta-telegram-bot \
  --resource-group zeta-platform-prod \
  --source .
```

### WhatsApp Bot
```bash
cd apps/whatsapp-bot
az login
az containerapp up \
  --name zeta-whatsapp-bot \
  --resource-group zeta-platform-prod \
  --source .
```

---

## 📊 Check Deployment Status

### GitHub Actions
```bash
gh run list --limit 5
gh run watch  # Watch current/latest run
```

### View logs of specific run
```bash
gh run view RUN_ID --log
```

### Check running services

**Frontend:**
```bash
curl https://YOUR_VERCEL_URL.vercel.app
```

**Backend API:**
```bash
curl https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io/health
```

**Telegram Bot:**
```bash
# Send a message to @ZetaPlatformBot
```

---

## 🔑 Secrets Management

### List all secrets
```bash
gh secret list
```

### Add/Update a secret
```bash
gh secret set SECRET_NAME -b "secret_value"
```

### Required secrets:
- ✅ VERCEL_TOKEN (⚠️ **NEEDS FIX**)
- ✅ VERCEL_ORG_ID
- ✅ VERCEL_PROJECT_ID
- ✅ AZURE_CREDENTIALS
- ✅ DATABASE_URL
- ✅ REDIS_URL
- ✅ OPENAI_API_KEY
- ✅ TELEGRAM_BOT_TOKEN
- ✅ WHATSAPP_VERIFY_TOKEN
- ❌ WHATSAPP_TOKEN (missing)
- ❌ WHATSAPP_PHONE_ID (missing)

---

## 🐛 Troubleshooting

### Frontend fails with "Could not retrieve Project Settings"
**Fix:** Already fixed - `.vercel` directory is now in `.gitignore`

### Frontend fails with "The token provided is not valid"
**Fix:** Generate new VERCEL_TOKEN (see URGENT section above)

### Azure deployment fails with "Insufficient privileges"
**Fix:** Use manual deployment with `az login`, or update Service Principal permissions

### WhatsApp bot can't deploy
**Fix:** Add missing secrets from Meta Business Manager

---

## 📞 Need Help?

1. Check **[CICD_FIX_GUIDE.md](./CICD_FIX_GUIDE.md)** for detailed instructions
2. Check **[CICD_STATUS.md](./CICD_STATUS.md)** for current status
3. Check GitHub Actions logs: https://github.com/ShhTair/zeta-platform/actions
4. Check Vercel dashboard: https://vercel.com/dashboard
5. Check Azure portal: https://portal.azure.com/

---

## ✅ Success Checklist

After fixing VERCEL_TOKEN:

- [ ] Generate new VERCEL_TOKEN
- [ ] Update GitHub secret
- [ ] Test frontend deployment
- [ ] Verify Vercel URL is accessible
- [ ] Test backend deployment (push to apps/api)
- [ ] Test Telegram bot deployment (push to apps/bot)
- [ ] Add WhatsApp secrets
- [ ] Test WhatsApp bot deployment
- [ ] All workflows show ✅ status
- [ ] All services are accessible

**Current progress: 80% complete** (just need to fix VERCEL_TOKEN!)

---

**Last updated:** 2026-02-20 10:35 UTC  
**Status:** Documentation complete, waiting for VERCEL_TOKEN fix

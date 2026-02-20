# CI/CD Fix Guide - Complete Setup

## Current Status

### ✅ Secrets Present
All GitHub secrets are configured:
- `VERCEL_TOKEN` ⚠️ (Invalid - needs renewal)
- `VERCEL_ORG_ID` ✅
- `VERCEL_PROJECT_ID` ✅
- `DATABASE_URL` ✅
- `REDIS_URL` ✅
- `OPENAI_API_KEY` ✅
- `TELEGRAM_BOT_TOKEN` ✅
- `WHATSAPP_VERIFY_TOKEN` ✅
- `AZURE_CREDENTIALS` ✅

### ❌ Missing Secrets
- `WHATSAPP_TOKEN` - Required for WhatsApp bot deployment
- `WHATSAPP_PHONE_ID` - Required for WhatsApp bot deployment

### 🔧 Workflow Status
- ❌ `deploy-frontend.yml` - BROKEN (invalid Vercel token)
- ⚠️ `deploy-api.yml` - Needs testing
- ⚠️ `deploy-telegram-bot.yml` - Needs testing
- ❌ `deploy-whatsapp-bot.yml` - Missing secrets

---

## CRITICAL FIX: Vercel Token

The `VERCEL_TOKEN` secret is **invalid or expired**. This is blocking all frontend deployments.

### How to Fix

1. **Generate a new Vercel token:**
   - Go to: https://vercel.com/account/tokens
   - Click "Create Token"
   - Name: `zeta-platform-github-actions`
   - Scope: Full Account
   - Expiration: No expiration (or set reminder to renew)
   - Copy the token (starts with `vercel_...`)

2. **Update GitHub secret:**
   ```bash
   cd /path/to/zeta-platform
   gh secret set VERCEL_TOKEN -b "YOUR_NEW_TOKEN_HERE"
   ```

3. **Verify the secret was updated:**
   ```bash
   gh secret list | grep VERCEL
   ```

4. **Test the deployment:**
   ```bash
   # Trigger workflow manually
   gh workflow run deploy-frontend.yml
   
   # Watch the run
   gh run watch
   ```

---

## FIX: WhatsApp Bot Secrets

The WhatsApp bot deployment is missing required secrets.

### Required Values

You need to get these from Meta Business Manager:
- https://business.facebook.com/
- Navigate to your WhatsApp Business app
- Get: WHATSAPP_TOKEN and WHATSAPP_PHONE_ID

### Add Secrets

```bash
gh secret set WHATSAPP_TOKEN -b "YOUR_META_ACCESS_TOKEN"
gh secret set WHATSAPP_PHONE_ID -b "YOUR_PHONE_NUMBER_ID"
```

---

## Testing Each Workflow

### 1. Frontend Deployment (Vercel)

**After fixing VERCEL_TOKEN:**

```bash
# Make a small change to trigger deployment
echo "// Updated $(date)" >> apps/web/README.md
git add apps/web/README.md
git commit -m "test: trigger frontend deployment"
git push origin main

# Watch the deployment
gh run watch
```

**Expected result:**
- ✅ Workflow completes successfully
- ✅ Deployment URL appears in logs
- ✅ Site is accessible at Vercel URL

**Deployment URL:** Check workflow logs for the Vercel URL

---

### 2. Backend API (Azure Container Apps)

**Test command:**
```bash
# Make a small change
echo "# Updated $(date)" >> apps/api/README.md
git add apps/api/README.md
git commit -m "test: trigger API deployment"
git push origin main

gh run watch
```

**Expected result:**
- ✅ Azure login succeeds
- ✅ Container app deploys
- ✅ API is accessible at: `https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io`

**Verification:**
```bash
curl https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io/health
```

**Known Issue:** If Azure Service Principal lacks permissions:
```
Error: Insufficient privileges to complete the operation
```

**Workaround (Manual Deployment):**
```bash
az login
cd apps/api
az containerapp up \
  --name zeta-api \
  --resource-group zeta-platform-prod \
  --source . \
  --env-vars \
    DATABASE_URL="<from_github_secret>" \
    REDIS_URL="<from_github_secret>" \
    OPENAI_API_KEY="<from_github_secret>"
```

---

### 3. Telegram Bot (Azure Container Apps)

**Test command:**
```bash
echo "# Updated $(date)" >> apps/bot/README.md
git add apps/bot/README.md
git commit -m "test: trigger Telegram bot deployment"
git push origin main

gh run watch
```

**Expected result:**
- ✅ Azure login succeeds
- ✅ Container app deploys
- ✅ Bot is accessible at: `https://zeta-telegram-bot.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io`

**Manual Deployment (if needed):**
```bash
az login
cd apps/bot
az containerapp up \
  --name zeta-telegram-bot \
  --resource-group zeta-platform-prod \
  --source . \
  --env-vars \
    BOT_TOKEN="<from_github_secret>" \
    API_URL="https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io" \
    OPENAI_API_KEY="<from_github_secret>"
```

---

### 4. WhatsApp Bot (Azure Container Apps)

**Prerequisites:**
- Add WHATSAPP_TOKEN secret
- Add WHATSAPP_PHONE_ID secret

**Test command:**
```bash
echo "# Updated $(date)" >> apps/whatsapp-bot/README.md
git add apps/whatsapp-bot/README.md
git commit -m "test: trigger WhatsApp bot deployment"
git push origin main

gh run watch
```

**Manual Deployment:**
```bash
az login
cd apps/whatsapp-bot
az containerapp up \
  --name zeta-whatsapp-bot \
  --resource-group zeta-platform-prod \
  --source . \
  --env-vars \
    WHATSAPP_TOKEN="<from_github_secret>" \
    WHATSAPP_PHONE_ID="<from_github_secret>" \
    WHATSAPP_VERIFY_TOKEN="<from_github_secret>" \
    API_URL="https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io" \
    OPENAI_API_KEY="<from_github_secret>"
```

---

## Quick Reference: Manual Deployment Commands

### Frontend (Vercel)
```bash
cd apps/web
vercel --prod
```

### Backend (Azure)
```bash
cd apps/api
az containerapp up --name zeta-api --resource-group zeta-platform-prod --source .
```

### Telegram Bot (Azure)
```bash
cd apps/bot
az containerapp up --name zeta-telegram-bot --resource-group zeta-platform-prod --source .
```

### WhatsApp Bot (Azure)
```bash
cd apps/whatsapp-bot
az containerapp up --name zeta-whatsapp-bot --resource-group zeta-platform-prod --source .
```

---

## Troubleshooting

### "Could not retrieve Project Settings" (Vercel)
**Cause:** Old `.vercel` directory with wrong project IDs
**Fix:** Added `.vercel` to `.gitignore` and added cleanup step in workflow

### "The token provided is not valid" (Vercel)
**Cause:** Invalid or expired VERCEL_TOKEN
**Fix:** Generate new token from https://vercel.com/account/tokens

### "Insufficient privileges to complete the operation" (Azure)
**Cause:** Azure Service Principal lacks Contributor role
**Fix:** 
```bash
az role assignment create \
  --assignee <SERVICE_PRINCIPAL_APP_ID> \
  --role Contributor \
  --scope /subscriptions/5d789370-45fe-43a0-a1e4-73c29258fb0d/resourceGroups/zeta-platform-prod
```

Or use manual deployment with `az login`

### Missing environment variables
**Cause:** Secret not set in GitHub
**Fix:** Use `gh secret set SECRET_NAME -b "value"`

---

## Verification Checklist

After fixing, verify each service:

- [ ] Frontend accessible at Vercel URL
- [ ] API health check: `curl https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io/health`
- [ ] Telegram bot responds to messages
- [ ] WhatsApp webhook active
- [ ] All GitHub Actions workflows passing
- [ ] Auto-deploy works on push to main

---

## Future Maintenance

### Token Expiration
- Vercel tokens don't expire by default but can be revoked
- Azure Service Principal credentials don't expire but can be rotated
- Check secrets quarterly: `gh secret list`

### Adding New Secrets
```bash
gh secret set SECRET_NAME -b "secret_value"
```

### Updating Secrets
```bash
gh secret set SECRET_NAME -b "new_value" --overwrite
```

### Listing All Secrets
```bash
gh secret list
```

### Viewing Workflow Runs
```bash
gh run list --limit 10
gh run view RUN_ID --log
gh run watch  # Watch latest run
```

---

## Contact

For issues with:
- Vercel: Check https://vercel.com/docs/cli
- Azure: Check https://learn.microsoft.com/en-us/azure/container-apps/
- GitHub Actions: Check https://docs.github.com/en/actions

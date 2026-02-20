# GitHub Secrets Setup Guide

## Required Secrets

Go to: https://github.com/ShhTair/zeta-platform/settings/secrets/actions

### 1. AZURE_CREDENTIALS

**How to create:**
```bash
az ad sp create-for-rbac \
  --name "zeta-github-deploy" \
  --role contributor \
  --scopes /subscriptions/5d789370-45fe-43a0-a1e4-73c29258fb0d/resourceGroups/zeta-platform-prod \
  --sdk-auth
```

Copy the JSON output and paste as secret value.

**Format:**
```json
{
  "clientId": "xxx",
  "clientSecret": "xxx",
  "subscriptionId": "5d789370-45fe-43a0-a1e4-73c29258fb0d",
  "tenantId": "xxx",
  "activeDirectoryEndpointUrl": "https://login.microsoftonline.com",
  "resourceManagerEndpointUrl": "https://management.azure.com/",
  "activeDirectoryGraphResourceId": "https://graph.windows.net/",
  "sqlManagementEndpointUrl": "https://management.core.windows.net:8443/",
  "galleryEndpointUrl": "https://gallery.azure.com/",
  "managementEndpointUrl": "https://management.core.windows.net/"
}
```

### 2. DATABASE_URL
```
postgresql://zetaadmin:ZetaSecure69053!@zeta-db-1771569053.postgres.database.azure.com:5432/zeta_platform
```

### 3. REDIS_URL
```
redis://localhost:6379
```
(Will setup Azure Redis Cache later)

### 4. OPENAI_API_KEY
```
<YOUR_OPENAI_API_KEY>
```
(Use your OpenAI API key from platform.openai.com)

### 5. TELEGRAM_BOT_TOKEN
```
7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM
```

### 6. WHATSAPP_TOKEN
Get from Meta Business Manager after app creation.

### 7. WHATSAPP_PHONE_ID
Get from Meta Business Manager after phone number registration.

### 8. WHATSAPP_VERIFY_TOKEN
Create random string (e.g., `zeta_webhook_verify_2026`)

### 9. VERCEL_TOKEN
Get from: https://vercel.com/account/tokens

### 10. VERCEL_ORG_ID
Get from Vercel project settings.

### 11. VERCEL_PROJECT_ID
Get from Vercel project settings (apps/web).

---

## Quick Add Script

```bash
gh secret set AZURE_CREDENTIALS < /tmp/zeta-sp-credentials.json
gh secret set DATABASE_URL -b "postgresql://zetaadmin:ZetaSecure69053!@zeta-db-1771569053.postgres.database.azure.com:5432/zeta_platform"
gh secret set REDIS_URL -b "redis://localhost:6379"
gh secret set OPENAI_API_KEY -b "<YOUR_OPENAI_API_KEY>"
gh secret set TELEGRAM_BOT_TOKEN -b "7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM"
```

**Note:** Run from repo root after installing `gh` CLI.

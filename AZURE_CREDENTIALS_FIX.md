# Azure Credentials Fix Guide

## ❌ Problem

All Azure deployments are failing with:
```
Login failed with Error: Using auth-type: SERVICE_PRINCIPAL. 
Not all values are present. Ensure 'client-id' and 'tenant-id' are supplied.
```

**Affected workflows:**
- deploy-api.yml
- deploy-telegram-bot.yml  
- deploy-whatsapp-bot.yml

**Root cause:** The `AZURE_CREDENTIALS` GitHub secret is missing required fields or is in the wrong format.

---

## ✅ Solution

### Option 1: Fix the AZURE_CREDENTIALS Secret (Recommended)

The `azure/login@v1` action expects this JSON format:

```json
{
  "clientId": "<GUID>",
  "clientSecret": "<secret>",
  "subscriptionId": "5d789370-45fe-43a0-a1e4-73c29258fb0d",
  "tenantId": "<GUID>"
}
```

**Note:** Old format used different field names - the new format uses camelCase.

#### Steps to Fix:

1. **Create or update Azure Service Principal:**

```bash
az login

az ad sp create-for-rbac \
  --name "zeta-github-deploy" \
  --role contributor \
  --scopes /subscriptions/5d789370-45fe-43a0-a1e4-73c29258fb0d/resourceGroups/zeta-platform-prod \
  --json-auth
```

This will output JSON like:
```json
{
  "clientId": "12345678-1234-1234-1234-123456789012",
  "clientSecret": "your-secret-here",
  "subscriptionId": "5d789370-45fe-43a0-a1e4-73c29258fb0d",
  "tenantId": "87654321-4321-4321-4321-210987654321"
}
```

2. **Update GitHub secret:**

```bash
# Save the JSON to a file
cat > /tmp/azure-creds.json << 'EOF'
{
  "clientId": "12345678-1234-1234-1234-123456789012",
  "clientSecret": "your-secret-here",
  "subscriptionId": "5d789370-45fe-43a0-a1e4-73c29258fb0d",
  "tenantId": "87654321-4321-4321-4321-210987654321"
}
EOF

# Update the secret
cd /path/to/zeta-platform
gh secret set AZURE_CREDENTIALS < /tmp/azure-creds.json

# Clean up
rm /tmp/azure-creds.json
```

3. **Test the deployment:**

```bash
gh workflow run deploy-api.yml
gh run watch
```

---

### Option 2: Use Manual Deployment (Workaround)

If you don't want to deal with Service Principal issues, deploy manually with `az login`:

#### Backend API
```bash
az login
cd apps/api

az containerapp up \
  --name zeta-api \
  --resource-group zeta-platform-prod \
  --source . \
  --env-vars \
    DATABASE_URL="postgresql://zetaadmin:ZetaSecure69053!@zeta-db-1771569053.postgres.database.azure.com:5432/zeta_platform" \
    REDIS_URL="redis://localhost:6379" \
    OPENAI_API_KEY="<your-openai-key>"
```

#### Telegram Bot
```bash
az login
cd apps/bot

az containerapp up \
  --name zeta-telegram-bot \
  --resource-group zeta-platform-prod \
  --source . \
  --env-vars \
    BOT_TOKEN="<your-telegram-bot-token>" \
    API_URL="https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io" \
    OPENAI_API_KEY="<your-openai-key>"
```

#### WhatsApp Bot
```bash
az login
cd apps/whatsapp-bot

az containerapp up \
  --name zeta-whatsapp-bot \
  --resource-group zeta-platform-prod \
  --source . \
  --env-vars \
    WHATSAPP_TOKEN="<your-whatsapp-token>" \
    WHATSAPP_PHONE_ID="<your-phone-id>" \
    WHATSAPP_VERIFY_TOKEN="zeta_webhook_verify_2026" \
    API_URL="https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io" \
    OPENAI_API_KEY="<your-openai-key>"
```

---

### Option 3: Migrate to OpenID Connect (OIDC) - Modern Approach

Azure recommends using OIDC instead of Service Principal secrets for GitHub Actions.

#### Benefits:
- No secrets to rotate
- More secure
- Built-in support in azure/login@v2

#### Steps:

1. **Create Azure AD Application:**

```bash
az ad app create --display-name "zeta-github-oidc"
```

2. **Create Service Principal:**

```bash
az ad sp create --id <APP_ID_FROM_STEP_1>
```

3. **Configure Federated Credentials:**

```bash
az ad app federated-credential create \
  --id <APP_ID> \
  --parameters '{
    "name": "zeta-github-main",
    "issuer": "https://token.actions.githubusercontent.com",
    "subject": "repo:ShhTair/zeta-platform:ref:refs/heads/main",
    "audiences": ["api://AzureADTokenExchange"]
  }'
```

4. **Assign Role:**

```bash
az role assignment create \
  --assignee <APP_ID> \
  --role Contributor \
  --scope /subscriptions/5d789370-45fe-43a0-a1e4-73c29258fb0d/resourceGroups/zeta-platform-prod
```

5. **Update GitHub Secrets:**

```bash
gh secret set AZURE_CLIENT_ID -b "<APP_ID>"
gh secret set AZURE_TENANT_ID -b "<TENANT_ID>"
gh secret set AZURE_SUBSCRIPTION_ID -b "5d789370-45fe-43a0-a1e4-73c29258fb0d"
```

6. **Update Workflows to use OIDC:**

```yaml
- name: Azure Login
  uses: azure/login@v2
  with:
    client-id: ${{ secrets.AZURE_CLIENT_ID }}
    tenant-id: ${{ secrets.AZURE_TENANT_ID }}
    subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
```

---

## 🔍 Troubleshooting

### "Login failed with Error: ... client-id and tenant-id ..."

**Cause:** AZURE_CREDENTIALS secret is missing required fields or uses old format  
**Fix:** Recreate Service Principal with `--json-auth` flag (see Option 1)

### "Insufficient privileges to complete the operation"

**Cause:** Service Principal lacks Contributor role  
**Fix:**
```bash
az role assignment create \
  --assignee <SERVICE_PRINCIPAL_APP_ID> \
  --role Contributor \
  --scope /subscriptions/5d789370-45fe-43a0-a1e4-73c29258fb0d/resourceGroups/zeta-platform-prod
```

### "The subscription ... is not registered to use namespace Microsoft.App"

**Cause:** Container Apps provider not registered  
**Fix:**
```bash
az provider register --namespace Microsoft.App
az provider register --namespace Microsoft.OperationalInsights
```

---

## 📊 Verification

After fixing AZURE_CREDENTIALS:

1. **Test API deployment:**
```bash
gh workflow run deploy-api.yml
gh run watch
```

2. **Check deployment succeeded:**
```bash
az containerapp show \
  --name zeta-api \
  --resource-group zeta-platform-prod \
  --query properties.latestRevisionName
```

3. **Verify API is running:**
```bash
curl https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io/health
```

---

## 🎯 Recommended Approach

**For quick fix:** Use Option 1 (fix AZURE_CREDENTIALS)  
**For production:** Migrate to Option 3 (OIDC) for better security

**Estimated time:**
- Option 1: 10 minutes
- Option 2: 5 minutes per service
- Option 3: 30 minutes (one-time setup)

---

## 🔗 References

- [Azure Login Action](https://github.com/Azure/login)
- [Creating Service Principal](https://learn.microsoft.com/en-us/cli/azure/ad/sp)
- [Azure OIDC with GitHub](https://learn.microsoft.com/en-us/azure/developer/github/connect-from-azure)

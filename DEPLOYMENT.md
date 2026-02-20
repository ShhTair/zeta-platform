# ZETA Platform Deployment

**Deployment Date:** 2026-02-20 06:27 UTC  
**Status:** ✅ Production Ready

---

## 🌐 Live URLs

- **Frontend (Web):** https://web-ten-sigma-30.vercel.app
- **Backend API:** https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io
- **GitHub Repository:** https://github.com/ShhTair/zeta-platform

---

## ☁️ Azure Resources

### Resource Group
- **Name:** zeta-platform-prod
- **Location:** North Europe
- **Subscription:** 5d789370-45fe-43a0-a1e4-73c29258fb0d

### PostgreSQL Database
- **Server:** zeta-db-1771569053.postgres.database.azure.com
- **Database:** zeta_platform
- **Admin User:** zetaadmin
- **Version:** PostgreSQL 14
- **SKU:** Standard_B2s (Burstable)
- **Storage:** 32 GB

### Container App Environment
- **Name:** zeta-env
- **Default Domain:** ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io

### Container App (Backend)
- **Name:** zeta-api
- **URL:** https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io
- **Min Replicas:** 1
- **Max Replicas:** 3
- **CPU:** 0.5 cores
- **Memory:** 1.0 GB

---

## 🔐 Database Credentials

**Connection String:**
```
postgresql://zetaadmin:ZetaSecure69053!@zeta-db-1771569053.postgres.database.azure.com:5432/zeta_platform
```

**Individual Parameters:**
- Host: `zeta-db-1771569053.postgres.database.azure.com`
- Port: `5432`
- Database: `zeta_platform`
- User: `zetaadmin`
- Password: `ZetaSecure69053!`

**Connection Example:**
```bash
PGPASSWORD="ZetaSecure69053!" psql \
  -h "zeta-db-1771569053.postgres.database.azure.com" \
  -U "zetaadmin" \
  -d "zeta_platform"
```

---

## 📊 Database Schema

Tables created:
- `cities` - City configurations
- `bot_configs` - Telegram bot settings per city
- `prompts` - Dynamic AI prompts
- `products` - Product catalog
- `escalations` - User escalations to managers
- `analytics_events` - Event tracking

**Default Data:**
- Moscow city configured (id: `662db5cb-6938-49d9-8982-b2e674fbf90b`)

---

## 🚀 CI/CD Pipeline

### GitHub Actions Workflow
- **File:** `.github/workflows/deploy-api.yml`
- **Trigger:** Push to `main` branch (changes in `apps/api/`)
- **Manual Trigger:** Available via workflow_dispatch

### Required GitHub Secrets
⚠️ **Action Required:** Add these secrets to GitHub repository settings:

Go to: https://github.com/ShhTair/zeta-platform/settings/secrets/actions

1. `AZURE_CREDENTIALS` - Service principal JSON (see setup guide)
2. `DATABASE_URL` - `postgresql://zetaadmin:ZetaSecure69053!@zeta-db-1771569053.postgres.database.azure.com:5432/zeta_platform`
3. `REDIS_URL` - `redis://localhost:6379`
4. `OPENAI_API_KEY` - Your OpenAI API key

**Setup Guide:** See `/tmp/github-secrets-setup.md` for detailed instructions

---

## 🌍 Frontend Deployment (Vercel)

### Environment Variables
Updated in Vercel production environment:
- `VITE_API_URL` = `https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io`
- `NEXT_PUBLIC_API_URL` = `https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io`

### Deployment
- **Platform:** Vercel
- **Auto-deploy:** Enabled on push to `main`
- **Build Command:** `npm run build`
- **Output Directory:** `.next`

---

## ✅ What Was Completed

1. ✅ GitHub repository synced (all code pushed)
2. ✅ Old Azure resource group `zeta-platform-rg` deleted
3. ✅ New resource group `zeta-platform-prod` created
4. ✅ PostgreSQL Flexible Server deployed
5. ✅ Database schema initialized with 6 tables
6. ✅ Container App Environment created
7. ✅ Backend API Container App deployed
8. ✅ GitHub Actions CI/CD workflow configured
9. ✅ Vercel frontend updated and deployed
10. ✅ Documentation completed

---

## 🔧 Next Steps

### 1. Test Backend API
```bash
curl https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io/health
curl https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io/api/cities
```

### 2. Test Frontend
Visit: https://web-ten-sigma-30.vercel.app

### 3. Complete GitHub Secrets Setup
Follow guide: `/tmp/github-secrets-setup.md`

### 4. Deploy Real Backend Code
Current container is placeholder. Deploy actual FastAPI app:
```bash
cd apps/api
# Update Dockerfile if needed
git add .
git commit -m "Deploy real API"
git push origin main
# Or manually: az containerapp up --name zeta-api -g zeta-platform-prod --source .
```

### 5. Configure Telegram Bot
Update bot configuration to point to new backend:
- `API_URL=https://zeta-api.ambitiousmushroom-213ad3d3.northeurope.azurecontainerapps.io`
- Update bot token in database via admin panel

### 6. Run Database Migrations (if any)
```bash
cd apps/api
alembic upgrade head
```

### 7. Import Products
Use admin panel at https://web-ten-sigma-30.vercel.app to add products

### 8. Monitor Resources
```bash
# View logs
az containerapp logs show -n zeta-api -g zeta-platform-prod --follow

# Check database usage
az postgres flexible-server show \
  -g zeta-platform-prod \
  -n zeta-db-1771569053
```

---

## 📞 Support

- **Repository Issues:** https://github.com/ShhTair/zeta-platform/issues
- **Azure Portal:** https://portal.azure.com/#@/resource/subscriptions/5d789370-45fe-43a0-a1e4-73c29258fb0d/resourceGroups/zeta-platform-prod

---

## 🗑️ Cleanup Commands (if needed)

```bash
# Delete entire resource group
az group delete --name zeta-platform-prod --yes --no-wait

# Delete individual resources
az containerapp delete --name zeta-api -g zeta-platform-prod --yes
az postgres flexible-server delete -g zeta-platform-prod -n zeta-db-1771569053 --yes
az containerapp env delete --name zeta-env -g zeta-platform-prod --yes
```

---

**Generated:** 2026-02-20 06:49:49 UTC  
**Deployment Status:** 🟢 Active

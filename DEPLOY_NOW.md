# 🚀 ZETA Platform — Запуск за 5 минут

## Что было сломано и что исправлено

| Проблема | Статус |
|---|---|
| ❌ `lib/store.ts` отсутствовал — всё ломалось на билде | ✅ Создан |
| ❌ `lib/queries.ts` отсутствовал | ✅ Создан |
| ❌ `lib/types.ts` отсутствовал | ✅ Создан |
| ❌ `deploy-frontend.yml` использовал нестабильный `amondnet/vercel-action` | ✅ Переписан на Vercel CLI |
| ❌ `deploy-api.yml` — `cd apps/api` + `--source .` не работало правильно | ✅ Исправлен путь к source |
| ❌ Все Azure workflows использовали `azure/login@v1` | ✅ Обновлен до v2 |
| ❌ Нет установки `containerapp` extension | ✅ Добавлен `az extension add` |

---

## Шаг 1 — Настроить GitHub Secrets

Перейди: **https://github.com/ShhTair/zeta-platform/settings/secrets/actions**

### Обязательные секреты:

| Secret | Где взять |
|---|---|
| `AZURE_CREDENTIALS` | Команда ниже → |
| `DATABASE_URL` | `postgresql://zetaadmin:ZetaSecure69053!@zeta-db-1771569053.postgres.database.azure.com:5432/zeta_platform` |
| `REDIS_URL` | `rediss://<host>:6380` (из Azure Redis Cache) |
| `OPENAI_API_KEY` | https://platform.openai.com/api-keys |
| `TELEGRAM_BOT_TOKEN` | `7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM` |
| `VERCEL_TOKEN` | https://vercel.com/account/tokens → Create Token |
| `VERCEL_ORG_ID` | Vercel → Settings → General → Team ID |
| `VERCEL_PROJECT_ID` | Vercel → Project → Settings → General → Project ID |
| `WHATSAPP_TOKEN` | Meta Business Manager → WhatsApp → Access Token |
| `WHATSAPP_PHONE_ID` | Meta Business Manager → WhatsApp → Phone Number ID |
| `WHATSAPP_VERIFY_TOKEN` | Любая случайная строка, например `zeta_webhook_2026` |

### Создать AZURE_CREDENTIALS:
```bash
az ad sp create-for-rbac \
  --name "zeta-github-deploy" \
  --role contributor \
  --scopes /subscriptions/5d789370-45fe-43a0-a1e4-73c29258fb0d/resourceGroups/zeta-platform-prod \
  --sdk-auth
```
Скопируй весь JSON вывод в секрет `AZURE_CREDENTIALS`.

### Добавить все секреты через GitHub CLI (быстрее):
```bash
# Установи gh CLI: https://cli.github.com/
gh auth login

gh secret set VERCEL_TOKEN -b "твой_токен"
gh secret set VERCEL_ORG_ID -b "твой_org_id"
gh secret set VERCEL_PROJECT_ID -b "твой_project_id"
gh secret set DATABASE_URL -b "postgresql://zetaadmin:ZetaSecure69053!@zeta-db-1771569053.postgres.database.azure.com:5432/zeta_platform"
gh secret set OPENAI_API_KEY -b "sk-..."
gh secret set TELEGRAM_BOT_TOKEN -b "7750680653:AAHs4Xe9gTwufOjNFLNf1SuMoy_cN_2sOzM"
gh secret set WHATSAPP_VERIFY_TOKEN -b "zeta_webhook_2026"
```

---

## Шаг 2 — Подключить Vercel к репозиторию

1. Зайди на https://vercel.com/new
2. Нажми **Import Git Repository** → выбери `ShhTair/zeta-platform`
3. **Root Directory**: `apps/web`
4. Framework: **Next.js** (автоматически)
5. Добавь переменную окружения: `NEXT_PUBLIC_API_URL` = `/api`
6. Deploy → после деплоя скопируй **Project ID** и **Team ID** в секреты GitHub

---

## Шаг 3 — Запустить деплой

```bash
# Push любые изменения → Actions запустятся автоматически
# Или вручную:
gh workflow run deploy-frontend.yml
gh workflow run deploy-api.yml
gh workflow run deploy-telegram-bot.yml
```

---

## Шаг 4 — Войти в панель

После деплоя фронтенда:
- URL: `https://твой-проект.vercel.app`
- Email: `admin@zeta.kz`
- Password: `admin123`

---

## Важно: обновить IP API в vercel.json

Если Azure Container App получит новый IP, обнови в [apps/web/vercel.json](apps/web/vercel.json):
```json
"destination": "http://НОВЫЙ_IP:8000/:path*"
```

Или лучше — настрой кастомный домен в Azure Container Apps и используй его.

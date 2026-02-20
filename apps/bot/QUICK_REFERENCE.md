# 🎯 ZETA Bot Interactive UI - Quick Reference Card

## 📁 New Files

```
handlers/interactive.py               # Core interactive UI
handlers/conversation_interactive.py  # Enhanced search
INTERACTIVE_FEATURES.md               # Full feature docs
MIGRATION_GUIDE.md                    # Migration steps
TEST_CHECKLIST.md                     # Testing guide
IMPLEMENTATION_SUMMARY.md             # Overview
QUICK_REFERENCE.md                    # This file
```

## 🚀 Deploy in 60 Seconds

```bash
# 1. Update contact info
nano handlers/interactive.py
# Search for "Телефон:" and update

# 2. Restart bot
sudo systemctl restart zeta-bot
# OR: pm2 restart zeta-bot
# OR: docker-compose restart bot

# 3. Quick test
# Telegram → /start → Should show menu
```

## 🔄 Rollback in 30 Seconds

```bash
# Edit main.py
nano main.py

# Comment these lines:
# dp.include_router(interactive.router)
# dp.include_router(conversation_interactive.router)

# Restart
sudo systemctl restart zeta-bot
```

## 🧪 Quick Test

```
1. /start     → Menu shows?
2. Type "стул" → Filters show?
3. Click filter → Products show?
4. Click product → Details + buttons?
5. Click "📸" → Photo sends?
6. All ✅? → Success!
```

## 📊 Key Metrics to Watch

```
✅ Response time < 3s
✅ Error rate < 1%
✅ Button click rate > 80%
✅ Session time +80%
✅ Conversion rate +100%
```

## 🔧 Quick Config

```python
# handlers/interactive.py
MAX_PRODUCTS_PER_PAGE = 5    # Products per page
MAX_CAROUSEL_PHOTOS = 10     # Max photos
WEBSITE_BASE_URL = "https://zeta.kz"
```

## 💡 Key Features

```
✅ Inline keyboards (no typing!)
✅ Photo sharing (single + carousel)
✅ Website links (one tap)
✅ Manager contact (auto CRM)
✅ Pagination (5 per page)
✅ Quick filters (home/office/price)
✅ Menu (/start, /menu)
```

## 🐛 Common Issues

### Buttons not showing
→ Check handler order in main.py

### Photos not sending
→ Verify product has `image_url` field

### Callback timeout
→ Always call `await callback.answer()`

### State not persisting
→ Use `MemoryStorage()` in Dispatcher

## 📞 Emergency Contacts

```
Logs: tail -f /var/log/zeta-bot.log
API Health: curl http://localhost:8000/api/health
Bot Status: systemctl status zeta-bot
```

## 📚 Full Docs

```
Features → INTERACTIVE_FEATURES.md
Migration → MIGRATION_GUIDE.md
Testing → TEST_CHECKLIST.md
Overview → IMPLEMENTATION_SUMMARY.md
```

---

**Version:** 2.0.0  
**Status:** ✅ Ready for Production  
**Last Updated:** 2025-02-19

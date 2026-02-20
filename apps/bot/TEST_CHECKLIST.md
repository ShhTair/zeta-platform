# ✅ Interactive Features Test Checklist

Run these tests manually after deployment to verify everything works.

## 🚀 Pre-Deployment Checks

### File Verification
```bash
cd /home/tair/.openclaw/workspace/zeta-platform/apps/bot

# Check new files exist
ls -l handlers/interactive.py                # Should exist
ls -l handlers/conversation_interactive.py   # Should exist
ls -l INTERACTIVE_FEATURES.md                # Should exist
ls -l MIGRATION_GUIDE.md                     # Should exist

# Check handlers are imported in main.py
grep -n "interactive" main.py                # Should show imports
grep -n "conversation_interactive" main.py   # Should show imports
```

### Configuration Check
```bash
# Verify environment variables
cat .env | grep -E "BOT_TOKEN|API_URL|OPENAI_API_KEY"

# Should show:
# BOT_TOKEN=xxx
# API_URL=http://localhost:8000
# OPENAI_API_KEY=xxx (if using AI)
```

---

## 🧪 Functional Tests (In Telegram)

### Test 1: Start Command
```
Action: Send /start to bot

Expected:
✅ Bot responds with welcome message
✅ Shows 4 inline buttons:
   • 🔍 Искать товар
   • 🏷️ Популярные товары
   • 💬 Связаться
   • ℹ️ О компании
✅ Buttons are clickable
```

### Test 2: Menu Command
```
Action: Send /menu to bot

Expected:
✅ Bot shows quick actions menu
✅ Same 4 buttons as /start
✅ Buttons respond to clicks
```

### Test 3: Vague Query + Filters
```
Action: Type "стул"

Expected:
✅ Bot asks for clarification
✅ Shows filter buttons:
   • 🏠 Для дома
   • 🏢 Для офиса
   • 🎨 По цвету
   • 💰 По цене
   • 📋 Показать всё

Action: Click "🏠 Для дома"

Expected:
✅ Bot searches for "стул для дома"
✅ Shows product list with buttons
```

### Test 4: Product Search
```
Action: Type "офисное кресло"

Expected:
✅ Bot shows "🔍 Ищу в каталоге..."
✅ Returns product list (if products exist)
✅ Each product shows as button:
   🪑 Product Name • Price ₸
✅ Shows navigation buttons:
   • 📄 Показать ещё (if >5 products)
   • 🔄 Новый поиск
```

### Test 5: Product Details
```
Action: Click on any product button from search results

Expected:
✅ Bot shows detailed product info:
   • 🪑 Product name
   • 📦 Артикул (SKU)
   • 📝 Description
   • 📏 Characteristics
   • 💰 Price
   • 📍 Stock status
✅ Shows action buttons:
   • 📸 Фото
   • 🔗 Ссылка на сайт
   • 💬 Связаться с менеджером
   • ↩️ Назад к списку
✅ If product has image, shows photo with caption
```

### Test 6: Photo Sharing
```
Action: Click "📸 Фото" button on product

Expected:
✅ Bot sends product photo
✅ Photo has caption with product name & SKU
✅ If multiple photos exist, sends as album
✅ If no photo, shows message "😔 Фото пока нет"
```

### Test 7: Website Link
```
Action: Click "🔗 Ссылка на сайт" button

Expected:
✅ Bot sends message with product URL
✅ Shows inline button "🌐 Открыть на сайте"
✅ Clicking button opens website in browser
✅ URL format: https://zeta.kz/products/{sku}
```

### Test 8: Manager Contact
```
Action: Click "💬 Связаться с менеджером" button

Expected:
✅ Bot creates CRM deal (Bitrix)
✅ Shows success message with deal ID
✅ Shows contact information:
   • 📞 Phone number
   • ✉️ Email
   • Product SKU
✅ If CRM fails, shows fallback contact info
```

### Test 9: Back to List
```
Action: Click "↩️ Назад к списку" button

Expected:
✅ Bot returns to product search results
✅ Shows same product list as before
✅ Pagination state preserved (if on page 2, stays on page 2)
✅ Can click on another product
```

### Test 10: Pagination
```
Setup: Search for query that returns >5 products

Action: Click "📄 Показать ещё" button

Expected:
✅ Bot shows next 5 products
✅ Page indicator updates (if shown)
✅ Can click on new products
✅ "Показать ещё" appears again if more products exist
✅ Can paginate through all results
```

### Test 11: New Search
```
Action: Click "🔄 Новый поиск" button

Expected:
✅ Clears current search results
✅ Shows search prompt or main menu
✅ Can start new search
✅ State is reset (offset = 0)
```

### Test 12: Price Filter
```
Action: Type "диван", then click "💰 По цене"

Expected:
✅ Bot shows price range buttons:
   • 💸 До 50,000 ₸
   • 💰 50,000 - 150,000 ₸
   • 💎 Более 150,000 ₸
   • 📋 Показать все

Action: Click price range

Expected:
✅ Bot searches with price filter
✅ Shows filtered results
```

### Test 13: Popular Products
```
Action: Click "🏷️ Популярные товары" from menu

Expected:
✅ Bot loads popular products
✅ Shows product list with buttons
✅ Can click on products for details
✅ All product actions work normally
```

### Test 14: Contact Action
```
Action: Click "💬 Связаться" from menu

Expected:
✅ Bot shows contact information:
   • 📞 Phone
   • ✉️ Email
   • 🌐 Website
   • 📍 Address
   • ⏰ Working hours
✅ Shows "↩️ Назад" button
✅ Back button returns to menu
```

### Test 15: About Company
```
Action: Click "ℹ️ О компании" from menu

Expected:
✅ Bot shows company information
✅ Lists advantages/benefits
✅ Shows mission
✅ Shows catalog size
✅ Has "🌐 Наш сайт" URL button
✅ Has "↩️ Назад в меню" button
```

---

## 🐛 Error Handling Tests

### Test 16: No Search Results
```
Action: Search for "asdfghjkl" (nonsense query)

Expected:
✅ Bot shows "😔 Ничего не найдено"
✅ Shows helpful message
✅ Shows buttons:
   • 💬 Связаться с менеджером
   • 🔄 Новый поиск
✅ Can click buttons to continue
```

### Test 17: Product Not Found
```
Setup: Manually trigger callback with invalid SKU
(Hard to test manually, check logs for graceful handling)

Expected:
✅ Bot shows "❌ Товар не найден"
✅ Doesn't crash
✅ User can continue using bot
```

### Test 18: API Timeout
```
Setup: Temporarily stop backend API server

Action: Search for any product

Expected:
✅ Bot shows error message
✅ Suggests trying again or contacting support
✅ Doesn't crash
✅ Can retry after API restored
```

### Test 19: Photo Load Failure
```
Setup: Product with invalid/broken image URL

Action: Click "📸 Фото" button

Expected:
✅ Bot shows "❌ Не удалось загрузить фото"
✅ Doesn't crash
✅ Other buttons still work
```

---

## 📊 Performance Tests

### Test 20: Rapid Button Clicks
```
Action: Click buttons very quickly (5 clicks/second)

Expected:
✅ Bot handles all clicks
✅ Callback queries answered
✅ No "Query is too old" errors
✅ No crashes or hangs
```

### Test 21: Large Product List
```
Action: Search for generic term that returns 20+ products

Expected:
✅ Bot responds in <3 seconds
✅ Shows first 5 products
✅ Pagination works smoothly
✅ Memory usage stable
```

### Test 22: Multiple Concurrent Users
```
Setup: 5 friends test bot simultaneously

Expected:
✅ Each user gets their own results
✅ No state mixing between users
✅ Bot responsive for all users
✅ No crashes under load
```

---

## 🎨 UI/UX Tests

### Test 23: Button Text Clarity
```
Check all buttons throughout bot

Expected:
✅ Button text is clear and actionable
✅ Emojis are appropriate and recognizable
✅ No text cutoff (under 40 chars)
✅ Consistent style across UI
```

### Test 24: Message Formatting
```
Check all bot messages

Expected:
✅ Bold/italic formatting works
✅ Product prices formatted with commas
✅ Emojis render correctly
✅ No HTML tags visible to user
✅ Line breaks appropriate
```

### Test 25: Mobile Responsiveness
```
Action: Test on mobile phone (Android/iOS)

Expected:
✅ Buttons are tappable (not too small)
✅ Text is readable (not too small)
✅ Photos display correctly
✅ Links open in mobile browser
✅ Overall UX feels smooth
```

---

## 🔒 Security Tests

### Test 26: Callback Data Validation
```
Action: Try to tamper with callback data (if possible)

Expected:
✅ Bot validates callback data
✅ Rejects invalid SKUs/IDs
✅ Shows appropriate error
✅ Doesn't expose sensitive info
```

### Test 27: User Data Privacy
```
Action: Check logs and database

Expected:
✅ User passwords NOT logged
✅ Telegram tokens NOT logged in plaintext
✅ Personal data handled properly
✅ GDPR compliance (if applicable)
```

---

## 📈 Analytics Tests

### Test 28: Button Click Tracking
```
Action: Click various buttons throughout flow

Expected:
✅ Clicks logged (if analytics enabled)
✅ User journey trackable
✅ Popular products identified
✅ Drop-off points visible
```

---

## ✅ Final Checklist

Before marking deployment as successful:

- [ ] All 25+ functional tests pass
- [ ] No critical errors in logs
- [ ] Response time < 3 seconds
- [ ] User feedback positive
- [ ] Analytics dashboard showing data
- [ ] Fallbacks work (no photos, no results, API down)
- [ ] Mobile UX excellent
- [ ] Desktop UX excellent
- [ ] Team trained on new features

---

## 🎯 Success Criteria

**Deployment is successful if:**
- ✅ 95%+ tests pass
- ✅ No P0/P1 bugs
- ✅ User engagement increased
- ✅ Support tickets decreased
- ✅ Team happy with new UI

**Rollback if:**
- ❌ >5% tests fail
- ❌ Any P0 bug (bot crashes)
- ❌ User complaints spike
- ❌ API errors spike

---

## 📞 Support Contacts

If issues arise during testing:

- **Developer:** @your_telegram
- **Backend API:** Check `/api/health`
- **Logs:** `/var/log/zeta-bot.log`
- **Monitoring:** Grafana dashboard (if available)

---

**Test Date:** _______________  
**Tested By:** _______________  
**Result:** ✅ PASS / ❌ FAIL  
**Notes:** _______________

# 🚀 ZETA Integrations Quick Start

**New to this project?** Start here!

---

## 📚 Read This First (5 minutes)

### What Was Built?
Phase 1 delivered a **complete foundation** for future integrations:
- Plugin system for 1C, Bitrix24, and more
- Document upload and search infrastructure
- Conversation memory and rate limiting
- Multilanguage support (Russian + Kazakh)

### Current Status
- ✅ **Architecture:** Complete and tested
- ✅ **Stubs:** 1C and Bitrix24 connectors ready for implementation
- ⏳ **Implementation:** Waiting for external system access

---

## 🗂️ File Guide (What to Read)

### Start Here
1. **`PHASE1_COMPLETE.md`** ← Read first! High-level overview
2. **`INTEGRATION_ARCHITECTURE.md`** ← Understand the design
3. **`INTEGRATION_GUIDE.md`** ← Step-by-step implementation

### When Implementing
4. **`config/integrations.yaml`** ← All configuration options
5. **`integrations/README.md`** ← Usage examples and patterns
6. **Individual files in `integrations/`** ← See TODO comments

### Reference
- **`requirements-integrations.txt`** - Dependencies to install
- **`test_integrations.py`** - Test suite
- **`verify_structure.py`** - Verify everything is in place

---

## ⚡ Quick Commands

### Verify Everything Is Set Up
```bash
cd apps/bot
python3 verify_structure.py
```

### View Configuration
```bash
cat config/integrations.yaml
```

### Install Optional Dependencies (when ready)
```bash
pip install -r requirements-integrations.txt
```

### Run Tests (requires dependencies)
```bash
python3 test_integrations.py
```

---

## 🎯 Next Steps (Choose Your Path)

### Path A: Implementing 1C Integration
**Prerequisites:** 1C server, HTTP Service, API credentials

1. Read: `INTEGRATION_GUIDE.md` → "Phase 1: 1C:Enterprise Integration"
2. Open: `integrations/onec.py`
3. Follow TODO comments
4. Test: Each method individually
5. Enable: `config/integrations.yaml` → `onec.enabled: true`

**Estimated Time:** 8-12 days

---

### Path B: Implementing Bitrix24 Integration
**Prerequisites:** Bitrix24 account, webhook URL

1. Read: `INTEGRATION_GUIDE.md` → "Phase 2: Bitrix24 Integration"
2. Open: `integrations/bitrix24.py`
3. Follow TODO comments
4. Test: Create test lead
5. Enable: `config/integrations.yaml` → `bitrix24.enabled: true`

**Estimated Time:** 5-7 days

---

### Path C: Implementing Document Search
**Prerequisites:** Redis, OpenAI API key, vector database

1. Read: `INTEGRATION_GUIDE.md` → "Phase 3: Document Upload & Search"
2. Open: `api/app/routers/documents.py`
3. Implement text extraction functions
4. Setup vector database
5. Enable: `config/integrations.yaml` → `documents.search.enabled: true`

**Estimated Time:** 7-10 days

---

### Path D: Enabling Advanced Features
**Prerequisites:** Redis server

1. Deploy Redis: `docker run -d -p 6379:6379 redis:alpine`
2. Enable memory: `config/integrations.yaml` → `advanced.memory.enabled: true`
3. Enable rate limit: `config/integrations.yaml` → `advanced.rate_limit.enabled: true`
4. Test: Check Redis keys with `redis-cli`

**Estimated Time:** 2-3 days

---

## 🔍 Common Questions

### Q: Where do I configure API credentials?
**A:** Environment variables. See `.env.example` and `config/integrations.yaml`

### Q: How do I add a new integration?
**A:** 
1. Create `integrations/myservice.py`
2. Inherit from `Integration` base class
3. Implement required methods
4. Register in manager
5. Add config section

See `integrations/README.md` → "How to Add New Integration"

### Q: Can I test without external systems?
**A:** Yes! Stubs return predictable data. Run `verify_structure.py` for structure checks.

### Q: Where are the logs?
**A:** Configure in your main bot file. Check `/var/log/zeta/bot.log` or console output.

### Q: Do I need to install all optional dependencies?
**A:** No! Install only what you need:
- Redis features: `pip install redis hiredis`
- Documents: `pip install PyPDF2 pandas pinecone-client`
- 1C/Bitrix24: `pip install httpx tenacity`

---

## 🛠️ Development Workflow

### 1. Pick an Integration to Implement
Choose 1C, Bitrix24, or Document Search

### 2. Read the Relevant Section
`INTEGRATION_GUIDE.md` has step-by-step instructions

### 3. Open the Stub File
- `integrations/onec.py` for 1C
- `integrations/bitrix24.py` for Bitrix24
- `api/app/routers/documents.py` for documents

### 4. Follow TODO Comments
Every file has clear TODO comments showing what to implement

### 5. Test Incrementally
Test each method as you implement it:
```python
# Test script
import asyncio
from integrations.onec import OneCIntegration

async def test():
    integration = OneCIntegration(
        api_url="http://localhost",
        username="test",
        password="test"
    )
    
    # Test connection
    success = await integration.initialize()
    print(f"Connection: {success}")

asyncio.run(test())
```

### 6. Enable in Config
Once tested, enable in `config/integrations.yaml`

### 7. Monitor Logs
Watch for errors and tune as needed

---

## 📋 Checklist for Each Integration

### Before Starting
- [ ] Read relevant guide section
- [ ] Confirm external system access
- [ ] Get API credentials
- [ ] Install required dependencies

### During Implementation
- [ ] Implement `initialize()` method
- [ ] Test connection
- [ ] Implement other required methods
- [ ] Add error handling
- [ ] Test with sample data
- [ ] Document any deviations from plan

### Before Production
- [ ] Full integration test
- [ ] Load testing (if applicable)
- [ ] Security review
- [ ] Update documentation
- [ ] Train team on new feature
- [ ] Setup monitoring/alerts

---

## 🐛 Troubleshooting

### "Module not found" errors
```bash
# Install dependencies
pip install -r requirements.txt
pip install -r requirements-integrations.txt
```

### "Redis connection failed"
```bash
# Check if Redis is running
redis-cli ping

# Start Redis if needed
docker run -d -p 6379:6379 redis:alpine
```

### "1C connection failed"
- Verify network access to 1C server
- Check HTTP Service is published
- Test with curl first
- Review 1C logs

### "Bitrix24 webhook not working"
- Verify webhook URL format
- Check permissions in Bitrix24 settings
- Test with curl or Postman
- Check Bitrix24 rate limits

### "Document search returns no results"
- Check vector database connection
- Verify embeddings were generated
- Test with simple queries first
- Review chunk size and overlap settings

---

## 🎓 Learning Resources

### Understanding the Architecture
- `INTEGRATION_ARCHITECTURE.md` - Design decisions and patterns
- `integrations/README.md` - Usage examples

### Implementation Details
- `INTEGRATION_GUIDE.md` - Complete implementation guide
- Code files have extensive comments
- `config/integrations.yaml` - Every option documented

### External Documentation
- **1C:** HTTP Service documentation (1C specific)
- **Bitrix24:** REST API docs at developers.bitrix24.com
- **OpenAI:** Embeddings API docs at platform.openai.com
- **Redis:** redis.io/documentation
- **Aiogram:** docs.aiogram.dev

---

## 💬 Get Help

### Check Documentation First
Most questions are answered in:
1. `INTEGRATION_GUIDE.md` - Implementation steps
2. `INTEGRATION_ARCHITECTURE.md` - Design questions
3. `integrations/README.md` - Usage examples

### Still Stuck?
1. Check TODO comments in relevant file
2. Review example code in comments
3. Test with minimal example
4. Check logs for error messages

---

## ✨ Tips for Success

### 🎯 Start Small
Don't try to implement everything at once. Pick one integration, get it working, then move to the next.

### 📝 Follow TODOs
Every stub file has clear TODO comments. Follow them in order.

### 🧪 Test Often
Test each method as you implement it. Don't wait until everything is done.

### 📚 Read Examples
The guide has working examples for every integration. Use them!

### 🔍 Check Logs
Enable detailed logging while developing. It will save you hours.

### 💾 Commit Frequently
Commit working code often. Easy to roll back if needed.

---

## 🏁 Success Criteria

You'll know you're done when:

- [ ] Integration connects successfully (`initialize()` returns `True`)
- [ ] Data syncs without errors
- [ ] Bot uses integration in real conversations
- [ ] Logs show successful operations
- [ ] Team trained on new features
- [ ] Documentation updated with any changes

---

## 🎉 You're Ready!

Pick a path above and get started. The foundation is solid, the docs are comprehensive, and the code is waiting for you.

**Good luck!** 🚀

---

**Need a refresher?** Come back to this file anytime for quick reference.

**Have questions?** Check the detailed guides:
- Architecture: `INTEGRATION_ARCHITECTURE.md`
- Implementation: `INTEGRATION_GUIDE.md`
- Usage: `integrations/README.md`

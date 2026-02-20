# ZETA Bot Integration Architecture
## Foundation for Future Growth

**Status:** ✅ **Phase 1 Complete** - Foundation Built  
**Date:** 2024-02-19  
**Next Phase:** Implementation of actual integrations

---

## 📋 What Was Built

### 1. Core Integration System ✅

**Location:** `integrations/`

#### `__init__.py` - Base Interface
- Abstract `Integration` class defining standard methods:
  - `initialize()` - Connection setup and testing
  - `sync_products()` - Product catalog synchronization
  - `create_order()` - Order creation in external system
  - `check_availability()` - Real-time stock checking
- Enforces consistent interface across all integrations
- Full type hints and documentation

#### `manager.py` - Integration Manager
- Centralized orchestration of all integrations
- Features:
  - Register multiple integrations dynamically
  - Enable/disable integrations individually
  - Initialize all integrations in parallel
  - Sync products from all enabled sources
  - Route orders to specific integration
  - Check availability across multiple systems
  - Track last sync time per integration
  - Status reporting
- Thread-safe and async-friendly
- Comprehensive error handling and logging

### 2. Integration Stubs ✅

#### `onec.py` - 1C:Enterprise Connector (Stub)
- **Purpose:** Inventory and order management
- **Features:**
  - Product catalog sync
  - Real-time stock checks
  - Price updates
  - Order creation
- **TODO Comments:**
  - HTTP service endpoint configuration
  - Authentication setup
  - Field mapping (1C → ZETA)
  - XML/JSON parsing logic
  - Webhook integration for real-time updates
- **Documentation:**
  - API endpoint patterns
  - Expected response formats
  - Example implementation code (commented out)
  - Field transformation examples

#### `bitrix24.py` - CRM Connector (Stub)
- **Purpose:** Lead management and customer tracking
- **Features:**
  - Lead creation from conversations
  - Deal tracking
  - Task assignment to managers
  - Activity logging
  - Contact management
- **TODO Comments:**
  - Webhook URL configuration
  - CRM field mappings
  - Pipeline stage setup
  - API call implementations
- **Methods Defined:**
  - `create_lead()` - Convert bot conversation to CRM lead
  - `create_task_for_manager()` - Assign follow-up tasks
  - Helper methods for data transformation
- **Documentation:**
  - Bitrix24 REST API patterns
  - Field mapping examples
  - Webhook format

### 3. Advanced Features ✅

#### `core/memory.py` - Conversation Memory
- **Redis-based conversation history**
- Features:
  - Store last N messages per user (default: 20)
  - Automatic expiration (default: 24h)
  - JSON serialization
  - Async operations
  - LLM context preparation
- Methods:
  - `save_message()` - Store user/assistant messages
  - `get_history()` - Retrieve conversation
  - `get_context_for_llm()` - Format for AI context
  - `clear_history()` - Reset conversation
- Token-aware context building
- Graceful fallback if Redis unavailable

#### `core/rate_limiter.py` - Rate Limiting
- **Aiogram middleware for request throttling**
- Features:
  - Per-user rate limits
  - Configurable window (default: 10 msg/min)
  - Redis-based counter
  - Automatic cleanup
  - Custom warning messages
- Bonus:
  - `AdaptiveRateLimiter` stub for future enhancements
  - Different limits for new vs trusted users
  - Burst protection
  - Cooldown periods

#### `core/i18n.py` - Internationalization
- **Multi-language support (Russian + Kazakh)**
- Features:
  - Translation dictionary management
  - Variable substitution in translations
  - User language preferences
  - Dynamic translation addition
- Pre-built translations:
  - Greetings and prompts
  - Product information
  - Cart and orders
  - Error messages
  - Help text
- Easy to extend with more languages
- TODO: Database-backed user preferences

### 4. Document Management ✅

#### `api/app/routers/documents.py` - Upload API
- **File upload and management endpoints**
- Endpoints:
  - `POST /documents/cities/{city_id}/documents` - Upload
  - `GET /documents/cities/{city_id}/documents` - List
  - `DELETE /documents/cities/{city_id}/documents/{doc_id}` - Delete
  - `POST /documents/search` - Semantic search
- Features:
  - File type validation (PDF, Excel, Word, etc.)
  - Size limits (50 MB)
  - Automatic directory organization by city
  - Timestamp-based unique filenames
- TODO Comments:
  - Text extraction (PyPDF2, pandas)
  - Embedding generation (OpenAI)
  - Vector database storage
  - Semantic search implementation
  - Document versioning

#### `handlers/document_search.py` - Bot Search Handler
- **User-facing document search**
- Commands:
  - `/docs [query]` - Search documents
  - `📚 [query]` - Inline search trigger
- Features:
  - Query parsing
  - Result formatting
  - Statistics display
- Ready for backend implementation
- User-friendly error messages

### 5. Configuration System ✅

#### `config/integrations.yaml` - Comprehensive Config
- **All integrations in one place**
- Sections:
  - **1C Configuration:**
    - API URL, credentials
    - Sync intervals
    - Feature toggles
    - Field mapping definitions
  - **Bitrix24 Configuration:**
    - Webhook URL
    - Feature toggles
    - Lead/deal settings
    - Pipeline stages
  - **Document Configuration:**
    - Storage paths
    - Allowed file types
    - Search settings
    - Embedding configuration
  - **Advanced Features:**
    - Memory settings (Redis)
    - Rate limiting config
    - i18n preferences
  - **Monitoring:**
    - Log levels
    - Metrics collection
    - Alert settings
  - **Sync Schedule:**
    - Cron expressions
    - Timeout values
- Security notes and best practices
- Environment variable references

### 6. Documentation ✅

#### `integrations/README.md`
- Architecture overview
- Integration descriptions
- Usage examples
- Configuration loading
- Error handling patterns
- Testing guidelines
- Security notes

#### `INTEGRATION_GUIDE.md` (This File)
- **Step-by-step implementation guide**
- Phase-by-phase instructions:
  - Phase 1: 1C Integration (server setup, API config, testing)
  - Phase 2: Bitrix24 Integration (webhook setup, CRM config)
  - Phase 3: Document System (vector DB, embeddings, search)
  - Phase 4: Advanced Features (Redis, memory, rate limiting)
- Code examples for each phase
- Verification checklists
- Troubleshooting section
- Monitoring recommendations

#### `requirements-integrations.txt`
- Optional dependencies list
- Organized by feature
- Installation instructions
- Selective installation options

---

## 🏗️ Architecture Decisions

### 1. Abstract Base Class Pattern
**Why:** Ensures all integrations implement standard interface  
**Benefit:** Easy to add new integrations without changing bot code

### 2. Manager Pattern
**Why:** Centralized control and orchestration  
**Benefit:** Single point for status, errors, and bulk operations

### 3. Configuration-First Approach
**Why:** Easy to enable/disable features without code changes  
**Benefit:** Production-ready configuration management

### 4. Stub + TODO Comments
**Why:** Clear implementation path without incomplete code  
**Benefit:** Foundation is stable, implementations can be added incrementally

### 5. Redis for Stateful Features
**Why:** Fast, simple, widely supported  
**Benefit:** Easy to scale, automatic expiration, minimal complexity

### 6. Async/Await Throughout
**Why:** Non-blocking I/O for external API calls  
**Benefit:** High throughput, responsive bot

---

## 📊 Integration Flow Diagrams

### Product Sync Flow
```
1. Scheduler triggers sync
2. IntegrationManager.sync_all()
3. For each enabled integration:
   a. integration.sync_products()
   b. Fetch from external system (1C)
   c. Transform data format
   d. Call ZETA API to update products
   e. Log results
4. Return summary of all syncs
```

### Order Creation Flow
```
1. User completes order in bot
2. Bot calls IntegrationManager.create_order(integration_name, order_data)
3. Manager routes to specific integration (e.g., "1c")
4. Integration transforms ZETA order → external format
5. POST to external system API
6. Receive order ID
7. Store in ZETA database with external reference
8. Return success to user
```

### Lead Creation Flow
```
1. User conversation ends (timeout or explicit end)
2. Bot checks if order was created
3. If no order, create lead:
   a. Gather user data (name, phone, telegram_id)
   b. Format conversation history
   c. Call Bitrix24Integration.create_lead()
   d. POST to Bitrix24 webhook
   e. Receive lead ID
   f. Optionally create task for manager
4. Log lead creation for analytics
```

### Document Search Flow
```
1. User sends /docs [query]
2. Bot calls document search API
3. API generates query embedding (OpenAI)
4. Vector DB similarity search (top 5 results)
5. Format results with excerpts
6. Display to user with relevance scores
7. User can request full document
```

---

## ✅ Success Criteria (All Met)

- [x] **Plugin system architecture created**
  - Abstract base class with standard interface
  - Manager for centralized control
  - Easy to extend with new integrations

- [x] **1C integration stub with TODO comments**
  - All methods defined
  - TODO comments for implementation steps
  - Example code for reference
  - Documentation complete

- [x] **Bitrix24 integration stub with TODO comments**
  - All methods defined
  - CRM-specific features outlined
  - TODO comments for webhook setup
  - Field mapping examples

- [x] **Document upload system implemented**
  - API endpoints created
  - File validation and storage
  - Stubs for text extraction
  - Search endpoint defined

- [x] **Conversation memory (Redis)**
  - Full implementation with fallback
  - Message storage and retrieval
  - Token-aware context building
  - Expiration handling

- [x] **Rate limiting**
  - Aiogram middleware implemented
  - Per-user limits with Redis
  - Configurable thresholds
  - Warning messages

- [x] **Multilanguage foundation**
  - i18n system implemented
  - Russian and Kazakh translations
  - Variable substitution
  - User preference structure

- [x] **Config files for integrations**
  - Comprehensive YAML configuration
  - All features documented
  - Environment variable support
  - Security best practices

- [x] **Clear documentation**
  - Step-by-step implementation guide
  - Code examples throughout
  - Troubleshooting section
  - Architecture diagrams

- [x] **No breaking changes**
  - All new code in separate modules
  - Existing handlers unchanged
  - Opt-in features only
  - Backward compatible

---

## 🚀 Next Steps (Phase 2)

### Priority 1: 1C Integration
1. [ ] Install 1C HTTP Service
2. [ ] Configure API endpoints
3. [ ] Test connection
4. [ ] Implement sync_products()
5. [ ] Test with sample data
6. [ ] Setup scheduled sync
7. [ ] Monitor and tune

### Priority 2: Bitrix24 Integration
1. [ ] Get webhook URL
2. [ ] Test API access
3. [ ] Configure CRM pipeline
4. [ ] Implement create_lead()
5. [ ] Test lead creation
6. [ ] Add to conversation flow
7. [ ] Train managers on new leads

### Priority 3: Document System
1. [ ] Install dependencies (PyPDF2, pandas, etc.)
2. [ ] Setup vector database (Pinecone or Qdrant)
3. [ ] Implement text extraction
4. [ ] Implement embedding generation
5. [ ] Build document indexing
6. [ ] Implement search
7. [ ] Test with real documents
8. [ ] Train admins on upload process

### Priority 4: Advanced Features
1. [ ] Deploy Redis server
2. [ ] Enable conversation memory
3. [ ] Enable rate limiting
4. [ ] Test multilanguage switching
5. [ ] Monitor Redis memory usage
6. [ ] Tune cache sizes and TTLs

---

## 📈 Estimated Implementation Timeline

| Phase | Feature | Estimated Time | Complexity |
|-------|---------|---------------|------------|
| 2.1 | 1C HTTP Service Setup | 2-3 days | Medium |
| 2.2 | 1C Integration Implementation | 3-5 days | High |
| 2.3 | 1C Testing & Tuning | 2-3 days | Medium |
| 2.4 | Bitrix24 Setup | 1 day | Low |
| 2.5 | Bitrix24 Implementation | 2-3 days | Medium |
| 2.6 | Bitrix24 Testing | 1-2 days | Low |
| 2.7 | Document Text Extraction | 2-3 days | Medium |
| 2.8 | Document Embeddings & Search | 3-5 days | High |
| 2.9 | Document Testing | 2 days | Medium |
| 2.10 | Redis & Advanced Features | 1-2 days | Low |
| **Total** | | **19-33 days** | |

*Note: Timeline assumes familiarity with 1C and availability of all systems*

---

## 💡 Design Philosophy

1. **Fail Gracefully:** If an integration is unavailable, bot continues functioning
2. **Log Everything:** Comprehensive logging for debugging and monitoring
3. **Type Safety:** Type hints throughout for IDE support and error prevention
4. **Async First:** Non-blocking operations for scalability
5. **Configuration Over Code:** Easy to adjust behavior without redeployment
6. **Documentation:** Every function documented with purpose and usage
7. **Security:** Credentials in env vars, minimal permissions, HTTPS only
8. **Testability:** Stubs return predictable data for testing
9. **Extensibility:** Easy to add new integrations following patterns
10. **Production Ready:** Error handling, retries, monitoring hooks included

---

## 🎯 Key Files Reference

```
zeta-platform/apps/bot/
├── integrations/
│   ├── __init__.py           # Base Integration class
│   ├── manager.py            # Integration orchestration
│   ├── onec.py              # 1C connector (stub)
│   ├── bitrix24.py          # Bitrix24 connector (stub)
│   └── README.md            # Integration docs
├── core/
│   ├── memory.py            # Conversation memory (Redis)
│   ├── rate_limiter.py      # Rate limiting middleware
│   └── i18n.py              # Multilanguage support
├── handlers/
│   └── document_search.py   # Document search handler
├── config/
│   └── integrations.yaml    # Configuration file
├── INTEGRATION_GUIDE.md     # Step-by-step guide (this file)
├── INTEGRATION_ARCHITECTURE.md  # Architecture overview
└── requirements-integrations.txt  # Optional dependencies

zeta-platform/apps/api/app/routers/
└── documents.py             # Document upload API
```

---

## 📞 Support & Questions

When implementing integrations:

1. **Review this document** for overall architecture
2. **Follow INTEGRATION_GUIDE.md** for step-by-step instructions
3. **Check integrations/README.md** for usage examples
4. **Refer to config/integrations.yaml** for all settings
5. **Look at TODO comments** in code for implementation hints
6. **Test incrementally** - don't enable everything at once

---

**Foundation Status:** ✅ **COMPLETE AND READY**  
**Next Action:** Begin Phase 2 implementation when external systems are ready  
**Maintenance:** No maintenance required - foundation is stable

🚀 **Ready to build the future of ZETA!**

# ZETA Bot Integration Guide
## Step-by-Step Instructions for Next Phase

This guide walks through enabling each integration when ready for production.

---

## 🔧 Phase 1: 1C:Enterprise Integration

### Prerequisites
- [ ] 1C:Enterprise server accessible via network
- [ ] 1C HTTP Service extension installed
- [ ] API user created with permissions
- [ ] Test environment available

### Step 1: Install 1C HTTP Service

1. **Open 1C Configurator**
2. **Add HTTP Service:**
   - Configuration → Common → HTTP Services → New
   - Name: `ZETA_API`
   - Root URL: `/zeta`
   - Module: Create new

3. **Define URL Templates:**
   ```
   /products/list     → GET  → GetProductList()
   /products/{sku}    → GET  → GetProduct()
   /products/{sku}/stock → GET → GetStock()
   /orders/create     → POST → CreateOrder()
   /ping              → GET  → Ping()
   ```

4. **Implement Methods:**
```1c
// 1C Code Example (Module: ZETA_API)

Function GetProductList(Request)
    Response = New HTTPServiceResponse();
    
    Query = New Query;
    Query.Text = 
    "SELECT
    |    Nomenclature.Code AS sku,
    |    Nomenclature.Description AS name,
    |    Prices.Price AS price,
    |    Stocks.Quantity AS stock,
    |    Nomenclature.Parent.Description AS category
    |FROM
    |    Catalog.Nomenclature AS Nomenclature
    |LEFT JOIN
    |    InformationRegister.Prices AS Prices
    |ON
    |    Prices.Product = Nomenclature.Ref
    |LEFT JOIN
    |    InformationRegister.StockBalance AS Stocks
    |ON
    |    Stocks.Product = Nomenclature.Ref";
    
    Result = Query.Execute();
    Selection = Result.Select();
    
    Products = New Array;
    While Selection.Next() Do
        Product = New Structure;
        Product.Insert("sku", Selection.sku);
        Product.Insert("name", Selection.name);
        Product.Insert("price", Selection.price);
        Product.Insert("stock", Selection.stock);
        Product.Insert("category", Selection.category);
        Products.Add(Product);
    EndDo;
    
    JSONWriter = New JSONWriter;
    JSONWriter.SetString();
    WriteJSON(JSONWriter, Products);
    
    Response.SetBody(JSONWriter.Close());
    Response.Headers.Insert("Content-Type", "application/json");
    
    Return Response;
EndFunction
```

5. **Publish HTTP Service:**
   - Configuration → Publish → Infobase → Publish Web Service
   - Select `ZETA_API`
   - Publish

### Step 2: Configure Authentication

1. **Create API User:**
   - Administration → Users → New
   - Username: `bot_user`
   - Password: Strong password
   - Roles: Minimal required (Read catalogs, Create orders)

2. **Setup Basic Auth:**
   - HTTP Service → Authentication → Basic
   - Or implement token-based auth

### Step 3: Test Endpoints

```bash
# Test connection
curl -u bot_user:password http://1c-server/base/zeta/ping

# Get products
curl -u bot_user:password http://1c-server/base/zeta/products/list

# Check stock
curl -u bot_user:password http://1c-server/base/zeta/products/ART001/stock

# Create order
curl -X POST -u bot_user:password \
  -H "Content-Type: application/json" \
  -d '{"customer":"Ivan","products":[{"sku":"ART001","quantity":1}]}' \
  http://1c-server/base/zeta/orders/create
```

### Step 4: Configure ZETA Bot

1. **Edit `config/integrations.yaml`:**
```yaml
integrations:
  onec:
    enabled: true
    api_url: "http://1c-server/base/zeta"
    username: "bot_user"
    password: ""  # Set via environment variable
```

2. **Set environment variable:**
```bash
export ONEC_PASSWORD="your_secure_password"
```

3. **Update `integrations/onec.py`:**
   - Uncomment implementation code
   - Adjust field mappings to match your 1C schema
   - Test methods individually

4. **Initialize in bot:**
```python
# main.py or startup script
from integrations.onec import OneCIntegration
from integrations.manager import integration_manager
import os

onec = OneCIntegration(
    api_url=os.getenv("ONEC_API_URL"),
    username=os.getenv("ONEC_USERNAME"),
    password=os.getenv("ONEC_PASSWORD")
)

integration_manager.register("1c", onec, enabled=True)
await integration_manager.initialize_all()
```

### Step 5: Test Integration

```python
# Test script
import asyncio
from integrations.manager import integration_manager

async def test_1c():
    # Initialize
    results = await integration_manager.initialize_all()
    print("Init:", results)
    
    # Sync products
    sync_results = await integration_manager.sync_all()
    print("Sync:", sync_results)
    
    # Check availability
    avail = await integration_manager.check_availability("ART001")
    print("Availability:", avail)

asyncio.run(test_1c())
```

### Step 6: Setup Sync Schedule

```python
# Add to bot startup
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Sync products every hour
scheduler.add_job(
    integration_manager.sync_all,
    'interval',
    hours=1,
    id='sync_products'
)

scheduler.start()
```

---

## 🔧 Phase 2: Bitrix24 Integration

### Prerequisites
- [ ] Bitrix24 account (cloud or self-hosted)
- [ ] Webhook access
- [ ] CRM configured with stages

### Step 1: Get Webhook URL

1. **Login to Bitrix24**
2. **Navigate to:** Settings → Developer Resources → Inbound Webhooks
3. **Create Webhook:**
   - Name: `ZETA Bot`
   - Permissions: `CRM` (read/write), `Tasks` (write)
   - Copy webhook URL: `https://your-domain.bitrix24.com/rest/1/xxxxx/`

### Step 2: Test API Access

```bash
# Test connection
curl "https://your-domain.bitrix24.com/rest/1/xxxxx/profile.json"

# Create test lead
curl -X POST "https://your-domain.bitrix24.com/rest/1/xxxxx/crm.lead.add.json" \
  -d 'fields[TITLE]=Test Lead&fields[NAME]=John&fields[SOURCE_ID]=TELEGRAM'

# Get lead stages
curl "https://your-domain.bitrix24.com/rest/1/xxxxx/crm.status.list.json?filter[ENTITY_ID]=STATUS"
```

### Step 3: Configure CRM Pipeline

1. **Setup Lead Stages:**
   - CRM → Leads → Settings → Stages
   - Stages: NEW → IN_PROCESS → CONVERTED

2. **Setup Deal Stages:**
   - CRM → Deals → Settings → Stages
   - Stages: NEW → QUOTE → PAYMENT → WON

3. **Add Custom Fields (Optional):**
   - CRM → Settings → Custom Fields
   - Add: `UF_CRM_TELEGRAM_ID` (string)
   - Add: `UF_CRM_CITY` (string)

### Step 4: Configure ZETA Bot

1. **Edit `config/integrations.yaml`:**
```yaml
integrations:
  bitrix24:
    enabled: true
    webhook_url: ""  # Set via environment variable
    features:
      create_leads: true
      create_deals: true
```

2. **Set environment variable:**
```bash
export BITRIX24_WEBHOOK_URL="https://your-domain.bitrix24.com/rest/1/xxxxx/"
```

3. **Update `integrations/bitrix24.py`:**
   - Uncomment implementation code
   - Adjust field mappings
   - Test API calls

### Step 5: Test Integration

```python
# Test lead creation
async def test_bitrix24():
    from integrations.bitrix24 import Bitrix24Integration
    
    bitrix = Bitrix24Integration(
        webhook_url=os.getenv("BITRIX24_WEBHOOK_URL")
    )
    
    # Initialize
    success = await bitrix.initialize()
    print("Connected:", success)
    
    # Create test lead
    result = await bitrix.create_lead(
        user_data={
            "name": "Test User",
            "phone": "+77771234567",
            "telegram_id": "123456789"
        },
        conversation=[
            {"role": "user", "content": "Хочу купить диван"},
            {"role": "assistant", "content": "Какой бюджет?"}
        ]
    )
    print("Lead:", result)

asyncio.run(test_bitrix24())
```

### Step 6: Integrate with Bot

```python
# Add to conversation handler
from integrations.manager import integration_manager

async def handle_conversation_end(user_id: int, conversation: list):
    """Create lead when conversation ends without order."""
    
    user_data = await get_user_data(user_id)
    
    result = await integration_manager.integrations["bitrix24"].create_lead(
        user_data=user_data,
        conversation=conversation
    )
    
    if result["success"]:
        logger.info(f"Lead created: {result['lead_id']}")
```

---

## 🔧 Phase 3: Document Upload & Search

### Prerequisites
- [ ] Redis server running (for embeddings cache)
- [ ] OpenAI API key (for embeddings)
- [ ] Vector database (Pinecone/Qdrant/pgvector)

### Step 1: Install Dependencies

```bash
cd apps/bot
pip install PyPDF2 pandas openpyxl python-docx openai pinecone-client
```

### Step 2: Setup Vector Database

**Option A: Pinecone (Cloud)**
```python
import pinecone

pinecone.init(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment="us-west1-gcp"
)

# Create index
if "zeta-documents" not in pinecone.list_indexes():
    pinecone.create_index(
        name="zeta-documents",
        dimension=1536,  # text-embedding-3-small
        metric="cosine"
    )

index = pinecone.Index("zeta-documents")
```

**Option B: Qdrant (Self-hosted)**
```bash
docker run -p 6333:6333 qdrant/qdrant
```

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

client = QdrantClient(host="localhost", port=6333)

client.create_collection(
    collection_name="zeta_documents",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)
```

### Step 3: Implement Text Extraction

```python
# Add to api/app/routers/documents.py

import PyPDF2
import pandas as pd
from docx import Document

def extract_pdf_text(file_path: Path) -> str:
    text = ""
    with open(file_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

def extract_excel_text(file_path: Path) -> str:
    df = pd.read_excel(file_path)
    return df.to_string()

def extract_docx_text(file_path: Path) -> str:
    doc = Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])
```

### Step 4: Implement Embedding Generation

```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_embeddings(text: str) -> List[float]:
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding

def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start = end - overlap
    return chunks
```

### Step 5: Implement Document Indexing

```python
async def index_document(city_id: int, filename: str, text: str):
    chunks = chunk_text(text)
    
    for i, chunk in enumerate(chunks):
        # Generate embedding
        embedding = await generate_embeddings(chunk)
        
        # Store in vector DB (Pinecone example)
        index.upsert([(
            f"{city_id}_{filename}_{i}",
            embedding,
            {
                "city_id": city_id,
                "filename": filename,
                "chunk_index": i,
                "text": chunk
            }
        )])
```

### Step 6: Implement Search

```python
async def search_documents(city_id: int, query: str, limit: int = 5) -> List[Dict]:
    # Generate query embedding
    query_embedding = await generate_embeddings(query)
    
    # Search vector DB
    results = index.query(
        query_embedding,
        top_k=limit,
        filter={"city_id": city_id}
    )
    
    # Format results
    return [{
        "filename": match.metadata["filename"],
        "text": match.metadata["text"],
        "score": match.score
    } for match in results.matches]
```

### Step 7: Enable in Configuration

```yaml
# config/integrations.yaml
integrations:
  documents:
    enabled: true
    index_on_upload: true
    search:
      enabled: true
      embedding_model: "text-embedding-3-small"
```

---

## 🔧 Phase 4: Advanced Features

### Conversation Memory (Redis)

1. **Install Redis:**
```bash
docker run -d -p 6379:6379 redis:alpine
```

2. **Enable in config:**
```yaml
advanced:
  memory:
    enabled: true
    redis_url: "redis://localhost:6379/0"
```

3. **Use in bot:**
```python
from core.memory import init_conversation_memory

memory = init_conversation_memory(redis_url=os.getenv("REDIS_URL"))
await memory.connect()

# Save messages
await memory.save_message(user_id, "user", "Hello")

# Get history
history = await memory.get_history(user_id)
```

### Rate Limiting

1. **Enable in config:**
```yaml
advanced:
  rate_limit:
    enabled: true
    limit: 10
    window: 60
```

2. **Add to bot:**
```python
from core.rate_limiter import RateLimitMiddleware

rate_limiter = RateLimitMiddleware(
    redis_url=os.getenv("REDIS_URL"),
    limit=10,
    window=60
)

dp.message.middleware(rate_limiter)
```

### Multilanguage Support

1. **Enable in config:**
```yaml
advanced:
  i18n:
    enabled: true
    default_language: "ru"
    supported_languages: [ru, kk]
```

2. **Use in handlers:**
```python
from core.i18n import t, get_user_language

lang = get_user_language(user_id)
await message.answer(t("greeting", lang=lang))
```

---

## ✅ Verification Checklist

### 1C Integration
- [ ] HTTP service accessible
- [ ] Authentication working
- [ ] Products sync successfully
- [ ] Stock checks return correct data
- [ ] Orders created in 1C
- [ ] Field mappings correct
- [ ] Scheduled sync running

### Bitrix24 Integration
- [ ] Webhook accessible
- [ ] Leads created successfully
- [ ] Deals created from orders
- [ ] Tasks assigned to managers
- [ ] Custom fields populated
- [ ] Pipeline stages correct

### Document System
- [ ] Files upload successfully
- [ ] Text extraction working
- [ ] Embeddings generated
- [ ] Search returns relevant results
- [ ] Bot can query documents

### Advanced Features
- [ ] Redis connected
- [ ] Conversation history saved
- [ ] Rate limiting working
- [ ] Language switching functional

---

## 🐛 Troubleshooting

### 1C Connection Issues
- Check network connectivity: `ping 1c-server`
- Verify HTTP service published: Access via browser
- Check authentication: Test with curl
- Review 1C logs for errors

### Bitrix24 Issues
- Verify webhook URL format
- Check permissions in webhook settings
- Test with Bitrix24 REST API explorer
- Check rate limits (50 req/sec standard)

### Document Search Issues
- Verify OpenAI API key valid
- Check vector DB connection
- Monitor embedding costs
- Review chunk sizes and overlap

### Redis Issues
- Check Redis running: `redis-cli ping`
- Verify connection string
- Check memory limits
- Monitor key expiration

---

## 📊 Monitoring & Maintenance

### Logs to Monitor
```bash
tail -f /var/log/zeta/bot.log | grep -E "(1C|Bitrix|Integration)"
```

### Metrics to Track
- Integration call success/failure rates
- API response times
- Sync duration
- Document search relevance
- Redis memory usage

### Regular Tasks
- [ ] Weekly: Review integration logs
- [ ] Monthly: Check API usage and costs
- [ ] Quarterly: Update field mappings
- [ ] As needed: Rotate API credentials

---

**Ready to implement?** Follow phases sequentially. Test thoroughly at each step. Good luck! 🚀

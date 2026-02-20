# ZETA Bot Integrations

This directory contains the integration system for connecting ZETA bot with external services.

## Architecture

The integration system is built with:
- **Abstract base class** (`Integration`) - Common interface for all integrations
- **Integration Manager** - Centralized management and orchestration
- **Pluggable connectors** - Easy to add new integrations

## Available Integrations

### 1. 1C:Enterprise (`onec.py`)
**Status:** 🚧 Stub - Implementation pending

Integration with 1C for:
- Real-time inventory sync
- Price updates
- Order creation
- Stock availability checks

**Next Steps:**
1. Install 1C HTTP service extension
2. Configure API credentials
3. Map product fields (SKU, price, stock)
4. Test connection and data flow
5. Implement sync logic

**Configuration:** See `config/integrations.yaml` → `integrations.onec`

---

### 2. Bitrix24 CRM (`bitrix24.py`)
**Status:** 🚧 Stub - Implementation pending

Integration with Bitrix24 for:
- Lead creation from bot conversations
- Deal tracking
- Task assignment to managers
- Activity logging

**Next Steps:**
1. Get Bitrix24 webhook URL
2. Configure CRM field mappings
3. Setup lead/deal stages
4. Test API calls
5. Implement automation rules

**Configuration:** See `config/integrations.yaml` → `integrations.bitrix24`

---

## How to Add New Integration

1. **Create connector class:**
```python
# integrations/myservice.py
from . import Integration

class MyServiceIntegration(Integration):
    async def initialize(self) -> bool:
        # Test connection
        pass
    
    async def sync_products(self) -> Dict:
        # Sync logic
        pass
    
    async def create_order(self, order_data: dict) -> Dict:
        # Order creation
        pass
    
    async def check_availability(self, sku: str) -> Dict:
        # Availability check
        pass
```

2. **Register in manager:**
```python
from integrations.manager import integration_manager
from integrations.myservice import MyServiceIntegration

# Initialize
my_integration = MyServiceIntegration(api_url="...", api_key="...")

# Register
integration_manager.register("myservice", my_integration, enabled=True)
```

3. **Add configuration:**
```yaml
# config/integrations.yaml
integrations:
  myservice:
    enabled: true
    api_url: "https://api.myservice.com"
    api_key: "your_key_here"
```

4. **Test:**
```python
# Initialize all integrations
await integration_manager.initialize_all()

# Sync products
await integration_manager.sync_all()

# Create order
result = await integration_manager.create_order(
    "myservice", 
    order_data={...}
)
```

## Usage Examples

### Basic Setup

```python
from integrations.manager import integration_manager
from integrations.onec import OneCIntegration
from integrations.bitrix24 import Bitrix24Integration

# Create integrations
onec = OneCIntegration(
    api_url="http://1c-server/base/hs",
    username="bot_user",
    password="secret"
)

bitrix = Bitrix24Integration(
    webhook_url="https://your-domain.bitrix24.com/rest/1/xxxxx/"
)

# Register
integration_manager.register("1c", onec, enabled=True)
integration_manager.register("bitrix24", bitrix, enabled=True)

# Initialize
await integration_manager.initialize_all()
```

### Sync Products

```python
# Sync from all integrations
results = await integration_manager.sync_all()

# Check results
for name, result in results.items():
    if result["success"]:
        print(f"✓ {name}: {result['products_synced']} products")
    else:
        print(f"✗ {name}: {result['errors']}")
```

### Check Availability

```python
# Check across all integrations
availability = await integration_manager.check_availability("ART001")

for integration, info in availability.items():
    if info["available"]:
        print(f"{integration}: {info['quantity']} in stock @ {info['price']} KZT")
```

### Create Order

```python
order_data = {
    "customer": {
        "name": "Иван Петров",
        "phone": "+77771234567"
    },
    "products": [
        {"sku": "ART001", "quantity": 1, "price": 45000}
    ],
    "delivery": {
        "address": "Алматы, ул. Абая 10"
    },
    "total": 45000
}

# Create in 1C
result = await integration_manager.create_order("1c", order_data)

if result["success"]:
    print(f"Order created: {result['order_id']}")
```

### Get Status

```python
status = integration_manager.get_status()

for name, info in status.items():
    print(f"{name}: enabled={info['enabled']}, last_sync={info['last_sync']}")
```

## Configuration Loading

Load configuration from YAML:

```python
import yaml
from pathlib import Path

def load_integrations_config():
    config_path = Path(__file__).parent / "config" / "integrations.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

config = load_integrations_config()

# Setup 1C if enabled
if config["integrations"]["onec"]["enabled"]:
    onec = OneCIntegration(
        api_url=config["integrations"]["onec"]["api_url"],
        username=config["integrations"]["onec"]["username"],
        password=os.getenv("ONEC_PASSWORD")
    )
    integration_manager.register("1c", onec, enabled=True)
```

## Error Handling

All integration methods return structured results:

```python
{
    "success": bool,
    "error": str (optional),
    # ... method-specific fields
}
```

Handle errors gracefully:

```python
try:
    result = await integration.sync_products()
    
    if not result["success"]:
        logger.error(f"Sync failed: {result.get('error')}")
        # Fallback logic
    
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    # Retry or alert
```

## Logging

Integrations use standard Python logging:

```python
import logging

logger = logging.getLogger("integrations")
logger.setLevel(logging.INFO)

# Integration logs will appear as:
# INFO:integrations.onec: Product sync started
# ERROR:integrations.bitrix24: Connection failed
```

## Testing

Test integrations before enabling:

```python
# Test connection
success = await integration.initialize()

if success:
    print("✓ Connection successful")
else:
    print("✗ Connection failed")

# Test sync (dry run)
# TODO: Add dry_run parameter to methods
```

## TODO: Next Phase

- [ ] Implement 1C connector
- [ ] Implement Bitrix24 connector
- [ ] Add retry logic with exponential backoff
- [ ] Add webhook support for real-time updates
- [ ] Add metrics and monitoring
- [ ] Add integration tests
- [ ] Add circuit breaker pattern
- [ ] Add caching layer
- [ ] Add background sync scheduler
- [ ] Add admin UI for integration management

## Support

For integration issues:
1. Check logs in `/var/log/zeta/bot.log`
2. Verify configuration in `config/integrations.yaml`
3. Test connection with `initialize()` method
4. Check external service status
5. Review field mappings

## Security Notes

- Store sensitive credentials in environment variables
- Never commit API keys or passwords
- Use separate API users with minimal permissions
- Rotate credentials regularly
- Monitor API usage for anomalies
- Use HTTPS for all external connections

---

**Last Updated:** 2024-02-19  
**Status:** Foundation ready, implementations pending

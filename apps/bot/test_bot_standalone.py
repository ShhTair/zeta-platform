"""
Standalone test script to verify bot logic without Telegram
"""
import asyncio
import sys
from services.api_client import APIClient
from services.prompt_manager import PromptManager


async def test_api_client():
    """Test API client"""
    print("🧪 Testing API Client...")
    
    api_client = APIClient("http://localhost:8000")
    
    try:
        # Test city config
        print("  → Fetching city config...")
        config = await api_client.get_city_config("moscow")
        print(f"  ✅ Config loaded: {config.get('city_name', 'Unknown')}")
        
        # Test product search
        print("  → Searching products...")
        products = await api_client.search_products("laptop", "moscow", limit=3)
        print(f"  ✅ Found {len(products)} products")
        
        if products:
            print(f"     First product: {products[0].get('name', 'N/A')}")
        
    except Exception as e:
        print(f"  ❌ API Error: {e}")
        return False
    finally:
        await api_client.close()
    
    return True


async def test_prompt_manager():
    """Test prompt manager"""
    print("\n🧪 Testing Prompt Manager...")
    
    api_client = APIClient("http://localhost:8000")
    prompt_manager = PromptManager(api_client, "moscow", cache_ttl=60)
    
    try:
        # Load config
        print("  → Loading config...")
        await prompt_manager.load_config()
        print("  ✅ Config loaded")
        
        # Get prompt
        greeting = await prompt_manager.get_prompt("greeting", "Default greeting")
        print(f"  ✅ Greeting: {greeting[:50]}...")
        
        # Get manager
        manager = prompt_manager.manager_telegram_id
        print(f"  ✅ Manager: {manager or 'Not set'}")
        
    except Exception as e:
        print(f"  ❌ Prompt Manager Error: {e}")
        return False
    finally:
        await api_client.close()
    
    return True


async def main():
    """Run all tests"""
    print("=" * 60)
    print("ZETA Bot - Standalone Test Suite")
    print("=" * 60)
    print()
    print("⚠️  Make sure API is running on http://localhost:8000")
    print()
    
    results = []
    
    # Test API Client
    results.append(await test_api_client())
    
    # Test Prompt Manager
    results.append(await test_prompt_manager())
    
    # Summary
    print("\n" + "=" * 60)
    if all(results):
        print("✅ All tests passed!")
        print("=" * 60)
        return 0
    else:
        print("❌ Some tests failed")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))

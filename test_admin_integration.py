#!/usr/bin/env python3
"""
Test script for ZETA Bot - Admin Platform Integration
Tests all API endpoints and bot services
"""
import asyncio
import aiohttp
import sys
from datetime import datetime

API_URL = "http://localhost:8000"
CITY_ID = 1


async def test_bot_config_public():
    """Test public bot config endpoint (no auth)"""
    print("\n🧪 Testing: GET /cities/{city_id}/bot-config (public)")
    
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}/cities/{CITY_ID}/bot-config"
        async with session.get(url) as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"✅ Config loaded: {data.get('greeting_message', 'N/A')[:50]}...")
                return True
            elif resp.status == 404:
                print("⚠️ Config not found - Create one in admin first")
                return False
            else:
                print(f"❌ Failed: HTTP {resp.status}")
                return False


async def test_create_escalation():
    """Test creating an escalation"""
    print("\n🧪 Testing: POST /escalations")
    
    payload = {
        "city_id": CITY_ID,
        "user_telegram_id": 123456789,
        "user_name": "Test User",
        "product_sku": "TEST-SKU-001",
        "reason": "test_integration",
        "conversation": [
            {"role": "user", "text": "Test message", "timestamp": datetime.now().isoformat()}
        ]
    }
    
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}/escalations"
        async with session.post(url, json=payload) as resp:
            if resp.status in (200, 201):
                data = await resp.json()
                escalation_id = data.get('id')
                print(f"✅ Escalation created: ID {escalation_id}")
                return escalation_id
            else:
                text = await resp.text()
                print(f"❌ Failed: HTTP {resp.status} - {text}")
                return None


async def test_list_escalations():
    """Test listing escalations"""
    print("\n🧪 Testing: GET /cities/{city_id}/escalations (requires auth)")
    print("⚠️ This endpoint requires authentication - test manually with JWT token")
    return True


async def test_create_analytics_event():
    """Test creating an analytics event"""
    print("\n🧪 Testing: POST /analytics/events")
    
    payload = {
        "city_id": CITY_ID,
        "event_type": "test_event",
        "data": {
            "test": True,
            "timestamp": datetime.now().isoformat()
        }
    }
    
    async with aiohttp.ClientSession() as session:
        url = f"{API_URL}/analytics/events"
        async with session.post(url, json=payload) as resp:
            if resp.status in (200, 201):
                print(f"✅ Analytics event tracked")
                return True
            else:
                text = await resp.text()
                print(f"❌ Failed: HTTP {resp.status} - {text}")
                return False


async def test_get_analytics():
    """Test getting analytics"""
    print("\n🧪 Testing: GET /cities/{city_id}/analytics (requires auth)")
    print("⚠️ This endpoint requires authentication - test manually with JWT token")
    return True


async def test_config_manager():
    """Test ConfigManager class"""
    print("\n🧪 Testing: ConfigManager class")
    
    try:
        from apps.bot.core.config_manager import ConfigManager
        
        config_manager = ConfigManager(api_url=API_URL, city_id=CITY_ID, reload_interval=300)
        
        # Test load_config
        await config_manager.load_config()
        print(f"✅ Config loaded via ConfigManager")
        print(f"   - Greeting: {config_manager.greeting_message[:50] if config_manager.greeting_message else 'None'}...")
        print(f"   - Manager contact: {config_manager.manager_contact or 'None'}")
        print(f"   - Escalation action: {config_manager.escalation_action}")
        
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_escalation_logger():
    """Test EscalationLogger class"""
    print("\n🧪 Testing: EscalationLogger class")
    
    try:
        from apps.bot.core.escalation_logger import EscalationLogger
        
        logger = EscalationLogger(api_url=API_URL)
        
        success = await logger.log_escalation(
            city_id=CITY_ID,
            user_id=999999999,
            user_name="Test User (Logger)",
            product_sku="TEST-SKU-002",
            reason="test_logger_class",
            conversation_history=[{"role": "user", "text": "Test from logger"}]
        )
        
        if success:
            print(f"✅ EscalationLogger works")
        else:
            print(f"❌ EscalationLogger failed")
        
        return success
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def test_analytics_tracker():
    """Test AnalyticsTracker class"""
    print("\n🧪 Testing: AnalyticsTracker class")
    
    try:
        from apps.bot.core.analytics_tracker import AnalyticsTracker
        
        tracker = AnalyticsTracker(api_url=API_URL)
        
        # Test tracking different event types
        await tracker.track_search(CITY_ID, "test search", 5)
        await tracker.track_product_view(CITY_ID, "TEST-SKU-003")
        await tracker.track_escalation(CITY_ID, "test_tracker")
        
        print(f"✅ AnalyticsTracker works")
        return True
    except Exception as e:
        print(f"❌ Failed: {e}")
        return False


async def main():
    """Run all tests"""
    print("=" * 60)
    print("ZETA Bot - Admin Integration Test Suite")
    print("=" * 60)
    print(f"API URL: {API_URL}")
    print(f"City ID: {CITY_ID}")
    print("=" * 60)
    
    # Check if API is running
    print("\n🔍 Checking if API is running...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{API_URL}/") as resp:
                if resp.status == 200:
                    print("✅ API is running")
                else:
                    print(f"⚠️ API returned {resp.status}")
    except Exception as e:
        print(f"❌ API is not running: {e}")
        print("\n💡 Start the API first:")
        print("   cd apps/api")
        print("   uvicorn app.main:app --reload")
        sys.exit(1)
    
    results = []
    
    # Test API endpoints
    results.append(("Bot Config (Public)", await test_bot_config_public()))
    results.append(("Create Escalation", await test_create_escalation()))
    results.append(("Create Analytics Event", await test_create_analytics_event()))
    
    # Test bot classes
    results.append(("ConfigManager Class", await test_config_manager()))
    results.append(("EscalationLogger Class", await test_escalation_logger()))
    results.append(("AnalyticsTracker Class", await test_analytics_tracker()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("=" * 60)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("\n🎉 All tests passed! Integration is working correctly.")
    else:
        print("\n⚠️ Some tests failed. Check the output above.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)

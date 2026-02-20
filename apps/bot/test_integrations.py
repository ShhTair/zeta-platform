#!/usr/bin/env python3
"""
Integration System Test Script
Verifies that all integration modules are importable and properly structured
"""

import sys
from pathlib import Path

# Add bot directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test that all modules can be imported."""
    print("🧪 Testing imports...\n")
    
    tests = [
        ("Integration base class", "from integrations import Integration"),
        ("Integration manager", "from integrations.manager import IntegrationManager, integration_manager"),
        ("1C integration", "from integrations.onec import OneCIntegration"),
        ("Bitrix24 integration", "from integrations.bitrix24 import Bitrix24Integration"),
        ("Conversation memory", "from core.memory import ConversationMemory, init_conversation_memory"),
        ("Rate limiter", "from core.rate_limiter import RateLimitMiddleware"),
        ("i18n system", "from core.i18n import t, translations, LANGUAGE_NAMES"),
    ]
    
    passed = 0
    failed = 0
    
    for name, import_stmt in tests:
        try:
            exec(import_stmt)
            print(f"✅ {name}")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: {e}")
            failed += 1
    
    print(f"\n📊 Results: {passed} passed, {failed} failed")
    return failed == 0


def test_integration_interface():
    """Test that integrations implement required methods."""
    print("\n🧪 Testing integration interface...\n")
    
    from integrations import Integration
    from integrations.onec import OneCIntegration
    from integrations.bitrix24 import Bitrix24Integration
    
    required_methods = ['initialize', 'sync_products', 'create_order', 'check_availability']
    
    integrations_to_test = [
        ("OneCIntegration", OneCIntegration),
        ("Bitrix24Integration", Bitrix24Integration),
    ]
    
    passed = 0
    failed = 0
    
    for name, cls in integrations_to_test:
        print(f"Testing {name}:")
        
        # Check if it's a subclass
        if not issubclass(cls, Integration):
            print(f"  ❌ Not a subclass of Integration")
            failed += 1
            continue
        
        # Check methods
        for method in required_methods:
            if hasattr(cls, method):
                print(f"  ✅ {method}()")
                passed += 1
            else:
                print(f"  ❌ Missing {method}()")
                failed += 1
        
        print()
    
    print(f"📊 Results: {passed} passed, {failed} failed")
    return failed == 0


def test_manager():
    """Test integration manager functionality."""
    print("\n🧪 Testing integration manager...\n")
    
    from integrations.manager import IntegrationManager
    
    try:
        manager = IntegrationManager()
        
        # Test methods exist
        assert hasattr(manager, 'register'), "Missing register()"
        assert hasattr(manager, 'initialize_all'), "Missing initialize_all()"
        assert hasattr(manager, 'sync_all'), "Missing sync_all()"
        assert hasattr(manager, 'create_order'), "Missing create_order()"
        assert hasattr(manager, 'check_availability'), "Missing check_availability()"
        assert hasattr(manager, 'get_status'), "Missing get_status()"
        
        print("✅ IntegrationManager has all required methods")
        
        # Test registration (without actual integration instances)
        print("✅ IntegrationManager instantiates correctly")
        
        # Test status
        status = manager.get_status()
        assert isinstance(status, dict), "get_status() should return dict"
        print("✅ get_status() returns dict")
        
        print("\n📊 Manager test passed!")
        return True
    except Exception as e:
        print(f"❌ Manager test failed: {e}")
        return False


def test_i18n():
    """Test internationalization system."""
    print("\n🧪 Testing i18n system...\n")
    
    from core.i18n import t, translations, get_available_languages
    
    try:
        # Test translations exist
        assert "ru" in translations, "Russian translations missing"
        assert "kk" in translations, "Kazakh translations missing"
        print("✅ Russian and Kazakh translations loaded")
        
        # Test translation function
        greeting_ru = t("greeting", lang="ru")
        greeting_kk = t("greeting", lang="kk")
        
        assert greeting_ru != greeting_kk, "Translations should differ"
        assert "мебель" in greeting_ru.lower() or "жиһаз" in greeting_ru.lower(), "Translation should contain furniture reference"
        print(f"✅ Translation works: '{greeting_ru}'")
        
        # Test variable substitution
        price_text = t("product_price", lang="ru", price=45000)
        assert "45000" in price_text, "Variable substitution failed"
        print(f"✅ Variable substitution: '{price_text}'")
        
        # Test available languages
        langs = get_available_languages()
        assert "ru" in langs and "kk" in langs, "Available languages incorrect"
        print(f"✅ Available languages: {langs}")
        
        print("\n📊 i18n test passed!")
        return True
    except Exception as e:
        print(f"❌ i18n test failed: {e}")
        return False


def test_memory():
    """Test conversation memory (without Redis)."""
    print("\n🧪 Testing conversation memory...\n")
    
    try:
        from core.memory import ConversationMemory
        
        # Just test that class can be imported and has methods
        assert hasattr(ConversationMemory, 'save_message'), "Missing save_message()"
        assert hasattr(ConversationMemory, 'get_history'), "Missing get_history()"
        assert hasattr(ConversationMemory, 'get_context_for_llm'), "Missing get_context_for_llm()"
        assert hasattr(ConversationMemory, 'clear_history'), "Missing clear_history()"
        
        print("✅ ConversationMemory has all required methods")
        print("⚠️  Redis connection not tested (requires Redis server)")
        
        print("\n📊 Memory test passed!")
        return True
    except ImportError as e:
        print(f"⚠️  ConversationMemory requires redis package: {e}")
        return True  # Not a failure, just optional dependency
    except Exception as e:
        print(f"❌ Memory test failed: {e}")
        return False


def test_config_files():
    """Test that config files exist and are readable."""
    print("\n🧪 Testing configuration files...\n")
    
    import yaml
    
    config_file = Path(__file__).parent / "config" / "integrations.yaml"
    
    if not config_file.exists():
        print(f"❌ Config file not found: {config_file}")
        return False
    
    print(f"✅ Config file exists: {config_file}")
    
    try:
        with open(config_file) as f:
            config = yaml.safe_load(f)
        
        # Check structure
        assert "integrations" in config, "Missing 'integrations' section"
        assert "onec" in config["integrations"], "Missing 1C config"
        assert "bitrix24" in config["integrations"], "Missing Bitrix24 config"
        assert "documents" in config["integrations"], "Missing documents config"
        
        print("✅ Config structure valid")
        print(f"  • 1C enabled: {config['integrations']['onec']['enabled']}")
        print(f"  • Bitrix24 enabled: {config['integrations']['bitrix24']['enabled']}")
        print(f"  • Documents enabled: {config['integrations']['documents']['enabled']}")
        
        print("\n📊 Config test passed!")
        return True
    except Exception as e:
        print(f"❌ Config test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 60)
    print("ZETA Bot Integration System Tests")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Integration Interface": test_integration_interface(),
        "Manager": test_manager(),
        "i18n": test_i18n(),
        "Memory": test_memory(),
        "Config Files": test_config_files(),
    }
    
    print("\n" + "=" * 60)
    print("📊 FINAL RESULTS")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("✅ Integration foundation is ready for implementation")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("❌ Review errors above before proceeding")
    print("=" * 60)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())

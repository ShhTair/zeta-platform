#!/usr/bin/env python3
"""
Test Interactive Features
Quick smoke test for inline keyboards, buttons, callbacks
"""
import asyncio
import sys
from handlers.interactive import (
    create_product_list_keyboard,
    create_product_actions_keyboard,
    create_quick_filters_keyboard,
    create_quick_actions_menu,
)


def test_product_list_keyboard():
    """Test product list keyboard generation"""
    print("🧪 Testing product list keyboard...")
    
    products = [
        {"id": "1", "sku": "SK-001", "name": "Стул деревянный классический", "price": 45000},
        {"id": "2", "sku": "SK-002", "name": "Кресло офисное эргономичное", "price": 67500},
        {"id": "3", "sku": "SK-003", "name": "Диван угловой тканевый", "price": 185000},
        {"id": "4", "sku": "SK-004", "name": "Стол письменный", "price": 55000},
        {"id": "5", "sku": "SK-005", "name": "Шкаф распашной", "price": 95000},
        {"id": "6", "sku": "SK-006", "name": "Тумба прикроватная", "price": 12000},
    ]
    
    keyboard = create_product_list_keyboard(products, offset=0, show_more=True)
    
    assert len(keyboard.inline_keyboard) > 0, "Keyboard should have buttons"
    assert len(keyboard.inline_keyboard) <= 6, "Should have max 6 rows (5 products + nav)"
    
    # Check first button
    first_button = keyboard.inline_keyboard[0][0]
    assert "🪑" in first_button.text, "Button should have emoji"
    assert first_button.callback_data.startswith("prod_"), "Callback should start with 'prod_'"
    
    # Check navigation buttons
    last_row = keyboard.inline_keyboard[-1]
    has_more = any("Показать ещё" in btn.text for btn in last_row)
    has_new_search = any("Новый поиск" in btn.text for btn in last_row)
    
    assert has_more, "Should have 'Показать ещё' button"
    assert has_new_search, "Should have 'Новый поиск' button"
    
    print("  ✅ Product list keyboard OK")
    print(f"  • Generated {len(keyboard.inline_keyboard)} rows")
    print(f"  • First button: {first_button.text}")
    return True


def test_product_actions_keyboard():
    """Test product actions keyboard"""
    print("\n🧪 Testing product actions keyboard...")
    
    keyboard = create_product_actions_keyboard("SK-001", has_photo=True, has_website_link=True)
    
    assert len(keyboard.inline_keyboard) >= 3, "Should have at least 3 rows"
    
    # Flatten all buttons
    all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    button_texts = [btn.text for btn in all_buttons]
    
    assert any("📸" in text for text in button_texts), "Should have photo button"
    assert any("🔗" in text for text in button_texts), "Should have link button"
    assert any("💬" in text for text in button_texts), "Should have manager button"
    assert any("↩️" in text for text in button_texts), "Should have back button"
    
    print("  ✅ Product actions keyboard OK")
    print(f"  • Total buttons: {len(all_buttons)}")
    return True


def test_quick_filters_keyboard():
    """Test quick filters keyboard"""
    print("\n🧪 Testing quick filters keyboard...")
    
    keyboard = create_quick_filters_keyboard()
    
    assert len(keyboard.inline_keyboard) == 5, "Should have 5 filter options"
    
    all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    button_texts = [btn.text for btn in all_buttons]
    
    assert any("🏠" in text for text in button_texts), "Should have home filter"
    assert any("🏢" in text for text in button_texts), "Should have office filter"
    assert any("🎨" in text for text in button_texts), "Should have color filter"
    assert any("💰" in text for text in button_texts), "Should have price filter"
    
    print("  ✅ Quick filters keyboard OK")
    print(f"  • Filter options: {len(keyboard.inline_keyboard)}")
    return True


def test_quick_actions_menu():
    """Test quick actions menu"""
    print("\n🧪 Testing quick actions menu...")
    
    keyboard = create_quick_actions_menu()
    
    assert len(keyboard.inline_keyboard) == 4, "Should have 4 action options"
    
    all_buttons = [btn for row in keyboard.inline_keyboard for btn in row]
    button_texts = [btn.text for btn in all_buttons]
    
    assert any("🔍" in text for text in button_texts), "Should have search action"
    assert any("📸" in text for text in button_texts), "Should have photo search"
    assert any("🏷️" in text for text in button_texts), "Should have popular products"
    assert any("💬" in text for text in button_texts), "Should have contact"
    
    print("  ✅ Quick actions menu OK")
    print(f"  • Action buttons: {len(all_buttons)}")
    return True


def test_pagination():
    """Test pagination behavior"""
    print("\n🧪 Testing pagination...")
    
    # Create 15 products
    products = [
        {"id": str(i), "sku": f"SK-{i:03d}", "name": f"Product {i}", "price": i * 1000}
        for i in range(1, 16)
    ]
    
    # Page 1 (offset 0)
    keyboard_p1 = create_product_list_keyboard(products, offset=0, show_more=True)
    assert len(keyboard_p1.inline_keyboard) == 6, "Page 1 should have 5 products + nav"
    
    # Page 2 (offset 5)
    keyboard_p2 = create_product_list_keyboard(products, offset=5, show_more=True)
    assert len(keyboard_p2.inline_keyboard) == 6, "Page 2 should have 5 products + nav"
    
    # Page 3 (offset 10)
    keyboard_p3 = create_product_list_keyboard(products, offset=10, show_more=True)
    assert len(keyboard_p3.inline_keyboard) == 6, "Page 3 should have 5 products + nav"
    
    # Check "Show More" button presence
    last_row_p1 = keyboard_p1.inline_keyboard[-1]
    has_more_p1 = any("Показать ещё" in btn.text for btn in last_row_p1)
    assert has_more_p1, "Page 1 should have 'Show More' button"
    
    print("  ✅ Pagination OK")
    print(f"  • Total products: {len(products)}")
    print(f"  • Products per page: 5")
    print(f"  • Total pages: 3")
    return True


def test_button_callback_data():
    """Test callback data format"""
    print("\n🧪 Testing callback data format...")
    
    products = [
        {"id": "123", "sku": "SK-001", "name": "Test Product", "price": 50000}
    ]
    
    keyboard = create_product_list_keyboard(products, offset=0, show_more=False)
    
    # Check product button callback
    product_btn = keyboard.inline_keyboard[0][0]
    assert product_btn.callback_data == "prod_SK-001", f"Expected 'prod_SK-001', got '{product_btn.callback_data}'"
    
    # Check actions keyboard
    actions_kb = create_product_actions_keyboard("SK-001", has_photo=True)
    
    # Find photo button
    photo_btn = None
    for row in actions_kb.inline_keyboard:
        for btn in row:
            if "📸" in btn.text:
                photo_btn = btn
                break
    
    assert photo_btn is not None, "Should have photo button"
    assert photo_btn.callback_data == "photo_SK-001", f"Expected 'photo_SK-001', got '{photo_btn.callback_data}'"
    
    print("  ✅ Callback data format OK")
    print(f"  • Product callback: {product_btn.callback_data}")
    print(f"  • Photo callback: {photo_btn.callback_data}")
    return True


def main():
    """Run all tests"""
    print("=" * 60)
    print("🎨 Interactive Features Test Suite")
    print("=" * 60)
    
    tests = [
        test_product_list_keyboard,
        test_product_actions_keyboard,
        test_quick_filters_keyboard,
        test_quick_actions_menu,
        test_pagination,
        test_button_callback_data,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
        except AssertionError as e:
            print(f"  ❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"  💥 ERROR: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    if failed == 0:
        print("✅ All tests passed! Interactive UI is ready.")
        return 0
    else:
        print("❌ Some tests failed. Please fix issues before deployment.")
        return 1


if __name__ == "__main__":
    sys.exit(main())

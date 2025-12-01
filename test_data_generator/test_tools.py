"""Test script to verify all data generation tools work correctly."""

import sys
import json

# Test imports
try:
    from tools.personal_data import (
        generate_names,
        generate_emails,
        generate_phone_numbers,
        generate_addresses,
        generate_user_profiles,
    )
    from tools.business_data import (
        generate_company_names,
        generate_product_names,
        generate_prices,
        generate_invoice_data,
    )
    from tools.numeric_data import (
        generate_integers,
        generate_floats,
        generate_dates,
        generate_timestamps,
        generate_uuids,
    )
    from tools.custom_patterns import (
        generate_from_regex,
        generate_from_format,
        generate_json_data,
        generate_csv_data,
    )
    print("✓ All imports successful")
except Exception as e:
    print(f"✗ Import failed: {e}")
    sys.exit(1)


def test_personal_data():
    """Test personal data generation tools."""
    print("\n--- Testing Personal Data Tools ---")
    
    try:
        names = generate_names(count=3)
        print(f"✓ generate_names: {names}")
        
        emails = generate_emails(count=3, domain="test.com")
        print(f"✓ generate_emails: {emails}")
        
        phones = generate_phone_numbers(count=2)
        print(f"✓ generate_phone_numbers: {phones}")
        
        addresses = generate_addresses(count=2)
        print(f"✓ generate_addresses: Generated {len(addresses)} addresses")
        
        profiles = generate_user_profiles(count=1)
        print(f"✓ generate_user_profiles: Generated {len(profiles)} profile(s)")
        
        return True
    except Exception as e:
        print(f"✗ Personal data test failed: {e}")
        return False


def test_business_data():
    """Test business data generation tools."""
    print("\n--- Testing Business Data Tools ---")
    
    try:
        companies = generate_company_names(count=3)
        print(f"✓ generate_company_names: {companies}")
        
        products = generate_product_names(count=2)
        print(f"✓ generate_product_names: {products}")
        
        prices = generate_prices(count=3, min_price=10.0, max_price=100.0)
        print(f"✓ generate_prices: Generated {len(prices)} prices")
        
        invoices = generate_invoice_data(count=1)
        print(f"✓ generate_invoice_data: Generated {len(invoices)} invoice(s)")
        
        return True
    except Exception as e:
        print(f"✗ Business data test failed: {e}")
        return False


def test_numeric_data():
    """Test numeric data generation tools."""
    print("\n--- Testing Numeric Data Tools ---")
    
    try:
        integers = generate_integers(count=5, min_value=1, max_value=100)
        print(f"✓ generate_integers: {integers}")
        
        floats = generate_floats(count=3, min_value=0.0, max_value=10.0, precision=2)
        print(f"✓ generate_floats: {floats}")
        
        dates = generate_dates(count=3)
        print(f"✓ generate_dates: {dates}")
        
        timestamps = generate_timestamps(count=2)
        print(f"✓ generate_timestamps: {timestamps}")
        
        uuids = generate_uuids(count=2)
        print(f"✓ generate_uuids: {uuids}")
        
        return True
    except Exception as e:
        print(f"✗ Numeric data test failed: {e}")
        return False


def test_custom_patterns():
    """Test custom pattern generation tools."""
    print("\n--- Testing Custom Pattern Tools ---")
    
    try:
        regex_data = generate_from_regex(pattern=r"[A-Z]{3}-\d{4}", count=3)
        print(f"✓ generate_from_regex: {regex_data}")
        
        format_data = generate_from_format(format_string="USER-{number:5}", count=2)
        print(f"✓ generate_from_format: {format_data}")
        
        schema = {"id": "uuid", "name": "name", "active": "boolean"}
        json_data = generate_json_data(schema=schema, count=2)
        print(f"✓ generate_json_data: Generated JSON with {len(json.loads(json_data))} records")
        
        csv_data = generate_csv_data(
            columns=["id", "name", "email"],
            column_types=["uuid", "name", "email"],
            count=2
        )
        print(f"✓ generate_csv_data: Generated CSV with {len(csv_data.split(chr(10)))} lines")
        
        return True
    except Exception as e:
        print(f"✗ Custom pattern test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("="*60)
    print("Test Data Generator - Tool Verification")
    print("="*60)
    
    results = []
    results.append(("Personal Data", test_personal_data()))
    results.append(("Business Data", test_business_data()))
    results.append(("Numeric Data", test_numeric_data()))
    results.append(("Custom Patterns", test_custom_patterns()))
    
    print("\n" + "="*60)
    print("Test Summary")
    print("="*60)
    
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())

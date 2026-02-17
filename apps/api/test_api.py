#!/usr/bin/env python3
"""
Quick API test script
"""
import requests
import sys

BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✓ Health check passed")
            return True
        else:
            print(f"✗ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Health check error: {e}")
        return False


def test_auth():
    """Test authentication"""
    try:
        # Try to login with default admin
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "admin@zeta.local", "password": "admin123"}
        )
        
        if response.status_code == 200:
            token = response.json()["access_token"]
            print("✓ Login successful")
            
            # Test protected endpoint
            headers = {"Authorization": f"Bearer {token}"}
            response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
            
            if response.status_code == 200:
                user = response.json()
                print(f"✓ Auth verified: {user['email']} ({user['role']})")
                return True
            else:
                print(f"✗ Auth verification failed: {response.status_code}")
                return False
        else:
            print(f"✗ Login failed: {response.status_code}")
            print("  Note: Make sure to run init_db.py first to create admin user")
            return False
    except Exception as e:
        print(f"✗ Auth test error: {e}")
        return False


def test_cities():
    """Test cities endpoint"""
    try:
        # Login first
        response = requests.post(
            f"{BASE_URL}/auth/login",
            json={"email": "admin@zeta.local", "password": "admin123"}
        )
        
        if response.status_code != 200:
            print("✗ Cannot test cities: login failed")
            return False
        
        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        # List cities
        response = requests.get(f"{BASE_URL}/cities", headers=headers)
        if response.status_code == 200:
            cities = response.json()
            print(f"✓ Cities endpoint works ({len(cities)} cities)")
            return True
        else:
            print(f"✗ Cities endpoint failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Cities test error: {e}")
        return False


def main():
    print("=" * 50)
    print("ZETA Platform API - Quick Test")
    print("=" * 50)
    print("\nMake sure the API server is running:")
    print("  uvicorn app.main:app --reload\n")
    
    results = []
    
    print("Testing endpoints...")
    results.append(("Health Check", test_health()))
    results.append(("Authentication", test_auth()))
    results.append(("Cities API", test_cities()))
    
    print("\n" + "=" * 50)
    print("Test Results")
    print("=" * 50)
    
    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
Test script for user registration API
"""
import requests
import json
import sys

# API endpoint
BASE_URL = "http://localhost:5001"
REGISTER_ENDPOINT = f"{BASE_URL}/api/v1/airliner/registerUser"

# Test users data
test_users = [
    {
        "username": "john_doe",
        "firstName": "John",
        "lastName": "Doe",
        "email": "john.doe@example.com",
        "password": "SecurePass123",
        "dateOfBirth": "1990-01-15"
    },
    {
        "username": "jane_smith",
        "firstName": "Jane",
        "lastName": "Smith",
        "email": "jane.smith@example.com",
        "password": "MySecurePass456",
        "dateOfBirth": "1992-05-20"
    },
    {
        "username": "bob_wilson",
        "firstName": "Bob",
        "lastName": "Wilson",
        "email": "bob.wilson@example.com",
        "password": "TestPassword789",
        "dateOfBirth": "1988-11-10"
    }
]


def test_register_user(user_data, headers=None):
    """Test user registration"""
    if headers is None:
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    
    print(f"\n{'='*60}")
    print(f"Testing user registration for: {user_data['username']}")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            REGISTER_ENDPOINT,
            json=user_data,
            headers=headers,
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response Body: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Body (text): {response.text}")
        
        return response.status_code, response.json() if response.headers.get('content-type', '').startswith('application/json') else response.text
        
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to the service. Is it running?")
        return None, None
    except Exception as e:
        print(f"ERROR: {str(e)}")
        return None, None


def main():
    """Run all tests"""
    print("="*60)
    print("USER REGISTRATION API TESTS")
    print("="*60)
    
    # Check if service is running
    try:
        health_check = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Service health check: {health_check.status_code}")
    except:
        print("WARNING: Service health check failed, but continuing with tests...")
    
    results = []
    
    # Test 1: Register first user
    print("\n[TEST 1] Registering first user...")
    status, response = test_register_user(test_users[0])
    results.append(("Test 1 - First User", status, status == 201))
    
    # Test 2: Register second user
    print("\n[TEST 2] Registering second user...")
    status, response = test_register_user(test_users[1])
    results.append(("Test 2 - Second User", status, status == 201))
    
    # Test 3: Register third user
    print("\n[TEST 3] Registering third user...")
    status, response = test_register_user(test_users[2])
    results.append(("Test 3 - Third User", status, status == 201))
    
    # Test 4: Try to register duplicate user (should fail)
    print("\n[TEST 4] Attempting to register duplicate user...")
    status, response = test_register_user(test_users[0])
    results.append(("Test 4 - Duplicate User", status, status != 201))
    
    # Test 5: Register user with missing fields
    print("\n[TEST 5] Attempting to register user with missing fields...")
    incomplete_user = {
        "username": "incomplete_user",
        "email": "incomplete@example.com"
        # Missing password, firstName, etc.
    }
    status, response = test_register_user(incomplete_user)
    results.append(("Test 5 - Incomplete Data", status, status != 201))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for test_name, status, passed in results:
        status_str = f"Status: {status}" if status else "Status: N/A"
        result_str = " PASSED" if passed else " FAILED"
        print(f"{test_name}: {result_str} ({status_str})")
    
    passed_count = sum(1 for _, _, passed in results if passed)
    total_count = len(results)
    print(f"\nTotal: {passed_count}/{total_count} tests passed")
    
    return 0 if passed_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())


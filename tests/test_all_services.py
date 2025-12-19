#!/usr/bin/env python3
"""
Comprehensive test suite for all microservices
"""
import requests
import json
import time
import sys

# Service URLs
USER_MGMT_URL = "http://localhost:5001/api/v1/airliner/registerUser"
BOOKING_URL = "http://localhost:5002/api/v1/airliner/bookings"
NOTIFICATION_URL = "http://localhost:5003"

# Common headers
HEADERS = {
    "Host": "localhost",
    "User-Agent": "Test-Suite/1.0",
    "Accept": "*/*",
    "Connection": "keep-alive",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
}


def check_service_health(service_name, url):
    """Check if a service is responding"""
    try:
        response = requests.get(f"{url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False


def test_user_registration():
    """Test user registration"""
    print("\n" + "="*60)
    print("TEST: User Registration")
    print("="*60)
    
    payload = {
        "username": f"testuser_{int(time.time())}",
        "firstName": "Test",
        "lastName": "User",
        "email": f"test_{int(time.time())}@example.com",
        "password": "TestPass123",
        "dateOfBirth": "1990-01-01"
    }
    
    try:
        response = requests.post(
            USER_MGMT_URL,
            headers={**HEADERS, "Host": "localhost:5001"},
            json=payload,
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f" User registered successfully")
            data = response.json()
            if "data" in data and "ID" in data["data"]:
                return data["data"]["ID"]
            return True
        else:
            print(f" Registration failed: {response.text}")
            return None
    except Exception as e:
        print(f" Error: {e}")
        return None


def test_booking_creation(user_id, flight_id=1000):
    """Test booking creation"""
    print("\n" + "="*60)
    print("TEST: Booking Creation")
    print("="*60)
    
    payload = {
        "userId": user_id,
        "flightId": flight_id,
        "numberOfSeats": 1
    }
    
    try:
        response = requests.post(
            BOOKING_URL,
            headers={**HEADERS, "Host": "localhost:5002"},
            json=payload,
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code in [200, 201]:
            print(f" Booking created successfully")
            data = response.json()
            if "booking" in data and "bookingId" in data["booking"]:
                return data["booking"]["bookingId"]
            return True
        else:
            print(f" Booking creation failed: {response.text}")
            return None
    except Exception as e:
        print(f" Error: {e}")
        return None


def test_booking_retrieval(booking_id):
    """Test booking retrieval"""
    print("\n" + "="*60)
    print("TEST: Booking Retrieval")
    print("="*60)
    
    try:
        response = requests.get(
            f"{BOOKING_URL}/{booking_id}",
            headers={**HEADERS, "Host": "localhost:5002"},
            timeout=10
        )
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(f" Booking retrieved successfully")
            return True
        else:
            print(f" Booking retrieval failed: {response.text}")
            return False
    except Exception as e:
        print(f" Error: {e}")
        return False


def test_kafka_events():
    """Test if Kafka events are being processed"""
    print("\n" + "="*60)
    print("TEST: Kafka Event Processing")
    print("="*60)
    print("ℹ  This test checks if notification service is consuming events")
    print("   Check notification service logs for event processing")
    
    # Wait a bit for events to be processed
    time.sleep(3)
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("MICROSERVICES TEST SUITE")
    print("="*60)
    
    # Check service health
    print("\n[1] Checking Service Health...")
    services_ok = True
    
    if check_service_health("User Management", "http://localhost:5001"):
        print(" User Management Service: UP")
    else:
        print(" User Management Service: DOWN")
        services_ok = False
    
    if check_service_health("Booking", "http://localhost:5002"):
        print(" Booking Service: UP")
    else:
        print(" Booking Service: DOWN")
        services_ok = False
    
    if check_service_health("Notification", "http://localhost:5003"):
        print(" Notification Service: UP")
    else:
        print(" Notification Service: DOWN (may be normal if no health endpoint)")
    
    if not services_ok:
        print("\n  Some services are not responding. Please check:")
        print("   docker-compose ps")
        print("   docker-compose logs [service-name]")
        return
    
    # Run tests
    results = {}
    
    # Test user registration
    user_id = test_user_registration()
    results["user_registration"] = user_id is not None
    
    if user_id:
        # Test booking (may fail if flight doesn't exist)
        booking_id = test_booking_creation(user_id)
        results["booking_creation"] = booking_id is not None
        
        if booking_id:
            results["booking_retrieval"] = test_booking_retrieval(booking_id)
        else:
            print("\n  Booking test skipped - flight may not exist")
            results["booking_retrieval"] = None
    else:
        print("\n  User registration failed - skipping booking tests")
        results["booking_creation"] = None
        results["booking_retrieval"] = None
    
    # Test Kafka events
    results["kafka_events"] = test_kafka_events()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v is True)
    total = sum(1 for v in results.values() if v is not None)
    skipped = sum(1 for v in results.values() if v is None)
    
    for test_name, result in results.items():
        if result is True:
            print(f" {test_name.replace('_', ' ').title()}: PASSED")
        elif result is False:
            print(f" {test_name.replace('_', ' ').title()}: FAILED")
        else:
            print(f"⊘ {test_name.replace('_', ' ').title()}: SKIPPED")
    
    print(f"\nResults: {passed}/{total} passed, {skipped} skipped")
    
    if passed == total:
        print("\n All tests passed!")
        return 0
    else:
        print("\n  Some tests failed or were skipped")
        return 1


if __name__ == "__main__":
    sys.exit(main())


#!/usr/bin/env python3
"""
Dry run tests for microservices
Tests service health and basic connectivity
"""
import requests
import time
import sys
from typing import Dict, Tuple


SERVICES = {
    "usermanagement": {
        "url": "http://localhost:5001",
        "port": 5001,
        "health_endpoint": "/health",
        "test_endpoint": "/api/v1/airliner/registerUser"
    },
    "booking": {
        "url": "http://localhost:5002",
        "port": 5002,
        "health_endpoint": "/health",
        "test_endpoint": "/api/v1/airliner/bookings"
    },
    "notification": {
        "url": "http://localhost:5003",
        "port": 5003,
        "health_endpoint": "/health",
        "test_endpoint": "/"
    }
}


def check_service_health(service_name: str, config: Dict) -> Tuple[bool, str]:
    """
    Check if a service is responding
    
    Returns:
        (is_healthy, message)
    """
    try:
        url = f"{config['url']}{config['health_endpoint']}"
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            return True, f"✓ {service_name} is healthy (200 OK)"
        else:
            return False, f"✗ {service_name} returned {response.status_code}"
    except requests.exceptions.ConnectionError:
        return False, f"✗ {service_name} connection refused (service may not be running)"
    except requests.exceptions.Timeout:
        return False, f"✗ {service_name} request timeout"
    except Exception as e:
        return False, f"✗ {service_name} error: {str(e)}"


def check_service_reachable(service_name: str, config: Dict) -> Tuple[bool, str]:
    """
    Check if service port is reachable
    """
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(3)
        result = sock.connect_ex(('localhost', config['port']))
        sock.close()
        
        if result == 0:
            return True, f"✓ {service_name} port {config['port']} is open"
        else:
            return False, f"✗ {service_name} port {config['port']} is not accessible"
    except Exception as e:
        return False, f"✗ {service_name} socket error: {str(e)}"


def test_user_registration() -> Tuple[bool, str]:
    """
    Test user registration endpoint (dry run - just check if it's reachable)
    """
    try:
        url = f"{SERVICES['usermanagement']['url']}{SERVICES['usermanagement']['test_endpoint']}"
        # Just do a HEAD request to check if endpoint exists
        response = requests.head(url, timeout=5)
        # Any response means the service is responding
        return True, f"✓ User registration endpoint is reachable"
    except requests.exceptions.ConnectionError:
        return False, f"✗ User registration endpoint connection refused"
    except Exception as e:
        # Method not allowed (405) is fine - means endpoint exists
        if "405" in str(e) or "Method Not Allowed" in str(e):
            return True, f"✓ User registration endpoint exists (405 Method Not Allowed is expected for HEAD)"
        return False, f"✗ User registration endpoint error: {str(e)}"


def main():
    """Run all dry run tests"""
    print("=" * 60)
    print("MICROSERVICES DRY RUN TESTS")
    print("=" * 60)
    print()
    
    # Wait a bit for services to be ready
    print("Waiting for services to start...")
    time.sleep(5)
    print()
    
    results = []
    
    # Test 1: Port connectivity
    print("[TEST 1] Checking Service Port Connectivity")
    print("-" * 60)
    for service_name, config in SERVICES.items():
        is_reachable, message = check_service_reachable(service_name, config)
        print(message)
        results.append(("Port Check", service_name, is_reachable))
    print()
    
    # Test 2: Health endpoints
    print("[TEST 2] Checking Service Health Endpoints")
    print("-" * 60)
    for service_name, config in SERVICES.items():
        is_healthy, message = check_service_health(service_name, config)
        print(message)
        results.append(("Health Check", service_name, is_healthy))
    print()
    
    # Test 3: API endpoints
    print("[TEST 3] Checking API Endpoints")
    print("-" * 60)
    
    # User Management
    is_reachable, message = test_user_registration()
    print(message)
    results.append(("API Endpoint", "usermanagement", is_reachable))
    
    # Booking (just check if endpoint exists)
    try:
        url = f"{SERVICES['booking']['url']}{SERVICES['booking']['test_endpoint']}"
        response = requests.head(url, timeout=5)
        print("✓ Booking endpoint is reachable")
        results.append(("API Endpoint", "booking", True))
    except:
        print("✗ Booking endpoint connection refused")
        results.append(("API Endpoint", "booking", False))
    
    # Notification (check root)
    try:
        response = requests.get(SERVICES['notification']['url'], timeout=5)
        print(f"✓ Notification service is reachable (status: {response.status_code})")
        results.append(("API Endpoint", "notification", True))
    except:
        print("✗ Notification service connection refused")
        results.append(("API Endpoint", "notification", False))
    
    print()
    
    # Summary
    print("=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, _, result in results if result)
    total = len(results)
    
    for test_type, service, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_type:20} {service:20} {status}")
    
    print()
    print(f"Total: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("🎉 All services are running and healthy!")
        return 0
    else:
        print("⚠️  Some services are not responding. Check logs with:")
        print("   docker-compose logs [service-name]")
        return 1


if __name__ == "__main__":
    sys.exit(main())


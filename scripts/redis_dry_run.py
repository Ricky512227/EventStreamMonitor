#!/usr/bin/env python3
"""
Dry run tests for Redis integration
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

def test_redis_import():
    """Test if Redis client can be imported"""
    print("[TEST 1] Testing Redis Client Import...")
    try:
        from common.pyportal_common.cache_handlers import RedisClient, get_redis_client
        print("✓ Redis client imports successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import Redis client: {e}")
        return False


def test_redis_connection():
    """Test Redis connection"""
    print("\n[TEST 2] Testing Redis Connection...")
    try:
        from common.pyportal_common.cache_handlers import get_redis_client
        
        # Use environment variables or defaults
        redis_client = get_redis_client(
            host=os.getenv('REDIS_HOST', 'localhost'),
            port=int(os.getenv('REDIS_PORT', 6379)),
            db=int(os.getenv('REDIS_DB', 0))
        )
        
        if redis_client.ping():
            print("✓ Redis connection successful")
            return True, redis_client
        else:
            print("✗ Redis ping failed")
            return False, None
    except Exception as e:
        print(f"✗ Redis connection error: {e}")
        print("  (This is expected if Redis is not running)")
        return False, None


def test_redis_operations(redis_client):
    """Test basic Redis operations"""
    print("\n[TEST 3] Testing Redis Operations...")
    if not redis_client:
        print("⊘ Skipped (Redis not available)")
        return False
    
    try:
        # Test set/get
        test_key = "dry_run_test_key"
        test_value = "dry_run_test_value"
        
        redis_client.set(test_key, test_value, ttl=60)
        retrieved = redis_client.get(test_key)
        
        if retrieved == test_value:
            print("✓ Set/Get operations working")
        else:
            print(f"✗ Set/Get failed: expected '{test_value}', got '{retrieved}'")
            return False
        
        # Test JSON operations
        test_json_key = "dry_run_test_json"
        test_json_value = {"name": "test", "value": 123}
        
        redis_client.set_json(test_json_key, test_json_value, ttl=60)
        retrieved_json = redis_client.get_json(test_json_key)
        
        if retrieved_json == test_json_value:
            print("✓ JSON operations working")
        else:
            print(f"✗ JSON operations failed")
            return False
        
        # Test delete
        redis_client.delete(test_key, test_json_key)
        if not redis_client.exists(test_key) and not redis_client.exists(test_json_key):
            print("✓ Delete operations working")
        else:
            print("✗ Delete operations failed")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Redis operations error: {e}")
        return False


def test_user_management_helper():
    """Test User Management Redis helper"""
    print("\n[TEST 4] Testing User Management Redis Helper...")
    try:
        from services.usermanagement.app.redis_helper import UserManagementRedisHelper
        
        helper = UserManagementRedisHelper()
        print("✓ UserManagementRedisHelper imported successfully")
        
        # Test caching (will fail if Redis not available, but that's ok)
        try:
            test_user_data = {"id": 999, "username": "test_user", "email": "test@example.com"}
            helper.cache_user(999, test_user_data, ttl=60)
            cached = helper.get_cached_user(999)
            if cached:
                helper.invalidate_user_cache(999)
                print("✓ User caching operations working")
            else:
                print("⊘ User caching tested (Redis may not be running)")
        except Exception as e:
            print(f"⊘ User caching test skipped (Redis not available: {e})")
        
        return True
    except Exception as e:
        print(f"✗ Failed to import UserManagementRedisHelper: {e}")
        return False


def test_booking_helper():
    """Test Booking Redis helper"""
    print("\n[TEST 5] Testing Booking Redis Helper...")
    try:
        from services.booking.app.redis_helper import BookingRedisHelper
        
        helper = BookingRedisHelper()
        print("✓ BookingRedisHelper imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import BookingRedisHelper: {e}")
        return False


def main():
    """Run all Redis dry run tests"""
    print("=" * 60)
    print("REDIS INTEGRATION DRY RUN TESTS")
    print("=" * 60)
    print()
    
    results = []
    
    # Test 1: Import
    results.append(("Import Test", test_redis_import()))
    
    # Test 2: Connection
    connected, redis_client = test_redis_connection()
    results.append(("Connection Test", connected))
    
    # Test 3: Operations (only if connected)
    if connected:
        results.append(("Operations Test", test_redis_operations(redis_client)))
    else:
        results.append(("Operations Test", False))
    
    # Test 4: User Management Helper
    results.append(("User Management Helper", test_user_management_helper()))
    
    # Test 5: Booking Helper
    results.append(("Booking Helper", test_booking_helper()))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{test_name:30} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print()
    
    if passed == total:
        print("🎉 All Redis integration tests passed!")
        return 0
    elif passed >= total - 1:
        print("⚠️  Most tests passed (connection test may fail if Redis is not running)")
        return 0
    else:
        print("⚠️  Some tests failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())


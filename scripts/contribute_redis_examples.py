#!/usr/bin/env python3
"""
Redis-py Usage Examples

This script demonstrates common redis-py usage patterns that can be
contributed to the redis-py project as examples.

These examples can be used to contribute to:
https://github.com/redis/redis-py/issues/1744
"""
import redis
from typing import Optional


def example_basic_operations():
    """Basic Redis operations example"""
    print("=" * 60)
    print("Example 1: Basic Redis Operations")
    print("=" * 60)
    
    # Connect to Redis
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    # String operations
    r.set('user:1000:name', 'John Doe')
    name = r.get('user:1000:name')
    print(f"Set and retrieved: {name}")
    
    # Hash operations
    r.hset('user:1000', mapping={
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': '30'
    })
    user_data = r.hgetall('user:1000')
    print(f"User data: {user_data}")
    
    # List operations
    r.lpush('tasks', 'task1', 'task2', 'task3')
    tasks = r.lrange('tasks', 0, -1)
    print(f"Tasks: {tasks}")
    
    # Set operations
    r.sadd('tags', 'python', 'redis', 'database')
    tags = r.smembers('tags')
    print(f"Tags: {tags}")
    
    # Expiration
    r.setex('session:abc123', 3600, 'active')
    ttl = r.ttl('session:abc123')
    print(f"Session TTL: {ttl} seconds")


def example_connection_pooling():
    """Redis connection pooling example"""
    print("\n" + "=" * 60)
    print("Example 2: Connection Pooling")
    print("=" * 60)
    
    # Create connection pool
    pool = redis.ConnectionPool(
        host='localhost',
        port=6379,
        db=0,
        max_connections=50,
        decode_responses=True
    )
    
    # Use pool for multiple connections
    r1 = redis.Redis(connection_pool=pool)
    r2 = redis.Redis(connection_pool=pool)
    
    # Both connections share the same pool
    r1.set('key1', 'value1')
    value = r2.get('key1')
    print(f"Shared pool - retrieved from r2: {value}")


def example_pipeline():
    """Redis pipeline example for batch operations"""
    print("\n" + "=" * 60)
    print("Example 3: Pipeline for Batch Operations")
    print("=" * 60)
    
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    # Use pipeline for multiple operations
    pipe = r.pipeline()
    pipe.set('counter', 0)
    pipe.incr('counter')
    pipe.incr('counter')
    pipe.get('counter')
    results = pipe.execute()
    
    print(f"Pipeline results: {results}")
    print(f"Final counter value: {results[-1]}")


def example_pubsub():
    """Redis pub/sub example"""
    print("\n" + "=" * 60)
    print("Example 4: Pub/Sub Pattern")
    print("=" * 60)
    
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    pubsub = r.pubsub()
    
    # Subscribe to a channel
    pubsub.subscribe('notifications')
    
    # Publish a message (in a real app, this would be in another process)
    r.publish('notifications', 'Hello, subscribers!')
    
    # Get message
    message = pubsub.get_message(timeout=1)
    if message and message['type'] == 'message':
        print(f"Received: {message['data']}")
    
    pubsub.unsubscribe('notifications')
    pubsub.close()


def example_transactions():
    """Redis transaction example"""
    print("\n" + "=" * 60)
    print("Example 5: Transactions (MULTI/EXEC)")
    print("=" * 60)
    
    r = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    
    # Start transaction
    pipe = r.pipeline()
    pipe.multi()
    pipe.set('balance:user1', 100)
    pipe.decr('balance:user1', 50)
    pipe.get('balance:user1')
    results = pipe.execute()
    
    print(f"Transaction results: {results}")
    print(f"Final balance: {results[-1]}")


def example_error_handling():
    """Redis error handling example"""
    print("\n" + "=" * 60)
    print("Example 6: Error Handling")
    print("=" * 60)
    
    try:
        r = redis.Redis(
            host='localhost',
            port=6379,
            db=0,
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=5
        )
        
        # Test connection
        r.ping()
        print("✓ Connected to Redis successfully")
        
        # Try operation that might fail
        result = r.get('nonexistent_key')
        if result is None:
            print("Key doesn't exist (expected behavior)")
        
    except redis.ConnectionError as e:
        print(f"✗ Connection error: {e}")
    except redis.TimeoutError as e:
        print(f"✗ Timeout error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def main():
    """Run all examples"""
    print("\n" + "=" * 60)
    print("REDIS-PY USAGE EXAMPLES")
    print("=" * 60)
    print("\nThese examples demonstrate common redis-py patterns.")
    print("They can be contributed to: https://github.com/redis/redis-py/issues/1744")
    print()
    
    try:
        example_basic_operations()
        example_connection_pooling()
        example_pipeline()
        example_pubsub()
        example_transactions()
        example_error_handling()
        
        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)
        print("\nTo contribute these examples:")
        print("1. Fork https://github.com/redis/redis-py")
        print("2. Create examples/ directory")
        print("3. Add these examples as separate .py files")
        print("4. Submit a pull request")
        
    except redis.ConnectionError:
        print("\n⚠️  Redis is not running. Start Redis with:")
        print("   docker run -d -p 6379:6379 redis:latest")
        print("\nOr install and start Redis locally.")


if __name__ == "__main__":
    main()


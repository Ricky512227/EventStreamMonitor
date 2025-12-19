#!/usr/bin/env python3
"""
Continuous error event streamer to Kafka
Streams errors periodically for testing and demonstration
"""
import sys
import os
import time
import random
from datetime import datetime
from kafka import KafkaProducer
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

SERVICES = ['usermanagement', 'booking', 'notification', 'logmonitor']
ERROR_MESSAGES = [
    {
        'level': 'ERROR',
        'message': 'Database connection timeout after 30s',
        'module': 'db_handlers',
        'function': 'connect_to_database'
    },
    {
        'level': 'CRITICAL',
        'message': 'Service unavailable - all database connections exhausted',
        'module': 'db_pool_manager',
        'function': 'get_connection'
    },
    {
        'level': 'ERROR',
        'message': 'Invalid request format - missing required field: userId',
        'module': 'views',
        'function': 'validate_request'
    },
    {
        'level': 'ERROR',
        'message': 'Failed to send notification - Kafka producer error',
        'module': 'kafka_producer',
        'function': 'publish_notification'
    },
    {
        'level': 'CRITICAL',
        'message': 'Memory usage exceeded 90% threshold',
        'module': 'monitoring',
        'function': 'check_resources'
    },
    {
        'level': 'ERROR',
        'message': 'Authentication failed - invalid JWT token',
        'module': 'auth',
        'function': 'verify_token'
    },
    {
        'level': 'ERROR',
        'message': 'Rate limit exceeded for user: 12345',
        'module': 'rate_limiter',
        'function': 'check_rate_limit'
    },
    {
        'level': 'ERROR',
        'message': 'External API call failed - HTTP 503',
        'module': 'external_client',
        'function': 'call_external_api'
    }
]


def create_kafka_producer(kafka_servers: str):
    """Create Kafka producer"""
    try:
        producer = KafkaProducer(
            bootstrap_servers=kafka_servers.split(','),
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3
        )
        return producer
    except Exception as e:
        print(f" Failed to create Kafka producer: {e}")
        return None


def send_error_to_kafka(producer, service_name: str, error_data: dict):
    """Send error event to Kafka"""
    log_data = {
        'timestamp': datetime.utcnow().isoformat(),
        'level': error_data['level'],
        'logger': f'{service_name}.{error_data["module"]}',
        'message': error_data['message'],
        'module': error_data['module'],
        'function': error_data['function'],
        'line': random.randint(1, 500),
        'service': service_name,
        'host': f'{service_name}-service',
        'thread': random.randint(1, 100),
        'process': os.getpid()
    }
    
    try:
        # Send to error topic
        topic = 'application-logs-errors' if error_data['level'] in ['ERROR', 'CRITICAL'] else 'application-logs'
        future = producer.send(topic, log_data)
        future.get(timeout=5)  # Wait for send confirmation
        return True
    except Exception as e:
        print(f" Failed to send to Kafka: {e}")
        return False


def main():
    """Stream errors to Kafka"""
    print("=" * 60)
    print("ERROR EVENT STREAMER - Streaming to Kafka")
    print("=" * 60)
    print()
    
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    print(f"Kafka Bootstrap Servers: {kafka_servers}")
    
    # Create producer
    producer = create_kafka_producer(kafka_servers)
    if not producer:
        return 1
    
    print(" Kafka producer connected")
    print()
    print("Streaming errors... (Press Ctrl+C to stop)")
    print("-" * 60)
    
    try:
        count = 0
        while True:
            service = random.choice(SERVICES)
            error = random.choice(ERROR_MESSAGES)
            
            if send_error_to_kafka(producer, service, error):
                count += 1
                print(f"[{count}] {error['level']} - {service} - {error['message'][:50]}")
            else:
                print(f" Failed to send error event")
            
            # Random interval between 2-5 seconds
            time.sleep(random.uniform(2, 5))
    
    except KeyboardInterrupt:
        print()
        print("-" * 60)
        print(f"\n Stopped. Sent {count} error events to Kafka")
        print()
        print("Check dashboard: http://localhost:5004")
    
    finally:
        producer.flush()
        producer.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


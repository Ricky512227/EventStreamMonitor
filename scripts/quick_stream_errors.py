#!/usr/bin/env python3
"""
Quick script to stream error events directly to Kafka
No dependencies on local imports - pure Kafka producer
"""
from kafka import KafkaProducer
import json
import time
from datetime import datetime

# Error events to stream
ERROR_EVENTS = [
    {
        'level': 'ERROR',
        'service': 'usermanagement',
        'message': 'Database connection timeout after 30 seconds',
        'module': 'db_handlers',
        'function': 'connect_to_database',
        'line': 145
    },
    {
        'level': 'CRITICAL',
        'service': 'booking',
        'message': 'Service unavailable - all database connections exhausted',
        'module': 'db_pool_manager',
        'function': 'get_connection',
        'line': 89
    },
    {
        'level': 'ERROR',
        'service': 'notification',
        'message': 'Failed to send notification - Kafka producer error',
        'module': 'kafka_producer',
        'function': 'publish_notification',
        'line': 234
    },
    {
        'level': 'ERROR',
        'service': 'usermanagement',
        'message': 'Invalid request format - missing required field: userId',
        'module': 'views',
        'function': 'validate_request',
        'line': 67
    },
    {
        'level': 'CRITICAL',
        'service': 'booking',
        'message': 'Memory usage exceeded 90% threshold',
        'module': 'monitoring',
        'function': 'check_resources',
        'line': 156
    }
]


def stream_errors():
    """Stream error events to Kafka"""
    print("=" * 60)
    print("Streaming Error Events to Kafka")
    print("=" * 60)
    print()
    
    try:
        producer = KafkaProducer(
            bootstrap_servers=['localhost:9092'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            acks='all',
            retries=3
        )
        print("✅ Connected to Kafka")
        print()
    except Exception as e:
        print(f"❌ Failed to connect to Kafka: {e}")
        print("Make sure Kafka is running: docker-compose up -d kafka")
        return 1
    
    print(f"Streaming {len(ERROR_EVENTS)} error events...")
    print("-" * 60)
    
    for i, error in enumerate(ERROR_EVENTS, 1):
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': error['level'],
            'logger': f"{error['service']}.{error['module']}",
            'message': error['message'],
            'module': error['module'],
            'function': error['function'],
            'line': error['line'],
            'service': error['service'],
            'host': f"{error['service']}-service",
            'thread': 100 + i,
            'process': 1234
        }
        
        try:
            # Send to error topic
            topic = 'application-logs-errors'
            future = producer.send(topic, log_data)
            future.get(timeout=5)  # Wait for confirmation
            print(f"[{i}/{len(ERROR_EVENTS)}] ✅ {error['level']} - {error['service']}: {error['message'][:50]}")
        except Exception as e:
            print(f"[{i}/{len(ERROR_EVENTS)}] ❌ Failed: {e}")
        
        time.sleep(0.3)  # Small delay
    
    producer.flush()
    producer.close()
    
    print()
    print("-" * 60)
    print("✅ All error events sent to Kafka!")
    print()
    print("Next steps:")
    print("1. Check dashboard: http://localhost:5004")
    print("2. Check API: curl http://localhost:5004/api/v1/logs/errors")
    print("3. Check Kafka: docker-compose exec kafka kafka-console-consumer \\")
    print("                  --bootstrap-server localhost:9092 \\")
    print("                  --topic application-logs-errors --from-beginning")
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(stream_errors())


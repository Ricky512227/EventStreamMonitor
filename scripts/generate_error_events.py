#!/usr/bin/env python3
"""
Script to generate test error events and stream them to Kafka
"""
import sys
import os
import time
import random
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.pyportal_common.logging_handlers.kafka_log_handler import KafkaLogHandler
from common.pyportal_common.logging_handlers.base_logger import LogMonitor
import logging

# Service names for testing
SERVICES = ['usermanagement', 'booking', 'notification', 'logmonitor']
ERROR_TYPES = [
    'Database connection failed',
    'Invalid user input',
    'Authentication failed',
    'Resource not found',
    'Internal server error',
    'Timeout error',
    'Validation error',
    'Permission denied',
    'Rate limit exceeded',
    'External API error'
]


def generate_error_event(service_name: str, logger: logging.Logger):
    """Generate a random error event"""
    error_type = random.choice(ERROR_TYPES)
    error_level = random.choice(['ERROR', 'CRITICAL'])
    
    if error_level == 'ERROR':
        logger.error(f"[{service_name}] {error_type} - Test error event at {datetime.now()}")
    else:
        logger.critical(f"[{service_name}] {error_type} - CRITICAL error event at {datetime.now()}")


def generate_exception_error(service_name: str, logger: logging.Logger):
    """Generate an error with exception"""
    try:
        # Simulate an exception
        result = 1 / 0
    except ZeroDivisionError as e:
        logger.exception(f"[{service_name}] Division by zero error occurred", exc_info=True)


def main():
    """Generate multiple error events"""
    print("=" * 60)
    print("ERROR EVENT GENERATOR - Streaming to Kafka")
    print("=" * 60)
    print()
    
    # Get Kafka bootstrap servers from environment or use default
    kafka_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'localhost:9092')
    print(f"Kafka Bootstrap Servers: {kafka_servers}")
    print()
    
    # Create logger with Kafka handler
    logger = logging.getLogger('error_generator')
    logger.setLevel(logging.INFO)
    
    # Add Kafka handler
    try:
        kafka_handler = KafkaLogHandler(
            kafka_bootstrap_servers=kafka_servers,
            topic='application-logs',
            level=logging.INFO
        )
        kafka_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(kafka_handler)
        print("✅ Kafka log handler initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Kafka handler: {e}")
        print("Make sure Kafka is running and accessible")
        return 1
    
    # Also add console handler for visibility
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(levelname)s - %(message)s'
    ))
    logger.addHandler(console_handler)
    
    print()
    print("Generating error events...")
    print("-" * 60)
    
    # Generate errors
    num_errors = 10
    for i in range(num_errors):
        service = random.choice(SERVICES)
        
        # Set service name in environment for log metadata
        os.environ['SERVICE_NAME'] = service
        os.environ['HOSTNAME'] = f"{service}-service"
        
        # Generate different types of errors
        if i % 3 == 0:
            generate_exception_error(service, logger)
        else:
            generate_error_event(service, logger)
        
        # Add some info/warning logs too
        if i % 4 == 0:
            logger.warning(f"[{service}] Warning: This is a test warning message")
        
        time.sleep(0.5)  # Small delay between events
    
    print()
    print("-" * 60)
    print(f"✅ Generated {num_errors} error events")
    print()
    print("Check the dashboard at: http://localhost:5004")
    print("Or check Kafka topics:")
    print(f"  docker-compose exec kafka kafka-console-consumer \\")
    print(f"    --bootstrap-server localhost:9092 \\")
    print(f"    --topic application-logs-errors \\")
    print(f"    --from-beginning")
    print()
    
    # Flush Kafka handler
    kafka_handler.close()
    
    return 0


if __name__ == "__main__":
    sys.exit(main())


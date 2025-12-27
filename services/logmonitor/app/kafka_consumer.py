"""

Kafka Consumer for Error Log Monitoring

Filters error logs and stores them for dashboard

"""

import json

import os

from typing import Optional, Dict, Any, List

from kafka import KafkaConsumer

from kafka.errors import KafkaError

from threading import Thread

from datetime import datetime, timedelta

from collections import deque

class ErrorLogStore:

    """

    In-memory store for error logs (can be replaced with database)

    """

    def __init__(self, max_size: int = 1000):

        """

        Initialize error log store

        Args:

            max_size: Maximum number of error logs to keep

        """

        self.errors: deque = deque(maxlen=max_size)

        self.error_stats: Dict[str, int] = {}

        self.service_stats: Dict[str, int] = {}

    def add_error(self, error_log: Dict[str, Any]):

        """Add error log to store"""

        self.errors.append({

            **error_log,

            'received_at': datetime.utcnow().isoformat()

        })

        # Update statistics

        level = error_log.get('level', 'UNKNOWN')

        self.error_stats[level] = self.error_stats.get(level, 0) + 1

        service = error_log.get('service', 'unknown')

        self.service_stats[service] = self.service_stats.get(service, 0) + 1

    def get_errors(self, limit: int = 100, service: Optional[str] = None) -> List[Dict[str, Any]]:

        """

        Get recent errors

        Args:

            limit: Maximum number of errors to return

            service: Filter by service name (optional)

        Returns:

            List of error logs

        """

        errors = list(self.errors)

        if service:

            errors = [e for e in errors if e.get('service') == service]

        return errors[-limit:]

    def get_stats(self) -> Dict[str, Any]:

        """Get error statistics"""

        return {

            'total_errors': len(self.errors),

            'by_level': dict(self.error_stats),

            'by_service': dict(self.service_stats),

            'recent_errors': len([e for e in self.errors 

                                 if datetime.fromisoformat(e['received_at'].replace('Z', '+00:00')) > 

                                 datetime.utcnow() - timedelta(hours=1)])

        }

# Global error log store

error_store = ErrorLogStore(max_size=1000)

def start_error_log_consumer(logger) -> Thread:

    """

    Start Kafka consumer for error logs

    Args:

        logger: Logger instance

    Returns:

        Thread running the consumer

    """

    kafka_bootstrap_servers = os.getenv(

        'KAFKA_BOOTSTRAP_SERVERS', 

        'localhost:9092'

    )

    topics = [

        'application-logs-errors',

        'application-logs'  # Also consume all logs to filter errors

    ]

    def consume_logs():

        """Consumer function"""

        consumer = None

        try:

            logger.info(f"Starting Kafka consumer for topics: {topics}")

            consumer = KafkaConsumer(

                *topics,

                bootstrap_servers=kafka_bootstrap_servers.split(','),

                value_deserializer=lambda m: json.loads(m.decode('utf-8')),

                auto_offset_reset='latest',

                enable_auto_commit=True,

                group_id='log-monitor-group',

                consumer_timeout_ms=1000

            )

            logger.info("Kafka consumer started successfully")

            for message in consumer:

                try:

                    log_data = message.value

                    # Filter errors (ERROR, CRITICAL levels)

                    level = log_data.get('level', '').upper()

                    if level in ['ERROR', 'CRITICAL', 'EXCEPTION']:

                        logger.info(f"Error log received: {log_data.get('message', '')[:100]}")

                        error_store.add_error(log_data)

                except Exception as e:

                    logger.error(f"Error processing log message: {e}")

        except KafkaError as e:

            logger.error(f"Kafka error: {e}")

        except Exception as e:

            logger.error(f"Consumer error: {e}")

        finally:

            if consumer:

                consumer.close()

            logger.info("Kafka consumer stopped")

    # Start consumer in background thread

    consumer_thread = Thread(target=consume_logs, daemon=True)

    consumer_thread.start()

    logger.info("Error log consumer thread started")

    return consumer_thread

# Export for use in __init__.py

init_error_log_consumer = type('obj', (object,), {

    'start_error_log_consumer': start_error_log_consumer

})

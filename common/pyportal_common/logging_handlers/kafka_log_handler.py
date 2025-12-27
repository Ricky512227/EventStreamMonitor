"""
Kafka Log Handler for streaming logs to Kafka
"""
import json
import logging
import os
from datetime import datetime
from typing import Optional
from kafka import KafkaProducer
from kafka.errors import KafkaError


class KafkaLogHandler(logging.Handler):
    """
    Custom logging handler that sends log records to Kafka
    """

    def __init__(self, 
                 kafka_bootstrap_servers: str,
                 topic: str = "application-logs",
                 level: int = logging.NOTSET):
        """
        Initialize Kafka log handler

        Args:
            kafka_bootstrap_servers: Kafka broker addresses (comma-separated)
            topic: Kafka topic to send logs to
            level: Logging level
        """
        super().__init__(level)
        self.topic = topic
        self.kafka_bootstrap_servers = kafka_bootstrap_servers
        self.producer: Optional[KafkaProducer] = None
        self._init_producer()

    def _init_producer(self):
        """Initialize Kafka producer"""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_bootstrap_servers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                acks='all',
                retries=3,
                max_in_flight_requests_per_connection=1
            )
        except Exception as e:
            print(f"Failed to initialize Kafka producer: {e}")
            self.producer = None

    def emit(self, record: logging.LogRecord):
        """
        Emit a log record to Kafka

        Args:
            record: LogRecord instance
        """
        if not self.producer:
            return

        try:
            # Format log message
            log_data = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': self.format(record),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno,
                'service': os.getenv('SERVICE_NAME', 'unknown'),
                'host': os.getenv('HOSTNAME', 'unknown'),
                'thread': record.thread,
                'process': record.process
            }

            # Add exception info if present
            if record.exc_info:
                log_data['exception'] = self.format(record)

            # Determine topic based on log level
            topic = self.topic
            if record.levelno >= logging.ERROR:
                topic = f"{self.topic}-errors"

            # Send to Kafka
            future = self.producer.send(topic, log_data)
            # Fire and forget - don't wait for response
            future.add_errback(self._on_send_error)

        except Exception as e:
            self.handleError(record)
            print(f"Error sending log to Kafka: {e}")

    def _on_send_error(self, exception):
        """Handle Kafka send errors"""
        print(f"Kafka send error: {exception}")

    def close(self):
        """Close the handler and flush producer"""
        if self.producer:
            self.producer.flush()
            self.producer.close()
        super().close()


def setup_kafka_logging(logger: logging.Logger,
                        kafka_bootstrap_servers: str,
                        topic: str = "application-logs",
                        level: int = logging.INFO) -> KafkaLogHandler:
    """
    Setup Kafka logging for a logger

    Args:
        logger: Logger instance
        kafka_bootstrap_servers: Kafka broker addresses
        topic: Kafka topic name
        level: Logging level

    Returns:
        KafkaLogHandler instance
    """
    handler = KafkaLogHandler(
        kafka_bootstrap_servers=kafka_bootstrap_servers,
        topic=topic,
        level=level
    )
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(handler)
    return handler

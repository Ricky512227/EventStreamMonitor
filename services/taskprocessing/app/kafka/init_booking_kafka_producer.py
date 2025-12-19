from common.pyportal_common.kafka_service_handlers.producer_handlers.base_producer_init import (
    init_pyportal_kafka_producer,
)


def start_booking_kafka_producer(booking_logger):
    """Validate data"""
    try:
        pyportal_kafka_producer = init_pyportal_kafka_producer(
            booking_logger
        )
        pyportal_kafka_producer.assign_topic_to_producer("task-events")
        booking_logger.info("Kafka producer initialized for task processing service")
        return pyportal_kafka_producer
    except Exception as ex:
        booking_logger.warning(f"Failed to initialize Kafka producer: {ex}")
        return None


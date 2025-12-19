from src.pyportal_common.kafka_service_handlers.producer_handlers.base_producer_init import (
    init_pyportal_kafka_producer,
)


def start_booking_kafka_producer(booking_logger):
    """
    Initialize Kafka producer for booking service.
    Publishes booking events to 'booking-events' topic.
    """
    try:
        pyportal_kafka_producer = init_pyportal_kafka_producer(
            booking_logger
        )
        # Set topic for booking events
        pyportal_kafka_producer.assign_topic_to_producer("booking-events")
        booking_logger.info("Kafka producer initialized for booking service")
        return pyportal_kafka_producer
    except Exception as ex:
        booking_logger.warning(f"Failed to initialize Kafka producer: {ex}")
        return None


import os
from common.pyportal_common.kafka_service_handlers.producer_handlers.notfication_producer import PyPortalKafkaProducer


def init_pyportal_kafka_producer(cmn_logger):
    """
    Initialize Kafka producer with configuration from environment variables.
    Defaults to kafka:29092 for Docker Compose networking.
    """
    producer_ip_address = os.environ.get("KAFKA_BOOTSTRAP_SERVER", "kafka")
    producer_port = int(os.environ.get("KAFKA_PORT", "29092"))
    notif_producer = PyPortalKafkaProducer(
        logger_instance=cmn_logger,
        producer_ip_address=producer_ip_address,
        producer_port=producer_port,
    )
    # Topic will be set by the calling service
    # notif_producer.assign_topic_to_producer("emailtobenotfiedtouser")
    return notif_producer

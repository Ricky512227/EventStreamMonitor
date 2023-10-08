from pyportal_common.kafka_service_handlers.producer_handlers.notfication_producer import PyPortalKafkaProducer


def init_pyportal_kafka_producer(cmn_logger):
    producer_ip_address = "127.0.0.1"
    producer_port = 29092
    notif_producer = PyPortalKafkaProducer(
        logger_instance=cmn_logger,
        producer_ip_address=producer_ip_address,
        producer_port=producer_port,
    )
    notif_producer.assign_topic_to_producer("emailtobenotfiedtouser")
    # notif_producer.publish_data_to_producer(1, 20)
    # notif_producer.close_the_producer()
    return notif_producer

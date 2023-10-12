from src.pyportal_common.kafka_service_handlers.producer_handlers.base_producer_init import (
                init_pyportal_kafka_producer,
            )

def start_user_management_kafka_producer(user_management_logger):
    pyportal_kafka_producer = init_pyportal_kafka_producer(
        user_management_logger
    )
    return pyportal_kafka_producer

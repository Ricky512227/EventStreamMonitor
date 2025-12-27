from common.pyportal_common.kafka_service_handlers.producer_handlers.base_producer_init import (

    init_pyportal_kafka_producer,

)

def start_user_management_kafka_producer(user_management_logger):

    """

    Initialize Kafka producer for user management service.

    Publishes user registration events to 'user-registration-events' topic.

    """

    try:

        pyportal_kafka_producer = init_pyportal_kafka_producer(

            user_management_logger

        )

        # Set topic for user registration events

        pyportal_kafka_producer.assign_topic_to_producer(

            "user-registration-events"

        )

        user_management_logger.info(

            "Kafka producer initialized for user management service"

        )

        return pyportal_kafka_producer

    except Exception as ex:

        user_management_logger.warning(

            f"Failed to initialize Kafka producer: {ex}"

        )

        return None

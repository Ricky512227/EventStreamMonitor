# pylint: disable=line-too-long

"""
This module contains the main entry point for the Notification service.

It initializes the server, configures settings, and starts Kafka consumer.
"""
import sys
import threading
from app import (
    notification_app,
    notification_logger,
    kafka_consumer,
)
from common.pyportal_common.utils import mask_ip_address

if __name__ == "__main__":
    print("Starting notification service")
    try:
        server_ip = notification_app.config["NOTIFICATION_SERVER_IPADDRESS"]
        masked_server_ip = mask_ip_address(server_ip)
        notification_logger.info(
            "Bound NOTIFICATION-SERVICE at IP-ADDRESS:PORT :: %s:%s",
            masked_server_ip,
            notification_app.config["NOTIFICATION_SERVER_PORT"],
        )
        notification_logger.info("Started the NOTIFICATION server ...")
        notification_logger.info("Kafka consumer is listening for events...")
        
        # Start Kafka consumer in background thread
        if kafka_consumer:
            consumer_thread = threading.Thread(
                target=kafka_consumer.start_consuming,
                daemon=True
            )
            consumer_thread.start()
            notification_logger.info("Kafka consumer thread started")
        
        notification_logger.info("Application is ready to serve traffic.")
        notification_app.run(
            host=notification_app.config["NOTIFICATION_SERVER_IPADDRESS"],
            port=notification_app.config["NOTIFICATION_SERVER_PORT"],
        )

    except Exception as ex:
        notification_logger.exception(
            "Error occurred :: %s\tLine No:: %s",
            ex,
            sys.exc_info()[2].tb_lineno
        )


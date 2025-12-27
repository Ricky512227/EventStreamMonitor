# pylint: disable=line-too-long

import os

import sys

from logging import Logger

from flask import Flask, Blueprint, jsonify

# Add parent directory to path for common imports

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from common.pyportal_common.logging_handlers.base_logger import LogMonitor

from common.pyportal_common.app_handlers.app_manager import AppHandler

from app.app_configs import init_app_configs

from app.models.notification_model import NotificationBase

# Initialize variables

notification_logger = None

notification_app = None

kafka_consumer = None

try:

    # Set the notification service directory as the current dir

    currentDir = os.getcwd()

    # Initialize the logger for the notification service

    notification_logger: Logger = LogMonitor("notification").logger

    notification_logger.info(

        "Environment variables loaded from docker-compose"

    )

    notification_manager: AppHandler = AppHandler(

        logger_instance=notification_logger

    )

    notification_app: Flask = notification_manager.create_app_instance()

    if notification_app is None:

        notification_logger.error("App creation failed")

        sys.exit()

    init_app_configs(notification_app)

    # Add health check endpoint (before database initialization)

    @notification_app.route('/health', methods=['GET'])

    def health():

        """Health check endpoint"""

        return jsonify({

            'status': 'healthy',

            'service': 'notification'

        }), 200

    # Create the blueprint for the notification service

    notification_bp: Blueprint = (

        notification_manager.create_blueprint_instance()

    )

    if notification_bp is None:

        notification_logger.error(

            "Blue print creation failed for the App"

        )

        sys.exit()

    from common.pyportal_common.db_handlers.db_init import (

        start_database_creation_work

    )

    app_manager_db_obj = start_database_creation_work(

        notification_logger, NotificationBase, notification_app

    )

    if app_manager_db_obj:

        # Initialize Kafka consumer

        try:

            from app.notification_kafka import (

                init_notification_kafka_consumer,

            )

            kafka_consumer = init_notification_kafka_consumer.start_notification_kafka_consumer(

                notification_logger

            )

        except Exception as ex:

            notification_logger.warning(

                f"Failed to initialize Kafka consumer: {ex}"

            )

            kafka_consumer = None

        notification_manager.register_blueprint_for_service(

            app_instance=notification_app,

            blueprint_instance=notification_bp,

        )

        notification_manager.display_registered_blueprints_for_service(

            app_instance=notification_app

        )

except Exception as ex:

    print(f"Exception in __init__: {ex}")

    import traceback

    traceback.print_exc()

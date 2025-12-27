"""

Log Monitoring Service

Consumes logs from Kafka, filters errors, and provides API for dashboard

"""

import os

import sys

from logging import Logger

from flask import Flask

# Add parent directory to path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from common.pyportal_common.logging_handlers.base_logger import LogMonitor

from common.pyportal_common.app_handlers.app_manager import AppHandler

# Initialize variables

logmonitor_logger = None

logmonitor_app = None

kafka_consumer = None

try:

    # Initialize logger

    logmonitor_logger: Logger = LogMonitor("logmonitor").logger

    logmonitor_logger.info("Initializing Log Monitoring Service")

    # Create Flask app

    logmonitor_manager: AppHandler = AppHandler(

        logger_instance=logmonitor_logger

    )

    logmonitor_app: Flask = logmonitor_manager.create_app_instance()

    if logmonitor_app is None:

        logmonitor_logger.error("App creation failed")

        sys.exit(1)

    # Initialize Kafka consumer for error logs

    try:

        from app.kafka_consumer import init_error_log_consumer

        kafka_consumer = init_error_log_consumer.start_error_log_consumer(

            logmonitor_logger

        )

        logmonitor_logger.info("Kafka error log consumer initialized")

    except Exception as ex:

        logmonitor_logger.warning(f"Failed to initialize Kafka consumer: {ex}")

        kafka_consumer = None

    # Register API routes

    from app.routes import register_routes

    register_routes(logmonitor_app, logmonitor_logger)

    logmonitor_logger.info("Log Monitoring Service initialized successfully")

except Exception as ex:

    print(f"Exception in __init__: {ex}")

    import traceback

    traceback.print_exc()

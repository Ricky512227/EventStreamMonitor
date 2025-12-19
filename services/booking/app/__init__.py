# pylint: disable=line-too-long
import os
import sys
import concurrent.futures
from logging import Logger
from flask import Flask, Blueprint

# Add parent directory to path for common imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from common.pyportal_common.logging_handlers.base_logger import LogMonitor
from common.pyportal_common.app_handlers.app_manager import AppHandler
from app.app_configs import init_app_configs
from app.models.booking_model import BookingBase

# Initialize variables
booking_logger = None
booking_app = None
booking_grpc_server = None
booking_kafka_producer = None

try:
    # Set the booking service directory as the current dir
    service_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Schema file paths
    booking_req_schema_filepath = os.path.join(
        service_dir,
        "schemas/requests/create_booking/"
        "req_schema.json"
    )
    booking_headers_schema_filepath = os.path.join(
        service_dir,
        "schemas/headers/"
        "booking_headers_schema.json"
    )

    # Initialize the logger for the booking service
    booking_logger: Logger = LogMonitor("flightbooking").logger
    booking_logger.info(
        "Environment variables loaded from docker-compose"
    )
    booking_manager: AppHandler = AppHandler(
        logger_instance=booking_logger
    )
    booking_app: Flask = booking_manager.create_app_instance()
    if booking_app is None:
        booking_logger.error("App creation failed")
        sys.exit()

    init_app_configs(booking_app)
    
    # Load and Validate Schema Files
    (
        booking_headers_schema_status,
        booking_headers_schema,
    ) = booking_manager.read_json_schema(booking_headers_schema_filepath)
    (
        booking_req_schema_status,
        booking_req_schema,
    ) = booking_manager.read_json_schema(booking_req_schema_filepath)
    
    # Export schemas for use in views
    __all__ = [
        "booking_logger",
        "booking_app",
        "booking_manager",
        "app_manager_db_obj",
        "booking_headers_schema",
        "booking_req_schema",
        "booking_kafka_producer",
    ]

    # Create the blueprint for the booking service
    booking_bp: Blueprint = (
        booking_manager.create_blueprint_instance()
    )
    if booking_bp is None:
        booking_logger.error(
            "Blue print creation failed for the App"
        )
        sys.exit()
    
    # Create the jwt_manager for the booking service
    booking_app_jwt = booking_manager.bind_jwt_manger_to_app_instance(
        app_instance=booking_app
    )
    
    from common.pyportal_common.db_handlers.db_init import (
        start_database_creation_work
    )

    app_manager_db_obj = start_database_creation_work(
        booking_logger, BookingBase, booking_app
    )
    
    if app_manager_db_obj:
        # Initialize Kafka producer for booking events
        booking_kafka_producer = None
        try:
            from app.booking_kafka import (
                init_booking_kafka_producer,
            )
            booking_kafka_producer = (
                init_booking_kafka_producer.start_booking_kafka_producer(
                    booking_logger
                )
            )
        except Exception as ex:
            booking_logger.warning(
                f"Failed to initialize Kafka producer: {ex}"
            )

        from app.views.create_booking import (
            create_booking,
        )
        from app.views.get_booking import (
            get_booking,
        )
        from app.views.cancel_booking import (
            cancel_booking,
        )

        booking_bp.route(
            "/api/v1/airliner/bookings", methods=["POST"]
        )(create_booking)
        booking_bp.route(
            "/api/v1/airliner/bookings/<int:booking_id>", methods=["GET"]
        )(get_booking)
        booking_bp.route(
            "/api/v1/airliner/bookings/<int:booking_id>/cancel",
            methods=["PUT"]
        )(cancel_booking)

        booking_manager.register_blueprint_for_service(
            app_instance=booking_app,
            blueprint_instance=booking_bp,
        )
        booking_manager.display_registered_blueprints_for_service(
            app_instance=booking_app
        )
except Exception as ex:
    print(f"Exception in __init__: {ex}")
    import traceback
    traceback.print_exc()


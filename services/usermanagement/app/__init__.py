# pylint: disable=line-too-long
import os
import sys
import concurrent.futures
from logging import Logger
from flask import Flask, Blueprint
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../..'))

from common.pyportal_common.logging_handlers.base_logger import LogMonitor
from common.pyportal_common.app_handlers.app_manager import AppHandler
from app.app_configs import init_app_configs
from app.models.user_model import UserBase

# Initialize variables
user_management_logger = None
usermanager_app = None
user_management_grpc_server = None


try:
    # Set the registration service directory as the current dir
    currentDir = os.getcwd()
    # Enable/Disable the env file path according to the environment,
    # Read Schema Files of headers/requests for all the diff operations.
    service_dir = os.path.dirname(os.path.abspath(__file__))
    user_management_env_filepath = os.path.join(
        service_dir, ".env.dev"
    )
    reg_user_req_schema_filepath = os.path.join(
        service_dir,
        "schemas/requests/register_user/"
        "req_schema.json"
    )
    req_headers_schema_filepath = os.path.join(
        service_dir,
        "schemas/headers/"
        "reg_headers_schema.json"
    )
    getuser_headers_schema_filepath = os.path.join(
        service_dir,
        "schemas/headers/"
        "getuser_headers_schema.json"
    )
    del_user_headers_schema_filepath = os.path.join(
        service_dir,
        "schemas/headers/"
        "del_user_headers_schema.json"
    )

    # user_management_env_filepath = os.path.join(
    #     currentDir, "src/usermanagement_service/.env.prod"
    # )
    # reg_user_req_schema_filepath = os.path.join(
    #     currentDir,
    #     "src/usermanagement_service/schemas/requests/register_user/"
    #     "req_schema.json"
    # )
    # req_headers_schema_filepath = os.path.join(
    #     currentDir,
    #     "src/usermanagement_service/schemas/headers/"
    #     "reg_headers_schema.json"
    # )
    # getuser_headers_schema_filepath = os.path.join(
    #     currentDir,
    #     "src/usermanagement_service/schemas/headers/"
    #     "getuser_headers_schema.json"
    # )
    # del_user_headers_schema_filepath = os.path.join(
    #     currentDir,
    #     "src/usermanagement_service/schemas/headers/"
    #     "del_user_headers_schema.json"
    # )

    # Load the env file.
    # load_dotenv(user_management_env_filepath)

    # Initialize the logger for the user_management service
    user_management_logger: Logger = LogMonitor("usermanagement").logger
    user_management_logger.info(
        "Environment variables loaded from docker-compose"
    )
    usermanager: AppHandler = AppHandler(
        logger_instance=user_management_logger
    )
    usermanager_app: Flask = usermanager.create_app_instance()
    if usermanager_app is None:
        user_management_logger.error("App creation failed")
        sys.exit()

    init_app_configs(usermanager_app)
    
    # Add health check endpoint (before database initialization)
    @usermanager_app.route('/health', methods=['GET'])
    def health():
        """Health check endpoint"""
        from flask import jsonify
        return jsonify({
            'status': 'healthy',
            'service': 'usermanagement'
        }), 200
    
    # Load and Validate Schema Files which are read.
    (
        req_headers_schema_status,
        req_headers_schema,
    ) = usermanager.read_json_schema(req_headers_schema_filepath)
    (
        getuser_headers_schema_status,
        getuser_headers_schema,
    ) = usermanager.read_json_schema(getuser_headers_schema_filepath)
    (
        del_user_headers_schema_status,
        del_user_headers_schema,
    ) = usermanager.read_json_schema(del_user_headers_schema_filepath)
    (
        reg_user_req_schema_status,
        reg_user_req_schema,
    ) = usermanager.read_json_schema(reg_user_req_schema_filepath)

    # Create the blueprint for the user_management service
    usermanager_bp: Blueprint = (
        usermanager.create_blueprint_instance()
    )
    if usermanager_bp is None:
        user_management_logger.error(
            "Blue print creation failed for the App"
        )
        sys.exit()
    # Create the jwt_manager for the user_management service
    usermanager_app_jwt = usermanager.bind_jwt_manger_to_app_instance(
        app_instance=usermanager_app
    )
    from common.pyportal_common.db_handlers.db_init import (
        start_database_creation_work
    )

    app_manager_db_obj = start_database_creation_work(
        user_management_logger, UserBase, usermanager_app
    )
    if app_manager_db_obj:
        from app.user_management_grpc import (
            init_grpc_usermanagement_server,
        )
        start_user_management_grpc_server = (
            init_grpc_usermanagement_server.start_user_management_grpc_server
        )

        # Initialize gRPC server
        try:
            user_management_grpc_server = (
                start_user_management_grpc_server(user_management_logger)
            )
        except Exception as ex:
            user_management_logger.warning(
                f"Failed to initialize gRPC server: {ex}"
            )
            user_management_grpc_server = None

        # Initialize Kafka producer (optional)
        user_management_kafka_producer = None
        try:
            from app.user_management_kafka import (
                init_kafka_usermangement_producer,
            )
            user_management_kafka_producer = (
                init_kafka_usermangement_producer.
                start_user_management_kafka_producer(user_management_logger)
            )
        except Exception as ex:
            user_management_logger.warning(
                f"Failed to initialize Kafka producer: {ex}"
            )
        
        # Export for use in views
        __all__ = [
            "user_management_logger",
            "usermanager_app",
            "usermanager",
            "app_manager_db_obj",
            "req_headers_schema",
            "reg_user_req_schema",
            "user_management_kafka_producer",
        ]

        from app.views.create_user import (
            register_user,
        )

        # from app.views.fetch_user import (
        #     get_user_info
        # )
        # from app.views.remove_user import (
        #     deregister_user
        # )
        usermanager_bp.route(
            "/api/v1/eventstreammonitor/users/register", methods=["POST"]
        )(register_user)
        # usermanager_bp.route(
        #     '/api/v1/eventstreammonitor/users/<int:userid>', methods=['GET']
        # )(get_user_info)
        # usermanager_bp.route(
        #     '/api/v1/eventstreammonitor/users/<int:userid>', methods=['DELETE']
        # )(deregister_user)

        usermanager.register_blueprint_for_service(
            app_instance=usermanager_app,
            blueprint_instance=usermanager_bp,
        )
        usermanager.display_registered_blueprints_for_service(
            app_instance=usermanager_app
        )
except Exception as ex:
    print(f"Exception in __init__: {ex}")
    import traceback
    traceback.print_exc()

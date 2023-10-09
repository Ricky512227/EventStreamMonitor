# pylint: disable=line-too-long
import os
import sys
from logging import Logger
from flask import Flask, Blueprint
from dotenv import load_dotenv
from src.pyportal_common.kafka_service_handlers.producer_handlers.notfication_producer import (
    PyPortalKafkaProducer,
)
from src.pyportal_common.logging_handlers.base_logger import LogMonitor
from src.pyportal_common.app_handlers.app_manager import AppHandler
from src.usermanagement_service.models.user_model import UserBase

try:
    # Set the registration service directory as the current dir
    currentDir = os.getcwd()
    print(f"Current Directory :: {currentDir}")
    # Enable/Disable the env file path according to the environment,Read Schema Files of headers/requests for all the diff operations.
    user_management_env_filepath = os.path.join(currentDir, ".env.dev")
    reg_user_req_schema_filepath = os.path.join(
        currentDir, "schemas/requests/register_user/req_schema.json"
    )
    req_headers_schema_filepath = os.path.join(
        currentDir, "schemas/headers/reg_headers_schema.json"
    )
    getuser_headers_schema_filepath = os.path.join(
        currentDir, "schemas/headers/getuser_headers_schema.json"
    )
    del_user_headers_schema_filepath = os.path.join(
        currentDir, "schemas/headers/del_user_headers_schema.json"
    )

    # user_management_env_filepath = os.path.join(currentDir, "src/usermanagement_service/.env.prod")
    # reg_user_req_schema_filepath = os.path.join(currentDir, "src/usermanagement_service/schemas/requests/register_user/req_schema.json")
    # req_headers_schema_filepath = os.path.join(currentDir, "src/usermanagement_service/schemas/headers/reg_headers_schema.json")
    # getuser_headers_schema_filepath = os.path.join(currentDir, "src/usermanagement_service/schemas/headers/getuser_headers_schema.json")
    # del_user_headers_schema_filepath = os.path.join(currentDir, "src/usermanagement_service/schemas/headers/del_user_headers_schema.json")

    print(f"Loading Env File path :: {user_management_env_filepath}")
    # Load the env file.
    if load_dotenv(user_management_env_filepath):
        print(
            f"Environment variables file loaded from :: {user_management_env_filepath} "
        )
        # Setting the env variable and binding to the application.
        FLASK_ENV = os.environ.get("FLASK_ENV")
        DEBUG = os.environ.get("DEBUG")
        JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
        FLASK_APP = os.environ.get("FLASK_APP")

        USER_MANAGEMENT_SERVER_IPADDRESS = os.environ.get(
            "USER_MANAGEMENT_SERVER_IPADDRESS"
        )
        USER_MANAGEMENT_SERVER_PORT = os.environ.get("USER_MANAGEMENT_SERVER_PORT")
        USER_MANAGEMENT_GRPC_SERVER_IP = os.environ.get(
            "USER_MANAGEMENT_GRPC_SERVER_IP"
        )
        USER_MANAGEMENT_GRPC_SERVER_PORT = os.environ.get(
            "USER_MANAGEMENT_GRPC_SERVER_PORT"
        )
        USER_MANAGEMENT_GRPC_MAX_WORKERS = int(
            os.environ.get("USER_MANAGEMENT_GRPC_MAX_WORKERS")
        )

        # Initialize the logger for the user_management service
        user_management_logger: Logger = LogMonitor("usermanagement").logger
        usermanager: AppHandler = AppHandler(logger_instance=user_management_logger)
        usermanager_app: Flask = usermanager.create_app_instance()
        if usermanager_app is None:
            user_management_logger.error("App creation failed")
            sys.exit()
        usermanager_app.config["FLASK_ENV"] = FLASK_ENV
        usermanager_app.config["DEBUG"] = DEBUG
        usermanager_app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
        usermanager_app.config["FLASK_APP"] = FLASK_APP

        usermanager_app.config[
            "USER_MANAGEMENT_SERVER_IPADDRESS"
        ] = USER_MANAGEMENT_SERVER_IPADDRESS
        usermanager_app.config[
            "USER_MANAGEMENT_SERVER_PORT"
        ] = USER_MANAGEMENT_SERVER_PORT

        usermanager_app.config[
            "USER_MANAGEMENT_GRPC_SERVER_IP"
        ] = USER_MANAGEMENT_GRPC_SERVER_IP
        usermanager_app.config[
            "USER_MANAGEMENT_GRPC_SERVER_PORT"
        ] = USER_MANAGEMENT_GRPC_SERVER_PORT
        usermanager_app.config[
            "USER_MANAGEMENT_GRPC_MAX_WORKERS"
        ] = USER_MANAGEMENT_GRPC_MAX_WORKERS
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
        usermanager_bp: Blueprint = usermanager.create_blueprint_instance()
        if usermanager_bp is None:
            user_management_logger.error("Blue print creation failed for the App")
            sys.exit()
        # Create the jwt_manager for the user_management service
        usermanager_app_jwt = usermanager.bind_jwt_manger_to_app_instance(
            app_instance=usermanager_app
        )
        from src.pyportal_common.db_handlers.db_init import start_database_creation_work

        session_maker_obj = start_database_creation_work(
            user_management_logger, UserBase, usermanager_app
        )
        if session_maker_obj:
            from src.usermanagement_service.views.create_user import (
                register_user,
            )

            # from src.usermanagement_service.views.fetch_user import get_user_info
            # from src.usermanagement_service.views.remove_user import deregister_user
            usermanager_bp.route("/api/v1/airliner/registerUser", methods=["POST"])(
                register_user
            )
            # usermanager_bp.route('/api/v1/airliner/getUser/<int:userid>', methods=['GET'])(get_user_info)
            # usermanager_bp.route('/api/v1/airliner/deleteUser/<int:userid>', methods=['DELETE'])(deregister_user)

            usermanager.register_blueprint_for_service(
                app_instance=usermanager_app,
                blueprint_instance=usermanager_bp,
            )
            usermanager.display_registered_blueprints_for_service(
                app_instance=usermanager_app
            )

            from src.pyportal_common.grpc_service_handlers.grpc_server_handler.grpc_base_server import (
                PyPortalGrpcBaseServer,
            )

            from src.proto_def.token_proto_v1.token_pb2_grpc import (
                add_UserValidationForTokenGenerationServiceServicer_to_server,
            )

            from src.usermanagement_service.user_management_grpc.user_grpc_server import (
                UserValidationForTokenGenerationService,
            )
            from src.pyportal_common.grpc_service_handlers.grpc_server_handler.grpc_base_server_init import (
                init_pyportal_grpc_base_server,
            )

            my_grpc_server = init_pyportal_grpc_base_server(user_management_logger)
            if my_grpc_server:
                my_grpc_server.bind_ip_port_server()
                if my_grpc_server is not None:
                    my_grpc_server.bind_rpc_method_server(
                        name_service_servicer_to_server=add_UserValidationForTokenGenerationServiceServicer_to_server,
                        name_service=UserValidationForTokenGenerationService,
                    )
            from src.pyportal_common.kafka_service_handlers.producer_handlers.base_producer_init import (
                init_pyportal_kafka_producer,
            )

            my_kafka_producer: PyPortalKafkaProducer = init_pyportal_kafka_producer(
                user_management_logger
            )
            if my_kafka_producer:
                pass

        else:
            print("Unable to start db")
    else:
        print(f"File not found or not loaded :: {user_management_env_filepath} ")
except Exception as ex:
    print(f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}")

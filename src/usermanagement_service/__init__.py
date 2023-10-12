# pylint: disable=line-too-long
import os
import sys
import concurrent.futures
from logging import Logger
from flask import Flask, Blueprint
from dotenv import load_dotenv
from src.pyportal_common.logging_handlers.base_logger import LogMonitor
from src.pyportal_common.app_handlers.app_manager import AppHandler
from app_configs import init_app_configs
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

        # Initialize the logger for the user_management service
        user_management_logger: Logger = LogMonitor("usermanagement").logger
        usermanager: AppHandler = AppHandler(logger_instance=user_management_logger)
        usermanager_app: Flask = usermanager.create_app_instance()
        if usermanager_app is None:
            user_management_logger.error("App creation failed")
            sys.exit()

        init_app_configs(usermanager_app)
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

        app_manager_db_obj = start_database_creation_work(
            user_management_logger, UserBase, usermanager_app
        )
        if app_manager_db_obj:
            from src.usermanagement_service.user_management_grpc.init_grpc_usermanagement_server import (
                start_user_management_grpc_server,
            )
            from src.usermanagement_service.user_management_kafka.init_kafka_usermangement_producer import (
                start_user_management_kafka_producer,
            )

            with concurrent.futures.ThreadPoolExecutor(
                max_workers=2
            ) as thread_executor:
                user_management_grpc_server_init_thread = thread_executor.submit(
                    start_user_management_grpc_server, user_management_logger
                )
                user_management_kafka_producer_init_thread = thread_executor.submit(
                    start_user_management_kafka_producer, user_management_logger
                )
                user_management_grpc_server = (
                    user_management_grpc_server_init_thread.result()
                )
                user_management_kafka_producer = (
                    user_management_kafka_producer_init_thread.result()
                )

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

        else:
            print("Unable to start db")
    else:
        print(f"File not found or not loaded :: {user_management_env_filepath} ")
except Exception as ex:
    print(f"Error occurred :: {ex}\tLine No:: {sys.exc_info()[2].tb_lineno}")

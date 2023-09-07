import os
import sys
from dotenv import load_dotenv
from src.airliner_common.create_app import CreatFlaskApp
from src.authtoken_service.models.token_model import Base


try:
    currentDir = "/Users/kamalsaidevarapalli/Desktop/Workshop/AirlinerAdminstration/src/authtoken_service/"
    # authtoken_env_filepath = os.path.join(currentDir, ".env.dev")
    authtoken_env_filepath = os.path.join(currentDir, ".env.prod")


    print("Loading .Env File path :: {0}".format(authtoken_env_filepath))
    loaded = load_dotenv(authtoken_env_filepath)

    if loaded:
        print("Environment variables file loaded from :: {0} ".format(authtoken_env_filepath))
        FLASK_ENV = os.environ.get("FLASK_ENV")
        DEBUG = os.environ.get("DEBUG")
        SECRET_KEY = os.environ.get("SECRET_KEY")
        FLASK_APP = os.environ.get("FLASK_APP")

        AUTHTOKEN_SERVER_IPADDRESS = os.environ.get("AUTHTOKEN_SERVER_IPADDRESS")
        AUTHTOKEN_SERVER_PORT = os.environ.get("AUTHTOKEN_SERVER_PORT")
        REGISTRATION_GRPC_SERVER_IP = os.environ.get("REGISTRATION_GRPC_SERVER_IP")
        REGISTRATION_GRPC_SERVER_PORT = os.environ.get("REGISTRATION_GRPC_SERVER_PORT")

        SERVICE_NAME = os.environ.get("SERVICE_NAME")
        DB_DRIVER_NAME = os.environ.get("DB_DRIVER_NAME")
        DB_USER = os.environ.get("DB_USER")
        DB_PASSWORD = os.environ.get("DB_PASSWORD")
        DB_IPADDRESS = os.environ.get("DB_IPADDRESS")
        DB_PORT = int(os.environ.get("DB_PORT"))
        DB_NAME = os.environ.get("DB_NAME")
        POOL_SIZE = int(os.environ.get("POOL_SIZE"))
        MAX_OVERFLOW = int(os.environ.get("MAX_OVERFLOW"))
        RETRY_INTERVAL = int(os.environ.get("RETRY_INTERVAL"))

        authtoken_app_obj = CreatFlaskApp(service_name=SERVICE_NAME, db_driver=DB_DRIVER_NAME, db_user=DB_USER,
                                    db_ip_address=DB_IPADDRESS, db_password=DB_PASSWORD, db_port=DB_PORT,
                                    db_name=DB_NAME, db_pool_size=POOL_SIZE, db_pool_max_overflow=MAX_OVERFLOW,
                                    retry_interval=RETRY_INTERVAL, base=Base)

        authtoken_app_logger = authtoken_app_obj.app_logger
        authtoken_app = authtoken_app_obj.create_app_instance()
        authtoken_app_jwt = authtoken_app_obj.init_jwt_manger()
        authtoken_app.config["FLASK_ENV"] = FLASK_ENV
        authtoken_app.config["DEBUG"] = DEBUG
        authtoken_app.config["SECRET_KEY"] = SECRET_KEY
        authtoken_app.config["FLASK_APP"] = FLASK_APP

        authtoken_app.config["AUTHTOKEN_SERVER_IPADDRESS"] = AUTHTOKEN_SERVER_IPADDRESS
        authtoken_app.config["AUTHTOKEN_SERVER_PORT"] = AUTHTOKEN_SERVER_PORT

        authtoken_app.config["REGISTRATION_GRPC_SERVER_IP"] = REGISTRATION_GRPC_SERVER_IP
        authtoken_app.config["REGISTRATION_GRPC_SERVER_PORT"] = REGISTRATION_GRPC_SERVER_PORT

        # Read Schema File
        gen_token_req_schema_filepath = os.path.join(currentDir, "schemas/requests/generate_token/req_schema.json")
        gen_token_req_headers_schema_filepath = os.path.join(currentDir, "schemas/headers/gentoken_headers_schema.json")

        gen_token_req_headers_schema_status, gen_token_req_headers_schema = authtoken_app_obj.read_json_schema(gen_token_req_headers_schema_filepath)
        gen_token_req_schema_status, gen_token_req_schema = authtoken_app_obj.read_json_schema(gen_token_req_schema_filepath)

        authtoken_bp = authtoken_app_obj.create_blueprint()
        authtoken_app_obj.display_registered_blueprints_for_service()

        registration_db_engine, is_engine_created = authtoken_app_obj.create_db_engine()
        if is_engine_created:
            if authtoken_app_obj.check_db_connectivity_and_retry():
                if authtoken_app_obj.init_databases_for_service():
                    if authtoken_app_obj.create_tables_associated_to_db_model():
                        registration_SQLAlchemy = authtoken_app_obj.bind_db_app()
                        registration_connection_pool, _ = authtoken_app_obj.create_pool_of_connections()
                        authtoken_app_obj.display_pool_info()
                        from src.authtoken_service.controllers.authtoken_controller import create_token

                        authtoken_bp.route('/api/v1/airliner/generateToken', methods=['POST'])(create_token)
                        authtoken_app_obj.register_blueprint()
                        authtoken_app_obj.display_registered_blueprints_for_service()

                        from src.airliner_common.airliner_err_handlers import internal_server_error, bad_request, \
                            not_found

                        authtoken_app_obj.register_err_handler(500, internal_server_error)
                        authtoken_app_obj.register_err_handler(400, bad_request)
                        authtoken_app_obj.register_err_handler(404, not_found)
                        authtoken_app_obj.display_registered_err_handlers()


except Exception as ex:
    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

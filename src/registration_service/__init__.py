import os
import sys
import grpc
from dotenv import load_dotenv
from concurrent import futures
from src.admin_grpc import token_pb2_grpc
from src.admin_common.create_app import CreatFlaskApp
from src.registration_service.models.user_model import Base

try:
    # Set the registration service directory as the current dir
    currentDir = os.getcwd()
    print("Current Directory :: {0}".format(currentDir))
    # Enable/Disable the env file path according to the environment
    registration_env_filepath = os.path.join(currentDir, ".env.dev")
    # registration_env_filepath = os.path.join(currentDir, ".env.prod")
    print("Loading Env File path :: {0}".format(registration_env_filepath))
    # Load the env file.
    loaded = load_dotenv(registration_env_filepath)
    if loaded:
        print("Environment variables file loaded from :: {0} ".format(registration_env_filepath))
        # Setting the env variable and binding to the application.
        FLASK_ENV = os.environ.get("FLASK_ENV")
        DEBUG = os.environ.get("DEBUG")
        JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
        FLASK_APP = os.environ.get("FLASK_APP")

        REGISTRATION_SERVER_IPADDRESS = os.environ.get("REGISTRATION_SERVER_IPADDRESS")
        REGISTRATION_SERVER_PORT = os.environ.get("REGISTRATION_SERVER_PORT")
        REGISTRATION_GRPC_SERVER_IP = os.environ.get("REGISTRATION_GRPC_SERVER_IP")
        REGISTRATION_GRPC_SERVER_PORT = os.environ.get("REGISTRATION_GRPC_SERVER_PORT")
        REGISTRATION_GRPC_MAX_WORKERS = int(os.environ.get("REGISTRATION_GRPC_MAX_WORKERS"))

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

        # Initialize the ap for registration service
        reg_app_obj = CreatFlaskApp(service_name=SERVICE_NAME, db_driver=DB_DRIVER_NAME, db_user=DB_USER,
                                    db_ip_address=DB_IPADDRESS, db_password=DB_PASSWORD, db_port=DB_PORT,
                                    db_name=DB_NAME, db_pool_size=POOL_SIZE, db_pool_max_overflow=MAX_OVERFLOW,
                                    retry_interval=RETRY_INTERVAL, base=Base)

        # Initialize the logger for the registration service
        registration_app_logger = reg_app_obj.app_logger
        registration_app = reg_app_obj.create_app_instance()

        registration_app.config["FLASK_ENV"] = FLASK_ENV
        registration_app.config["DEBUG"] = DEBUG
        registration_app.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
        registration_app.config["FLASK_APP"] = FLASK_APP

        registration_app_jwt = reg_app_obj.init_jwt_manger()

        registration_app.config["REGISTRATION_SERVER_IPADDRESS"] = REGISTRATION_SERVER_IPADDRESS
        registration_app.config["REGISTRATION_SERVER_PORT"] = REGISTRATION_SERVER_PORT

        registration_app.config["REGISTRATION_GRPC_SERVER_IP"] = REGISTRATION_GRPC_SERVER_IP
        registration_app.config["REGISTRATION_GRPC_SERVER_PORT"] = REGISTRATION_GRPC_SERVER_PORT
        registration_app.config["REGISTRATION_GRPC_MAX_WORKERS"] = REGISTRATION_GRPC_MAX_WORKERS

        # Read Schema Files of headers/requests for all the diff operations.
        reg_user_req_schema_filepath = os.path.join(currentDir, "schemas/requests/register_user/req_schema.json")
        req_headers_schema_filepath = os.path.join(currentDir, "schemas/headers/reg_headers_schema.json")
        getuser_headers_schema_filepath = os.path.join(currentDir, "schemas/headers/getuser_headers_schema.json")
        del_user_headers_schema_filepath = os.path.join(currentDir, "schemas/headers/del_user_headers_schema.json")

        # Load and Validate Schema Files which are read.
        req_headers_schema_status, req_headers_schema = reg_app_obj.read_json_schema(req_headers_schema_filepath)
        getuser_headers_schema_status, getuser_headers_schema = reg_app_obj.read_json_schema(
            getuser_headers_schema_filepath)
        del_user_headers_schema_status, del_user_headers_schema = reg_app_obj.read_json_schema(
            del_user_headers_schema_filepath)

        reg_user_req_schema_status, reg_user_req_schema = reg_app_obj.read_json_schema(reg_user_req_schema_filepath)

        # Create the blueprint for the registration service
        registration_bp = reg_app_obj.create_blueprint()
        # Display Register the blueprint for the registration service
        reg_app_obj.display_registered_blueprints_for_service()
        # Create a database engine
        registration_db_engine, is_engine_created = reg_app_obj.create_db_engine()
        # If the engine doesn't create, then go for retry  of max_retries=3 with retry_delay=5.
        if is_engine_created:
            # If the engine is created then check the connection for the status of th db.
            if reg_app_obj.check_db_connectivity_and_retry():
                # If the connection  health is connected, then initialise the database for the particular service.
                if reg_app_obj.init_databases_for_service():
                    # If the connection  health is connected, then create the tables for the services which was defined in the models.
                    if reg_app_obj.create_tables_associated_to_db_model():
                        # Bind the application with the sqlAlchemy.
                        registration_SQLAlchemy = reg_app_obj.bind_db_app()
                        # Bind the application with the migrations
                        registration_migrate = reg_app_obj.migrate_db_bind_app()
                        # Initialize/Create a pool of connections for the service
                        registration_connection_pool, _ = reg_app_obj.create_pool_of_connections()
                        # Display the  pool of connections for the service which was initialized
                        reg_app_obj.display_pool_info()
                        ''' 
                        To create and initialize the controllers, we need to 
                            - attach the routes to the created blueprint
                            - register the blueprint
                        '''
                        from src.registration_service.controllers.user_controller import register_user, get_user_info, \
                            remove_user

                        registration_bp.route('/api/v1/airliner/registerUser', methods=['POST'])(register_user)
                        registration_bp.route('/api/v1/airliner/getUser/<int:userid>', methods=['GET'])(get_user_info)
                        registration_bp.route('/api/v1/airliner/deleteUser/<int:userid>', methods=['DELETE'])(
                            remove_user)

                        reg_app_obj.register_blueprint()
                        reg_app_obj.display_registered_blueprints_for_service()

                        # Registering the custom error handlers  to the application instance
                        from src.admin_common.admin_err_handlers import internal_server_error, bad_request, \
                            not_found

                        reg_app_obj.register_err_handler(500, internal_server_error)
                        reg_app_obj.register_err_handler(400, bad_request)
                        reg_app_obj.register_err_handler(404, not_found)
                        reg_app_obj.display_registered_err_handlers()

                        from src.registration_service.registration_grpc.server import \
                            UserValidationForTokenGenerationService

                        # Create/Initialise the grpc server for the registration service
                        server = grpc.server(futures.ThreadPoolExecutor(
                            max_workers=registration_app.config["REGISTRATION_GRPC_MAX_WORKERS"]))
                        registration_app_logger.info("Created GRPC server with the workers of max :: {0}".format(10))
                        token_pb2_grpc.add_UserValidationForTokenGenerationServicer_to_server(
                            UserValidationForTokenGenerationService(), server)
                        registration_app_logger.info("Registered GRPC server to the server :: {0}".format(
                            "UserValidationForTokenGenerationService"))
                        server.add_insecure_port(
                            registration_app.config["REGISTRATION_GRPC_SERVER_IP"] + ":" + registration_app.config[
                                "REGISTRATION_GRPC_SERVER_PORT"])
                        registration_app_logger.info(
                            "Starting GRPC server for the Token-User service with the IP & PORT:: {0}:{1}".format(
                                registration_app.config["REGISTRATION_GRPC_SERVER_IP"],
                                registration_app.config["REGISTRATION_GRPC_SERVER_PORT"]))

    else:
        print("File not found or not loaded :: {0} ".format(registration_env_filepath))


except Exception as ex:
    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

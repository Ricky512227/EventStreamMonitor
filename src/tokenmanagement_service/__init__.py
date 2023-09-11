import os
import sys
from dotenv import load_dotenv
from src.admin_common.create_app import CreatFlaskApp
from src.tokenmanagement_service.models.token_model import Base


try:
    # Set the authtoken service directory as the current dir
    currentDir = os.getcwd()
    print("Current Directory :: {0}".format(currentDir))
    # Enable/Disable the env file path according to the environment
    authtoken_env_filepath = os.path.join(currentDir, ".env.dev")
    # registration_env_filepath = os.path.join(currentDir, ".env.prod")
    print("Loading Env File path :: {0}".format(authtoken_env_filepath))
    # Load the env file.
    loaded = load_dotenv(authtoken_env_filepath)
    if loaded:
        print("Environment variables file loaded from :: {0} ".format(authtoken_env_filepath))
        # Setting the env variable and binding to the application.
        FLASK_ENV = os.environ.get("FLASK_ENV")
        DEBUG = os.environ.get("DEBUG")
        JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY")
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

        # Initialize the ap for authtoken service
        token_management_obj = CreatFlaskApp(service_name=SERVICE_NAME, db_driver=DB_DRIVER_NAME, db_user=DB_USER,
                                    db_ip_address=DB_IPADDRESS, db_password=DB_PASSWORD, db_port=DB_PORT,
                                    db_name=DB_NAME, db_pool_size=POOL_SIZE, db_pool_max_overflow=MAX_OVERFLOW,
                                    retry_interval=RETRY_INTERVAL, base=Base)

        # Initialize the logger for the authtoken service
        token_management_logger = token_management_obj.app_logger
        token_management = token_management_obj.create_app_instance()
        token_management.config["JWT_SECRET_KEY"] = JWT_SECRET_KEY
        token_management_jwt = token_management_obj.init_jwt_manger()

        token_management.config["FLASK_ENV"] = FLASK_ENV
        token_management.config["DEBUG"] = DEBUG
        token_management.config["FLASK_APP"] = FLASK_APP

        token_management.config["AUTHTOKEN_SERVER_IPADDRESS"] = AUTHTOKEN_SERVER_IPADDRESS
        token_management.config["AUTHTOKEN_SERVER_PORT"] = AUTHTOKEN_SERVER_PORT

        token_management.config["REGISTRATION_GRPC_SERVER_IP"] = REGISTRATION_GRPC_SERVER_IP
        token_management.config["REGISTRATION_GRPC_SERVER_PORT"] = REGISTRATION_GRPC_SERVER_PORT

        # Read Schema Files of headers/requests for all the diff operations.
        gen_token_req_schema_filepath = os.path.join(currentDir, "schemas/requests/generate_token/req_schema.json")
        gen_token_req_headers_schema_filepath = os.path.join(currentDir, "schemas/headers/gentoken_headers_schema.json")

        # Load and Validate Schema Files which are read.
        gen_token_req_headers_schema_status, gen_token_req_headers_schema = token_management_obj.read_json_schema(gen_token_req_headers_schema_filepath)
        gen_token_req_schema_status, gen_token_req_schema = token_management_obj.read_json_schema(gen_token_req_schema_filepath)



        # Create the blueprint for the authtoken service
        authtoken_bp = token_management_obj.create_blueprint()
        # Display Register the blueprint for the authtoken service
        token_management_obj.display_registered_blueprints_for_service()
        # Create a database engine
        authtoken_db_engine, is_engine_created = token_management_obj.create_db_engine()
        # If the engine doesn't create, then go for retry  of max_retries=3 with retry_delay=5.
        if is_engine_created:
            # If the engine is created then check the connection for the status of th db.
            if token_management_obj.check_db_connectivity_and_retry():
                # If the connection  health is connected, then initialise the database for the particular service.
                if token_management_obj.init_databases_for_service():
                    # If the connection  health is connected, then create the tables for the services which was defined in the models.
                    if token_management_obj.create_tables_associated_to_db_model():
                        # Bind the application with the sqlAlchemy.
                        authtoken_SQLAlchemy = token_management_obj.bind_db_app()
                        # Bind the application with the migrations
                        authtoken_migrate = token_management_obj.migrate_db_bind_app()
                        # Initialize/Create a pool of connections for the service
                        registration_connection_pool, _ = token_management_obj.create_pool_of_connections()
                        token_management_obj.display_pool_info()
                        from src.tokenmanagement_service.controllers.authtoken_controller import create_token

                        ''' 
                        To create and initialize the controllers, we need to 
                            - attach the routes to the created blueprint
                            - register the blueprint
                        '''
                        authtoken_bp.route('/api/v1/airliner/generateToken', methods=['POST'])(create_token)
                        token_management_obj.register_blueprint()
                        token_management_obj.display_registered_blueprints_for_service()

                        # Registering the custom error handlers  to the application instance
                        from src.admin_common.admin_err_handlers import internal_server_error, bad_request, \
                            not_found

                        token_management_obj.register_err_handler(500, internal_server_error)
                        token_management_obj.register_err_handler(400, bad_request)
                        token_management_obj.register_err_handler(404, not_found)
                        token_management_obj.display_registered_err_handlers()


except Exception as ex:
    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

import sys, grpc
from concurrent import futures
from src.airliner_common.log_monitor import LogMonitor
from src.registration_service.users.user import User
from src.registration_service.users.token import Token
from src.registration_service.models.user_model import Base, UsersModel
from src.airliner_common.create_app import CreatFlaskApp
from src.airliner_common.create_db_engine import CreateDbEngine, BindSQLALCHEMY, QueuePool_To_Target_DB, \
    init_databases_for_service, \
    check_db_connectivity_and_retry, create_tables_associated_to_db_model, create_session_for_service

from src.airliner_common.read_configs import read_json_schema
from src.airliner_grpc import token_pb2_grpc
from src.registration_service.server import UserValidationForTokenGenerationService

try:
    USER_SERVICE_NAME = "USERS"

    USER_APP_NAME = USER_SERVICE_NAME.lower() + "_" + "app"


    user_logger = LogMonitor(USER_SERVICE_NAME.lower()).create_logger_for_service()

    # Read Schema File
    login_user_req_schema_filepath = "/registration_service/schemas/requests/login_user/req_schema.json"
    reg_user_req_schema_filepath = "/registration_service/schemas/requests/register_user/req_schema.json"
    req_headers_schema_filepath = "/registration_service/schemas/headers/request_headers_schema.json"

    req_headers_schema, _ = read_json_schema(req_headers_schema_filepath)
    login_user_req_schema, _ = read_json_schema(login_user_req_schema_filepath)
    reg_user_req_schema, _ = read_json_schema(reg_user_req_schema_filepath)

    # Application Bringup
    user_app = CreatFlaskApp(USER_SERVICE_NAME).create_app_instance()
    user_logger.info("Application :: {0} , Type :: {1}".format(user_app, type(user_app)))


    # REGISTRATION
    from src.registration_service.routes.registration_routes import user_blueprint, bind_reg_blueprints, display_reg_blueprints_per_service

    bind_reg_blueprints(user_app, user_blueprint)
    display_reg_blueprints_per_service(user_app)




    # DataBase Bringup
    user_db_obj = CreateDbEngine(USER_SERVICE_NAME, "mysql+pymysql", "root", "testeventstreammonitor#123", "localhost", "3304", "Users")

    user_db_engine = user_db_obj.create_db_engine()

    if check_db_connectivity_and_retry(USER_SERVICE_NAME, user_db_engine):
        database_uri = user_db_obj.get_database_uri()
        if init_databases_for_service(database_uri):
            if create_tables_associated_to_db_model(Base, airliner_db_engine=user_db_engine):
                user_db_bind_obj = BindSQLALCHEMY(USER_SERVICE_NAME, user_app, database_uri)
                user_db_sqlalchemy = user_db_bind_obj.bind_db_app()
                user_pool_obj = QueuePool_To_Target_DB(USER_SERVICE_NAME, user_db_engine, 100, 20)
                user_connection_pool = user_pool_obj.create_pool()
                user_pool_obj.display_pool_info()

    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    print("Created GRPC server with the workers of max :: {0}".format(10))
    token_pb2_grpc.add_UserValidationForTokenGenerationServicer_to_server(UserValidationForTokenGenerationService(), server)
    print("Registered GRPC server to the server :: {0}".format("UserValidationForTokenGenerationService"))
    server.add_insecure_port('127.0.0.1:8081')
    print("Registering GRPC server for the Token-User service with the IP & PORT:: {0}:{1}".format("localhost", "8081"))
    server.start()
    print("Started the grpc server ...")



except Exception as ex:
    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

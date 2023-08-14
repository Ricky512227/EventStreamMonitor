import sys
from src.airliner_common.base_logger import LogMonitor
from src.airliner_common.create_app import CreatFlaskApp
from registration_service.users.user import User
from registration_service.models.user_model import Base
from src.airliner_common.create_db_engine import CreateDbEngine, BindSQLALCHEMY, QueuePool_To_Target_DB, init_databases_for_service, check_db_connectivity_and_retry, create_tables_associated_to_db_model
import grpc
from concurrent import futures
from src.airliner_grpc import token_pb2_grpc
from registration_service.server import UserValidationForTokenGenerationService

def create_app():
    try:
        SERVICE_NAME = "REGISTRATION"

        registration_app_logger = LogMonitor(SERVICE_NAME.lower()).create_logger_for_service()
        registration_app = CreatFlaskApp(SERVICE_NAME).create_app_instance()
        registration_app_logger.info("Application :: {0} , Type :: {1}".format(registration_app, type(registration_app)))

        from src.airliner_common.read_configs import read_json_schema
        # Read Schema File
        login_user_req_schema_filepath = "/Users/kamalsaidevarapalli/Desktop/Workshop/AirlinerAdminstration/src/registration_service/schemas/requests/login_user/req_schema.json"
        reg_user_req_schema_filepath = "/Users/kamalsaidevarapalli/Desktop/Workshop/AirlinerAdminstration/src/registration_service/schemas/requests/register_user/req_schema.json"
        req_headers_schema_filepath = "/Users/kamalsaidevarapalli/Desktop/Workshop/AirlinerAdminstration/src/registration_service/schemas/headers/request_headers_schema.json"

        req_headers_schema, _ = read_json_schema(req_headers_schema_filepath)
        login_user_req_schema, _ = read_json_schema(login_user_req_schema_filepath)
        reg_user_req_schema, _ = read_json_schema(reg_user_req_schema_filepath)
        #
        # # DataBase Bringup
        registration_db_obj = CreateDbEngine(SERVICE_NAME, "mysql+pymysql", "root", "testeventstreammonitor#123", "localhost", "3304", "Registration")

        registration_db_engine = registration_db_obj.create_db_engine()

        if check_db_connectivity_and_retry(SERVICE_NAME, registration_db_engine):
            database_uri = registration_db_obj.get_database_uri()
            if init_databases_for_service(database_uri):
                if create_tables_associated_to_db_model(Base, airliner_db_engine=registration_db_engine):
                    registration_db_bind_obj = BindSQLALCHEMY(SERVICE_NAME, registration_app, database_uri)
                    registration_db_sqlalchemy = registration_db_bind_obj.bind_db_app()
                    registration_pool_obj = QueuePool_To_Target_DB(SERVICE_NAME, registration_db_engine, 100, 20)
                    registration_connection_pool = registration_pool_obj.create_pool()
                    registration_pool_obj.display_pool_info()
        #
                    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
                    print("Created GRPC server with the workers of max :: {0}".format(10))
                    token_pb2_grpc.add_UserValidationForTokenGenerationServicer_to_server(UserValidationForTokenGenerationService(), server)
                    print("Registered GRPC server to the server :: {0}".format("UserValidationForTokenGenerationService"))
                    server.add_insecure_port('127.0.0.1:8081')
                    print("Registering GRPC server for the Token-User service with the IP & PORT:: {0}:{1}".format("localhost", "8081"))
                    server.start()
                    print("Started the grpc server ...")


                    registration_app_init_data={
                        "SERVICE_NAME" : SERVICE_NAME,
                        "app_instance" : registration_app,
                        "logger_instance" : registration_app_logger,
                        "req_headers_schema": req_headers_schema,
                        "login_user_req_schema": login_user_req_schema,
                        "reg_user_req_schema": reg_user_req_schema,
                        "registration_db_engine" : registration_db_engine,
                        "registration_pool_obj" : registration_pool_obj

                    }
                    return registration_app_init_data
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

import sys
from flask_jwt_extended import JWTManager

from src.airliner_common.base_logger import LogMonitor
from src.airliner_common.create_app import CreatFlaskApp
from auth_token_service.tokens.token import Token
from auth_token_service.models.token_model import Base
from src.airliner_common.create_db_engine import CreateDbEngine, BindSQLALCHEMY, QueuePool_To_Target_DB, init_databases_for_service, check_db_connectivity_and_retry, create_tables_associated_to_db_model



def create_app():
    try:
        SERVICE_NAME = "AUTHTOKEN"

        auth_token_app_logger = LogMonitor(SERVICE_NAME.lower()).create_logger_for_service()
        auth_token_app = CreatFlaskApp(SERVICE_NAME).create_app_instance()
        auth_token_app.config['JWT_SECRET_KEY'] = '12345Ricky@23'
        auth_token_jwt = JWTManager(auth_token_app)
        auth_token_app_logger.info("Application :: {0} , Type :: {1}".format(auth_token_app, type(auth_token_app)))

        from src.airliner_common.read_configs import read_json_schema
        # Read Schema File
        login_user_req_schema_filepath = "/Users/kamalsaidevarapalli/Desktop/Workshop/AirlinerAdminstration/src/auth_token_service/schemas/requests/login_user/req_schema.json"
        gen_token_req_schema_filepath = "/Users/kamalsaidevarapalli/Desktop/Workshop/AirlinerAdminstration/src/auth_token_service/schemas/requests/generate_token/req_schema.json"
        req_headers_schema_filepath = "/Users/kamalsaidevarapalli/Desktop/Workshop/AirlinerAdminstration/src/auth_token_service/schemas/headers/request_headers_schema.json"

        req_headers_schema, _ = read_json_schema(req_headers_schema_filepath)
        login_user_req_schema, _ = read_json_schema(login_user_req_schema_filepath)
        gen_token_req_schema, _ = read_json_schema(gen_token_req_schema_filepath)
        #
        # # DataBase Bringup
        auth_token_db_obj = CreateDbEngine(service_name=SERVICE_NAME, db_driver="mysql+pymysql", db_user="root", db_password="testeventstreammonitor#123", db_ip_address="localhost", db_port="3305", db_name="AUTHTOKENS")

        auth_token_db_engine = auth_token_db_obj.create_db_engine()

        if check_db_connectivity_and_retry(SERVICE_NAME, auth_token_db_engine):
            database_uri = auth_token_db_obj.get_database_uri()
            if init_databases_for_service(database_uri):
                if create_tables_associated_to_db_model(Base, airliner_db_engine=auth_token_db_engine):
                    auth_token_db_bind_obj = BindSQLALCHEMY(SERVICE_NAME, auth_token_app, database_uri)
                    auth_token_db_sqlalchemy = auth_token_db_bind_obj.bind_db_app()
                    auth_token_pool_obj = QueuePool_To_Target_DB(SERVICE_NAME, auth_token_db_engine, 100, 20)
                    auth_token_connection_pool = auth_token_pool_obj.create_pool()
                    auth_token_pool_obj.display_pool_info()
                    auth_token_app_init_data={
                        "SERVICE_NAME" : SERVICE_NAME,
                        "app_instance" : auth_token_app,
                        "logger_instance" : auth_token_app_logger,
                        "req_headers_schema": req_headers_schema,
                        "login_user_req_schema": login_user_req_schema,
                        "gen_token_req_schema": gen_token_req_schema,
                        "auth_token_db_engine" : auth_token_db_engine,
                        "auth_token_pool_obj" : auth_token_pool_obj

                    }
                    return auth_token_app_init_data
    except Exception as ex:
        print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))

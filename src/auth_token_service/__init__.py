import sys
from flask_jwt_extended import JWTManager
from src.auth_token_service.client import init_grpc_token_client
from src.airliner_common.base_logger import LogMonitor
from src.auth_token_service.tokens.token import Token
from src.auth_token_service.models.token_model import Base, TokensModel
from src.airliner_common.create_app import CreatFlaskApp
from src.airliner_common.create_db_engine import CreateDbEngine, BindSQLALCHEMY, QueuePool_To_Target_DB, \
    init_databases_for_service, check_db_connectivity_and_retry, create_tables_associated_to_db_model, create_session_for_service

from src.airliner_common.read_configs import read_json_schema


try:
    TOKEN_SERVICE_NAME = "AUTH_TOKEN"
    TOKEN_SERVICE_APP_NAME = TOKEN_SERVICE_NAME.lower() + "_" + "app"
    authtoken_logger = LogMonitor(TOKEN_SERVICE_NAME.lower()).create_logger_for_service()
    # Read Schema File
    login_user_req_schema_filepath = "/registration_service/schemas/requests/login_user/req_schema.json"
    reg_user_req_schema_filepath = "/registration_service/schemas/requests/register_user/req_schema.json"
    req_headers_schema_filepath = "/registration_service/schemas/headers/request_headers_schema.json"

    req_headers_schema, _ = read_json_schema(req_headers_schema_filepath)
    login_user_req_schema, _ = read_json_schema(login_user_req_schema_filepath)
    reg_user_req_schema, _ = read_json_schema(reg_user_req_schema_filepath)

    # Application Bringup
    auth_server_app = CreatFlaskApp(TOKEN_SERVICE_NAME).create_app_instance()
    authtoken_logger.info("Application :: {0} , Type :: {1}".format(auth_server_app, type(auth_server_app)))
    auth_server_app.config['JWT_SECRET_KEY'] = '12345Ricky@23'
    # auth_server_app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=100)  # Set token expiration time
    # token_expiry = auth_server_app.config['JWT_ACCESS_TOKEN_EXPIRES']
    airliner_jwt = JWTManager(auth_server_app)

    # REGISTRATION
    from src.auth_token_service.routes.token_routes import authtoken_blueprint, bind_reg_blueprints, display_reg_blueprints_per_service


    bind_reg_blueprints(auth_server_app, authtoken_blueprint)
    display_reg_blueprints_per_service(auth_server_app)



    # DataBase Bringup
    token_db_obj = CreateDbEngine(TOKEN_SERVICE_NAME, "mysql+pymysql", "root", "testeventstreammonitor#123", "localhost", "3303", "AuthTokens")

    token_db_engine = token_db_obj.create_db_engine()

    if check_db_connectivity_and_retry(TOKEN_SERVICE_NAME, token_db_engine):
        database_uri = token_db_obj.get_database_uri()
        if init_databases_for_service(database_uri):
            if create_tables_associated_to_db_model(Base, airliner_db_engine=token_db_engine):
                token_db_bind_obj = BindSQLALCHEMY(TOKEN_SERVICE_NAME, auth_server_app, database_uri)
                token_db_sqlalchemy = token_db_bind_obj.bind_db_app()
                token_pool_obj = QueuePool_To_Target_DB(TOKEN_SERVICE_NAME, token_db_engine, 100, 20)
                token_connection_pool = token_pool_obj.create_pool()
                token_pool_obj.display_pool_info()

    tokenstub, grpc_client_status = init_grpc_token_client("127.0.0.1", "8081")



except Exception as ex:
    print("Error occurred :: {0}\tLine No:: {1}".format(ex, sys.exc_info()[2].tb_lineno))
